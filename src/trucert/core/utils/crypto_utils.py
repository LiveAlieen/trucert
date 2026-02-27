"""加密工具模块

提供加密和签名相关的工具函数，使用模块化算法系统
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.backends import default_backend
from typing import Union, Optional
from ..algorithms import get_algorithm
from .root_key_manager import encrypt_with_root_key, decrypt_with_root_key
import json


def generate_rsa_key(key_size: int = 2048) -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """生成RSA密钥对
    
    Args:
        key_size: 密钥大小，默认为2048位
    
    Returns:
        (私钥对象, 公钥对象)
    """
    rsa_algorithm = get_algorithm('encryption', 'RSA')
    rsa_instance = rsa_algorithm()
    return rsa_instance.generate_key(key_size=key_size)


def generate_ecc_key(curve: str = "SECP256R1") -> tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
    """生成ECC密钥对
    
    Args:
        curve: 椭圆曲线名称，默认为"SECP256R1"
    
    Returns:
        (私钥对象, 公钥对象)
    """
    ecc_algorithm = get_algorithm('encryption', 'ECC')
    ecc_instance = ecc_algorithm()
    return ecc_instance.generate_key(curve=curve)


def sign_data(private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey], 
             data: bytes, algorithm: str = "sha256") -> bytes:
    """使用私钥签名数据
    
    Args:
        private_key: 私钥对象
        data: 要签名的数据
        algorithm: 哈希算法，默认为"sha256"
    
    Returns:
        签名数据
    """
    if isinstance(private_key, rsa.RSAPrivateKey):
        sign_algorithm = get_algorithm('signature', 'RSA-SIGN')
    elif isinstance(private_key, ec.EllipticCurvePrivateKey):
        sign_algorithm = get_algorithm('signature', 'ECC-SIGN')
    else:
        raise TypeError("Unsupported private key type")
    
    sign_instance = sign_algorithm()
    return sign_instance.sign(private_key, data, algorithm=algorithm)


def verify_signature(public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey], 
                    signature: bytes, data: bytes, algorithm: str = "sha256") -> bool:
    """使用公钥验证签名
    
    Args:
        public_key: 公钥对象
        signature: 签名数据
        data: 原始数据
        algorithm: 哈希算法，默认为"sha256"
    
    Returns:
        签名是否有效
    """
    if isinstance(public_key, rsa.RSAPublicKey):
        sign_algorithm = get_algorithm('signature', 'RSA-SIGN')
    elif isinstance(public_key, ec.EllipticCurvePublicKey):
        sign_algorithm = get_algorithm('signature', 'ECC-SIGN')
    else:
        raise TypeError("Unsupported public key type")
    
    sign_instance = sign_algorithm()
    return sign_instance.verify(public_key, signature, data, algorithm=algorithm)


def save_private_key(private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey], 
                    filepath: str, password: Optional[str] = None) -> None:
    """保存私钥到文件
    
    Args:
        private_key: 私钥对象
        filepath: 文件路径
        password: 密码，可选（忽略，使用根密钥加密）
    """
    # 使用无加密方式获取PEM格式私钥
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # 使用根密钥加密私钥
    encrypted_data = encrypt_with_root_key(pem)
    
    # 保存加密后的私钥
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(encrypted_data, f, indent=2, ensure_ascii=False)


def save_public_key(public_key: Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey], 
                   filepath: str) -> None:
    """保存公钥到文件
    
    Args:
        public_key: 公钥对象
        filepath: 文件路径
    """
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    with open(filepath, "wb") as f:
        f.write(pem)


def load_private_key(filepath: str, password: Optional[str] = None) -> Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey]:
    """从文件加载私钥
    
    Args:
        filepath: 文件路径
        password: 密码，可选（忽略，使用根密钥解密）
    
    Returns:
        私钥对象
    """
    backend = default_backend()
    
    # 读取加密的私钥文件
    with open(filepath, "r", encoding="utf-8") as f:
        encrypted_data = json.load(f)
    
    # 使用根密钥解密私钥
    pem = decrypt_with_root_key(encrypted_data)
    
    # 加载私钥
    return serialization.load_pem_private_key(
        pem,
        password=None,
        backend=backend
    )


def load_public_key(filepath: str) -> Union[rsa.RSAPublicKey, ec.EllipticCurvePublicKey]:
    """从文件加载公钥
    
    Args:
        filepath: 文件路径
    
    Returns:
        公钥对象
    """
    backend = default_backend()
    
    with open(filepath, "rb") as f:
        key_data = f.read()
    
    return serialization.load_pem_public_key(
        key_data,
        backend=backend
    )


def get_key_info(key: Union[rsa.RSAPrivateKey, rsa.RSAPublicKey, 
                         ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]) -> dict:
    """获取密钥信息
    
    Args:
        key: 密钥对象
    
    Returns:
        密钥信息字典
    """
    info = {}
    
    if isinstance(key, rsa.RSAPrivateKey):
        info["type"] = "RSA Private Key"
        info["key_size"] = key.key_size
    elif isinstance(key, rsa.RSAPublicKey):
        info["type"] = "RSA Public Key"
        info["key_size"] = key.key_size
    elif isinstance(key, ec.EllipticCurvePrivateKey):
        info["type"] = "ECC Private Key"
        info["curve"] = key.curve.name
    elif isinstance(key, ec.EllipticCurvePublicKey):
        info["type"] = "ECC Public Key"
        info["curve"] = key.curve.name
    
    return info
