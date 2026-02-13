from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox, QSpinBox, QTabWidget, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
# 使用正确的绝对导入路径
import sys
import os
# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.services import CertService, KeyService, ConfigService
from core.utils import file_utils

class CertTab(QWidget):
    def __init__(self):
        super().__init__()
        self.cert_service = CertService()
        self.key_service = KeyService()
        self.config_service = ConfigService()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建子标签页
        self.tab_widget = QTabWidget()
        
        # 自签名证书标签页
        self.self_signed_tab = QWidget()
        self.init_self_signed_tab()
        
        # 二级证书签名标签页
        self.sign_tab = QWidget()
        self.init_sign_tab()
        
        # 现有证书管理标签页
        self.existing_cert_tab = QWidget()
        self.init_existing_cert_tab()
        
        # 添加子标签页
        self.tab_widget.addTab(self.self_signed_tab, "自签名证书")
        self.tab_widget.addTab(self.sign_tab, "二级证书签名")
        self.tab_widget.addTab(self.existing_cert_tab, "现有证书管理")
        
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
        self.current_cert = None
    
    def init_self_signed_tab(self):
        """初始化自签名证书标签页"""
        layout = QVBoxLayout()
        
        # 证书生成组
        generate_group = QGroupBox("生成自签名证书")
        generate_layout = QVBoxLayout()
        
        # 存储的密钥对选择
        stored_key_layout = QHBoxLayout()
        stored_key_layout.addWidget(QLabel("存储的密钥对:"))
        self.stored_key_combo = QComboBox()
        self.stored_key_combo.addItem("选择存储的密钥对")
        self.stored_key_combo.currentIndexChanged.connect(self.on_stored_key_selected)
        stored_key_layout.addWidget(self.stored_key_combo)
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_stored_keys)
        stored_key_layout.addWidget(refresh_btn)
        generate_layout.addLayout(stored_key_layout)
        
        # 私钥选择
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("私钥文件:"))
        self.key_path_edit = QLineEdit()
        key_layout.addWidget(self.key_path_edit)
        key_btn = QPushButton("浏览")
        key_btn.clicked.connect(self.browse_key)
        key_layout.addWidget(key_btn)
        generate_layout.addLayout(key_layout)
        
        # 公钥选择
        pub_key_layout = QHBoxLayout()
        pub_key_layout.addWidget(QLabel("公钥文件:"))
        self.pub_key_path_edit = QLineEdit()
        pub_key_layout.addWidget(self.pub_key_path_edit)
        pub_key_btn = QPushButton("浏览")
        pub_key_btn.clicked.connect(self.browse_pub_key)
        pub_key_layout.addWidget(pub_key_btn)
        generate_layout.addLayout(pub_key_layout)
        
        # 证书参数
        param_layout = QHBoxLayout()
        
        # 有效期
        param_layout.addWidget(QLabel("有效期 (天):"))
        self.validity_spin = QSpinBox()
        self.validity_spin.setRange(1, 3650)
        self.validity_spin.setValue(365)
        param_layout.addWidget(self.validity_spin)
        
        # 正向偏移量
        param_layout.addWidget(QLabel("正向偏移量 (秒):"))
        self.offset_spin = QSpinBox()
        self.offset_spin.setRange(0, 86400)
        self.offset_spin.setValue(0)
        param_layout.addWidget(self.offset_spin)
        
        param_layout.addStretch()
        generate_layout.addLayout(param_layout)
        
        # 生成按钮
        generate_btn = QPushButton("生成证书")
        generate_btn.clicked.connect(self.generate_cert)
        generate_layout.addWidget(generate_btn)
        
        generate_group.setLayout(generate_layout)
        layout.addWidget(generate_group)
        
        # 证书信息组
        info_group = QGroupBox("证书信息")
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 操作按钮组
        button_group = QHBoxLayout()
        
        self.save_cert_btn = QPushButton("保存证书")
        self.save_cert_btn.clicked.connect(self.save_cert)
        self.save_cert_btn.setEnabled(False)
        button_group.addWidget(self.save_cert_btn)
        
        button_group.addStretch()
        layout.addLayout(button_group)
        
        self.self_signed_tab.setLayout(layout)
        # 初始化时刷新存储的密钥对
        self.refresh_stored_keys()
    
    def refresh_stored_keys(self):
        """刷新存储的密钥对列表"""
        # 清空下拉框
        self.stored_key_combo.clear()
        self.stored_key_combo.addItem("选择存储的密钥对")
        
        # 获取存储的密钥对列表
        try:
            keys = self.key_service.list_keys()
            for key_info in keys:
                key_id = key_info["id"]
                key_type = key_info["type"]
                created_at = key_info["created_at"]
                # 显示格式：类型_时间戳 (创建时间)
                display_text = f"{key_type}_{key_id.split('_')[-1]} ({created_at[:10]})"
                self.stored_key_combo.addItem(display_text, key_id)
        except Exception as e:
            print(f"刷新密钥对列表失败: {str(e)}")
    
    def on_stored_key_selected(self, index):
        """处理存储密钥对选择事件"""
        if index == 0:  # 选择了"选择存储的密钥对"选项
            self.key_path_edit.clear()
            self.pub_key_path_edit.clear()
            return
        
        # 获取选择的密钥对ID
        key_id = self.stored_key_combo.itemData(index)
        if not key_id:
            return
        
        # 构建密钥文件路径
        import os
        # 构建相对于当前文件的路径
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        key_folder = os.path.join(current_dir, "cert_manager", "configs", "key", key_id)
        private_key_path = os.path.join(key_folder, f"{key_id}_private.pem")
        public_key_path = os.path.join(key_folder, f"{key_id}_public.pem")
        
        # 检查文件是否存在
        if file_utils.file_exists(private_key_path) and file_utils.file_exists(public_key_path):
            self.key_path_edit.setText(private_key_path)
            self.pub_key_path_edit.setText(public_key_path)
        else:
            QMessageBox.warning(self, "警告", "选中的密钥对文件不存在")
            self.stored_key_combo.setCurrentIndex(0)
    
    def init_sign_tab(self):
        """初始化二级证书签名标签页"""
        layout = QVBoxLayout()
        
        # 证书签名组
        sign_group = QGroupBox("二级证书签名")
        sign_layout = QVBoxLayout()
        
        # 上级证书选择
        parent_cert_layout = QHBoxLayout()
        parent_cert_layout.addWidget(QLabel("上级证书文件:"))
        self.parent_cert_path_edit = QLineEdit()
        parent_cert_layout.addWidget(self.parent_cert_path_edit)
        parent_cert_btn = QPushButton("浏览")
        parent_cert_btn.clicked.connect(self.browse_parent_cert)
        parent_cert_layout.addWidget(parent_cert_btn)
        sign_layout.addLayout(parent_cert_layout)
        
        # 上级私钥选择
        parent_key_layout = QHBoxLayout()
        parent_key_layout.addWidget(QLabel("上级私钥文件:"))
        self.parent_key_path_edit = QLineEdit()
        parent_key_layout.addWidget(self.parent_key_path_edit)
        parent_key_btn = QPushButton("浏览")
        parent_key_btn.clicked.connect(self.browse_parent_key)
        parent_key_layout.addWidget(parent_key_btn)
        sign_layout.addLayout(parent_key_layout)
        
        # 二级公钥选择
        secondary_pub_key_layout = QHBoxLayout()
        secondary_pub_key_layout.addWidget(QLabel("二级公钥文件:"))
        self.secondary_pub_key_path_edit = QLineEdit()
        secondary_pub_key_layout.addWidget(self.secondary_pub_key_path_edit)
        secondary_pub_key_btn = QPushButton("浏览")
        secondary_pub_key_btn.clicked.connect(self.browse_secondary_pub_key)
        secondary_pub_key_layout.addWidget(secondary_pub_key_btn)
        sign_layout.addLayout(secondary_pub_key_layout)
        

        
        # 证书参数
        param_layout = QHBoxLayout()
        
        # 有效期
        param_layout.addWidget(QLabel("有效期 (天):"))
        self.sign_validity_spin = QSpinBox()
        self.sign_validity_spin.setRange(1, 3650)
        self.sign_validity_spin.setValue(365)
        param_layout.addWidget(self.sign_validity_spin)
        
        # 正向偏移量
        param_layout.addWidget(QLabel("正向偏移量 (秒):"))
        self.sign_offset_spin = QSpinBox()
        self.sign_offset_spin.setRange(0, 86400)
        self.sign_offset_spin.setValue(0)
        param_layout.addWidget(self.sign_offset_spin)
        
        param_layout.addStretch()
        sign_layout.addLayout(param_layout)
        
        # 签名按钮
        sign_btn = QPushButton("签名证书")
        sign_btn.clicked.connect(self.sign_cert)
        sign_layout.addWidget(sign_btn)
        
        sign_group.setLayout(sign_layout)
        layout.addWidget(sign_group)
        
        # 证书信息组
        info_group = QGroupBox("证书信息")
        info_layout = QVBoxLayout()
        self.sign_info_text = QTextEdit()
        self.sign_info_text.setReadOnly(True)
        info_layout.addWidget(self.sign_info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 操作按钮组
        button_group = QHBoxLayout()
        
        self.save_signed_cert_btn = QPushButton("保存签名证书")
        self.save_signed_cert_btn.clicked.connect(self.save_signed_cert)
        self.save_signed_cert_btn.setEnabled(False)
        button_group.addWidget(self.save_signed_cert_btn)
        
        button_group.addStretch()
        layout.addLayout(button_group)
        
        self.sign_tab.setLayout(layout)
    
    def init_existing_cert_tab(self):
        """初始化现有证书管理标签页"""
        layout = QVBoxLayout()
        
        # 证书列表组
        list_group = QGroupBox("证书列表")
        list_layout = QVBoxLayout()
        
        # 证书列表
        self.cert_list = QListWidget()
        self.cert_list.currentItemChanged.connect(self.on_cert_selected)
        list_layout.addWidget(self.cert_list)
        
        # 操作按钮组
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_cert_list)
        button_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_cert)
        button_layout.addWidget(delete_btn)
        
        import_btn = QPushButton("导入")
        import_btn.clicked.connect(self.import_cert)
        button_layout.addWidget(import_btn)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # 证书信息组
        info_group = QGroupBox("证书信息")
        info_layout = QVBoxLayout()
        self.cert_detail_info = QTextEdit()
        self.cert_detail_info.setReadOnly(True)
        info_layout.addWidget(self.cert_detail_info)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        self.existing_cert_tab.setLayout(layout)
        
        # 初始化时刷新证书列表
        self.refresh_cert_list()
    
    def refresh_cert_list(self):
        """刷新证书列表"""
        # 清空列表
        self.cert_list.clear()
        
        # 获取证书列表
        try:
            certs = self.cert_service.list_certs()
            for cert_info in certs:
                filename = cert_info["filename"]
                cert_type = cert_info["type"]
                timestamp = cert_info["cert_info"].get("timestamp", "未知")
                
                # 创建列表项
                item_text = f"{filename} ({cert_type})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, cert_info)
                self.cert_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新证书列表失败: {str(e)}")
    
    def on_cert_selected(self, current, previous):
        """处理证书选择事件"""
        if current:
            # 获取证书信息
            cert_info = current.data(Qt.UserRole)
            if cert_info:
                # 显示证书详细信息
                detail_text = "证书详情:\n"
                detail_text += f"文件名: {cert_info['filename']}\n"
                detail_text += f"路径: {cert_info['path']}\n"
                detail_text += f"类型: {cert_info['type']}\n"
                detail_text += f"根证书: {'是' if cert_info.get('is_root_cert', False) else '否'}\n"
                if not cert_info.get('is_root_cert', False):
                    detail_text += "上级证书公钥: 存在\n"
                detail_text += "\n证书信息:\n"
                
                for key, value in cert_info['cert_info'].items():
                    detail_text += f"  - {key}: {value}\n"
                
                self.cert_detail_info.setText(detail_text)
    
    def delete_cert(self):
        """删除选中的证书"""
        current_item = self.cert_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要删除的证书")
            return
        
        cert_info = current_item.data(Qt.UserRole)
        if not cert_info:
            return
        
        # 确认删除
        reply = QMessageBox.question(self, "确认", f"确定要删除证书 {cert_info['filename']} 吗？",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 删除证书
            success = self.cert_service.delete_cert(cert_info['path'])
            if success:
                QMessageBox.information(self, "成功", "证书删除成功")
                # 刷新证书列表
                self.refresh_cert_list()
                # 清空证书信息
                self.cert_detail_info.clear()
            else:
                QMessageBox.critical(self, "错误", "证书删除失败")
    
    def import_cert(self):
        """导入证书"""
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(self, "选择证书文件", "", "JSON Files (*.json)")
        if not file_path:
            return
        
        try:
            # 导入证书
            cert_data = self.cert_service.import_cert(file_path)
            QMessageBox.information(self, "成功", "证书导入成功")
            # 刷新证书列表
            self.refresh_cert_list()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"证书导入失败: {str(e)}")
    
    def browse_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择私钥文件", "", "PEM Files (*.pem);;DER Files (*.der)")
        if file_path:
            self.key_path_edit.setText(file_path)
    
    def browse_parent_key(self):
        """浏览上级私钥文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择上级私钥文件", "", "PEM Files (*.pem);;DER Files (*.der)")
        if file_path:
            self.parent_key_path_edit.setText(file_path)
    
    def browse_ca_cert(self):
        """浏览CA证书文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择CA证书文件", "", "PEM Files (*.pem);;DER Files (*.der)")
        if file_path:
            self.ca_cert_path_edit.setText(file_path)
    
    def browse_csr(self):
        """浏览CSR文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择证书请求文件", "", "PEM Files (*.pem);;DER Files (*.der)")
        if file_path:
            self.csr_path_edit.setText(file_path)
    
    def browse_pub_key(self):
        """浏览公钥文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择公钥文件", "", "PEM Files (*.pem);;DER Files (*.der)")
        if file_path:
            self.pub_key_path_edit.setText(file_path)
    
    def browse_secondary_pub_key(self):
        """浏览二级公钥文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择二级公钥文件", "", "PEM Files (*.pem);;DER Files (*.der)")
        if file_path:
            self.secondary_pub_key_path_edit.setText(file_path)
    
    def browse_parent_cert(self):
        """浏览上级证书文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择上级证书文件", "", "JSON Files (*.json)")
        if file_path:
            self.parent_cert_path_edit.setText(file_path)
    
    def generate_cert(self):
        try:
            # 加载私钥
            key_path = self.key_path_edit.text()
            if not key_path:
                QMessageBox.warning(self, "警告", "请选择私钥文件")
                return
            
            # 加载公钥
            pub_key_path = self.pub_key_path_edit.text()
            if not pub_key_path:
                QMessageBox.warning(self, "警告", "请选择公钥文件")
                return
            
            private_key = self.key_service.load_private_key(key_path, None)
            public_key = self.key_service.load_public_key(pub_key_path)
            
            # 生成证书
            validity_days = self.validity_spin.value()
            forward_offset = self.offset_spin.value()
            
            cert_data = self.cert_service.generate_self_signed_cert(
                public_key,
                private_key,
                validity_days,
                forward_offset
            )
            
            self.current_cert = cert_data
            
            # 显示证书信息
            cert_info = self.cert_service.get_cert_info(cert_data)
            info_text = "证书信息:\n"
            for key, value in cert_info.items():
                if isinstance(value, dict):
                    info_text += f"{key}:\n"
                    for sub_key, sub_value in value.items():
                        info_text += f"  - {sub_key}: {sub_value}\n"
                else:
                    info_text += f"{key}: {value}\n"
            
            self.info_text.setText(info_text)
            
            # 启用保存按钮
            self.save_cert_btn.setEnabled(True)
            
            QMessageBox.information(self, "成功", "证书生成成功")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成证书失败: {str(e)}")
    
    def save_cert(self):
        if not self.current_cert:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存证书", "", "JSON Files (*.json)")
        if not file_path:
            return
        
        try:
            self.cert_service.save_cert(self.current_cert, file_path)
            QMessageBox.information(self, "成功", "证书保存成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存证书失败: {str(e)}")
    
    def sign_cert(self):
        """签名证书"""
        try:
            # 加载上级证书
            parent_cert_path = self.parent_cert_path_edit.text()
            if not parent_cert_path:
                QMessageBox.warning(self, "警告", "请选择上级证书文件")
                return
            
            # 加载上级私钥
            parent_key_path = self.parent_key_path_edit.text()
            if not parent_key_path:
                QMessageBox.warning(self, "警告", "请选择上级私钥文件")
                return
            
            # 加载二级公钥
            secondary_pub_key_path = self.secondary_pub_key_path_edit.text()
            if not secondary_pub_key_path:
                QMessageBox.warning(self, "警告", "请选择二级公钥文件")
                return
            
            # 加载上级证书以获取公钥
            parent_cert_data = self.cert_service.load_cert(parent_cert_path)
            parent_public_key_hex = parent_cert_data.get("public_key", "")
            if not parent_public_key_hex:
                QMessageBox.warning(self, "警告", "上级证书文件无效，缺少public_key字段")
                return
            
            # 加载上级私钥
            parent_private_key = self.key_service.load_private_key(parent_key_path, None)
            
            # 加载上级公钥
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            parent_public_key_data = bytes.fromhex(parent_public_key_hex)
            parent_public_key = serialization.load_der_public_key(
                parent_public_key_data,
                backend=default_backend()
            )
            
            # 加载二级公钥
            secondary_public_key = self.key_service.load_public_key(secondary_pub_key_path)
            
            # 签名证书
            validity_days = self.sign_validity_spin.value()
            forward_offset = self.sign_offset_spin.value()
            
            cert_data = self.cert_service.generate_secondary_cert(
                secondary_public_key,
                parent_private_key,
                parent_public_key,
                validity_days,
                forward_offset
            )
            
            self.current_sign_cert = cert_data
            
            # 显示证书信息
            cert_info = self.cert_service.get_cert_info(cert_data)
            info_text = "证书信息:\n"
            for key, value in cert_info.items():
                if isinstance(value, dict):
                    info_text += f"{key}:\n"
                    for sub_key, sub_value in value.items():
                        info_text += f"  - {sub_key}: {sub_value}\n"
                else:
                    info_text += f"{key}: {value}\n"
            
            self.sign_info_text.setText(info_text)
            
            # 启用保存按钮
            self.save_signed_cert_btn.setEnabled(True)
            
            QMessageBox.information(self, "成功", "证书签名成功")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"签名证书失败: {str(e)}")
    
    def save_signed_cert(self):
        """保存签名后的证书"""
        if not self.current_sign_cert:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存签名证书", "", "JSON Files (*.json)")
        if not file_path:
            return
        
        try:
            self.cert_service.save_cert(self.current_sign_cert, file_path)
            QMessageBox.information(self, "成功", "证书保存成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存证书失败: {str(e)}")
