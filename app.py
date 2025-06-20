# app.py - Kuikma Chess Engine Main Application
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Import all modules
import database
import auth
import training
import insights
import analysis
import pgn_loader
import game_analysis
import spatial_analysis
import chess_board
import settings
import config
from jsonl_processor import JSONLProcessor
from typing import Dict, Any, List, Optional, Tuple

# Import enhanced modules
from config import config
from database import upgrade_existing_database, create_enhanced_tables
from auth import (authenticate_user, register_user, ensure_admin_user, check_user_access,
                 get_user_subscription, can_use_resource)
from admin_panel import display_enhanced_admin_panel
from user_dashboard import display_user_dashboard

# Import existing modules (assuming they exist)
try:
    import training
    import insights
    import analysis
    import game_analysis
    import spatial_analysis
    import settings
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.info("Some modules may not be available. Please ensure all required files are present.")


# Initialize enhanced database and create admin user on startup
database.init_db()
database.create_admin_user()

# Page configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for Kuikma branding
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .database-viewer {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .admin-panel {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff7675;
    }
    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .success-alert {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-alert {
        background: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .table-crud {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)


def display_kuikma_header():
    """Display enhanced application header."""
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <h1>♟️ {config.APP_NAME}</h1>
        <p style="color: #666; margin: 0;">
            Advanced Chess Training & Analysis Platform v{config.APP_VERSION}
        </p>
    </div>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "🎯 Training"


def display_database_viewer():
    """Comprehensive database viewer with CRUD operations."""
    st.markdown('<div class="database-viewer">', unsafe_allow_html=True)
    st.markdown("## 🗄️ Database Administration Panel")
    
    # Database overview
    sanity_result = database.database_sanity_check()
    
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
    st.markdown("### 🔧 Database Actions")
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("🔄 Sanity Check", use_container_width=True):
            with st.spinner("Running sanity check..."):
                result = database.database_sanity_check()
                if result['healthy']:
                    st.success("✅ Database is healthy!")
                else:
                    st.error("❌ Issues found in database")
                st.rerun()
    
    with action_col2:
        if st.button("⚡ Optimize DB", use_container_width=True):
            with st.spinner("Optimizing database..."):
                if database.optimize_database():
                    st.success("✅ Database optimized!")
                else:
                    st.error("❌ Optimization failed")
    
    with action_col3:
        if st.button("💾 Export DB", use_container_width=True):
            with st.spinner("Exporting database..."):
                export_path = database.export_database_with_schema()
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
    
    # Reset Options Modal
    if st.session_state.get('show_reset_options', False):
        st.markdown("### ⚠️ Database Reset Options")
        
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
                        if database.reset_database(reset_type):
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


def display_game_analysis():
    """Game analysis interface with enhanced functionality."""
    st.markdown("## 🎮 Game Analysis")
    
    # Existing game analysis functionality would go here
    # This is a placeholder for the existing game analysis features
    st.info("Game analysis functionality - integrate existing pgn_loader and game analysis features here")

def display_enhanced_settings():
    """Enhanced settings with JSONL processor integration."""
    st.markdown("## ⚙️ Settings & Data Management")
    
    settings_tab1, settings_tab2, settings_tab3 = st.tabs(["📤 Import Data", "💾 Export/Backup", "🔧 Configuration"])
    
    with settings_tab1:
        st.markdown("### 📥 Import Training Data")
        
        import_tab1, import_tab2 = st.tabs(["🧩 JSONL Positions", "♟️ PGN Games"])
        
        with import_tab1:
            st.markdown("Upload enhanced JSONL files with comprehensive position analysis.")
            uploaded_jsonl = st.file_uploader("Upload Enhanced JSONL File", type=['jsonl'], key="enhanced_jsonl")
            
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
        
        with import_tab2:
            st.markdown("Upload PGN files containing complete chess games for analysis.")
            uploaded_pgn = st.file_uploader("Upload PGN File", type=['pgn'], key="settings_pgn")
            
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
    
    with settings_tab2:
        st.markdown("### 💾 Export & Backup")
        
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            if st.button("💾 Download Complete Database", use_container_width=True):
                with st.spinner("📦 Preparing database export..."):
                    export_path = database.export_database_with_schema()
                    
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
                    backup_path = database.export_database_with_schema()
                    if backup_path:
                        st.success(f"✅ Backup created: {backup_path}")
                    else:
                        st.error("❌ Backup failed")
    
    with settings_tab3:
        st.markdown("### 🔧 User Configuration")
        
        # User settings form
        with st.form("user_settings"):
            st.markdown("#### Training Preferences")
            
            random_positions = st.checkbox("Random position selection", value=True)
            top_n_threshold = st.slider("Top N moves threshold", 1, 10, 3)
            score_difference = st.slider("Score difference threshold (cp)", 5, 50, 10)
            theme = st.selectbox("Board theme", ["default", "dark", "blue", "green"])
            
            if st.form_submit_button("💾 Save Settings", use_container_width=True):
                # Save user settings logic here
                st.success("✅ Settings saved successfully!")

def display_login_interface():
    """Display enhanced login/registration interface."""
    st.markdown("### 🔐 Authentication")
    
    auth_tab1, auth_tab2, auth_tab3 = st.tabs(["🔑 Login", "📝 Register", "👑 Admin"])
    
    with auth_tab1:
        display_login_tab()
    
    with auth_tab2:
        display_registration_tab()
    
    with auth_tab3:
        display_admin_login_tab()

def display_login_tab():
    """Display login tab."""
    st.markdown("#### Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="your@email.com")
        password = st.text_input("Password", type="password")
        
        submitted = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
        
        if submitted:
            if email and password:
                result = authenticate_user(email, password)
                
                if result and 'error' not in result:
                    st.session_state.logged_in = True
                    st.session_state.user_id = result['id']
                    st.session_state.user_email = result['email']
                    st.session_state.user_info = result
                    
                    # Check verification status
                    if not result['is_verified'] and not result['is_admin']:
                        st.warning("⚠️ Your account is pending verification. Access is limited until approved by an admin.")
                    else:
                        st.success("✅ Logged in successfully!")
                    
                    st.rerun()
                
                elif result and 'error' in result:
                    if result['error'] == 'account_locked':
                        st.error(f"🔒 Account locked until {result['locked_until']}")
                    elif result['error'] == 'account_inactive':
                        st.error(f"❌ Account is {result['status']}. Please contact admin.")
                    else:
                        st.error("❌ Authentication failed")
                else:
                    st.error("❌ Invalid email or password")
            else:
                st.error("❌ Please fill in all fields")

def display_registration_tab():
    """Display registration tab."""
    if not config.ENABLE_USER_REGISTRATION:
        st.warning("🚫 User registration is currently disabled.")
        return
    
    st.markdown("#### Create New Account")
    
    with st.form("registration_form"):
        reg_email = st.text_input("Email Address", placeholder="your@email.com")
        reg_full_name = st.text_input("Full Name", placeholder="Your full name")
        reg_password = st.text_input("Password", type="password")
        reg_confirm = st.text_input("Confirm Password", type="password")
        
        # Terms acceptance
        accept_terms = st.checkbox("I accept the terms of service and privacy policy")
        
        submitted = st.form_submit_button("📝 Create Account", use_container_width=True, type="primary")
        
        if submitted:
            if not accept_terms:
                st.error("❌ Please accept the terms of service")
            elif not all([reg_email, reg_full_name, reg_password, reg_confirm]):
                st.error("❌ Please fill in all fields")
            elif reg_password != reg_confirm:
                st.error("❌ Passwords do not match")
            elif len(reg_password) < 6:
                st.error("❌ Password must be at least 6 characters")
            else:
                result = register_user(reg_email, reg_password, reg_full_name)
                
                if result['success']:
                    if result.get('verification_required'):
                        st.success("✅ Account created! Please wait for admin approval before accessing features.")
                        st.info("💡 You can login now, but access will be limited until verification.")
                    else:
                        st.success("✅ Account created successfully! You can now login.")
                else:
                    error_messages = {
                        'email_exists': "❌ An account with this email already exists",
                        'admin_cannot_register': "❌ Admin users cannot register through this form",
                        'registration_disabled': "❌ Registration is currently disabled",
                        'registration_failed': "❌ Registration failed. Please try again."
                    }
                    st.error(error_messages.get(result.get('error'), "❌ Registration failed"))

def display_admin_login_tab():
    """Display admin login tab."""
    st.markdown("#### 👑 Admin Access")
    st.info(f"Use {config.ADMIN_EMAIL} with configured password for admin access")
    
    with st.form("admin_login_form"):
        admin_email = st.text_input("Admin Email", value=config.ADMIN_EMAIL)
        admin_password = st.text_input("Admin Password", type="password")
        
        submitted = st.form_submit_button("🔑 Admin Login", use_container_width=True)
        
        if submitted:
            if admin_email and admin_password:
                result = authenticate_user(admin_email, admin_password)
                
                if result and 'error' not in result and result.get('is_admin'):
                    st.session_state.logged_in = True
                    st.session_state.user_id = result['id']
                    st.session_state.user_email = result['email']
                    st.session_state.user_info = result
                    st.success("✅ Admin logged in successfully!")
                    st.rerun()
                else:
                    st.error("❌ Invalid admin credentials")
            else:
                st.error("❌ Please fill in all fields")

def display_user_sidebar():
    """Display user sidebar with navigation and user info."""
    # User info section
    user_info = st.session_state.user_info
    st.markdown(f"### Welcome, {user_info.get('full_name') or user_info.get('email', 'User')}")
    
    # User status indicators
    if user_info.get('is_admin'):
        st.markdown("🛡️ **Admin Account**")
    elif user_info.get('is_verified'):
        st.markdown("✅ **Verified User**")
    else:
        st.markdown("⏳ **Pending Verification**")
    
    # Subscription info for non-admin users
    if not user_info.get('is_admin'):
        subscription = get_user_subscription(st.session_state['user_id'])
        if subscription:
            with st.expander("📊 Subscription Info"):
                st.markdown(f"**Type:** {subscription['subscription_type'].title()}")
                st.progress(subscription['positions_used'] / subscription['position_limit'])
                st.caption(f"Positions: {subscription['positions_used']}/{subscription['position_limit']}")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.user_info = {}
        st.rerun()
    
    st.markdown("---")

def display_navigation_menu():
    """Display navigation menu with access control."""
    st.markdown("### 🧭 Navigation")
    
    user_id = st.session_state['user_id']
    
    # Define menu items with required permissions
    menu_items = [
        ("🎯 Training", "training"),
        ("📊 Insights", "insights"),
        ("📈 Analysis", "analysis"),
        ("🎮 Game Analysis", "game_analysis"),
        ("🔍 Spatial Analysis", "spatial_analysis"),
        ("⚙️ Settings", "view_profile"),
        ("🚶 User Dashboard", "user_dashboard"),
    ]
    
    # Admin menu items
    admin_items = [
        ("🗄️ Database Viewer", "database_viewer"),
        ("👑 Admin Panel", "admin_panel"),
    ]
    
    # Display accessible menu items
    for label, permission in menu_items:
        if check_user_access(user_id, permission):
            if st.button(label, use_container_width=True):
                st.session_state.selected_page = label
                st.rerun()
        else:
            # Show disabled button for inaccessible items
            st.button(
                f"{label} 🔒",
                use_container_width=True,
                disabled=True,
                help="Requires verification or higher permissions"
            )
    
    # Admin section
    if check_user_access(user_id, 'admin_panel'):
        st.markdown("---")
        st.markdown("### 👑 Admin")
        
        for label, permission in admin_items:
            if check_user_access(user_id, permission):
                if st.button(label, use_container_width=True):
                    st.session_state.selected_page = label
                    st.rerun()

def display_access_denied():
    """Display access denied message."""
    st.error("🔒 Access Denied")
    st.markdown("""
    You don't have permission to access this feature. This might be because:
    
    - Your account is pending verification
    - You've reached your subscription limits
    - This feature requires admin privileges
    
    Please contact an administrator if you believe this is an error.
    """)

def display_main_content():
    """Display main content based on selected page."""
    selected_page = st.session_state.get('selected_page', "🎯 Training")
    user_id = st.session_state['user_id']
    
    # Check access before displaying content
    page_permissions = {
        "🎯 Training": "training",
        "📊 Insights": "insights", 
        "📈 Analysis": "analysis",
        "🎮 Game Analysis": "game_analysis",
        "🔍 Spatial Analysis": "spatial_analysis",
        "⚙️ Settings": "view_profile",
        "🚶 User Dashboard": "user_dashboard",
        "🗄️ Database Viewer": "database_viewer",
        "👑 Admin Panel": "admin_panel",
    }
    
    required_permission = page_permissions.get(selected_page)
    
    if required_permission and not check_user_access(user_id, required_permission):
        display_access_denied()
        return
    
    # Display content based on page
    try:
        if selected_page == "🎯 Training":
            # Check resource limits for training
            can_train, reason = can_use_resource(user_id, 'position')
            if not can_train and not st.session_state.user_info.get('is_admin'):
                st.warning(f"⚠️ Training limited: {reason}")
                st.info("Contact admin to increase your position limit.")
            else:
                training.display_training_interface()
        
        elif selected_page == "📊 Insights":
            insights.display_insights()
        
        elif selected_page == "📈 Analysis":
            # Check resource limits for analysis
            can_analyze, reason = can_use_resource(user_id, 'analysis')
            if not can_analyze and not st.session_state.user_info.get('is_admin'):
                st.warning(f"⚠️ Analysis limited: {reason}")
                st.info("Contact admin to increase your analysis limit.")
            else:
                analysis.display_analysis()
        
        elif selected_page == "🎮 Game Analysis":
            game_analysis.display_game_analysis()
        
        elif selected_page == "🔍 Spatial Analysis":
            spatial_analysis.display_spatial_analysis()
        
        elif selected_page == "⚙️ Settings":
            settings.display_user_configuration()
            display_enhanced_settings()

        elif selected_page == "🚶 User Dashboard":
            display_user_dashboard()
        
        elif selected_page == "🗄️ Database Viewer":
            display_database_viewer()
        
        elif selected_page == "👑 Admin Panel":
            display_enhanced_admin_panel()
            
    except Exception as e:
        st.error(f"Error loading {selected_page}: {e}")
        st.info("This feature may not be fully implemented yet.")

def main():
    """Main application function with enhanced authentication."""
    # Initialize database and admin user
    try:
        upgrade_existing_database()
        create_enhanced_tables()
        ensure_admin_user()
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        st.stop()
    
    # Display header
    display_kuikma_header()
    
    # Initialize session state
    initialize_session_state()
    
    # Authentication flow
    if not st.session_state.logged_in:
        display_login_interface()
    else:
        # Main application interface
        with st.sidebar:
            display_user_sidebar()
            display_navigation_menu()
        
        # Main content area
        display_main_content()


if __name__ == "__main__":
    main()
