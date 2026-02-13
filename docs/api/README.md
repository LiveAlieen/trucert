# API文档

## 1. 服务层API

### 1.1 KeyService

**功能**：提供密钥管理相关的服务接口

**导入路径**：`from cert_manager.core.services.key_service import KeyService`

**方法**：

#### 1.1.1 generate_key_pair

**功能**：生成密钥对

**参数**：
- `key_type` (str)：密钥类型，支持 "RSA" 或 "ECC"
- `key_size` (int, optional)：RSA密钥大小，仅当 key_type 为 "RSA" 时使用，默认 2048
- `curve` (str, optional)：ECC曲线名称，仅当 key_type 为 "ECC" 时使用，默认 "secp256r1"

**返回值**：
- `Dict[str, str]`：包含私钥和公钥路径的字典
  ```python
  {
      "private_key": "path/to/private.pem",
      "public_key": "path/to/public.pem"
  }
  ```

**示例**：
```python
key_service = KeyService()
rsa_key_pair = key_service.generate_key_pair(key_type="RSA", key_size=2048)
ecc_key_pair = key_service.generate_key_pair(key_type="ECC", curve="secp256r1")
```

#### 1.1.2 load_key_pair

**功能**：加载密钥对

**参数**：
- `key_id` (str)：密钥ID

**返回值**：
- `Tuple`：包含私钥和公钥对象的元组
  ```python
  (private_key_object, public_key_object)
  ```

**示例**：
```python
private_key, public_key = key_service.load_key_pair("RSA_1234567890")
```

#### 1.1.3 list_keys

**功能**：列出所有存储的密钥

**参数**：无

**返回值**：
- `List[Dict[str, Any]]`：密钥信息列表
  ```python
  [
      {
          "id": "RSA_1234567890",
          "type": "RSA",
          "private_key_path": "path/to/private.pem",
          "public_key_path": "path/to/public.pem",
          "created_at": "2023-01-01T00:00:00"
      },
      # 更多密钥...
  ]
  ```

**示例**：
```python
keys = key_service.list_keys()
```

#### 1.1.4 delete_key

**功能**：删除密钥

**参数**：
- `key_id` (str)：密钥ID

**返回值**：
- `bool`：是否删除成功

**示例**：
```python
success = key_service.delete_key("RSA_1234567890")
```

### 1.2 CertService

**功能**：提供证书管理相关的服务接口

**导入路径**：`from cert_manager.core.services.cert_service import CertService`

**方法**：

#### 1.2.1 generate_self_signed_cert

**功能**：生成自签名证书

**参数**：
- `key_id` (str)：密钥ID
- `cert_info` (Dict[str, Any])：证书信息
  ```python
  {
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
  ```

**返回值**：
- `str`：证书文件路径

**示例**：
```python
cert_path = cert_service.generate_self_signed_cert("RSA_1234567890", cert_info)
```

#### 1.2.2 generate_secondary_cert

**功能**：生成二级证书

**参数**：
- `key_id` (str)：密钥ID
- `issuer_key_id` (str)：签发者密钥ID
- `cert_info` (Dict[str, Any])：证书信息（格式同上）

**返回值**：
- `str`：证书文件路径

**示例**：
```python
cert_path = cert_service.generate_secondary_cert("RSA_1234567890", "RSA_9876543210", cert_info)
```

#### 1.2.3 list_certs

**功能**：列出所有存储的证书

**参数**：无

**返回值**：
- `List[Dict[str, Any]]`：证书信息列表
  ```python
  [
      {
          "filename": "self_signed_1234567890.json",
          "path": "path/to/cert.json",
          "type": "self_signed",
          "is_root_cert": True,
          "cert_info": { ... }
      },
      # 更多证书...
  ]
  ```

**示例**：
```python
certs = cert_service.list_certs()
```

#### 1.2.4 import_cert

**功能**：导入证书

**参数**：
- `filepath` (str)：证书文件路径

**返回值**：
- `Dict[str, Any]`：导入的证书数据

**示例**：
```python
imported_cert = cert_service.import_cert("path/to/external/cert.json")
```

### 1.3 FileSignerService

**功能**：提供文件签名相关的服务接口

**导入路径**：`from cert_manager.core.services.file_signer_service import FileSignerService`

**方法**：

#### 1.3.1 sign_file

**功能**：签名文件

**参数**：
- `file_path` (str)：文件路径
- `key_id` (str)：密钥ID

**返回值**：
- `str`：签名文件路径

**示例**：
```python
signature_path = file_signer_service.sign_file("path/to/file.txt", "RSA_1234567890")
```

### 1.4 VerifierService

**功能**：提供文件验证相关的服务接口

**导入路径**：`from cert_manager.core.services.verifier_service import VerifierService`

**方法**：

#### 1.4.1 verify_file

**功能**：验证文件签名

**参数**：
- `file_path` (str)：文件路径
- `signature_path` (str)：签名文件路径
- `public_key_path` (str, optional)：公钥文件路径
- `cert_path` (str, optional)：证书文件路径

**返回值**：
- `bool`：验证是否成功

**示例**：
```python
# 使用公钥验证
result = verifier_service.verify_file("path/to/file.txt", "path/to/signature.txt", public_key_path="path/to/public.pem")

# 使用证书验证
result = verifier_service.verify_file("path/to/file.txt", "path/to/signature.txt", cert_path="path/to/cert.json")
```

#### 1.4.2 verify_cert_data

**功能**：验证证书数据

**参数**：
- `cert_data` (Dict[str, Any])：证书数据

**返回值**：
- `bool`：验证是否成功

**示例**：
```python
result = verifier_service.verify_cert_data(cert_data)
```

### 1.5 ConfigService

**功能**：提供配置管理相关的服务接口

**导入路径**：`from cert_manager.core.services.config_service import ConfigService`

**方法**：

#### 1.5.1 get_algorithms

**功能**：获取算法配置

**参数**：无

**返回值**：
- `Dict[str, Any]`：算法配置
  ```python
  {
      "hash_algorithms": ["sha256", "sha384", "sha512"],
      "rsa_key_sizes": [2048, 3072, 4096],
      "ecc_curves": ["secp256r1", "secp384r1", "secp521r1"]
  }
  ```

**示例**：
```python
algorithms = config_service.get_algorithms()
```

#### 1.5.2 get_cert_versions

**功能**：获取证书版本配置

**参数**：无

**返回值**：
- `Dict[str, Any]`：证书版本配置
  ```python
  {
      "v1": {
          "version": 0,
          "fields": ["subject", "issuer", "public_key", "serial_number", "not_valid_before", "not_valid_after", "signature_algorithm"]
      },
      "v3": {
          "version": 2,
          "fields": ["subject", "issuer", "public_key", "serial_number", "not_valid_before", "not_valid_after", "signature_algorithm", "extensions"]
      }
  }
  ```

**示例**：
```python
cert_versions = config_service.get_cert_versions()
```

#### 1.5.3 update_config

**功能**：更新配置

**参数**：
- `config_name` (str)：配置名称
- `updates` (Dict[str, Any])：要更新的配置数据

**返回值**：
- `Dict[str, Any]`：更新后的配置数据

**示例**：
```python
updates = {"hash_algorithms": ["sha256", "sha384", "sha512", "sha1"]}
updated_config = config_service.update_config("algorithms", updates)
```

## 2. 存储层API

### 2.1 StorageManager

**功能**：提供统一的存储接口

**导入路径**：`from cert_manager.core.storage.storage_manager import StorageManager`

**方法**：

#### 2.1.1 __init__

**功能**：初始化存储管理器

**参数**：
- `base_dir` (str, optional)：基础目录路径，默认为 None

**示例**：
```python
# 使用默认目录
storage_manager = StorageManager()

# 使用自定义目录
storage_manager = StorageManager(base_dir="path/to/custom/configs")
```

#### 2.1.2 save

**功能**：保存数据到文件

**参数**：
- `data` (Union[Dict[str, Any], bytes])：要保存的数据
- `filepath` (str)：文件路径
- `format` (str, optional)：文件格式，支持 "json" 和 "binary"，默认 "json"

**返回值**：无

**示例**：
```python
# 保存JSON数据
storage_manager.save({"key": "value"}, "path/to/data.json", format="json")

# 保存二进制数据
storage_manager.save(b"binary data", "path/to/data.bin", format="binary")
```

#### 2.1.3 load

**功能**：从文件加载数据

**参数**：
- `filepath` (str)：文件路径
- `format` (str, optional)：文件格式，支持 "json" 和 "binary"，默认 "json"

**返回值**：
- `Union[Dict[str, Any], bytes]`：加载的数据

**示例**：
```python
# 加载JSON数据
data = storage_manager.load("path/to/data.json", format="json")

# 加载二进制数据
data = storage_manager.load("path/to/data.bin", format="binary")
```

#### 2.1.4 delete

**功能**：删除文件

**参数**：
- `filepath` (str)：文件路径

**返回值**：
- `bool`：是否删除成功

**示例**：
```python
success = storage_manager.delete("path/to/file.txt")
```

#### 2.1.5 list_files

**功能**：列出目录中的文件

**参数**：
- `directory` (str)：目录路径
- `pattern` (str, optional)：文件匹配模式，默认 "*"

**返回值**：
- `List[str]`：文件路径列表

**示例**：
```python
files = storage_manager.list_files("path/to/directory", pattern="*.json")
```

#### 2.1.6 get_key_dir

**功能**：获取密钥存储目录

**参数**：无

**返回值**：
- `str`：密钥存储目录路径

**示例**：
```python
key_dir = storage_manager.get_key_dir()
```

#### 2.1.7 get_trust_dir

**功能**：获取证书信任存储目录

**参数**：无

**返回值**：
- `str`：证书信任存储目录路径

**示例**：
```python
trust_dir = storage_manager.get_trust_dir()
```

#### 2.1.8 get_root_key_dir

**功能**：获取根密钥存储目录

**参数**：无

**返回值**：
- `str`：根密钥存储目录路径

**示例**：
```python
root_key_dir = storage_manager.get_root_key_dir()
```

#### 2.1.9 get_file_info

**功能**：获取文件信息

**参数**：
- `filepath` (str)：文件路径

**返回值**：
- `Dict[str, Any]`：文件信息字典
  ```python
  {
      "exists": True,
      "path": "path/to/file.txt",
      "size": 1024,
      "mtime": 1234567890.123,
      "is_dir": False
  }
  ```

**示例**：
```python
file_info = storage_manager.get_file_info("path/to/file.txt")
```

### 2.2 KeyStorage

**功能**：提供密钥存储相关的接口

**导入路径**：`from cert_manager.core.storage.key_storage import KeyStorage`

**方法**：

#### 2.2.1 __init__

**功能**：初始化密钥存储

**参数**：
- `storage_manager` (StorageManager, optional)：存储管理器实例，默认为 None

**示例**：
```python
key_storage = KeyStorage()
```

#### 2.2.2 save_private_key

**功能**：保存私钥

**参数**：
- `private_key`：私钥对象
- `filepath` (str)：文件路径
- `password` (str, optional)：密码，默认为 None

**返回值**：无

**示例**：
```python
key_storage.save_private_key(private_key, "path/to/private.pem", password="password")
```

#### 2.2.3 save_public_key

**功能**：保存公钥

**参数**：
- `public_key`：公钥对象
- `filepath` (str)：文件路径

**返回值**：无

**示例**：
```python
key_storage.save_public_key(public_key, "path/to/public.pem")
```

#### 2.2.4 load_private_key

**功能**：加载私钥

**参数**：
- `filepath` (str)：文件路径
- `password` (str, optional)：密码，默认为 None

**返回值**：
- 私钥对象

**示例**：
```python
private_key = key_storage.load_private_key("path/to/private.pem", password="password")
```

#### 2.2.5 load_public_key

**功能**：加载公钥

**参数**：
- `filepath` (str)：文件路径

**返回值**：
- 公钥对象

**示例**：
```python
public_key = key_storage.load_public_key("path/to/public.pem")
```

#### 2.2.6 save_key_pair

**功能**：保存密钥对

**参数**：
- `private_key`：私钥对象
- `public_key`：公钥对象
- `key_id` (str)：密钥ID
- `key_type` (str)：密钥类型

**返回值**：
- `Dict[str, str]`：保存的文件路径
  ```python
  {
      "private_key": "path/to/private.pem",
      "public_key": "path/to/public.pem"
  }
  ```

**示例**：
```python
paths = key_storage.save_key_pair(private_key, public_key, "RSA_1234567890", "RSA")
```

#### 2.2.7 load_key_pair

**功能**：加载密钥对

**参数**：
- `key_id` (str)：密钥ID

**返回值**：
- `Tuple`：包含私钥和公钥对象的元组

**示例**：
```python
private_key, public_key = key_storage.load_key_pair("RSA_1234567890")
```

#### 2.2.8 list_keys

**功能**：列出所有存储的密钥

**参数**：无

**返回值**：
- `List[Dict[str, Any]]`：密钥信息列表

**示例**：
```python
keys = key_storage.list_keys()
```

#### 2.2.9 delete_key

**功能**：删除密钥

**参数**：
- `key_id` (str)：密钥ID

**返回值**：
- `bool`：是否删除成功

**示例**：
```python
success = key_storage.delete_key("RSA_1234567890")
```

#### 2.2.10 save_root_key_pair

**功能**：保存根密钥对

**参数**：
- `private_key`：根私钥对象
- `public_key`：根公钥对象

**返回值**：
- `Dict[str, str]`：保存的文件路径

**示例**：
```python
paths = key_storage.save_root_key_pair(private_key, public_key)
```

#### 2.2.11 load_root_key_pair

**功能**：加载根密钥对

**参数**：无

**返回值**：
- `Tuple`：包含根私钥和根公钥对象的元组

**示例**：
```python
root_private_key, root_public_key = key_storage.load_root_key_pair()
```

### 2.3 CertStorage

**功能**：提供证书存储相关的接口

**导入路径**：`from cert_manager.core.storage.cert_storage import CertStorage`

**方法**：

#### 2.3.1 __init__

**功能**：初始化证书存储

**参数**：
- `storage_manager` (StorageManager, optional)：存储管理器实例，默认为 None

**示例**：
```python
cert_storage = CertStorage()
```

#### 2.3.2 save_cert

**功能**：保存证书

**参数**：
- `cert_data` (Dict[str, Any])：证书数据
- `filepath` (str, optional)：文件路径，默认为 None

**返回值**：
- `str`：保存的文件路径

**示例**：
```python
cert_path = cert_storage.save_cert(cert_data)
```

#### 2.3.3 load_cert

**功能**：加载证书

**参数**：
- `filepath` (str)：文件路径

**返回值**：
- `Dict[str, Any]`：证书数据

**示例**：
```python
cert_data = cert_storage.load_cert("path/to/cert.json")
```

#### 2.3.4 delete_cert

**功能**：删除证书

**参数**：
- `filepath` (str)：文件路径

**返回值**：
- `bool`：是否删除成功

**示例**：
```python
success = cert_storage.delete_cert("path/to/cert.json")
```

#### 2.3.5 list_certs

**功能**：列出所有存储的证书

**参数**：无

**返回值**：
- `List[Dict[str, Any]]`：证书信息列表

**示例**：
```python
certs = cert_storage.list_certs()
```

#### 2.3.6 get_cert_by_filename

**功能**：根据文件名获取证书

**参数**：
- `filename` (str)：文件名

**返回值**：
- `Dict[str, Any]`：证书数据

**示例**：
```python
cert_data = cert_storage.get_cert_by_filename("self_signed_1234567890.json")
```

#### 2.3.7 import_cert

**功能**：导入证书

**参数**：
- `filepath` (str)：证书文件路径

**返回值**：
- `Dict[str, Any]`：导入的证书数据

**示例**：
```python
imported_cert = cert_storage.import_cert("path/to/external/cert.json")
```

### 2.4 ConfigStorage

**功能**：提供配置存储相关的接口

**导入路径**：`from cert_manager.core.storage.config_storage import ConfigStorage`

**方法**：

#### 2.4.1 __init__

**功能**：初始化配置存储

**参数**：
- `storage_manager` (StorageManager, optional)：存储管理器实例，默认为 None

**示例**：
```python
config_storage = ConfigStorage()
```

#### 2.4.2 save_config

**功能**：保存配置

**参数**：
- `config_name` (str)：配置名称
- `config_data` (Dict[str, Any])：配置数据
- `format` (str, optional)：文件格式，支持 "json"，默认 "json"

**返回值**：无

**示例**：
```python
config_storage.save_config("algorithms", {"hash_algorithms": ["sha256"]})
```

#### 2.4.3 load_config

**功能**：加载配置

**参数**：
- `config_name` (str)：配置名称
- `format` (str, optional)：文件格式，支持 "json"，默认 "json"

**返回值**：
- `Dict[str, Any]`：配置数据

**示例**：
```python
config = config_storage.load_config("algorithms")
```

#### 2.4.4 get_config

**功能**：获取配置，如果不存在则返回默认值

**参数**：
- `config_name` (str)：配置名称
- `default` (Dict[str, Any], optional)：默认配置数据，默认为 None
- `format` (str, optional)：文件格式，支持 "json"，默认 "json"

**返回值**：
- `Dict[str, Any]`：配置数据

**示例**：
```python
default_config = {"hash_algorithms": ["sha256"]}
config = config_storage.get_config("algorithms", default=default_config)
```

#### 2.4.5 update_config

**功能**：更新配置

**参数**：
- `config_name` (str)：配置名称
- `updates` (Dict[str, Any])：要更新的配置数据
- `format` (str, optional)：文件格式，支持 "json"，默认 "json"

**返回值**：
- `Dict[str, Any]`：更新后的配置数据

**示例**：
```python
updates = {"hash_algorithms": ["sha256", "sha384"]}
updated_config = config_storage.update_config("algorithms", updates)
```

#### 2.4.6 delete_config

**功能**：删除配置

**参数**：
- `config_name` (str)：配置名称
- `format` (str, optional)：文件格式，支持 "json"，默认 "json"

**返回值**：
- `bool`：是否删除成功

**示例**：
```python
success = config_storage.delete_config("algorithms")
```

#### 2.4.7 list_configs

**功能**：列出所有配置

**参数**：
- `format` (str, optional)：文件格式，支持 "json"，默认 "json"

**返回值**：
- `List[str]`：配置名称列表

**示例**：
```python
configs = config_storage.list_configs()
```

#### 2.4.8 get_cert_versions

**功能**：获取证书版本配置

**参数**：无

**返回值**：
- `Dict[str, Any]`：证书版本配置

**示例**：
```python
cert_versions = config_storage.get_cert_versions()
```

#### 2.4.9 get_algorithms

**功能**：获取算法配置

**参数**：无

**返回值**：
- `Dict[str, Any]`：算法配置

**示例**：
```python
algorithms = config_storage.get_algorithms()
```

## 3. 业务逻辑层API

### 3.1 KeyManager

**功能**：提供密钥管理相关的业务逻辑

**导入路径**：`from cert_manager.core.business.key_manager import KeyManager`

**方法**：

#### 3.1.1 generate_key_pair

**功能**：生成密钥对

**参数**：
- `key_type` (str)：密钥类型，支持 "RSA" 或 "ECC"
- `key_size` (int, optional)：RSA密钥大小，仅当 key_type 为 "RSA" 时使用
- `curve` (str, optional)：ECC曲线名称，仅当 key_type 为 "ECC" 时使用

**返回值**：
- `Tuple`：包含私钥和公钥对象的元组

**示例**：
```python
key_manager = KeyManager()
private_key, public_key = key_manager.generate_key_pair(key_type="RSA", key_size=2048)
```

### 3.2 CertManager

**功能**：提供证书管理相关的业务逻辑

**导入路径**：`from cert_manager.core.business.cert_manager import CertManager`

**方法**：

#### 3.2.1 generate_self_signed_cert

**功能**：生成自签名证书

**参数**：
- `private_key`：私钥对象
- `public_key`：公钥对象
- `cert_info` (Dict[str, Any])：证书信息

**返回值**：
- `Dict[str, Any]`：证书数据

**示例**：
```python
cert_manager = CertManager()
cert_data = cert_manager.generate_self_signed_cert(private_key, public_key, cert_info)
```

#### 3.2.2 generate_secondary_cert

**功能**：生成二级证书

**参数**：
- `private_key`：私钥对象
- `public_key`：公钥对象
- `issuer_private_key`：签发者私钥对象
- `issuer_public_key`：签发者公钥对象
- `cert_info` (Dict[str, Any])：证书信息

**返回值**：
- `Dict[str, Any]`：证书数据

**示例**：
```python
cert_data = cert_manager.generate_secondary_cert(private_key, public_key, issuer_private_key, issuer_public_key, cert_info)
```

### 3.3 FileSigner

**功能**：提供文件签名相关的业务逻辑

**导入路径**：`from cert_manager.core.business.file_signer import FileSigner`

**方法**：

#### 3.3.1 sign_file

**功能**：签名文件

**参数**：
- `file_path` (str)：文件路径
- `private_key`：私钥对象

**返回值**：
- `Dict[str, Any]`：签名数据

**示例**：
```python
file_signer = FileSigner()
signature_data = file_signer.sign_file("path/to/file.txt", private_key)
```

### 3.4 Verifier

**功能**：提供文件验证相关的业务逻辑

**导入路径**：`from cert_manager.core.business.verifier import Verifier`

**方法**：

#### 3.4.1 verify_file

**功能**：验证文件签名

**参数**：
- `file_path` (str)：文件路径
- `signature_data` (Dict[str, Any])：签名数据
- `public_key`：公钥对象

**返回值**：
- `bool`：验证是否成功

**示例**：
```python
verifier = Verifier()
result = verifier.verify_file("path/to/file.txt", signature_data, public_key)
```

#### 3.4.2 verify_cert_data

**功能**：验证证书数据

**参数**：
- `cert_data` (Dict[str, Any])：证书数据

**返回值**：
- `bool`：验证是否成功

**示例**：
```python
result = verifier.verify_cert_data(cert_data)
```

### 3.5 Config

**功能**：提供配置管理相关的业务逻辑

**导入路径**：`from cert_manager.core.business.config import Config`

**方法**：

#### 3.5.1 get_algorithms

**功能**：获取算法配置

**参数**：无

**返回值**：
- `Dict[str, Any]`：算法配置

**示例**：
```python
config = Config()
algorithms = config.get_algorithms()
```

#### 3.5.2 get_cert_versions

**功能**：获取证书版本配置

**参数**：无

**返回值**：
- `Dict[str, Any]`：证书版本配置

**示例**：
```python
cert_versions = config.get_cert_versions()
```

## 4. 工具函数API

### 4.1 get_logger

**功能**：获取日志记录器

**导入路径**：`from cert_manager.core.utils import get_logger`

**参数**：
- `name` (str)：日志记录器名称
- `level` (str, optional)：日志级别，默认 "INFO"

**返回值**：
- `logging.Logger`：日志记录器对象

**示例**：
```python
logger = get_logger("my_module", level="DEBUG")
logger.info("This is an info message")
```