import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.data.hdf5_reader import HDF5Reader

hdf5_file = r"c:\Users\Administrator\Desktop\new hope\code\NeuroPrime\test2\data\processed\FC_Grating_012.h5"

print("=" * 60)
print("统计abort的试次数量")
print("=" * 60)

with HDF5Reader(hdf5_file) as reader:
    trials = reader.get_trials()
    total_trials = len(trials)
    aborted_trials = [t for t in trials if t.get('aborted', False)]
    num_aborted = len(aborted_trials)
    
    print(f"总试次数: {total_trials}")
    print(f"Abort的试次数: {num_aborted}")
    print(f"正常试次数: {total_trials - num_aborted}")
    
    if num_aborted > 0:
        print("\nAbort的试次详情:")
        for i, trial in enumerate(aborted_trials):
            print(f"  试次{trial['trial_num']}: start_time={trial['start_time']:.3f}s, "
                  f"end_time={trial['end_time']:.3f}s, "
                  f"abort_time={trial.get('abort_time', 'N/A')}")
    else:
        print("\n没有发现abort的试次")

print("\n" + "=" * 60)
input("\n按回车键退出...")
