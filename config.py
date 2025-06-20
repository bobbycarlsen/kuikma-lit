# config.py - Kuikma Chess Engine Configuration
"""
Configuration settings for Kuikma Chess Engine
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    """Configuration class that reads from .env file and provides defaults"""
    
    def __init__(self):
        self.load_env_file()
        self._feature_permissions = self._init_feature_permissions()
    
    def load_env_file(self):
        """Load environment variables from .env file"""
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with type conversion"""
        value = os.environ.get(key, default)
        
        # Handle boolean conversion
        if isinstance(value, str):
            if value.lower() in ('true', 'yes', '1'):
                return True
            elif value.lower() in ('false', 'no', '0'):
                return False
            # Handle integer conversion
            elif value.isdigit():
                return int(value)
        
        return value
    
    def _init_feature_permissions(self) -> Dict[str, Dict[str, bool]]:
        """Initialize feature permissions matrix"""
        return {
            'guest': {
                'view_public_content': True,
                'register': True,
                'login': True,
            },
            'unverified_user': {
                'view_profile': True,
                'change_password': True,
                'logout': True,
                'request_verification': True,
            },
            'verified_user': {
                'training': True,
                'analysis': True,
                'insights': True,
                'game_analysis': True,
                'spatial_analysis': True,
                'upload_games': True,
                'save_positions': True,
                'export_data': True,
                'view_history': True,
                'user_dashboard': True
            },
            'admin': {
                'user_management': True,
                'database_viewer': True,
                'admin_panel': True,
                'system_maintenance': True,
                'feature_management': True,
                'subscription_management': True,
                'backup_restore': True,
                'system_settings': True,
                'user_dashboard': True
            }
        }
    
    def get_user_permissions(self, user_type: str) -> Dict[str, bool]:
        """Get permissions for a user type"""
        permissions = {}
        
        # Build cumulative permissions
        if user_type in ['verified_user', 'admin']:
            permissions.update(self._feature_permissions.get('guest', {}))
            permissions.update(self._feature_permissions.get('unverified_user', {}))
            permissions.update(self._feature_permissions.get('verified_user', {}))
        elif user_type == 'unverified_user':
            permissions.update(self._feature_permissions.get('guest', {}))
            permissions.update(self._feature_permissions.get('unverified_user', {}))
        elif user_type == 'guest':
            permissions.update(self._feature_permissions.get('guest', {}))
        
        # Add admin permissions if admin
        if user_type == 'admin':
            permissions.update(self._feature_permissions.get('admin', {}))
        
        return permissions
    
    # Application Settings
    @property
    def APP_NAME(self) -> str:
        return self.get('APP_NAME', 'Kuikma Chess Engine')
    
    @property
    def APP_VERSION(self) -> str:
        return self.get('APP_VERSION', '2.0.0')
    
    @property
    def DEBUG_MODE(self) -> bool:
        return self.get('DEBUG_MODE', False)
    
    # Database Configuration
    @property
    def DATABASE_PATH(self) -> str:
        return self.get('DATABASE_PATH', 'data/kuikma_chess.db')
    
    @property
    def BACKUP_PATH(self) -> str:
        return self.get('BACKUP_PATH', 'data/backups/')
    
    # Admin Configuration
    @property
    def ADMIN_EMAIL(self) -> str:
        return self.get('ADMIN_EMAIL', 'admin@kuikma.com')
    
    @property
    def ADMIN_PASSWORD(self) -> str:
        return self.get('ADMIN_PASSWORD', 'passpass')
    
    @property
    def ADMIN_NAME(self) -> str:
        return self.get('ADMIN_NAME', 'System Administrator')
    
    # Security Configuration
    @property
    def SESSION_TIMEOUT(self) -> int:
        return self.get('SESSION_TIMEOUT', 86400)
    
    @property
    def PASSWORD_HASH_ALGORITHM(self) -> str:
        return self.get('PASSWORD_HASH_ALGORITHM', 'sha256')
    
    @property
    def MAX_LOGIN_ATTEMPTS(self) -> int:
        return self.get('MAX_LOGIN_ATTEMPTS', 5)
    
    @property
    def LOCKOUT_DURATION(self) -> int:
        return self.get('LOCKOUT_DURATION', 300)
    
    # Feature Flags
    @property
    def REQUIRE_EMAIL_VERIFICATION(self) -> bool:
        return self.get('REQUIRE_EMAIL_VERIFICATION', False)
    
    @property
    def AUTO_APPROVE_USERS(self) -> bool:
        return self.get('AUTO_APPROVE_USERS', False)
    
    @property
    def ENABLE_USER_REGISTRATION(self) -> bool:
        return self.get('ENABLE_USER_REGISTRATION', True)
    
    @property
    def ENABLE_SUBSCRIPTION_LIMITS(self) -> bool:
        return self.get('ENABLE_SUBSCRIPTION_LIMITS', True)
    
    # Default User Limits
    @property
    def DEFAULT_POSITION_LIMIT(self) -> int:
        return self.get('DEFAULT_POSITION_LIMIT', 100)
    
    @property
    def DEFAULT_ANALYSIS_LIMIT(self) -> int:
        return self.get('DEFAULT_ANALYSIS_LIMIT', 50)
    
    @property
    def DEFAULT_GAME_UPLOAD_LIMIT(self) -> int:
        return self.get('DEFAULT_GAME_UPLOAD_LIMIT', 20)
    
    # Training Configuration
    @property
    def TRAINING_CONFIG(self) -> Dict[str, Any]:
        return {
            'max_time_per_position': 300,
            'auto_advance_delay': 2,
            'session_timeout': 3600,
            'max_positions_per_session': 50
        }
    
    # Import/Export Configuration
    @property
    def IMPORT_CONFIG(self) -> Dict[str, Any]:
        return {
            'max_file_size_mb': 300,
            'batch_size': 10000,
            'jsonl_validation_sample_size': 10,
            'pgn_validation_sample_size': 50
        }

# Global configuration instance
config = Config()

# Backward compatibility - maintaining existing interface
APP_NAME = config.APP_NAME
APP_VERSION = config.APP_VERSION
DATABASE_PATH = config.DATABASE_PATH
BACKUP_PATH = config.BACKUP_PATH

ADMIN_CONFIG = {
    'default_admin_email': config.ADMIN_EMAIL,
    'default_admin_password': config.ADMIN_PASSWORD,
    'default_admin_name': config.ADMIN_NAME,
    'auto_create_admin': True,
}

TRAINING_CONFIG = config.TRAINING_CONFIG
IMPORT_CONFIG = config.IMPORT_CONFIG

# Feature access configuration
FEATURE_PERMISSIONS = config._feature_permissions

# User verification settings
USER_VERIFICATION_CONFIG = {
    'require_email_verification': config.REQUIRE_EMAIL_VERIFICATION,
    'auto_approve_users': config.AUTO_APPROVE_USERS,
    'enable_user_registration': config.ENABLE_USER_REGISTRATION,
}

# Subscription limits configuration
SUBSCRIPTION_CONFIG = {
    'enable_limits': config.ENABLE_SUBSCRIPTION_LIMITS,
    'default_position_limit': config.DEFAULT_POSITION_LIMIT,
    'default_analysis_limit': config.DEFAULT_ANALYSIS_LIMIT,
    'default_game_upload_limit': config.DEFAULT_GAME_UPLOAD_LIMIT,
}
