from PyQt5.QtWidgets import QApplication
import sys
import os

# 获取src目录路径
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
parent_dir = os.path.dirname(current_dir)
src_dir = parent_dir
# 添加src目录到Python路径，确保所有模块都能被正确导入
sys.path.insert(0, src_dir)
print(f"Added src directory to Python path: {src_dir}")

# 现在使用绝对导入
try:
    from trucert.gui.main_window import MainWindow
    from trucert.core.utils import initialize_dependencies
    print("Import successful!")
except ImportError as e:
    print(f"导入失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    try:
        # 初始化依赖注入容器
        print("Initializing dependencies...")
        initialize_dependencies()
        print("Dependencies initialized successfully!")
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("\n应用程序被用户中断，正在优雅退出...")
        sys.exit(0)
    except Exception as e:
        print(f"应用程序启动失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
