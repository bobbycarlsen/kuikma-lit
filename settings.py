# settings.py - Enhanced Settings Module for Kuikma Chess Engine
import auth
import streamlit as st

def display_user_configuration():
    """Display user configuration interface."""
    st.markdown("### 🔧 User Configuration")
    
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("User not logged in.")
        return
    
    # Get current settings
    current_settings = auth.get_user_settings(user_id)
    user_info = auth.get_user_info(user_id)
    
    # User information
    st.markdown("#### 👤 User Information")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown(f"**Email:** {user_info.get('email', 'Unknown')}")
        st.markdown(f"**Account Created:** {user_info.get('created_at', 'Unknown')}")
    
    with info_col2:
        st.markdown(f"**Last Login:** {user_info.get('last_login', 'Unknown')}")
        st.markdown(f"**Admin Status:** {'Yes' if user_info.get('is_admin') else 'No'}")
    
    st.markdown("---")
    
    # Training preferences
    st.markdown("#### 🎯 Training Preferences")
    
    with st.form("user_settings_form1"):
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
        
        # Notification preferences
        st.markdown("#### 🔔 Notification Preferences")
        
        email_notifications = st.checkbox(
            "Email notifications for achievements",
            value=False,
            help="Receive email notifications for training milestones"
        )
        
        session_reminders = st.checkbox(
            "Training session reminders",
            value=False,
            help="Get reminders to continue training"
        )
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            analysis_depth = st.slider(
                "Preferred analysis depth",
                min_value=10,
                max_value=25,
                value=18,
                help="Depth of engine analysis for new positions"
            )
            
            auto_generate_analysis = st.checkbox(
                "Auto-generate HTML analysis",
                value=False,
                help="Automatically generate comprehensive HTML analysis for each training move"
            )
        
        # Save settings
        if st.form_submit_button("💾 Save Settings", use_container_width=True, type="primary"):
            new_settings = {
                'random_positions': random_positions,
                'top_n_threshold': top_n_threshold,
                'score_difference_threshold': score_difference_threshold,
                'theme': theme
            }
            
            if auth.update_user_settings(user_id, new_settings):
                st.success("✅ Settings saved successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to save settings")

if __name__ == "__main__":
    print("Enhanced settings module for Kuikma Chess Engine loaded.")
