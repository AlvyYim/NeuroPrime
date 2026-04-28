"""
Algorithm Scheduler - 算法调度器

管理算法的注册、调度和执行历史
"""

import sys
import time
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
from datetime import datetime

try:
    from .base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput
except ImportError:
    from base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput

# 尝试导入logger
try:
    from utils.debug_logger import get_logger
    logger = get_logger()
except ImportError:
    # 如果logger不可用，使用print
    class DummyLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def debug(self, msg): print(f"[DEBUG] {msg}")
    logger = DummyLogger()


class AlgorithmScheduler:
    """
    算法调度器
    
    管理所有分析算法的生命周期：
    - 注册内置算法
    - 加载自定义算法
    - 执行算法
    - 管理算法执行历史
    
    用法:
        scheduler = AlgorithmScheduler()
        
        # 注册内置算法
        scheduler.register_builtin_algorithms()
        
        # 获取可用算法列表
        algorithms = scheduler.get_available_algorithms()
        
        # 执行算法
        output = scheduler.run_algorithm("PSTHAnalysis", input_data, parameters)
    """
    
    def __init__(self):
        """初始化算法调度器"""
        self._algorithms: Dict[str, BaseAlgorithm] = {}
        self._execution_history: List[Dict[str, Any]] = []
        self._current_execution_id: int = 0
    
    def register_algorithm(self, algorithm: BaseAlgorithm) -> bool:
        """
        注册算法
        
        Args:
            algorithm: 算法实例
            
        Returns:
            True if successful
        """
        name = algorithm.name
        
        if name in self._algorithms:
            print(f"Warning: Algorithm '{name}' already registered, overwriting")
        
        self._algorithms[name] = algorithm
        return True
    
    def register_algorithm_class(self, algorithm_class: Type[BaseAlgorithm]) -> bool:
        """
        注册算法类
        
        Args:
            algorithm_class: 算法类
            
        Returns:
            True if successful
        """
        try:
            # 跳过抽象基类（如BaseAlgorithm本身）
            import inspect
            if inspect.isabstract(algorithm_class):
                logger.debug(f"Skipping abstract class: {algorithm_class.__name__}")
                return False
            
            algorithm = algorithm_class()
            return self.register_algorithm(algorithm)
        except Exception as e:
            print(f"Error registering algorithm class {algorithm_class.__name__}: {e}")
            return False
    
    def register_builtin_algorithms(self):
        """注册所有内置算法"""
        try:
            # Spike检测和排序算法
            from .spike_detection import SpikeDetectionThreshold, SpikeSortingPCA
            self.register_algorithm_class(SpikeDetectionThreshold)
            self.register_algorithm_class(SpikeSortingPCA)
            
            # LFP分析算法
            from .lfp_analysis import LFPPowerSpectrum, LFPSpectrogram
            self.register_algorithm_class(LFPPowerSpectrum)
            self.register_algorithm_class(LFPSpectrogram)
            
            # Spike分析算法
            from .spike_analysis import PSTHAnalysis, RasterPlotAnalysis, TuningCurveAnalysis
            self.register_algorithm_class(PSTHAnalysis)
            self.register_algorithm_class(RasterPlotAnalysis)
            self.register_algorithm_class(TuningCurveAnalysis)
            
            # 行为分析算法
            from .behavior_analysis import ROCAnalysis
            self.register_algorithm_class(ROCAnalysis)
            
            # 解码算法
            from .decoding import LDADecoder, SVMClassifier, RandomForestClassifier
            self.register_algorithm_class(LDADecoder)
            self.register_algorithm_class(SVMClassifier)
            self.register_algorithm_class(RandomForestClassifier)
            
            print(f"Registered {len(self._algorithms)} builtin algorithms")
            
            # 加载自定义算法
            self._load_custom_algorithms()
            
        except Exception as e:
            print(f"Error registering builtin algorithms: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_custom_algorithms(self):
        """加载自定义算法"""
        try:
            # 清除模块缓存，确保删除的算法不会被重新加载
            import sys
            # 清除所有可能的自定义算法模块
            modules_to_remove = []
            for module_name in list(sys.modules.keys()):
                # 清除所有可能的自定义算法模块
                # 包括文件名模块和类名模块
                if (module_name in ['aaaa', 'bbbb', 'cccc', 'CustomAlgorithm', 'CustomAlgorithmTest', 'New', 'newnew', 'newnewnew', 'newnewnewnewnewn', 'ViewRawLFPData'] or 
                    module_name.startswith('customalgorithm') or 
                    module_name.startswith('new') or 
                    module_name.startswith('view_raw')):
                    modules_to_remove.append(module_name)
            
            # 清除所有pycache文件
            import shutil
            pycache_dir = Path(__file__).parent.parent.parent / "custom_algorithms" / "__pycache__"
            if pycache_dir.exists():
                shutil.rmtree(pycache_dir)
                logger.info(f"[Scheduler] Removed pycache directory: {pycache_dir}")
            
            for module_name in modules_to_remove:
                if module_name in sys.modules:
                    del sys.modules[module_name]
                    logger.info(f"[Scheduler] Removed module from cache: {module_name}")
            
            # 获取自定义算法目录 - 使用绝对路径
            # 尝试多种方式找到custom_algorithms目录
            possible_paths = []
            
            # 首先尝试从环境变量获取项目根目录
            import os
            neuroprime_root = os.environ.get('NEUROPRIME_ROOT')
            if neuroprime_root:
                possible_paths.append(Path(neuroprime_root) / "custom_algorithms")
            
            # 其他可能的路径
            possible_paths.extend([
                Path(__file__).parent.parent.parent / "custom_algorithms",  # 相对于scheduler.py
                Path.cwd() / "custom_algorithms",  # 相对于当前工作目录
            ])
            
            custom_algorithms_dir = None
            for path in possible_paths:
                if path and path.exists():
                    custom_algorithms_dir = path
                    break
            
            # 如果都找不到，使用默认路径
            if custom_algorithms_dir is None:
                custom_algorithms_dir = Path(__file__).parent.parent.parent / "custom_algorithms"
            
            logger.info(f"[Scheduler] NEUROPRIME_ROOT = {neuroprime_root}")
            logger.info(f"[Scheduler] Looking for custom algorithms in: {custom_algorithms_dir}")
            logger.info(f"[Scheduler] Current working directory: {Path.cwd()}")
            logger.info(f"[Scheduler] Script directory: {Path(__file__).parent}")
            
            if not custom_algorithms_dir.exists():
                logger.error(f"[Scheduler] Custom algorithms directory not found: {custom_algorithms_dir}")
                return
            
            logger.info(f"[Scheduler] Custom algorithms directory exists: {custom_algorithms_dir}")
            
            # 遍历所有Python文件
            py_files = list(custom_algorithms_dir.glob("*.py"))
            logger.info(f"[Scheduler] Found {len(py_files)} Python files: {[f.name for f in py_files]}")
            
            for py_file in py_files:
                if py_file.name.startswith("__"):
                    continue
                
                logger.info(f"[Scheduler] Loading custom algorithm from: {py_file}")
                
                try:
                    # 动态加载模块
                    spec = importlib.util.spec_from_file_location(
                        py_file.stem, py_file
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 检查是否有ALGORITHM_INFO字典
                    if hasattr(module, 'ALGORITHM_INFO'):
                        algo_info = module.ALGORITHM_INFO
                        algorithm_class = algo_info.get('class')
                        
                        # 检查类是否有效（通过检查是否有get_parameters_schema方法）
                        if algorithm_class and hasattr(algorithm_class, 'get_parameters_schema'):
                            self.register_algorithm_class(algorithm_class)
                            logger.info(f"[Scheduler] Loaded custom algorithm from ALGORITHM_INFO: {algo_info.get('name', py_file.stem)}")
                        else:
                            logger.error(f"[Scheduler] ALGORITHM_INFO found but class not valid: {algorithm_class}")
                    
                    # 只有当ALGORITHM_INFO不存在时，才尝试查找BaseAlgorithm的子类
                    if not hasattr(module, 'ALGORITHM_INFO'):
                        logger.info(f"[Scheduler] Searching for algorithm classes in {py_file}...")
                        found = False
                        for name, obj in inspect.getmembers(module):
                            if inspect.isclass(obj):
                                # 跳过BaseAlgorithm基类本身（通过名称检查，因为导入路径可能不同）
                                if name == 'BaseAlgorithm' or obj.__name__ == 'BaseAlgorithm':
                                    continue
                                # 跳过抽象类
                                if inspect.isabstract(obj):
                                    continue
                                # 检查类名是否以Algorithm结尾或者有get_parameters_schema方法
                                if hasattr(obj, 'get_parameters_schema') and callable(getattr(obj, 'get_parameters_schema')):
                                    try:
                                        self.register_algorithm_class(obj)
                                        logger.info(f"[Scheduler] Loaded custom algorithm: {name}")
                                        found = True
                                        # 只加载第一个找到的算法类
                                        break
                                    except Exception as reg_e:
                                        logger.error(f"[Scheduler] Failed to register {name}: {reg_e}")
                    
                    if not found:
                        logger.error(f"[Scheduler] No valid algorithm class found in {py_file}")
                                
                except Exception as e:
                    logger.error(f"[Scheduler] Error loading custom algorithm from {py_file}: {e}")
                    import traceback
                    logger.error(f"[Scheduler] Traceback: {traceback.format_exc()}")
                    
        except Exception as e:
            logger.error(f"[Scheduler] Error loading custom algorithms: {e}")
            import traceback
            logger.error(f"[Scheduler] Traceback: {traceback.format_exc()}")
    
    def load_custom_algorithm(self, file_path: str, class_name: str) -> bool:
        """
        从Python文件加载自定义算法
        
        Args:
            file_path: Python文件路径
            class_name: 算法类名
            
        Returns:
            True if successful
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                print(f"Error: File not found: {file_path}")
                return False
            
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(
                file_path.stem, file_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取算法类
            if not hasattr(module, class_name):
                print(f"Error: Class '{class_name}' not found in {file_path}")
                return False
            
            algorithm_class = getattr(module, class_name)
            
            # 检查是否继承自BaseAlgorithm
            if not issubclass(algorithm_class, BaseAlgorithm):
                print(f"Error: Class '{class_name}' must inherit from BaseAlgorithm")
                return False
            
            # 注册算法
            return self.register_algorithm_class(algorithm_class)
            
        except Exception as e:
            print(f"Error loading custom algorithm: {e}")
            return False
    
    def unregister_algorithm(self, name: str) -> bool:
        """
        注销算法
        
        Args:
            name: 算法名称
            
        Returns:
            True if successful
        """
        if name not in self._algorithms:
            print(f"Warning: Algorithm '{name}' not found")
            return False
        
        del self._algorithms[name]
        return True
    
    def get_algorithm(self, name: str) -> Optional[BaseAlgorithm]:
        """
        获取算法实例
        
        Args:
            name: 算法名称
            
        Returns:
            算法实例，未找到返回None
        """
        return self._algorithms.get(name)
    
    def get_algorithm_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取算法信息
        
        Args:
            name: 算法名称
            
        Returns:
            算法信息字典，未找到返回None
        """
        algorithm = self._algorithms.get(name)
        if algorithm:
            return algorithm.get_info()
        return None
    
    def get_available_algorithms(self) -> List[Dict[str, Any]]:
        """
        获取所有可用算法的信息
        
        Returns:
            算法信息列表
        """
        return [algo.get_info() for algo in self._algorithms.values()]
    
    def get_algorithms_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        获取特定分类的算法
        
        Args:
            category: 算法分类
            
        Returns:
            算法信息列表
        """
        return [
            algo.get_info()
            for algo in self._algorithms.values()
            if algo.category == category
        ]
    
    def get_categories(self) -> List[str]:
        """
        获取所有算法分类
        
        Returns:
            分类列表
        """
        categories = set()
        for algo in self._algorithms.values():
            categories.add(algo.category)
        return sorted(list(categories))
    
    def run_algorithm(self, name: str, input_data: AlgorithmInput,
                     parameters: Optional[Dict[str, Any]] = None) -> AlgorithmOutput:
        """
        执行算法
        
        Args:
            name: 算法名称
            input_data: 算法输入数据
            parameters: 算法参数（None使用默认值）
            
        Returns:
            算法输出结果
        """
        # 获取算法
        algorithm = self.get_algorithm(name)
        if algorithm is None:
            return AlgorithmOutput(
                success=False,
                error_message=f"Algorithm '{name}' not found"
            )
        
        # 使用默认参数
        if parameters is None:
            parameters = algorithm.get_default_parameters()
        
        # 验证参数
        is_valid, errors = algorithm.validate_parameters(parameters)
        if not is_valid:
            return AlgorithmOutput(
                success=False,
                error_message=f"Invalid parameters: {', '.join(errors)}"
            )
        
        # 验证输入数据
        if not algorithm.validate_input(input_data):
            return AlgorithmOutput(
                success=False,
                error_message="Invalid input data"
            )
        
        # 生成执行ID
        self._current_execution_id += 1
        execution_id = self._current_execution_id
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 执行算法
            output = algorithm.run(input_data, parameters)
            
            # 计算执行时间
            execution_time = time.time() - start_time
            output.execution_time = execution_time
            
            # 记录执行历史
            self._record_execution(execution_id, name, parameters, output)
            
            return output
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            output = AlgorithmOutput(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
            
            # 记录失败
            self._record_execution(execution_id, name, parameters, output)
            
            return output
    
    def _record_execution(self, execution_id: int, algorithm_name: str,
                         parameters: Dict[str, Any], output: AlgorithmOutput):
        """记录算法执行历史"""
        self._execution_history.append({
            'execution_id': execution_id,
            'algorithm_name': algorithm_name,
            'timestamp': datetime.now().isoformat(),
            'parameters': parameters,
            'success': output.success,
            'execution_time': output.execution_time,
            'error_message': output.error_message if not output.success else None
        })
    
    def get_execution_history(self, algorithm_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取算法执行历史
        
        Args:
            algorithm_name: 算法名称筛选（None=所有）
            
        Returns:
            执行历史列表
        """
        if algorithm_name is None:
            return self._execution_history.copy()
        
        return [
            record for record in self._execution_history
            if record['algorithm_name'] == algorithm_name
        ]
    
    def clear_history(self):
        """清除执行历史"""
        self._execution_history.clear()
        self._current_execution_id = 0
    
    def get_algorithm_count(self) -> int:
        """获取已注册算法数量"""
        return len(self._algorithms)
    
    def get_algorithms(self) -> Dict[str, BaseAlgorithm]:
        """
        获取所有已注册的算法
        
        Returns:
            算法名称到算法实例的映射
        """
        return self._algorithms


if __name__ == '__main__':
    # 测试代码
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from algorithms.base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput
    from algorithms.base import ParameterType, create_parameter
    
    print("=== Testing AlgorithmScheduler ===\n")
    
    # 创建测试算法类
    class TestAlgorithm1(BaseAlgorithm):
        def __init__(self):
            super().__init__()
            self.description = "Test algorithm 1"
            self.category = "Test"
        
        def get_parameters_schema(self):
            return [
                create_parameter("param1", ParameterType.FLOAT, "Parameter 1", 1.0),
                create_parameter("param2", ParameterType.INTEGER, "Parameter 2", 10)
            ]
        
        def validate_input(self, input_data):
            return True
        
        def run(self, input_data, parameters):
            time.sleep(0.01)  # 模拟执行时间
            return AlgorithmOutput(
                data={'result': [1, 2, 3]},
                success=True
            )
    
    class TestAlgorithm2(BaseAlgorithm):
        def __init__(self):
            super().__init__()
            self.description = "Test algorithm 2"
            self.category = "Analysis"
        
        def get_parameters_schema(self):
            return [
                create_parameter("threshold", ParameterType.FLOAT, "Threshold", 0.5)
            ]
        
        def validate_input(self, input_data):
            return True
        
        def run(self, input_data, parameters):
            return AlgorithmOutput(
                data={'result': [4, 5, 6]},
                success=True
            )
    
    # 创建调度器
    scheduler = AlgorithmScheduler()
    
    print("1. Registering algorithms...")
    scheduler.register_algorithm_class(TestAlgorithm1)
    scheduler.register_algorithm_class(TestAlgorithm2)
    print(f"   Registered {scheduler.get_algorithm_count()} algorithms\n")
    
    print("2. Available algorithms:")
    for algo_info in scheduler.get_available_algorithms():
        print(f"   - {algo_info['name']} ({algo_info['category']}): {algo_info['description']}")
    print()
    
    print("3. Categories:")
    categories = scheduler.get_categories()
    print(f"   {categories}\n")
    
    print("4. Running algorithms...")
    input_data = AlgorithmInput()
    
    # 运行第一个算法
    output1 = scheduler.run_algorithm("TestAlgorithm1", input_data)
    print(f"   TestAlgorithm1: success={output1.success}, time={output1.execution_time:.4f}s")
    
    # 运行第二个算法
    output2 = scheduler.run_algorithm("TestAlgorithm2", input_data, {'threshold': 0.8})
    print(f"   TestAlgorithm2: success={output2.success}, time={output2.execution_time:.4f}s")
    
    # 运行不存在的算法
    output3 = scheduler.run_algorithm("NonExistent", input_data)
    print(f"   NonExistent: success={output3.success}, error={output3.error_message}")
    print()
    
    print("5. Execution history:")
    history = scheduler.get_execution_history()
    for record in history:
        print(f"   - {record['algorithm_name']} at {record['timestamp']}: "
              f"success={record['success']}, time={record['execution_time']:.4f}s")
    print()
    
    print("6. Algorithm by category 'Test':")
    test_algos = scheduler.get_algorithms_by_category("Test")
    for algo in test_algos:
        print(f"   - {algo['name']}")
    print()
    
    print("✅ AlgorithmScheduler tests completed!")
