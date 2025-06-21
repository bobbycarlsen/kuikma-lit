# app.py - Optimized Kuikma Chess Engine Main Application
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
import config
from jsonl_processor import JSONLProcessor
from typing import Dict, Any, List, Optional, Tuple

# Import enhanced modules
from config import config
from database import upgrade_existing_database, create_enhanced_tables
from auth import (authenticate_user, register_user, ensure_admin_user, check_user_access,
                 get_user_subscription, can_use_resource)
from user_dashboard import display_user_dashboard
from admin import display_consolidated_admin

# Import existing modules with error handling
try:
    import training
    import insights
    import analysis
    import game_analysis
    import spatial_analysis
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
        try:
            subscription = get_user_subscription(st.session_state['user_id'])
            if subscription:
                with st.expander("📊 Subscription Info"):
                    st.markdown(f"**Type:** {subscription['subscription_type'].title()}")
                    progress_val = min(subscription['positions_used'] / max(subscription['position_limit'], 1), 1.0)
                    st.progress(progress_val)
                    st.caption(f"Positions: {subscription['positions_used']}/{subscription['position_limit']}")
        except Exception as e:
            st.caption("📊 Subscription info unavailable")
    
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
    is_admin = st.session_state.get('user_info', {}).get('is_admin', False)
    
    # Define menu items with required permissions
    menu_items = [
        ("🎯 Training", "training"),
        ("📊 Insights", "insights"),
        ("📈 Analysis", "analysis"),
        ("🎮 Game Analysis", "game_analysis"),
        ("🔍 Spatial Analysis", "spatial_analysis"),
        ("👤 User Dashboard", "user_dashboard"),
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
    
    # Admin section - consolidated
    if is_admin:
        st.markdown("---")
        st.markdown("### 👑 Admin Console")
        
        if st.button("🛡️ Admin Console", use_container_width=True, type="primary"):
            st.session_state.selected_page = "👑 Admin Console"
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

def display_settings_interface():
    """Simplified settings interface - removed redundancy."""
    st.markdown("## ⚙️ Data Management")
    
    # Only show data import/export for admins, user settings moved to dashboard
    if not st.session_state.get('user_info', {}).get('is_admin'):
        st.info("💡 User settings have been moved to the User Dashboard. Admin data management is available in the Admin Console.")
        return
    
    # For admin users, redirect to admin console
    st.info("🛡️ Admin data management features are now available in the Admin Console.")
    if st.button("🚀 Go to Admin Console", use_container_width=True):
        st.session_state.selected_page = "👑 Admin Console"
        st.rerun()

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
        "👤 User Dashboard": "user_dashboard",
        "👑 Admin Console": "admin_panel",
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
            display_settings_interface()

        elif selected_page == "👤 User Dashboard":
            display_user_dashboard()
        
        elif selected_page == "👑 Admin Console":
            display_consolidated_admin()
            
    except Exception as e:
        st.error(f"Error loading {selected_page}: {e}")
        st.info("This feature may not be fully implemented yet.")
        # Add debug info for admin users
        if st.session_state.get('user_info', {}).get('is_admin'):
            with st.expander("🔧 Debug Information"):
                st.code(f"Error details: {str(e)}")

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
