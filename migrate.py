# migrate.py - Migration Script for Existing Kuikma Installations
"""
Migration script to upgrade existing Kuikma Chess Engine installations to v2.0
with enhanced user management, verification, and subscription systems.

This script:
1. Backs up existing database
2. Migrates database schema
3. Migrates existing users to new system
4. Sets up default subscriptions
5. Validates migration success
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import json

def print_banner():
    """Print migration banner."""
    print("=" * 60)
    print("🚀 KUIKMA CHESS ENGINE MIGRATION TO v2.0")
    print("=" * 60)
    print("Upgrading to enhanced user management system...")
    print()

def check_prerequisites():
    """Check if migration prerequisites are met."""
    print("📋 Checking prerequisites...")
    
    # Check if old database exists
    old_db_path = "data/kuikma_chess.db"
    if not Path(old_db_path).exists():
        print("❌ No existing database found. This appears to be a fresh installation.")
        print("   Please run 'python setup.py' instead.")
        return False
    
    print(f"   ✅ Found existing database: {old_db_path}")
    
    # Check if backup directory exists
    backup_dir = Path("data/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ Backup directory ready: {backup_dir}")
    
    # Check for .env file
    env_path = Path(".env")
    if not env_path.exists():
        print("   ⚠️  No .env file found. Creating default configuration...")
        create_default_env()
    else:
        print("   ✅ Configuration file exists")
    
    return True

def create_default_env():
    """Create default .env file for migration."""
    env_content = """# Kuikma Chess Engine v2.0 Configuration

# Admin Configuration (UPDATE THESE!)
ADMIN_EMAIL=admin@kuikma.com
ADMIN_PASSWORD=passpass
ADMIN_NAME=System Administrator

# Migration Settings
AUTO_APPROVE_USERS=true
ENABLE_USER_REGISTRATION=true
ENABLE_SUBSCRIPTION_LIMITS=true

# Default User Limits
DEFAULT_POSITION_LIMIT=1000
DEFAULT_ANALYSIS_LIMIT=500
DEFAULT_GAME_UPLOAD_LIMIT=100

# Security Settings
SESSION_TIMEOUT=86400
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=300
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("   ✅ Created default .env file")
    print("   💡 Please review and update the admin credentials in .env file")

def backup_database():
    """Create backup of existing database."""
    print("💾 Creating database backup...")
    
    source_db = "data/kuikma_chess.db"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"kuikma_chess_backup_{timestamp}.db"
    backup_path = f"data/backups/{backup_name}"
    
    try:
        shutil.copy2(source_db, backup_path)
        print(f"   ✅ Database backed up to: {backup_path}")
        return backup_path
    
    except Exception as e:
        print(f"   ❌ Backup failed: {e}")
        return None

def analyze_existing_schema():
    """Analyze existing database schema."""
    print("🔍 Analyzing existing database schema...")
    
    conn = sqlite3.connect("data/kuikma_chess.db")
    cursor = conn.cursor()
    
    try:
        # Get list of existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   📊 Found {len(tables)} existing tables: {', '.join(tables)}")
        
        # Check users table structure
        if 'users' in tables:
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"   👥 Users table has {len(columns)} columns: {', '.join(columns)}")
            
            # Count existing users
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"   📈 Found {user_count} existing users")
            
            # Count admin users
            if 'is_admin' in columns:
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
                admin_count = cursor.fetchone()[0]
                print(f"   👑 Found {admin_count} admin users")
            else:
                print("   ⚠️  No admin column found - will need to create admin user")
        
        return {
            'tables': tables,
            'user_count': user_count if 'users' in tables else 0,
            'has_admin_column': 'is_admin' in columns if 'users' in tables else False
        }
    
    except Exception as e:
        print(f"   ❌ Schema analysis failed: {e}")
        return None
    
    finally:
        conn.close()

def migrate_database_schema():
    """Migrate database schema to v2.0."""
    print("🔄 Migrating database schema...")
    
    try:
        # Import enhanced database functions
        from database import create_enhanced_tables, upgrade_existing_database
        
        # Create new tables
        if create_enhanced_tables():
            print("   ✅ Enhanced tables created")
        else:
            print("   ❌ Failed to create enhanced tables")
            return False
        
        # Upgrade existing schema
        if upgrade_existing_database():
            print("   ✅ Existing schema upgraded")
        else:
            print("   ❌ Failed to upgrade existing schema")
            return False
        
        return True
    
    except Exception as e:
        print(f"   ❌ Schema migration failed: {e}")
        return False

def migrate_existing_users():
    """Migrate existing users to new system."""
    print("👥 Migrating existing users...")
    
    conn = sqlite3.connect("data/kuikma_chess.db")
    cursor = conn.cursor()
    
    try:
        # Get all existing users
        cursor.execute("SELECT id, email, created_at, is_admin FROM users")
        users = cursor.fetchall()
        
        migrated_count = 0
        
        for user_id, email, created_at, is_admin in users:
            try:
                # Update user with new fields if they don't exist
                cursor.execute('''
                    UPDATE users 
                    SET is_verified = ?, 
                        verification_status = ?,
                        verified_at = ?,
                        account_status = ?
                    WHERE id = ?
                ''', (
                    True,  # Auto-verify existing users
                    'approved',
                    datetime.now().isoformat(),
                    'active',
                    user_id
                ))
                
                # Create subscription for user if it doesn't exist
                cursor.execute("SELECT id FROM user_subscriptions WHERE user_id = ?", (user_id,))
                if not cursor.fetchone():
                    # Create default subscription
                    subscription_type = 'admin' if is_admin else 'legacy'
                    position_limit = 999999 if is_admin else 1000
                    analysis_limit = 999999 if is_admin else 500
                    game_limit = 999999 if is_admin else 100
                    
                    cursor.execute('''
                        INSERT INTO user_subscriptions (
                            user_id, subscription_type, position_limit, 
                            analysis_limit, game_upload_limit, updated_by
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, subscription_type, position_limit, analysis_limit, game_limit, user_id))
                
                migrated_count += 1
                print(f"   ✅ Migrated user: {email} ({'Admin' if is_admin else 'User'})")
            
            except Exception as e:
                print(f"   ❌ Failed to migrate user {email}: {e}")
        
        conn.commit()
        print(f"   🎉 Successfully migrated {migrated_count} users")
        return True
    
    except Exception as e:
        print(f"   ❌ User migration failed: {e}")
        return False
    
    finally:
        conn.close()

def setup_admin_user():
    """Setup admin user from configuration."""
    print("👑 Setting up admin user...")
    
    try:
        from auth import ensure_admin_user
        from config import config
        
        ensure_admin_user()
        print(f"   ✅ Admin user configured: {config.ADMIN_EMAIL}")
        return True
    
    except Exception as e:
        print(f"   ❌ Admin setup failed: {e}")
        return False

def validate_migration():
    """Validate migration success."""
    print("✅ Validating migration...")
    
    conn = sqlite3.connect("data/kuikma_chess.db")
    cursor = conn.cursor()
    
    try:
        validation_results = {}
        
        # Check new tables exist
        new_tables = [
            'user_verification_requests',
            'user_subscriptions', 
            'user_feature_access',
            'admin_audit_log',
            'user_sessions'
        ]
        
        for table in new_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            validation_results[f'{table}_exists'] = True
            print(f"   ✅ {table}: {count} records")
        
        # Check users have subscriptions
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_subscriptions")
        subscription_count = cursor.fetchone()[0]
        
        if subscription_count >= user_count:
            print(f"   ✅ All users have subscriptions ({subscription_count}/{user_count})")
            validation_results['subscriptions_complete'] = True
        else:
            print(f"   ⚠️  Some users missing subscriptions ({subscription_count}/{user_count})")
            validation_results['subscriptions_complete'] = False
        
        # Check admin user exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        admin_count = cursor.fetchone()[0]
        
        if admin_count > 0:
            print(f"   ✅ Admin users configured: {admin_count}")
            validation_results['admin_exists'] = True
        else:
            print(f"   ❌ No admin users found")
            validation_results['admin_exists'] = False
        
        return validation_results
    
    except Exception as e:
        print(f"   ❌ Validation failed: {e}")
        return None
    
    finally:
        conn.close()

def create_migration_report(backup_path, validation_results):
    """Create migration report."""
    print("📄 Creating migration report...")
    
    report = {
        'migration_date': datetime.now().isoformat(),
        'backup_file': backup_path,
        'validation_results': validation_results,
        'kuikma_version': '2.0.0',
        'migration_script_version': '1.0.0'
    }
    
    report_path = f"data/backups/migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   ✅ Migration report saved: {report_path}")
        return report_path
    
    except Exception as e:
        print(f"   ❌ Report creation failed: {e}")
        return None

def display_migration_summary(backup_path, validation_results, report_path):
    """Display migration summary."""
    print("\n" + "=" * 60)
    print("🎉 MIGRATION COMPLETED!")
    print("=" * 60)
    
    print(f"\n📊 Migration Summary:")
    print(f"   Backup Created: {backup_path}")
    print(f"   Report Saved: {report_path}")
    
    if validation_results:
        print(f"\n✅ Validation Results:")
        for check, result in validation_results.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}: {'Pass' if result else 'Fail'}")
    
    print(f"\n🚀 Next Steps:")
    print("1. Review the .env file and update admin credentials")
    print("2. Start the application: streamlit run app.py")
    print("3. Login with admin credentials to access new features")
    print("4. Review user verification settings in Admin Panel")
    print("5. Configure subscription limits as needed")
    
    print(f"\n💡 New Features Available:")
    print("• User verification system")
    print("• Subscription/usage limits")
    print("• Feature access control")
    print("• Enhanced admin panel")
    print("• User dashboard")
    print("• Audit logging")
    
    print(f"\n📖 For help, see the README.md file")

def rollback_migration(backup_path):
    """Rollback migration if something goes wrong."""
    print("🔄 Rolling back migration...")
    
    if backup_path and Path(backup_path).exists():
        try:
            shutil.copy2(backup_path, "data/kuikma_chess.db")
            print(f"   ✅ Database restored from: {backup_path}")
            return True
        except Exception as e:
            print(f"   ❌ Rollback failed: {e}")
            return False
    else:
        print("   ❌ No backup available for rollback")
        return False

def main():
    """Main migration function."""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Analyze existing database
    schema_info = analyze_existing_schema()
    if not schema_info:
        print("❌ Could not analyze existing database")
        sys.exit(1)
    
    # Create backup
    backup_path = backup_database()
    if not backup_path:
        print("❌ Migration aborted - backup failed")
        sys.exit(1)
    
    print("\n⚠️  MIGRATION WILL MODIFY YOUR DATABASE")
    print("   A backup has been created, but please confirm you want to proceed.")
    
    if input("\nProceed with migration? (y/N): ").lower() != 'y':
        print("❌ Migration cancelled by user")
        sys.exit(0)
    
    migration_steps = [
        ("Migrating database schema", migrate_database_schema),
        ("Migrating existing users", migrate_existing_users),
        ("Setting up admin user", setup_admin_user),
    ]
    
    failed_steps = []
    
    print("\n🔄 Starting migration process...")
    
    for step_name, step_func in migration_steps:
        print(f"\n{step_name}...")
        try:
            if not step_func():
                failed_steps.append(step_name)
                break
        except Exception as e:
            print(f"   ❌ {step_name} failed: {e}")
            failed_steps.append(step_name)
            break
    
    if failed_steps:
        print(f"\n❌ Migration failed at: {failed_steps[-1]}")
        print("🔄 Attempting rollback...")
        
        if rollback_migration(backup_path):
            print("✅ Database restored to pre-migration state")
        else:
            print("❌ Rollback failed - please restore manually from backup")
        
        sys.exit(1)
    
    # Validate migration
    validation_results = validate_migration()
    
    # Create report
    report_path = create_migration_report(backup_path, validation_results)
    
    # Display summary
    display_migration_summary(backup_path, validation_results, report_path)

if __name__ == "__main__":
    main()
