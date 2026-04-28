"""
Project Manager - 工程管理模块

管理NeuroPrime工程的创建、打开、保存和试验数据管理
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class TrialInfo:
    """试验信息数据类"""
    name: str
    experiment_name: str
    creation_time: str
    hdf5_file: str
    source_files: Dict[str, str] = field(default_factory=dict)
    duration: float = 0.0
    num_channels: int = 0
    sampling_rate: float = 0.0
    num_trials: int = 0
    num_spikes: int = 0
    description: str = ""


@dataclass
class ProjectConfig:
    """工程配置数据类"""
    name: str
    creation_time: str
    last_modified: str
    version: str = "1.0"
    description: str = ""
    trials: List[TrialInfo] = field(default_factory=list)


class ProjectManager:
    """
    工程管理器
    
    负责NeuroPrime工程的完整生命周期管理：
    - 新建工程（创建文件夹结构和project.json）
    - 打开工程（读取project.json）
    - 保存工程（更新project.json）
    - 添加/删除试验
    - 管理工程文件
    
    工程结构:
    {project_name}/
    ├── project.json          # 工程配置文件
    ├── Document/             # 文档目录
    ├── Backup/               # 备份目录
    ├── src/                  # 源代码目录
    └── data/                 # 数据目录
        ├── raw/              # 原始数据
        └── processed/        # 处理后数据(HDF5)
    """
    
    def __init__(self):
        """初始化工程管理器"""
        self.project_path: Optional[Path] = None
        self.config: Optional[ProjectConfig] = None
        self._is_modified = False
    
    def create_project(self, project_path: str, name: str, 
                       description: str = "") -> bool:
        """
        创建新工程
        
        Args:
            project_path: 工程根目录路径
            name: 工程名称
            description: 工程描述
            
        Returns:
            True if successful
        """
        try:
            project_path = Path(project_path)
            
            # 检查目录是否已存在
            if project_path.exists():
                print(f"Error: Directory already exists: {project_path}")
                return False
            
            # 创建工程目录结构
            self._create_directory_structure(project_path)
            
            # 创建工程配置
            now = datetime.now().isoformat()
            self.config = ProjectConfig(
                name=name,
                creation_time=now,
                last_modified=now,
                description=description
            )
            
            self.project_path = project_path
            self._is_modified = True
            
            # 保存工程配置
            return self.save_project()
            
        except Exception as e:
            print(f"Error creating project: {e}")
            return False
    
    def open_project(self, project_path: str) -> bool:
        """
        打开已有工程
        
        Args:
            project_path: 工程根目录路径
            
        Returns:
            True if successful
        """
        try:
            project_path = Path(project_path)
            config_file = project_path / "project.json"
            
            # 检查工程文件是否存在
            if not config_file.exists():
                print(f"Error: Project file not found: {config_file}")
                return False
            
            # 读取工程配置
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 解析试验列表
            trials = []
            for trial_data in data.get('trials', []):
                trials.append(TrialInfo(**trial_data))
            
            # 创建配置对象
            self.config = ProjectConfig(
                name=data.get('name', 'Unknown'),
                creation_time=data.get('creation_time', ''),
                last_modified=data.get('last_modified', ''),
                version=data.get('version', '1.0'),
                description=data.get('description', ''),
                trials=trials
            )
            
            self.project_path = project_path
            self._is_modified = False
            
            print(f"Project opened: {self.config.name}")
            print(f"  Trials: {len(self.config.trials)}")
            return True
            
        except Exception as e:
            print(f"Error opening project: {e}")
            return False
    
    def save_project(self) -> bool:
        """
        保存工程配置
        
        Returns:
            True if successful
        """
        if self.config is None or self.project_path is None:
            print("Error: No project to save")
            return False
        
        try:
            # 更新最后修改时间
            self.config.last_modified = datetime.now().isoformat()
            
            # 转换为字典
            config_dict = asdict(self.config)
            
            # 保存为JSON
            config_file = self.project_path / "project.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            self._is_modified = False
            return True
            
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
    
    def add_trial(self, trial_info: TrialInfo) -> bool:
        """
        添加试验到工程
        
        Args:
            trial_info: 试验信息
            
        Returns:
            True if successful
        """
        if self.config is None:
            print("Error: No project opened")
            return False
        
        # 检查试验名称是否已存在
        for trial in self.config.trials:
            if trial.name == trial_info.name:
                print(f"Error: Trial '{trial_info.name}' already exists")
                return False
        
        # 添加试验
        self.config.trials.append(trial_info)
        self._is_modified = True
        
        return self.save_project()
    
    def remove_trial(self, trial_name: str) -> bool:
        """
        从工程中删除试验
        
        Args:
            trial_name: 试验名称
            
        Returns:
            True if successful
        """
        if self.config is None:
            print("Error: No project opened")
            return False
        
        # 查找试验
        trial_to_remove = None
        for trial in self.config.trials:
            if trial.name == trial_name:
                trial_to_remove = trial
                break
        
        if trial_to_remove is None:
            print(f"Error: Trial '{trial_name}' not found")
            return False
        
        # 删除HDF5文件
        if self.project_path:
            hdf5_path = self.project_path / "data" / "processed" / trial_to_remove.hdf5_file
            if hdf5_path.exists():
                hdf5_path.unlink()
        
        # 从列表中移除
        self.config.trials.remove(trial_to_remove)
        self._is_modified = True
        
        return self.save_project()
    
    def get_trial(self, trial_name: str) -> Optional[TrialInfo]:
        """
        获取试验信息
        
        Args:
            trial_name: 试验名称
            
        Returns:
            TrialInfo对象，未找到返回None
        """
        if self.config is None:
            return None
        
        for trial in self.config.trials:
            if trial.name == trial_name:
                return trial
        
        return None
    
    def get_all_trials(self) -> List[TrialInfo]:
        """
        获取所有试验列表
        
        Returns:
            试验信息列表
        """
        if self.config is None:
            return []
        return self.config.trials.copy()
    
    def get_trial_names(self) -> List[str]:
        """
        获取所有试验名称
        
        Returns:
            试验名称列表
        """
        if self.config is None:
            return []
        return [trial.name for trial in self.config.trials]
    
    def get_project_info(self) -> Dict[str, Any]:
        """
        获取工程信息
        
        Returns:
            工程信息字典
        """
        if self.config is None:
            return {}
        
        return {
            'name': self.config.name,
            'path': str(self.project_path) if self.project_path else None,
            'creation_time': self.config.creation_time,
            'last_modified': self.config.last_modified,
            'version': self.config.version,
            'description': self.config.description,
            'num_trials': len(self.config.trials),
            'is_modified': self._is_modified
        }
    
    def get_hdf5_path(self, trial_name: str) -> Optional[Path]:
        """
        获取试验的HDF5文件路径
        
        Args:
            trial_name: 试验名称
            
        Returns:
            HDF5文件路径，未找到返回None
        """
        trial = self.get_trial(trial_name)
        if trial is None or self.project_path is None:
            return None
        
        return self.project_path / "data" / "processed" / trial.hdf5_file
    
    def remove_trial_data(self, trial_name: str, data_category: str) -> bool:
        """
        删除试验中的特定数据类别
        
        Args:
            trial_name: 试验名称
            data_category: 数据类别 ('signals', 'spikes', 'behavior')
            
        Returns:
            True if successful
        """
        if self.config is None:
            print("Error: No project opened")
            return False
        
        trial = self.get_trial(trial_name)
        if trial is None:
            print(f"Error: Trial '{trial_name}' not found")
            return False
        
        hdf5_path = self.get_hdf5_path(trial_name)
        if hdf5_path is None or not hdf5_path.exists():
            print(f"Error: HDF5 file not found for trial '{trial_name}'")
            return False
        
        try:
            import h5py
            
            # 映射数据类别到HDF5中的组名
            category_mapping = {
                'signals': 'signals',
                'spikes': 'spikes',
                'behavior': 'behavior'
            }
            
            group_name = category_mapping.get(data_category)
            if group_name is None:
                print(f"Error: Unknown data category '{data_category}'")
                return False
            
            # 打开HDF5文件并删除对应的数据组
            with h5py.File(hdf5_path, 'a') as f:
                if group_name in f:
                    del f[group_name]
                    print(f"Deleted {group_name} from {hdf5_path}")
                else:
                    print(f"Warning: {group_name} not found in HDF5 file")
            
            self._is_modified = True
            return self.save_project()
            
        except Exception as e:
            print(f"Error removing trial data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def close_project(self):
        """关闭当前工程"""
        if self._is_modified:
            self.save_project()
        
        self.project_path = None
        self.config = None
        self._is_modified = False
    
    def is_project_opened(self) -> bool:
        """检查是否有工程已打开"""
        return self.project_path is not None and self.config is not None
    
    def _create_directory_structure(self, project_path: Path):
        """创建工程目录结构"""
        # 创建主目录
        project_path.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (project_path / "Document").mkdir(exist_ok=True)
        (project_path / "Backup").mkdir(exist_ok=True)
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "data").mkdir(exist_ok=True)
        (project_path / "data" / "raw").mkdir(exist_ok=True)
        (project_path / "data" / "processed").mkdir(exist_ok=True)
    
    def backup_project(self, backup_path: Optional[str] = None) -> bool:
        """
        备份工程
        
        Args:
            backup_path: 备份路径，默认为工程目录下的Backup文件夹
            
        Returns:
            True if successful
        """
        if self.project_path is None:
            print("Error: No project opened")
            return False
        
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{self.config.name}_{timestamp}"
                backup_path = self.project_path / "Backup" / backup_name
            else:
                backup_path = Path(backup_path)
            
            # 创建备份
            shutil.copytree(self.project_path, backup_path, 
                          ignore=shutil.ignore_patterns('Backup'))
            
            print(f"Project backed up to: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Error backing up project: {e}")
            return False


def create_project(project_path: str, name: str, description: str = "") -> bool:
    """
    便捷函数：创建新工程
    
    Args:
        project_path: 工程根目录路径
        name: 工程名称
        description: 工程描述
        
    Returns:
        True if successful
    """
    manager = ProjectManager()
    return manager.create_project(project_path, name, description)


if __name__ == '__main__':
    # 测试代码
    import tempfile
    import os
    
    # 创建临时目录用于测试
    test_dir = tempfile.mkdtemp()
    project_path = Path(test_dir) / "TestProject"
    
    print("=== Testing ProjectManager ===\n")
    
    # 测试创建工程
    print("1. Creating new project...")
    manager = ProjectManager()
    success = manager.create_project(project_path, "TestProject", "A test project")
    print(f"   Result: {'✓ Success' if success else '✗ Failed'}\n")
    
    if success:
        # 显示工程结构
        print("2. Project structure:")
        for item in sorted(project_path.rglob("*")):
            level = len(item.relative_to(project_path).parts)
            indent = "   " * level
            print(f"{indent}{item.name}/" if item.is_dir() else f"{indent}{item.name}")
        print()
        
        # 测试添加试验
        print("3. Adding trials...")
        trial1 = TrialInfo(
            name="FC_Grating_014",
            experiment_name="FC_Grating",
            creation_time=datetime.now().isoformat(),
            hdf5_file="FC_Grating_014.h5",
            duration=84.812,
            num_channels=101,
            sampling_rate=2000.0,
            num_trials=61,
            num_spikes=150496
        )
        success = manager.add_trial(trial1)
        print(f"   Added trial 'FC_Grating_014': {'✓ Success' if success else '✗ Failed'}")
        
        trial2 = TrialInfo(
            name="FC_Grating_015",
            experiment_name="FC_Grating",
            creation_time=datetime.now().isoformat(),
            hdf5_file="FC_Grating_015.h5",
            duration=90.5,
            num_channels=101,
            sampling_rate=2000.0,
            num_trials=65,
            num_spikes=160000
        )
        success = manager.add_trial(trial2)
        print(f"   Added trial 'FC_Grating_015': {'✓ Success' if success else '✗ Failed'}\n")
        
        # 测试获取工程信息
        print("4. Project info:")
        info = manager.get_project_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        print()
        
        # 测试获取试验列表
        print("5. Trial list:")
        trials = manager.get_all_trials()
        for trial in trials:
            print(f"   - {trial.name}: {trial.experiment_name}, "
                  f"{trial.duration:.2f}s, {trial.num_spikes} spikes")
        print()
        
        # 测试关闭和重新打开
        print("6. Closing and reopening project...")
        manager.close_project()
        
        success = manager.open_project(project_path)
        print(f"   Reopen result: {'✓ Success' if success else '✗ Failed'}")
        if success:
            print(f"   Loaded {len(manager.get_all_trials())} trials\n")
        
        # 测试删除试验
        print("7. Removing trial...")
        success = manager.remove_trial("FC_Grating_015")
        print(f"   Remove result: {'✓ Success' if success else '✗ Failed'}")
        print(f"   Remaining trials: {len(manager.get_all_trials())}\n")
    
    # 清理测试目录
    shutil.rmtree(test_dir)
    print("✅ All tests completed!")
