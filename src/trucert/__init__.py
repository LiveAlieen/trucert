# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

# 证书管理工具包

from .core import (
    # Business
    CertManager,
    FileSigner,
    KeyManager,
    Verifier,
    ConfigManager,
    
    # Services
    KeyService,
    CertService,
    FileSignerService,
    VerifierService,
    ConfigService,
    
    # Storage
    KeyStorage,
    CertStorage,
    ConfigStorage,
    StorageManager,
    
    # Utils (crypto_utils)
    generate_rsa_key,
    generate_ecc_key,
    load_private_key,
    load_public_key,
    save_private_key,
    save_public_key,
    get_key_info,
    sign_data,
    verify_signature,
    
    # Utils (file_utils)
    read_binary_file,
    write_binary_file,
    read_file,
    write_file,
    read_json_file,
    write_json_file,
    ensure_directory,
    get_file_extension,
    get_file_name,
    get_directory_path,
    list_files,
    file_exists,
    directory_exists,
    delete_file,
    copy_file,
    move_file,
    
    # Utils (hash_utils)
    calculate_hash,
    calculate_file_hash,
    verify_hash,
    verify_file_hash,
    
    # Utils (verify_utils)
    parse_certificate,
    load_certificate,
    get_certificate_info,
    verify_certificate_chain,
    is_certificate_expired,
    get_certificate_subject,
    get_certificate_issuer,
    extract_public_key_from_certificate,
    save_certificate,
    
    # Utils (log_utils)
    setup_logger,
    get_logger,
    default_logger,
    set_log_level,
    set_console_level,
    set_file_level,
    log_manager,
    
    # Utils (error_utils)
    TruCertError,
    KeyError,
    CertError,
    FileError,
    StorageError,
    ValidationError,
    ConfigError,
    handle_error,
    raise_error,
    
    # Utils (di)
    DependencyInjector,
    di_container,
    register,
    register_factory,
    register_singleton,
    get,
    has,
    inject,
    clear,
    
    # Utils (di_initializer)
    DIInitializer,
    initialize_dependencies
)

__all__ = [
    # Business
    "CertManager",
    "FileSigner",
    "KeyManager",
    "Verifier",
    "ConfigManager",
    
    # Services
    "KeyService",
    "CertService",
    "FileSignerService",
    "VerifierService",
    "ConfigService",
    
    # Storage
    "KeyStorage",
    "CertStorage",
    "ConfigStorage",
    "StorageManager",
    
    # Utils (crypto_utils)
    "generate_rsa_key",
    "generate_ecc_key",
    "load_private_key",
    "load_public_key",
    "save_private_key",
    "save_public_key",
    "get_key_info",
    "sign_data",
    "verify_signature",
    
    # Utils (file_utils)
    "read_binary_file",
    "write_binary_file",
    "read_file",
    "write_file",
    "read_json_file",
    "write_json_file",
    "ensure_directory",
    "get_file_extension",
    "get_file_name",
    "get_directory_path",
    "list_files",
    "file_exists",
    "directory_exists",
    "delete_file",
    "copy_file",
    "move_file",
    
    # Utils (hash_utils)
    "calculate_hash",
    "calculate_file_hash",
    "verify_hash",
    "verify_file_hash",
    
    # Utils (verify_utils)
    "parse_certificate",
    "load_certificate",
    "get_certificate_info",
    "verify_certificate_chain",
    "is_certificate_expired",
    "get_certificate_subject",
    "get_certificate_issuer",
    "extract_public_key_from_certificate",
    "save_certificate",
    
    # Utils (log_utils)
    "setup_logger",
    "get_logger",
    "default_logger",
    "set_log_level",
    "set_console_level",
    "set_file_level",
    "log_manager",
    
    # Utils (error_utils)
    "TruCertError",
    "KeyError",
    "CertError",
    "FileError",
    "StorageError",
    "ValidationError",
    "ConfigError",
    "handle_error",
    "raise_error",
    
    # Utils (di)
    "DependencyInjector",
    "di_container",
    "register",
    "register_factory",
    "register_singleton",
    "get",
    "has",
    "inject",
    "clear",
    
    # Utils (di_initializer)
    "DIInitializer",
    "initialize_dependencies"
]
