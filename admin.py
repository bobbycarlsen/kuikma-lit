# admin.py - Unified Admin Interface
"""
Consolidated admin interface combining all admin features under one umbrella.
Includes user management, database operations, analytics, and system maintenance.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Import enhanced modules
from database import (get_db_connection, get_user_verification_stats, 
                     get_subscription_usage_stats, log_admin_action,
                     database_sanity_check, optimize_database, get_all_tables,
                     get_table_info, get_table_data, update_table_row, delete_table_row,
                     reset_database, export_database_with_schema)
from auth import (verify_user, get_users_for_verification, update_user_subscription,
                 get_user_subscription, check_user_access, get_user_info, get_user_statistics)
from config import config
import pgn_loader
from jsonl_processor import JSONLProcessor
import database

def display_consolidated_admin():
    """Main consolidated admin interface."""
    
    # Check admin access
    if not st.session_state.get('user_id'):
        st.error("❌ Please login first")
        return
    
    if not check_user_access(st.session_state['user_id'], 'admin_panel'):
        st.error("❌ Admin access required")
        return
    
    st.markdown("# 👑 Admin Console")
    st.markdown("**Unified administration interface for Kuikma Chess Engine**")
    st.markdown("---")
    
    # Main admin tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "👥 User Management",
        "💳 Subscriptions", 
        "🗄️ Database",
        "📤 Data Import/Export",
        "📊 Analytics",
        "🔧 System Settings",
        "🛠️ Maintenance"
    ])
    
    with tab1:
        display_user_management_section()
    
    with tab2:
        display_subscription_management_section()
    
    with tab3:
        display_database_management_section()
    
    with tab4:
        display_data_import_export_section()
    
    with tab5:
        display_analytics_section()
    
    with tab6:
        display_system_settings_section()
    
    with tab7:
        display_maintenance_section()

def display_user_management_section():
    """Comprehensive user management section."""
    st.markdown("### 👥 User Management")
    
    # User verification subsection
    st.markdown("#### 📋 User Verification")
    
    # Get verification statistics
    try:
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
        
        # Users pending verification
        pending_users = get_users_for_verification()
        
        if pending_users:
            st.markdown("##### 🔄 Users Pending Verification")
            
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
    
    except Exception as e:
        st.error(f"Error loading verification data: {e}")
    
    st.markdown("---")
    
    # User management subsection
    st.markdown("#### 👥 All Users")
    
    try:
        # Get all users with proper error handling
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check what columns exist in users table
        cursor.execute("PRAGMA table_info(users)")
        columns_info = cursor.fetchall()
        available_columns = [col[1] for col in columns_info]
        
        # Build query based on available columns
        base_columns = ['id', 'email', 'created_at', 'last_login', 'is_admin']
        optional_columns = []
        
        if 'is_verified' in available_columns:
            optional_columns.append('is_verified')
        if 'verification_status' in available_columns:
            optional_columns.append('verification_status')
        if 'account_status' in available_columns:
            optional_columns.append('account_status')
        if 'full_name' in available_columns:
            optional_columns.append('full_name')
        
        all_columns = base_columns + optional_columns
        
        # Get users with subscription info
        cursor.execute(f'''
            SELECT u.{", u.".join(all_columns)},
                   s.subscription_type, s.position_limit, s.positions_used
            FROM users u
            LEFT JOIN user_subscriptions s ON u.id = s.user_id
            ORDER BY u.created_at DESC
        ''')
        users_raw = cursor.fetchall()
        conn.close()
        
        if users_raw:
            # Create structured user data for easier handling
            users_data = []
            for row in users_raw:
                user_dict = {
                    'id': row[0],
                    'email': row[1],
                    'created_at': row[2],
                    'last_login': row[3],
                    'is_admin': bool(row[4])
                }
                
                # Add optional columns safely
                col_index = 5
                for col in optional_columns:
                    if col_index < len(row):
                        if col == 'is_verified':
                            user_dict[col] = bool(row[col_index])
                        else:
                            user_dict[col] = row[col_index]
                        col_index += 1
                
                # Add subscription info
                if col_index < len(row):
                    user_dict['subscription_type'] = row[col_index]
                    user_dict['position_limit'] = row[col_index + 1] if col_index + 1 < len(row) else None
                    user_dict['positions_used'] = row[col_index + 2] if col_index + 2 < len(row) else None
                
                users_data.append(user_dict)
            
            # Create display DataFrame
            display_data = []
            for user in users_data:
                display_row = [
                    user['id'],
                    user['email'],
                    user['created_at'],
                    user['last_login'] or 'Never',
                    'Yes' if user['is_admin'] else 'No'
                ]
                
                # Add optional columns for display
                for col in optional_columns:
                    value = user.get(col)
                    if col == 'is_verified':
                        display_row.append('Yes' if value else 'No')
                    elif col == 'verification_status':
                        display_row.append((value or 'pending').title())
                    elif col == 'account_status':
                        display_row.append((value or 'active').title())
                    else:
                        display_row.append(value or '')
                
                # Add subscription info
                display_row.extend([
                    user.get('subscription_type', 'None'),
                    user.get('position_limit', 'N/A'),
                    user.get('positions_used', 'N/A')
                ])
                
                display_data.append(display_row)
            
            # Create column names for display
            display_columns = ['ID', 'Email', 'Created', 'Last Login', 'Admin'] + \
                            [col.replace('_', ' ').title() for col in optional_columns] + \
                            ['Subscription', 'Position Limit', 'Positions Used']
            
            df = pd.DataFrame(display_data, columns=display_columns)
            
            # Add filters
            st.markdown("##### 🔍 Filters")
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                if 'Verification Status' in df.columns:
                    status_filter = st.selectbox(
                        "Verification Status",
                        ["All", "Pending", "Approved", "Rejected"]
                    )
                else:
                    status_filter = "All"
            
            with filter_col2:
                admin_filter = st.selectbox(
                    "User Type",
                    ["All", "Admin", "Regular Users"]
                )
            
            with filter_col3:
                if 'Account Status' in df.columns:
                    account_filter = st.selectbox(
                        "Account Status",
                        ["All", "Active", "Inactive", "Suspended"]
                    )
                else:
                    account_filter = "All"
            
            # Apply filters
            filtered_df = df.copy()
            
            if status_filter != "All" and 'Verification Status' in df.columns:
                filtered_df = filtered_df[filtered_df['Verification Status'] == status_filter]
            
            if admin_filter == "Admin":
                filtered_df = filtered_df[filtered_df['Admin'] == 'Yes']
            elif admin_filter == "Regular Users":
                filtered_df = filtered_df[filtered_df['Admin'] == 'No']
            
            if account_filter != "All" and 'Account Status' in df.columns:
                filtered_df = filtered_df[filtered_df['Account Status'] == account_filter]
            
            # Display filtered results
            st.markdown(f"##### 📊 Users ({len(filtered_df)} of {len(df)})")
            st.dataframe(filtered_df, use_container_width=True)
            
            # User actions
            st.markdown("##### ⚙️ User Actions")
            
            if len(users_data) > 0:
                # Create user options with proper mapping
                user_options = []
                user_lookup = {}
                
                for user in users_data:
                    # Create display text
                    display_text = f"{user['email']}"
                    if user.get('full_name'):
                        display_text += f" ({user['full_name']})"
                    if user.get('is_admin'):
                        display_text += " [Admin]"
                    
                    user_options.append(display_text)
                    # Map display text to user data
                    user_lookup[display_text] = user
                
                selected_user_display = st.selectbox(
                    "Select User for Actions",
                    options=user_options
                )
                
                if selected_user_display and selected_user_display in user_lookup:
                    selected_user = user_lookup[selected_user_display]
                    selected_user_id = selected_user['id']
                    selected_user_email = selected_user['email']
                    
                    st.markdown(f"**Selected:** {selected_user_email}")
                    
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
                            
                            try:
                                log_admin_action(
                                    st.session_state['user_id'],
                                    'toggle_admin_status',
                                    selected_user_id,
                                    'user_account'
                                )
                            except Exception as log_error:
                                print(f"Error logging admin action: {log_error}")
                            
                            st.success("✅ Admin status updated!")
                            st.rerun()
                    
                    with action_col2:
                        if 'account_status' in available_columns:
                            current_status = selected_user.get('account_status', 'active') or 'active'
                            
                            new_status = st.selectbox(
                                "Change Account Status",
                                ["active", "inactive", "suspended"],
                                index=["active", "inactive", "suspended"].index(current_status),
                                key=f"status_select_{selected_user_id}"
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
                                
                                try:
                                    log_admin_action(
                                        st.session_state['user_id'],
                                        'update_account_status',
                                        selected_user_id,
                                        'user_account',
                                        {'new_status': new_status}
                                    )
                                except Exception as log_error:
                                    print(f"Error logging admin action: {log_error}")
                                
                                st.success("✅ Account status updated!")
                                st.rerun()
                        else:
                            st.info("Account status management not available")
                    
                    with action_col3:
                        # Don't allow deletion of admin users or self
                        is_admin = selected_user['is_admin']
                        is_self = selected_user_id == st.session_state['user_id']
                        
                        if not is_admin and not is_self:
                            if st.button("🗑️ Delete User", use_container_width=True, type="primary"):
                                # Use a unique key for the confirmation checkbox
                                confirm_key = f"confirm_delete_{selected_user_id}_{datetime.now().strftime('%H%M%S')}"
                                if st.checkbox(f"Confirm deletion of {selected_user_email}", key=confirm_key):
                                    perform_user_deletion(selected_user_id, selected_user_email)
                        else:
                            reason = "Cannot delete admin user" if is_admin else "Cannot delete yourself"
                            st.button(f"🚫 {reason}", disabled=True, use_container_width=True)
            else:
                st.info("No users found.")
                
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        if st.session_state.get('user_info', {}).get('is_admin'):
            with st.expander("🔧 Debug Information"):
                st.code(f"Error details: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

def perform_user_deletion(user_id: int, user_email: str):
    """Perform user deletion with all related data - ENHANCED VERSION."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete user and cascade - with better error handling
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
        
        deleted_counts = {}
        
        for table in tables_to_clean:
            try:
                # Check if table exists first
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if cursor.fetchone():
                    cursor.execute(f'DELETE FROM {table} WHERE user_id = ?', (user_id,))
                    deleted_counts[table] = cursor.rowcount
                else:
                    deleted_counts[table] = 0
            except Exception as table_error:
                print(f"Warning: Could not clean table {table}: {table_error}")
                deleted_counts[table] = 0
        
        # Finally delete the user
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        user_deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if user_deleted:
            try:
                log_admin_action(
                    st.session_state['user_id'],
                    'delete_user',
                    user_id,
                    'user_account',
                    {'email': user_email, 'deleted_records': deleted_counts}
                )
            except Exception as log_error:
                print(f"Warning: Could not log admin action: {log_error}")
            
            st.success(f"✅ User {user_email} deleted successfully!")
            
            # Show cleanup summary
            with st.expander("🧹 Cleanup Summary"):
                for table, count in deleted_counts.items():
                    if count > 0:
                        st.info(f"• {table}: {count} records deleted")
            
            st.rerun()
        else:
            st.error("❌ User not found or already deleted")
        
    except Exception as e:
        st.error(f"❌ Failed to delete user: {e}")
        # Show debug info for admin users
        if st.session_state.get('user_info', {}).get('is_admin'):
            with st.expander("🔧 Debug Information"):
                st.code(f"Error details: {str(e)}")

def display_subscription_management_section():
    """Subscription and limits management section."""
    st.markdown("### 💳 Subscription Management")
    
    try:
        # Get subscription statistics
        stats = get_subscription_usage_stats()
        
        if 'error' not in stats and stats.get('average_usage'):
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
            WHERE u.is_admin = 0
            ORDER BY u.email
        ''')
        users_with_subs = cursor.fetchall()
        conn.close()
        
        if users_with_subs:
            user_options = [f"{user[1]} - {user[3]}" for user in users_with_subs]
            selected_option = st.selectbox("Select User", options=user_options)
            
            if selected_option:
                selected_index = user_options.index(selected_option)
                user_data = users_with_subs[selected_index]
                
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
                with st.form(f"update_subscription_{user_data[0]}"):
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
                            user_data[0],
                            st.session_state['user_id'],
                            **update_data
                        ):
                            st.success("✅ Subscription updated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update subscription")
        else:
            st.info("No users with subscriptions found.")
            
    except Exception as e:
        st.error(f"Error in subscription management: {e}")

def display_database_management_section():
    """Database management section."""
    st.markdown("### 🗄️ Database Management")
    
    # Database overview
    try:
        sanity_result = database_sanity_check()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            health_color = "🟢" if sanity_result['healthy'] else "🔴"
            st.metric("Database Health", f"{health_color} {'Healthy' if sanity_result['healthy'] else 'Issues Found'}")
        
        with col2:
            st.metric("Total Tables", sanity_result.get('total_tables', 0))
        
        with col3:
            total_records = sum(sanity_result.get('stats', {}).values())
            st.metric("Total Records", total_records)
        
        # Display issues if any
        if not sanity_result['healthy']:
            st.error("🚨 Database Issues Detected:")
            for issue in sanity_result.get('issues', []):
                st.error(f"• {issue}")
        
        # Database Actions
        st.markdown("#### 🔧 Database Actions")
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        
        with action_col1:
            if st.button("🔄 Sanity Check", use_container_width=True):
                with st.spinner("Running sanity check..."):
                    result = database_sanity_check()
                    if result['healthy']:
                        st.success("✅ Database is healthy!")
                    else:
                        st.error("❌ Issues found in database")
                    st.rerun()
        
        with action_col2:
            if st.button("⚡ Optimize DB", use_container_width=True):
                with st.spinner("Optimizing database..."):
                    if optimize_database():
                        st.success("✅ Database optimized!")
                    else:
                        st.error("❌ Optimization failed")
        
        with action_col3:
            if st.button("💾 Export DB", use_container_width=True):
                with st.spinner("Exporting database..."):
                    export_path = export_database_with_schema()
                    if export_path:
                        with open(export_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ Download Export",
                                data=f.read(),
                                file_name=f"kuikma_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                                mime="application/octet-stream"
                            )
                        st.success("✅ Export ready!")
                    else:
                        st.error("❌ Export failed")
        
        with action_col4:
            if st.button("🗑️ Reset Options", use_container_width=True):
                st.session_state.show_reset_options = True
        
        # Reset Options
        if st.session_state.get('show_reset_options', False):
            st.markdown("#### ⚠️ Database Reset Options")
            
            reset_type = st.selectbox(
                "Choose reset type:",
                ["complete", "positions_only", "users_only", "games_only"],
                format_func=lambda x: {
                    "complete": "🔴 Complete Reset (ALL DATA)",
                    "positions_only": "🟠 Positions & Training Data Only", 
                    "users_only": "🟡 Users & Sessions Only",
                    "games_only": "🟢 Games Only"
                }[x]
            )
            
            st.warning(f"This will permanently delete data according to: {reset_type}")
            
            reset_col1, reset_col2 = st.columns(2)
            
            with reset_col1:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_reset_options = False
                    st.rerun()
            
            with reset_col2:
                confirmation = st.text_input("Type 'CONFIRM' to proceed:")
                if st.button("🗑️ RESET DATABASE", use_container_width=True, type="primary"):
                    if confirmation == "CONFIRM":
                        with st.spinner("Resetting database..."):
                            if reset_database(reset_type):
                                st.success(f"✅ Database reset completed: {reset_type}")
                                st.session_state.show_reset_options = False
                                st.rerun()
                            else:
                                st.error("❌ Reset failed")
                    else:
                        st.error("Please type 'CONFIRM' to proceed")

        # Table Management
        st.markdown("### 📊 Table Management")
        
        tables = database.get_all_tables()
        selected_table = st.selectbox("Select table to manage:", tables)
        
        if selected_table:
            # Get table info
            table_info = database.get_table_info(selected_table)
            
            if 'error' not in table_info:
                # Table statistics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"#### 📋 Table: `{selected_table}`")
                    st.metric("Total Rows", table_info['row_count'])
                
                with col2:
                    st.markdown("#### 🏗️ Schema")
                    columns_df = pd.DataFrame(
                        table_info['columns'], 
                        columns=['ID', 'Name', 'Type', 'NotNull', 'Default', 'PK']
                    )
                    st.dataframe(columns_df, use_container_width=True)
                
                # CRUD Operations
                st.markdown("#### 🔧 CRUD Operations")
                
                crud_tab1, crud_tab2, crud_tab3, crud_tab4 = st.tabs(["📖 Read", "✏️ Update", "🗑️ Delete", "➕ Advanced"])
                
                with crud_tab1:
                    # Read operations with pagination
                    st.markdown("##### 👀 View Data")
                    
                    page_size = st.selectbox("Records per page:", [10, 25, 50, 100], index=1)
                    
                    if table_info['row_count'] > 0:
                        max_pages = (table_info['row_count'] - 1) // page_size + 1
                        page = st.number_input("Page:", min_value=1, max_value=max_pages, value=1)
                        offset = (page - 1) * page_size
                        
                        table_data = database.get_table_data(selected_table, page_size, offset)
                        
                        if 'error' not in table_data:
                            st.dataframe(
                                pd.DataFrame(table_data['data']), 
                                use_container_width=True
                            )
                            
                            st.info(f"Showing {len(table_data['data'])} of {table_data['total_count']} records")
                        else:
                            st.error(f"Error loading data: {table_data['error']}")
                    else:
                        st.info("No data in this table")
                
                with crud_tab2:
                    # Update operations
                    st.markdown("##### ✏️ Update Record")
                    
                    if table_info['row_count'] > 0:
                        record_id = st.number_input("Record ID to update:", min_value=1, value=1)
                        
                        # Get current record
                        current_data = database.get_table_data(selected_table, 1, record_id - 1)
                        
                        if current_data.get('data'):
                            current_record = current_data['data'][0]
                            st.json(current_record)
                            
                            # Update form
                            with st.form(f"update_{selected_table}"):
                                st.markdown("**Update fields (JSON format):**")
                                update_data = st.text_area(
                                    "Field updates (key:value pairs):",
                                    placeholder='{"field_name": "new_value", "another_field": 123}'
                                )
                                
                                if st.form_submit_button("🔄 Update Record"):
                                    try:
                                        update_dict = json.loads(update_data)
                                        if database.update_table_row(selected_table, record_id, update_dict):
                                            st.success("✅ Record updated successfully!")
                                            st.rerun()
                                        else:
                                            st.error("❌ Update failed")
                                    except json.JSONDecodeError:
                                        st.error("❌ Invalid JSON format")
                        else:
                            st.warning("Record not found")
                    else:
                        st.info("No records to update")
                
                with crud_tab3:
                    # Delete operations
                    st.markdown("##### 🗑️ Delete Record")
                    
                    if table_info['row_count'] > 0:
                        delete_id = st.number_input("Record ID to delete:", min_value=1, value=1)
                        
                        st.warning("⚠️ This action cannot be undone!")
                        
                        if st.button("🗑️ Delete Record", type="primary"):
                            if database.delete_table_row(selected_table, delete_id):
                                st.success("✅ Record deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Delete failed or record not found")
                    else:
                        st.info("No records to delete")
                
                with crud_tab4:
                    # Advanced operations
                    st.markdown("##### 🔬 Advanced Operations")
                    
                    # Raw SQL query
                    with st.expander("🔍 Execute Raw SQL Query"):
                        st.warning("⚠️ Use with caution! This can modify data.")
                        
                        sql_query = st.text_area(
                            "SQL Query:",
                            placeholder=f"SELECT * FROM {selected_table} LIMIT 10;"
                        )
                        
                        if st.button("▶️ Execute Query"):
                            try:
                                conn = database.get_db_connection()
                                cursor = conn.cursor()
                                
                                cursor.execute(sql_query)
                                
                                if sql_query.strip().upper().startswith('SELECT'):
                                    results = cursor.fetchall()
                                    if results:
                                        df = pd.DataFrame([dict(row) for row in results])
                                        st.dataframe(df, use_container_width=True)
                                    else:
                                        st.info("No results returned")
                                else:
                                    conn.commit()
                                    st.success(f"✅ Query executed. Rows affected: {cursor.rowcount}")
                                
                                conn.close()
                                
                            except Exception as e:
                                st.error(f"❌ Query error: {e}")
                    
                    # Table statistics
                    if st.button("📊 Generate Table Statistics"):
                        conn = database.get_db_connection()
                        cursor = conn.cursor()
                        
                        try:
                            # Get column statistics
                            stats = {}
                            for col_info in table_info['columns']:
                                col_name = col_info[1]
                                col_type = col_info[2]
                                
                                if 'INTEGER' in col_type or 'REAL' in col_type:
                                    cursor.execute(f"SELECT MIN({col_name}), MAX({col_name}), AVG({col_name}) FROM {selected_table}")
                                    min_val, max_val, avg_val = cursor.fetchone()
                                    stats[col_name] = {
                                        'type': col_type,
                                        'min': min_val,
                                        'max': max_val, 
                                        'avg': round(avg_val, 2) if avg_val else None
                                    }
                                elif 'TEXT' in col_type:
                                    cursor.execute(f"SELECT COUNT(DISTINCT {col_name}) FROM {selected_table}")
                                    unique_count = cursor.fetchone()[0]
                                    stats[col_name] = {
                                        'type': col_type,
                                        'unique_values': unique_count
                                    }
                            
                            st.json(stats)
                            
                        except Exception as e:
                            st.error(f"Error generating statistics: {e}")
                        finally:
                            conn.close()
            
            else:
                st.error(f"Error accessing table: {table_info['error']}")
        
        st.markdown('</div>', unsafe_allow_html=True)


    except Exception as e:
        st.error(f"Error in database management: {e}")

def display_data_import_export_section():
    """Data import and export section."""
    st.markdown("### 📤 Data Import/Export")
    
    import_tab, export_tab = st.tabs(["📥 Import Data", "💾 Export/Backup"])
    
    with import_tab:
        st.markdown("#### 📥 Import Training Data")
        
        jsonl_tab, pgn_tab = st.tabs(["🧩 JSONL Positions", "♟️ PGN Games"])
        
        with jsonl_tab:
            st.markdown("Upload enhanced JSONL files with comprehensive position analysis.")
            uploaded_jsonl = st.file_uploader("Upload Enhanced JSONL File", type=['jsonl'], key="admin_jsonl")
            
            if uploaded_jsonl:
                file_content = uploaded_jsonl.read().decode('utf-8')
                
                # Preview first few lines
                lines = file_content.strip().split('\n')
                st.info(f"📊 Found {len(lines)} positions to process")
                
                if st.button("⬆️ Import Enhanced Positions", use_container_width=True):
                    with st.spinner("🔄 Processing enhanced JSONL data..."):
                        # Initialize enhanced processor
                        processor = JSONLProcessor()
                        
                        # Process and load positions
                        result = database.load_positions_from_enhanced_jsonl(processor, file_content)
                        
                        if result['success']:
                            st.success(f"✅ Successfully imported {result['positions_loaded']} positions!")
                            if result.get('positions_updated', 0) > 0:
                                st.info(f"ℹ️ Updated {result['positions_updated']} existing positions")
                            
                            # Display processor statistics
                            stats = result['processor_stats']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Processed", stats['processed_count'])
                            with col2:
                                st.metric("Valid", stats['valid_count'])
                            with col3:
                                st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
                            
                            if stats['errors']:
                                with st.expander("⚠️ Processing Errors"):
                                    for error in stats['errors']:
                                        st.error(error)
                        else:
                            st.error(f"❌ Import failed: {result['error']}")
        
        with pgn_tab:
            st.markdown("Upload PGN files containing complete chess games for analysis.")
            uploaded_pgn = st.file_uploader("Upload PGN File", type=['pgn'], key="admin_pgn")
            
            if uploaded_pgn:
                file_content = uploaded_pgn.read().decode('utf-8')
                stats = pgn_loader.get_file_statistics(file_content)
                
                if 'error' not in stats:
                    st.info(f"📊 Found {stats['total_games']} games")
                    
                    if st.button("⬆️ Import Games", use_container_width=True):
                        with st.spinner("🎮 Importing games..."):
                            games = pgn_loader.load_pgn_games(file_content, max_games=100000)
                            result = database.store_pgn_games(games, uploaded_pgn.name)
                            
                            if result['games_stored'] > 0:
                                st.success(f"🎮 Imported {result['games_stored']} games successfully!")
                            else:
                                st.error("❌ Failed to import games")
                else:
                    st.error(f"❌ {stats['error']}")
    
    with export_tab:
        st.markdown("#### 💾 Export & Backup")
        
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            if st.button("💾 Download Complete Database", use_container_width=True):
                with st.spinner("📦 Preparing database export..."):
                    export_path = export_database_with_schema()
                    
                    if export_path:
                        with open(export_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ Download Database File",
                                data=f.read(),
                                file_name=f"kuikma_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                                mime="application/octet-stream",
                                use_container_width=True
                            )
                        st.success("✅ Database export ready for download!")
                    else:
                        st.error("❌ Export failed")
        
        with export_col2:
            if st.button("🔧 Create Backup", use_container_width=True):
                with st.spinner("Creating backup..."):
                    backup_path = export_database_with_schema()
                    if backup_path:
                        st.success(f"✅ Backup created: {backup_path}")
                    else:
                        st.error("❌ Backup failed")

def display_analytics_section():
    """Analytics and reporting section."""
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
        try:
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
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_feature_access'")
            if cursor.fetchone():
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
            else:
                st.info("Feature access tracking not available")
            
            # Training activity
            st.markdown("#### 🎯 Training Activity")
            
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as moves,
                       SUM(CASE WHEN result = 'correct' THEN 1 ELSE 0 END) as correct
                FROM user_moves
                WHERE DATE(timestamp) BETWEEN ? AND ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (start_date, end_date))
            
            training_data = cursor.fetchall()
            
            if training_data:
                df_training = pd.DataFrame(training_data, columns=['Date', 'Total Moves', 'Correct Moves'])
                st.line_chart(df_training.set_index('Date'))
            else:
                st.info("No training data in selected period")
            
            conn.close()
            
        except Exception as e:
            st.error(f"Error generating reports: {e}")

def display_system_settings_section():
    """System settings section."""
    st.markdown("### 🔧 System Settings")
    
    st.markdown("#### ⚙️ Configuration")
    
    # Display current configuration
    config_data = []
    config_data.append(['App Name', config.APP_NAME])
    config_data.append(['App Version', config.APP_VERSION])
    config_data.append(['Database Path', config.DATABASE_PATH])
    config_data.append(['Admin Email', config.ADMIN_EMAIL])
    config_data.append(['User Registration Enabled', str(config.ENABLE_USER_REGISTRATION)])
    config_data.append(['Auto Approve Users', str(config.AUTO_APPROVE_USERS)])
    config_data.append(['Default Position Limit', str(config.DEFAULT_POSITION_LIMIT)])
    config_data.append(['Default Analysis Limit', str(config.DEFAULT_ANALYSIS_LIMIT)])
    config_data.append(['Default Game Upload Limit', str(config.DEFAULT_GAME_UPLOAD_LIMIT)])
    
    df_config = pd.DataFrame(config_data, columns=['Setting', 'Value'])
    st.dataframe(df_config, use_container_width=True, hide_index=True)
    
    st.info("💡 To modify these settings, update the .env file and restart the application.")

def display_maintenance_section():
    """System maintenance section."""
    st.markdown("### 🛠️ System Maintenance")
    
    maintenance_col1, maintenance_col2 = st.columns(2)
    
    with maintenance_col1:
        if st.button("🧹 Clean Orphaned Records", use_container_width=True):
            with st.spinner("Cleaning orphaned records..."):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Clean orphaned moves
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
                    
                except Exception as e:
                    st.error(f"❌ Cleanup failed: {e}")
    
    with maintenance_col2:
        if st.button("📊 Rebuild Indexes", use_container_width=True):
            with st.spinner("Rebuilding database indexes..."):
                if optimize_database():
                    st.success("✅ Indexes rebuilt successfully!")
                else:
                    st.error("❌ Index rebuild failed")
    
    # System status
    st.markdown("#### 📊 System Status")
    
    try:
        import os
        import shutil
        
        # Disk usage
        total, used, free = shutil.disk_usage(os.path.dirname(config.DATABASE_PATH))
        
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            st.metric("Disk Total", f"{total // (2**30)} GB")
        
        with status_col2:
            st.metric("Disk Used", f"{used // (2**30)} GB")
        
        with status_col3:
            st.metric("Disk Free", f"{free // (2**30)} GB")
        
        # Database file size
        if os.path.exists(config.DATABASE_PATH):
            db_size = os.path.getsize(config.DATABASE_PATH)
            st.metric("Database Size", f"{db_size // (2**20)} MB")
        
    except Exception as e:
        st.error(f"Error getting system status: {e}")

def display_feature_access_panel():
    """Feature access control panel - FIXED VERSION."""
    st.markdown("### 🔧 Feature Access Control")
    
    try:
        # Available features
        all_features = [
            'training', 'analysis', 'insights', 'game_analysis',
            'spatial_analysis', 'upload_games', 'save_positions',
            'export_data', 'view_history'
        ]
        
        # Get users with error handling
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if users table has required columns
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [col[1] for col in cursor.fetchall()]
        
        # Build safe query based on available columns
        base_query = 'SELECT id, email'
        if 'full_name' in user_columns:
            base_query += ', full_name'
        if 'is_verified' in user_columns:
            base_query += ', is_verified'
        if 'verification_status' in user_columns:
            base_query += ', verification_status'
        
        cursor.execute(f'''
            {base_query}
            FROM users 
            WHERE is_admin = 0
            ORDER BY email
        ''')
        users_result = cursor.fetchall()
        
        # Feature access configuration
        st.markdown("#### 🎛️ Global Feature Configuration")
        
        with st.expander("Configure Feature Access Rules"):
            st.markdown("**Default Permissions by User Type:**")
            
            try:
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
            except Exception as config_error:
                st.warning(f"Could not load global configuration: {config_error}")
        
        st.markdown("---")
        
        # Individual user feature access
        st.markdown("#### 👤 Individual Feature Access")
        
        if users_result and len(users_result) > 0:
            # Create user options safely
            user_options = []
            user_data = []
            
            for row in users_result:
                try:
                    user_id = row[0]
                    email = row[1]
                    full_name = row[2] if len(row) > 2 else None
                    is_verified = row[3] if len(row) > 3 else None
                    verification_status = row[4] if len(row) > 4 else None
                    
                    # Create display text
                    display_text = email
                    if full_name:
                        display_text += f" ({full_name})"
                    if is_verified is not None:
                        status = 'Verified' if is_verified else 'Unverified'
                        display_text += f" - {status}"
                    
                    user_options.append(display_text)
                    user_data.append({
                        'id': user_id,
                        'email': email,
                        'full_name': full_name,
                        'is_verified': is_verified,
                        'verification_status': verification_status
                    })
                except Exception as row_error:
                    print(f"Error processing user row: {row_error}")
                    continue
            
            if user_options:
                selected_user_option = st.selectbox(
                    "Select User for Feature Management",
                    options=range(len(user_options)),
                    format_func=lambda x: user_options[x]
                )
                
                if selected_user_option is not None:
                    selected_user = user_data[selected_user_option]
                    user_id = selected_user['id']
                    
                    st.markdown(f"**Managing features for:** {selected_user['email']} ({selected_user.get('full_name', 'No name')})")
                    
                    # Get current custom feature access with safe handling
                    try:
                        # Check if feature access table exists
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_feature_access'")
                        if cursor.fetchone():
                            cursor.execute('''
                                SELECT feature_name, access_granted, expires_at, notes
                                FROM user_feature_access 
                                WHERE user_id = ?
                            ''', (user_id,))
                            
                            feature_access_result = cursor.fetchall()
                            custom_access = {}
                            
                            for access_row in feature_access_result:
                                if len(access_row) >= 2:
                                    feature_name = access_row[0]
                                    access_granted = access_row[1]
                                    expires_at = access_row[2] if len(access_row) > 2 else None
                                    notes = access_row[3] if len(access_row) > 3 else None
                                    
                                    custom_access[feature_name] = {
                                        'granted': access_granted,
                                        'expires_at': expires_at,
                                        'notes': notes
                                    }
                        else:
                            custom_access = {}
                            st.info("Feature access table not found. Creating default access...")
                    
                    except Exception as access_error:
                        st.error(f"Error loading feature access: {access_error}")
                        custom_access = {}
                    
                    # Feature management form
                    with st.form(f"feature_access_{user_id}"):
                        st.markdown("#### 🎯 Custom Feature Access")
                        
                        feature_col1, feature_col2 = st.columns(2)
                        
                        feature_updates = {}
                        
                        for i, feature in enumerate(all_features):
                            col = feature_col1 if i % 2 == 0 else feature_col2
                            
                            with col:
                                current_custom = custom_access.get(feature, {})
                                current_granted = current_custom.get('granted', False)
                                
                                grant_access = st.checkbox(
                                    f"{feature.replace('_', ' ').title()}",
                                    value=current_granted,
                                    key=f"custom_{feature}_{user_id}"
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
                            try:
                                success_count = 0
                                
                                for feature, granted in feature_updates.items():
                                    try:
                                        # Delete existing record
                                        cursor.execute('''
                                            DELETE FROM user_feature_access 
                                            WHERE user_id = ? AND feature_name = ?
                                        ''', (user_id, feature))
                                        
                                        # Insert new record if access granted
                                        if granted:
                                            cursor.execute('''
                                                INSERT INTO user_feature_access (
                                                    user_id, feature_name, access_granted, granted_at,
                                                    granted_by, expires_at, notes
                                                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                                            ''', (
                                                user_id, feature, True,
                                                datetime.now().isoformat(),
                                                st.session_state['user_id'],
                                                expires_at.isoformat() if expires_at else None,
                                                access_notes
                                            ))
                                            success_count += 1
                                    except Exception as feature_error:
                                        st.error(f"Error updating {feature}: {feature_error}")
                                        continue
                                
                                conn.commit()
                                
                                # Log action
                                try:
                                    log_admin_action(
                                        st.session_state['user_id'],
                                        'update_feature_access',
                                        user_id,
                                        'user_features',
                                        {
                                            'features_updated': list(feature_updates.keys()),
                                            'grants_made': success_count
                                        }
                                    )
                                except Exception as log_error:
                                    print(f"Error logging admin action: {log_error}")
                                
                                st.success(f"✅ Updated feature access for {selected_user['email']}!")
                                st.rerun()
                                
                            except Exception as update_error:
                                st.error(f"❌ Failed to update feature access: {update_error}")
                                conn.rollback()
            else:
                st.info("No non-admin users found.")
        else:
            st.info("No users found for feature access management.")
        
        conn.close()
        
    except Exception as e:
        st.error(f"Error in feature access control: {e}")
        # Add debug info for admin users
        if st.session_state.get('user_info', {}).get('is_admin'):
            with st.expander("🔧 Debug Information"):
                st.code(f"Error details: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

def display_analytics_panel():
    """Analytics and reporting panel - FIXED VERSION."""
    st.markdown("### 📊 Analytics & Reports")
    
    try:
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
            
            try:
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
                
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_feature_access'")
                if cursor.fetchone():
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
                else:
                    st.info("Feature access tracking not available")
                
                # Training activity
                st.markdown("#### 🎯 Training Activity")
                
                cursor.execute('''
                    SELECT DATE(timestamp) as date, COUNT(*) as moves,
                           SUM(CASE WHEN result = 'correct' THEN 1 ELSE 0 END) as correct
                    FROM user_moves
                    WHERE DATE(timestamp) BETWEEN ? AND ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                ''', (start_date, end_date))
                
                training_data = cursor.fetchall()
                
                if training_data:
                    df_training = pd.DataFrame(training_data, columns=['Date', 'Total Moves', 'Correct Moves'])
                    st.line_chart(df_training.set_index('Date'))
                else:
                    st.info("No training data in selected period")
                
                # Admin activity log
                st.markdown("#### 👑 Admin Activity Log")
                
                # Check if admin audit table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_audit_log'")
                if cursor.fetchone():
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
                else:
                    st.info("Admin audit logging not available")
                
            except Exception as report_error:
                st.error(f"Error generating reports: {report_error}")
            finally:
                conn.close()
                
    except Exception as e:
        st.error(f"Error in analytics panel: {e}")

def display_maintenance_panel():
    """Maintenance panel - FIXED VERSION."""
    st.markdown("### 🛠️ Maintenance")
    
    try:
        # System actions
        maint_col1, maint_col2 = st.columns(2)
        
        with maint_col1:
            if st.button("🧹 Clean Orphaned Records", use_container_width=True):
                with st.spinner("Cleaning orphaned records..."):
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        cleanup_results = {}
                        
                        # Clean orphaned moves
                        cursor.execute('''
                            DELETE FROM moves WHERE position_id NOT IN (SELECT id FROM positions)
                        ''')
                        cleanup_results['orphaned_moves'] = cursor.rowcount
                        
                        # Clean orphaned user_moves
                        cursor.execute('''
                            DELETE FROM user_moves WHERE user_id NOT IN (SELECT id FROM users)
                        ''')
                        cleanup_results['orphaned_user_moves'] = cursor.rowcount
                        
                        # Clean orphaned user_move_analysis
                        try:
                            cursor.execute('''
                                DELETE FROM user_move_analysis WHERE user_id NOT IN (SELECT id FROM users)
                            ''')
                            cleanup_results['orphaned_analysis'] = cursor.rowcount
                        except:
                            cleanup_results['orphaned_analysis'] = 0
                        
                        conn.commit()
                        conn.close()
                        
                        st.success(f"✅ Cleanup completed:")
                        for key, value in cleanup_results.items():
                            st.info(f"• {key.replace('_', ' ').title()}: {value}")
                        
                    except Exception as cleanup_error:
                        st.error(f"❌ Cleanup failed: {cleanup_error}")
        
        with maint_col2:
            if st.button("📊 Rebuild Indexes", use_container_width=True):
                with st.spinner("Rebuilding database indexes..."):
                    if optimize_database():
                        st.success("✅ Indexes rebuilt successfully!")
                    else:
                        st.error("❌ Index rebuild failed")
        
        # System status
        st.markdown("#### 📊 System Status")
        
        try:
            import os
            import shutil
            
            # Disk usage
            total, used, free = shutil.disk_usage(os.path.dirname(config.DATABASE_PATH))
            
            status_col1, status_col2, status_col3 = st.columns(3)
            
            with status_col1:
                st.metric("Disk Total", f"{total // (2**30)} GB")
            
            with status_col2:
                st.metric("Disk Used", f"{used // (2**30)} GB")
            
            with status_col3:
                st.metric("Disk Free", f"{free // (2**30)} GB")
            
            # Database file size
            if os.path.exists(config.DATABASE_PATH):
                db_size = os.path.getsize(config.DATABASE_PATH)
                st.metric("Database Size", f"{db_size // (2**20)} MB")
            
        except Exception as status_error:
            st.error(f"Error getting system status: {status_error}")
            
    except Exception as e:
        st.error(f"Error in maintenance panel: {e}")

# Make function available for import
__all__ = ['display_consolidated_admin', 'display_feature_access_panel', 'display_analytics_panel', 'display_maintenance_panel']
