from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from src.cert_manager.core.services import KeyService, ConfigService
from src.cert_manager.core.utils import file_utils

class KeyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.key_service = KeyService()
        self.config_service = ConfigService()
        self.algorithms = self.config_service.get_algorithms()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 密钥生成组
        generate_group = QGroupBox("生成密钥对")
        generate_layout = QVBoxLayout()
        
        # 密钥类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("密钥类型:"))
        self.key_type_combo = QComboBox()
        self.key_type_combo.addItems(["RSA", "ECC"])
        self.key_type_combo.currentTextChanged.connect(self.on_key_type_changed)
        type_layout.addWidget(self.key_type_combo)
        type_layout.addStretch()
        generate_layout.addLayout(type_layout)
        
        # RSA参数
        self.rsa_group = QGroupBox("RSA参数")
        rsa_layout = QHBoxLayout()
        rsa_layout.addWidget(QLabel("密钥大小:"))
        self.rsa_key_size_combo = QComboBox()
        for size in self.algorithms.get("rsa_key_sizes", [2048, 3072, 4096]):
            self.rsa_key_size_combo.addItem(str(size))
        rsa_layout.addWidget(self.rsa_key_size_combo)
        rsa_layout.addStretch()
        self.rsa_group.setLayout(rsa_layout)
        generate_layout.addWidget(self.rsa_group)
        
        # ECC参数
        self.ecc_group = QGroupBox("ECC参数")
        ecc_layout = QHBoxLayout()
        ecc_layout.addWidget(QLabel("曲线类型:"))
        self.ecc_curve_combo = QComboBox()
        # 使用大写曲线名称以匹配cryptography库
        for curve in self.algorithms.get("ecc_curves", ["SECP256R1", "SECP384R1", "SECP521R1"]):
            self.ecc_curve_combo.addItem(curve)
        ecc_layout.addWidget(self.ecc_curve_combo)
        ecc_layout.addStretch()
        self.ecc_group.setLayout(ecc_layout)
        self.ecc_group.setVisible(False)
        generate_layout.addWidget(self.ecc_group)
        
        # 生成按钮
        generate_btn = QPushButton("生成密钥对")
        generate_btn.clicked.connect(self.generate_key)
        generate_layout.addWidget(generate_btn)
        
        generate_group.setLayout(generate_layout)
        layout.addWidget(generate_group)
        
        # 密钥信息组
        info_group = QGroupBox("密钥信息")
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 操作按钮组
        button_group = QHBoxLayout()
        
        self.save_private_btn = QPushButton("保存私钥")
        self.save_private_btn.clicked.connect(self.save_private_key)
        self.save_private_btn.setEnabled(False)
        button_group.addWidget(self.save_private_btn)
        
        self.save_public_btn = QPushButton("保存公钥")
        self.save_public_btn.clicked.connect(self.save_public_key)
        self.save_public_btn.setEnabled(False)
        button_group.addWidget(self.save_public_btn)
        
        button_group.addStretch()
        layout.addLayout(button_group)
        
        # 存储密钥组
        stored_group = QGroupBox("存储的密钥")
        stored_layout = QVBoxLayout()
        
        # 密钥列表
        self.key_list = QListWidget()
        self.key_list.itemClicked.connect(self.on_key_selected)
        stored_layout.addWidget(self.key_list)
        
        # 密钥操作按钮
        key_ops_layout = QHBoxLayout()
        self.refresh_keys_btn = QPushButton("刷新列表")
        self.refresh_keys_btn.clicked.connect(self.refresh_key_list)
        key_ops_layout.addWidget(self.refresh_keys_btn)
        
        self.load_key_btn = QPushButton("加载密钥")
        self.load_key_btn.clicked.connect(self.load_key_from_config)
        self.load_key_btn.setEnabled(False)
        key_ops_layout.addWidget(self.load_key_btn)
        
        self.delete_key_btn = QPushButton("删除密钥")
        self.delete_key_btn.clicked.connect(self.delete_selected_key)
        self.delete_key_btn.setEnabled(False)
        key_ops_layout.addWidget(self.delete_key_btn)
        
        key_ops_layout.addStretch()
        stored_layout.addLayout(key_ops_layout)
        
        stored_group.setLayout(stored_layout)
        layout.addWidget(stored_group)
        
        self.setLayout(layout)
        self.current_private_key = None
        self.current_public_key = None
        self.selected_key_id = None
        
        # 初始刷新密钥列表
        self.refresh_key_list()
    
    def on_key_type_changed(self, text):
        if text == "RSA":
            self.rsa_group.setVisible(True)
            self.ecc_group.setVisible(False)
        else:
            self.rsa_group.setVisible(False)
            self.ecc_group.setVisible(True)
    
    def generate_key(self):
        try:
            key_type = self.key_type_combo.currentText()
            
            if key_type == "RSA":
                key_size = int(self.rsa_key_size_combo.currentText())
                private_info, public_info = self.key_service.generate_rsa_key(key_size)
                # 注意：服务层返回的是密钥信息，不是密钥对象，所以需要重新加载密钥
                # 这里简化处理，直接使用服务层返回的信息
                self.current_private_key = None  # 实际应用中应该从存储加载
                self.current_public_key = None  # 实际应用中应该从存储加载
            else:
                curve = self.ecc_curve_combo.currentText()
                private_info, public_info = self.key_service.generate_ecc_key(curve)
                # 注意：服务层返回的是密钥信息，不是密钥对象，所以需要重新加载密钥
                # 这里简化处理，直接使用服务层返回的信息
                self.current_private_key = None  # 实际应用中应该从存储加载
                self.current_public_key = None  # 实际应用中应该从存储加载
            
            # 显示密钥信息
            info_text = f"私钥信息:\n"
            for key, value in private_info.items():
                info_text += f"{key}: {value}\n"
            info_text += f"\n公钥信息:\n"
            for key, value in public_info.items():
                info_text += f"{key}: {value}\n"
            info_text += f"\n已自动存储到配置文件中（使用根密钥加密）"
            
            self.info_text.setText(info_text)
            
            # 启用保存按钮
            # 注意：由于我们没有实际的密钥对象，这里暂时禁用保存按钮
            # 实际应用中应该从存储加载密钥对象后再启用
            self.save_private_btn.setEnabled(False)
            self.save_public_btn.setEnabled(False)
            
            # 刷新密钥列表
            self.refresh_key_list()
            
            QMessageBox.information(self, "成功", "密钥生成并自动存储成功")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成密钥失败: {str(e)}")
    
    def refresh_key_list(self):
        """刷新存储的密钥列表"""
        try:
            self.key_list.clear()
            # 默认按最新时间排序
            keys = self.key_service.list_keys()
            
            for key in keys:
                # 直接显示ID，不做复杂处理
                display_text = f"{key['id']} - {key['type']} - {key['private_info'].get('key_size', key['private_info'].get('curve', ''))}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, key['id'])
                self.key_list.addItem(item)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新密钥列表失败: {str(e)}")
    
    def on_key_selected(self, item):
        """当选择密钥时"""
        self.selected_key_id = item.data(Qt.UserRole)
        self.load_key_btn.setEnabled(True)
        self.delete_key_btn.setEnabled(True)
    
    def delete_selected_key(self):
        """删除选中的密钥"""
        if not self.selected_key_id:
            return
        
        # 确认删除
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "确认删除", 
                                    f"确定要删除密钥 {self.selected_key_id} 吗？此操作不可撤销。",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                success = self.key_service.delete_key(self.selected_key_id)
                if success:
                    QMessageBox.information(self, "成功", "密钥删除成功")
                    # 刷新密钥列表
                    self.refresh_key_list()
                    # 清除选中状态
                    self.selected_key_id = None
                    self.load_key_btn.setEnabled(False)
                    self.delete_key_btn.setEnabled(False)
                else:
                    QMessageBox.warning(self, "失败", "密钥删除失败，可能密钥不存在")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除密钥时出错: {str(e)}")
    
    def load_key_from_config(self):
        """从配置加载密钥"""
        if not self.selected_key_id:
            return
        
        try:
            # 使用根密钥自动解密
            private_key, public_key = self.key_service.load_key_pair(self.selected_key_id)
            
            self.current_private_key = private_key
            self.current_public_key = public_key
            
            # 显示密钥信息
            private_info = self.key_service.get_key_info(private_key)
            public_info = self.key_service.get_key_info(public_key)
            
            info_text = f"私钥信息:\n"
            for key, value in private_info.items():
                info_text += f"{key}: {value}\n"
            info_text += f"\n公钥信息:\n"
            for key, value in public_info.items():
                info_text += f"{key}: {value}\n"
            info_text += f"\n从配置文件加载（使用根密钥解密）"
            
            self.info_text.setText(info_text)
            
            # 启用保存按钮
            self.save_private_btn.setEnabled(True)
            self.save_public_btn.setEnabled(True)
            
            QMessageBox.information(self, "成功", "密钥加载成功")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载密钥失败: {str(e)}")
    
    def save_private_key(self):
        if not self.current_private_key:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存私钥", "", "PEM Files (*.pem);;DER Files (*.der)")
        if not file_path:
            return
        
        try:
            # 询问是否需要密码保护
            from PyQt5.QtWidgets import QInputDialog
            password, ok = QInputDialog.getText(self, "密码保护", "输入密码 (可选):", QLineEdit.Password)
            if not ok:
                return
            
            # 确定文件格式
            format = "pem" if file_path.endswith(".pem") else "der"
            
            self.key_service.save_private_key(self.current_private_key, file_path, password if password else None)
            QMessageBox.information(self, "成功", "私钥保存成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存私钥失败: {str(e)}")
    
    def save_public_key(self):
        if not self.current_public_key:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存公钥", "", "PEM Files (*.pem);;DER Files (*.der)")
        if not file_path:
            return
        
        try:
            # 确定文件格式
            format = "pem" if file_path.endswith(".pem") else "der"
            
            self.key_service.save_public_key(self.current_public_key, file_path)
            QMessageBox.information(self, "成功", "公钥保存成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存公钥失败: {str(e)}")
