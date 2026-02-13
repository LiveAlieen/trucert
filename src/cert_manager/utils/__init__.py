"""工具模块

提供各种工具函数，包括哈希、加密、文件操作和验证等
"""

# 导出哈希工具
from .hash_utils import (
    calculate_hash,
    calculate_file_hash,
    verify_hash,
    verify_file_hash
)

# 导出加密工具
from .crypto_utils import (
    generate_rsa_key,
    generate_ecc_key,
    sign_data,
    verify_signature,
    save_private_key,
    save_public_key,
    load_private_key,
    load_public_key,
    get_key_info
)

# 导出文件工具
from .file_utils import (
    read_file,
    write_file,
    read_binary_file,
    write_binary_file,
    read_json_file,
    write_json_file,
    get_file_extension,
    get_file_name,
    get_directory_path,
    ensure_directory,
    list_files,
    file_exists,
    directory_exists,
    delete_file,
    copy_file,
    move_file
)

# 导出验证工具
from .verify_utils import (
    parse_certificate,
    load_certificate,
    get_certificate_info,
    verify_certificate_chain,
    is_certificate_expired,
    get_certificate_subject,
    get_certificate_issuer,
    extract_public_key_from_certificate,
    save_certificate
)

__all__ = [
    # 哈希工具
    "calculate_hash",
    "calculate_file_hash",
    "verify_hash",
    "verify_file_hash",
    # 加密工具
    "generate_rsa_key",
    "generate_ecc_key",
    "sign_data",
    "verify_signature",
    "save_private_key",
    "save_public_key",
    "load_private_key",
    "load_public_key",
    "get_key_info",
    # 文件工具
    "read_file",
    "write_file",
    "read_binary_file",
    "write_binary_file",
    "read_json_file",
    "write_json_file",
    "get_file_extension",
    "get_file_name",
    "get_directory_path",
    "ensure_directory",
    "list_files",
    "file_exists",
    "directory_exists",
    "delete_file",
    "copy_file",
    "move_file",
    # 验证工具
    "parse_certificate",
    "load_certificate",
    "get_certificate_info",
    "verify_certificate_chain",
    "is_certificate_expired",
    "get_certificate_subject",
    "get_certificate_issuer",
    "extract_public_key_from_certificate",
    "save_certificate"
]
