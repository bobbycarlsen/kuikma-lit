# backup_utilities.py - Supporting utilities for backup and export functionality

import sqlite3
import shutil
import json
import zipfile
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from io import BytesIO, StringIO
from typing import Dict, List, Any, Optional
import streamlit as st

def download_backup(backup_filename: str):
    """Provide download functionality for backup files."""
    try:
        backup_path = Path(f"data/backups/{backup_filename}")
        
        if not backup_path.exists():
            st.error(f"❌ Backup file not found: {backup_filename}")
            return
        
        with open(backup_path, 'rb') as f:
            st.download_button(
                label=f"⬇️ Download {backup_filename}",
                data=f.read(),
                file_name=backup_filename,
                mime="application/octet-stream",
                use_container_width=True
            )
        
        st.success(f"✅ {backup_filename} ready for download!")
        
    except Exception as e:
        st.error(f"❌ Download preparation failed: {e}")

def restore_from_backup(backup_filename: str):
    """Restore database from backup file."""
    try:
        backup_path = Path(f"data/backups/{backup_filename}")
        current_db_path = Path("data/kuikma_chess.db")
        
        if not backup_path.exists():
            st.error(f"❌ Backup file not found: {backup_filename}")
            return
        
        # Create a backup of current database before restore
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_restore_backup = f"data/backups/pre_restore_backup_{timestamp}.db"
        shutil.copy2(current_db_path, pre_restore_backup)
        
        # Restore from backup
        shutil.copy2(backup_path, current_db_path)
        
        st.success(f"✅ Database restored from {backup_filename}")
        st.info(f"💾 Current database backed up to: pre_restore_backup_{timestamp}.db")
        
        # Log the restore action
        log_admin_action(
            st.session_state.get('user_id'),
            'database_restore',
            None,
            'database',
            {'backup_file': backup_filename, 'pre_restore_backup': pre_restore_backup}
        )
        
        st.warning("🔄 Please restart the application to ensure all components use the restored database.")
        
    except Exception as e:
        st.error(f"❌ Restore failed: {e}")

def verify_backup(backup_filename: str):
    """Verify backup file integrity."""
    try:
        backup_path = Path(f"data/backups/{backup_filename}")
        
        if not backup_path.exists():
            st.error(f"❌ Backup file not found: {backup_filename}")
            return
        
        with st.spinner("🔍 Verifying backup integrity..."):
            # Basic SQLite integrity check
            conn = sqlite3.connect(str(backup_path))
            cursor = conn.cursor()
            
            # Check if database can be opened and basic tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Verify critical tables exist
            critical_tables = ['users', 'positions', 'moves']
            missing_tables = []
            
            table_names = [table[0] for table in tables]
            for critical_table in critical_tables:
                if critical_table not in table_names:
                    missing_tables.append(critical_table)
            
            if missing_tables:
                st.error(f"❌ Backup verification failed: Missing critical tables: {missing_tables}")
            else:
                # Check data counts
                verification_results = {}
                for table in critical_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    verification_results[table] = count
                
                st.success("✅ Backup verification passed!")
                
                # Display verification results
                with st.expander("📊 Verification Details"):
                    for table, count in verification_results.items():
                        st.metric(f"{table.title()} Records", count)
            
            conn.close()
            
    except Exception as e:
        st.error(f"❌ Verification failed: {e}")

def delete_backup(backup_filename: str):
    """Delete a backup file."""
    try:
        backup_path = Path(f"data/backups/{backup_filename}")
        
        if not backup_path.exists():
            st.error(f"❌ Backup file not found: {backup_filename}")
            return
        
        backup_path.unlink()
        
        st.success(f"✅ Backup deleted: {backup_filename}")
        
        # Log the deletion
        log_admin_action(
            st.session_state.get('user_id'),
            'backup_deletion',
            None,
            'backup_file',
            {'deleted_file': backup_filename}
        )
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Deletion failed: {e}")

def get_all_users_for_export():
    """Get all users for export selection."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, full_name, is_admin, is_verified
            FROM users
            ORDER BY email
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'email': row[1],
                'full_name': row[2] or '',
                'is_admin': bool(row[3]),
                'is_verified': bool(row[4])
            })
        
        conn.close()
        return users
        
    except Exception as e:
        st.error(f"❌ Error loading users: {e}")
        return []

def get_position_themes():
    """Get available position themes for filtering."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # This assumes you have themes stored in your positions table
        # Adjust based on your actual schema
        cursor.execute('''
            SELECT DISTINCT theme 
            FROM positions 
            WHERE theme IS NOT NULL AND theme != ''
            ORDER BY theme
        ''')
        
        themes = [row[0] for row in cursor.fetchall()]
        conn.close()
        return themes
        
    except Exception as e:
        # Return some common themes if database query fails
        return ["Tactics", "Endgame", "Opening", "Middlegame", "Puzzle"]

def export_database_to_json(include_user_data: bool, include_games: bool) -> Dict[str, Any]:
    """Export database to JSON format."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'export_version': '2.0.0',
            'tables': {}
        }
        
        # Core tables to always export
        core_tables = ['positions', 'moves']
        
        for table in core_tables:
            cursor.execute(f"SELECT * FROM {table}")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            export_data['tables'][table] = {
                'columns': columns,
                'data': [dict(zip(columns, row)) for row in rows]
            }
        
        # Conditionally include user data
        if include_user_data:
            user_tables = ['users', 'user_moves', 'user_settings', 'training_sessions']
            for table in user_tables:
                try:
                    cursor.execute(f"SELECT * FROM {table}")
                    columns = [description[0] for description in cursor.description]
                    rows = cursor.fetchall()
                    
                    export_data['tables'][table] = {
                        'columns': columns,
                        'data': [dict(zip(columns, row)) for row in rows]
                    }
                except sqlite3.OperationalError:
                    # Table doesn't exist, skip it
                    pass
        
        # Conditionally include games
        if include_games:
            try:
                cursor.execute("SELECT * FROM games")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                export_data['tables']['games'] = {
                    'columns': columns,
                    'data': [dict(zip(columns, row)) for row in rows]
                }
            except sqlite3.OperationalError:
                # Games table doesn't exist, skip it
                pass
        
        conn.close()
        return export_data
        
    except Exception as e:
        st.error(f"❌ JSON export failed: {e}")
        return {}

def export_database_to_csv(include_user_data: bool, include_games: bool) -> Dict[str, str]:
    """Export database to CSV files."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        csv_files = {}
        
        # Core tables
        core_tables = ['positions', 'moves']
        
        for table in core_tables:
            cursor.execute(f"SELECT * FROM {table}")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            df = pd.DataFrame(rows, columns=columns)
            csv_files[f"{table}.csv"] = df.to_csv(index=False)
        
        # User data tables
        if include_user_data:
            user_tables = ['users', 'user_moves', 'user_settings', 'training_sessions']
            for table in user_tables:
                try:
                    cursor.execute(f"SELECT * FROM {table}")
                    columns = [description[0] for description in cursor.description]
                    rows = cursor.fetchall()
                    
                    df = pd.DataFrame(rows, columns=columns)
                    csv_files[f"{table}.csv"] = df.to_csv(index=False)
                except sqlite3.OperationalError:
                    pass
        
        # Games data
        if include_games:
            try:
                cursor.execute("SELECT * FROM games")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                df = pd.DataFrame(rows, columns=columns)
                csv_files["games.csv"] = df.to_csv(index=False)
            except sqlite3.OperationalError:
                pass
        
        conn.close()
        return csv_files
        
    except Exception as e:
        st.error(f"❌ CSV export failed: {e}")
        return {}

def log_admin_action(admin_user_id: int, action: str, target_user_id: Optional[int], 
                    target_resource: Optional[str], action_data: Optional[Dict] = None):
    """Log admin action for audit purposes."""
    try:
        from database import log_admin_action as db_log_action
        db_log_action(admin_user_id, action, target_user_id, target_resource, action_data)
    except ImportError:
        # If the function doesn't exist in database module, implement basic logging
        pass

def create_automated_backup():
    """Create an automated backup (for scheduled backups)."""
    try:
        source_db = "data/kuikma_chess.db"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"auto_backup_{timestamp}.db"
        backup_path = f"data/backups/{backup_name}"
        
        # Ensure backup directory exists
        Path("data/backups").mkdir(parents=True, exist_ok=True)
        
        # Copy database
        shutil.copy2(source_db, backup_path)
        
        # Verify backup if setting is enabled
        if get_backup_setting('verify_after_backup', True):
            conn = sqlite3.connect(backup_path)
            conn.execute("SELECT COUNT(*) FROM sqlite_master")
            conn.close()
        
        return backup_path
        
    except Exception as e:
        print(f"Automated backup failed: {e}")
        return None

def export_template_styles():
    """Export CSS styles for consistent export formatting."""
    return """
    <style>
    .export-header {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    
    .export-table {
        border-collapse: collapse;
        width: 100%;
    }
    
    .export-table th, .export-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    
    .export-table th {
        background-color: #4CAF50;
        color: white;
    }
    
    .export-table tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    </style>
    """

def generate_export_summary(export_type: str, record_count: int, file_size: Optional[float] = None) -> str:
    """Generate a summary for export operations."""
    summary = f"""
    📊 **Export Summary**
    
    **Type:** {export_type}
    **Records Exported:** {record_count:,}
    **Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    if file_size:
        summary += f"\n**File Size:** {file_size:.2f} MB"
    
    return summary

def validate_export_permissions(user_id: int, export_type: str) -> bool:
    """Validate if user has permission to perform specific export."""
    try:
        from auth import check_user_access
        
        # Map export types to required permissions
        permission_map = {
            'user_data': 'export_data',
            'admin_data': 'admin_panel',
            'system_analytics': 'admin_panel',
            'database_backup': 'database_viewer'
        }
        
        required_permission = permission_map.get(export_type, 'export_data')
        return check_user_access(user_id, required_permission)
        
    except ImportError:
        # If auth module not available, allow for admin users only
        return st.session_state.get('user_info', {}).get('is_admin', False)

def format_export_filename(base_name: str, export_format: str, timestamp: Optional[str] = None) -> str:
    """Generate standardized export filenames."""
    if not timestamp:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Clean base name
    clean_name = base_name.lower().replace(' ', '_').replace('-', '_')
    
    return f"kuikma_{clean_name}_{timestamp}.{export_format.lower()}"

# Configuration management for backup settings
class BackupConfig:
    """Manage backup configuration settings."""
    
    def __init__(self):
        self.config_file = Path("data/backup_config.json")
        self.default_settings = {
            'auto_backup_enabled': False,
            'backup_frequency': 'Weekly',
            'retention_days': 30,
            'compression_level': 6,
            'include_logs': False,
            'verify_after_backup': True,
            'max_backup_size_mb': 1000,
            'backup_location': 'data/backups'
        }
    
    def load_settings(self) -> Dict[str, Any]:
        """Load backup settings from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**self.default_settings, **settings}
            else:
                return self.default_settings.copy()
        except Exception:
            return self.default_settings.copy()
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save backup settings to file."""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception:
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific backup setting."""
        settings = self.load_settings()
        return settings.get(key, default)

# Global backup config instance
backup_config = BackupConfig()

# Update the get_backup_setting function to use the config class
def get_backup_setting(key: str, default: Any = None) -> Any:
    """Get backup setting using the config system."""
    return backup_config.get_setting(key, default)

def save_backup_settings(settings: Dict[str, Any]) -> bool:
    """Save backup settings using the config system."""
    return backup_config.save_settings(settings)
