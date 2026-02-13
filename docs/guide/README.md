# 使用指南

## 1. 环境准备

### 1.1 系统要求

- **操作系统**：Windows、macOS、Linux
- **Python版本**：Python 3.8+
- **依赖库**：cryptography

### 1.2 安装步骤

1. **克隆项目**：
   ```bash
   git clone <项目地址>
   cd <项目目录>
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **验证安装**：
   ```bash
   python -c "import cert_manager; print('Installation successful')"
   ```

## 2. 快速入门

### 2.1 基本概念

- **密钥对**：由私钥和公钥组成，私钥用于签名，公钥用于验证
- **证书**：包含公钥和身份信息的数字文档，由可信方签发
- **自签名证书**：由密钥所有者自己签发的证书
- **二级证书**：由其他证书签发的证书
- **文件签名**：使用私钥对文件进行数字签名，确保文件完整性

### 2.2 示例流程

以下是一个完整的证书管理流程示例：

1. **生成密钥对**
2. **生成自签名证书**
3. **生成二级证书**
4. **使用私钥签名文件**
5. **使用公钥验证文件**

## 3. 密钥管理使用指南

### 3.1 生成密钥对

**使用示例**：

```python
from cert_manager.core.services.key_service import KeyService

# 初始化密钥服务
key_service = KeyService()

# 生成RSA密钥对
rsa_key_pair = key_service.generate_key_pair(
    key_type="RSA",
    key_size=2048
)
print(f"RSA密钥对生成成功，私钥路径: {rsa_key_pair['private_key']}")

# 生成ECC密钥对
ecc_key_pair = key_service.generate_key_pair(
    key_type="ECC",
    curve="secp256r1"
)
print(f"ECC密钥对生成成功，私钥路径: {ecc_key_pair['private_key']}")
```

### 3.2 加载密钥对

**使用示例**：

```python
from cert_manager.core.services.key_service import KeyService

# 初始化密钥服务
key_service = KeyService()

# 加载密钥对
key_id = "RSA_1234567890"  # 替换为实际的密钥ID
private_key, public_key = key_service.load_key_pair(key_id)
print("密钥对加载成功")
```

### 3.3 列出密钥

**使用示例**：

```python
from cert_manager.core.services.key_service import KeyService

# 初始化密钥服务
key_service = KeyService()

# 列出所有密钥
keys = key_service.list_keys()
for key in keys:
    print(f"密钥ID: {key['id']}, 类型: {key['type']}")
```

### 3.4 删除密钥

**使用示例**：

```python
from cert_manager.core.services.key_service import KeyService

# 初始化密钥服务
key_service = KeyService()

# 删除密钥
key_id = "RSA_1234567890"  # 替换为实际的密钥ID
success = key_service.delete_key(key_id)
print(f"密钥删除 {'成功' if success else '失败'}")
```

## 4. 证书管理使用指南

### 4.1 生成自签名证书

**使用示例**：

```python
from cert_manager.core.services.cert_service import CertService
from cert_manager.core.services.key_service import KeyService

# 初始化服务
cert_service = CertService()
key_service = KeyService()

# 生成密钥对
key_pair = key_service.generate_key_pair(key_type="RSA", key_size=2048)
key_id = key_pair['private_key'].split('\\')[-2]  # 提取密钥ID

# 准备证书信息
cert_info = {
    "subject": {
        "common_name": "Example Organization",
        "country_name": "CN",
        "state_or_province_name": "Beijing",
        "locality_name": "Beijing",
        "organization_name": "Example Org",
        "organizational_unit_name": "IT Department"
    },
    "expiry_days": 365
}

# 生成自签名证书
cert_path = cert_service.generate_self_signed_cert(key_id, cert_info)
print(f"自签名证书生成成功，路径: {cert_path}")
```

### 4.2 生成二级证书

**使用示例**：

```python
from cert_manager.core.services.cert_service import CertService
from cert_manager.core.services.key_service import KeyService

# 初始化服务
cert_service = CertService()
key_service = KeyService()

# 生成根密钥对和自签名证书
root_key_pair = key_service.generate_key_pair(key_type="RSA", key_size=2048)
root_key_id = root_key_pair['private_key'].split('\\')[-2]

root_cert_info = {
    "subject": {
        "common_name": "Root CA",
        "country_name": "CN",
        "state_or_province_name": "Beijing",
        "locality_name": "Beijing",
        "organization_name": "Example CA",
        "organizational_unit_name": "Certificate Authority"
    },
    "expiry_days": 3650
}

root_cert_path = cert_service.generate_self_signed_cert(root_key_id, root_cert_info)

# 生成二级密钥对
secondary_key_pair = key_service.generate_key_pair(key_type="RSA", key_size=2048)
secondary_key_id = secondary_key_pair['private_key'].split('\\')[-2]

# 准备二级证书信息
secondary_cert_info = {
    "subject": {
        "common_name": "Server Certificate",
        "country_name": "CN",
        "state_or_province_name": "Beijing",
        "locality_name": "Beijing",
        "organization_name": "Example Server",
        "organizational_unit_name": "Web Server"
    },
    "expiry_days": 365
}

# 生成二级证书
secondary_cert_path = cert_service.generate_secondary_cert(
    secondary_key_id, 
    root_key_id, 
    secondary_cert_info
)
print(f"二级证书生成成功，路径: {secondary_cert_path}")
```

### 4.3 列出证书

**使用示例**：

```python
from cert_manager.core.services.cert_service import CertService

# 初始化证书服务
cert_service = CertService()

# 列出所有证书
certs = cert_service.list_certs()
for cert in certs:
    print(f"证书名称: {cert['filename']}, 类型: {cert['type']}, 是根证书: {cert['is_root_cert']}")
```

### 4.4 导入证书

**使用示例**：

```python
from cert_manager.core.services.cert_service import CertService

# 初始化证书服务
cert_service = CertService()

# 导入证书
external_cert_path = "path/to/external/cert.json"
imported_cert = cert_service.import_cert(external_cert_path)
print("证书导入成功")
```

## 5. 文件签名与验证指南

### 5.1 签名文件

**使用示例**：

```python
from cert_manager.core.services.file_signer_service import FileSignerService
from cert_manager.core.services.key_service import KeyService

# 初始化服务
file_signer_service = FileSignerService()
key_service = KeyService()

# 生成密钥对
key_pair = key_service.generate_key_pair(key_type="RSA", key_size=2048)
key_id = key_pair['private_key'].split('\\')[-2]

# 准备要签名的文件
file_path = "path/to/file.txt"

# 签名文件
signature_path = file_signer_service.sign_file(file_path, key_id)
print(f"文件签名成功，签名文件路径: {signature_path}")
```

### 5.2 验证文件

**使用示例**：

```python
from cert_manager.core.services.verifier_service import VerifierService

# 初始化验证服务
verifier_service = VerifierService()

# 准备文件和签名文件
file_path = "path/to/file.txt"
signature_path = "path/to/signature.txt"

# 使用公钥验证
public_key_path = "path/to/public.pem"
result = verifier_service.verify_file(file_path, signature_path, public_key_path=public_key_path)
print(f"验证结果: {'成功' if result else '失败'}")

# 或使用证书验证
cert_path = "path/to/cert.json"
result = verifier_service.verify_file(file_path, signature_path, cert_path=cert_path)
print(f"验证结果: {'成功' if result else '失败'}")
```

## 6. 配置管理指南

### 6.1 获取配置

**使用示例**：

```python
from cert_manager.core.services.config_service import ConfigService

# 初始化配置服务
config_service = ConfigService()

# 获取算法配置
algorithms = config_service.get_algorithms()
print("支持的哈希算法:", algorithms['hash_algorithms'])
print("支持的RSA密钥大小:", algorithms['rsa_key_sizes'])
print("支持的ECC曲线:", algorithms['ecc_curves'])

# 获取证书版本配置
cert_versions = config_service.get_cert_versions()
print("证书版本配置:", cert_versions)
```

### 6.2 更新配置

**使用示例**：

```python
from cert_manager.core.services.config_service import ConfigService

# 初始化配置服务
config_service = ConfigService()

# 更新算法配置
updates = {
    "hash_algorithms": ["sha256", "sha384", "sha512", "sha1"]
}
updated_config = config_service.update_config("algorithms", updates)
print("更新后的算法配置:", updated_config)
```

## 7. 高级使用

### 7.1 自定义存储目录

**使用示例**：

```python
from cert_manager.core.storage.storage_manager import StorageManager
from cert_manager.core.storage.key_storage import KeyStorage

# 自定义存储目录
custom_base_dir = "path/to/custom/configs"

# 初始化存储管理器
storage_manager = StorageManager(base_dir=custom_base_dir)

# 初始化密钥存储
key_storage = KeyStorage(storage_manager=storage_manager)

# 现在使用key_storage进行操作，数据会存储在自定义目录中
```

### 7.2 使用密码保护私钥

**使用示例**：

```python
from cert_manager.core.storage.key_storage import KeyStorage
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# 初始化密钥存储
key_storage = KeyStorage()

# 生成RSA密钥对
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# 使用密码保存私钥
password = "your_secure_password"
filepath = "path/to/encrypted_private.pem"
key_storage.save_private_key(private_key, filepath, password=password)
print("加密私钥保存成功")

# 使用密码加载私钥
loaded_private_key = key_storage.load_private_key(filepath, password=password)
print("加密私钥加载成功")
```

### 7.3 批量操作

**使用示例**：

```python
from cert_manager.core.services.key_service import KeyService
from cert_manager.core.services.cert_service import CertService

# 初始化服务
key_service = KeyService()
cert_service = CertService()

# 批量生成密钥对和证书
for i in range(5):
    # 生成密钥对
    key_pair = key_service.generate_key_pair(key_type="ECC", curve="secp256r1")
    key_id = key_pair['private_key'].split('\\')[-2]
    
    # 生成自签名证书
    cert_info = {
        "subject": {
            "common_name": f"Test Certificate {i}",
            "country_name": "CN",
            "state_or_province_name": "Beijing"
        },
        "expiry_days": 365
    }
    
    cert_path = cert_service.generate_self_signed_cert(key_id, cert_info)
    print(f"生成证书 {i+1}: {cert_path}")
```

## 8. 故障排除

### 8.1 常见错误

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|--------|
| FileNotFoundError | 文件或目录不存在 | 检查文件路径是否正确，确保目录存在 |
| PermissionError | 权限不足 | 确保有足够的文件系统权限 |
| ValueError | 参数值无效 | 检查参数类型和值是否符合要求 |
| cryptography.exceptions | 加密操作错误 | 检查密钥是否有效，算法是否支持 |

### 8.2 日志查看

系统会生成详细的日志信息，帮助排查问题：

- **日志位置**：系统会在控制台输出日志
- **日志级别**：默认INFO级别，可在代码中调整

### 8.3 调试技巧

1. **启用调试日志**：
   ```python
   from cert_manager.core.utils import get_logger
   logger = get_logger("debug", level="DEBUG")
   ```

2. **检查存储结构**：
   - 确保configs目录结构正确
   - 检查密钥和证书文件是否存在

3. **验证密钥和证书**：
   - 使用openssl命令验证密钥格式：`openssl rsa -in private.pem -text -noout`
   - 检查证书JSON格式是否正确

## 9. 最佳实践

### 9.1 安全建议

- **保护私钥**：私钥文件应严格保密，避免泄露
- **使用强密码**：为私钥设置强密码保护
- **定期更新**：定期更新密钥和证书，避免使用过期证书
- **备份数据**：定期备份密钥和证书数据

### 9.2 性能建议

- **选择合适的密钥大小**：RSA密钥建议使用2048位或3072位
- **合理使用ECC**：对于性能要求高的场景，建议使用ECC密钥
- **批量操作**：对于大量文件的签名和验证，使用批量操作提高效率

### 9.3 维护建议

- **定期清理**：清理不需要的密钥和证书，保持存储整洁
- **监控存储**：监控存储使用情况，避免存储空间不足
- **更新依赖**：定期更新cryptography库，获取安全补丁和性能改进