# MNE ICA Artifact Removal Algorithm Template

"""MNE ICA伪迹去除算法模板，用于识别和去除脑电信号中的伪迹。

该算法模板演示了如何使用MNE库进行ICA伪迹去除，包括：
1. ICA成分分离
2. 伪迹成分识别（眨眼、心跳）
3. 伪迹成分去除
4. 信号重建

适用于提高脑电信号质量，去除眨眼、心跳等生理伪迹。
"""

"""
=============================================================
ALGORITHM TEMPLATE GUIDE
=============================================================

1. TEST DATA STRUCTURE:
   When validating your algorithm, the system will use mock input data with the following structure:
   
   - input_data.spike_times: List of spike timestamps (e.g., [0.1, 0.5, 1.2, ...])
   - input_data.trial_info: List of trial information dictionaries
     Example: [{'start_time': 0, 'end_time': 5}, {'start_time': 5, 'end_time': 10}]
   - input_data.sampling_rate: Sampling rate (default: 2000.0 Hz)
   - input_data.lfp_data: LFP data (if available) as 2D array [channels x samples]

2. TEMPLATE COMPONENTS:
   - REQUIRED: class MNEICAArtifactRemovalAlgorithm(BaseAlgorithm): Main algorithm class
   - REQUIRED: def run(self, input_data, parameters): Algorithm execution method
   - REQUIRED: def get_parameters_schema(): Define algorithm parameters
   - REQUIRED: def validate_input(input_data): Validate input data
   - REQUIRED: def run_algorithm(input_data, parameters): Legacy function for direct execution
   - REQUIRED: ALGORITHM_INFO: Algorithm metadata for scheduler

3. API USAGE:
   - input_data: Contains the input data from the software
   - parameters: Dictionary of algorithm parameters set by the user
   - AlgorithmOutput: Return this object with your results
     Example: return AlgorithmOutput(data={...}, success=True, error_message="")

4. CUSTOMIZATION GUIDE:
   - MODIFY: Algorithm class name (update both class definition and ALGORITHM_INFO)
   - MODIFY: get_parameters_schema() to define your algorithm parameters
   - MODIFY: run() method to implement your algorithm logic
   - MODIFY: Algorithm description and category in __init__()
   - KEEP: The overall structure and required components

5. INTEGRATION PROCESS:
   1. Write your algorithm code
   2. Click "Validate" to test with mock data
   3. Click "Integrate" to add to the algorithm dropdown
   4. Enter a name for your algorithm when prompted

=============================================================
"""

import numpy as np
import matplotlib.pyplot as plt
import mne

# Import algorithm base classes
from src.algorithms.base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput
from src.algorithms.base import ParameterType, create_parameter

# HDF5数据转换为MNE格式
def hdf5_to_mne(input_data):
    """将HDF5数据转换为MNE数据格式"""
    # 获取数据
    lfp_data = input_data.lfp_data
    sampling_rate = input_data.sampling_rate
    
    # 创建MNE信息对象
    ch_names = [f'ch{i}' for i in range(lfp_data.shape[0])]
    info = mne.create_info(ch_names=ch_names, sfreq=sampling_rate, ch_types=['eeg']*lfp_data.shape[0])
    
    # 创建Raw对象
    raw = mne.io.RawArray(lfp_data, info)
    
    return raw

# Algorithm implementation class
class MNEICAArtifactRemovalAlgorithm(BaseAlgorithm):
    """MNE ICA artifact去除算法"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNEICAArtifactRemovalAlgorithm'
        self.description = "MNE ICA artifact去除算法，用于去除眨眼、心跳等伪迹"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "n_components", ParameterType.INTEGER,
                "ICA成分数量", 10,
                min_value=1, max_value=50
            ),
            create_parameter(
                "method", ParameterType.SELECT,
                "ICA方法", "fastica",
                options=["fastica", "infomax", "picard"]
            ),
            create_parameter(
                "random_state", ParameterType.INTEGER,
                "随机种子", 42,
                min_value=0, max_value=1000
            ),
            create_parameter(
                "reject", ParameterType.FLOAT,
                "拒绝阈值 (μV)", 200.0,
                min_value=100.0, max_value=500.0
            ),
            create_parameter(
                "artifacts_to_remove", ParameterType.SELECT,
                "要去除的伪迹类型", "eye,heart",
                options=["eye", "heart", "eye,heart", "none"]
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE ICA artifact removal...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            n_components = parameters.get('n_components', 10)
            method = parameters.get('method', 'fastica')
            random_state = parameters.get('random_state', 42)
            reject = parameters.get('reject', 200.0)
            artifacts_to_remove = parameters.get('artifacts_to_remove', 'eye,heart')
            
            # Get input data
            lfp_data = input_data.lfp_data
            sampling_rate = input_data.sampling_rate
            
            # 转换数据格式
            raw = hdf5_to_mne(input_data)
            
            # 过滤数据以提高ICA性能
            raw.filter(1.0, 40.0, fir_design='firwin')
            
            # 创建ICA对象
            ica = mne.preprocessing.ICA(n_components=n_components, method=method, random_state=random_state)
            
            # 拟合ICA
            try:
                # 尝试使用拒绝阈值
                ica.fit(raw, reject={'eeg': reject/1e6})
            except Exception as e:
                print(f"使用拒绝阈值拟合ICA失败: {e}")
                print("尝试不使用拒绝阈值重新拟合...")
                try:
                    # 不使用拒绝阈值
                    ica.fit(raw)
                except Exception as e2:
                    print(f"不使用拒绝阈值拟合ICA也失败: {e2}")
                    print("尝试使用更保守的参数...")
                    # 使用更保守的参数
                    ica = mne.preprocessing.ICA(n_components=min(5, n_components), method=method, random_state=random_state)
                    ica.fit(raw, reject=None)
            
            # 识别和标记伪迹成分
            try:
                eog_indices, eog_scores = ica.find_bads_eog(raw, ch_name=None)
            except Exception as e:
                print(f"寻找EOG伪迹时出错: {e}")
                print("没有找到EOG通道，跳过EOG伪迹去除")
                eog_indices, eog_scores = [], []
            
            try:
                ecg_indices, ecg_scores = ica.find_bads_ecg(raw, method='correlation', ch_name=None)
            except Exception as e:
                print(f"寻找ECG伪迹时出错: {e}")
                print("没有找到ECG通道，跳过ECG伪迹去除")
                ecg_indices, ecg_scores = [], []
            
            # 根据配置选择要去除的伪迹
            bad_indices = []
            if 'eye' in artifacts_to_remove:
                bad_indices.extend(eog_indices)
            if 'heart' in artifacts_to_remove:
                bad_indices.extend(ecg_indices)
            
            # 去除重复的成分索引
            bad_indices = list(set(bad_indices))
            
            # 应用ICA去除伪迹
            ica.exclude = bad_indices
            raw_clean = raw.copy()
            ica.apply(raw_clean)
            
            # 获取数据
            clean_data = raw_clean.get_data()
            
            # Prepare output
            output_data = {
                'clean_data': clean_data,
                'original_data': lfp_data,
                'ica_components': ica.get_components(),
                'bad_indices': bad_indices,
                'eog_indices': eog_indices,
                'ecg_indices': ecg_indices,
                'n_components': n_components,
                'method': method
            }
            # Prepare visualization data with clean data
            if input_data.lfp_data is not None:
                # Use clean data for visualization
                output_data['signal_data'] = clean_data
                output_data['sampling_rate'] = input_data.sampling_rate
                # Generate time axis
                times = np.arange(clean_data.shape[1]) / input_data.sampling_rate
                output_data['times'] = times
                output_data['plot_type'] = 'raw_signal'
            elif input_data.spike_times:
                # For spike data, use base class method
                vis_data = self.prepare_visualization_data(input_data)
                output_data.update(vis_data)
            

            
            # Statistics
            statistics = {
                'n_components': n_components,
                'method': method,
                'bad_components': len(bad_indices),
                'eog_components': len(eog_indices),
                'ecg_components': len(ecg_indices),
                'channels': clean_data.shape[0],
                'samples': clean_data.shape[1]
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE ICA Artifact Removal Results',
                'xlabel': 'Time (s)',
                'ylabel': 'Amplitude (μV)'
            }
            
            # Return results
            return AlgorithmOutput(
                data=output_data,
                statistics=statistics,
                plot_config=plot_config,
                success=True,
                error_message=""
            )
            
        except Exception as e:
            print(f"Algorithm execution error: {e}")
            import traceback
            traceback.print_exc()
            return AlgorithmOutput(
                success=False,
                error_message=str(e)
            )

# Legacy function for direct execution
def run_algorithm(input_data, parameters):
    """Legacy run function for direct execution"""
    algo = MNEICAArtifactRemovalAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNEICAArtifactRemovalAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNEICAArtifactRemovalAlgorithm',
    'class': MNEICAArtifactRemovalAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
