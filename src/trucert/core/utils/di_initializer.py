"""依赖注入初始化模块

用于注册和初始化所有核心模块的依赖项
"""

from .di import register, register_factory, di_container


class DIInitializer:
    """依赖注入初始化器"""
    
    @staticmethod
    def initialize():
        """初始化所有依赖项"""
        # 注册存储层依赖项
        DIInitializer._register_storage_dependencies()
        
        # 注册业务层依赖项
        DIInitializer._register_business_dependencies()
        
        # 注册服务层依赖项
        DIInitializer._register_service_dependencies()
    
    @staticmethod
    def _register_storage_dependencies():
        """注册存储层依赖项"""
        from ..storage import StorageManager, KeyStorage, CertStorage, ConfigStorage
        
        # 注册StorageManager为单例
        storage_manager = StorageManager()
        register("storage_manager", storage_manager)
        
        # 注册其他存储组件
        register_factory("key_storage", lambda: KeyStorage(di_container.get("storage_manager")))
        register_factory("cert_storage", lambda: CertStorage(di_container.get("storage_manager")))
        register_factory("config_storage", lambda: ConfigStorage())
    
    @staticmethod
    def _register_business_dependencies():
        """注册业务层依赖项"""
        from ..business import KeyManager, CertManager, FileSigner, Verifier, ConfigManager
        
        # 注册业务层组件
        register_factory("key_manager", KeyManager)
        register_factory("cert_manager", CertManager)
        register_factory("file_signer", FileSigner)
        register_factory("verifier", Verifier)
        register_factory("config_manager", ConfigManager)
    
    @staticmethod
    def _register_service_dependencies():
        """注册服务层依赖项"""
        from ..services import KeyService, CertService, FileSignerService, VerifierService, ConfigService
        
        # 注册服务层组件
        register_factory("key_service", KeyService)
        register_factory("cert_service", CertService)
        register_factory("file_signer_service", FileSignerService)
        register_factory("verifier_service", VerifierService)
        register_factory("config_service", ConfigService)


# 导出初始化函数
def initialize_dependencies():
    """初始化所有依赖项"""
    DIInitializer.initialize()


__all__ = ["DIInitializer", "initialize_dependencies"]