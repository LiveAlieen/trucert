# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from ..utils import get

class CertService:
    """证书服务类，封装证书管理功能，作为GUI和核心业务逻辑之间的桥梁
    
    提供标准化的接口调用，负责从业务层调用和封装证书管理功能，
    统一GUI和CLI的接口规范，确保接口的一致性和可维护性。
    """
    
    def __init__(self):
        """初始化证书服务
        
        使用依赖注入获取证书管理组件，确保与业务层的解耦。
        """
        # 使用依赖注入获取业务层组件
        self.cert_manager = get("cert_manager")
    
    def generate_self_signed_cert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成自签名证书
        
        Args:
            params: 包含以下字段的字典：
                - public_key: 公钥
                - private_key: 私钥
                - validity_days: 有效期（天），默认365
                - forward_offset: 时间偏移量（秒），默认0
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，证书数据
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            public_key = params.get('public_key')
            private_key = params.get('private_key')
            validity_days = params.get('validity_days', 365)
            forward_offset = params.get('forward_offset', 0)
            
            # 验证参数
            if not public_key or not private_key:
                return {
                    "success": False,
                    "error": "缺少必要的公钥或私钥参数"
                }
            
            if validity_days <= 0:
                return {
                    "success": False,
                    "error": "有效期必须为正数"
                }
            
            # 调用业务逻辑层
            cert_data = self.cert_manager.generate_self_signed_cert(
                public_key=public_key,
                private_key=private_key,
                validity_days=validity_days,
                forward_offset=forward_offset
            )
            
            return {
                "success": True,
                "data": cert_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_secondary_cert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成二级证书
        
        Args:
            params: 包含以下字段的字典：
                - public_key: 公钥
                - parent_private_key: 父证书私钥
                - parent_public_key: 父证书公钥
                - validity_days: 有效期（天），默认365
                - forward_offset: 时间偏移量（秒），默认0
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，证书数据
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            public_key = params.get('public_key')
            parent_private_key = params.get('parent_private_key')
            parent_public_key = params.get('parent_public_key')
            validity_days = params.get('validity_days', 365)
            forward_offset = params.get('forward_offset', 0)
            
            # 验证参数
            if not public_key or not parent_private_key or not parent_public_key:
                return {
                    "success": False,
                    "error": "缺少必要的公钥、父证书私钥或父证书公钥参数"
                }
            
            if validity_days <= 0:
                return {
                    "success": False,
                    "error": "有效期必须为正数"
                }
            
            # 调用业务逻辑层
            cert_data = self.cert_manager.generate_secondary_cert(
                public_key=public_key,
                parent_private_key=parent_private_key,
                parent_public_key=parent_public_key,
                validity_days=validity_days,
                forward_offset=forward_offset
            )
            
            return {
                "success": True,
                "data": cert_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_cert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成证书（统一接口）
        
        Args:
            params: 包含以下字段的字典：
                - cert_type: 证书类型，"self_signed"或"secondary"
                - public_key: 公钥
                - private_key: 私钥（仅自签名证书）
                - parent_private_key: 父证书私钥（仅二级证书）
                - parent_public_key: 父证书公钥（仅二级证书）
                - validity_days: 有效期（天），默认365
                - forward_offset: 时间偏移量（秒），默认0
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，证书数据
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            cert_type = params.get('cert_type')
            public_key = params.get('public_key')
            private_key = params.get('private_key')
            parent_private_key = params.get('parent_private_key')
            parent_public_key = params.get('parent_public_key')
            validity_days = params.get('validity_days', 365)
            forward_offset = params.get('forward_offset', 0)
            
            # 验证参数
            if not cert_type or cert_type not in ['self_signed', 'secondary']:
                return {
                    "success": False,
                    "error": "证书类型必须是'self_signed'或'secondary'"
                }
            
            if not public_key:
                return {
                    "success": False,
                    "error": "缺少必要的公钥参数"
                }
            
            if validity_days <= 0:
                return {
                    "success": False,
                    "error": "有效期必须为正数"
                }
            
            if cert_type == 'self_signed':
                if not private_key:
                    return {
                        "success": False,
                        "error": "自签名证书需要私钥参数"
                    }
                # 调用业务逻辑层生成自签名证书
                cert_data = self.cert_manager.generate_self_signed_cert(
                    public_key=public_key,
                    private_key=private_key,
                    validity_days=validity_days,
                    forward_offset=forward_offset
                )
            else:  # secondary
                if not parent_private_key or not parent_public_key:
                    return {
                        "success": False,
                        "error": "二级证书需要父证书私钥和公钥参数"
                    }
                # 调用业务逻辑层生成二级证书
                cert_data = self.cert_manager.generate_secondary_cert(
                    public_key=public_key,
                    parent_private_key=parent_private_key,
                    parent_public_key=parent_public_key,
                    validity_days=validity_days,
                    forward_offset=forward_offset
                )
            
            return {
                "success": True,
                "data": cert_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_cert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """保存证书
        
        Args:
            params: 包含以下字段的字典：
                - cert_data: 证书数据
                - filepath: 文件路径，默认None
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: str，保存的文件路径
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            cert_data = params.get('cert_data')
            filepath = params.get('filepath', None)
            
            # 验证参数
            if not cert_data:
                return {
                    "success": False,
                    "error": "缺少必要的证书数据参数"
                }
            
            # 调用业务逻辑层
            saved_path = self.cert_manager.save_cert(cert_data, filepath)
            
            return {
                "success": True,
                "data": saved_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_cert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """加载证书
        
        Args:
            params: 包含以下字段的字典：
                - filepath: 文件路径
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，证书数据
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            filepath = params.get('filepath')
            
            # 验证参数
            if not filepath:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径参数"
                }
            
            # 调用业务逻辑层
            cert_data = self.cert_manager.load_cert(filepath)
            
            return {
                "success": True,
                "data": cert_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_certs(self) -> Dict[str, Any]:
        """列出所有存储的证书
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: List[str]，证书文件路径列表
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 调用业务逻辑层
            certs = self.cert_manager.list_certs()
            
            return {
                "success": True,
                "data": certs
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_cert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """删除证书
        
        Args:
            params: 包含以下字段的字典：
                - filepath: 文件路径
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: bool，是否删除成功
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            filepath = params.get('filepath')
            
            # 验证参数
            if not filepath:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径参数"
                }
            
            # 调用业务逻辑层
            success = self.cert_manager.delete_cert(filepath)
            
            return {
                "success": True,
                "data": success
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def import_cert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """导入证书
        
        Args:
            params: 包含以下字段的字典：
                - filepath: 文件路径
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，导入的证书数据
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            filepath = params.get('filepath')
            
            # 验证参数
            if not filepath:
                return {
                    "success": False,
                    "error": "缺少必要的文件路径参数"
                }
            
            # 调用业务逻辑层
            cert_data = self.cert_manager.import_cert(filepath)
            
            return {
                "success": True,
                "data": cert_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_cert_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取证书信息
        
        Args:
            params: 包含以下字段的字典：
                - cert_data: 证书数据
        
        Returns:
            Dict[str, Any]: 包含以下字段的字典：
                - success: bool，操作是否成功
                - data: Dict[str, Any]，证书信息
                - error: str，错误信息（如果操作失败）
        """
        try:
            # 提取参数
            cert_data = params.get('cert_data')
            
            # 验证参数
            if not cert_data:
                return {
                    "success": False,
                    "error": "缺少必要的证书数据参数"
                }
            
            # 调用业务逻辑层
            cert_info = self.cert_manager.get_cert_info(cert_data)
            
            return {
                "success": True,
                "data": cert_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
