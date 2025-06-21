# user_dashboard.py - Fixed User Dashboard Component
"""
User dashboard component displaying account status, subscription usage,
recent activity, and account management options.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from auth import (get_user_subscription, get_user_info, get_user_statistics,
                 update_user_password)
from access_control import require_login, verification_context, resource_context
from database import get_db_connection
from config import config

def display_user_dashboard():
    """Display comprehensive user dashboard."""
    st.markdown("# 👤 User Dashboard")
    
    user_id = st.session_state['user_id']
    user_info = get_user_info(user_id)
    
    if not user_info:
        st.error("❌ Could not load user information")
        return
    
    # Dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "💳 Subscription", 
        "📈 Activity", 
        "⚙️ Account Settings"
    ])
    
    with tab1:
        display_overview_tab(user_info)
    
    with tab2:
        display_subscription_tab(user_id)
    
    with tab3:
        display_activity_tab(user_id)
    
    with tab4:
        display_account_settings_tab(user_id, user_info)

def display_overview_tab(user_info: Dict):
    """Display user overview information."""
    st.markdown("### 📋 Account Overview")
    
    # Account status cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Verification status
        if user_info.get('is_admin'):
            st.success("👑 **Admin Account**")
            st.caption("Full access to all features")
        elif user_info.get('is_verified'):
            st.success("✅ **Verified User**")
            st.caption("Full feature access")
        else:
            st.warning("⏳ **Pending Verification**")
            st.caption("Limited access until approved")
    
    with col2:
        # Account age
        if user_info.get('created_at'):
            created_date = datetime.fromisoformat(user_info['created_at'])
            days_since = (datetime.now() - created_date).days
            st.info(f"📅 **Member for {days_since} days**")
            st.caption(f"Joined {created_date.strftime('%B %d, %Y')}")
        else:
            st.info("📅 **New Account**")
    
    with col3:
        # Last activity
        if user_info.get('last_login'):
            last_login = datetime.fromisoformat(user_info['last_login'])
            st.info(f"🕐 **Last seen: {last_login.strftime('%m/%d/%Y')}**")
            st.caption(f"At {last_login.strftime('%I:%M %p')}")
        else:
            st.info("🕐 **First time login**")
    
    st.markdown("---")
    
    # Quick stats
    stats = get_user_statistics(st.session_state['user_id'])
    
    if stats:
        st.markdown("### 📊 Quick Statistics")
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.metric(
                "Training Moves",
                stats.get('total_moves', 0)
            )
        
        with stat_col2:
            correct_moves = stats.get('correct_moves', 0)
            total_moves = stats.get('total_moves', 1)
            accuracy = (correct_moves / total_moves * 100) if total_moves > 0 else 0
            st.metric(
                "Accuracy",
                f"{accuracy:.1f}%"
            )
        
        with stat_col3:
            st.metric(
                "Training Sessions",
                stats.get('training_sessions', 0)
            )
        
        with stat_col4:
            st.metric(
                "Games Analyzed",
                stats.get('games_analyzed', 0)
            )
    
    # Verification status details
    if not user_info.get('is_verified') and not user_info.get('is_admin'):
        st.markdown("---")
        st.markdown("### ⚠️ Verification Required")
        
        verification_status = user_info.get('verification_status', 'pending')
        
        if verification_status == 'pending':
            st.info("""
            📋 **Your account is pending admin approval**
            
            While you wait for verification:
            - You can update your profile information
            - Change your password
            - View this dashboard
            
            Once verified, you'll have access to:
            - Training positions
            - Analysis tools
            - Game uploads
            - Export features
            """)
            
            # Request verification button
            if st.button("📧 Request Verification Review", use_container_width=True):
                request_verification_review(st.session_state['user_id'])
        
        elif verification_status == 'rejected':
            st.error("""
            ❌ **Your verification request was rejected**
            
            Please contact an administrator for more information or to appeal this decision.
            """)

def display_subscription_tab(user_id: int):
    """Display subscription information and usage."""
    st.markdown("### 💳 Subscription & Usage")
    
    try:
        subscription = get_user_subscription(user_id)
        
        if not subscription:
            # Try to create default subscription if missing
            from database import create_user_subscription
            if create_user_subscription(user_id):
                subscription = get_user_subscription(user_id)
            
            if not subscription:
                st.error("❌ Could not load subscription information")
                st.info("💡 Contact an administrator to set up your subscription.")
                return
        
        # Subscription type and overview
        st.markdown(f"**Subscription Type:** {subscription['subscription_type'].title()}")
        
        if subscription.get('reset_date'):
            st.markdown(f"**Next Reset:** {subscription['reset_date']}")
        
        st.markdown("---")
        
        # Usage meters
        st.markdown("#### 📊 Usage Overview")
        
        # Position usage
        position_usage = subscription['positions_used'] / max(subscription['position_limit'], 1)
        st.markdown("**Training Positions**")
        st.progress(min(position_usage, 1.0))
        st.caption(f"{subscription['positions_used']} of {subscription['position_limit']} used ({subscription['positions_remaining']} remaining)")
        
        # Analysis usage
        analysis_usage = subscription['analyses_used'] / max(subscription['analysis_limit'], 1)
        st.markdown("**Analysis Credits**")
        st.progress(min(analysis_usage, 1.0))
        st.caption(f"{subscription['analyses_used']} of {subscription['analysis_limit']} used ({subscription['analyses_remaining']} remaining)")
        
        # Game upload usage
        game_usage = subscription['games_uploaded'] / max(subscription['game_upload_limit'], 1)
        st.markdown("**Game Uploads**")
        st.progress(min(game_usage, 1.0))
        st.caption(f"{subscription['games_uploaded']} of {subscription['game_upload_limit']} used ({subscription['games_remaining']} remaining)")
        
        # Usage warnings
        if position_usage > 0.8:
            st.warning("⚠️ You're running low on training positions!")
        
        if analysis_usage > 0.8:
            st.warning("⚠️ You're running low on analysis credits!")
        
        if game_usage > 0.8:
            st.warning("⚠️ You're approaching your game upload limit!")
        
        # Subscription details
        with st.expander("📋 Subscription Details"):
            details_data = {
                'Feature': ['Position Limit', 'Analysis Limit', 'Game Upload Limit', 'Subscription Type'],
                'Current': [
                    subscription['position_limit'],
                    subscription['analysis_limit'], 
                    subscription['game_upload_limit'],
                    subscription['subscription_type'].title()
                ],
                'Used': [
                    subscription['positions_used'],
                    subscription['analyses_used'],
                    subscription['games_uploaded'],
                    'N/A'
                ]
            }
            
            df = pd.DataFrame(details_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Upgrade information
        st.markdown("---")
        st.markdown("#### 🚀 Need More Resources?")
        st.info("Contact an administrator to upgrade your subscription or increase your limits.")
        
    except Exception as e:
        st.error(f"❌ Error loading subscription information: {e}")
        st.info("💡 Contact an administrator for assistance.")

def display_activity_tab(user_id: int):
    """Display user activity and history."""
    st.markdown("### 📈 Activity & History")
    
    # Recent training activity
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Fixed query to use correct column name 'result' instead of 'is_correct'
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as moves,
                   SUM(CASE WHEN result = 'correct' THEN 1 ELSE 0 END) as correct_moves
            FROM user_moves 
            WHERE user_id = ? AND timestamp > ?
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
        ''', (user_id, (datetime.now() - timedelta(days=30)).isoformat()))
        
        training_data = cursor.fetchall()
        
        if training_data:
            st.markdown("#### 🎯 Training Activity (Last 30 Days)")
            
            df_training = pd.DataFrame(training_data, columns=['Date', 'Moves', 'Correct Moves'])
            df_training['Accuracy'] = (df_training['Correct Moves'] / df_training['Moves'] * 100).round(1)
            
            # Chart
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.line_chart(df_training.set_index('Date')['Moves'])
                st.caption("Daily training moves")
            
            with chart_col2:
                st.line_chart(df_training.set_index('Date')['Accuracy'])
                st.caption("Daily accuracy %")
            
            # Recent sessions table
            with st.expander("📊 Detailed Training History"):
                st.dataframe(df_training, use_container_width=True, hide_index=True)
        else:
            st.info("📊 No training activity in the last 30 days")
        
        # Recent sessions
        cursor.execute('''
            SELECT session_id, start_time, end_time, total_moves, correct_moves
            FROM training_sessions
            WHERE user_id = ?
            ORDER BY start_time DESC
            LIMIT 10
        ''', (user_id,))
        
        sessions_data = cursor.fetchall()
        
        if sessions_data:
            st.markdown("#### 🎮 Recent Training Sessions")
            
            for session in sessions_data:
                session_id, start_time, end_time, total_moves, correct_moves = session
                
                if start_time:
                    start_dt = datetime.fromisoformat(start_time)
                    
                    accuracy = (correct_moves / total_moves * 100) if total_moves > 0 else 0
                    
                    with st.expander(f"Session {session_id} - {start_dt.strftime('%m/%d/%Y %I:%M %p')}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Moves", total_moves or 0)
                        
                        with col2:
                            st.metric("Correct Moves", correct_moves or 0)
                        
                        with col3:
                            st.metric("Accuracy", f"{accuracy:.1f}%")
                        
                        if end_time:
                            end_dt = datetime.fromisoformat(end_time)
                            duration = end_dt - start_dt
                            st.caption(f"Duration: {duration}")
        else:
            st.info("🎮 No training sessions recorded yet")
    
    except Exception as e:
        st.error(f"Error loading activity data: {e}")
        # Add debug info for admin users
        if st.session_state.get('user_info', {}).get('is_admin'):
            st.code(f"Debug info: {str(e)}")
    
    finally:
        conn.close()

def display_account_settings_tab(user_id: int, user_info: Dict):
    """Display account settings and management options."""
    st.markdown("### ⚙️ Account Settings")
    
    # Profile information
    st.markdown("#### 👤 Profile Information")
    
    with st.form("profile_form"):
        current_name = user_info.get('full_name', '')
        new_name = st.text_input("Full Name", value=current_name)
        
        # Display email (read-only)
        st.text_input("Email Address", value=user_info.get('email', ''), disabled=True)
        
        if st.form_submit_button("💾 Update Profile"):
            if update_user_profile(user_id, new_name):
                st.success("✅ Profile updated successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to update profile")
    
    st.markdown("---")
    
    # Password change
    st.markdown("#### 🔐 Change Password")
    
    with st.form("password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("🔑 Change Password"):
            if not all([current_password, new_password, confirm_password]):
                st.error("❌ Please fill in all password fields")
            elif new_password != confirm_password:
                st.error("❌ New passwords do not match")
            elif len(new_password) < 6:
                st.error("❌ New password must be at least 6 characters")
            else:
                if update_user_password(user_id, current_password, new_password):
                    st.success("✅ Password changed successfully!")
                else:
                    st.error("❌ Failed to change password. Check your current password.")
    
    st.markdown("---")
    
    # Training preferences (consolidated here)
    display_training_preferences(user_id)
    
    st.markdown("---")
    
    # Account information
    st.markdown("#### ℹ️ Account Information")
    
    # Use simple dict for dataframe to avoid PyArrow issues
    info_data = []
    info_data.append(['User ID', str(user_info.get('id', 'N/A'))])
    info_data.append(['Email', str(user_info.get('email', 'N/A'))])
    info_data.append(['Account Type', 'Admin' if user_info.get('is_admin') else 'Regular User'])
    info_data.append(['Verification Status', str(user_info.get('verification_status', 'Unknown')).title()])
    info_data.append(['Created', str(user_info.get('created_at', 'N/A'))])
    info_data.append(['Last Login', str(user_info.get('last_login', 'Never'))])
    
    df_info = pd.DataFrame(info_data, columns=['Field', 'Value'])
    st.dataframe(df_info, use_container_width=True, hide_index=True)
    
    # Export data
    st.markdown("---")
    st.markdown("#### 📥 Export Your Data")
    
    if st.button("📄 Export Personal Data", use_container_width=True):
        export_user_data(user_id)

def display_training_preferences(user_id: int):
    """Display training preferences settings."""
    st.markdown("#### 🎯 Training Preferences")
    
    # Get current settings
    from auth import get_user_settings, update_user_settings
    current_settings = get_user_settings(user_id)
    
    with st.form("training_preferences_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            random_positions = st.checkbox(
                "Random position selection",
                value=current_settings.get('random_positions', True),
                help="Select positions randomly instead of sequentially"
            )
            
            top_n_threshold = st.slider(
                "Top N moves threshold",
                min_value=1,
                max_value=10,
                value=current_settings.get('top_n_threshold', 3),
                help="Consider moves within top N as correct"
            )
        
        with col2:
            score_difference_threshold = st.slider(
                "Score difference threshold (centipawns)",
                min_value=5,
                max_value=50,
                value=current_settings.get('score_difference_threshold', 10),
                help="Maximum centipawn loss for a move to be considered correct"
            )
            
            theme = st.selectbox(
                "Board theme",
                ["default", "dark", "blue", "green", "wood"],
                index=["default", "dark", "blue", "green", "wood"].index(current_settings.get('theme', 'default')),
                help="Visual theme for the chess board"
            )
        
        # Save settings
        if st.form_submit_button("💾 Save Training Preferences", use_container_width=True):
            new_settings = {
                'random_positions': random_positions,
                'top_n_threshold': top_n_threshold,
                'score_difference_threshold': score_difference_threshold,
                'theme': theme
            }
            
            if update_user_settings(user_id, new_settings):
                st.success("✅ Training preferences saved successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to save training preferences")

def request_verification_review(user_id: int):
    """Request a verification review."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if there's already a pending request
        cursor.execute('''
            SELECT id FROM user_verification_requests 
            WHERE user_id = ? AND status = 'pending'
        ''', (user_id,))
        
        if cursor.fetchone():
            st.warning("⚠️ You already have a pending verification request")
            return
        
        # Create new verification request
        cursor.execute('''
            INSERT INTO user_verification_requests (
                user_id, request_type, request_data
            ) VALUES (?, ?, ?)
        ''', (user_id, 'review_request', '{"type": "user_initiated"}'))
        
        conn.commit()
        st.success("✅ Verification review requested! An admin will review your account soon.")
        
    except Exception as e:
        st.error(f"❌ Failed to request verification review: {e}")
    finally:
        conn.close()

def update_user_profile(user_id: int, full_name: str) -> bool:
    """Update user profile information."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE users 
            SET full_name = ?
            WHERE id = ?
        ''', (full_name, user_id))
        
        conn.commit()
        
        # Update session state
        if 'user_info' in st.session_state:
            st.session_state.user_info['full_name'] = full_name
        
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return False
    finally:
        conn.close()

def export_user_data(user_id: int):
    """Export user's personal data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Collect user data from various tables
        user_data = {}
        
        # User info
        cursor.execute('''
            SELECT email, full_name, created_at, last_login, verification_status
            FROM users WHERE id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        if result:
            user_data['profile'] = dict(zip(['email', 'full_name', 'created_at', 'last_login', 'verification_status'], result))
        
        # Training moves - fixed query
        cursor.execute('''
            SELECT position_id, move_id, result, timestamp, time_taken
            FROM user_moves WHERE user_id = ?
            ORDER BY timestamp DESC
        ''', (user_id,))
        user_data['training_moves'] = [dict(zip(['position_id', 'move_id', 'result', 'timestamp', 'time_taken'], row)) for row in cursor.fetchall()]
        
        # Subscription info
        cursor.execute('''
            SELECT subscription_type, position_limit, analysis_limit, game_upload_limit,
                   positions_used, analyses_used, games_uploaded
            FROM user_subscriptions WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        if result:
            user_data['subscription'] = dict(zip(['subscription_type', 'position_limit', 'analysis_limit', 'game_upload_limit', 'positions_used', 'analyses_used', 'games_uploaded'], result))
        
        # Create downloadable JSON
        import json
        json_data = json.dumps(user_data, indent=2, default=str)
        
        st.download_button(
            label="⬇️ Download Personal Data (JSON)",
            data=json_data,
            file_name=f"kuikma_user_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
        
        st.success("✅ Personal data export prepared!")
        
    except Exception as e:
        st.error(f"❌ Failed to export personal data: {e}")
    finally:
        conn.close()

# Make the main function available for import
__all__ = ['display_user_dashboard']
