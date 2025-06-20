# admin_panel.py - Comprehensive Admin Panel for User Management
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Import enhanced modules
from database import (get_db_connection, get_user_verification_stats, 
                     get_subscription_usage_stats, log_admin_action,
                     database_sanity_check, optimize_database, )
from auth import (verify_user, get_users_for_verification, update_user_subscription,
                 get_user_subscription, check_user_access)
from config import config

def display_enhanced_admin_panel():
    """Enhanced admin panel with comprehensive user management."""
    
    # Check admin access
    if not st.session_state.get('user_id'):
        st.error("❌ Please login first")
        return
    
    if not check_user_access(st.session_state['user_id'], 'admin_panel'):
        st.error("❌ Admin access required")
        return
    
    st.markdown("# 👑 Enhanced Admin Panel")
    st.markdown("---")
    
    # Admin navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 User Verification", 
        "👥 User Management", 
        "💳 Subscription Management",
        "🔧 Feature Access Control",
        "📊 Analytics & Reports",
        "🛠️ Maintenance"
    ])
    
    with tab1:
        display_user_verification_panel()
    
    with tab2:
        display_user_management_panel()
    
    with tab3:
        display_subscription_management_panel()
    
    with tab4:
        display_feature_access_panel()
    
    with tab5:
        display_analytics_panel()

    with tab6:
        display_maintenance_panel()

def display_user_verification_panel():
    """User verification management panel."""
    st.markdown("### 📋 User Verification Management")
    
    # Get verification statistics
    stats = get_user_verification_stats()
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", stats.get('total_users', 0))
    
    with col2:
        st.metric("Verified Users", stats.get('verified_users', 0))
    
    with col3:
        st.metric("Pending Verification", stats.get('pending_verification', 0))
    
    with col4:
        st.metric("Recent Registrations", stats.get('recent_registrations', 0))
    
    st.markdown("---")
    
    # Users pending verification
    pending_users = get_users_for_verification()
    
    if pending_users:
        st.markdown("#### 🔄 Users Pending Verification")
        
        for user in pending_users:
            with st.expander(f"📧 {user['email']} - {user.get('full_name', 'No name provided')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Email:** {user['email']}")
                    st.markdown(f"**Full Name:** {user.get('full_name', 'Not provided')}")
                    st.markdown(f"**Registration Date:** {user['created_at']}")
                    
                    if user.get('request_data'):
                        st.markdown("**Additional Info:**")
                        st.json(user['request_data'])
                
                with col2:
                    admin_notes = st.text_area(
                        "Admin Notes",
                        key=f"notes_{user['id']}",
                        placeholder="Optional notes about verification decision..."
                    )
                    
                    col_approve, col_reject = st.columns(2)
                    
                    with col_approve:
                        if st.button(
                            "✅ Approve", 
                            key=f"approve_{user['id']}",
                            use_container_width=True,
                            type="primary"
                        ):
                            if verify_user(
                                user['id'], 
                                st.session_state['user_id'], 
                                approved=True, 
                                admin_notes=admin_notes
                            ):
                                st.success(f"✅ User {user['email']} approved!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to approve user")
                    
                    with col_reject:
                        if st.button(
                            "❌ Reject", 
                            key=f"reject_{user['id']}",
                            use_container_width=True
                        ):
                            if verify_user(
                                user['id'], 
                                st.session_state['user_id'], 
                                approved=False, 
                                admin_notes=admin_notes
                            ):
                                st.success(f"❌ User {user['email']} rejected!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to reject user")
    else:
        st.info("🎉 No users pending verification!")

def display_user_management_panel():
    """Comprehensive user management panel."""
    st.markdown("### 👥 User Management")
    
    # Get all users
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.email, u.full_name, u.created_at, u.last_login, 
               u.is_admin, u.is_verified, u.verification_status, u.account_status,
               s.subscription_type, s.position_limit, s.positions_used
        FROM users u
        LEFT JOIN user_subscriptions s ON u.id = s.user_id
        ORDER BY u.created_at DESC
    ''')
    users = cursor.fetchall()
    conn.close()
    
    if users:
        # Create DataFrame for display
        df = pd.DataFrame(users, columns=[
            'ID', 'Email', 'Full Name', 'Created', 'Last Login',
            'Admin', 'Verified', 'Status', 'Account Status',
            'Subscription', 'Position Limit', 'Positions Used'
        ])
        
        # Add filters
        st.markdown("#### 🔍 Filters")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            status_filter = st.selectbox(
                "Verification Status",
                ["All", "pending", "approved", "rejected"]
            )
        
        with filter_col2:
            admin_filter = st.selectbox(
                "User Type",
                ["All", "Admin", "Regular Users"]
            )
        
        with filter_col3:
            account_filter = st.selectbox(
                "Account Status",
                ["All", "active", "inactive", "suspended"]
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['Status'] == status_filter]
        
        if admin_filter == "Admin":
            filtered_df = filtered_df[filtered_df['Admin'] == True]
        elif admin_filter == "Regular Users":
            filtered_df = filtered_df[filtered_df['Admin'] == False]
        
        if account_filter != "All":
            filtered_df = filtered_df[filtered_df['Account Status'] == account_filter]
        
        # Display filtered results
        st.markdown(f"#### 📊 Users ({len(filtered_df)} of {len(df)})")
        st.dataframe(filtered_df, use_container_width=True)
        
        # User actions
        st.markdown("#### ⚙️ User Actions")
        
        selected_user_id = st.selectbox(
            "Select User for Actions",
            options=[row[0] for row in users],
            format_func=lambda x: f"ID {x}: {next(row[1] for row in users if row[0] == x)}"
        )
        
        if selected_user_id:
            selected_user = next(row for row in users if row[0] == selected_user_id)
            
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button("🔄 Toggle Admin Status", use_container_width=True):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        'UPDATE users SET is_admin = NOT is_admin WHERE id = ?',
                        (selected_user_id,)
                    )
                    conn.commit()
                    conn.close()
                    
                    # Log action
                    log_admin_action(
                        st.session_state['user_id'],
                        'toggle_admin_status',
                        selected_user_id,
                        'user_account'
                    )
                    
                    st.success("✅ Admin status updated!")
                    st.rerun()
            
            with action_col2:
                new_status = st.selectbox(
                    "Change Account Status",
                    ["active", "inactive", "suspended"],
                    index=["active", "inactive", "suspended"].index(selected_user[8])
                )
                
                if st.button("💾 Update Status", use_container_width=True):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        'UPDATE users SET account_status = ? WHERE id = ?',
                        (new_status, selected_user_id)
                    )
                    conn.commit()
                    conn.close()
                    
                    log_admin_action(
                        st.session_state['user_id'],
                        'update_account_status',
                        selected_user_id,
                        'user_account',
                        {'new_status': new_status}
                    )
                    
                    st.success("✅ Account status updated!")
                    st.rerun()
            
            with action_col3:
                if not selected_user[5]:  # Not admin
                    if st.button("🗑️ Delete User", use_container_width=True, type="primary"):
                        if st.checkbox(f"Confirm deletion of {selected_user[1]}", key="confirm_delete"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            
                            # Delete user and cascade
                            tables_to_clean = [
                                'user_verification_requests',
                                'user_subscriptions',
                                'user_feature_access',
                                'user_sessions',
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
                                cursor.execute(f'DELETE FROM {table} WHERE user_id = ?', (selected_user_id,))
                            
                            cursor.execute('DELETE FROM users WHERE id = ?', (selected_user_id,))
                            conn.commit()
                            conn.close()
                            
                            log_admin_action(
                                st.session_state['user_id'],
                                'delete_user',
                                selected_user_id,
                                'user_account'
                            )
                            
                            st.success("✅ User deleted!")
                            st.rerun()

def display_subscription_management_panel():
    """Subscription and limits management panel."""
    st.markdown("### 💳 Subscription Management")
    
    # Get subscription statistics
    stats = get_subscription_usage_stats()
    
    # Display statistics
    if stats.get('average_usage'):
        st.markdown("#### 📊 Usage Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Avg Positions Used", 
                stats['average_usage']['positions']
            )
        
        with col2:
            st.metric(
                "Avg Analyses Used", 
                stats['average_usage']['analyses']
            )
        
        with col3:
            st.metric(
                "Avg Games Uploaded", 
                stats['average_usage']['games']
            )
        
        # Alert metrics
        alert_col1, alert_col2 = st.columns(2)
        
        with alert_col1:
            st.metric(
                "Near Position Limit", 
                stats.get('users_near_position_limit', 0),
                help="Users using >90% of position limit"
            )
        
        with alert_col2:
            st.metric(
                "Near Analysis Limit", 
                stats.get('users_near_analysis_limit', 0),
                help="Users using >90% of analysis limit"
            )
    
    st.markdown("---")
    
    # Individual user subscription management
    st.markdown("#### 👤 Individual Subscription Management")
    
    # Get users with subscriptions
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.email, u.full_name, s.subscription_type,
               s.position_limit, s.positions_used,
               s.analysis_limit, s.analyses_used,
               s.game_upload_limit, s.games_uploaded
        FROM users u
        JOIN user_subscriptions s ON u.id = s.user_id
        WHERE u.is_admin = FALSE
        ORDER BY u.email
    ''')
    users_with_subs = cursor.fetchall()
    conn.close()
    
    if users_with_subs:
        selected_sub_user = st.selectbox(
            "Select User",
            options=[row[0] for row in users_with_subs],
            format_func=lambda x: f"{next(row[1] for row in users_with_subs if row[0] == x)} - {next(row[3] for row in users_with_subs if row[0] == x)}"
        )
        
        if selected_sub_user:
            user_data = next(row for row in users_with_subs if row[0] == selected_sub_user)
            
            st.markdown(f"**Managing subscription for:** {user_data[1]}")
            
            # Current usage display
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Positions",
                    f"{user_data[5]}/{user_data[4]}",
                    delta=f"{user_data[4] - user_data[5]} remaining"
                )
            
            with col2:
                st.metric(
                    "Analyses", 
                    f"{user_data[7]}/{user_data[6]}",
                    delta=f"{user_data[6] - user_data[7]} remaining"
                )
            
            with col3:
                st.metric(
                    "Games",
                    f"{user_data[9]}/{user_data[8]}",
                    delta=f"{user_data[8] - user_data[9]} remaining"
                )
            
            # Update subscription form
            with st.form(f"update_subscription_{selected_sub_user}"):
                st.markdown("#### ✏️ Update Limits")
                
                form_col1, form_col2 = st.columns(2)
                
                with form_col1:
                    new_subscription_type = st.selectbox(
                        "Subscription Type",
                        ["basic", "premium", "unlimited", "admin"],
                        index=["basic", "premium", "unlimited", "admin"].index(user_data[3])
                    )
                    
                    new_position_limit = st.number_input(
                        "Position Limit",
                        min_value=0,
                        max_value=999999,
                        value=user_data[4],
                        step=50
                    )
                    
                    new_analysis_limit = st.number_input(
                        "Analysis Limit",
                        min_value=0,
                        max_value=999999,
                        value=user_data[6],
                        step=25
                    )
                
                with form_col2:
                    new_game_limit = st.number_input(
                        "Game Upload Limit",
                        min_value=0,
                        max_value=999999,
                        value=user_data[8],
                        step=10
                    )
                    
                    reset_usage = st.checkbox(
                        "Reset Usage Counters",
                        help="Reset positions_used, analyses_used, games_uploaded to 0"
                    )
                
                if st.form_submit_button("💾 Update Subscription", use_container_width=True):
                    update_data = {
                        'subscription_type': new_subscription_type,
                        'position_limit': new_position_limit,
                        'analysis_limit': new_analysis_limit,
                        'game_upload_limit': new_game_limit
                    }
                    
                    if reset_usage:
                        update_data.update({
                            'positions_used': 0,
                            'analyses_used': 0,
                            'games_uploaded': 0
                        })
                    
                    if update_user_subscription(
                        selected_sub_user,
                        st.session_state['user_id'],
                        **update_data
                    ):
                        st.success("✅ Subscription updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update subscription")

def display_feature_access_panel():
    """Feature access control panel."""
    st.markdown("### 🔧 Feature Access Control")
    
    # Available features
    all_features = [
        'training', 'analysis', 'insights', 'game_analysis',
        'spatial_analysis', 'upload_games', 'save_positions',
        'export_data', 'view_history'
    ]
    
    # Get users
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, email, full_name, is_verified, verification_status
        FROM users 
        WHERE is_admin = FALSE
        ORDER BY email
    ''')
    users = cursor.fetchall()
    
    # Feature access configuration
    st.markdown("#### 🎛️ Global Feature Configuration")
    
    with st.expander("Configure Feature Access Rules"):
        st.markdown("**Default Permissions by User Type:**")
        
        permissions = config.get_user_permissions('verified_user')
        
        for feature in all_features:
            current_access = permissions.get(feature, False)
            st.checkbox(
                f"{feature.replace('_', ' ').title()}",
                value=current_access,
                key=f"global_{feature}",
                disabled=True,
                help="Global permissions are configured in config.py"
            )
    
    st.markdown("---")
    
    # Individual user feature access
    st.markdown("#### 👤 Individual Feature Access")
    
    if users:
        selected_feature_user = st.selectbox(
            "Select User for Feature Management",
            options=[row[0] for row in users],
            format_func=lambda x: f"{next(row[1] for row in users if row[0] == x)} - {'Verified' if next(row[3] for row in users if row[0] == x) else 'Unverified'}"
        )
        
        if selected_feature_user:
            user_info = next(row for row in users if row[0] == selected_feature_user)
            
            st.markdown(f"**Managing features for:** {user_info[1]} ({user_info[2] or 'No name'})")
            
            # Get current custom feature access
            cursor.execute('''
                SELECT feature_name, access_granted, expires_at, notes
                FROM user_feature_access 
                WHERE user_id = ?
            ''', (selected_feature_user,))
            
            custom_access = dict(cursor.fetchall())
            
            # Feature management form
            with st.form(f"feature_access_{selected_feature_user}"):
                st.markdown("#### 🎯 Custom Feature Access")
                
                feature_col1, feature_col2 = st.columns(2)
                
                feature_updates = {}
                
                for i, feature in enumerate(all_features):
                    col = feature_col1 if i % 2 == 0 else feature_col2
                    
                    with col:
                        current_custom = custom_access.get(feature, (False, None, None))
                        
                        grant_access = st.checkbox(
                            f"{feature.replace('_', ' ').title()}",
                            value=current_custom[0],
                            key=f"custom_{feature}_{selected_feature_user}"
                        )
                        
                        feature_updates[feature] = grant_access
                
                # Expiration date for access
                expires_at = st.date_input(
                    "Access Expires On (optional)",
                    help="Leave empty for permanent access"
                )
                
                access_notes = st.text_area(
                    "Notes",
                    placeholder="Reason for custom access..."
                )
                
                if st.form_submit_button("💾 Update Feature Access", use_container_width=True):
                    success_count = 0
                    
                    for feature, granted in feature_updates.items():
                        # Delete existing record
                        cursor.execute('''
                            DELETE FROM user_feature_access 
                            WHERE user_id = ? AND feature_name = ?
                        ''', (selected_feature_user, feature))
                        
                        # Insert new record if access granted
                        if granted:
                            cursor.execute('''
                                INSERT INTO user_feature_access (
                                    user_id, feature_name, access_granted, granted_at,
                                    granted_by, expires_at, notes
                                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                selected_feature_user, feature, True,
                                datetime.now().isoformat(),
                                st.session_state['user_id'],
                                expires_at.isoformat() if expires_at else None,
                                access_notes
                            ))
                            success_count += 1
                    
                    conn.commit()
                    
                    # Log action
                    log_admin_action(
                        st.session_state['user_id'],
                        'update_feature_access',
                        selected_feature_user,
                        'user_features',
                        {
                            'features_updated': list(feature_updates.keys()),
                            'grants_made': success_count
                        }
                    )
                    
                    st.success(f"✅ Updated feature access for {user_info[1]}!")
                    st.rerun()
    
    conn.close()

def display_analytics_panel():
    """Analytics and reporting panel."""
    st.markdown("### 📊 Analytics & Reports")
    
    # Time range selector
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date() - timedelta(days=30)
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date()
        )
    
    # Generate reports
    if st.button("📈 Generate Reports", use_container_width=True):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # User registration trends
        st.markdown("#### 📈 User Registration Trends")
        
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as registrations
            FROM users 
            WHERE DATE(created_at) BETWEEN ? AND ?
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (start_date, end_date))
        
        registration_data = cursor.fetchall()
        
        if registration_data:
            df_reg = pd.DataFrame(registration_data, columns=['Date', 'Registrations'])
            st.line_chart(df_reg.set_index('Date'))
        else:
            st.info("No registration data in selected period")
        
        # Feature usage analysis
        st.markdown("#### 🎯 Feature Usage Analysis")
        
        cursor.execute('''
            SELECT feature_name, COUNT(*) as grants
            FROM user_feature_access
            WHERE granted_at BETWEEN ? AND ?
            GROUP BY feature_name
            ORDER BY grants DESC
        ''', (start_date, end_date))
        
        feature_data = cursor.fetchall()
        
        if feature_data:
            df_features = pd.DataFrame(feature_data, columns=['Feature', 'Grants'])
            st.bar_chart(df_features.set_index('Feature'))
        else:
            st.info("No feature access data in selected period")
        
        # Admin activity log
        st.markdown("#### 👑 Admin Activity Log")
        
        cursor.execute('''
            SELECT a.timestamp, u.email as admin_email, a.action, 
                   target_user.email as target_email, a.target_resource
            FROM admin_audit_log a
            JOIN users u ON a.admin_user_id = u.id
            LEFT JOIN users target_user ON a.target_user_id = target_user.id
            WHERE DATE(a.timestamp) BETWEEN ? AND ?
            ORDER BY a.timestamp DESC
            LIMIT 50
        ''', (start_date, end_date))
        
        admin_activity = cursor.fetchall()
        
        if admin_activity:
            df_activity = pd.DataFrame(admin_activity, columns=[
                'Timestamp', 'Admin', 'Action', 'Target User', 'Resource'
            ])
            st.dataframe(df_activity, use_container_width=True)
        else:
            st.info("No admin activity in selected period")
        
        conn.close()

def display_maintenance_panel():
    """Admin-only functionality panel."""
    if st.session_state.get('user_id'):
        # Check if user is admin
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (st.session_state['user_id'],))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
            st.markdown("### 🔐 Admin Panel")
            
            admin_tab1, admin_tab2, admin_tab3 = st.tabs(["👥 User Management", "📊 System Stats", "🔧 Maintenance"])
            
            with admin_tab1:
                st.markdown("#### User Management")
                
                # Get all users
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT id, email, created_at, last_login, is_admin FROM users ORDER BY created_at DESC')
                users = cursor.fetchall()
                conn.close()
                
                if users:
                    users_df = pd.DataFrame(users, columns=['ID', 'Email', 'Created', 'Last Login', 'Admin'])
                    st.dataframe(users_df, use_container_width=True)
                    
                    # User actions
                    user_id_to_modify = st.selectbox("Select user to modify:", [u[0] for u in users], format_func=lambda x: f"ID {x}: {next(u[1] for u in users if u[0] == x)}")
                    
                    action_col1, action_col2 = st.columns(2)
                    
                    with action_col1:
                        if st.button("🛡️ Toggle Admin Status"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute('UPDATE users SET is_admin = NOT is_admin WHERE id = ?', (user_id_to_modify,))
                            conn.commit()
                            conn.close()
                            st.success("✅ Admin status updated!")
                            st.rerun()
                    
                    with action_col2:
                        if st.button("🗑️ Delete User", type="primary"):
                            if st.session_state.get('confirm_user_delete'):
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute('DELETE FROM users WHERE id = ?', (user_id_to_modify,))
                                conn.commit()
                                conn.close()
                                st.success("✅ User deleted!")
                                st.session_state.confirm_user_delete = False
                                st.rerun()
                            else:
                                st.session_state.confirm_user_delete = True
                                st.warning("Click again to confirm deletion")
                
                else:
                    st.info("No users found")
            
            with admin_tab2:
                st.markdown("#### System Statistics")
                
                # Get comprehensive stats
                sanity_result = database_sanity_check()
                stats = sanity_result.get('stats', {})
                
                # Display stats in cards
                stat_cols = st.columns(3)
                
                for i, (table, count) in enumerate(stats.items()):
                    with stat_cols[i % 3]:
                        st.metric(table.replace('_', ' ').title(), count)
                
                # Performance metrics
                st.markdown("##### 📈 Performance Metrics")
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                try:
                    # Most active users
                    cursor.execute('''
                        SELECT u.email, COUNT(um.id) as move_count 
                        FROM users u 
                        LEFT JOIN user_moves um ON u.id = um.user_id 
                        GROUP BY u.id 
                        ORDER BY move_count DESC 
                        LIMIT 5
                    ''')
                    active_users = cursor.fetchall()
                    
                    if active_users:
                        st.markdown("**Most Active Users:**")
                        for email, count in active_users:
                            st.write(f"• {email}: {count} moves")
                    
                    # Training accuracy
                    cursor.execute('''
                        SELECT AVG(CASE WHEN result = 'correct' THEN 1.0 ELSE 0.0 END) * 100 as accuracy
                        FROM user_moves
                    ''')
                    accuracy = cursor.fetchone()[0]
                    
                    if accuracy:
                        st.metric("Overall Training Accuracy", f"{accuracy:.1f}%")
                
                except Exception as e:
                    st.error(f"Error loading performance metrics: {e}")
                finally:
                    conn.close()
            
            with admin_tab3:
                st.markdown("#### System Maintenance")
                
                # System actions
                maint_col1, maint_col2 = st.columns(2)
                
                with maint_col1:
                    if st.button("🧹 Clean Orphaned Records"):
                        with st.spinner("Cleaning orphaned records..."):
                            # Clean orphaned moves
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute('''
                                DELETE FROM moves WHERE position_id NOT IN (SELECT id FROM positions)
                            ''')
                            orphaned_moves = cursor.rowcount
                            
                            # Clean orphaned user_moves
                            cursor.execute('''
                                DELETE FROM user_moves WHERE user_id NOT IN (SELECT id FROM users)
                            ''')
                            orphaned_user_moves = cursor.rowcount
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Cleaned {orphaned_moves} orphaned moves and {orphaned_user_moves} orphaned user moves")
                
                with maint_col2:
                    if st.button("📊 Rebuild Indexes"):
                        with st.spinner("Rebuilding database indexes..."):
                            if optimize_database():
                                st.success("✅ Indexes rebuilt successfully!")
                            else:
                                st.error("❌ Index rebuild failed")
            
            st.markdown('</div>', unsafe_allow_html=True)

# Make function available for import
__all__ = ['display_enhanced_admin_panel']
