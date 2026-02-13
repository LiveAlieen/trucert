from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox, QTabWidget
from PyQt5.QtCore import Qt
from cert_manager.core.verifier import Verifier
from cert_manager.core.key_manager import KeyManager
from cert_manager.core.cert_manager import CertManager
from cert_manager.core.file_signer import FileSigner
from cert_manager.core.config import ConfigManager
from cert_manager.utils import file_utils

class VerifyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.verifier = Verifier()
        self.key_manager = KeyManager()
        self.cert_manager = CertManager()
        self.file_signer = FileSigner()
        self.config_manager = ConfigManager()
        self.algorithms = self.config_manager.get_algorithms()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 验证类型标签页
        self.tab_widget = QTabWidget()
        
        # 证书验证标签页
        self.cert_verify_tab = QWidget()
        self.init_cert_verify_ui()
        
        # 文件验证标签页
        self.file_verify_tab = QWidget()
        self.init_file_verify_ui()
        
        self.tab_widget.addTab(self.cert_verify_tab, "证书验证")
        self.tab_widget.addTab(self.file_verify_tab, "文件验证")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def init_cert_verify_ui(self):
        layout = QVBoxLayout()
        
        # 证书验证组
        verify_group = QGroupBox("验证证书")
        verify_layout = QVBoxLayout()
        
        # 证书文件
        cert_layout = QHBoxLayout()
        cert_layout.addWidget(QLabel("证书文件:"))
        self.cert_path_edit = QLineEdit()
        cert_layout.addWidget(self.cert_path_edit)
        cert_btn = QPushButton("浏览")
        cert_btn.clicked.connect(self.browse_cert)
        cert_layout.addWidget(cert_btn)
        verify_layout.addLayout(cert_layout)
        
        # 上级证书
        parent_layout = QHBoxLayout()
        parent_layout.addWidget(QLabel("上级证书 (可选):"))
        self.parent_path_edit = QLineEdit()
        parent_layout.addWidget(self.parent_path_edit)
        parent_btn = QPushButton("浏览")
        parent_btn.clicked.connect(self.browse_parent_cert)
        parent_layout.addWidget(parent_btn)
        verify_layout.addLayout(parent_layout)
        
        # 验证按钮
        verify_btn = QPushButton("验证证书")
        verify_btn.clicked.connect(self.verify_cert)
        verify_layout.addWidget(verify_btn)
        
        verify_group.setLayout(verify_layout)
        layout.addWidget(verify_group)
        
        # 验证结果组
        result_group = QGroupBox("验证结果")
        result_layout = QVBoxLayout()
        self.cert_result_text = QTextEdit()
        self.cert_result_text.setReadOnly(True)
        result_layout.addWidget(self.cert_result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        self.cert_verify_tab.setLayout(layout)
    
    def init_file_verify_ui(self):
        layout = QVBoxLayout()
        
        # 文件验证组
        verify_group = QGroupBox("验证文件")
        verify_layout = QVBoxLayout()
        
        # 文件选择
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("文件:"))
        self.verify_file_path_edit = QLineEdit()
        file_layout.addWidget(self.verify_file_path_edit)
        file_btn = QPushButton("浏览")
        file_btn.clicked.connect(self.browse_verify_file)
        file_layout.addWidget(file_btn)
        verify_layout.addLayout(file_layout)
        
        # 签名文件
        sig_layout = QHBoxLayout()
        sig_layout.addWidget(QLabel("签名文件 (可选):"))
        self.sig_path_edit = QLineEdit()
        sig_layout.addWidget(self.sig_path_edit)
        sig_btn = QPushButton("浏览")
        sig_btn.clicked.connect(self.browse_signature)
        sig_layout.addWidget(sig_btn)
        verify_layout.addLayout(sig_layout)
        
        # 公钥选择
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("公钥文件:"))
        self.verify_key_path_edit = QLineEdit()
        key_layout.addWidget(self.verify_key_path_edit)
        key_btn = QPushButton("浏览")
        key_btn.clicked.connect(self.browse_verify_key)
        key_layout.addWidget(key_btn)
        verify_layout.addLayout(key_layout)
        
        # 哈希算法
        hash_layout = QHBoxLayout()
        hash_layout.addWidget(QLabel("哈希算法:"))
        self.verify_hash_combo = QComboBox()
        for algo in self.algorithms.get("hash_algorithms", ["sha256", "sha384", "sha512"]):
            self.verify_hash_combo.addItem(algo)
        hash_layout.addWidget(self.verify_hash_combo)
        hash_layout.addStretch()
        verify_layout.addLayout(hash_layout)
        
        # 验证按钮
        verify_btn = QPushButton("验证文件")
        verify_btn.clicked.connect(self.verify_file)
        verify_layout.addWidget(verify_btn)
        
        verify_group.setLayout(verify_layout)
        layout.addWidget(verify_group)
        
        # 验证结果组
        result_group = QGroupBox("验证结果")
        result_layout = QVBoxLayout()
        self.file_result_text = QTextEdit()
        self.file_result_text.setReadOnly(True)
        result_layout.addWidget(self.file_result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        self.file_verify_tab.setLayout(layout)
    
    def browse_cert(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择证书文件", "", "JSON Files (*.json)")
        if file_path:
            self.cert_path_edit.setText(file_path)
    
    def browse_parent_cert(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择上级证书文件", "", "JSON Files (*.json)")
        if file_path:
            self.parent_path_edit.setText(file_path)
    
    def browse_verify_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.verify_file_path_edit.setText(file_path)
    
    def browse_signature(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择签名文件", "", "JSON Files (*.json)")
        if file_path:
            self.sig_path_edit.setText(file_path)
    
    def browse_verify_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择公钥文件", "", "PEM Files (*.pem);;DER Files (*.der)")
        if file_path:
            self.verify_key_path_edit.setText(file_path)
    
    def verify_cert(self):
        try:
            # 检查证书路径
            cert_path = self.cert_path_edit.text()
            if not cert_path:
                QMessageBox.warning(self, "警告", "请选择证书文件")
                return
            
            # 加载证书
            cert = self.cert_manager.load_cert(cert_path)
            
            # 加载上级证书（如果提供）
            parent_cert = None
            parent_path = self.parent_path_edit.text()
            if parent_path:
                parent_cert = self.cert_manager.load_cert(parent_path)
            
            # 验证证书
            result = self.verifier.verify_json_cert(cert, parent_cert)
            
            # 显示验证结果
            result_text = "验证结果:\n"
            result_text += f"有效: {result['valid']}\n"
            result_text += f"原因: {result['reason']}\n"
            
            if 'cert_info' in result:
                result_text += "\n证书信息:\n"
                for key, value in result['cert_info'].items():
                    result_text += f"{key}: {value}\n"
            
            self.cert_result_text.setText(result_text)
            
            # 显示消息框
            if result['valid']:
                QMessageBox.information(self, "成功", "证书验证通过")
            else:
                QMessageBox.warning(self, "失败", f"证书验证失败: {result['reason']}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"验证失败: {str(e)}")
    
    def verify_file(self):
        try:
            # 检查文件路径
            file_path = self.verify_file_path_edit.text()
            if not file_path:
                QMessageBox.warning(self, "警告", "请选择文件")
                return
            
            # 检查公钥路径
            key_path = self.verify_key_path_edit.text()
            if not key_path:
                QMessageBox.warning(self, "警告", "请选择公钥文件")
                return
            
            # 加载公钥
            public_key = self.key_manager.load_public_key(key_path)
            
            # 获取哈希算法
            hash_algorithm = self.verify_hash_combo.currentText()
            
            # 检查是否是带签名的文件
            is_signed_file = False
            try:
                # 尝试提取签名
                file_content, signature = self.file_signer.extract_signature_from_file(file_path)
                is_signed_file = True
            except:
                is_signed_file = False
            
            if is_signed_file:
                # 验证带签名的文件
                result = self.verifier.verify_signed_file(file_path, public_key, hash_algorithm)
            else:
                # 检查是否提供了签名文件
                sig_path = self.sig_path_edit.text()
                if not sig_path:
                    QMessageBox.warning(self, "警告", "请提供签名文件")
                    return
                
                # 加载签名
                # 加载签名、哈希算法和文件信息
                signature, sig_hash_algorithm, file_info = self.file_signer.load_signature(sig_path)
                # 如果从签名文件中获取到哈希算法，则使用它
                if sig_hash_algorithm:
                    hash_algorithm = sig_hash_algorithm
                
                # 验证文件
                result = self.verifier.verify_file_signature(file_path, signature, public_key, hash_algorithm)
            
            # 显示验证结果
            result_text = "验证结果:\n"
            result_text += f"有效: {result['valid']}\n"
            result_text += f"原因: {result['reason']}\n"
            
            if 'file_info' in result:
                result_text += "\n文件信息:\n"
                for key, value in result['file_info'].items():
                    result_text += f"{key}: {value}\n"
            
            self.file_result_text.setText(result_text)
            
            # 显示消息框
            if result['valid']:
                QMessageBox.information(self, "成功", "文件验证通过")
            else:
                QMessageBox.warning(self, "失败", f"文件验证失败: {result['reason']}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"验证失败: {str(e)}")
