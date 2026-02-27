# TruCert

## 项目简介

TruCert是一个用于管理加密密钥和数字证书的综合工具，旨在简化证书的创建、存储、管理和验证过程。该系统支持多种加密算法，提供完整的证书生命周期管理功能，适用于需要安全通信和数据完整性验证的场景。

## 核心功能

- **密钥管理**：支持RSA和ECC密钥对的生成、存储、加载和管理
- **证书管理**：支持自签名证书和二级证书的生成、存储、加载和管理
- **文件签名**：支持使用私钥对文件进行签名
- **文件验证**：支持使用公钥或证书验证文件签名的有效性
- **配置管理**：提供灵活的配置存储和管理功能

## 技术栈

- **编程语言**：Python 3.8+
- **加密库**：cryptography
- **测试框架**：pytest
- **文档格式**：Markdown

## 目录结构

```
├── src/                # 源代码目录
│   └── trucert/        # TruCert核心代码
│       ├── core/       # 核心模块
│       ├── configs/    # 配置和存储目录
│       └── root_key/   # 根密钥存储目录
├── docs/               # 文档目录
├── tests/              # 测试目录
├── README.md           # 项目说明文件
└── requirements.txt    # 依赖库文件
```

## 文档导航

### 1. 项目概述

[项目概述](docs/overview/README.md) 提供了系统的整体介绍，包括项目简介、核心功能、系统架构、技术栈、目录结构、系统特点、应用场景、后续发展方向和项目状态等内容。

### 2. 功能说明

[功能说明](docs/features/README.md) 详细介绍了系统的各个功能模块，包括：

- **密钥管理**：密钥对生成、密钥存储、密钥加载、密钥管理
- **证书管理**：自签名证书生成、二级证书生成、证书存储、证书加载、证书管理
- **文件签名**：文件签名功能、签名文件格式
- **文件验证**：签名验证功能、验证结果
- **配置管理**：配置存储、配置类型、配置管理
- **存储管理**：存储接口、存储目录、存储安全性
- **日志管理**：日志功能、日志级别
- **错误处理**：错误处理机制、常见错误类型
- **功能集成**：功能模块集成使用
- **性能优化**：系统性能优化措施
- **可扩展性**：系统可扩展性设计

### 3. 使用指南

[使用指南](docs/guide/README.md) 提供了系统的详细使用说明，包括：

- **环境准备**：系统要求、安装步骤
- **快速入门**：基本概念、示例流程
- **密钥管理使用指南**：生成密钥对、加载密钥对、列出密钥、删除密钥
- **证书管理使用指南**：生成自签名证书、生成二级证书、列出证书、导入证书
- **文件签名与验证指南**：签名文件、验证文件
- **配置管理指南**：获取配置、更新配置
- **高级使用**：自定义存储目录、使用密码保护私钥、批量操作
- **故障排除**：常见错误、日志查看、调试技巧
- **最佳实践**：安全建议、性能建议、维护建议

### 4. API文档

[API文档](docs/api/README.md) 提供了系统的完整API接口说明，包括：

- **服务层API**：KeyService、CertService、FileSignerService、VerifierService、ConfigService
- **存储层API**：StorageManager、KeyStorage、CertStorage、ConfigStorage
- **业务逻辑层API**：KeyManager、CertManager、FileSigner、Verifier、Config
- **工具函数API**：get_logger

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

1. **生成密钥对**
   ```python
   from trucert.core.services.key_service import KeyService
   key_service = KeyService()
   key_pair = key_service.generate_key_pair(key_type="RSA", key_size=2048)
   ```

2. **生成自签名证书**
   ```python
   from trucert.core.services.cert_service import CertService
   cert_service = CertService()
   cert_info = {
       "subject": {
           "common_name": "Example Organization",
           "country_name": "CN"
       },
       "expiry_days": 365
   }
   key_id = key_pair['private_key'].split('\\')[-2]
   cert_path = cert_service.generate_self_signed_cert(key_id, cert_info)
   ```

3. **签名文件**
   ```python
   from trucert.core.services.file_signer_service import FileSignerService
   file_signer_service = FileSignerService()
   signature_path = file_signer_service.sign_file("path/to/file.txt", key_id)
   ```

4. **验证文件**
   ```python
   from trucert.core.services.verifier_service import VerifierService
   verifier_service = VerifierService()
   result = verifier_service.verify_file("path/to/file.txt", signature_path, cert_path=cert_path)
   print(f"验证结果: {'成功' if result else '失败'}")
   ```

## 测试

运行测试套件：

```bash
pytest tests/
```

## 贡献

欢迎贡献代码、提出问题和建议！

## 许可证

本项目采用 MIT 许可证。

## 联系方式

如有任何问题，请联系项目维护者。

---

*项目文档自动生成于 2026-02-13*