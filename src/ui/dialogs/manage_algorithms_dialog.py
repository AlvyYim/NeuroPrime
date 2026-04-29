"""
ManageAlgorithmsDialog - Manage Custom Algorithms Dialog

Displays the list of integrated algorithms, allowing users to delete integrated algorithms 
or add scripts from the custom_algorithms folder.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal


class ManageAlgorithmsDialog(QDialog):
    """Manage Custom Algorithms Dialog"""
    
    algorithms_updated = pyqtSignal(str)  # Signal emitted when algorithms are updated, passing file path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Custom Algorithms")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self._init_ui()
        self._load_algorithms()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Integrated Algorithms")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Algorithm list
        self.algorithm_list = QListWidget()
        layout.addWidget(self.algorithm_list)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Add stretch
        button_layout.addStretch()
        
        # Delete algorithm button
        self.delete_button = QPushButton("Delete Algorithm")
        self.delete_button.clicked.connect(self._on_delete_algorithm)
        self.delete_button.setFixedWidth(100)
        button_layout.addWidget(self.delete_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.close_button.setFixedWidth(100)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _load_algorithms(self):
        """Load integrated algorithms"""
        self.algorithm_list.clear()
        
        try:
            # Clear module cache to ensure deleted algorithms are not reloaded
            import sys
            import importlib
            # Clear all potential custom algorithm modules
            modules_to_remove = []
            for module_name in list(sys.modules.keys()):
                if (module_name in ['aaaa', 'bbbb', 'cccc', 'CustomAlgorithm', 'CustomAlgorithmTest', 'New', 'newnew', 'newnewnew', 'newnewnewnewnewn', 'ViewRawLFPData'] or 
                    module_name.startswith('customalgorithm') or 
                    module_name.startswith('new') or 
                    module_name.startswith('view_raw')):
                    modules_to_remove.append(module_name)
            
            # Clear all pycache files
            import shutil
            import os
            pycache_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'custom_algorithms', '__pycache__')
            if os.path.exists(pycache_dir):
                shutil.rmtree(pycache_dir)
                print(f"Deleted pycache directory: {pycache_dir}")
            
            # Clear all modules related to custom algorithms
            for module_name in modules_to_remove:
                if module_name in sys.modules:
                    del sys.modules[module_name]
                    print(f"Removed module from cache: {module_name}")
            
            # Force reload scheduler module
            if 'src.algorithms.scheduler' in sys.modules:
                del sys.modules['src.algorithms.scheduler']
                print("Removed scheduler module from cache")
            
            # Import AlgorithmScheduler
            from src.algorithms.scheduler import AlgorithmScheduler
            scheduler = AlgorithmScheduler()
            
            # Register built-in algorithms and load custom algorithms
            scheduler.register_builtin_algorithms()
            
            # Get all algorithms
            algorithms = scheduler.get_algorithms()
            
            # Filter custom algorithms
            custom_algorithms = []
            for algo_name, algo_class in algorithms.items():
                if hasattr(algo_class, 'category') and algo_class.category == "Custom Algorithm":
                    custom_algorithms.append((algo_name, algo_class))
            
            # Add to list
            for algo_name, algo_class in custom_algorithms:
                item = QListWidgetItem(algo_name)
                item.setData(Qt.ItemDataRole.UserRole, algo_name)
                self.algorithm_list.addItem(item)
            
            # Show algorithm count
            self.setWindowTitle(f"Manage Custom Algorithms ({len(custom_algorithms)} algorithms)")
            
        except Exception as e:
            print(f"Error loading algorithm list: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_add_algorithm(self):
        """Add algorithm"""
        # Open file dialog to select algorithm script
        default_dir = Path(__file__).parent.parent.parent.parent / "custom_algorithms"
        if not default_dir.exists():
            default_dir = Path(__file__).parent.parent.parent.parent
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Algorithm Script", str(default_dir), "Python Files (*.py)"
        )
        
        if file_path:
            try:
                # Import algorithm
                from src.algorithms.scheduler import AlgorithmScheduler
                scheduler = AlgorithmScheduler()
                
                # Load algorithm
                scheduler._load_custom_algorithms()
                
                # Refresh list
                self._load_algorithms()
                
                # Emit update signal
                self.algorithms_updated.emit(file_path)
                
                QMessageBox.information(self, "Success", f"Algorithm added: {Path(file_path).name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add algorithm: {str(e)}")
                print(f"Error adding algorithm: {e}")
                import traceback
                traceback.print_exc()
    
    def _on_delete_algorithm(self):
        """Delete algorithm"""
        selected_items = self.algorithm_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select an algorithm to delete")
            return
        
        # Get selected algorithm name
        algo_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Delete", f"Are you sure you want to delete algorithm '{algo_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Find and delete algorithm file
                import os
                custom_algorithms_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'custom_algorithms')
                print(f"Custom algorithms directory: {custom_algorithms_dir}")
                
                file_deleted = False
                if os.path.exists(custom_algorithms_dir):
                    # Find matching file
                    for file_name in os.listdir(custom_algorithms_dir):
                        if file_name.endswith('.py') and not file_name.startswith('__'):
                            file_path = os.path.join(custom_algorithms_dir, file_name)
                            # Read file content to check for algorithm name
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    # More flexible matching
                                    if (f"class {algo_name}" in content or 
                                        f"'name': '{algo_name}'" in content or 
                                        f'"name": "{algo_name}"' in content or
                                        f"self.name = '{algo_name}'" in content or
                                        algo_name in content):
                                        # Delete file
                                        os.remove(file_path)
                                        print(f"Deleted algorithm file: {file_path}")
                                        file_deleted = True
                                        break
                            except Exception as e:
                                print(f"Error reading file: {e}")
                
                if not file_deleted:
                    # Try to delete by file name directly
                    possible_file_names = [
                        f"{algo_name.lower()}.py",
                        f"{algo_name}.py",
                        f"custom{algo_name.lower()}.py"
                    ]
                    
                    for file_name in possible_file_names:
                        file_path = os.path.join(custom_algorithms_dir, file_name)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"Deleted algorithm file by name: {file_path}")
                            file_deleted = True
                            break
                
                # Clear all pycache files
                import shutil
                pycache_dir = os.path.join(custom_algorithms_dir, '__pycache__')
                if os.path.exists(pycache_dir):
                    shutil.rmtree(pycache_dir)
                    print(f"Deleted pycache directory: {pycache_dir}")
                
                # Clear module cache
                import sys
                # Clear all potential custom algorithm modules
                modules_to_remove = []
                for module_name in list(sys.modules.keys()):
                    if (module_name in ['aaaa', 'bbbb', 'cccc', 'CustomAlgorithm', 'CustomAlgorithmTest', 'New', 'newnew', 'newnewnew', 'newnewnewnewnewn', 'ViewRawLFPData'] or 
                        module_name.startswith('customalgorithm') or 
                        module_name.startswith('new') or 
                        module_name.startswith('view_raw') or
                        module_name == algo_name or
                        module_name.endswith('algorithm') or
                        module_name.startswith('src.algorithms') or
                        module_name.startswith('custom_algorithms')):
                        modules_to_remove.append(module_name)
                
                # Clear all modules related to custom algorithms
                for module_name in modules_to_remove:
                    if module_name in sys.modules:
                        del sys.modules[module_name]
                        print(f"Removed module from cache: {module_name}")
                
                # Force reload all related modules
                modules_to_reload = [
                    'src.algorithms.scheduler',
                    'src.algorithms.base',
                    'src.algorithms.spike_detection',
                    'src.algorithms.lfp_analysis',
                    'src.algorithms.behavior_analysis',
                    'src.algorithms.decoding'
                ]
                
                for module_name in modules_to_reload:
                    if module_name in sys.modules:
                        del sys.modules[module_name]
                        print(f"Removed module from cache: {module_name}")
                
                # Reload algorithms
                from src.algorithms.scheduler import AlgorithmScheduler
                
                # Recreate scheduler and load algorithms
                scheduler = AlgorithmScheduler()
                scheduler.register_builtin_algorithms()
                
                # Refresh list
                self._load_algorithms()
                
                # Emit update signal
                self.algorithms_updated.emit("")
                
                QMessageBox.information(self, "Success", f"Algorithm deleted: {algo_name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete algorithm: {str(e)}")
                print(f"Error deleting algorithm: {e}")
                import traceback
                traceback.print_exc()