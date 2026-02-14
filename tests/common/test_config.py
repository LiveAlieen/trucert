"""测试配置模块

测试配置管理的功能
"""

import unittest
import os
from src.cert_manager.core.config import ConfigManager
from tests.utils.test_utils import create_temp_directory, cleanup_temp_path


class TestConfigManager(unittest.TestCase):
    """测试配置管理"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建配置管理器实例
        self.config_manager = ConfigManager()
    
    def tearDown(self):
        """清理测试环境"""
        pass
    
    def test_get_algorithms(self):
        """测试获取算法配置"""
        algorithms = self.config_manager.get_algorithms()
        self.assertIsInstance(algorithms, dict)
        self.assertIn("hash_algorithms", algorithms)
        self.assertIn("rsa_key_sizes", algorithms)
        self.assertIn("ecc_curves", algorithms)


if __name__ == "__main__":
    unittest.main()
