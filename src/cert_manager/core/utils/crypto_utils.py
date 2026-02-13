"""加密工具模块

提供加密和签名相关的工具函数
"""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.backends import default_backend
from typing import Union, Optional


def generate_rsa_key(key_size: int = 2048) -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """生成RSA密钥对
    
    Args:
        key_size: 密钥大小，默认为2048位
    
    Returns:
        (私钥对象, 公钥对象)
    """
    backend = default_backend()
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=backend
    )
    public_key = private_key.public_key()
    return private_key, public_key


def generate_ecc_key(curve: str = "SECP256R1") -> tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
    """生成ECC密钥对
    
    Args:
        curve: 椭圆曲线名称，默认为"SECP256R1"
    
    Returns:
        (私钥对象, 公钥对象)
    """
    backend = default_backend()
    curve_upper = curve.upper()
    curve_obj = getattr(ec, curve_upper)()
    private_key = ec.generate_private_key(
        curve=curve_obj,
        backend=backend
    )
    public_key = private_key.public_key()
    return private_key, public_key


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
    hash_obj = getattr(hashes, algorithm.upper())()
    
    if isinstance(private_key, rsa.RSAPrivateKey):
        return private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hash_obj),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hash_obj
        )
    elif isinstance(private_key, ec.EllipticCurvePrivateKey):
        return private_key.sign(
            data,
            ec.ECDSA(hash_obj)
        )
    else:
        raise TypeError("Unsupported private key type")


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
    hash_obj = getattr(hashes, algorithm.upper())()
    
    try:
        if isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hash_obj),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hash_obj
            )
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(
                signature,
                data,
                ec.ECDSA(hash_obj)
            )
        else:
            raise TypeError("Unsupported public key type")
        return True
    except Exception:
        return False


def save_private_key(private_key: Union[rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey], 
                    filepath: str, password: Optional[str] = None) -> None:
    """保存私钥到文件
    
    Args:
        private_key: 私钥对象
        filepath: 文件路径
        password: 密码，可选
    """
    if password:
        encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
    else:
        encryption_algorithm = serialization.NoEncryption()
    
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )
    
    with open(filepath, "wb") as f:
        f.write(pem)


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
        password: 密码，可选
    
    Returns:
        私钥对象
    """
    backend = default_backend()
    
    with open(filepath, "rb") as f:
        key_data = f.read()
    
    if password:
        password_bytes = password.encode()
    else:
        password_bytes = None
    
    return serialization.load_pem_private_key(
        key_data,
        password=password_bytes,
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
