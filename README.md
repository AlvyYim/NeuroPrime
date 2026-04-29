# NeuroPrime

A comprehensive electrophysiology data analysis software for macaque neural recordings.

## Overview

NeuroPrime is a powerful desktop application designed for analyzing neural spike data from macaque electrophysiology experiments. It provides a user-friendly interface for loading, processing, and visualizing neural recordings, with specialized tools for spike detection, sorting, and analysis.

## Features

### Spike Analysis
- **PSTH Analysis**: Peri-Stimulus Time Histogram calculation with customizable time windows
- **Raster Plot**: Visualize spike times across multiple trials
- **Tuning Curve**: Analyze neuron response selectivity to different stimulus conditions

### Data Processing
- **Spike Detection**: Automated spike detection with threshold-based methods
- **Spike Sorting**: PCA-based clustering for spike classification
- **Time Alignment**: Synchronize spike times with behavioral events

### LFP Analysis
- **Power Spectrum**: Frequency domain analysis of local field potentials
- **Filtering**: Bandpass filtering for specific frequency bands
- **Event-Related Potentials**: Analyze stimulus-locked LFP responses

### Behavioral Analysis
- **ROC Analysis**: Receiver Operating Characteristic curve analysis
- **Trial Management**: Organize and filter experimental trials
- **Abort Detection**: Identify and exclude aborted trials

### Custom Algorithms
- **Plugin System**: Extend functionality with custom Python scripts
- **Algorithm Editor**: Built-in code editor for creating custom analyses
- **Seamless Integration**: Import and manage custom algorithms

## Technology Stack

- **Framework**: PyQt6
- **Language**: Python 3.10+
- **Data Processing**: NumPy, SciPy
- **Visualization**: Matplotlib
- **Data Storage**: HDF5

## Installation

```bash
# Clone the repository
git clone https://github.com/AlvyYim/NeuroPrime.git
cd NeuroPrime

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the application
python run.py
```

### Quick Start

1. **Load Data**: Click "Data Loading" tab and import your electrophysiology data
2. **Select Algorithm**: Choose from available analysis tools in the ribbon bar
3. **Configure Parameters**: Adjust analysis settings in the parameter panel
4. **Run Analysis**: Click "Run Analysis" button to process data
5. **View Results**: Visualize results in the visualization area

## Project Structure

```
NeuroPrime/
├── src/
│   ├── algorithms/          # Analysis algorithms
│   │   ├── spike_analysis.py    # PSTH, raster plot, tuning curve
│   │   ├── behavior_analysis.py # Behavioral analysis tools
│   │   ├── lfp_analysis.py      # LFP processing
│   │   └── base.py              # Base algorithm classes
│   ├── parsers/             # Data file parsers
│   │   ├── nev_parser.py        # Blackrock NEV format
│   │   └── mbm_parser.py        # MBM behavior files
│   ├── ui/                  # User interface components
│   │   ├── main_window.py       # Main application window
│   │   ├── ribbon_bar.py         # Ribbon toolbar
│   │   └── visualization_area.py # Plot visualization
│   └── utils/               # Utility functions
├── custom_algorithms/       # User-defined algorithms
├── test2/                   # Test data directory
├── requirements.txt         # Project dependencies
└── run.py                   # Application entry point
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Commit your changes: `git commit -m 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please open an issue on GitHub.

## Acknowledgments

This software was developed for macaque electrophysiology research, with special thanks to the neuroscience community for their valuable feedback and contributions.
