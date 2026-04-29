"""
NEV Parser Module
=================

This module provides a comprehensive parser for Blackrock NEV spike event files.
NEV files contain neural spike waveforms and digital events recorded from 
electrophysiology experiments.

File Structure:
- Basic Header: 336 bytes - Contains file metadata and format information
- Extended Headers: 32 bytes each - Channel/waveform configuration
- Data Packets: 108 bytes each - Contains spike timestamps, waveforms, and events

Key Features:
- Parses spike events with timestamps and waveforms
- Extracts digital events (START, STOP, PAUSEON, PAUSEOFF, ABORT, STIMCND)
- Parses trial information with start/end times and stimulus conditions
- Integrates with MBM behavior data files for validation
- Handles time alignment between spikes and trials
- Follows LoadSpike.m logic for consistency with MATLAB pipeline

Usage:
    from src.parsers.nev_parser import parse_nev
    
    result = parse_nev("experiment.nev")
    spike_times = np.array([s.timestamp for s in result['spike_events']])
    trials = result['trials']
"""

import struct
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path

from .mbm_parser import load_mbm, MBMInfo


@dataclass
class NEVBasicHeader:
    """
    NEV Basic Header structure (336 bytes).
    
    Contains fundamental metadata about the NEV file format and recording parameters.
    
    Attributes:
        file_type: File magic number, should be "NEURALEV"
        version: File format version (major.minor)
        extra_flag: Waveform format indicator
        header_size: Total header size in bytes
        dp_size: Data packet size (typically 108 bytes)
        clock_fs: Clock frequency in Hz
        waveform_fs: Waveform sampling rate in Hz
        time_origin: Recording start time components
        software_version: Recording software version
        num_extend: Number of extended headers
    """
    file_type: str           # "NEURALEV" magic number
    version: str             # Version string "major.minor"
    extra_flag: str          # Waveform format flag
    header_size: int         # Total header size
    dp_size: int            # Data packet size
    clock_fs: int           # Clock frequency (Hz)
    waveform_fs: int        # Waveform sampling rate (Hz)
    time_origin: List[int]  # Time origin components
    software_version: str    # Recording software version
    num_extend: int         # Number of extended headers


@dataclass
class NEUNEVWAVHeader:
    """
    NEUEVWAV Extended Header - Neural Event Waveform configuration.
    
    Contains electrode-specific configuration for spike detection and recording.
    
    Attributes:
        packet_id: Always "NEUEVWAV"
        elec_id: Electrode identifier
        connector: Connector letter (A, B, C, etc.)
        pin: Pin number on connector
        scale: Scaling factor (nV per LSB)
        energy_threshold: Energy detection threshold
        high_threshold: High threshold in uV
        low_threshold: Low threshold in uV
        num_unit: Number of sorted units
        waveform_size: Number of waveform samples (default 48)
    """
    packet_id: str = "NEUEVWAV"
    elec_id: int = 0
    connector: str = ""
    pin: int = 0
    scale: int = 0           # nV per LSB
    energy_threshold: int = 0
    high_threshold: int = 0  # uV
    low_threshold: int = 0   # uV
    num_unit: int = 0
    waveform_size: int = 48  # Number of waveform samples


@dataclass
class NEVSpikeEvent:
    """
    NEV Spike Event representation.
    
    Represents a single detected spike with its timestamp, electrode ID,
    unit classification, and waveform data.
    
    Attributes:
        timestamp: Spike time in seconds
        elec_id: Electrode channel ID
        unit: Cluster unit ID (0=unsorted, 1-5=sorted)
        waveform: 48-sample waveform in uV
    """
    timestamp: float         # Timestamp in seconds
    elec_id: int            # Electrode ID
    unit: int               # Cluster unit (0=unsorted, 1-5=sorted)
    waveform: np.ndarray    # Waveform data (48 samples)


@dataclass
class NEVDigitalEvent:
    """
    NEV Digital Event representation.
    
    Represents behavioral markers and experimental events.
    
    Attributes:
        timestamp: Event time in seconds
        event_type: Event classification (START, STOP, PAUSEON, PAUSEOFF, ABORT, STIMCND)
        value: Event-specific value (e.g., stimulus condition)
    """
    timestamp: float         # Timestamp in seconds
    event_type: str          # Event type classification
    value: int              # Event-specific value


@dataclass
class NEVTrialInfo:
    """
    Trial information extracted from NEV file.
    
    Contains timing and condition information for a single experimental trial.
    
    Attributes:
        trial_num: Trial number (1-indexed)
        start_time: Trial start time (PAUSEOFF event) in seconds
        end_time: Trial end time (PAUSEON event) in seconds
        stim_cnd: Stimulus condition ID
        abort_time: Abort time relative to TTL (or -999 if no abort)
        ttl_time: TTL time offset for this trial
    """
    trial_num: int
    start_time: float        # PAUSEOFF time
    end_time: float         # PAUSEON time
    stim_cnd: int          # Stimulus condition
    abort_time: Optional[float] = None
    ttl_time: Optional[float] = None


class NEVParser:
    """
    Main parser class for NEV files.
    
    Parses Blackrock NEV format files to extract spike events, digital events,
    and trial information. Integrates with MBM behavior files for validation.
    
    Usage:
        parser = NEVParser("path/to/file.nev")
        success = parser.parse()
        
        # Access parsed data
        spike_events = parser.spike_events
        digital_events = parser.digital_events  
        trials = parser.trials
    """

    # Mapping of digital event codes to human-readable names
    EVENT_TYPES = {
        1: "START",
        2: "STOP",
        3: "PAUSEON",      # Trial end marker
        4: "PAUSEOFF",     # Trial start marker
        5: "ABORT",
        128: "VSGTRIG",
        253: "STIMCND",    # Stimulus condition (values 512+)
        254: "STIMCND",    # Stimulus condition (values 256-511)
        255: "STIMCND"     # Stimulus condition (values 0-255)
    }

    def __init__(self, file_path: str):
        """
        Initialize NEV parser.
        
        Args:
            file_path: Path to the NEV file
        """
        self.file_path = Path(file_path)
        self.file = None
        self.file_size = 0

        # Header information
        self.basic_header: Optional[NEVBasicHeader] = None
        self.extended_headers: List[Dict] = []
        self.waveform_headers: Dict[int, NEUNEVWAVHeader] = {}

        # Parsed event data
        self.spike_events: List[NEVSpikeEvent] = []
        self.digital_events: List[NEVDigitalEvent] = []
        self.trials: List[NEVTrialInfo] = []

        # MBM integration
        self.mbm_info: Optional[MBMInfo] = None
        self.valid_mbm: bool = False

        # TTL events for time synchronization
        self.ttl_events: List[NEVDigitalEvent] = []

        # Raw data arrays
        self.raw_timestamps: Optional[np.ndarray] = None
        self.raw_elec_ids: Optional[np.ndarray] = None
        self.raw_units: Optional[np.ndarray] = None
        self.raw_waveforms: Optional[np.ndarray] = None

        # Trial parsing intermediate data
        self.off_pos: np.ndarray = None
        self.on_pos: np.ndarray = None
        self.ttl_time: np.ndarray = None

    def parse(self) -> bool:
        """
        Parse the NEV file completely.
        
        Executes all parsing stages in order:
        1. Read basic header
        2. Read extended headers
        3. Read data packets
        4. Parse digital events
        5. Load MBM file (if available)
        6. Parse trial information
        7. Compare with MBM data
        8. Adjust spike timestamps
        
        Returns:
            True if parsing succeeded, False otherwise
        """
        try:
            with open(self.file_path, 'rb') as f:
                self.file = f

                # Get file size
                f.seek(0, 2)
                self.file_size = f.tell()
                f.seek(0, 0)

                # Parse header and data
                if not self._read_basic_header():
                    return False

                if not self._read_extended_headers():
                    return False

                if not self._read_data_packets():
                    return False

                # Post-processing
                self._parse_digital_events()
                self._load_mbm()
                self._parse_trials()
                self._compare_with_mbm()
                self._adjust_spike_timestamps()

            return True

        except Exception as e:
            print(f"Error parsing NEV file: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _read_basic_header(self) -> bool:
        """
        Read and parse the NEV basic header (336 bytes).
        
        Extracts file format information, clock frequencies, and header structure.
        
        Returns:
            True if successful, False on error
        """
        f = self.file

        try:
            file_type = struct.unpack('8s', f.read(8))[0].decode('ascii', errors='ignore').strip('\x00')
        except:
            file_type = "Unknown"

        ver_major, ver_minor = struct.unpack('2B', f.read(2))
        version = f"{ver_major}.{ver_minor}"

        waveform_bit = struct.unpack('H', f.read(2))[0]
        extra_flag = "all 16-bit wav" if waveform_bit == 1 else "mixed 16-bit wav"

        header_size = struct.unpack('I', f.read(4))[0]
        dp_size = struct.unpack('I', f.read(4))[0]
        clock_fs = struct.unpack('I', f.read(4))[0]
        waveform_fs = struct.unpack('I', f.read(4))[0]

        time_origin = list(struct.unpack('8H', f.read(16)))

        try:
            software_version = struct.unpack('32s', f.read(32))[0].decode('ascii', errors='ignore').strip('\x00')
        except:
            software_version = "Unknown"

        # Seek to correct position for num_extend
        curr_pos = f.tell()
        offset = 332 - curr_pos
        if offset != 0:
            f.seek(offset, 1)

        num_extend = struct.unpack('I', f.read(4))[0]

        # Validate position
        curr_pos = f.tell()
        if curr_pos != 336:
            print(f"Warning: Basic header position mismatch. Expected 336, got {curr_pos}")
            f.seek(336, 0)

        # Validate header size
        expected_header_size = 336 + num_extend * 32
        if header_size != expected_header_size:
            print(f"Error: Extended header size mismatch. Expected {expected_header_size}, got {header_size}")
            return False

        self.basic_header = NEVBasicHeader(
            file_type=file_type,
            version=version,
            extra_flag=extra_flag,
            header_size=header_size,
            dp_size=dp_size,
            clock_fs=clock_fs,
            waveform_fs=waveform_fs,
            time_origin=time_origin,
            software_version=software_version,
            num_extend=num_extend
        )

        return True

    def _read_extended_headers(self) -> bool:
        """
        Read and parse extended headers.
        
        Each extended header is 32 bytes. NEUEVWAV headers contain
        electrode-specific configuration.
        
        Returns:
            True if successful, False on error
        """
        f = self.file
        num_extend = self.basic_header.num_extend

        for i in range(num_extend):
            packet_id = struct.unpack('8s', f.read(8))[0].decode('ascii').strip('\x00')

            if packet_id == 'NEUEVWAV':
                # Parse neural event waveform header
                header = self._read_neuevwav_header(f)
                self.waveform_headers[header.elec_id] = header
                self.extended_headers.append({
                    'type': 'NEUEVWAV',
                    'data': header
                })
            else:
                # Skip unrecognized header types
                f.seek(24, 1)
                self.extended_headers.append({
                    'type': packet_id,
                    'data': None
                })

        # Validate position
        if f.tell() != self.basic_header.header_size:
            print(f"Error: Extended header position mismatch")
            return False

        return True

    def _read_neuevwav_header(self, f) -> NEUNEVWAVHeader:
        """
        Read a single NEUEVWAV extended header.
        
        Args:
            f: Open file handle
            
        Returns:
            NEUNEVWAVHeader object
        """
        elec_id = struct.unpack('H', f.read(2))[0]

        connector_code = struct.unpack('B', f.read(1))[0]
        connector = chr(64 + connector_code)  # Convert to ASCII letter (A=65)

        pin = struct.unpack('B', f.read(1))[0]

        scale = struct.unpack('H', f.read(2))[0]

        energy_threshold = struct.unpack('H', f.read(2))[0]

        high_threshold = struct.unpack('h', f.read(2))[0]

        low_threshold = struct.unpack('h', f.read(2))[0]

        num_unit = struct.unpack('B', f.read(1))[0]

        waveform_size = struct.unpack('B', f.read(1))[0]
        if waveform_size == 0:
            waveform_size = 48  # Default value

        # Skip remaining bytes (reserved)
        f.seek(10, 1)

        return NEUNEVWAVHeader(
            elec_id=elec_id,
            connector=connector,
            pin=pin,
            scale=scale,
            energy_threshold=energy_threshold,
            high_threshold=high_threshold,
            low_threshold=low_threshold,
            num_unit=num_unit,
            waveform_size=waveform_size
        )

    def _read_data_packets(self) -> bool:
        """
        Read all data packets from the file.
        
        Data packets contain spike timestamps, electrode IDs, unit IDs,
        and waveform data. Each packet is typically 108 bytes.
        
        Returns:
            True if successful, False on error
        """
        f = self.file
        dp_size = self.basic_header.dp_size
        clock_fs = self.basic_header.clock_fs

        # Calculate number of data packets
        num_dp = (self.file_size - self.basic_header.header_size) // dp_size

        # Arrays to store raw data
        timestamps = []
        elec_ids = []
        units = []
        waveforms = []

        for i in range(num_dp):
            # Read timestamp (4 bytes, unsigned int)
            timestamp_raw = struct.unpack('I', f.read(4))[0]
            timestamp = timestamp_raw / clock_fs

            # Read electrode ID (2 bytes)
            elec_id = struct.unpack('H', f.read(2))[0]

            # Read unit ID (1 byte)
            unit = struct.unpack('B', f.read(1))[0]

            # Skip 1 reserved byte
            f.seek(1, 1)

            # Read waveform samples (remaining bytes / 2 for int16)
            waveform_samples = (dp_size - 8) // 2
            waveform = np.fromfile(f, dtype=np.int16, count=waveform_samples)

            # Store raw data
            timestamps.append(timestamp)
            elec_ids.append(elec_id)
            units.append(unit)
            waveforms.append(waveform)

        # Store raw arrays
        self.raw_timestamps = np.array(timestamps)
        self.raw_elec_ids = np.array(elec_ids)
        self.raw_units = np.array(units)
        self.raw_waveforms = np.array(waveforms)

        # Extract spike events (elec_id != 0 and != 129)
        spike_mask = (self.raw_elec_ids != 0) & (self.raw_elec_ids != 129)

        for i in np.where(spike_mask)[0]:
            elec_id = self.raw_elec_ids[i]
            scale = 1.0
            if elec_id in self.waveform_headers:
                scale = self.waveform_headers[elec_id].scale / 1000.0  # Convert nV to uV

            # Convert waveform to physical units (uV)
            waveform_physical = self.raw_waveforms[i] * scale

            event = NEVSpikeEvent(
                timestamp=self.raw_timestamps[i],
                elec_id=elec_id,
                unit=self.raw_units[i],
                waveform=waveform_physical.astype(np.float32)
            )
            self.spike_events.append(event)

        return True
    
    def _adjust_spike_timestamps(self):
        """
        Adjust spike timestamps to align with trial timing.
        
        When spike times and trial times use different time bases, this method
        detects and corrects the offset. If spikes start near 0 but trials start
        at a later time, we shift all spike times to match the trial time base.
        """
        if not self.trials or not self.spike_events:
            return
        
        # Get first trial start time as reference
        first_trial_start = self.trials[0].start_time
        
        # Analyze spike time distribution relative to first trial
        spike_times = np.array([e.timestamp for e in self.spike_events])
        pre_trial_spikes = spike_times[spike_times < first_trial_start]
        post_trial_spikes = spike_times[spike_times >= first_trial_start]
        
        print(f"\n=== Time Alignment Adjustment ===")
        print(f"First trial start time: {first_trial_start:.3f} seconds")
        print(f"Spikes before first trial: {len(pre_trial_spikes)}")
        print(f"Spikes after first trial: {len(post_trial_spikes)}")
        
        # Check time ranges
        min_spike_time = spike_times.min()
        max_spike_time = spike_times.max()
        min_trial_time = min(t.start_time for t in self.trials)
        max_trial_time = max(t.end_time for t in self.trials)
        
        print(f"Spike time range: {min_spike_time:.3f} - {max_spike_time:.3f} seconds")
        print(f"Trial time range: {min_trial_time:.3f} - {max_trial_time:.3f} seconds")
        
        # Detect time base mismatch: spikes start near 0, trials start much later
        if min_spike_time < 1.0 and min_trial_time > 10.0:
            # Calculate offset to align spike times with trial times
            time_offset = first_trial_start
            
            print(f"Trial 1 start time: {first_trial_start:.3f} seconds")
            print(f"Calculated time offset: {time_offset:.3f} seconds")
            
            # Apply offset to all spike timestamps
            for event in self.spike_events:
                event.timestamp += time_offset
            
            # Update raw timestamps too
            if self.raw_timestamps is not None:
                self.raw_timestamps += time_offset
            
            print(f"Adjusted spike time range: {self.spike_events[0].timestamp:.3f} - {self.spike_events[-1].timestamp:.3f} seconds")
            print(f"Trial 1 start time remains: {self.trials[0].start_time:.3f} seconds")
        else:
            print("Spike times and trial times are already aligned")

    def _parse_digital_events(self):
        """
        Parse digital events from raw data.
        
        Digital events are identified by elec_id == 0 and contain
        behavioral markers like trial boundaries and stimulus conditions.
        """
        digital_mask = self.raw_elec_ids == 0

        for i in np.where(digital_mask)[0]:
            unit = self.raw_units[i]

            # Check if this is a valid digital event (bit 0 set)
            if unit & 0x01:
                if len(self.raw_waveforms[i]) >= 2:
                    lower_byte = int(self.raw_waveforms[i][0]) & 0xFF
                    higher_byte = int(self.raw_waveforms[i][1]) & 0xFF

                    if lower_byte in self.EVENT_TYPES:
                        event_type = self.EVENT_TYPES[lower_byte]

                        # Calculate stimulus condition value based on event type
                        if lower_byte == 255:
                            value = higher_byte
                        elif lower_byte == 254:
                            value = 256 + higher_byte
                        elif lower_byte == 253:
                            value = 512 + higher_byte
                        else:
                            value = higher_byte

                        event = NEVDigitalEvent(
                            timestamp=self.raw_timestamps[i],
                            event_type=event_type,
                            value=value
                        )
                        self.digital_events.append(event)

    def _load_mbm(self):
        """
        Load corresponding MBM behavior file if it exists.
        
        MBM files contain behavioral response data used to validate
        trial information and abort status.
        """
        mbm_path = self.file_path.with_suffix('.mbm')

        if mbm_path.exists():
            print(f"Loading MBM file: {mbm_path}")
            self.mbm_info = load_mbm(str(mbm_path))
            self.valid_mbm = self.mbm_info is not None
        else:
            print(f"MBM file not found: {mbm_path}")
            self.valid_mbm = False
            self.mbm_info = None

    def _parse_trials(self):
        """
        Parse trial information from digital events.
        
        Extracts trial boundaries from PAUSEON/PAUSEOFF events,
        stimulus conditions from STIMCND events, and abort times
        from ABORT events. Follows LoadSpike.m logic.
        """
        # Extract relevant events
        pause_off_events = [e for e in self.digital_events if e.event_type == "PAUSEOFF"]
        pause_on_events = [e for e in self.digital_events if e.event_type == "PAUSEON"]
        stim_cnd_events = [e for e in self.digital_events if e.event_type == "STIMCND"]
        abort_events = [e for e in self.digital_events if e.event_type == "ABORT"]

        # Sort events by timestamp
        pause_off_events.sort(key=lambda x: x.timestamp)
        pause_on_events.sort(key=lambda x: x.timestamp)
        abort_events.sort(key=lambda x: x.timestamp)

        num_pause_off = len(pause_off_events)
        num_pause_on = len(pause_on_events)
        num_abort = len(abort_events)
        num_stim_cnd = len(stim_cnd_events)

        # Validate event counts
        if not ((num_pause_off == num_pause_on - 1 or num_pause_off == num_pause_on)
                and num_pause_off >= num_abort and num_pause_off >= num_stim_cnd):
            print(f"Warning: Abnormal PAUSEON/OFF/ABORT count relationship")
            print(f"  NumPauseOff={num_pause_off}, NumPauseOn={num_pause_on}, NumAbort={num_abort}, NumStimCnd={num_stim_cnd}")

        # Find TTL event positions
        ttldppos = np.where(self.raw_elec_ids == 129)[0]

        # Get positions of PAUSEON/OFF events
        off_pos = np.array([i for i, e in enumerate(self.digital_events) if e.event_type == "PAUSEOFF"])
        on_pos = np.array([i for i, e in enumerate(self.digital_events) if e.event_type == "PAUSEON"])

        # Initialize TTL time array
        ttl_time = np.full((num_pause_off, 1000), np.nan)

        # Map TTL events to trials
        for ttl_idx in ttldppos:
            ttl_time_stamp = self.raw_timestamps[ttl_idx]
            for trial_idx in range(num_pause_off):
                if trial_idx < num_pause_on:
                    off_time = pause_off_events[trial_idx].timestamp
                    on_time = pause_on_events[trial_idx].timestamp

                    if off_time <= ttl_time_stamp <= on_time:
                        col = np.argmax(np.isnan(ttl_time[trial_idx, :]))
                        ttl_time[trial_idx, col] = ttl_time_stamp

        # Handle case where there's an extra PAUSEON at the beginning
        if num_pause_on > num_pause_off:
            start_idx = num_pause_on - num_pause_off
            on_pos = on_pos[start_idx:]
            pause_on_events = pause_on_events[start_idx:]

        # Validate trial timing
        for i in range(min(len(pause_off_events), len(pause_on_events))):
            if pause_off_events[i].timestamp > pause_on_events[i].timestamp:
                print(f"Warning: Trial {i+1} has OffTime > OnTime")

        # Get TTL times for each trial
        time_offsets = ttl_time[:, 0]

        num_trials = min(len(pause_off_events), len(pause_on_events))

        # Create trial objects
        trials_data = []
        for i in range(num_trials):
            # Use raw timestamps directly for consistent time base
            start_time = pause_off_events[i].timestamp
            end_time = pause_on_events[i].timestamp

            ttl_offset = time_offsets[i] if i < len(time_offsets) else np.nan
            
            # Use raw time without TTL subtraction for consistency
            adjusted_start_time = start_time
            adjusted_end_time = end_time

            trial = NEVTrialInfo(
                trial_num=i + 1,
                start_time=adjusted_start_time,
                end_time=adjusted_end_time,
                stim_cnd=stim_cnd_events[i].value if i < len(stim_cnd_events) else -1
            )

            trial.ttl_time = 0.0  # Default to 0 for consistent time base

            trials_data.append(trial)

        # Calculate abort times following LoadSpike.m logic:
        # ExpMonitor.AbortT = AbortTime-TTLTime(:,1);
        # ExpMonitor.AbortT(isnan(TTLTime(:,1))) = -999;
        abort_index = 0
        for i in range(num_trials):
            if abort_index < num_abort:
                ttl_offset = time_offsets[i] if i < len(time_offsets) else np.nan
                
                if not np.isnan(ttl_offset):
                    trials_data[i].abort_time = abort_events[abort_index].timestamp - ttl_offset
                else:
                    # Mark missing TTL as -999 per LoadSpike.m convention
                    trials_data[i].abort_time = -999.0
                
                abort_index += 1

        # Store results
        self.trials = trials_data
        self.off_pos = off_pos
        self.on_pos = on_pos
        self.ttl_time = ttl_time

    def _compare_with_mbm(self):
        """
        Compare parsed trial information with MBM behavior data.
        
        Validates abort status and stimulus conditions against
        behavior data for consistency.
        """
        if not self.valid_mbm or self.mbm_info is None:
            return

        mbm_trials = self.mbm_info.nTrials
        spike_trials = len(self.trials)

        print(f"MBM trials: {mbm_trials}, SPIKE trials: {spike_trials}")

        if mbm_trials != spike_trials:
            print(f"Warning: MBM and SPIKE trial counts do not match")
            return

        # Validate each trial against MBM data
        for i in range(min(mbm_trials, spike_trials)):
            trial = self.trials[i]
            mbm_resp_code = self.mbm_info.RespCode[i]

            # Determine validity from both sources
            mbm_valid = mbm_resp_code > 0
            spike_valid = trial.abort_time is None

            # Correct abort status if mismatch
            if mbm_valid != spike_valid:
                print(f"Correcting abort status for trial {i+1}")
                if not mbm_valid:
                    trial.abort_time = trial.start_time  # Mark as aborted
                else:
                    trial.abort_time = None  # Mark as valid

            # Validate stimulus condition
            mbm_stim_id = self.mbm_info.StimID[i]
            if trial.stim_cnd == -1 or trial.stim_cnd != mbm_stim_id:
                print(f"Correcting stim_cnd for trial {i+1}: {trial.stim_cnd} -> {mbm_stim_id}")
                trial.stim_cnd = mbm_stim_id

    def get_spike_times(self, elec_id: int = None, unit: int = None) -> np.ndarray:
        """
        Get spike times filtered by electrode and/or unit.
        
        Args:
            elec_id: Electrode ID to filter by (optional)
            unit: Unit ID to filter by (optional)
        
        Returns:
            Array of spike timestamps
        """
        spikes = self.spike_events

        if elec_id is not None:
            spikes = [s for s in spikes if s.elec_id == elec_id]

        if unit is not None:
            spikes = [s for s in spikes if s.unit == unit]

        return np.array([s.timestamp for s in spikes])

    def get_spike_waveforms(self, elec_id: int = None) -> np.ndarray:
        """
        Get spike waveforms filtered by electrode.
        
        Args:
            elec_id: Electrode ID to filter by (optional)
        
        Returns:
            Array of spike waveforms
        """
        spikes = self.spike_events

        if elec_id is not None:
            spikes = [s for s in spikes if s.elec_id == elec_id]

        return np.array([s.waveform for s in spikes])

    def get_channel_info(self) -> List[Dict]:
        """
        Get channel information from waveform headers.
        
        Returns:
            List of dictionaries containing electrode configuration
        """
        channels = []
        for elec_id, header in self.waveform_headers.items():
            channels.append({
                'elec_id': elec_id,
                'connector': header.connector,
                'pin': header.pin,
                'scale_nv': header.scale,
                'high_threshold_uv': header.high_threshold,
                'low_threshold_uv': header.low_threshold,
                'num_unit': header.num_unit
            })
        return channels


def parse_nev(file_path: str) -> Optional[Dict]:
    """
    Parse an NEV file and return the results as a dictionary.
    
    Args:
        file_path: Path to the NEV file
        
    Returns:
        Dictionary containing parsed data or None if parsing failed
    """
    parser = NEVParser(file_path)

    if not parser.parse():
        return None

    return {
        'basic_header': parser.basic_header,
        'extended_headers': parser.extended_headers,
        'waveform_headers': parser.waveform_headers,
        'spike_events': parser.spike_events,
        'digital_events': parser.digital_events,
        'trials': parser.trials,
        'channel_info': parser.get_channel_info()
    }


if __name__ == '__main__':
    """
    Self-test for NEV parser.
    Demonstrates parsing and displays key information.
    """
    import sys

    test_file = r"c:\Users\buaal\Desktop\NeuroPrime\coco1227rawdata\FC_Grating_014.nev"

    print(f"Parsing NEV file: {test_file}")
    result = parse_nev(test_file)

    if result:
        print("\n=== Basic Header ===")
        bh = result['basic_header']
        print(f"File Type: {bh.file_type}")
        print(f"Version: {bh.version}")
        print(f"Clock Frequency: {bh.clock_fs} Hz")
        print(f"Waveform Frequency: {bh.waveform_fs} Hz")
        print(f"Number of Extended Headers: {bh.num_extend}")

        print(f"\n=== Spike Events ===")
        print(f"Total Spike Events: {len(result['spike_events'])}")

        if result['spike_events']:
            from collections import Counter
            elec_counts = Counter([s.elec_id for s in result['spike_events']])
            print(f"Active Electrodes: {len(elec_counts)}")
            print("Top 5 electrodes by spike count:")
            for elec_id, count in elec_counts.most_common(5):
                print(f"  Electrode {elec_id}: {count} spikes")

        print(f"\n=== Digital Events ===")
        print(f"Total Digital Events: {len(result['digital_events'])}")

        from collections import Counter
        event_counts = Counter([e.event_type for e in result['digital_events']])
        for event_type, count in event_counts.items():
            print(f"  {event_type}: {count} events")

        print(f"\n=== Trials ===")
        print(f"Number of Trials: {len(result['trials'])}")
        if result['trials']:
            print("First 3 trials:")
            for trial in result['trials'][:3]:
                abort_status = f"Aborted at {trial.abort_time:.3f}" if trial.abort_time else "Completed"
                print(f"  Trial {trial.trial_num}: {trial.start_time:.3f}s - {trial.end_time:.3f}s, "
                      f"StimCnd={trial.stim_cnd}, {abort_status}")

        print("\n✅ NEV parsing completed successfully!")
    else:
        print("❌ NEV parsing failed!")
        sys.exit(1)
