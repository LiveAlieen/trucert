# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

"""验证工具模块

提供证书验证、签名验证等相关的工具函数
"""

from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from typing import Dict, Any, Optional, List


def parse_certificate(cert_data: bytes) -> Dict[str, Any]:
    """解析证书数据
    
    Args:
        cert_data: PEM格式的证书数据
    
    Returns:
        证书信息字典
    """
    backend = default_backend()
    cert = load_pem_x509_certificate(cert_data, backend)
    
    info = {
        "subject": {},
        "issuer": {},
        "serial_number": str(cert.serial_number),
        "not_valid_before": cert.not_valid_before.isoformat(),
        "not_valid_after": cert.not_valid_after.isoformat(),
        "version": cert.version.value + 1,  # X.509版本从0开始，转换为从1开始
    }
    
    # 解析主题信息
    for attr in cert.subject:
        oid = attr.oid
        value = attr.value
        if oid == NameOID.COUNTRY_NAME:
            info["subject"]["country"] = value
        elif oid == NameOID.STATE_OR_PROVINCE_NAME:
            info["subject"]["state"] = value
        elif oid == NameOID.LOCALITY_NAME:
            info["subject"]["locality"] = value
        elif oid == NameOID.ORGANIZATION_NAME:
            info["subject"]["organization"] = value
        elif oid == NameOID.ORGANIZATIONAL_UNIT_NAME:
            info["subject"]["organizational_unit"] = value
        elif oid == NameOID.COMMON_NAME:
            info["subject"]["common_name"] = value
        elif oid == NameOID.EMAIL_ADDRESS:
            info["subject"]["email"] = value
    
    # 解析颁发者信息
    for attr in cert.issuer:
        oid = attr.oid
        value = attr.value
        if oid == NameOID.COUNTRY_NAME:
            info["issuer"]["country"] = value
        elif oid == NameOID.STATE_OR_PROVINCE_NAME:
            info["issuer"]["state"] = value
        elif oid == NameOID.LOCALITY_NAME:
            info["issuer"]["locality"] = value
        elif oid == NameOID.ORGANIZATION_NAME:
            info["issuer"]["organization"] = value
        elif oid == NameOID.ORGANIZATIONAL_UNIT_NAME:
            info["issuer"]["organizational_unit"] = value
        elif oid == NameOID.COMMON_NAME:
            info["issuer"]["common_name"] = value
        elif oid == NameOID.EMAIL_ADDRESS:
            info["issuer"]["email"] = value
    
    return info


def load_certificate(cert_path: str) -> Any:
    """从文件加载证书
    
    Args:
        cert_path: 证书文件路径
    
    Returns:
        证书对象
    """
    backend = default_backend()
    
    with open(cert_path, "rb") as f:
        cert_data = f.read()
    
    return load_pem_x509_certificate(cert_data, backend)


def get_certificate_info(cert_path: str) -> Dict[str, Any]:
    """获取证书信息
    
    Args:
        cert_path: 证书文件路径
    
    Returns:
        证书信息字典
    """
    with open(cert_path, "rb") as f:
        cert_data = f.read()
    
    return parse_certificate(cert_data)


def verify_certificate_chain(cert: Any, trusted_certs: List[Any]) -> bool:
    """验证证书链
    
    Args:
        cert: 要验证的证书对象
        trusted_certs: 受信任的根证书列表
    
    Returns:
        证书链是否有效
    """
    from cryptography.x509 import Certificate
    from cryptography.x509.verification import PolicyBuilder
    from cryptography.hazmat.primitives import hashes
    
    try:
        # 创建验证策略
        policy = PolicyBuilder().build()
        
        # 验证证书链
        # 注意：这里简化了验证过程，实际应用中可能需要更复杂的验证逻辑
        for trusted_cert in trusted_certs:
            try:
                # 尝试使用当前根证书验证
                policy.verify(cert, [trusted_cert])
                return True
            except Exception:
                continue
        
        return False
    except Exception:
        return False


def is_certificate_expired(cert: Any) -> bool:
    """检查证书是否过期
    
    Args:
        cert: 证书对象
    
    Returns:
        证书是否过期
    """
    from datetime import datetime
    
    now = datetime.utcnow()
    return now < cert.not_valid_before or now > cert.not_valid_after


def get_certificate_subject(cert: Any) -> Dict[str, str]:
    """获取证书主题信息
    
    Args:
        cert: 证书对象
    
    Returns:
        主题信息字典
    """
    subject = {}
    
    for attr in cert.subject:
        oid = attr.oid
        value = attr.value
        if oid == NameOID.COUNTRY_NAME:
            subject["country"] = value
        elif oid == NameOID.STATE_OR_PROVINCE_NAME:
            subject["state"] = value
        elif oid == NameOID.LOCALITY_NAME:
            subject["locality"] = value
        elif oid == NameOID.ORGANIZATION_NAME:
            subject["organization"] = value
        elif oid == NameOID.ORGANIZATIONAL_UNIT_NAME:
            subject["organizational_unit"] = value
        elif oid == NameOID.COMMON_NAME:
            subject["common_name"] = value
        elif oid == NameOID.EMAIL_ADDRESS:
            subject["email"] = value
    
    return subject


def get_certificate_issuer(cert: Any) -> Dict[str, str]:
    """获取证书颁发者信息
    
    Args:
        cert: 证书对象
    
    Returns:
        颁发者信息字典
    """
    issuer = {}
    
    for attr in cert.issuer:
        oid = attr.oid
        value = attr.value
        if oid == NameOID.COUNTRY_NAME:
            issuer["country"] = value
        elif oid == NameOID.STATE_OR_PROVINCE_NAME:
            issuer["state"] = value
        elif oid == NameOID.LOCALITY_NAME:
            issuer["locality"] = value
        elif oid == NameOID.ORGANIZATION_NAME:
            issuer["organization"] = value
        elif oid == NameOID.ORGANIZATIONAL_UNIT_NAME:
            issuer["organizational_unit"] = value
        elif oid == NameOID.COMMON_NAME:
            issuer["common_name"] = value
        elif oid == NameOID.EMAIL_ADDRESS:
            issuer["email"] = value
    
    return issuer


def extract_public_key_from_certificate(cert: Any) -> Any:
    """从证书中提取公钥
    
    Args:
        cert: 证书对象
    
    Returns:
        公钥对象
    """
    return cert.public_key()


def save_certificate(cert: Any, filepath: str) -> None:
    """保存证书到文件
    
    Args:
        cert: 证书对象
        filepath: 文件路径
    """
    from .file_utils import write_binary_file
    
    cert_data = cert.public_bytes(encoding=serialization.Encoding.PEM)
    write_binary_file(filepath, cert_data)