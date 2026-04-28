"""
Decoding Algorithms - 解码算法

提供LDA解码、SVM分类、随机森林分类功能
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier as SklearnRF
from sklearn.model_selection import cross_val_score, StratifiedKFold, train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler

try:
    from .base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, ParameterType, create_parameter
except ImportError:
    from base import BaseAlgorithm, AlgorithmInput, AlgorithmOutput, ParameterType, create_parameter


class LDADecoder(BaseAlgorithm):
    """
    线性判别分析（LDA）解码算法
    
    使用LDA对神经活动进行解码，预测刺激条件或行为状态。
    
    可设置参数:
    - solver: LDA求解器（svd/lsqr/eigen）
    - shrinkage: 收缩参数（auto/manual/none）
    - n_components: 降维后的维度
    - cv_folds: 交叉验证折数
    - test_size: 测试集比例
    """
    
    def __init__(self):
        super().__init__()
        self.name = "LDADecoder"
        self.description = "线性判别分析（LDA）解码"
        self.category = "Decoding"
        self.version = "1.0"
        self.required_data_types = ['spike', 'behavior']
        self.data_requirements_description = "需要Spike数据和行为数据（试次信息），或LFP数据和行为数据"
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "solver", ParameterType.SELECT,
                "LDA求解器", "svd",
                options=["svd", "lsqr", "eigen"],
                required=False
            ),
            create_parameter(
                "shrinkage", ParameterType.SELECT,
                "收缩参数", "auto",
                options=["auto", "none", "manual"],
                required=False
            ),
            create_parameter(
                "shrinkage_value", ParameterType.FLOAT,
                "手动收缩值", 0.1,
                min_value=0.0, max_value=1.0,
                required=False
            ),
            create_parameter(
                "n_components", ParameterType.INTEGER,
                "降维维度", 2,
                min_value=1, max_value=10,
                required=False
            ),
            create_parameter(
                "cv_folds", ParameterType.INTEGER,
                "交叉验证折数", 5,
                min_value=2, max_value=10,
                required=False
            ),
            create_parameter(
                "test_size", ParameterType.FLOAT,
                "测试集比例", 0.2,
                min_value=0.1, max_value=0.5,
                required=False
            ),
            create_parameter(
                "random_state", ParameterType.INTEGER,
                "随机种子", 42,
                min_value=0, max_value=1000,
                required=False
            ),
            create_parameter(
                "feature_type", ParameterType.SELECT,
                "特征类型", "spike",
                options=["spike", "lfp", "combined"],
                required=False
            )
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        # 基本验证：必须有trial_info
        if input_data.trial_info is None:
            print("[LDADecoder] validate_input failed: trial_info is None")
            return False
        
        if len(input_data.trial_info) == 0:
            print("[LDADecoder] validate_input failed: trial_info is empty")
            return False
        
        # 根据特征类型验证对应的数据
        # 注意：这里无法直接获取feature_type参数，所以做宽松验证
        # 只要spike_times或lfp_data有一个存在即可
        has_spike = (input_data.spike_times is not None and 
                     len(input_data.spike_times) > 0)
        has_lfp = (input_data.lfp_data is not None and 
                   input_data.lfp_data.size > 0)
        
        print(f"[LDADecoder] validate_input: has_spike={has_spike}, has_lfp={has_lfp}, trial_info_count={len(input_data.trial_info)}")
        
        if not has_spike and not has_lfp:
            print("[LDADecoder] validate_input failed: neither spike_times nor lfp_data available")
            return False
        
        return True
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        import time
        start_time = time.time()
        
        try:
            spike_times = input_data.spike_times
            trial_info = input_data.trial_info
            lfp_data = input_data.lfp_data
            
            # 详细验证输入数据
            if trial_info is None:
                return AlgorithmOutput(
                    success=False,
                    error_message="缺少行为数据（试次信息）。请确保选择了包含Events的数据项。",
                    execution_time=time.time() - start_time
                )
            
            if len(trial_info) == 0:
                return AlgorithmOutput(
                    success=False,
                    error_message="行为数据（试次信息）为空。请检查选择的数据项是否包含有效的试次信息。",
                    execution_time=time.time() - start_time
                )
            
            has_spike = spike_times is not None and len(spike_times) > 0
            has_lfp = lfp_data is not None and lfp_data.size > 0
            
            if not has_spike and not has_lfp:
                return AlgorithmOutput(
                    success=False,
                    error_message="缺少神经数据。请确保选择了Spike数据或LFP信号数据。",
                    execution_time=time.time() - start_time
                )
            
            # 提取参数
            solver = parameters.get("solver", "svd")
            shrinkage = parameters.get("shrinkage", "auto")
            shrinkage_value = parameters.get("shrinkage_value", 0.1)
            n_components = parameters.get("n_components", 2)
            cv_folds = parameters.get("cv_folds", 5)
            test_size = parameters.get("test_size", 0.2)
            random_state = parameters.get("random_state", 42)
            feature_type = parameters.get("feature_type", "spike")
            
            # 准备特征和标签
            X, y = self._prepare_features(spike_times, trial_info, lfp_data, feature_type)
            
            print(f"[LDADecoder] Prepared features: X.shape={X.shape}, y.shape={y.shape}")
            print(f"[LDADecoder] Unique classes: {np.unique(y)}, class distribution: {np.bincount(y)}")
            
            if len(np.unique(y)) < 2:
                return AlgorithmOutput(
                    success=False,
                    error_message="Need at least 2 classes for LDA"
                )
            
            # 标准化特征
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            
            # 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            print(f"[LDADecoder] Train set: X_train.shape={X_train.shape}, y_train distribution={np.bincount(y_train)}")
            print(f"[LDADecoder] Test set: X_test.shape={X_test.shape}, y_test distribution={np.bincount(y_test)}")
            
            # 设置收缩参数（仅lsqr和eigen求解器支持）
            if solver == "svd":
                shrinkage_param = None  # svd不支持shrinkage
            elif shrinkage == "auto":
                shrinkage_param = "auto"
            elif shrinkage == "manual":
                shrinkage_param = shrinkage_value
            else:
                shrinkage_param = None
            
            # 创建LDA模型
            lda_kwargs = {
                'solver': solver,
                'n_components': min(n_components, len(np.unique(y)) - 1)
            }
            if shrinkage_param is not None:
                lda_kwargs['shrinkage'] = shrinkage_param
            
            lda = LinearDiscriminantAnalysis(**lda_kwargs)
            
            # 交叉验证
            cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
            cv_scores = cross_val_score(lda, X_train, y_train, cv=cv, scoring='accuracy')
            
            # 训练最终模型
            lda.fit(X_train, y_train)
            
            # 预测
            y_pred_train = lda.predict(X_train)
            y_pred_test = lda.predict(X_test)
            
            print(f"[LDADecoder] y_test: {y_test}")
            print(f"[LDADecoder] y_pred_test: {y_pred_test}")
            
            # 计算准确率
            train_accuracy = accuracy_score(y_train, y_pred_train)
            test_accuracy = accuracy_score(y_test, y_pred_test)
            
            print(f"[LDADecoder] train_accuracy={train_accuracy:.3f}, test_accuracy={test_accuracy:.3f}")
            
            # 计算混淆矩阵
            classes = np.unique(y)
            conf_matrix = confusion_matrix(y_test, y_pred_test)
            
            # 计算每个类别的准确率
            class_accuracies = {}
            for i, cls in enumerate(classes):
                class_mask = y_test == cls
                if np.sum(class_mask) > 0:
                    class_accuracies[f'class_{cls}_accuracy'] = float(
                        np.mean(y_pred_test[class_mask] == cls)
                    )
            
            # 降维后的特征
            X_transformed = lda.transform(X)
            
            execution_time = time.time() - start_time
            
            # 准备输出
            output = AlgorithmOutput(
                data={
                    'X_transformed': X_transformed,
                    'y_true': y,
                    'y_pred_train': y_pred_train,
                    'y_pred_test': y_pred_test,
                    'confusion_matrix': conf_matrix,
                    'classes': classes,
                    'X_test': X_test,
                    'y_test': y_test
                },
                statistics={
                    'mean_cv_accuracy': float(np.mean(cv_scores)),
                    'std_cv_accuracy': float(np.std(cv_scores)),
                    'train_accuracy': float(train_accuracy),
                    'test_accuracy': float(test_accuracy),
                    'n_samples': len(y),
                    'n_train_samples': len(y_train),
                    'n_test_samples': len(y_test),
                    'n_classes': len(classes),
                    'n_features': X.shape[1],
                    **class_accuracies
                },
                plot_config={
                    'type': 'lda_decoding',
                    'title': 'LDA Decoding Results',
                    'xlabel': 'Component 1',
                    'ylabel': 'Component 2'
                },
                export_data={
                    'X_transformed': X_transformed,
                    'y_true': y,
                    'y_pred_test': y_pred_test,
                    'confusion_matrix': conf_matrix,
                    'cv_scores': cv_scores,
                    'classes': classes
                },
                metadata={
                    'classes': classes.tolist(),
                    'solver': solver,
                    'shrinkage': shrinkage,
                    'n_components': n_components,
                    'cv_folds': cv_folds,
                    'feature_type': feature_type
                },
                execution_time=execution_time,
                success=True
            )
            
            self._record_execution(input_data, parameters, output)
            return output
            
        except Exception as e:
            return AlgorithmOutput(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def _prepare_features(self, spike_times: np.ndarray, 
                         trial_info: List[Dict],
                         lfp_data: Optional[np.ndarray],
                         feature_type: str = "spike") -> Tuple[np.ndarray, np.ndarray]:
        """
        准备特征和标签
        
        支持多种特征类型：spike、lfp、combined
        """
        features = []
        labels = []
        
        for trial in trial_info:
            if 'start_time' not in trial or 'end_time' not in trial:
                continue
            
            start_time = trial['start_time']
            end_time = trial['end_time']
            stim_condition = trial.get('stim_cnd', 0)
            
            feature_vector = []
            
            # Spike特征
            if feature_type in ["spike", "combined"] and spike_times is not None:
                trial_spikes = spike_times[
                    (spike_times >= start_time) & (spike_times <= end_time)
                ]
                spike_count = len(trial_spikes)
                firing_rate = spike_count / (end_time - start_time) if end_time > start_time else 0
                feature_vector.extend([spike_count, firing_rate])
            
            # LFP特征
            if feature_type in ["lfp", "combined"] and lfp_data is not None:
                # 计算LFP功率特征（简化版本）
                # 实际应用中可以使用更复杂的频谱特征
                trial_duration = end_time - start_time
                start_sample = int(start_time * 2000)  # 假设采样率2000Hz
                end_sample = int(end_time * 2000)
                
                if start_sample < lfp_data.shape[1] and end_sample <= lfp_data.shape[1]:
                    lfp_segment = lfp_data[:, start_sample:end_sample]
                    # 计算每个通道的功率
                    for ch in range(lfp_segment.shape[0]):
                        power = np.mean(lfp_segment[ch, :] ** 2)
                        feature_vector.append(power)
            
            if feature_vector:
                features.append(feature_vector)
                labels.append(stim_condition)
        
        return np.array(features), np.array(labels)


class SVMClassifier(BaseAlgorithm):
    """
    支持向量机（SVM）分类算法
    
    使用SVM对神经活动进行分类，支持多种核函数。
    
    可设置参数:
    - kernel: 核函数类型（rbf/linear/poly/sigmoid）
    - C: 正则化参数
    - gamma: 核系数
    - degree: 多项式核次数
    - cv_folds: 交叉验证折数
    - test_size: 测试集比例
    """
    
    def __init__(self):
        super().__init__()
        self.name = "SVMClassifier"
        self.description = "支持向量机（SVM）分类"
        self.category = "Decoding"
        self.version = "1.0"
        self.required_data_types = ['spike', 'behavior']
        self.data_requirements_description = "需要Spike数据和行为数据（试次信息），或LFP数据和行为数据"
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "kernel", ParameterType.SELECT,
                "核函数", "rbf",
                options=["rbf", "linear", "poly", "sigmoid"],
                required=False
            ),
            create_parameter(
                "C", ParameterType.FLOAT,
                "正则化参数", 1.0,
                min_value=0.01, max_value=100.0,
                required=False
            ),
            create_parameter(
                "gamma", ParameterType.SELECT,
                "核系数", "scale",
                options=["scale", "auto"],
                required=False
            ),
            create_parameter(
                "degree", ParameterType.INTEGER,
                "多项式次数", 3,
                min_value=2, max_value=10,
                required=False
            ),
            create_parameter(
                "cv_folds", ParameterType.INTEGER,
                "交叉验证折数", 5,
                min_value=2, max_value=10,
                required=False
            ),
            create_parameter(
                "test_size", ParameterType.FLOAT,
                "测试集比例", 0.2,
                min_value=0.1, max_value=0.5,
                required=False
            ),
            create_parameter(
                "random_state", ParameterType.INTEGER,
                "随机种子", 42,
                min_value=0, max_value=1000,
                required=False
            ),
            create_parameter(
                "feature_type", ParameterType.SELECT,
                "特征类型", "spike",
                options=["spike", "lfp", "combined"],
                required=False
            )
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        return (input_data.spike_times is not None and 
                input_data.trial_info is not None and
                len(input_data.spike_times) > 0 and
                len(input_data.trial_info) > 0)
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        import time
        start_time = time.time()
        
        try:
            spike_times = input_data.spike_times
            trial_info = input_data.trial_info
            lfp_data = input_data.lfp_data
            
            # 提取参数
            kernel = parameters.get("kernel", "rbf")
            C = parameters.get("C", 1.0)
            gamma = parameters.get("gamma", "scale")
            degree = parameters.get("degree", 3)
            cv_folds = parameters.get("cv_folds", 5)
            test_size = parameters.get("test_size", 0.2)
            random_state = parameters.get("random_state", 42)
            feature_type = parameters.get("feature_type", "spike")
            
            # 准备特征和标签
            X, y = self._prepare_features(spike_times, trial_info, lfp_data, feature_type)
            
            if len(np.unique(y)) < 2:
                return AlgorithmOutput(
                    success=False,
                    error_message="Need at least 2 classes for SVM"
                )
            
            # 标准化特征
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            
            # 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            # 创建SVM模型
            svm_kwargs = {
                'kernel': kernel,
                'C': C,
                'gamma': gamma,
                'random_state': random_state,
                'probability': True
            }
            if kernel == "poly":
                svm_kwargs['degree'] = degree
            
            svm = SVC(**svm_kwargs)
            
            # 交叉验证
            cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
            cv_scores = cross_val_score(svm, X_train, y_train, cv=cv, scoring='accuracy')
            
            # 训练最终模型
            svm.fit(X_train, y_train)
            
            # 预测
            y_pred_train = svm.predict(X_train)
            y_pred_test = svm.predict(X_test)
            y_prob_test = svm.predict_proba(X_test)
            
            # 计算准确率
            train_accuracy = accuracy_score(y_train, y_pred_train)
            test_accuracy = accuracy_score(y_test, y_pred_test)
            
            # 计算混淆矩阵
            classes = np.unique(y)
            conf_matrix = confusion_matrix(y_test, y_pred_test)
            
            # 计算每个类别的准确率
            class_accuracies = {}
            for i, cls in enumerate(classes):
                class_mask = y_test == cls
                if np.sum(class_mask) > 0:
                    class_accuracies[f'class_{cls}_accuracy'] = float(
                        np.mean(y_pred_test[class_mask] == cls)
                    )
            
            # 获取支持向量信息
            n_support_vectors = len(svm.support_)
            
            execution_time = time.time() - start_time
            
            # 准备输出
            output = AlgorithmOutput(
                data={
                    'y_true': y,
                    'y_pred_train': y_pred_train,
                    'y_pred_test': y_pred_test,
                    'y_prob_test': y_prob_test,
                    'confusion_matrix': conf_matrix,
                    'classes': classes,
                    'support_vectors': svm.support_vectors_,
                    'X_test': X_test,
                    'y_test': y_test
                },
                statistics={
                    'mean_cv_accuracy': float(np.mean(cv_scores)),
                    'std_cv_accuracy': float(np.std(cv_scores)),
                    'train_accuracy': float(train_accuracy),
                    'test_accuracy': float(test_accuracy),
                    'n_samples': len(y),
                    'n_train_samples': len(y_train),
                    'n_test_samples': len(y_test),
                    'n_classes': len(classes),
                    'n_features': X.shape[1],
                    'n_support_vectors': n_support_vectors,
                    **class_accuracies
                },
                plot_config={
                    'type': 'svm_decoding',
                    'title': 'SVM Classification Results',
                    'xlabel': 'Predicted Class',
                    'ylabel': 'True Class'
                },
                export_data={
                    'y_true': y,
                    'y_pred_test': y_pred_test,
                    'y_prob_test': y_prob_test,
                    'confusion_matrix': conf_matrix,
                    'cv_scores': cv_scores,
                    'classes': classes
                },
                metadata={
                    'classes': classes.tolist(),
                    'kernel': kernel,
                    'C': C,
                    'gamma': gamma,
                    'cv_folds': cv_folds,
                    'feature_type': feature_type
                },
                execution_time=execution_time,
                success=True
            )
            
            self._record_execution(input_data, parameters, output)
            return output
            
        except Exception as e:
            return AlgorithmOutput(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def _prepare_features(self, spike_times: np.ndarray, 
                         trial_info: List[Dict],
                         lfp_data: Optional[np.ndarray],
                         feature_type: str = "spike") -> Tuple[np.ndarray, np.ndarray]:
        """准备特征和标签"""
        features = []
        labels = []
        
        for trial in trial_info:
            if 'start_time' not in trial or 'end_time' not in trial:
                continue
            
            start_time = trial['start_time']
            end_time = trial['end_time']
            stim_condition = trial.get('stim_cnd', 0)
            
            feature_vector = []
            
            # Spike特征
            if feature_type in ["spike", "combined"] and spike_times is not None:
                trial_spikes = spike_times[
                    (spike_times >= start_time) & (spike_times <= end_time)
                ]
                spike_count = len(trial_spikes)
                firing_rate = spike_count / (end_time - start_time) if end_time > start_time else 0
                feature_vector.extend([spike_count, firing_rate])
            
            # LFP特征
            if feature_type in ["lfp", "combined"] and lfp_data is not None:
                trial_duration = end_time - start_time
                start_sample = int(start_time * 2000)
                end_sample = int(end_time * 2000)
                
                if start_sample < lfp_data.shape[1] and end_sample <= lfp_data.shape[1]:
                    lfp_segment = lfp_data[:, start_sample:end_sample]
                    for ch in range(lfp_segment.shape[0]):
                        power = np.mean(lfp_segment[ch, :] ** 2)
                        feature_vector.append(power)
            
            if feature_vector:
                features.append(feature_vector)
                labels.append(stim_condition)
        
        return np.array(features), np.array(labels)


class RandomForestClassifier(BaseAlgorithm):
    """
    随机森林分类算法
    
    使用随机森林对神经活动进行分类，提供特征重要性分析。
    
    可设置参数:
    - n_estimators: 树的数量
    - max_depth: 树的最大深度
    - min_samples_split: 节点分裂最小样本数
    - min_samples_leaf: 叶子节点最小样本数
    - max_features: 特征采样比例
    - cv_folds: 交叉验证折数
    - test_size: 测试集比例
    """
    
    def __init__(self):
        super().__init__()
        self.name = "RandomForestClassifier"
        self.description = "随机森林分类"
        self.category = "Decoding"
        self.version = "1.0"
        self.required_data_types = ['spike', 'behavior']
        self.data_requirements_description = "需要Spike数据和行为数据（试次信息），或LFP数据和行为数据"
    
    def get_parameters_schema(self):
        return [
            create_parameter(
                "n_estimators", ParameterType.INTEGER,
                "树的数量", 100,
                min_value=10, max_value=500,
                required=False
            ),
            create_parameter(
                "max_depth", ParameterType.INTEGER,
                "最大深度", 10,
                min_value=1, max_value=50,
                required=False
            ),
            create_parameter(
                "min_samples_split", ParameterType.INTEGER,
                "分裂最小样本数", 2,
                min_value=2, max_value=20,
                required=False
            ),
            create_parameter(
                "min_samples_leaf", ParameterType.INTEGER,
                "叶子最小样本数", 1,
                min_value=1, max_value=20,
                required=False
            ),
            create_parameter(
                "max_features", ParameterType.SELECT,
                "特征采样", "sqrt",
                options=["sqrt", "log2", "auto"],
                required=False
            ),
            create_parameter(
                "cv_folds", ParameterType.INTEGER,
                "交叉验证折数", 5,
                min_value=2, max_value=10,
                required=False
            ),
            create_parameter(
                "test_size", ParameterType.FLOAT,
                "测试集比例", 0.2,
                min_value=0.1, max_value=0.5,
                required=False
            ),
            create_parameter(
                "random_state", ParameterType.INTEGER,
                "随机种子", 42,
                min_value=0, max_value=1000,
                required=False
            ),
            create_parameter(
                "feature_type", ParameterType.SELECT,
                "特征类型", "spike",
                options=["spike", "lfp", "combined"],
                required=False
            )
        ]
    
    def validate_input(self, input_data: AlgorithmInput) -> bool:
        return (input_data.spike_times is not None and 
                input_data.trial_info is not None and
                len(input_data.spike_times) > 0 and
                len(input_data.trial_info) > 0)
    
    def run(self, input_data: AlgorithmInput, parameters: Dict) -> AlgorithmOutput:
        import time
        start_time = time.time()
        
        try:
            spike_times = input_data.spike_times
            trial_info = input_data.trial_info
            lfp_data = input_data.lfp_data
            
            # 提取参数
            n_estimators = parameters.get("n_estimators", 100)
            max_depth = parameters.get("max_depth", 10)
            min_samples_split = parameters.get("min_samples_split", 2)
            min_samples_leaf = parameters.get("min_samples_leaf", 1)
            max_features = parameters.get("max_features", "sqrt")
            cv_folds = parameters.get("cv_folds", 5)
            test_size = parameters.get("test_size", 0.2)
            random_state = parameters.get("random_state", 42)
            feature_type = parameters.get("feature_type", "spike")
            
            # 准备特征和标签
            X, y = self._prepare_features(spike_times, trial_info, lfp_data, feature_type)
            
            if len(np.unique(y)) < 2:
                return AlgorithmOutput(
                    success=False,
                    error_message="Need at least 2 classes for Random Forest"
                )
            
            # 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            # 创建随机森林模型
            rf = SklearnRF(
                n_estimators=n_estimators,
                max_depth=max_depth,
                min_samples_split=min_samples_split,
                min_samples_leaf=min_samples_leaf,
                max_features=max_features,
                random_state=random_state,
                n_jobs=-1  # 使用所有CPU核心
            )
            
            # 交叉验证
            cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
            cv_scores = cross_val_score(rf, X_train, y_train, cv=cv, scoring='accuracy')
            
            # 训练最终模型
            rf.fit(X_train, y_train)
            
            # 预测
            y_pred_train = rf.predict(X_train)
            y_pred_test = rf.predict(X_test)
            y_prob_test = rf.predict_proba(X_test)
            
            # 计算准确率
            train_accuracy = accuracy_score(y_train, y_pred_train)
            test_accuracy = accuracy_score(y_test, y_pred_test)
            
            # 计算混淆矩阵
            classes = np.unique(y)
            conf_matrix = confusion_matrix(y_test, y_pred_test)
            
            # 计算每个类别的准确率
            class_accuracies = {}
            for i, cls in enumerate(classes):
                class_mask = y_test == cls
                if np.sum(class_mask) > 0:
                    class_accuracies[f'class_{cls}_accuracy'] = float(
                        np.mean(y_pred_test[class_mask] == cls)
                    )
            
            # 获取特征重要性
            feature_importance = rf.feature_importances_
            
            execution_time = time.time() - start_time
            
            # 准备输出
            output = AlgorithmOutput(
                data={
                    'y_true': y,
                    'y_pred_train': y_pred_train,
                    'y_pred_test': y_pred_test,
                    'y_prob_test': y_prob_test,
                    'confusion_matrix': conf_matrix,
                    'classes': classes,
                    'feature_importance': feature_importance,
                    'X_test': X_test,
                    'y_test': y_test
                },
                statistics={
                    'mean_cv_accuracy': float(np.mean(cv_scores)),
                    'std_cv_accuracy': float(np.std(cv_scores)),
                    'train_accuracy': float(train_accuracy),
                    'test_accuracy': float(test_accuracy),
                    'n_samples': len(y),
                    'n_train_samples': len(y_train),
                    'n_test_samples': len(y_test),
                    'n_classes': len(classes),
                    'n_features': X.shape[1],
                    'n_trees': n_estimators,
                    **class_accuracies
                },
                plot_config={
                    'type': 'rf_decoding',
                    'title': 'Random Forest Classification Results',
                    'xlabel': 'Predicted Class',
                    'ylabel': 'True Class'
                },
                export_data={
                    'y_true': y,
                    'y_pred_test': y_pred_test,
                    'y_prob_test': y_prob_test,
                    'confusion_matrix': conf_matrix,
                    'cv_scores': cv_scores,
                    'feature_importance': feature_importance,
                    'classes': classes
                },
                metadata={
                    'classes': classes.tolist(),
                    'n_estimators': n_estimators,
                    'max_depth': max_depth,
                    'cv_folds': cv_folds,
                    'feature_type': feature_type
                },
                execution_time=execution_time,
                success=True
            )
            
            self._record_execution(input_data, parameters, output)
            return output
            
        except Exception as e:
            return AlgorithmOutput(
                success=False,
                error_message=str(e),
                execution_time=time.time() - start_time
            )
    
    def _prepare_features(self, spike_times: np.ndarray, 
                         trial_info: List[Dict],
                         lfp_data: Optional[np.ndarray],
                         feature_type: str = "spike") -> Tuple[np.ndarray, np.ndarray]:
        """准备特征和标签"""
        features = []
        labels = []
        
        for trial in trial_info:
            if 'start_time' not in trial or 'end_time' not in trial:
                continue
            
            start_time = trial['start_time']
            end_time = trial['end_time']
            stim_condition = trial.get('stim_cnd', 0)
            
            feature_vector = []
            
            # Spike特征
            if feature_type in ["spike", "combined"] and spike_times is not None:
                trial_spikes = spike_times[
                    (spike_times >= start_time) & (spike_times <= end_time)
                ]
                spike_count = len(trial_spikes)
                firing_rate = spike_count / (end_time - start_time) if end_time > start_time else 0
                feature_vector.extend([spike_count, firing_rate])
            
            # LFP特征
            if feature_type in ["lfp", "combined"] and lfp_data is not None:
                trial_duration = end_time - start_time
                start_sample = int(start_time * 2000)
                end_sample = int(end_time * 2000)
                
                if start_sample < lfp_data.shape[1] and end_sample <= lfp_data.shape[1]:
                    lfp_segment = lfp_data[:, start_sample:end_sample]
                    for ch in range(lfp_segment.shape[0]):
                        power = np.mean(lfp_segment[ch, :] ** 2)
                        feature_vector.append(power)
            
            if feature_vector:
                features.append(feature_vector)
                labels.append(stim_condition)
        
        return np.array(features), np.array(labels)


if __name__ == '__main__':
    # 测试代码
    print("=== Testing Decoding Algorithms ===\n")
    
    # 创建模拟数据
    np.random.seed(42)
    
    # 模拟Spike时间（20秒，平均15Hz）
    duration = 20.0
    spike_rate = 15.0
    n_spikes = int(duration * spike_rate)
    spike_times = np.sort(np.random.uniform(0, duration, n_spikes))
    
    # 模拟试次信息（20个试次，2种刺激条件）
    trial_info = []
    for i in range(20):
        # 条件0：低发放率，条件1：高发放率
        condition = i % 2
        
        trial_info.append({
            'trial_num': i + 1,
            'start_time': i * 1.0,
            'end_time': i * 1.0 + 0.8,
            'stim_cnd': condition
        })
    
    input_data = AlgorithmInput(
        spike_times=spike_times,
        trial_info=trial_info
    )
    
    # 测试LDA解码
    print("1. Testing LDADecoder...")
    lda_decoder = LDADecoder()
    
    lda_params = lda_decoder.get_default_parameters()
    lda_params['n_components'] = 1
    
    lda_output = lda_decoder.run(input_data, lda_params)
    
    if lda_output.success:
        print(f"   ✓ LDA decoding successful")
        print(f"     Mean CV accuracy: {lda_output.statistics['mean_cv_accuracy']:.3f}")
        print(f"     Test accuracy: {lda_output.statistics['test_accuracy']:.3f}")
        print(f"     Number of samples: {lda_output.statistics['n_samples']}")
    else:
        print(f"   ✗ LDA decoding failed: {lda_output.error_message}")
    print()
    
    # 测试SVM分类
    print("2. Testing SVMClassifier...")
    svm_classifier = SVMClassifier()
    
    svm_params = svm_classifier.get_default_parameters()
    
    svm_output = svm_classifier.run(input_data, svm_params)
    
    if svm_output.success:
        print(f"   ✓ SVM classification successful")
        print(f"     Mean CV accuracy: {svm_output.statistics['mean_cv_accuracy']:.3f}")
        print(f"     Test accuracy: {svm_output.statistics['test_accuracy']:.3f}")
        print(f"     Number of support vectors: {svm_output.statistics['n_support_vectors']}")
    else:
        print(f"   ✗ SVM classification failed: {svm_output.error_message}")
    print()
    
    # 测试随机森林分类
    print("3. Testing RandomForestClassifier...")
    rf_classifier = RandomForestClassifier()
    
    rf_params = rf_classifier.get_default_parameters()
    rf_params['n_estimators'] = 50
    
    rf_output = rf_classifier.run(input_data, rf_params)
    
    if rf_output.success:
        print(f"   ✓ Random Forest classification successful")
        print(f"     Mean CV accuracy: {rf_output.statistics['mean_cv_accuracy']:.3f}")
        print(f"     Test accuracy: {rf_output.statistics['test_accuracy']:.3f}")
        print(f"     Feature importance: {rf_output.data['feature_importance']}")
    else:
        print(f"   ✗ Random Forest classification failed: {rf_output.error_message}")
    
    print("\n✅ Decoding tests completed!")
