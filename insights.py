# =============================================================================
# insights.py - User Insights and Analytics for Kuikma
# =============================================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import database
import auth
from typing import Dict, Any, List, Optional, Tuple

def display_insights():
    """Display comprehensive user insights and analytics."""
    st.markdown("## 📊 Training Insights")
    
    if 'user_id' not in st.session_state:
        st.error("Please log in to view insights.")
        return
    
    user_id = st.session_state.user_id
    
    # Get user statistics
    user_stats = auth.get_user_statistics(user_id)
    user_info = auth.get_user_info(user_id)
    
    # overview metrics
    display_enhanced_overview_metrics(user_stats)
    
    # Performance trends
    display_performance_trends(user_id)
    
    # Position analysis
    display_position_insights(user_id)
    
    # analytics dashboard
    display_enhanced_analytics_dashboard(user_stats)
    
    # Recommendations
    display_training_recommendations(user_stats)

def display_enhanced_overview_metrics(user_stats: Dict[str, Any]):
    """Display enhanced overview metrics with all new statistics."""
    st.markdown("### 📈 Training Overview")
    
    # Primary Training Metrics
    st.markdown("#### 🎯 Training Performance")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Moves",
            user_stats.get('total_moves', 0),
            help="Total training moves attempted"
        )
    
    with col2:
        st.metric(
            "Accuracy",
            f"{user_stats.get('accuracy', 0):.1f}%",
            help="Percentage of correct moves (score > 0)"
        )
    
    with col3:
        st.metric(
            "Correct Moves",
            user_stats.get('correct_moves', 0),
            help="Number of moves with positive score"
        )
    
    with col4:
        st.metric(
            "Training Sessions",
            user_stats.get('training_sessions', 0),
            help="Number of training sessions completed"
        )
    
    # Advanced Analytics Metrics
    st.markdown("#### ⚡ Advanced Analytics")
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            "Avg Time",
            f"{user_stats.get('average_time', 0):.2f}s",
            help="Average time per move"
        )
    
    with col6:
        st.metric(
            "Avg Score",
            f"{user_stats.get('average_score', 0):.2f}",
            help="Average move score from engine evaluation"
        )
    
    with col7:
        st.metric(
            "Avg Centipawn Loss",
            f"{user_stats.get('average_centipawn_loss', 0):.2f}",
            help="Average centipawn loss per move"
        )
    
    with col8:
        st.metric(
            "Avg Move Rank",
            f"{user_stats.get('average_rank', 0):.2f}",
            help="Average rank of chosen moves"
        )
    
    # Strategic Metrics
    st.markdown("#### 🧠 Strategic Metrics")
    col9, col10, col11, col12 = st.columns(4)
    
    with col9:
        st.metric(
            "Move Complexity",
            f"{user_stats.get('average_move_complexity', 0):.2f}/5",
            help="Average complexity of positions played"
        )
    
    with col10:
        st.metric(
            "Strategic Value",
            f"{user_stats.get('average_strategic_value', 0):.2f}/5",
            help="Average strategic value of chosen moves"
        )
    
    with col11:
        games_analyzed = user_stats.get('games_analyzed', 0)
        st.metric(
            "Games Analyzed",
            games_analyzed,
            help="Total number of games analyzed"
        )
    
    with col12:
        total_moves_analyzed = user_stats.get('total_moves_analyzed', 0)
        st.metric(
            "Moves Analyzed",
            total_moves_analyzed,
            help="Total moves analyzed in games"
        )
    
    # Activity Overview
    st.markdown("#### 📅 Activity Overview")
    col13, col14 = st.columns(2)
    
    with col13:
        avg_analysis_time = user_stats.get('avg_analysis_time', 0)
        st.metric(
            "Avg Analysis Time",
            f"{avg_analysis_time:.2f}s",
            help="Average time spent analyzing games"
        )
    
    with col14:
        last_training = user_stats.get('last_training')
        if last_training:
            try:
                last_date = datetime.fromisoformat(last_training.replace('Z', '+00:00')).date()
                days_ago = (datetime.now().date() - last_date).days
                last_training_display = f"{days_ago} days ago" if days_ago > 0 else "Today"
            except:
                last_training_display = "Recently"
        else:
            last_training_display = "Never"
        
        st.metric(
            "Last Training",
            last_training_display,
            help="When you last completed a training move"
        )

def display_enhanced_analytics_dashboard(user_stats: Dict[str, Any]):
    """Display enhanced analytics dashboard with detailed metrics."""
    st.markdown("### 📊 Detailed Analytics Dashboard")
    
    # Create performance indicators
    total_moves = user_stats.get('total_moves', 0)
    
    if total_moves == 0:
        st.info("📈 Complete some training moves to see detailed analytics!")
        return
    
    # Performance Quality Indicators
    st.markdown("#### 🎯 Performance Quality")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Move Quality Chart
        accuracy = user_stats.get('accuracy', 0)
        avg_score = user_stats.get('average_score', 0)
        avg_rank = user_stats.get('average_rank', 0)
        
        # Create a radar chart for move quality
        categories = ['Accuracy', 'Avg Score', 'Move Rank (Inv)', 'Strategic Value', 'Complexity']
        
        # Normalize values for radar chart (0-100 scale)
        values = [
            accuracy,
            min(abs(avg_score) * 10, 100),  # Scale score to 0-100
            max(0, 100 - (avg_rank * 20)),  # Invert rank (lower is better)
            user_stats.get('average_strategic_value', 0) * 20,  # Scale 0-5 to 0-100
            user_stats.get('average_move_complexity', 0) * 20   # Scale 0-5 to 0-100
        ]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Your Performance'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Performance Profile"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with col2:
        # Training Progress Metrics
        st.markdown("**📈 Training Progress**")
        
        # Calculate some derived metrics
        moves_per_session = total_moves / max(user_stats.get('training_sessions', 1), 1)
        centipawn_loss = user_stats.get('average_centipawn_loss', 0)
        
        # Progress indicators
        progress_data = {
            'Metric': ['Moves per Session', 'Centipawn Loss', 'Move Efficiency', 'Strategic Focus'],
            'Value': [
                f"{moves_per_session:.1f}",
                f"{centipawn_loss:.1f}",
                f"{(100 - min(centipawn_loss, 100)):.1f}%",
                f"{user_stats.get('average_strategic_value', 0):.1f}/5"
            ],
            'Status': [
                '🟢' if moves_per_session > 10 else '🟡' if moves_per_session > 5 else '🔴',
                '🟢' if centipawn_loss < 20 else '🟡' if centipawn_loss < 50 else '🔴',
                '🟢' if centipawn_loss < 20 else '🟡' if centipawn_loss < 50 else '🔴',
                '🟢' if user_stats.get('average_strategic_value', 0) > 3 else '🟡' if user_stats.get('average_strategic_value', 0) > 2 else '🔴'
            ]
        }
        
        progress_df = pd.DataFrame(progress_data)
        
        for _, row in progress_df.iterrows():
            st.markdown(f"**{row['Metric']}**: {row['Value']} {row['Status']}")
    
    # Game Analysis Section (if applicable)
    games_analyzed = user_stats.get('games_analyzed', 0)
    if games_analyzed > 0:
        st.markdown("#### 🎮 Game Analysis Performance")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            total_moves_analyzed = user_stats.get('total_moves_analyzed', 0)
            avg_moves_per_game = total_moves_analyzed / games_analyzed if games_analyzed > 0 else 0
            st.metric(
                "Avg Moves/Game",
                f"{avg_moves_per_game:.1f}",
                help="Average moves analyzed per game"
            )
        
        with col4:
            avg_analysis_time = user_stats.get('avg_analysis_time', 0)
            st.metric(
                "Analysis Efficiency",
                f"{avg_analysis_time:.1f}s/move",
                help="Average time per move in game analysis"
            )
        
        with col5:
            analysis_completion = min((total_moves_analyzed / (games_analyzed * 40)) * 100, 100) if games_analyzed > 0 else 0
            st.metric(
                "Analysis Depth",
                f"{analysis_completion:.1f}%",
                help="Estimated completion rate of game analysis"
            )

def display_overview_metrics(user_stats: Dict[str, Any]):
    """Legacy function - keep for backward compatibility."""
    display_enhanced_overview_metrics(user_stats)

def display_performance_trends(user_id: int):
    """Display performance trends over time."""
    st.markdown("### 📈 Performance Trends")
    
    # Get recent performance data
    performance_data = get_performance_data(user_id)
    
    if performance_data:
        df = pd.DataFrame(performance_data)
        
        # Create tabs for different trend views
        tab1, tab2, tab3 = st.tabs(["📊 Accuracy & Time", "🎯 Score Trends", "📈 Volume"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Accuracy trend
                fig_accuracy = px.line(
                    df, 
                    x='date', 
                    y='accuracy',
                    title='Training Accuracy Over Time',
                    labels={'accuracy': 'Accuracy (%)', 'date': 'Date'}
                )
                st.plotly_chart(fig_accuracy, use_container_width=True)
            
            with col2:
                # Time trend
                fig_time = px.line(
                    df,
                    x='date',
                    y='avg_time', 
                    title='Average Move Time Over Time',
                    labels={'avg_time': 'Average Time (seconds)', 'date': 'Date'}
                )
                st.plotly_chart(fig_time, use_container_width=True)
        
        with tab2:
            # Score and centipawn loss trends (if available)
            if 'avg_score' in df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_score = px.line(
                        df,
                        x='date',
                        y='avg_score',
                        title='Average Score Trend',
                        labels={'avg_score': 'Average Score', 'date': 'Date'}
                    )
                    st.plotly_chart(fig_score, use_container_width=True)
                
                with col2:
                    if 'avg_centipawn_loss' in df.columns:
                        fig_cpl = px.line(
                            df,
                            x='date',
                            y='avg_centipawn_loss',
                            title='Centipawn Loss Trend',
                            labels={'avg_centipawn_loss': 'Avg Centipawn Loss', 'date': 'Date'}
                        )
                        st.plotly_chart(fig_cpl, use_container_width=True)
            else:
                st.info("Score trend data will appear as you complete more training with detailed analytics.")
        
        with tab3:
            # Volume trends
            fig_volume = px.bar(
                df,
                x='date',
                y='total_moves',
                title='Daily Training Volume',
                labels={'total_moves': 'Moves Completed', 'date': 'Date'}
            )
            st.plotly_chart(fig_volume, use_container_width=True)
    else:
        st.info("No performance data available yet. Complete some training to see trends!")

def display_position_insights(user_id: int):
    """Display position-specific insights with proper error handling."""
    st.markdown("### 🎯 Position Analysis")
    
    # Get position performance data
    position_data = get_position_performance_data(user_id)
    
    if not position_data or (not position_data['by_difficulty'] and not position_data['by_theme']):
        st.info("📊 Complete more training positions to see detailed analysis.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Difficulty performance
        if position_data['by_difficulty']:
            difficulty_df = pd.DataFrame(position_data['by_difficulty'])
            
            if not difficulty_df.empty and 'difficulty_range' in difficulty_df.columns:
                fig_diff = px.bar(
                    difficulty_df,
                    x='difficulty_range',
                    y='accuracy',
                    title='Accuracy by Position Difficulty',
                    labels={'accuracy': 'Accuracy (%)', 'difficulty_range': 'Difficulty Range'},
                    text='total_moves'
                )
                fig_diff.update_traces(texttemplate='%{text} moves', textposition='outside')
                fig_diff.update_xaxes(tickangle=45)
                st.plotly_chart(fig_diff, use_container_width=True)
            else:
                st.info("Insufficient difficulty data for visualization.")
        else:
            st.info("No difficulty analysis data available.")
    
    with col2:
        # Theme performance  
        if position_data['by_theme']:
            themes_df = pd.DataFrame(position_data['by_theme'])
            
            if not themes_df.empty and 'theme' in themes_df.columns:
                fig_themes = px.bar(
                    themes_df,
                    x='theme',
                    y='accuracy',
                    title='Accuracy by Position Theme',
                    labels={'accuracy': 'Accuracy (%)', 'theme': 'Theme'},
                    text='total_moves'
                )
                fig_themes.update_traces(texttemplate='%{text} moves', textposition='outside')
                fig_themes.update_xaxes(tickangle=45)
                st.plotly_chart(fig_themes, use_container_width=True)
            else:
                st.info("Insufficient theme data for visualization.")
        else:
            st.info("No theme analysis data available.")

def display_training_recommendations(user_stats: Dict[str, Any]):
    """Display personalized training recommendations with enhanced analytics."""
    st.markdown("### 🎓 Training Recommendations")
    
    recommendations = generate_enhanced_recommendations(user_stats)
    
    # Group recommendations by type
    improvement_recs = [r for r in recommendations if r['type'] == 'improvement']
    strength_recs = [r for r in recommendations if r['type'] == 'strength']
    general_recs = [r for r in recommendations if r['type'] == 'general']
    
    col1, col2 = st.columns(2)
    
    with col1:
        if improvement_recs:
            st.markdown("#### 🎯 Areas for Improvement")
            for rec in improvement_recs:
                st.warning(f"**{rec['title']}**: {rec['description']}")
        
        if general_recs:
            st.markdown("#### 💡 General Recommendations")
            for rec in general_recs:
                st.info(f"**{rec['title']}**: {rec['description']}")
    
    with col2:
        if strength_recs:
            st.markdown("#### 💪 Strengths")
            for rec in strength_recs:
                st.success(f"**{rec['title']}**: {rec['description']}")

def generate_enhanced_recommendations(user_stats: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate enhanced personalized training recommendations."""
    recommendations = []
    
    accuracy = user_stats.get('accuracy', 0)
    total_moves = user_stats.get('total_moves', 0)
    avg_time = user_stats.get('average_time', 0)
    avg_score = user_stats.get('average_score', 0)
    avg_centipawn_loss = user_stats.get('average_centipawn_loss', 0)
    avg_rank = user_stats.get('average_rank', 0)
    avg_complexity = user_stats.get('average_move_complexity', 0)
    avg_strategic = user_stats.get('average_strategic_value', 0)
    
    # Enhanced accuracy-based recommendations
    if accuracy < 30:
        recommendations.append({
            'type': 'improvement',
            'title': 'Focus on Basic Tactics',
            'description': 'Your accuracy is quite low. Start with simpler tactical puzzles and focus on fundamental patterns like pins, forks, and skewers.'
        })
    elif accuracy < 50:
        recommendations.append({
            'type': 'improvement',
            'title': 'Strengthen Pattern Recognition',
            'description': 'Work on recognizing common tactical motifs. Practice identifying threats before making moves.'
        })
    elif accuracy > 80:
        recommendations.append({
            'type': 'strength',
            'title': 'Excellent Tactical Vision!',
            'description': 'Your accuracy shows strong tactical skills. Consider increasing difficulty or focusing on strategic positions.'
        })
    
    # Centipawn loss recommendations
    if avg_centipawn_loss > 50:
        recommendations.append({
            'type': 'improvement',
            'title': 'Reduce Move Inaccuracies',
            'description': f'Your average centipawn loss is {avg_centipawn_loss:.1f}. Focus on move quality over speed.'
        })
    elif avg_centipawn_loss < 20:
        recommendations.append({
            'type': 'strength',
            'title': 'High Move Quality',
            'description': 'You maintain low centipawn loss, showing good move selection!'
        })
    
    # Move rank recommendations
    if avg_rank > 3:
        recommendations.append({
            'type': 'improvement',
            'title': 'Improve Move Selection',
            'description': f'Your moves average rank {avg_rank:.1f}. Try to find the engine\'s top choices more often.'
        })
    elif avg_rank < 1.5:
        recommendations.append({
            'type': 'strength',
            'title': 'Excellent Move Selection',
            'description': 'You frequently find the best moves! Your pattern recognition is strong.'
        })
    
    # Strategic value recommendations
    if avg_strategic < 2:
        recommendations.append({
            'type': 'improvement',
            'title': 'Develop Strategic Understanding',
            'description': 'Focus on understanding positional concepts like pawn structure, piece activity, and king safety.'
        })
    elif avg_strategic > 3.5:
        recommendations.append({
            'type': 'strength',
            'title': 'Strong Strategic Sense',
            'description': 'You show good strategic understanding in your move choices!'
        })
    
    # Complexity recommendations
    if avg_complexity < 2 and total_moves > 20:
        recommendations.append({
            'type': 'general',
            'title': 'Try More Complex Positions',
            'description': 'You handle simpler positions well. Challenge yourself with more complex tactical puzzles.'
        })
    elif avg_complexity > 4:
        recommendations.append({
            'type': 'improvement',
            'title': 'Master Complex Positions',
            'description': 'You\'re tackling difficult positions. Focus on calculation accuracy in complex scenarios.'
        })
    
    # Time-based recommendations (existing)
    if avg_time > 60:
        recommendations.append({
            'type': 'improvement',
            'title': 'Improve Speed',
            'description': 'Consider practicing pattern recognition to reduce thinking time.'
        })
    elif avg_time < 5 and total_moves > 10:
        recommendations.append({
            'type': 'improvement',
            'title': 'Take More Time',
            'description': 'You move very quickly. Consider analyzing positions more thoroughly.'
        })
    
    # Volume-based recommendations
    if total_moves < 10:
        recommendations.append({
            'type': 'general',
            'title': 'Keep Training!',
            'description': 'Complete more training positions to get better insights into your performance.'
        })
    elif total_moves > 100:
        recommendations.append({
            'type': 'strength',
            'title': 'Dedicated Trainer',
            'description': f'You\'ve completed {total_moves} moves! Your consistency is impressive.'
        })
    
    # Game analysis recommendations
    games_analyzed = user_stats.get('games_analyzed', 0)
    if games_analyzed == 0 and total_moves > 50:
        recommendations.append({
            'type': 'general',
            'title': 'Try Game Analysis',
            'description': 'Consider analyzing complete games to understand how tactical themes develop in real play.'
        })
    elif games_analyzed > 5:
        recommendations.append({
            'type': 'strength',
            'title': 'Well-Rounded Training',
            'description': 'Great job combining tactical training with game analysis!'
        })
    
    # Default recommendation if no specific ones apply
    if not recommendations:
        recommendations.append({
            'type': 'general',
            'title': 'Continue Balanced Training',
            'description': 'Your performance shows balanced improvement. Keep practicing different types of positions.'
        })
    
    return recommendations

def get_performance_data(user_id: int) -> List[Dict[str, Any]]:
    """Get enhanced user performance data over time with new metrics."""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Check what columns exist
        cursor.execute("PRAGMA table_info(user_moves)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Build query based on available columns
        base_query = '''
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_moves,
                SUM(CASE WHEN result = 'correct' OR score > 0 THEN 1 ELSE 0 END) as correct_moves,
                AVG(time_taken) as avg_time
        '''
        
        additional_fields = []
        if 'score' in columns:
            additional_fields.append('AVG(score) as avg_score')
        if 'centipawn_loss' in columns:
            additional_fields.append('AVG(centipawn_loss) as avg_centipawn_loss')
        if 'rank' in columns:
            additional_fields.append('AVG(rank) as avg_rank')
        if 'move_complexity' in columns:
            additional_fields.append('AVG(move_complexity) as avg_complexity')
        if 'strategic_value' in columns:
            additional_fields.append('AVG(strategic_value) as avg_strategic')
        
        if additional_fields:
            base_query += ', ' + ', '.join(additional_fields)
        
        query = base_query + '''
            FROM user_moves 
            WHERE user_id = ? AND timestamp >= date('now', '-30 days')
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp)
        '''
        
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        conn.close()
        
        performance_data = []
        for row in results:
            date, total, correct, avg_time = row[0], row[1], row[2], row[3]
            accuracy = (correct / total * 100) if total > 0 else 0
            
            data_point = {
                'date': date,
                'total_moves': total,
                'correct_moves': correct,
                'accuracy': accuracy,
                'avg_time': avg_time or 0
            }
            
            # Add additional fields if available
            field_index = 4
            if 'score' in columns and field_index < len(row):
                data_point['avg_score'] = row[field_index] or 0
                field_index += 1
            if 'centipawn_loss' in columns and field_index < len(row):
                data_point['avg_centipawn_loss'] = row[field_index] or 0
                field_index += 1
            if 'rank' in columns and field_index < len(row):
                data_point['avg_rank'] = row[field_index] or 0
                field_index += 1
            if 'move_complexity' in columns and field_index < len(row):
                data_point['avg_complexity'] = row[field_index] or 0
                field_index += 1
            if 'strategic_value' in columns and field_index < len(row):
                data_point['avg_strategic'] = row[field_index] or 0
                field_index += 1
            
            performance_data.append(data_point)
        
        return performance_data
        
    except Exception as e:
        st.error(f"Error loading performance data: {e}")
        return []

def get_position_performance_data(user_id: int) -> Dict[str, Any]:
    """Get position-specific performance data with proper error handling."""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Check if user has any moves first
        cursor.execute('SELECT COUNT(*) FROM user_moves WHERE user_id = ?', (user_id,))
        total_moves = cursor.fetchone()[0]
        
        if total_moves == 0:
            conn.close()
            return {
                'by_difficulty': [],
                'by_theme': []
            }
        
        # Performance by difficulty with fallback
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN COALESCE(p.difficulty_rating, 1200) < 1200 THEN 'Beginner (< 1200)'
                    WHEN COALESCE(p.difficulty_rating, 1200) < 1600 THEN 'Intermediate (1200-1600)'
                    WHEN COALESCE(p.difficulty_rating, 1200) < 2000 THEN 'Advanced (1600-2000)'
                    ELSE 'Expert (2000+)'
                END as difficulty_range,
                COUNT(*) as total_moves,
                SUM(CASE WHEN um.result = 'correct' OR um.result = 'excellent' OR um.score > 0 THEN 1 ELSE 0 END) as correct_moves
            FROM user_moves um
            LEFT JOIN positions p ON um.position_id = p.id
            WHERE um.user_id = ?
            GROUP BY difficulty_range
            HAVING COUNT(*) > 0
        ''', (user_id,))
        
        difficulty_results = cursor.fetchall()
        
        by_difficulty = []
        for row in difficulty_results:
            diff_range, total, correct = row
            accuracy = round((correct / total * 100), 2) if total > 0 else 0
            by_difficulty.append({
                'difficulty_range': diff_range,
                'total_moves': total,
                'accuracy': accuracy
            })
        
        # Performance by theme (using game phase as fallback)
        cursor.execute('''
            SELECT 
                COALESCE(p.game_phase, 'middlegame') as theme,
                COUNT(*) as total_moves,
                SUM(CASE WHEN um.result = 'correct' OR um.result = 'excellent' OR um.score > 0 THEN 1 ELSE 0 END) as correct_moves
            FROM user_moves um
            LEFT JOIN positions p ON um.position_id = p.id
            WHERE um.user_id = ?
            GROUP BY COALESCE(p.game_phase, 'middlegame')
            HAVING COUNT(*) > 0
        ''', (user_id,))
        
        theme_results = cursor.fetchall()
        
        by_theme = []
        for row in theme_results:
            theme, total, correct = row
            accuracy = round((correct / total * 100), 2) if total > 0 else 0
            by_theme.append({
                'theme': theme.title(),
                'total_moves': total,
                'accuracy': accuracy
            })
        
        conn.close()
        
        return {
            'by_difficulty': by_difficulty,
            'by_theme': by_theme
        }
        
    except Exception as e:
        st.error(f"Error loading position performance data: {e}")
        return {
            'by_difficulty': [],
            'by_theme': []
        }

# Legacy function alias for backward compatibility
def generate_recommendations(user_stats: Dict[str, Any]) -> List[Dict[str, str]]:
    """Legacy function - redirects to enhanced version."""
    return generate_enhanced_recommendations(user_stats)
