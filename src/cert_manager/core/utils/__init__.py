"""工具模块

提供加密、文件操作、哈希计算、验证和日志等工具函数
"""

from .crypto_utils import (
    generate_rsa_key,
    generate_ecc_key,
    load_private_key,
    load_public_key,
    save_private_key,
    save_public_key,
    get_key_info,
    sign_data,
    verify_signature
)

from .file_utils import (
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
    move_file
)

from .hash_utils import (
    calculate_hash,
    calculate_file_hash,
    verify_hash,
    verify_file_hash
)

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

from .log_utils import (
    setup_logger,
    get_logger,
    default_logger
)

__all__ = [
    # crypto_utils
    "generate_rsa_key",
    "generate_ecc_key",
    "load_private_key",
    "load_public_key",
    "save_private_key",
    "save_public_key",
    "get_key_info",
    "sign_data",
    "verify_signature",
    # file_utils
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
    # hash_utils
    "calculate_hash",
    "calculate_file_hash",
    "verify_hash",
    "verify_file_hash",
    # verify_utils
    "parse_certificate",
    "load_certificate",
    "get_certificate_info",
    "verify_certificate_chain",
    "is_certificate_expired",
    "get_certificate_subject",
    "get_certificate_issuer",
    "extract_public_key_from_certificate",
    "save_certificate",
    # log_utils
    "setup_logger",
    "get_logger",
    "default_logger"
]