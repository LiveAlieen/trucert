import unittest
import os
import shutil
from cert_manager.core.storage.storage_manager import StorageManager

class TestCleanup(unittest.TestCase):
    """清理测试套件，用于清理测试过程中生成的密钥和证书文件"""
    
    def setUp(self):
        """设置测试环境"""
        self.storage_manager = StorageManager()
        self.key_dir = self.storage_manager.get_key_dir()
        self.trust_dir = self.storage_manager.get_trust_dir()
        self.root_key_dir = self.storage_manager.get_root_key_dir()
        
    def test_cleanup_keys(self):
        """清理所有密钥文件"""
        if os.path.exists(self.key_dir):
            try:
                # 遍历密钥目录，删除所有密钥文件夹
                for key_folder in os.listdir(self.key_dir):
                    folder_path = os.path.join(self.key_dir, key_folder)
                    if os.path.isdir(folder_path):
                        shutil.rmtree(folder_path)
                        print(f"已删除密钥文件夹: {folder_path}")
                print("所有密钥文件清理完成")
            except Exception as e:
                print(f"清理密钥文件时出错: {str(e)}")
                raise
    
    def test_cleanup_certs(self):
        """清理所有证书文件"""
        if os.path.exists(self.trust_dir):
            try:
                # 遍历证书目录，删除所有证书文件
                for cert_file in os.listdir(self.trust_dir):
                    file_path = os.path.join(self.trust_dir, cert_file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"已删除证书文件: {file_path}")
                print("所有证书文件清理完成")
            except Exception as e:
                print(f"清理证书文件时出错: {str(e)}")
                raise
    
    def test_cleanup_root_keys(self):
        """根密钥文件不清理"""
        print("根密钥文件保持不变，不进行清理")
    
    def test_cleanup_all(self):
        """清理所有测试数据（除根密钥外）"""
        self.test_cleanup_keys()
        self.test_cleanup_certs()
        print("\n测试数据清理完成！")
        print("注意：根密钥文件保持不变")

if __name__ == "__main__":
    unittest.main()