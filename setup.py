# setup.py - Kuikma Chess Engine Setup Script
"""
Setup script for Kuikma Chess Engine
Run this script to initialize the application and database.

Enhanced setup script for Kuikma Chess Engine with user verification and subscription management.
This script handles:
- Environment configuration
- Database creation and migration
- Admin user setup from .env
- Initial data setup
- System validation
"""

import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path
import subprocess



def initialize_database():
    """Initialize the database with tables and admin user."""
    print("🗄️ Initializing database...")
    
    try:
        import database
        
        # Initialize database tables
        database.init_db()
        print("✅ Database tables created")
        
        # Create admin user
        database.create_admin_user()
        print("✅ Admin user created")
        
        # Optimize database
        database.optimize_database()
        print("✅ Database optimized")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False


def setup_logging():
    """Setup logging configuration."""
    print("📋 Setting up logging...")
    
    try:
        import logging
        from datetime import datetime
        
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/kuikma.log'),
                logging.StreamHandler()
            ]
        )
        
        # Test logging
        logger = logging.getLogger('kuikma_setup')
        logger.info("Logging system initialized")
        
        print("✅ Logging configured")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up logging: {e}")
        return False

def run_tests():
    """Run basic system tests."""
    print("🧪 Running system tests...")
    
    try:
        # Test database connection
        import database
        conn = database.get_db_connection()
        conn.close()
        print("✅ Database connection test passed")
        
        # Test authentication
        import auth
        auth.ensure_admin_user()
        print("✅ Authentication test passed")
        
        # Test JSONL processor
        from jsonl_processor import JSONLProcessor
        processor = JSONLProcessor()
        print("✅ JSONL processor test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False


def create_env_file_if_missing():
    """Create .env file with default values if it doesn't exist."""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("📄 Creating default .env file...")
        
        default_env = """# Kuikma Chess Engine Configuration

# Admin Configuration
ADMIN_EMAIL=admin@kuikma.com
ADMIN_PASSWORD=passpass
ADMIN_NAME=System Administrator

# Database Configuration
DATABASE_PATH=data/kuikma_chess.db
BACKUP_PATH=data/backups/

# Security Settings
SESSION_TIMEOUT=86400
PASSWORD_HASH_ALGORITHM=sha256
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=300

# Feature Flags
REQUIRE_EMAIL_VERIFICATION=false
AUTO_APPROVE_USERS=false
ENABLE_USER_REGISTRATION=true
ENABLE_SUBSCRIPTION_LIMITS=true

# Default User Limits
DEFAULT_POSITION_LIMIT=100
DEFAULT_ANALYSIS_LIMIT=50
DEFAULT_GAME_UPLOAD_LIMIT=20

# Application Settings
APP_NAME=Kuikma Chess Engine
APP_VERSION=2.0.0
DEBUG_MODE=false
"""
        
        with open(env_path, 'w') as f:
            f.write(default_env)
        
        print("✅ .env file created with default values")
        print("💡 You can customize these settings in the .env file")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create required directories."""
    print("📁 Creating directories...")
    
    directories = [
        'data',
        'data/backups',
        'logs',
        'kuikma_analysis'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")
    
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'streamlit',
        'pandas',
        'sqlite3'  # Built-in with Python
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def initialize_enhanced_database():
    """Initialize database with enhanced schema."""
    print("🗄️ Initializing enhanced database...")
    
    try:
        # Import and initialize enhanced database
        from database import create_enhanced_tables, upgrade_existing_database
        
        # Create enhanced tables
        if create_enhanced_tables():
            print("   ✅ Enhanced tables created")
        else:
            print("   ❌ Failed to create enhanced tables")
            return False
        
        # Upgrade existing database
        if upgrade_existing_database():
            print("   ✅ Database upgraded successfully")
        else:
            print("   ❌ Failed to upgrade database")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}")
        return False

def setup_admin_user():
    """Setup admin user from .env configuration."""
    print("👑 Setting up admin user...")
    
    try:
        from auth import ensure_admin_user
        from config import config
        
        ensure_admin_user()
        print(f"   ✅ Admin user configured: {config.ADMIN_EMAIL}")
        print(f"   🔑 Password: {config.ADMIN_PASSWORD}")
        print("   💡 You can change these credentials in the .env file")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Admin user setup failed: {e}")
        return False

def create_sample_data():
    """Create sample data for testing (optional)."""
    print("📋 Creating sample data...")
    
    try:
        from database import get_db_connection
        from auth import register_user
        
        # Create a sample regular user if auto-approve is enabled
        from config import config
        
        if config.AUTO_APPROVE_USERS:
            result = register_user(
                "test@example.com", 
                "testpass", 
                "Test User"
            )
            
            if result.get('success'):
                print("   ✅ Sample user created: test@example.com / testpass")
            else:
                print("   ℹ️  Sample user already exists or creation skipped")
        else:
            print("   ℹ️  Sample user creation skipped (manual approval required)")
        
        return True
    except Exception as e:
        print(f"   ⚠️  Sample data creation failed: {e}")
        return True  # Non-critical


    print("📝 Creating sample data...")
    
    try:
        from jsonl_processor import JSONLProcessor
        import json
        
        # Create sample JSONL data
        sample_positions = [
            {
                "id": 1,
                "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "turn": "white",
                "fullmove_number": 1,
                "game_phase": "opening",
                "difficulty_rating": 800,
                "themes": ["opening", "development"],
                "title": "Starting Position",
                "description": "The initial position of a chess game",
                "position_type": "opening",
                "top_moves": [
                    {
                        "move": "e4",
                        "score": 25,
                        "classification": "excellent",
                        "centipawn_loss": 0,
                        "rank": 1,
                        "pv": "e4 e5 Nf3"
                    },
                    {
                        "move": "d4",
                        "score": 20,
                        "classification": "good", 
                        "centipawn_loss": 5,
                        "rank": 2,
                        "pv": "d4 d5 c4"
                    }
                ]
            }
        ]
        
        # Save sample data
        sample_file = "sample_positions.jsonl"
        with open(sample_file, 'w') as f:
            for position in sample_positions:
                f.write(json.dumps(position) + '\n')
        
        print(f"✅ Sample data created: {sample_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def validate_system():
    """Validate system functionality."""
    print("🧪 Validating system...")
    
    try:
        # Test database connection
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test user table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   ✅ Users table: {user_count} users")
        
        # Test admin user
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
        admin_count = cursor.fetchone()[0]
        print(f"   ✅ Admin users: {admin_count}")
        
        # Test subscriptions table
        cursor.execute("SELECT COUNT(*) FROM user_subscriptions")
        sub_count = cursor.fetchone()[0]
        print(f"   ✅ Subscriptions: {sub_count}")
        
        conn.close()
        
        # Test authentication module
        from auth import hash_password
        test_hash = hash_password("test")
        print("   ✅ Authentication module working")
        
        # Test config module
        from config import config
        print(f"   ✅ Configuration loaded: {config.APP_NAME} v{config.APP_VERSION}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ System validation failed: {e}")
        return False

def display_setup_summary():
    """Display setup summary and next steps."""
    print("\n" + "=" * 60)
    print("🎉 KUIKMA CHESS ENGINE SETUP COMPLETED!")
    print("=" * 60)
    
    from config import config
    
    print(f"\n📊 Configuration Summary:")
    print(f"   App Name: {config.APP_NAME}")
    print(f"   Version: {config.APP_VERSION}")
    print(f"   Admin Email: {config.ADMIN_EMAIL}")
    print(f"   Database: {config.DATABASE_PATH}")
    print(f"   Auto-approve Users: {config.AUTO_APPROVE_USERS}")
    print(f"   Registration Enabled: {config.ENABLE_USER_REGISTRATION}")
    
    print(f"\n🚀 Next Steps:")
    print("1. Run the application:")
    print("   streamlit run app.py")
    print("\n2. Open your browser to:")
    print("   http://localhost:8501")
    print("\n3. Login as admin:")
    print(f"   Email: {config.ADMIN_EMAIL}")
    print(f"   Password: {config.ADMIN_PASSWORD}")
    print("\n4. Configure user verification settings in Admin Panel")
    print("\n5. Import your chess data via Settings")
    
    print(f"\n💡 Tips:")
    print("- Customize settings in the .env file")
    print("- Use Admin Panel to manage user verification")
    print("- Set subscription limits per user as needed")
    print("- Enable/disable features through Feature Access Control")
    
    print(f"\n📖 For help, see the README.md file")

def main():
    """Main setup function."""
    print("🚀 KUIKMA CHESS ENGINE ENHANCED SETUP")
    print("=" * 50)
    print("Setting up user verification and subscription management...")
    print()
    
    # Setup steps
    steps = [
        ("Creating .env configuration", create_env_file_if_missing),
        ("Creating directories", create_directories),
        ("Checking dependencies", install_dependencies),
        ("Initializing enhanced database", initialize_enhanced_database),
        ("Setting up admin user", setup_admin_user),
        ("Creating sample data", create_sample_data),
        ("Validating system", validate_system)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        try:
            if not step_func():
                failed_steps.append(step_name)
                print(f"❌ {step_name} failed")
        except Exception as e:
            failed_steps.append(step_name)
            print(f"❌ {step_name} failed: {e}")
    
    if failed_steps:
        print(f"\n❌ Setup completed with errors:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease review the errors above and run setup again if needed.")
        sys.exit(1)
    else:
        display_setup_summary()

if __name__ == "__main__":
    main()
