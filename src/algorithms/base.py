"""
Algorithm Base - 算法基类

定义所有分析算法的抽象基类和数据类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class ParameterType(Enum):
    """参数类型枚举"""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    SELECT = "select"
    RANGE = "range"


@dataclass
class AlgorithmParameter:
    """算法参数定义"""
    name: str
    param_type: ParameterType
    description: str
    default_value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[List[str]] = None  # 用于SELECT类型
    required: bool = True


@dataclass
class AlgorithmInput:
    """算法输入数据类"""
    # 信号数据
    lfp_data: Optional[np.ndarray] = None  # [通道数 × 样本数]
    spike_times: Optional[np.ndarray] = None
    spike_waveforms: Optional[np.ndarray] = None
    spike_elec_ids: Optional[np.ndarray] = None
    
    # 行为数据
    trial_info: Optional[List[Dict]] = None
    events: Optional[List[Dict]] = None
    
    # 元数据
    sampling_rate: float = 2000.0
    duration: float = 0.0
    num_channels: int = 0
    
    # 时间对齐配置
    time_range: Optional[tuple] = None  # (start, end) in seconds
    trial_indices: Optional[List[int]] = None  # 选中的试次索引
    
    # 额外数据
    extra_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlgorithmOutput:
    """算法输出数据类"""
    # 分析结果
    data: Dict[str, np.ndarray] = field(default_factory=dict)
    statistics: Dict[str, float] = field(default_factory=dict)
    
    # 图表配置
    plot_config: Dict[str, Any] = field(default_factory=dict)
    
    # 导出数据
    export_data: Dict[str, np.ndarray] = field(default_factory=dict)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 执行信息
    execution_time: float = 0.0
    success: bool = True
    error_message: str = ""


class BaseAlgorithm(ABC):
    """
    算法抽象基类
    
    所有分析算法必须继承此类并实现以下方法：
    - get_parameters_schema(): 返回参数模式定义
    - validate_input(): 验证输入数据
    - run(): 执行算法
    
    用法:
        class MyAlgorithm(BaseAlgorithm):
            def get_parameters_schema(self):
                return [...]
            
            def validate_input(self, input_data):
                return True
            
            def run(self, input_data, parameters):
                # 实现算法逻辑
                return AlgorithmOutput(...)
    """
    
    def __init__(self):
        """初始化算法"""
        self.name = self.__class__.__name__
        self.description = ""
        self.version = "1.0"
        self.category = "General"  # 算法分类
        self._execution_history: List[Dict] = []
        
        # 数据需求定义
        # required_data_types: 列表，可包含 'lfp', 'spike', 'behavior' 等
        # data_requirements_description: 人类可读的描述
        self.required_data_types: List[str] = []
        self.data_requirements_description: str = ""
    
    def get_data_requirements(self) -> Dict[str, Any]:
        """
        获取算法的数据需求信息
        
        Returns:
            包含数据需求的字典
        """
        return {
            'required_types': self.required_data_types,
            'description': self.data_requirements_description,
            'requires_trial_info': 'behavior' in self.required_data_types or 'spike' in self.required_data_types
        }
    
    @abstractmethod
    def get_parameters_schema(self) -> List[AlgorithmParameter]:
        """
        获取算法参数模式定义
        
        Returns:
            参数定义列表
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        """
        验证输入数据
        
        Args:
            input_data: 算法输入数据
            
        Returns:
            True if valid
        """
        pass
    
    @abstractmethod
    def run(self, input_data: AlgorithmInput, 
            parameters: Dict[str, Any]) -> AlgorithmOutput:
        """
        执行算法
        
        Args:
            input_data: 算法输入数据
            parameters: 算法参数
            
        Returns:
            算法输出结果
        """
        pass
    
    def get_default_parameters(self) -> Dict[str, Any]:
        """
        获取默认参数值
        
        Returns:
            参数名 -> 默认值 的字典
        """
        schema = self.get_parameters_schema()
        return {p.name: p.default_value for p in schema}
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> tuple:
        """
        验证参数值
        
        Args:
            parameters: 参数字典
            
        Returns:
            (is_valid, error_messages)
        """
        schema = self.get_parameters_schema()
        errors = []
        
        for param in schema:
            # 检查必需参数
            if param.required and param.name not in parameters:
                errors.append(f"Missing required parameter: {param.name}")
                continue
            
            if param.name not in parameters:
                continue
            
            value = parameters[param.name]
            
            # 类型检查
            if param.param_type == ParameterType.INTEGER:
                if not isinstance(value, (int, np.integer)):
                    errors.append(f"Parameter '{param.name}' must be an integer")
                    continue
            elif param.param_type == ParameterType.FLOAT:
                if not isinstance(value, (int, float, np.number)):
                    errors.append(f"Parameter '{param.name}' must be a number")
                    continue
            elif param.param_type == ParameterType.BOOLEAN:
                if not isinstance(value, bool):
                    errors.append(f"Parameter '{param.name}' must be a boolean")
                    continue
            elif param.param_type == ParameterType.SELECT:
                if param.options and value not in param.options:
                    errors.append(f"Parameter '{param.name}' must be one of {param.options}")
                    continue
            
            # 范围检查
            if param.min_value is not None and value < param.min_value:
                errors.append(f"Parameter '{param.name}' must be >= {param.min_value}")
            
            if param.max_value is not None and value > param.max_value:
                errors.append(f"Parameter '{param.name}' must be <= {param.max_value}")
        
        return len(errors) == 0, errors
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取算法信息
        
        Returns:
            算法信息字典
        """
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'category': self.category,
            'parameters': [
                {
                    'name': p.name,
                    'type': p.param_type.value,
                    'description': p.description,
                    'default': p.default_value,
                    'required': p.required
                }
                for p in self.get_parameters_schema()
            ]
        }
    
    def _record_execution(self, input_data: AlgorithmInput, 
                         parameters: Dict[str, Any],
                         output: AlgorithmOutput):
        """记录算法执行历史"""
        import time
        from datetime import datetime
        
        self._execution_history.append({
            'timestamp': datetime.now().isoformat(),
            'parameters': parameters,
            'execution_time': output.execution_time,
            'success': output.success
        })
    
    def prepare_visualization_data(self, input_data: AlgorithmInput) -> Dict[str, Any]:
        """
        准备可视化数据
        
        Args:
            input_data: 算法输入数据
            
        Returns:
            可视化数据字典
        """
        import numpy as np
        output_data = {}
        
        if input_data.lfp_data is not None:
            # 准备LFP数据的可视化
            output_data['signal_data'] = input_data.lfp_data
            output_data['sampling_rate'] = input_data.sampling_rate
            # 生成时间轴
            times = np.arange(input_data.lfp_data.shape[1]) / input_data.sampling_rate
            output_data['times'] = times
            output_data['plot_type'] = 'raw_signal'
        elif input_data.spike_times:
            # 准备Spike数据的可视化
            output_data['spike_times'] = input_data.spike_times
            output_data['trial_info'] = input_data.trial_info
            output_data['plot_type'] = 'spike_raster'
        
        return output_data


# 便捷函数
def create_parameter(name: str, param_type: ParameterType,
                    description: str, default_value: Any,
                    **kwargs) -> AlgorithmParameter:
    """
    创建算法参数的便捷函数
    
    Args:
        name: 参数名
        param_type: 参数类型
        description: 参数描述
        default_value: 默认值
        **kwargs: 其他参数
        
    Returns:
        AlgorithmParameter对象
    """
    return AlgorithmParameter(
        name=name,
        param_type=param_type,
        description=description,
        default_value=default_value,
        **kwargs
    )


if __name__ == '__main__':
    # 测试代码
    print("=== Testing BaseAlgorithm ===\n")
    
    # 创建一个测试算法
    class TestAlgorithm(BaseAlgorithm):
        def __init__(self):
            super().__init__()
            self.description = "A test algorithm"
            self.category = "Test"
        
        def get_parameters_schema(self):
            return [
                create_parameter(
                    "threshold", ParameterType.FLOAT,
                    "Detection threshold", 3.5,
                    min_value=0.1, max_value=10.0
                ),
                create_parameter(
                    "window_size", ParameterType.INTEGER,
                    "Window size in ms", 50,
                    min_value=10, max_value=200
                ),
                create_parameter(
                    "use_filter", ParameterType.BOOLEAN,
                    "Apply filter", True
                ),
                create_parameter(
                    "method", ParameterType.SELECT,
                    "Analysis method", "method1",
                    options=["method1", "method2", "method3"]
                )
            ]
        
        def validate_input(self, input_data):
            return input_data.lfp_data is not None
        
        def run(self, input_data, parameters):
            import time
            start_time = time.time()
            
            # 模拟算法执行
            result_data = np.random.randn(100, 100)
            
            execution_time = time.time() - start_time
            
            return AlgorithmOutput(
                data={'result': result_data},
                statistics={'mean': np.mean(result_data), 'std': np.std(result_data)},
                execution_time=execution_time,
                success=True
            )
    
    # 测试算法
    algo = TestAlgorithm()
    
    print("1. Algorithm info:")
    info = algo.get_info()
    print(f"   Name: {info['name']}")
    print(f"   Description: {info['description']}")
    print(f"   Category: {info['category']}")
    print(f"   Parameters:")
    for param in info['parameters']:
        print(f"     - {param['name']} ({param['type']}): {param['description']}")
    print()
    
    print("2. Default parameters:")
    defaults = algo.get_default_parameters()
    for name, value in defaults.items():
        print(f"   {name}: {value}")
    print()
    
    print("3. Parameter validation:")
    # 有效参数
    valid_params = {'threshold': 5.0, 'window_size': 100, 'use_filter': False, 'method': 'method2'}
    is_valid, errors = algo.validate_parameters(valid_params)
    print(f"   Valid params: {is_valid}")
    
    # 无效参数
    invalid_params = {'threshold': 15.0, 'window_size': 5, 'method': 'invalid_method'}
    is_valid, errors = algo.validate_parameters(invalid_params)
    print(f"   Invalid params: {is_valid}")
    print(f"   Errors: {errors}")
    print()
    
    print("4. Run algorithm:")
    input_data = AlgorithmInput(
        lfp_data=np.random.randn(10, 1000),
        sampling_rate=2000.0
    )
    output = algo.run(input_data, valid_params)
    print(f"   Success: {output.success}")
    print(f"   Execution time: {output.execution_time:.4f}s")
    print(f"   Output data shape: {output.data['result'].shape}")
    print(f"   Statistics: {output.statistics}")
    print()
    
    print("✅ BaseAlgorithm tests completed!")
