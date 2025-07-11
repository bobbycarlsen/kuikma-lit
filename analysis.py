
# =============================================================================
# analysis.py - Advanced Analysis Module for Kuikma
# =============================================================================
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple
import json
import database
from database import get_db_connection
import chess
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def display_analysis():
    """Display comprehensive advanced analysis interface."""
    st.markdown("## 📈 Advanced Analysis")
    
    if 'user_id' not in st.session_state:
        st.error("Please log in to access analysis.")
        return
    
    # Analysis tabs with full implementation
    analysis_tabs = st.tabs([
        "📊 Performance Analysis",
        "🎯 Position Analysis", 
        "📈 Progress Tracking",
        "🔍 Pattern Recognition"
    ])
    
    with analysis_tabs[0]:
        display_performance_analysis_complete()
    
    with analysis_tabs[1]:
        display_position_analysis_complete()
    
    with analysis_tabs[2]:
        display_progress_tracking_complete()
    
    with analysis_tabs[3]:
        display_pattern_recognition_complete()

def display_performance_analysis_complete():
    """Complete implementation of performance analysis."""
    st.markdown("### 📊 Comprehensive Performance Analysis")
    
    user_id = st.session_state.user_id
    
    # Get comprehensive performance data
    performance_summary = get_user_performance_summary(user_id)
    
    if performance_summary.get('total_moves', 0) == 0:
        st.info("📝 Complete some training positions to see performance analysis.")
        return
    
    # Performance overview KPIs
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    with perf_col1:
        total_moves = performance_summary.get('total_moves', 0)
        st.metric("Total Moves", total_moves)
    
    with perf_col2:
        accuracy = performance_summary.get('accuracy', 0)
        st.metric("Overall Accuracy", f"{accuracy:.1f}%")
    
    with perf_col3:
        avg_time = performance_summary.get('average_time', 0)
        st.metric("Average Time", f"{avg_time:.1f}s")
    
    with perf_col4:
        recent_accuracy = performance_summary.get('recent_accuracy', 0)
        st.metric("Recent Accuracy", f"{recent_accuracy:.1f}%")
    
    # Performance by category
    category_stats = performance_summary.get('category_stats', [])
    if category_stats:
        st.markdown("#### 🎯 Performance by Game Phase")
        
        category_df = pd.DataFrame(category_stats)
        fig = px.bar(
            category_df,
            x='category',
            y='accuracy',
            title='Accuracy by Game Phase',
            color='category',
            text='accuracy'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    # Performance by move classification
    classification_stats = performance_summary.get('classification_stats', [])
    if classification_stats:
        st.markdown("#### 🏆 Performance by Move Quality")
        
        class_df = pd.DataFrame(classification_stats)
        fig = px.bar(
            class_df,
            x='classification',
            y='accuracy',
            title='Accuracy by Move Classification',
            color='accuracy',
            text='attempts'
        )
        fig.update_traces(texttemplate='%{text} attempts', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

def display_position_analysis_complete():
    """Complete implementation of position analysis."""
    st.markdown("### 🎯 Advanced Position Analysis")
    
    user_id = st.session_state.user_id
    
    # Position analysis options
    analysis_type = st.selectbox(
        "Choose analysis type:",
        ["Material Balance", "Mobility Analysis", "Spatial Control", "Comparative Analysis"]
    )
    
    if analysis_type == "Material Balance":
        material_analysis = get_material_analysis(user_id)
        if material_analysis:
            display_material_analysis_results(material_analysis)
        else:
            st.info("No material analysis data available.")
    
    elif analysis_type == "Mobility Analysis":
        mobility_analysis = get_mobility_analysis(user_id)
        if mobility_analysis:
            display_mobility_analysis_results(mobility_analysis)
        else:
            st.info("No mobility analysis data available.")
    
    elif analysis_type == "Spatial Control":
        st.info("🚧 Spatial control analysis integration coming soon!")
    
    elif analysis_type == "Comparative Analysis":
        display_comparative_analysis_interface(user_id)

def display_progress_tracking_complete():
    """Complete implementation of progress tracking."""
    st.markdown("### 📈 Progress Tracking & Trends")
    
    user_id = st.session_state.user_id
    
    # Get calendar data for progress tracking
    calendar_data = get_user_calendar_data(user_id)
    
    if not calendar_data:
        st.info("📅 Complete training over multiple days to see progress trends.")
        return
    
    # Progress overview
    prog_col1, prog_col2, prog_col3 = st.columns(3)
    
    total_sessions = len(calendar_data)
    total_accuracy = sum(day['accuracy'] for day in calendar_data) / len(calendar_data) if calendar_data else 0
    total_attempts = sum(day['attempts'] for day in calendar_data)
    
    with prog_col1:
        st.metric("Training Days", total_sessions)
    
    with prog_col2:
        st.metric("Average Daily Accuracy", f"{total_accuracy:.1f}%")
    
    with prog_col3:
        st.metric("Total Attempts", total_attempts)
    
    # Progress chart
    if len(calendar_data) > 1:
        st.markdown("#### 📈 Daily Progress Trend")
        
        calendar_df = pd.DataFrame(calendar_data)
        fig = px.line(
            calendar_df,
            x='date',
            y='accuracy',
            title='Daily Training Accuracy',
            markers=True
        )
        fig.update_layout(yaxis_title="Accuracy (%)", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)
        
        # Activity heatmap
        st.markdown("#### 🔥 Training Activity")
        activity_df = calendar_df[['date', 'attempts', 'accuracy']].copy()
        
        fig2 = px.scatter(
            activity_df,
            x='date',
            y='attempts',
            size='accuracy',
            color='accuracy',
            title='Training Activity & Accuracy',
            labels={'attempts': 'Daily Attempts', 'accuracy': 'Accuracy (%)'}
        )
        st.plotly_chart(fig2, use_container_width=True)

def display_pattern_recognition_complete():
    """Complete implementation of pattern recognition analysis."""
    st.markdown("### 🔍 Pattern Recognition Analysis")
    
    user_id = st.session_state.user_id
    
    # Get recent moves for pattern analysis
    recent_moves = get_filtered_user_moves(user_id, {'limit': 50})
    
    if not recent_moves:
        st.info("🧩 Complete more training positions to enable pattern recognition analysis.")
        return
    
    # Pattern statistics
    pattern_col1, pattern_col2, pattern_col3 = st.columns(3)
    
    # Analyze patterns
    opening_moves = [m for m in recent_moves if m.get('game_phase', {}).get('phase') == 'opening']
    middlegame_moves = [m for m in recent_moves if m.get('game_phase', {}).get('phase') == 'middlegame']
    endgame_moves = [m for m in recent_moves if m.get('game_phase', {}).get('phase') == 'endgame']
    
    with pattern_col1:
        opening_accuracy = sum(1 for m in opening_moves if m.get('result') == 'correct') / len(opening_moves) * 100 if opening_moves else 0
        st.metric("Opening Accuracy", f"{opening_accuracy:.1f}%")
    
    with pattern_col2:
        middlegame_accuracy = sum(1 for m in middlegame_moves if m.get('result') == 'correct') / len(middlegame_moves) * 100 if middlegame_moves else 0
        st.metric("Middlegame Accuracy", f"{middlegame_accuracy:.1f}%")
    
    with pattern_col3:
        endgame_accuracy = sum(1 for m in endgame_moves if m.get('result') == 'correct') / len(endgame_moves) * 100 if endgame_moves else 0
        st.metric("Endgame Accuracy", f"{endgame_accuracy:.1f}%")
    
    # Pattern trends
    st.markdown("#### 🧩 Pattern Recognition Trends")
    
    # Time-based pattern analysis
    time_patterns = []
    for move in recent_moves:
        time_cat = move.get('time_category', {})
        time_patterns.append({
            'Time Category': time_cat.get('label', 'Unknown'),
            'Result': 'Correct' if move.get('result') == 'correct' else 'Incorrect',
            'Phase': move.get('game_phase', {}).get('label', 'Unknown')
        })
    
    if time_patterns:
        pattern_df = pd.DataFrame(time_patterns)
        fig = px.histogram(
            pattern_df,
            x='Time Category',
            color='Result',
            title='Performance by Thinking Time',
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)

# Helper functions for enhanced analysis
def display_material_analysis_results(material_analysis: Dict[str, Any]):
    """Display material analysis results."""
    st.markdown("#### ⚖️ Material Balance Performance")
    
    imbalance_perf = material_analysis.get('imbalance_performance', [])
    
    if imbalance_perf:
        imbalance_df = pd.DataFrame(imbalance_perf)
        fig = px.bar(
            imbalance_df,
            x='imbalance_range',
            y='accuracy',
            title='Accuracy by Material Imbalance',
            color='accuracy',
            text='total'
        )
        fig.update_traces(texttemplate='%{text} games', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    # Piece-specific performance
    piece_perf = material_analysis.get('piece_performance', [])
    if piece_perf:
        st.markdown("#### 🏆 Performance with Piece Advantages")
        
        piece_df = pd.DataFrame(piece_perf)
        fig2 = px.bar(
            piece_df,
            x='piece_advantage',
            y='accuracy',
            title='Accuracy with Different Piece Advantages',
            color='accuracy'
        )
        st.plotly_chart(fig2, use_container_width=True)

def display_mobility_analysis_results(mobility_analysis: Dict[str, Any]):
    """Display mobility analysis results."""
    st.markdown("#### ⚡ Mobility Analysis Performance")
    
    mobility_buckets = mobility_analysis.get('mobility_buckets', [])
    
    if mobility_buckets:
        mobility_df = pd.DataFrame(mobility_buckets)
        fig = px.bar(
            mobility_df,
            x='mobility_advantage',
            y='accuracy',
            title='Performance by Mobility Advantage',
            color='accuracy',
            text='total'
        )
        fig.update_traces(texttemplate='%{text} positions', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

def display_comparative_analysis_interface(user_id: int):
    """Display comparative analysis interface."""
    st.markdown("#### 🔬 Comparative Analysis")
    
    factor1 = st.selectbox("First factor:", ['time_taken', 'material', 'center_control'])
    factor2 = st.selectbox("Second factor:", ['result', 'accuracy', 'classification'])
    
    if st.button("🔍 Run Comparative Analysis"):
        comparison_result = get_comparative_analysis(user_id, factor1, factor2)
        
        if 'analysis' in comparison_result:
            analysis_data = comparison_result['analysis']
            
            if isinstance(analysis_data, list) and analysis_data:
                comp_df = pd.DataFrame(analysis_data)
                
                if factor1 == 'time_taken' and factor2 == 'result':
                    fig = px.bar(
                        comp_df,
                        x='time_bucket',
                        y='accuracy',
                        title=f'Accuracy by {factor1.replace("_", " ").title()}',
                        text='attempts'
                    )
                    fig.update_traces(texttemplate='%{text} attempts', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display insights
                for row in analysis_data:
                    if 'insight' in row:
                        st.info(f"💡 {row['insight']}")



def get_user_performance_summary(user_id):
    """
    Get comprehensive summary of user's training performance with enhanced mobile-friendly data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get basic stats
    cursor.execute('''
        SELECT 
            COUNT(*) as total_attempts,
            SUM(CASE WHEN result = 'pass' THEN 1 ELSE 0 END) as correct_moves,
            AVG(time_taken) as avg_time,
            MIN(time_taken) as min_time,
            MAX(time_taken) as max_time,
            COUNT(DISTINCT position_id) as unique_positions_attempted
        FROM user_moves
        WHERE user_id = ?
    ''', (user_id,))
    
    summary = dict(cursor.fetchone())
    
    # Calculate accuracy
    summary['accuracy'] = (summary['correct_moves'] / summary['total_attempts']) * 100 if summary['total_attempts'] > 0 else 0
    
    # Get performance by move category (opening, middle game, endgame)
    cursor.execute('''
        SELECT 
            CASE 
                WHEN p.fullmove_number <= 15 THEN 'opening'
                WHEN p.fullmove_number <= 32 THEN 'middlegame'
                ELSE 'endgame'
            END as category,
            COUNT(*) as attempts,
            SUM(CASE WHEN um.result = 'pass' THEN 1 ELSE 0 END) as correct,
            AVG(um.time_taken) as avg_time
        FROM user_moves um
        JOIN positions p ON um.position_id = p.id
        WHERE um.user_id = ?
        GROUP BY category
    ''', (user_id,))
    
    category_stats = []
    for row in cursor.fetchall():
        category_dict = dict(row)
        category_dict['accuracy'] = (category_dict['correct'] / category_dict['attempts']) * 100 if category_dict['attempts'] > 0 else 0
        category_stats.append(category_dict)
    
    summary['category_stats'] = category_stats
    
    # Get performance by move classification
    cursor.execute('''
        SELECT 
            m.classification,
            COUNT(*) as attempts,
            SUM(CASE WHEN um.result = 'pass' THEN 1 ELSE 0 END) as correct,
            AVG(um.time_taken) as avg_time
        FROM user_moves um
        JOIN moves m ON um.move_id = m.id
        WHERE um.user_id = ?
        GROUP BY m.classification
        ORDER BY attempts DESC
    ''', (user_id,))
    
    classification_stats = []
    for row in cursor.fetchall():
        class_dict = dict(row)
        class_dict['accuracy'] = (class_dict['correct'] / class_dict['attempts']) * 100 if class_dict['attempts'] > 0 else 0
        classification_stats.append(class_dict)
    
    summary['classification_stats'] = classification_stats
    
    # Get performance by color
    cursor.execute('''
        SELECT 
            p.turn as color,
            COUNT(*) as attempts,
            SUM(CASE WHEN um.result = 'pass' THEN 1 ELSE 0 END) as correct,
            AVG(um.time_taken) as avg_time
        FROM user_moves um
        JOIN positions p ON um.position_id = p.id
        WHERE um.user_id = ?
        GROUP BY p.turn
    ''', (user_id,))
    
    color_stats = []
    for row in cursor.fetchall():
        color_dict = dict(row)
        color_dict['accuracy'] = (color_dict['correct'] / color_dict['attempts']) * 100 if color_dict['attempts'] > 0 else 0
        color_stats.append(color_dict)
    
    summary['color_stats'] = color_stats
    
    # Get performance by top N ranking
    cursor.execute('''
        SELECT 
            CASE 
                WHEN m.rank = 1 THEN 'rank_1'
                WHEN m.rank <= 3 THEN 'rank_2_3'
                WHEN m.rank <= 5 THEN 'rank_4_5'
                ELSE 'rank_6_plus' 
            END as rank_group,
            COUNT(*) as attempts,
            SUM(CASE WHEN um.result = 'pass' THEN 1 ELSE 0 END) as correct,
            AVG(um.time_taken) as avg_time
        FROM user_moves um
        JOIN moves m ON um.move_id = m.id
        WHERE um.user_id = ?
        GROUP BY rank_group
    ''', (user_id,))
    
    rank_stats = []
    for row in cursor.fetchall():
        rank_dict = dict(row)
        rank_dict['accuracy'] = (rank_dict['correct'] / rank_dict['attempts']) * 100 if rank_dict['attempts'] > 0 else 0
        
        # Make labels more mobile-friendly
        rank_labels = {
            'rank_1': 'Best Move',
            'rank_2_3': 'Top 3 Moves',
            'rank_4_5': 'Top 5 Moves',
            'rank_6_plus': 'Other Moves'
        }
        rank_dict['rank_label'] = rank_labels.get(rank_dict['rank_group'], rank_dict['rank_group'])
        rank_stats.append(rank_dict)
    
    summary['rank_stats'] = rank_stats
    
    # Get recent performance trend (last 20 moves)
    cursor.execute('''
        SELECT 
            um.result,
            um.time_taken,
            um.timestamp,
            m.classification,
            p.fullmove_number
        FROM user_moves um
        JOIN moves m ON um.move_id = m.id
        JOIN positions p ON um.position_id = p.id
        WHERE um.user_id = ?
        ORDER BY um.timestamp DESC
        LIMIT 20
    ''', (user_id,))
    
    recent_moves = [dict(row) for row in cursor.fetchall()]
    summary['recent_moves'] = recent_moves
    
    # Calculate recent accuracy
    if recent_moves:
        recent_correct = sum(1 for move in recent_moves if move['result'] == 'pass')
        summary['recent_accuracy'] = (recent_correct / len(recent_moves)) * 100
    else:
        summary['recent_accuracy'] = 0
    
    conn.close()
    return summary

def get_material_analysis(user_id):
    """Get material analysis with corrected database schema."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Get positions with user moves (simplified query)
    cursor.execute('''
        SELECT 
            um.result,
            um.time_taken,
            p.fen,
            p.turn
        FROM user_moves um
        JOIN positions p ON um.position_id = p.id
        WHERE um.user_id = ?
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return None
    
    # Basic material analysis without metadata dependency
    imbalance_buckets = {
        'equal': {'total': 0, 'correct': 0},
        'advantage': {'total': 0, 'correct': 0},
        'disadvantage': {'total': 0, 'correct': 0}
    }
    
    for row in rows:
        result = row[0]
        
        # Simple material categorization based on FEN
        fen = row[2]
        try:
            board = chess.Board(fen)
            material_diff = calculate_simple_material_difference(board)
            
            if abs(material_diff) < 1:
                bucket = 'equal'
            elif material_diff > 0:
                bucket = 'advantage'
            else:
                bucket = 'disadvantage'
            
            imbalance_buckets[bucket]['total'] += 1
            if result in ['correct', 'excellent']:
                imbalance_buckets[bucket]['correct'] += 1
                
        except:
            continue
    
    # Convert to display format
    imbalance_performance = []
    for bucket, data in imbalance_buckets.items():
        if data['total'] > 0:
            accuracy = (data['correct'] / data['total']) * 100
            imbalance_performance.append({
                'imbalance_range': bucket.title(),
                'total': data['total'],
                'correct': data['correct'],
                'accuracy': round(accuracy, 2)
            })
    
    return {
        'imbalance_performance': imbalance_performance,
        'piece_performance': [],  # Simplified for now
        'summary': {
            'total_positions': len(rows),
            'material_positions': len(rows)
        }
    }

def calculate_simple_material_difference(board: chess.Board) -> float:
    """Calculate simple material difference."""
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }
    
    white_material = 0
    black_material = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type in piece_values:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                white_material += value
            else:
                black_material += value
    
    return white_material - black_material

def get_mobility_analysis(user_id):
    """Get mobility analysis with simplified approach."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Simplified mobility analysis
    cursor.execute('''
        SELECT 
            um.result,
            um.time_taken,
            p.fen,
            p.fullmove_number
        FROM user_moves um
        JOIN positions p ON um.position_id = p.id
        WHERE um.user_id = ?
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return None
    
    # Basic categorization
    mobility_buckets = {
        'opening': {'total': 0, 'correct': 0},
        'middlegame': {'total': 0, 'correct': 0},
        'endgame': {'total': 0, 'correct': 0}
    }
    
    for row in rows:
        result = row[0]
        move_number = row[3]
        
        # Categorize by game phase
        if move_number <= 15:
            phase = 'opening'
        elif move_number <= 30:
            phase = 'middlegame'
        else:
            phase = 'endgame'
        
        mobility_buckets[phase]['total'] += 1
        if result in ['correct', 'excellent']:
            mobility_buckets[phase]['correct'] += 1
    
    # Convert to display format
    mobility_analysis = []
    for phase, data in mobility_buckets.items():
        if data['total'] > 0:
            accuracy = (data['correct'] / data['total']) * 100
            mobility_analysis.append({
                'mobility_advantage': f"{phase.title()} Phase",
                'total': data['total'],
                'correct': data['correct'],
                'accuracy': round(accuracy, 2),
                'category': phase
            })
    
    return {
        'mobility_buckets': mobility_analysis,
        'summary': {
            'total_positions': len(rows),
            'mobility_positions': len(rows)
        }
    }


def get_filtered_user_moves(user_id, filters=None):
    """
    Get user moves with enhanced filtering options for mobile display.
    """
    filters = filters or {}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enhanced base query with more data
    query = '''
        SELECT 
            um.id, um.position_id, um.move_id, um.time_taken, um.result, um.timestamp,
            p.fen, p.turn, p.fullmove_number, p.position_classification,
            m.move, m.score, m.centipawn_loss, m.classification, m.rank,
            m.tactics, m.position_impact
        FROM user_moves um
        JOIN positions p ON um.position_id = p.id
        JOIN moves m ON um.move_id = m.id
        WHERE um.user_id = ?
    '''
    
    params = [user_id]
    
    # Enhanced filters
    if filters.get('move_number'):
        query += ' AND p.fullmove_number = ?'
        params.append(filters['move_number'])
        
    if filters.get('color'):
        query += ' AND p.turn = ?'
        params.append(filters['color'])
        
    if filters.get('result'):
        query += ' AND um.result = ?'
        params.append(filters['result'])
        
    if filters.get('category'):
        if filters['category'] == 'opening':
            query += ' AND p.fullmove_number <= 15'
        elif filters['category'] == 'middlegame':
            query += ' AND p.fullmove_number > 15 AND p.fullmove_number <= 32'
        elif filters['category'] == 'endgame':
            query += ' AND p.fullmove_number > 32'
    
    if filters.get('classification'):
        query += ' AND m.classification = ?'
        params.append(filters['classification'])
    
    if filters.get('time_range'):
        if filters['time_range'] == 'fast':
            query += ' AND um.time_taken < 10'
        elif filters['time_range'] == 'normal':
            query += ' AND um.time_taken BETWEEN 10 AND 30'
        elif filters['time_range'] == 'slow':
            query += ' AND um.time_taken > 30'
    
    if filters.get('date_range'):
        query += ' AND DATE(um.timestamp) >= ?'
        params.append(filters['date_range'])
    
    # Order by timestamp descending
    query += ' ORDER BY um.timestamp DESC'
    
    # Apply limit if provided
    limit = filters.get('limit', 50)  # Default to 50 for mobile
    query += ' LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    moves = []
    
    for row in cursor.fetchall():
        move_dict = dict(row)
        
        # Parse JSON fields
        move_dict['position_classification'] = json.loads(move_dict['position_classification']) if move_dict['position_classification'] else []
        move_dict['tactics'] = json.loads(move_dict['tactics']) if move_dict['tactics'] else []
        move_dict['position_impact'] = json.loads(move_dict['position_impact']) if move_dict['position_impact'] else {}
        
        # Add mobile-friendly computed fields
        move_dict['game_phase'] = get_game_phase(move_dict['fullmove_number'])
        move_dict['performance_level'] = get_performance_level(move_dict['classification'])
        move_dict['time_category'] = get_time_category(move_dict['time_taken'])
        
        moves.append(move_dict)
    
    conn.close()
    return moves

def get_game_phase(fullmove_number):
    """Get mobile-friendly game phase description."""
    if fullmove_number <= 15:
        return {'phase': 'opening', 'emoji': '🌅', 'label': 'Opening'}
    elif fullmove_number <= 30:
        return {'phase': 'middlegame', 'emoji': '⚔️', 'label': 'Middlegame'}
    else:
        return {'phase': 'endgame', 'emoji': '🏰', 'label': 'Endgame'}

def get_performance_level(classification):
    """Get mobile-friendly performance level."""
    levels = {
        'great': {'level': 'excellent', 'emoji': '🎯', 'color': '#28a745'},
        'good': {'level': 'good', 'emoji': '✅', 'color': '#20c997'},
        'inaccuracy': {'level': 'okay', 'emoji': '⚠️', 'color': '#ffc107'},
        'mistake': {'level': 'poor', 'emoji': '❌', 'color': '#fd7e14'},
        'blunder': {'level': 'bad', 'emoji': '💥', 'color': '#dc3545'}
    }
    return levels.get(classification, {'level': 'unknown', 'emoji': '❓', 'color': '#6c757d'})

def get_time_category(time_taken):
    """Get mobile-friendly time category."""
    if time_taken < 5:
        return {'category': 'lightning', 'emoji': '⚡', 'label': 'Lightning'}
    elif time_taken < 15:
        return {'category': 'fast', 'emoji': '🚀', 'label': 'Fast'}
    elif time_taken < 30:
        return {'category': 'normal', 'emoji': '🤔', 'label': 'Thoughtful'}
    elif time_taken < 60:
        return {'category': 'slow', 'emoji': '🐌', 'label': 'Deliberate'}
    else:
        return {'category': 'very_slow', 'emoji': '🔍', 'label': 'Deep Analysis'}

def get_user_calendar_data(user_id):
    """
    Get enhanced training activity by date for calendar visualization.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as attempts,
            SUM(CASE WHEN result = 'pass' THEN 1 ELSE 0 END) as correct,
            AVG(time_taken) as avg_time,
            COUNT(DISTINCT position_id) as unique_positions,
            MIN(time_taken) as fastest_time,
            MAX(time_taken) as slowest_time
        FROM user_moves
        WHERE user_id = ?
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        LIMIT 90
    ''', (user_id,))
    
    calendar_data = []
    for row in cursor.fetchall():
        date_data = dict(row)
        date_data['accuracy'] = (date_data['correct'] / date_data['attempts']) * 100 if date_data['attempts'] > 0 else 0
        
        # Add mobile-friendly activity level
        attempts = date_data['attempts']
        if attempts >= 20:
            date_data['activity_level'] = 'high'
            date_data['activity_emoji'] = '🔥'
        elif attempts >= 10:
            date_data['activity_level'] = 'medium'
            date_data['activity_emoji'] = '💪'
        elif attempts >= 5:
            date_data['activity_level'] = 'low'
            date_data['activity_emoji'] = '👍'
        else:
            date_data['activity_level'] = 'minimal'
            date_data['activity_emoji'] = '📚'
        
        calendar_data.append(date_data)
    
    conn.close()
    return calendar_data

def get_comparative_analysis(user_id, factor1, factor2):
    """
    Enhanced comparative analysis between two factors with mobile optimization.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    valid_factors = ['time_taken', 'center_control', 'pawn_structure', 'king_safety', 'material', 'mobility']
    
    if factor1 not in valid_factors or factor2 not in valid_factors:
        conn.close()
        return {"error": f"Invalid factors. Valid options: {', '.join(valid_factors)}"}
    
    # Enhanced time vs result analysis
    if factor1 == 'time_taken' and factor2 == 'result':
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN time_taken < 5 THEN 'Lightning (<5s)'
                    WHEN time_taken < 15 THEN 'Fast (5-15s)'
                    WHEN time_taken < 30 THEN 'Normal (15-30s)'
                    WHEN time_taken < 60 THEN 'Slow (30-60s)'
                    ELSE 'Very Slow (>60s)'
                END as time_bucket,
                COUNT(*) as attempts,
                SUM(CASE WHEN result = 'pass' THEN 1 ELSE 0 END) as correct,
                AVG(time_taken) as avg_time_in_bucket,
                MIN(time_taken) as min_time,
                MAX(time_taken) as max_time
            FROM user_moves
            WHERE user_id = ?
            GROUP BY time_bucket
            ORDER BY avg_time_in_bucket
        ''', (user_id,))
        
        analysis = []
        for row in cursor.fetchall():
            bucket_data = dict(row)
            bucket_data['accuracy'] = (bucket_data['correct'] / bucket_data['attempts']) * 100 if bucket_data['attempts'] > 0 else 0
            
            # Add mobile-friendly insights
            if bucket_data['accuracy'] > 70:
                bucket_data['performance'] = 'strong'
                bucket_data['insight'] = f"Strong performance in {bucket_data['time_bucket'].lower()} decisions"
            elif bucket_data['accuracy'] > 50:
                bucket_data['performance'] = 'average'
                bucket_data['insight'] = f"Average performance in {bucket_data['time_bucket'].lower()} decisions"
            else:
                bucket_data['performance'] = 'weak'
                bucket_data['insight'] = f"Room for improvement in {bucket_data['time_bucket'].lower()} decisions"
            
            analysis.append(bucket_data)
    
    # Enhanced material vs performance analysis
    elif factor1 == 'material' and factor2 == 'result':
        cursor.execute('''
            SELECT 
                um.result,
                p.metadata,
                um.time_taken
            FROM user_moves um
            JOIN positions p ON um.position_id = p.id
            WHERE um.user_id = ?
        ''', (user_id,))
        
        rows = cursor.fetchall()
        material_buckets = {
            'Major Advantage (+3)': {'total': 0, 'correct': 0, 'times': []},
            'Slight Advantage (+1/+2)': {'total': 0, 'correct': 0, 'times': []},
            'Equal Material': {'total': 0, 'correct': 0, 'times': []},
            'Slight Disadvantage (-1/-2)': {'total': 0, 'correct': 0, 'times': []},
            'Major Disadvantage (-3)': {'total': 0, 'correct': 0, 'times': []}
        }
        
        for row in rows:
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            material = metadata.get('material', {})
            
            if material:
                imbalance = material.get('imbalance', 0)
                
                if imbalance >= 3:
                    bucket = 'Major Advantage (+3)'
                elif imbalance >= 1:
                    bucket = 'Slight Advantage (+1/+2)'
                elif imbalance <= -3:
                    bucket = 'Major Disadvantage (-3)'
                elif imbalance <= -1:
                    bucket = 'Slight Disadvantage (-1/-2)'
                else:
                    bucket = 'Equal Material'
                
                material_buckets[bucket]['total'] += 1
                material_buckets[bucket]['times'].append(row['time_taken'])
                if row['result'] == 'pass':
                    material_buckets[bucket]['correct'] += 1
        
        analysis = []
        for bucket, data in material_buckets.items():
            if data['total'] > 0:
                accuracy = (data['correct'] / data['total']) * 100
                avg_time = sum(data['times']) / len(data['times']) if data['times'] else 0
                
                analysis.append({
                    'material_situation': bucket,
                    'total': data['total'],
                    'correct': data['correct'],
                    'accuracy': accuracy,
                    'avg_time': avg_time
                })
    
    else:
        # Placeholder for other complex comparisons
        analysis = {
            "message": f"Comparison between {factor1} and {factor2} requires advanced analysis",
            "factors": [factor1, factor2],
            "available_comparisons": ["time_taken vs result", "material vs result"]
        }
    
    conn.close()
    return {
        'analysis': analysis,
        'factor1': factor1,
        'factor2': factor2,
        'comparison_type': f"{factor1}_vs_{factor2}"
    }

