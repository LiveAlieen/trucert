from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog, QMessageBox, QTabWidget
from PyQt5.QtCore import Qt
import sys
import os
# 使用相对导入
from ..core.services import FileSignerService, KeyService, ConfigService
from ..core.utils import file_utils

class FileTab(QWidget):
    def __init__(self):
        super().__init__()
        self.file_signer_service = FileSignerService()
        self.key_service = KeyService()
        self.config_service = ConfigService()
        self.algorithms = self.config_service.get_algorithms()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 单个文件签名标签页
        self.single_file_tab = QWidget()
        self.init_single_file_tab()
        
        # 批量签名标签页
        self.batch_file_tab = QWidget()
        self.init_batch_file_tab()
        
        # 添加标签页
        self.tab_widget.addTab(self.single_file_tab, "单个文件签名")
        self.tab_widget.addTab(self.batch_file_tab, "批量签名")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        self.current_signature = None
        self.batch_files = []
    
    def init_single_file_tab(self):
        """初始化单个文件签名标签页"""
        layout = QVBoxLayout()
        
        # 文件签名组
        sign_group = QGroupBox("文件签名")
        sign_layout = QVBoxLayout()
        
        # 文件选择
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("文件:"))
        self.file_path_edit = QLineEdit()
        file_layout.addWidget(self.file_path_edit)
        file_btn = QPushButton("浏览")
        file_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(file_btn)
        sign_layout.addLayout(file_layout)
        
        # 私钥选择
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("私钥文件:"))
        self.key_path_edit = QLineEdit()
        key_layout.addWidget(self.key_path_edit)
        key_btn = QPushButton("浏览")
        key_btn.clicked.connect(self.browse_key)
        key_layout.addWidget(key_btn)
        sign_layout.addLayout(key_layout)
        
        # 哈希算法
        hash_layout = QHBoxLayout()
        hash_layout.addWidget(QLabel("哈希算法:"))
        self.hash_combo = QComboBox()
        for algo in self.algorithms.get("hash_algorithms", ["sha256", "sha384", "sha512"]):
            self.hash_combo.addItem(algo)
        hash_layout.addWidget(self.hash_combo)
        hash_layout.addStretch()
        sign_layout.addLayout(hash_layout)
        
        # 签名按钮
        sign_btn = QPushButton("签名文件")
        sign_btn.clicked.connect(self.sign_file)
        sign_layout.addWidget(sign_btn)
        
        sign_group.setLayout(sign_layout)
        layout.addWidget(sign_group)
        
        # 签名信息组
        info_group = QGroupBox("签名信息")
        info_layout = QVBoxLayout()
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 操作按钮组
        button_group = QHBoxLayout()
        
        self.save_sig_btn = QPushButton("保存签名")
        self.save_sig_btn.clicked.connect(self.save_signature)
        self.save_sig_btn.setEnabled(False)
        button_group.addWidget(self.save_sig_btn)
        
        self.attach_sig_btn = QPushButton("附加到文件")
        self.attach_sig_btn.clicked.connect(self.attach_signature)
        self.attach_sig_btn.setEnabled(False)
        button_group.addWidget(self.attach_sig_btn)
        
        button_group.addStretch()
        layout.addLayout(button_group)
        
        self.single_file_tab.setLayout(layout)
    
    def init_batch_file_tab(self):
        """初始化批量签名标签页"""
        layout = QVBoxLayout()
        
        # 批量签名组
        batch_group = QGroupBox("批量签名")
        batch_layout = QVBoxLayout()
        
        # 多个文件选择
        batch_file_layout = QHBoxLayout()
        batch_file_layout.addWidget(QLabel("文件:", alignment=Qt.AlignTop))
        self.batch_file_list = QTextEdit()
        self.batch_file_list.setReadOnly(True)
        self.batch_file_list.setFixedHeight(80)
        batch_file_layout.addWidget(self.batch_file_list)
        batch_file_btn = QPushButton("选择多个文件")
        batch_file_btn.clicked.connect(self.browse_batch_files)
        batch_file_layout.addWidget(batch_file_btn)
        batch_layout.addLayout(batch_file_layout)
        
        # 私钥选择
        batch_key_layout = QHBoxLayout()
        batch_key_layout.addWidget(QLabel("私钥文件:"))
        self.batch_key_path_edit = QLineEdit()
        batch_key_layout.addWidget(self.batch_key_path_edit)
        batch_key_btn = QPushButton("浏览")
        batch_key_btn.clicked.connect(self.browse_batch_key)
        batch_key_layout.addWidget(batch_key_btn)
        batch_layout.addLayout(batch_key_layout)
        
        # 哈希算法
        batch_hash_layout = QHBoxLayout()
        batch_hash_layout.addWidget(QLabel("哈希算法:"))
        self.batch_hash_combo = QComboBox()
        for algo in self.algorithms.get("hash_algorithms", ["sha256", "sha384", "sha512"]):
            self.batch_hash_combo.addItem(algo)
        batch_hash_layout.addWidget(self.batch_hash_combo)
        batch_hash_layout.addStretch()
        batch_layout.addLayout(batch_hash_layout)
        
        # 输出目录选择
        batch_output_layout = QHBoxLayout()
        batch_output_layout.addWidget(QLabel("输出目录:"))
        self.batch_output_edit = QLineEdit()
        batch_output_layout.addWidget(self.batch_output_edit)
        batch_output_btn = QPushButton("浏览")
        batch_output_btn.clicked.connect(self.browse_batch_output)
        batch_output_layout.addWidget(batch_output_btn)
        batch_layout.addLayout(batch_output_layout)
        
        # 批量签名按钮
        batch_sign_btn = QPushButton("批量签名")
        batch_sign_btn.clicked.connect(self.batch_sign_files)
        batch_layout.addWidget(batch_sign_btn)
        
        # 批量签名结果
        self.batch_result_text = QTextEdit()
        self.batch_result_text.setReadOnly(True)
        self.batch_result_text.setFixedHeight(100)
        batch_layout.addWidget(self.batch_result_text)
        
        batch_group.setLayout(batch_layout)
        layout.addWidget(batch_group)
        
        self.batch_file_tab.setLayout(layout)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def browse_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择私钥文件", "", "PEM Files (*.pem);;DER Files (*.der)")
        if file_path:
            self.key_path_edit.setText(file_path)
    
    def sign_file(self):
        try:
            # 检查文件路径
            file_path = self.file_path_edit.text()
            if not file_path:
                QMessageBox.warning(self, "警告", "请选择文件")
                return
            
            # 检查私钥路径
            key_path = self.key_path_edit.text()
            if not key_path:
                QMessageBox.warning(self, "警告", "请选择私钥文件")
                return
            
            # 加载私钥
            result_key = self.key_service.load_private_key({"file_path": key_path, "password": None})
            if not result_key.get("success"):
                raise Exception(result_key.get("error", "加载私钥失败"))
            private_key = result_key["data"]
            
            # 获取哈希算法
            hash_algorithm = self.hash_combo.currentText()
            
            # 签名文件
            result_sign = self.file_signer_service.sign_file({"file_path": file_path, "private_key": private_key, "hash_algorithm": hash_algorithm})
            if not result_sign.get("success"):
                raise Exception(result_sign.get("error", "签名文件失败"))
            signature = result_sign["data"]
            
            self.current_signature = signature
            
            # 显示签名信息
            result_file_info = self.file_signer_service.get_file_info({"file_path": file_path})
            if not result_file_info.get("success"):
                raise Exception(result_file_info.get("error", "获取文件信息失败"))
            file_info = result_file_info["data"]
            
            info_text = "文件信息:\n"
            for key, value in file_info.items():
                info_text += f"{key}: {value}\n"
            
            info_text += f"\n签名信息:\n"
            info_text += f"哈希算法: {hash_algorithm}\n"
            info_text += f"签名长度: {len(signature)} bytes\n"
            info_text += f"签名 (前20字节): {signature[:20].hex()}..."
            
            self.info_text.setText(info_text)
            
            # 启用按钮
            self.save_sig_btn.setEnabled(True)
            self.attach_sig_btn.setEnabled(True)
            
            QMessageBox.information(self, "成功", "文件签名成功")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"签名失败: {str(e)}")
    
    def save_signature(self):
        if not self.current_signature:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "保存签名", "", "JSON Files (*.json)")
        if not file_path:
            return
        
        try:
            # 保存为JSON格式
            hash_algorithm = self.hash_combo.currentText()
            original_file = self.file_path_edit.text()
            
            result = self.file_signer_service.save_signature({
                "signature": self.current_signature,
                "file_path": file_path,
                "original_file_path": original_file,
                "hash_algorithm": hash_algorithm
            })
            
            if not result.get("success"):
                raise Exception(result.get("error", "保存签名失败"))
            
            QMessageBox.information(self, "成功", "签名保存成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存签名失败: {str(e)}")
    
    def attach_signature(self):
        if not self.current_signature:
            return
        
        file_path = self.file_path_edit.text()
        if not file_path:
            return
        
        output_path, _ = QFileDialog.getSaveFileName(self, "保存带签名的文件", file_path + ".signed", "All Files (*)")
        if not output_path:
            return
        
        try:
            result = self.file_signer_service.attach_signature_to_file({
                "original_file": file_path,
                "signature": self.current_signature,
                "output_file": output_path
            })
            
            if not result.get("success"):
                raise Exception(result.get("error", "附加签名失败"))
            
            result_path = result["data"]
            QMessageBox.information(self, "成功", f"签名已附加到文件: {result_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"附加签名失败: {str(e)}")
    
    def browse_batch_files(self):
        """选择多个文件进行批量签名"""
        file_paths, _ = QFileDialog.getOpenFileNames(self, "选择多个文件", "", "All Files (*)")
        if file_paths:
            self.batch_files = file_paths
            # 显示选择的文件列表
            file_list_text = "\n".join(file_paths)
            self.batch_file_list.setText(file_list_text)
    
    def browse_batch_output(self):
        """选择批量签名的输出目录"""
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if output_dir:
            self.batch_output_edit.setText(output_dir)
    
    def browse_batch_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择私钥文件", "", "PEM Files (*.pem);;DER Files (*.der)")
        if file_path:
            self.batch_key_path_edit.setText(file_path)
    
    def batch_sign_files(self):
        """执行批量签名"""
        try:
            # 检查文件列表
            if not self.batch_files:
                QMessageBox.warning(self, "警告", "请选择要签名的文件")
                return
            
            # 检查输出目录
            output_dir = self.batch_output_edit.text()
            if not output_dir:
                QMessageBox.warning(self, "警告", "请选择输出目录")
                return
            
            # 检查私钥路径
            key_path = self.batch_key_path_edit.text()
            if not key_path:
                QMessageBox.warning(self, "警告", "请选择私钥文件")
                return
            
            # 加载私钥
            result_key = self.key_service.load_private_key({"file_path": key_path, "password": None})
            if not result_key.get("success"):
                raise Exception(result_key.get("error", "加载私钥失败"))
            private_key = result_key["data"]
            
            # 获取哈希算法
            hash_algorithm = self.batch_hash_combo.currentText()
            
            # 执行批量签名
            result_batch = self.file_signer_service.batch_sign({
                "file_paths": self.batch_files,
                "private_key": private_key,
                "output_dir": output_dir,
                "hash_algorithm": hash_algorithm
            })
            
            if not result_batch.get("success"):
                raise Exception(result_batch.get("error", "批量签名失败"))
            
            results = result_batch["data"]
            
            # 显示批量签名结果
            result_text = "批量签名结果:\n"
            success_count = 0
            fail_count = 0
            
            for result in results:
                if result["success"]:
                    result_text += f"✓ {result['file']} → {result['signature_file']}\n"
                    success_count += 1
                else:
                    result_text += f"✗ {result['file']} → {result['reason']}\n"
                    fail_count += 1
            
            result_text += f"\n总计: {success_count} 成功, {fail_count} 失败"
            self.batch_result_text.setText(result_text)
            
            QMessageBox.information(self, "批量签名完成", f"批量签名完成: {success_count} 成功, {fail_count} 失败")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"批量签名失败: {str(e)}")
