from PyQt5.QtWidgets import QApplication
import sys
import os

# 获取项目根目录路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 添加项目根目录到Python路径，确保所有模块都能被正确导入
sys.path.insert(0, project_root)

# 现在使用绝对导入
try:
    from cert_manager.gui.main_window import MainWindow
except ImportError as e:
    print(f"导入失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    try:
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
