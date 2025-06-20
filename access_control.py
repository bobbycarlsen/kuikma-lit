# access_control.py - Access Control Decorators & Middleware
"""
Access control utilities to simplify permission checking throughout the application.
Provides decorators and context managers for protecting functions and UI components.
"""

import streamlit as st
from functools import wraps
from typing import Callable, Optional, List, Union
from contextlib import contextmanager

from auth import check_user_access, can_use_resource, increment_resource_usage
from config import config

class PermissionError(Exception):
    """Custom exception for permission-related errors."""
    pass

def require_login(func: Callable) -> Callable:
    """
    Decorator to require user login before accessing a function.
    
    Usage:
        @require_login
        def some_function():
            # Function only accessible to logged-in users
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get('logged_in') or not st.session_state.get('user_id'):
            st.error("🔐 Please login to access this feature")
            st.stop()
        
        return func(*args, **kwargs)
    
    return wrapper

def require_permission(permission: str, show_error: bool = True) -> Callable:
    """
    Decorator to require specific permission before accessing a function.
    
    Args:
        permission: Required permission string
        show_error: Whether to show error message if access denied
    
    Usage:
        @require_permission('admin_panel')
        def admin_function():
            # Function only accessible to users with admin_panel permission
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = st.session_state.get('user_id')
            
            if not user_id:
                if show_error:
                    st.error("🔐 Please login to access this feature")
                st.stop()
            
            if not check_user_access(user_id, permission):
                if show_error:
                    st.error(f"🔒 Access denied. Required permission: {permission}")
                    display_permission_help(permission)
                st.stop()
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_verification(func: Callable) -> Callable:
    """
    Decorator to require verified user status.
    
    Usage:
        @require_verification
        def verified_user_function():
            # Function only accessible to verified users
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_info = st.session_state.get('user_info', {})
        
        if not user_info.get('is_verified') and not user_info.get('is_admin'):
            st.warning("⚠️ Account verification required")
            st.info("Your account is pending admin approval. Please wait for verification.")
            st.stop()
        
        return func(*args, **kwargs)
    
    return wrapper

def require_resource(resource_type: str, amount: int = 1, auto_increment: bool = True) -> Callable:
    """
    Decorator to check and optionally consume resource limits.
    
    Args:
        resource_type: Type of resource ('position', 'analysis', 'game_upload')
        amount: Amount of resource to consume
        auto_increment: Whether to automatically increment usage counter
    
    Usage:
        @require_resource('position', amount=1, auto_increment=True)
        def training_function():
            # Function that consumes 1 position from user's limit
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = st.session_state.get('user_id')
            user_info = st.session_state.get('user_info', {})
            
            # Skip resource checks for admin users
            if user_info.get('is_admin'):
                return func(*args, **kwargs)
            
            if not user_id:
                st.error("🔐 Please login to access this feature")
                st.stop()
            
            # Check resource availability
            can_use, reason = can_use_resource(user_id, resource_type)
            
            if not can_use:
                st.error(f"🚫 Resource limit exceeded: {reason}")
                display_subscription_info(user_id)
                st.stop()
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Increment usage if successful and auto_increment is True
            if auto_increment and result is not None:
                increment_resource_usage(user_id, resource_type, amount)
            
            return result
        
        return wrapper
    return decorator

def admin_only(func: Callable) -> Callable:
    """
    Decorator to restrict access to admin users only.
    
    Usage:
        @admin_only
        def admin_function():
            # Function only accessible to admin users
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_info = st.session_state.get('user_info', {})
        
        if not user_info.get('is_admin'):
            st.error("👑 Admin access required")
            st.stop()
        
        return func(*args, **kwargs)
    
    return wrapper

@contextmanager
def permission_context(permission: str, fallback_message: Optional[str] = None):
    """
    Context manager for conditional UI rendering based on permissions.
    
    Usage:
        with permission_context('training'):
            st.button("Start Training")  # Only shown if user has training permission
        else:
            st.info("Training requires verification")
    """
    user_id = st.session_state.get('user_id')
    has_permission = user_id and check_user_access(user_id, permission)
    
    if has_permission:
        yield True
    else:
        if fallback_message:
            st.info(fallback_message)
        yield False

@contextmanager
def verification_context(fallback_message: Optional[str] = None):
    """
    Context manager for conditional UI rendering based on verification status.
    
    Usage:
        with verification_context():
            st.button("Verified Feature")  # Only shown if user is verified
        else:
            st.warning("Verification required")
    """
    user_info = st.session_state.get('user_info', {})
    is_verified = user_info.get('is_verified') or user_info.get('is_admin')
    
    if is_verified:
        yield True
    else:
        if fallback_message:
            st.warning(fallback_message)
        else:
            st.warning("⚠️ Account verification required for this feature")
        yield False

@contextmanager
def resource_context(resource_type: str, fallback_message: Optional[str] = None):
    """
    Context manager for conditional UI rendering based on resource availability.
    
    Usage:
        with resource_context('position'):
            st.button("Use Position")  # Only shown if user has positions available
        else:
            st.error("Position limit reached")
    """
    user_id = st.session_state.get('user_id')
    user_info = st.session_state.get('user_info', {})
    
    # Always allow for admin users
    if user_info.get('is_admin'):
        yield True
        return
    
    can_use, reason = can_use_resource(user_id, resource_type) if user_id else (False, "Not logged in")
    
    if can_use:
        yield True
    else:
        if fallback_message:
            st.error(fallback_message)
        else:
            st.error(f"🚫 {reason}")
        yield False

def display_permission_help(permission: str):
    """Display helpful information about a required permission."""
    help_messages = {
        'training': "Training requires a verified account. Please wait for admin approval.",
        'analysis': "Analysis features require verification and available analysis credits.",
        'admin_panel': "Admin panel access is restricted to administrators only.",
        'database_viewer': "Database viewer requires administrator privileges.",
        'user_management': "User management requires administrator privileges.",
        'user_dashboard': "User management requires verification/admin user privileges.",
        'subscription_management': "Subscription management requires administrator privileges.",
    }
    
    if permission in help_messages:
        st.info(f"💡 {help_messages[permission]}")
    else:
        st.info(f"💡 This feature requires the '{permission}' permission.")

def display_subscription_info(user_id: int):
    """Display subscription information and upgrade options."""
    from auth import get_user_subscription
    
    subscription = get_user_subscription(user_id)
    
    if subscription:
        with st.expander("📊 View Subscription Details"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Positions",
                    f"{subscription['positions_used']}/{subscription['position_limit']}",
                    delta=f"{subscription['positions_remaining']} remaining"
                )
            
            with col2:
                st.metric(
                    "Analyses",
                    f"{subscription['analyses_used']}/{subscription['analysis_limit']}",
                    delta=f"{subscription['analyses_remaining']} remaining"
                )
            
            with col3:
                st.metric(
                    "Games",
                    f"{subscription['games_uploaded']}/{subscription['game_upload_limit']}",
                    delta=f"{subscription['games_remaining']} remaining"
                )
            
            st.info("💡 Contact an administrator to increase your limits.")

class AccessControlMixin:
    """
    Mixin class to add access control methods to other classes.
    
    Usage:
        class MyFeature(AccessControlMixin):
            def display(self):
                if not self.check_permission('training'):
                    self.show_access_denied()
                    return
                
                # Display feature content
    """
    
    def check_permission(self, permission: str) -> bool:
        """Check if current user has permission."""
        user_id = st.session_state.get('user_id')
        return user_id and check_user_access(user_id, permission)
    
    def check_verification(self) -> bool:
        """Check if current user is verified."""
        user_info = st.session_state.get('user_info', {})
        return user_info.get('is_verified') or user_info.get('is_admin')
    
    def check_admin(self) -> bool:
        """Check if current user is admin."""
        user_info = st.session_state.get('user_info', {})
        return user_info.get('is_admin', False)
    
    def check_resource(self, resource_type: str) -> tuple[bool, Optional[str]]:
        """Check if current user can use a resource."""
        user_id = st.session_state.get('user_id')
        if not user_id:
            return False, "Not logged in"
        
        return can_use_resource(user_id, resource_type)
    
    def show_access_denied(self, message: Optional[str] = None):
        """Show access denied message."""
        if message:
            st.error(message)
        else:
            st.error("🔒 Access denied. You don't have permission to access this feature.")
    
    def show_verification_required(self):
        """Show verification required message."""
        st.warning("⚠️ Account verification required for this feature.")
        st.info("Please wait for admin approval to access this feature.")
    
    def show_resource_exceeded(self, resource_type: str, reason: str):
        """Show resource limit exceeded message."""
        st.error(f"🚫 {resource_type.title()} limit exceeded: {reason}")
        display_subscription_info(st.session_state.get('user_id'))

# Convenience functions for common access patterns
def is_logged_in() -> bool:
    """Check if user is logged in."""
    return bool(st.session_state.get('logged_in') and st.session_state.get('user_id'))

def is_verified() -> bool:
    """Check if current user is verified."""
    user_info = st.session_state.get('user_info', {})
    return user_info.get('is_verified') or user_info.get('is_admin')

def is_admin() -> bool:
    """Check if current user is admin."""
    user_info = st.session_state.get('user_info', {})
    return user_info.get('is_admin', False)

def get_current_user_id() -> Optional[int]:
    """Get current user ID."""
    return st.session_state.get('user_id')

def get_current_user_info() -> dict:
    """Get current user info."""
    return st.session_state.get('user_info', {})

