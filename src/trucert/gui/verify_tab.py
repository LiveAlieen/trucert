from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox, QTabWidget
from PyQt5.QtCore import Qt
import sys
import os
# 使用相对导入
from ..core.services import VerifierService, KeyService, CertService, FileSignerService, ConfigService
from ..core.utils import file_utils

class VerifyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.verifier_service = VerifierService()
        self.key_service = KeyService()
        self.cert_service = CertService()
        self.file_signer_service = FileSignerService()
        self.config_service = ConfigService()
        self.algorithms = self.config_service.get_algorithms()
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
        
        # 验证方式选择
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("验证方式:"))
        self.verify_method_combo = QComboBox()
        self.verify_method_combo.addItem("使用公钥")
        self.verify_method_combo.addItem("使用证书")
        self.verify_method_combo.currentIndexChanged.connect(self.on_verify_method_changed)
        method_layout.addWidget(self.verify_method_combo)
        method_layout.addStretch()
        verify_layout.addLayout(method_layout)
        
        # 公钥选择
        self.key_group = QGroupBox("公钥验证")
        key_layout = QVBoxLayout()
        key_path_layout = QHBoxLayout()
        key_path_layout.addWidget(QLabel("公钥文件:"))
        self.verify_key_path_edit = QLineEdit()
        key_path_layout.addWidget(self.verify_key_path_edit)
        key_btn = QPushButton("浏览")
        key_btn.clicked.connect(self.browse_verify_key)
        key_path_layout.addWidget(key_btn)
        key_layout.addLayout(key_path_layout)
        self.key_group.setLayout(key_layout)
        verify_layout.addWidget(self.key_group)
        
        # 证书选择
        self.cert_group = QGroupBox("证书验证")
        cert_layout = QVBoxLayout()
        cert_path_layout = QHBoxLayout()
        cert_path_layout.addWidget(QLabel("证书文件:"))
        self.verify_cert_path_edit = QLineEdit()
        cert_path_layout.addWidget(self.verify_cert_path_edit)
        cert_btn = QPushButton("浏览")
        cert_btn.clicked.connect(self.browse_verify_cert)
        cert_path_layout.addWidget(cert_btn)
        cert_layout.addLayout(cert_path_layout)
        self.cert_group.setLayout(cert_layout)
        verify_layout.addWidget(self.cert_group)
        
        # 默认显示公钥验证
        self.on_verify_method_changed(0)
        
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
        file_path, _ = QFileDialog.getOpenFileName(self, "选择签名文件", "", "JSON Files (*.json);;GIQ Files (*.giq);;GIQS Files (*.giqs)")
        if file_path:
            self.sig_path_edit.setText(file_path)
            
            # 尝试从签名文件中提取文件信息
            try:
                result_load = self.file_signer_service.load_signature({"file_path": file_path})
                if result_load.get("success"):
                    signature_data = result_load["data"]
                    file_info = signature_data.get("file_info", {})
                    
                    # 自动填充文件路径（如果签名文件包含文件名）
                    if file_info.get("filename"):
                        # 尝试在当前目录或签名文件所在目录查找同名文件
                        sig_dir = os.path.dirname(file_path)
                        potential_file_path = os.path.join(sig_dir, file_info["filename"])
                        if os.path.exists(potential_file_path):
                            self.verify_file_path_edit.setText(potential_file_path)
                            QMessageBox.information(self, "信息", f"已自动填充文件路径: {potential_file_path}")
                        else:
                            QMessageBox.information(self, "信息", f"签名文件对应文件: {file_info['filename']}")
                    
                    # 处理批量签名文件
                    if file_info.get("batch_signature"):
                        QMessageBox.information(self, "信息", f"批量签名文件，包含 {file_info.get('total_files', 0)} 个文件的签名")
            except Exception as e:
                # 静默处理错误，不影响用户体验
                pass
    
    def browse_verify_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择公钥文件", "", "PEM Files (*.pem);;DER Files (*.der)")
        if file_path:
            self.verify_key_path_edit.setText(file_path)
    
    def browse_verify_cert(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择证书文件", "", "JSON Files (*.json);;TRU Files (*.tru)")
        if file_path:
            self.verify_cert_path_edit.setText(file_path)
    
    def on_verify_method_changed(self, index):
        if index == 0:  # 使用公钥
            self.key_group.show()
            self.cert_group.hide()
        else:  # 使用证书
            self.key_group.hide()
            self.cert_group.show()
    
    def verify_cert(self):
        try:
            # 检查证书路径
            cert_path = self.cert_path_edit.text()
            if not cert_path:
                QMessageBox.warning(self, "警告", "请选择证书文件")
                return
            
            # 加载证书
            result_cert = self.cert_service.load_cert({"filepath": cert_path})
            if not result_cert.get("success"):
                raise Exception(result_cert.get("error", "加载证书失败"))
            cert = result_cert["data"]
            
            # 加载上级证书（如果提供）
            parent_cert = None
            parent_path = self.parent_path_edit.text()
            if parent_path:
                result_parent = self.cert_service.load_cert({"filepath": parent_path})
                if not result_parent.get("success"):
                    raise Exception(result_parent.get("error", "加载上级证书失败"))
                parent_cert = result_parent["data"]
            
            # 验证证书
            result_verify = self.verifier_service.verify_json_cert({"cert_json_path": cert_path, "public_key": None})
            if not result_verify.get("success"):
                raise Exception(result_verify.get("error", "验证证书失败"))
            
            result = {"valid": result_verify["data"], "reason": "证书验证成功" if result_verify["data"] else "证书验证失败"}
            
            # 显示验证结果
            result_text = "验证结果:\n"
            result_text += f"有效: {result['valid']}\n"
            result_text += f"原因: {result['reason']}\n"
            
            if 'cert_info' in cert:
                result_text += "\n证书信息:\n"
                for key, value in cert['cert_info'].items():
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
            
            # 获取哈希算法
            hash_algorithm = self.verify_hash_combo.currentText()
            
            # 检查是否是带签名的文件
            is_signed_file = False
            try:
                # 尝试提取签名
                result_extract = self.file_signer_service.extract_signature_from_file({"signed_file": file_path})
                if result_extract.get("success"):
                    is_signed_file = True
            except:
                is_signed_file = False
            
            # 根据验证方式选择不同的验证方法
            verify_method = self.verify_method_combo.currentText()
            
            if is_signed_file:
                # 验证带签名的文件
                if verify_method == "使用公钥":
                    # 检查公钥路径
                    key_path = self.verify_key_path_edit.text()
                    if not key_path:
                        QMessageBox.warning(self, "警告", "请选择公钥文件")
                        return
                    
                    # 加载公钥
                    result_key = self.key_service.load_public_key({"file_path": key_path})
                    if not result_key.get("success"):
                        raise Exception(result_key.get("error", "加载公钥失败"))
                    public_key = result_key["data"]
                    
                    result_verify = self.verifier_service.verify_signed_file({"signed_file": file_path, "public_key": public_key, "hash_algorithm": hash_algorithm})
                else:  # 使用证书
                    # 检查证书路径
                    cert_path = self.verify_cert_path_edit.text()
                    if not cert_path:
                        QMessageBox.warning(self, "警告", "请选择证书文件")
                        return
                    
                    # 这里需要修改verifier_service以支持证书验证，暂时使用文件签名服务的验证方法
                    # 首先提取签名
                    result_extract = self.file_signer_service.extract_signature_from_file({"signed_file": file_path})
                    if not result_extract.get("success"):
                        raise Exception(result_extract.get("error", "提取签名失败"))
                    
                    file_content, signature = result_extract["data"].values()
                    
                    # 使用证书验证
                    result_verify = self.file_signer_service.verify_file_signature_with_cert({
                        "file_path": file_path,
                        "signature": signature,
                        "certificate": cert_path,
                        "hash_algorithm": hash_algorithm
                    })
                    
                    # 构造结果格式
                    if result_verify.get("success"):
                        result_verify["data"] = {
                            "valid": result_verify["data"],
                            "reason": "文件签名验证成功" if result_verify["data"] else "文件签名验证失败"
                        }
            else:
                # 检查是否提供了签名文件
                sig_path = self.sig_path_edit.text()
                if not sig_path:
                    QMessageBox.warning(self, "警告", "请提供签名文件")
                    return
                
                # 加载签名
                result_load = self.file_signer_service.load_signature({"file_path": sig_path})
                if not result_load.get("success"):
                    raise Exception(result_load.get("error", "加载签名失败"))
                
                signature_data = result_load["data"]
                signature = signature_data["signature"]
                sig_hash_algorithm = signature_data["hash_algorithm"]
                file_info = signature_data["file_info"]
                
                # 如果从签名文件中获取到哈希算法，则使用它
                if sig_hash_algorithm:
                    hash_algorithm = sig_hash_algorithm
                
                # 验证文件
                if verify_method == "使用公钥":
                    # 检查公钥路径
                    key_path = self.verify_key_path_edit.text()
                    if not key_path:
                        QMessageBox.warning(self, "警告", "请选择公钥文件")
                        return
                    
                    # 加载公钥
                    result_key = self.key_service.load_public_key({"file_path": key_path})
                    if not result_key.get("success"):
                        raise Exception(result_key.get("error", "加载公钥失败"))
                    public_key = result_key["data"]
                    
                    result_verify = self.file_signer_service.verify_file_signature({
                        "file_path": file_path,
                        "signature": signature,
                        "public_key": public_key,
                        "hash_algorithm": hash_algorithm
                    })
                else:  # 使用证书
                    # 检查证书路径
                    cert_path = self.verify_cert_path_edit.text()
                    if not cert_path:
                        QMessageBox.warning(self, "警告", "请选择证书文件")
                        return
                    
                    # 使用证书验证
                    result_verify = self.file_signer_service.verify_file_signature_with_cert({
                        "file_path": file_path,
                        "signature": signature,
                        "certificate": cert_path,
                        "hash_algorithm": hash_algorithm
                    })
                
                # 构造结果格式
                if result_verify.get("success"):
                    result_verify["data"] = {
                        "valid": result_verify["data"],
                        "reason": "文件签名验证成功" if result_verify["data"] else "文件签名验证失败",
                        "file_info": file_info
                    }
            
            if not result_verify.get("success"):
                raise Exception(result_verify.get("error", "验证文件签名失败"))
            
            result = result_verify["data"]
            
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
