from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMenuBar, QMenu, QAction, QStatusBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from cert_manager.gui.key_tab import KeyTab
from cert_manager.gui.cert_tab import CertTab
from cert_manager.gui.file_tab import FileTab
from cert_manager.gui.verify_tab import VerifyTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("证书生成与管理工具")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 创建各个标签页
        self.key_tab = KeyTab()
        self.cert_tab = CertTab()
        self.file_tab = FileTab()
        self.verify_tab = VerifyTab()
        
        # 添加标签页
        self.tab_widget.addTab(self.key_tab, "密钥管理")
        self.tab_widget.addTab(self.cert_tab, "证书管理")
        self.tab_widget.addTab(self.file_tab, "文件签名")
        self.tab_widget.addTab(self.verify_tab, "验证")
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 设置中心部件
        self.setCentralWidget(self.tab_widget)
    
    def create_menu_bar(self):
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)
        
        # 文件菜单
        file_menu = QMenu("文件", self)
        menu_bar.addMenu(file_menu)
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tool_menu = QMenu("工具", self)
        menu_bar.addMenu(tool_menu)
        
        # 帮助菜单
        help_menu = QMenu("帮助", self)
        menu_bar.addMenu(help_menu)
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_about(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(self, "关于", "证书生成与管理工具 v1.0\n\n用于生成和管理数字证书、签名文件的工具")
    
    def update_status(self, message):
        """更新状态栏消息"""
        self.status_bar.showMessage(message)
