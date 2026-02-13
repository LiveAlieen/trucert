from PyQt5.QtWidgets import QApplication
import sys
import os

# 添加当前目录到Python路径，支持直接运行
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 尝试相对导入（包方式运行）
    from .gui.main_window import MainWindow
except ImportError:
    # 直接导入（直接运行）
    from gui.main_window import MainWindow

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
