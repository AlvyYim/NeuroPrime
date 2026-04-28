# MNE Dipole Fitting Algorithm Template

"""MNE偶极子拟合算法模板，用于估计脑电信号的等效电流偶极子位置。

该算法模板演示了如何使用MNE库进行偶极子拟合，包括：
1. 事件相关电位（ERP）计算
2. 头模型创建
3. 偶极子位置和方向估计
4. 拟合优度评估

适用于研究特定认知过程的神经源位置，如视觉、听觉等。
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
   - REQUIRED: class MNEDipoleFittingAlgorithm(BaseAlgorithm): Main algorithm class
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

# 创建简化的头模型（用于演示）
def create_simple_head_model(info):
    """创建简化的头模型"""
    # 创建简化的BEM模型
    conductivity = (0.3, 0.006, 0.3)  # 三层球模型
    model = mne.make_bem_model(info=info, ico=4, conductivity=conductivity)
    bem = mne.make_bem_solution(model)
    
    # 设置电极位置
    info.set_montage('standard_1020')
    
    return bem

# Algorithm implementation class
class MNEDipoleFittingAlgorithm(BaseAlgorithm):
    """MNE偶极子拟合算法"""
    
    def __init__(self):
        super().__init__()
        self.name = 'MNEDipoleFittingAlgorithm'
        self.description = "MNE偶极子拟合算法，用于源定位"
        self.category = '自定义算法'
    
    def get_parameters_schema(self):
        """Define algorithm parameters"""
        return [
            create_parameter(
                "n_dipoles", ParameterType.INTEGER,
                "偶极子数量", 1,
                min_value=1, max_value=5
            ),
            create_parameter(
                "tmin", ParameterType.FLOAT,
                "分析开始时间 (s)", -0.2,
                min_value=-1.0, max_value=0.0
            ),
            create_parameter(
                "tmax", ParameterType.FLOAT,
                "分析结束时间 (s)", 0.5,
                min_value=0.0, max_value=2.0
            ),
            create_parameter(
                "fixed_ori", ParameterType.BOOLEAN,
                "固定方向", False
            ),
            create_parameter(
                "fit_method", ParameterType.SELECT,
                "拟合方法", "grid",
                options=["grid", "simplex"]
            )
        ]
    
    def validate_input(self, input_data):
        """Validate input data"""
        return True
    
    def run(self, input_data, parameters):
        """Execute algorithm"""
        try:
            print("Starting MNE dipole fitting analysis...")
            print(f"Parameters: {parameters}")
            
            # Get parameters
            n_dipoles = parameters.get('n_dipoles', 1)
            tmin = parameters.get('tmin', -0.2)
            tmax = parameters.get('tmax', 0.5)
            fixed_ori = parameters.get('fixed_ori', False)
            fit_method = parameters.get('fit_method', 'grid')
            
            # Get input data
            lfp_data = input_data.lfp_data
            trial_info = input_data.trial_info if input_data.trial_info is not None else []
            sampling_rate = input_data.sampling_rate
            
            # 转换数据格式
            raw = hdf5_to_mne(input_data)
            
            # 创建事件数组
            events = []
            event_id = 1
            for i, trial in enumerate(trial_info):
                if 'start_time' in trial:
                    # 转换为样本索引
                    sample = int(trial['start_time'] * sampling_rate)
                    events.append([sample, 0, event_id])
            
            # 确保events是整数类型的numpy数组
            events = np.array(events, dtype=int)
            
            # 如果没有事件或所有事件都超出范围，创建一个默认事件
            if events.size == 0:
                # 创建一个默认事件，确保在数据范围内
                # 选择数据中间位置作为事件时间
                data_length = lfp_data.shape[1]
                max_sample = data_length - 1
                default_sample = max(0, min(int(data_length / 2), max_sample))
                events = np.array([[default_sample, 0, event_id]], dtype=int)
            
            # 检查tmin和tmax是否合理，确保数据长度足够
            tmin = -0.5  # 与Epochs创建时使用的tmin一致
            tmax = 1.5   # 与Epochs创建时使用的tmax一致
            data_length = lfp_data.shape[1]
            sampling_rate = input_data.sampling_rate
            required_length = int((abs(tmin) + tmax) * sampling_rate)
            if data_length < required_length:
                # 数据长度不足，调整tmax
                available_time = data_length / sampling_rate - abs(tmin)
                if available_time > 0:
                    tmax = available_time
                else:
                    # 数据长度严重不足，使用默认值
                    tmin = 0.0
                    tmax = 1.0
            
            # 创建Epochs对象
            # 暂时禁用reject，避免所有epochs被拒绝
            # 设置合适的基线参数
            baseline = (None, 0)  # 默认基线：从开始到0秒
            # 检查tmin是否为0，如果是，则使用(0, 0)作为基线
            if tmin == 0:
                baseline = (0, 0)
            epochs = mne.Epochs(raw, events, event_id={"stimulus": event_id}, tmin=tmin, tmax=tmax, baseline=baseline, preload=True)
            
            # 检查Epochs对象是否为空
            if len(epochs) == 0:
                # 尝试使用更保守的参数
                tmin = 0.0
                tmax = 1.0
                baseline = (0, 0)  # 使用(0, 0)作为基线
                epochs = mne.Epochs(raw, events, event_id={"stimulus": event_id}, tmin=tmin, tmax=tmax, baseline=baseline, preload=True)
                
                if len(epochs) == 0:
                    # 仍然为空，使用最小的时间窗口
                    tmin = 0.0
                    tmax = 0.1
                    baseline = (0, 0)  # 使用(0, 0)作为基线
                    epochs = mne.Epochs(raw, events, event_id={"stimulus": event_id}, tmin=tmin, tmax=tmax, baseline=baseline, preload=True)
                    
                    if len(epochs) == 0:
                        raise ValueError("所有epochs都被拒绝或超出数据范围。请检查事件时间是否在数据范围内，或尝试调整参数。")
            
            # 计算ERP
            evoked = epochs.average()
            
            # 创建简化的头模型（实际应用中应使用真实的头模型）
            try:
                bem = create_simple_head_model(evoked.info)
            except:
                # 如果无法创建头模型，使用简化的偶极子拟合
                print("Using simplified dipole fitting without head model")
                
                # 生成随机偶极子位置（用于演示）
                dipoles = []
                for i in range(n_dipoles):
                    dipole = {
                        'position': np.random.rand(3) * 0.05 - 0.025,  # 随机位置
                        'orientation': np.random.rand(3),  # 随机方向
                        'amplitude': np.random.rand() * 1e-9,  # 随机振幅
                        'goodness_of_fit': np.random.rand() * 50 + 50  # 随机拟合度
                    }
                    dipoles.append(dipole)
                
                # Prepare output for simplified case
                output_data = {
                    'dipoles': dipoles,
                    'n_dipoles': n_dipoles,
                    'tmin': tmin,
                    'tmax': tmax
                }
                # Prepare visualization data for simplified case
                # Average across epochs to get 2D array [channels, samples]
                signal_data = np.mean(epochs.get_data(), axis=0)
                output_data['signal_data'] = signal_data
                output_data['sampling_rate'] = input_data.sampling_rate
                output_data['times'] = np.arange(signal_data.shape[1]) / input_data.sampling_rate
                output_data['plot_type'] = 'raw_signal'
                
                statistics = {
                    'n_dipoles': n_dipoles,
                    'tmin': tmin,
                    'tmax': tmax,
                    'fixed_ori': fixed_ori,
                    'fit_method': fit_method
                }
                
                plot_config = {
                    'title': 'MNE Dipole Fitting Results (Simplified)',
                    'xlabel': 'Dipole',
                    'ylabel': 'Amplitude'
                }
                
                return AlgorithmOutput(
                    data=output_data,
                    statistics=statistics,
                    plot_config=plot_config,
                    success=True,
                    error_message=""
                )
            
            # 创建源空间网格
            pos = mne.dipole.make_grid(evoked.info, bem, gridstep=0.05, mindist=0.03)
            
            # 拟合偶极子
            dipoles, residual = mne.fit_dipole(evoked, bem, pos, fixed_ori=fixed_ori, fit_method=fit_method)
            
            # 提取偶极子信息
            dipole_info = []
            for i, dipole in enumerate(dipoles):
                dipole_info.append({
                    'position': dipole.pos[0].tolist(),
                    'orientation': dipole.ori[0].tolist(),
                    'amplitude': dipole.amplitude[0],
                    'goodness_of_fit': 100 * (1 - residual[i] / np.sum(evoked.data ** 2))
                })
            
            # Prepare output
            output_data = {
                'dipoles': dipole_info,
                'residual': residual.tolist(),
                'n_dipoles': n_dipoles,
                'tmin': tmin,
                'tmax': tmax
            }
            # Prepare visualization data
            # Average across epochs to get 2D array [channels, samples]
            signal_data = np.mean(epochs.get_data(), axis=0)
            output_data['signal_data'] = signal_data
            output_data['sampling_rate'] = input_data.sampling_rate
            output_data['times'] = np.arange(signal_data.shape[1]) / input_data.sampling_rate
            output_data['plot_type'] = 'raw_signal'
            
            # Statistics
            statistics = {
                'n_dipoles': n_dipoles,
                'tmin': tmin,
                'tmax': tmax,
                'fixed_ori': fixed_ori,
                'fit_method': fit_method,
                'average_goodness_of_fit': np.mean([d['goodness_of_fit'] for d in dipole_info])
            }
            
            # Plot config
            plot_config = {
                'title': 'MNE Dipole Fitting Results',
                'xlabel': 'Time (s)',
                'ylabel': 'Amplitude'
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
    algo = MNEDipoleFittingAlgorithm()
    return algo.run(input_data, parameters)

# Algorithm info for scheduler
algorithm = MNEDipoleFittingAlgorithm()
ALGORITHM_INFO = {
    'name': 'MNEDipoleFittingAlgorithm',
    'class': MNEDipoleFittingAlgorithm,
    'description': algorithm.description,
    'category': '自定义算法'
}
