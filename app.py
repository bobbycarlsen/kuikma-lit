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

# Initialize enhanced database and create admin user on startup
database.init_db()
database.create_admin_user()

# Page configuration for Kuikma
st.set_page_config(
    page_title="Kuikma Chess Engine",
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
    """Display the main Kuikma header."""
    st.markdown('<h1 class="main-header">♟️ Kuikma Chess Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Advanced Chess Training & Analysis Platform</p>', unsafe_allow_html=True)

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

def display_admin_panel():
    """Admin-only functionality panel."""
    if st.session_state.get('user_id'):
        # Check if user is admin
        conn = database.get_db_connection()
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
                conn = database.get_db_connection()
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
                            conn = database.get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute('UPDATE users SET is_admin = NOT is_admin WHERE id = ?', (user_id_to_modify,))
                            conn.commit()
                            conn.close()
                            st.success("✅ Admin status updated!")
                            st.rerun()
                    
                    with action_col2:
                        if st.button("🗑️ Delete User", type="primary"):
                            if st.session_state.get('confirm_user_delete'):
                                conn = database.get_db_connection()
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
                sanity_result = database.database_sanity_check()
                stats = sanity_result.get('stats', {})
                
                # Display stats in cards
                stat_cols = st.columns(3)
                
                for i, (table, count) in enumerate(stats.items()):
                    with stat_cols[i % 3]:
                        st.metric(table.replace('_', ' ').title(), count)
                
                # Performance metrics
                st.markdown("##### 📈 Performance Metrics")
                
                conn = database.get_db_connection()
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
                            conn = database.get_db_connection()
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
                            if database.optimize_database():
                                st.success("✅ Indexes rebuilt successfully!")
                            else:
                                st.error("❌ Index rebuild failed")
            
            st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function."""
    display_kuikma_header()
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Authentication
    if not st.session_state.logged_in:
        auth_tab1, auth_tab2, auth_tab3 = st.tabs(["🔐 Login", "📝 Register", "👑 Admin"])
        
        with auth_tab1:
            st.markdown("### Login to Kuikma")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.button("🚀 Login", use_container_width=True):
                user_id = auth.authenticate_user(email, password)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.user_email = email
                    st.success("✅ Logged in successfully!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        with auth_tab2:
            st.markdown("### Register for Kuikma")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_confirm = st.text_input("Confirm Password", type="password")
            
            if st.button("📝 Register", use_container_width=True):
                if reg_password == reg_confirm:
                    if auth.register_user(reg_email, reg_password):
                        st.success("✅ Registration successful! Please login.")
                    else:
                        st.error("❌ Registration failed. Email might already exist.")
                else:
                    st.error("❌ Passwords do not match")
        
        with auth_tab3:
            st.markdown("### 👑 Admin Access")
            st.info("Use admin@kuikma.com / passpass for admin access")
            
            admin_email = st.text_input("Admin Email", value="admin@kuikma.com")
            admin_password = st.text_input("Admin Password", type="password", key="admin_pass")
            
            if st.button("🔑 Admin Login", use_container_width=True):
                if admin_email == "admin@kuikma.com" and admin_password == "passpass":
                    user_id = auth.authenticate_user(admin_email, admin_password)
                    if user_id:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.user_email = admin_email
                        st.success("✅ Admin logged in successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Admin authentication failed")
                else:
                    st.error("❌ Invalid admin credentials")
    
    else:
        # Main application interface with normal menu items
        with st.sidebar:
            st.markdown(f"### Welcome, {st.session_state.user_email}")
            
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.user_email = None
                st.rerun()
            
            st.markdown("---")
            
            # Check if admin
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT is_admin FROM users WHERE id = ?', (st.session_state['user_id'],))
            result = cursor.fetchone()
            is_admin = result and result[0] if result else False
            conn.close()
            
            # Navigation Menu Items (NOT dropdown)
            st.markdown("### 🧭 Navigation")
            
            # Initialize page selection
            if 'selected_page' not in st.session_state:
                st.session_state.selected_page = "🎯 Training"
            
            # Menu buttons
            if st.button("🎯 Training", use_container_width=True):
                st.session_state.selected_page = "🎯 Training"
                st.rerun()
            
            if st.button("📊 Insights", use_container_width=True):
                st.session_state.selected_page = "📊 Insights"
                st.rerun()
            
            if st.button("📈 Analysis", use_container_width=True):
                st.session_state.selected_page = "📈 Analysis"
                st.rerun()
            
            if st.button("🎮 Game Analysis", use_container_width=True):
                st.session_state.selected_page = "🎮 Game Analysis"
                st.rerun()
            
            if st.button("🔍 Spatial Analysis", use_container_width=True):
                st.session_state.selected_page = "🔍 Spatial Analysis"
                st.rerun()
            
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.selected_page = "⚙️ Settings"
                st.rerun()
            
            # Admin-only menu items
            if is_admin:
                st.markdown("---")
                st.markdown("### 👑 Admin")
                
                if st.button("🗄️ Database Viewer", use_container_width=True):
                    st.session_state.selected_page = "🗄️ Database Viewer"
                    st.rerun()
                
                if st.button("👑 Admin Panel", use_container_width=True):
                    st.session_state.selected_page = "👑 Admin Panel"
                    st.rerun()
        
        # Display selected page
        selected_page = st.session_state.get('selected_page', "🎯 Training")
        
        if selected_page == "🎯 Training":
            training.display_training_interface()
        
        elif selected_page == "📊 Insights":
            insights.display_insights()
        
        elif selected_page == "📈 Analysis":
            analysis.display_analysis()

        elif selected_page == "🎮 Game Analysis":
            game_analysis.display_game_analysis()        

        elif selected_page == "🔍 Spatial Analysis":
            spatial_analysis.display_spatial_analysis()
        
        elif selected_page == "⚙️ Settings":
            display_enhanced_settings()
        
        elif selected_page == "🗄️ Database Viewer" and is_admin:
            display_database_viewer()
        
        elif selected_page == "👑 Admin Panel" and is_admin:
            display_admin_panel()

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

if __name__ == "__main__":
    main()
