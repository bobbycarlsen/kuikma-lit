# auth.py - Authentication Module with User Verification & Access Control
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import json
import secrets
from config import config
import database
from database import (get_db_connection, create_user_subscription, log_admin_action, 
                     upgrade_existing_database)


def is_admin_user(user_id: int) -> bool:
    """
    Check if a user has admin privileges.
    
    Args:
        user_id: User's ID
        
    Returns:
        True if user is admin, False otherwise
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        return bool(result and result[0])
        
    except Exception as e:
        print(f"Admin check error: {e}")
        return False
    finally:
        conn.close()

def update_user_password(user_id: int, old_password: str, new_password: str) -> bool:
    """
    Update user password.
    
    Args:
        user_id: User's ID
        old_password: Current password
        new_password: New password
        
    Returns:
        True if update successful, False otherwise
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verify old password
        old_password_hash = hash_password(old_password)
        cursor.execute('''
            SELECT id FROM users 
            WHERE id = ? AND password_hash = ?
        ''', (user_id, old_password_hash))
        
        if not cursor.fetchone():
            return False
        
        # Update to new password
        new_password_hash = hash_password(new_password)
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?
            WHERE id = ?
        ''', (new_password_hash, user_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Password update error: {e}")
        return False
    finally:
        conn.close()

def get_user_settings(user_id: int) -> dict:
    """
    Get user settings.
    
    Args:
        user_id: User's ID
        
    Returns:
        Dictionary with user settings
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT random_positions, top_n_threshold, score_difference_threshold, theme
            FROM user_settings 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if result:
            return {
                'random_positions': bool(result[0]),
                'top_n_threshold': result[1],
                'score_difference_threshold': result[2],
                'theme': result[3]
            }
        else:
            # Create default settings if they don't exist
            default_settings = {
                'random_positions': True,
                'top_n_threshold': 3,
                'score_difference_threshold': 10,
                'theme': 'default'
            }
            
            cursor.execute('''
                INSERT INTO user_settings (user_id, random_positions, top_n_threshold, score_difference_threshold, theme)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, default_settings['random_positions'], default_settings['top_n_threshold'],
                  default_settings['score_difference_threshold'], default_settings['theme']))
            
            conn.commit()
            return default_settings
        
    except Exception as e:
        print(f"Error getting user settings: {e}")
        return {
            'random_positions': True,
            'top_n_threshold': 3,
            'score_difference_threshold': 10,
            'theme': 'default'
        }
    finally:
        conn.close()

def update_user_settings(user_id: int, settings: dict) -> bool:
    """
    Update user settings.
    
    Args:
        user_id: User's ID
        settings: Dictionary with settings to update
        
    Returns:
        True if update successful, False otherwise
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE user_settings 
            SET random_positions = ?, top_n_threshold = ?, score_difference_threshold = ?, theme = ?
            WHERE user_id = ?
        ''', (
            settings.get('random_positions', True),
            settings.get('top_n_threshold', 3),
            settings.get('score_difference_threshold', 10),
            settings.get('theme', 'default'),
            user_id
        ))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Settings update error: {e}")
        return False
    finally:
        conn.close()

def delete_user_account(user_id: int, password: str) -> bool:
    """
    Delete user account and all associated data.
    
    Args:
        user_id: User's ID
        password: User's password for confirmation
        
    Returns:
        True if deletion successful, False otherwise
    """
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verify password
        password_hash = hash_password(password)
        cursor.execute('''
            SELECT id FROM users 
            WHERE id = ? AND password_hash = ?
        ''', (user_id, password_hash))
        
        if not cursor.fetchone():
            return False
        
        # Don't allow admin account deletion
        if is_admin_user(user_id):
            return False
        
        # Delete all user data (foreign keys will handle cascading)
        tables_to_clean = [
            'user_move_analysis',
            'user_moves', 
            'user_settings',
            'training_sessions',
            'user_game_analysis',
            'user_saved_games',
            'user_game_sessions',
            'user_insights_cache'
        ]
        
        for table in tables_to_clean:
            cursor.execute(f'DELETE FROM {table} WHERE user_id = ?', (user_id,))
        
        # Finally delete the user
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Account deletion error: {e}")
        return False
    finally:
        conn.close()

def toggle_admin_status(admin_user_id: int, target_user_id: int) -> bool:
    """
    Toggle admin status of a user (admin only).
    
    Args:
        admin_user_id: ID of admin user making the request
        target_user_id: ID of user to toggle admin status
        
    Returns:
        True if toggle successful, False otherwise
    """
    if not is_admin_user(admin_user_id):
        return False
    
    # Don't allow toggling the original admin account
    if target_user_id == 1:  # Assuming first user is the main admin
        return False
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE users 
            SET is_admin = NOT is_admin
            WHERE id = ?
        ''', (target_user_id,))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Admin toggle error: {e}")
        return False
    finally:
        conn.close()

def generate_session_token() -> str:
    """Generate a secure session token."""
    return secrets.token_urlsafe(32)

def ensure_admin_user():
    """Ensure the admin user exists from .env configuration."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        admin_email = config.ADMIN_EMAIL
        admin_password = config.ADMIN_PASSWORD
        admin_name = config.ADMIN_NAME
        
        cursor.execute('SELECT id FROM users WHERE email = ?', (admin_email,))
        if not cursor.fetchone():
            # Create admin user
            password_hash = hash_password(admin_password)
            cursor.execute('''
                INSERT INTO users (
                    email, password_hash, created_at, is_admin, is_verified,
                    verification_status, verified_at, full_name, account_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                admin_email, password_hash, datetime.now().isoformat(),
                True, True, 'approved', datetime.now().isoformat(),
                admin_name, 'active'
            ))
            
            user_id = cursor.lastrowid
            
            # Create default settings for admin
            cursor.execute('''
                INSERT INTO user_settings (user_id)
                VALUES (?)
            ''', (user_id,))
            
            # Create unlimited subscription for admin
            cursor.execute('''
                INSERT INTO user_subscriptions (
                    user_id, subscription_type, position_limit, analysis_limit, 
                    game_upload_limit, updated_by
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, 'admin', 999999, 999999, 999999, user_id))
            
            conn.commit()
            print(f"✅ Admin user created: {admin_email}")
        else:
            # Update existing admin user credentials if they changed
            password_hash = hash_password(admin_password)
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, full_name = ?, is_verified = TRUE, 
                    verification_status = 'approved'
                WHERE email = ? AND is_admin = TRUE
            ''', (password_hash, admin_name, admin_email))
            conn.commit()
        
    except Exception as e:
        print(f"Error ensuring admin user: {e}")
    finally:
        conn.close()

def verify_user(user_id: int, admin_user_id: int, approved: bool = True, 
               admin_notes: str = "") -> bool:
    """
    Verify or reject a user registration.
    
    Args:
        user_id: ID of user to verify
        admin_user_id: ID of admin performing verification
        approved: Whether to approve or reject
        admin_notes: Admin notes for the decision
        
    Returns:
        True if verification successful, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        verification_status = 'approved' if approved else 'rejected'
        verified_at = datetime.now().isoformat() if approved else None
        
        # Update user verification status
        cursor.execute('''
            UPDATE users 
            SET is_verified = ?, verification_status = ?, verified_at = ?, verified_by = ?
            WHERE id = ?
        ''', (approved, verification_status, verified_at, admin_user_id, user_id))
        
        # Update verification request if exists
        cursor.execute('''
            UPDATE user_verification_requests 
            SET status = ?, reviewed_at = ?, reviewed_by = ?, admin_notes = ?
            WHERE user_id = ? AND status = 'pending'
        ''', (verification_status, datetime.now().isoformat(), admin_user_id, admin_notes, user_id))
        
        # Log admin action
        log_admin_action(
            admin_user_id, 
            f'user_verification_{verification_status}',
            user_id,
            'user_account',
            {'admin_notes': admin_notes}
        )
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error verifying user: {e}")
        return False
    finally:
        conn.close()

def get_users_for_verification() -> List[Dict[str, any]]:
    """Get list of users pending verification."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT u.id, u.email, u.full_name, u.created_at, u.verification_status,
                   vr.request_data, vr.requested_at
            FROM users u
            LEFT JOIN user_verification_requests vr ON u.id = vr.user_id
            WHERE u.verification_status = 'pending' AND u.is_admin = FALSE
            ORDER BY u.created_at ASC
        ''')
        
        results = cursor.fetchall()
        
        users = []
        for row in results:
            user_data = {
                'id': row[0],
                'email': row[1],
                'full_name': row[2] or '',
                'created_at': row[3],
                'verification_status': row[4],
                'request_data': json.loads(row[5]) if row[5] else {},
                'requested_at': row[6]
            }
            users.append(user_data)
        
        return users
        
    except Exception as e:
        print(f"Error getting users for verification: {e}")
        return []
    finally:
        conn.close()

def update_user_subscription(user_id: int, admin_user_id: int, **kwargs) -> bool:
    """Update user subscription limits."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build update query dynamically
        allowed_fields = ['position_limit', 'analysis_limit', 'game_upload_limit', 
                         'subscription_type', 'positions_used', 'analyses_used', 'games_uploaded']
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = ?")
                values.append(value)
        
        if not update_fields:
            return False
        
        values.extend([datetime.now().isoformat(), admin_user_id, user_id])
        
        query = f'''
            UPDATE user_subscriptions 
            SET {", ".join(update_fields)}, updated_at = ?, updated_by = ?
            WHERE user_id = ?
        '''
        
        cursor.execute(query, values)
        
        # Log admin action
        log_admin_action(
            admin_user_id,
            'subscription_update',
            user_id,
            'user_subscription',
            kwargs
        )
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Error updating user subscription: {e}")
        return False
    finally:
        conn.close()

def get_user_statistics(user_id: int) -> dict:
    """
    Get comprehensive user statistics - FIXED VERSION.
    
    Args:
        user_id: User's ID
        
    Returns:
        Dictionary with user statistics
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        # Training statistics - fixed to use 'result' column
        cursor.execute('''
            SELECT 
                COUNT(*) as total_moves,
                SUM(CASE WHEN result = 'correct' THEN 1 ELSE 0 END) as correct_moves,
                AVG(time_taken) as avg_time
            FROM user_moves 
            WHERE user_id = ?
        ''', (user_id,))
        
        training_stats = cursor.fetchone()
        if training_stats:
            total_moves = training_stats[0] or 0
            correct_moves = training_stats[1] or 0
            avg_time = training_stats[2] or 0
            
            stats.update({
                'total_moves': total_moves,
                'correct_moves': correct_moves,
                'accuracy': round((correct_moves / total_moves * 100), 2) if total_moves > 0 else 0,
                'average_time': round(avg_time, 2)
            })
        else:
            stats.update({
                'total_moves': 0,
                'correct_moves': 0,
                'accuracy': 0,
                'average_time': 0
            })
        
        # Game analysis statistics - with error handling
        try:
            cursor.execute('''
                SELECT 
                    COUNT(*) as games_analyzed,
                    SUM(moves_analyzed) as total_moves_analyzed,
                    AVG(total_time_spent) as avg_analysis_time
                FROM user_game_analysis 
                WHERE user_id = ?
            ''', (user_id,))
            
            game_stats = cursor.fetchone()
            if game_stats:
                stats.update({
                    'games_analyzed': game_stats[0] or 0,
                    'total_moves_analyzed': game_stats[1] or 0,
                    'avg_analysis_time': round(game_stats[2] or 0, 2)
                })
            else:
                stats.update({
                    'games_analyzed': 0,
                    'total_moves_analyzed': 0,
                    'avg_analysis_time': 0
                })
        except Exception as game_error:
            print(f"Error getting game analysis stats: {game_error}")
            stats.update({
                'games_analyzed': 0,
                'total_moves_analyzed': 0,
                'avg_analysis_time': 0
            })
        
        # Training sessions - with error handling
        try:
            cursor.execute('''
                SELECT COUNT(*) as session_count
                FROM training_sessions 
                WHERE user_id = ?
            ''', (user_id,))
            
            session_count = cursor.fetchone()
            if session_count:
                stats['training_sessions'] = session_count[0] or 0
            else:
                stats['training_sessions'] = 0
        except Exception as session_error:
            print(f"Error getting training session stats: {session_error}")
            stats['training_sessions'] = 0
        
        # Recent activity - with error handling
        try:
            cursor.execute('''
                SELECT MAX(timestamp) as last_training
                FROM user_moves 
                WHERE user_id = ?
            ''', (user_id,))
            
            last_training = cursor.fetchone()
            if last_training and last_training[0]:
                stats['last_training'] = last_training[0]
            else:
                stats['last_training'] = None
        except Exception as activity_error:
            print(f"Error getting recent activity: {activity_error}")
            stats['last_training'] = None
        
        return stats
        
    except Exception as e:
        print(f"Error getting user statistics: {e}")
        return {
            'total_moves': 0,
            'correct_moves': 0,
            'accuracy': 0,
            'average_time': 0,
            'games_analyzed': 0,
            'total_moves_analyzed': 0,
            'avg_analysis_time': 0,
            'training_sessions': 0,
            'last_training': None
        }
    finally:
        conn.close()

def get_user_subscription(user_id: int) -> Optional[Dict[str, any]]:
    """Get user subscription information - ENHANCED VERSION."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT subscription_type, position_limit, analysis_limit, game_upload_limit,
                   positions_used, analyses_used, games_uploaded, reset_date
            FROM user_subscriptions 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'subscription_type': result[0],
                'position_limit': result[1],
                'analysis_limit': result[2],
                'game_upload_limit': result[3],
                'positions_used': result[4],
                'analyses_used': result[5],
                'games_uploaded': result[6],
                'reset_date': result[7],
                'positions_remaining': max(result[1] - result[4], 0),
                'analyses_remaining': max(result[2] - result[5], 0),
                'games_remaining': max(result[3] - result[6], 0)
            }
        else:
            # Create default subscription if missing
            return create_missing_subscription(user_id)
        
    except Exception as e:
        print(f"Error getting user subscription: {e}")
        # Try to create default subscription
        return create_missing_subscription(user_id)
    finally:
        conn.close()

def create_missing_subscription(user_id: int) -> Optional[Dict[str, any]]:
    """Create a missing subscription for a user."""
    try:
        from database import create_user_subscription
        if create_user_subscription(user_id):
            # Try to get the subscription again
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT subscription_type, position_limit, analysis_limit, game_upload_limit,
                       positions_used, analyses_used, games_uploaded, reset_date
                FROM user_subscriptions 
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'subscription_type': result[0],
                    'position_limit': result[1],
                    'analysis_limit': result[2],
                    'game_upload_limit': result[3],
                    'positions_used': result[4],
                    'analyses_used': result[5],
                    'games_uploaded': result[6],
                    'reset_date': result[7],
                    'positions_remaining': max(result[1] - result[4], 0),
                    'analyses_remaining': max(result[2] - result[5], 0),
                    'games_remaining': max(result[3] - result[6], 0)
                }
        
        return None
        
    except Exception as e:
        print(f"Error creating missing subscription: {e}")
        return None

def authenticate_user(email: str, password: str) -> Optional[Dict[str, any]]:
    """
    Authenticate a user and return their info if successful - ENHANCED VERSION.
    
    Args:
        email: User's email address
        password: User's plain text password
        
    Returns:
        User info dictionary if authentication successful, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        email = email.lower().strip()
        
        # Check if required columns exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Build query based on available columns
        base_select = 'id, email, is_admin'
        optional_columns = []
        
        if 'is_verified' in columns:
            optional_columns.append('is_verified')
        if 'verification_status' in columns:
            optional_columns.append('verification_status')
        if 'account_status' in columns:
            optional_columns.append('account_status')
        if 'failed_login_attempts' in columns:
            optional_columns.append('failed_login_attempts')
        if 'locked_until' in columns:
            optional_columns.append('locked_until')
        if 'full_name' in columns:
            optional_columns.append('full_name')
        
        select_clause = base_select
        if optional_columns:
            select_clause += ', ' + ', '.join(optional_columns)
        
        # Check for account lockout if columns exist
        if 'locked_until' in columns and 'failed_login_attempts' in columns:
            cursor.execute(f'''
                SELECT locked_until, failed_login_attempts 
                FROM users WHERE email = ?
            ''', (email,))
            
            lock_info = cursor.fetchone()
            if lock_info and lock_info[0]:
                try:
                    locked_until = datetime.fromisoformat(lock_info[0])
                    if datetime.now() < locked_until:
                        return {'error': 'account_locked', 'locked_until': lock_info[0]}
                except:
                    pass  # Invalid datetime format, continue
        
        password_hash = hash_password(password)
        
        cursor.execute(f'''
            SELECT {select_clause}
            FROM users 
            WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        result = cursor.fetchone()
        
        if result:
            # Parse result based on available columns
            user_data = {
                'id': result[0],
                'email': result[1],
                'is_admin': bool(result[2])
            }
            
            # Add optional columns if they exist
            col_index = 3
            for col in optional_columns:
                if col_index < len(result):
                    if col in ['is_verified']:
                        user_data[col] = bool(result[col_index])
                    else:
                        user_data[col] = result[col_index]
                    col_index += 1
            
            # Set defaults for missing columns
            if 'is_verified' not in user_data:
                user_data['is_verified'] = True  # Default for backward compatibility
            if 'verification_status' not in user_data:
                user_data['verification_status'] = 'approved'
            if 'account_status' not in user_data:
                user_data['account_status'] = 'active'
            if 'full_name' not in user_data:
                user_data['full_name'] = None
            
            # Check account status
            if user_data.get('account_status', 'active') != 'active':
                return {'error': 'account_inactive', 'status': user_data['account_status']}
            
            # Reset failed login attempts on successful login
            if 'failed_login_attempts' in columns:
                cursor.execute('''
                    UPDATE users 
                    SET last_login = ?, failed_login_attempts = 0, locked_until = NULL
                    WHERE id = ?
                ''', (datetime.now().isoformat(), user_data['id']))
            else:
                cursor.execute('''
                    UPDATE users 
                    SET last_login = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), user_data['id']))
            
            conn.commit()
            
            return user_data
        else:
            # Increment failed login attempts if columns exist
            if 'failed_login_attempts' in columns:
                cursor.execute('''
                    UPDATE users 
                    SET failed_login_attempts = COALESCE(failed_login_attempts, 0) + 1
                    WHERE email = ?
                ''', (email,))
                
                # Check if we should lock the account
                cursor.execute('''
                    SELECT failed_login_attempts FROM users WHERE email = ?
                ''', (email,))
                
                attempts_result = cursor.fetchone()
                if attempts_result and attempts_result[0] >= config.MAX_LOGIN_ATTEMPTS:
                    if 'locked_until' in columns:
                        locked_until = datetime.now() + timedelta(seconds=config.LOCKOUT_DURATION)
                        cursor.execute('''
                            UPDATE users 
                            SET locked_until = ?
                            WHERE email = ?
                        ''', (locked_until.isoformat(), email))
                
                conn.commit()
            
            return None
        
    except Exception as e:
        print(f"Authentication error: {e}")
        return None
    finally:
        conn.close()

def get_user_info(user_id: int) -> Optional[dict]:
    """
    Get user information - ENHANCED VERSION.
    
    Args:
        user_id: User's ID
        
    Returns:
        Dictionary with user info or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check what columns exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Build query based on available columns
        base_columns = ['id', 'email', 'created_at', 'last_login', 'is_admin']
        optional_columns = []
        
        for col in ['is_verified', 'verification_status', 'verified_at', 'verified_by', 
                   'full_name', 'profile_notes', 'account_status']:
            if col in columns:
                optional_columns.append(col)
        
        all_columns = base_columns + optional_columns
        
        cursor.execute(f'''
            SELECT {", ".join(all_columns)}
            FROM users 
            WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if result:
            user_info = {}
            for i, col in enumerate(all_columns):
                if i < len(result):
                    if col in ['is_admin', 'is_verified']:
                        user_info[col] = bool(result[i])
                    else:
                        user_info[col] = result[i]
            
            return user_info
        
        return None
        
    except Exception as e:
        print(f"Error getting user info: {e}")
        return None
    finally:
        conn.close()

def check_user_access(user_id: int, feature: str) -> bool:
    """
    Check if user has access to a specific feature - ENHANCED VERSION.
    
    Args:
        user_id: User's ID
        feature: Feature name to check
        
    Returns:
        True if user has access, False otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get user info with error handling
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Build safe query
        base_query = 'SELECT is_admin'
        if 'is_verified' in columns:
            base_query += ', is_verified'
        if 'verification_status' in columns:
            base_query += ', verification_status'
        
        cursor.execute(f'{base_query} FROM users WHERE id = ?', (user_id,))
        
        result = cursor.fetchone()
        if not result:
            return False
        
        is_admin = bool(result[0])
        is_verified = bool(result[1]) if len(result) > 1 else True  # Default for backward compatibility
        verification_status = result[2] if len(result) > 2 else 'approved'
        
        # Determine user type
        if is_admin:
            user_type = 'admin'
        elif is_verified and verification_status == 'approved':
            user_type = 'verified_user'
        else:
            user_type = 'unverified_user'
        
        # Get permissions for user type
        try:
            permissions = config.get_user_permissions(user_type)
            
            # Check specific feature access
            if feature in permissions:
                return permissions[feature]
        except Exception as config_error:
            print(f"Error getting user permissions: {config_error}")
            # Fallback permissions
            if is_admin:
                return True
            elif feature in ['login', 'view_profile', 'change_password']:
                return True
            elif is_verified and feature in ['training', 'analysis', 'insights', 'user_dashboard']:
                return True
            else:
                return False
        
        # Check custom feature access if table exists
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_feature_access'")
            if cursor.fetchone():
                cursor.execute('''
                    SELECT access_granted, expires_at 
                    FROM user_feature_access 
                    WHERE user_id = ? AND feature_name = ?
                ''', (user_id, feature))
                
                custom_access = cursor.fetchone()
                if custom_access:
                    granted, expires_at = custom_access
                    if granted:
                        if not expires_at or datetime.now() < datetime.fromisoformat(expires_at):
                            return True
        except Exception as custom_error:
            print(f"Error checking custom feature access: {custom_error}")
        
        return False
        
    except Exception as e:
        print(f"Error checking user access: {e}")
        return False
    finally:
        conn.close()

def can_use_resource(user_id: int, resource_type: str) -> Tuple[bool, Optional[str]]:
    """
    Check if user can use a resource - ENHANCED VERSION.
    
    Args:
        user_id: User's ID
        resource_type: Type of resource ('position', 'analysis', 'game_upload')
        
    Returns:
        Tuple of (can_use, reason_if_not)
    """
    try:
        # Check if user is admin first
        user_info = get_user_info(user_id)
        if user_info and user_info.get('is_admin'):
            return True, None
        
        subscription = get_user_subscription(user_id)
        if not subscription:
            return False, "No subscription found"
        
        if resource_type == 'position':
            if subscription['positions_used'] >= subscription['position_limit']:
                return False, f"Position limit reached ({subscription['position_limit']})"
        elif resource_type == 'analysis':
            if subscription['analyses_used'] >= subscription['analysis_limit']:
                return False, f"Analysis limit reached ({subscription['analysis_limit']})"
        elif resource_type == 'game_upload':
            if subscription['games_uploaded'] >= subscription['game_upload_limit']:
                return False, f"Game upload limit reached ({subscription['game_upload_limit']})"
        
        return True, None
        
    except Exception as e:
        print(f"Error checking resource usage: {e}")
        return False, f"Error checking resource: {str(e)}"

def increment_resource_usage(user_id: int, resource_type: str, amount: int = 1) -> bool:
    """Increment resource usage counter - ENHANCED VERSION."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user is admin - don't track usage for admin
        user_info = get_user_info(user_id)
        if user_info and user_info.get('is_admin'):
            return True
        
        field_map = {
            'position': 'positions_used',
            'analysis': 'analyses_used',
            'game_upload': 'games_uploaded'
        }
        
        field = field_map.get(resource_type)
        if not field:
            return False
        
        cursor.execute(f'''
            UPDATE user_subscriptions 
            SET {field} = {field} + ?, updated_at = ?
            WHERE user_id = ?
        ''', (amount, datetime.now().isoformat(), user_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Error incrementing resource usage: {e}")
        return False
    finally:
        conn.close()

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email: str, password: str, full_name: str = "") -> Dict[str, any]:
    """
    Register a new user with enhanced verification system - FIXED VERSION.
    
    Args:
        email: User's email address
        password: User's plain text password
        full_name: User's full name (optional)
        
    Returns:
        Dictionary with registration result
    """
    if not config.ENABLE_USER_REGISTRATION:
        return {'success': False, 'error': 'registration_disabled'}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        email = email.lower().strip()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return {'success': False, 'error': 'email_exists'}
        
        # Check if this is an admin email (admins cannot register, only login)
        if email == config.ADMIN_EMAIL:
            return {'success': False, 'error': 'admin_cannot_register'}
        
        password_hash = hash_password(password)
        
        # Check what columns exist in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Determine initial verification status
        is_verified = config.AUTO_APPROVE_USERS
        verification_status = 'approved' if config.AUTO_APPROVE_USERS else 'pending'
        verified_at = datetime.now().isoformat() if config.AUTO_APPROVE_USERS else None
        
        # Build insert query based on available columns
        base_columns = ['email', 'password_hash', 'created_at', 'is_admin']
        base_values = [email, password_hash, datetime.now().isoformat(), False]
        
        optional_columns = []
        optional_values = []
        
        if 'is_verified' in columns:
            optional_columns.append('is_verified')
            optional_values.append(is_verified)
        
        if 'verification_status' in columns:
            optional_columns.append('verification_status')
            optional_values.append(verification_status)
        
        if 'verified_at' in columns:
            optional_columns.append('verified_at')
            optional_values.append(verified_at)
        
        if 'full_name' in columns:
            optional_columns.append('full_name')
            optional_values.append(full_name)
        
        if 'account_status' in columns:
            optional_columns.append('account_status')
            optional_values.append('active')
        
        all_columns = base_columns + optional_columns
        all_values = base_values + optional_values
        
        placeholders = ', '.join(['?' for _ in all_columns])
        
        cursor.execute(f'''
            INSERT INTO users ({", ".join(all_columns)})
            VALUES ({placeholders})
        ''', all_values)
        
        user_id = cursor.lastrowid
        
        # Create default user settings if table exists
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_settings'")
            if cursor.fetchone():
                cursor.execute('''
                    INSERT INTO user_settings (user_id)
                    VALUES (?)
                ''', (user_id,))
        except Exception as settings_error:
            print(f"Warning: Could not create user settings: {settings_error}")
        
        # Create default subscription
        try:
            from database import create_user_subscription
            create_user_subscription(user_id)
        except Exception as sub_error:
            print(f"Warning: Could not create user subscription: {sub_error}")
        
        # Create verification request if manual approval required
        if not config.AUTO_APPROVE_USERS:
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_verification_requests'")
                if cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO user_verification_requests (
                            user_id, request_type, request_data
                        ) VALUES (?, ?, ?)
                    ''', (user_id, 'registration', json.dumps({'full_name': full_name})))
            except Exception as verification_error:
                print(f"Warning: Could not create verification request: {verification_error}")
        
        conn.commit()
        
        return {
            'success': True,
            'user_id': user_id,
            'verification_required': not config.AUTO_APPROVE_USERS,
            'message': 'Registration successful. Please wait for admin approval.' if not config.AUTO_APPROVE_USERS else 'Registration successful!'
        }
        
    except Exception as e:
        print(f"Registration error: {e}")
        conn.rollback()
        return {'success': False, 'error': 'registration_failed', 'details': str(e)}
    finally:
        conn.close()

# Initialize on import
if __name__ == "__main__":
    print("Initializing enhanced authentication...")
    upgrade_existing_database()
    ensure_admin_user()
    print("Authentication module initialized.")
