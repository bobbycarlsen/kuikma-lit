# game_analysis.py - Game Analysis for Kuikma Chess Engine
import streamlit as st
import sqlite3
import chess
import chess.pgn
import chess.svg
import math
import io
import json
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import database
import auth
from game_html_generator import GameHTMLGenerator
from pathlib import Path

def display_game_analysis():
    """Main entry point for game analysis with simplified UX."""
    
    # Always show back button if we're in analysis mode
    if st.session_state.get('ga_mode') == 'analyzing':
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("🔙 Back to Game Selection", type="secondary", use_container_width=True):
                # Clear all analysis state and go back
                for key in list(st.session_state.keys()):
                    if key.startswith('ga_'):
                        del st.session_state[key]
                st.rerun()
        with col2:
            st.markdown("<h2 style='text-align: center; margin: 0;'>🎮 Game Analysis</h2>", unsafe_allow_html=True)
        with col3:
            if st.button("🔄 Reset Analysis", type="secondary", use_container_width=True):
                # Reset analysis but keep the game
                st.session_state['ga_position_index'] = 0
                st.rerun()
    else:
        # Clean header
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 2rem;">
            <h1 style="color: #1a202c; font-size: 2.5rem; font-weight: 300; margin: 0;">🎮 Game Analysis</h1>
            <p style="color: #718096; font-size: 1.1rem; margin-top: 0.5rem;">Choose a game to analyze</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Check if we're in analysis mode
    if st.session_state.get('ga_mode') == 'analyzing':
        display_game_analysis_interface()
    else:
        display_game_selection_interface()


def display_game_selection_interface():
    """Simplified game selection interface."""
    
    st.markdown("### 📂 Select a Game to Analyze")
    
    # Simple tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🗄️ Browse Database", "📋 Paste PGN", "📤 Upload PGN", "🎲 Random Game"])
    
    with tab1:
        handle_database_browser()
    
    with tab2:
        handle_pgn_paste()
    
    with tab3:
        handle_pgn_upload()
    
    with tab4:
        handle_random_game()


def handle_database_browser():
    """Enhanced database browser with comprehensive search filters."""
    st.markdown("#### 🔍 Browse Your Game Database")
    
    # Quick stats
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM games")
        total_games = cursor.fetchone()['total']
        conn.close()
        st.info(f"📊 Total games in database: {total_games}")
    except Exception as e:
        st.error(f"❌ Database error: {e}")
        return
    
    # Enhanced search form with more filters
    with st.form("game_search"):
        st.markdown("##### 🔍 Search Filters")
        
        # Row 1: Players and Result
        col1, col2, col3 = st.columns(3)
        with col1:
            player_name = st.text_input("Player Name", placeholder="e.g., Carlsen, Magnus")
        with col2:
            result_filter = st.selectbox("Result", ["All", "1-0", "0-1", "1/2-1/2"])
        with col3:
            event_filter = st.text_input("Event", placeholder="e.g., World Championship")
        
        # Row 2: Advanced filters
        col4, col5, col6 = st.columns(3)
        with col4:
            opening_filter = st.text_input("Opening", placeholder="e.g., Sicilian, French")
        with col5:
            min_elo = st.number_input("Min ELO", min_value=0, max_value=3000, value=0, step=50)
        with col6:
            max_elo = st.number_input("Max ELO", min_value=0, max_value=3000, value=3000, step=50)
        
        # Row 3: Date and Move filters
        col7, col8, col9 = st.columns(3)
        with col7:
            date_from = st.date_input("Date From", value=None)
        with col8:
            date_to = st.date_input("Date To", value=None)
        with col9:
            min_moves = st.number_input("Min Moves", min_value=0, value=0, step=5)
        
        # Search buttons
        search_col1, search_col2, search_col3, search_col4 = st.columns(4)
        with search_col1:
            search_clicked = st.form_submit_button("🔍 Advanced Search", use_container_width=True, type="primary")
        with search_col2:
            quick_search_clicked = st.form_submit_button("⚡ Quick Search", use_container_width=True)
        with search_col3:
            load_all_clicked = st.form_submit_button("📚 Load All", use_container_width=True)
        with search_col4:
            clear_clicked = st.form_submit_button("🗑️ Clear Results", use_container_width=True)
    
    # Handle search with enhanced filters
    if clear_clicked:
        if 'search_results' in st.session_state:
            del st.session_state['search_results']
        st.rerun()
    
    if search_clicked or quick_search_clicked or load_all_clicked:
        try:
            conn = database.get_db_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check column names
            cursor.execute("PRAGMA table_info(games)")
            columns = [col['name'] for col in cursor.fetchall()]
            
            # Build query based on available columns
            if 'white_player' in columns:
                base_sql = """SELECT id, white_player as white, black_player as black, 
                             white_elo, black_elo, result, date, event, opening, 
                             COALESCE(total_moves, 0) as moves FROM games"""
            else:
                base_sql = """SELECT id, white, black, white_elo, black_elo, result, date, 
                             event, opening, COALESCE(moves, 0) as moves FROM games"""
            
            where_clauses = []
            params = []
            
            # Apply filters based on search type
            if search_clicked or quick_search_clicked:
                # Player filter
                if player_name:
                    if 'white_player' in columns:
                        where_clauses.append("(white_player LIKE ? OR black_player LIKE ?)")
                    else:
                        where_clauses.append("(white LIKE ? OR black LIKE ?)")
                    params.extend([f"%{player_name}%", f"%{player_name}%"])
                
                # Result filter
                if result_filter != "All":
                    where_clauses.append("result = ?")
                    params.append(result_filter)
                
                # Advanced filters (only for full search)
                if search_clicked:
                    if event_filter:
                        where_clauses.append("event LIKE ?")
                        params.append(f"%{event_filter}%")
                    
                    if opening_filter:
                        where_clauses.append("opening LIKE ?")
                        params.append(f"%{opening_filter}%")
                    
                    if min_elo > 0:
                        where_clauses.append("(COALESCE(white_elo, 0) >= ? OR COALESCE(black_elo, 0) >= ?)")
                        params.extend([min_elo, min_elo])
                    
                    if max_elo < 3000:
                        where_clauses.append("(COALESCE(white_elo, 9999) <= ? OR COALESCE(black_elo, 9999) <= ?)")
                        params.extend([max_elo, max_elo])
                    
                    if date_from:
                        where_clauses.append("date >= ?")
                        params.append(date_from.strftime('%Y.%m.%d'))
                    
                    if date_to:
                        where_clauses.append("date <= ?")
                        params.append(date_to.strftime('%Y.%m.%d'))
                    
                    if min_moves > 0:
                        moves_col = 'total_moves' if 'total_moves' in columns else 'moves'
                        where_clauses.append(f"COALESCE({moves_col}, 0) >= ?")
                        params.append(min_moves)
            
            # Build final query
            sql = base_sql
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # Limit results
            limit = 100 if search_clicked else 50 if quick_search_clicked else 25
            sql += f" ORDER BY id DESC LIMIT {limit}"
            
            cursor.execute(sql, params)
            games = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            st.session_state['search_results'] = games
            
            if games:
                st.success(f"✅ Found {len(games)} games")
            else:
                st.warning("🔍 No games found matching your criteria")
            
        except Exception as e:
            st.error(f"❌ Search error: {e}")
    
    # Display enhanced results
    if 'search_results' in st.session_state:
        games = st.session_state['search_results']
        display_enhanced_games_grid(games)


def handle_pgn_paste():
    """Simplified PGN paste handler."""
    st.markdown("#### 📋 Paste PGN Content")
    
    pgn_content = st.text_area(
        "Paste your PGN here:",
        height=200,
        placeholder="""[Event "Example Game"]
[Site "Chess.com"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1.e4 e5 2.Nf3 Nc6 3.Bb5 a6..."""
    )
    
    if pgn_content.strip():
        if st.button("🎯 Analyze Game", type="primary", use_container_width=True):
            try:
                games = parse_pgn_content(pgn_content)
                if games:
                    start_analysis(games[0])
                    st.success("✅ Game loaded!")
                    st.rerun()
                else:
                    st.error("❌ No valid games found in PGN")
            except Exception as e:
                st.error(f"❌ Error parsing PGN: {e}")


def handle_pgn_upload():
    """Simplified PGN upload handler."""
    st.markdown("#### 📤 Upload PGN File")
    
    uploaded_file = st.file_uploader("Choose a PGN file", type=['pgn', 'txt'])
    
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode('utf-8')
            games = parse_pgn_content(content)
            
            if games:
                if len(games) == 1:
                    if st.button("🎯 Analyze Game", type="primary", use_container_width=True):
                        start_analysis(games[0])
                        st.success("✅ Game loaded!")
                        st.rerun()
                else:
                    selected_game = st.selectbox(
                        "Select game to analyze:",
                        range(len(games)),
                        format_func=lambda i: f"Game {i+1}: {games[i].headers.get('White', 'Unknown')} vs {games[i].headers.get('Black', 'Unknown')}"
                    )
                    
                    if st.button("🎯 Analyze Selected Game", type="primary", use_container_width=True):
                        start_analysis(games[selected_game])
                        st.success("✅ Game loaded!")
                        st.rerun()
            else:
                st.error("❌ No valid games found in file")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")


def handle_random_game():
    """Simplified random game handler."""
    st.markdown("#### 🎲 Random Game Selection")
    
    if st.button("🎲 Load Random Game", type="primary", use_container_width=True):
        try:
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM games ORDER BY RANDOM() LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            
            if result:
                load_game_from_database(result['id'])
            else:
                st.error("❌ No games found in database")
        except Exception as e:
            st.error(f"❌ Error loading random game: {e}")


def load_game_from_database(game_id: int):
    """Load game from database and start analysis."""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Try to get PGN text first
        cursor.execute("PRAGMA table_info(games)")
        columns = [col['name'] for col in cursor.fetchall()]
        
        if 'pgn_text' in columns:
            cursor.execute("SELECT pgn_text FROM games WHERE id = ?", (game_id,))
            result = cursor.fetchone()
            if result and result['pgn_text']:
                games = parse_pgn_content(result['pgn_text'])
                if games:
                    start_analysis(games[0])
                    conn.close()
                    st.rerun()
                    return
        
        # Fallback to structured data
        if 'white_player' in columns:
            query = """
                SELECT white_player, black_player, result, date, event, 
                       moves_data, positions_data 
                FROM games WHERE id = ?
            """
        else:
            query = """
                SELECT white, black, result, date, event, 
                       moves_data, positions_data 
                FROM games WHERE id = ?
            """
        
        cursor.execute(query, (game_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            white, black, result_str, date, event, moves_data, positions_data = result
            
            # Create a simple game object
            game = chess.pgn.Game()
            game.headers['White'] = white or 'Unknown'
            game.headers['Black'] = black or 'Unknown'
            game.headers['Result'] = result_str or '*'
            game.headers['Date'] = date or 'Unknown'
            game.headers['Event'] = event or 'Unknown'
            
            # Add moves if available
            if moves_data:
                try:
                    moves = json.loads(moves_data) if isinstance(moves_data, str) else moves_data
                    board = chess.Board()
                    node = game
                    
                    for move_data in moves:
                        uci = move_data.get('uci', '')
                        if uci:
                            try:
                                move = chess.Move.from_uci(uci)
                                if move in board.legal_moves:
                                    node = node.add_variation(move)
                                    board.push(move)
                            except:
                                break
                except:
                    pass
            
            start_analysis(game)
            st.rerun()
        else:
            st.error(f"❌ Game {game_id} not found")
            
    except Exception as e:
        st.error(f"❌ Error loading game: {e}")


def show_game_preview(game: Dict):
    """Show a quick preview of the game in an expander."""
    with st.expander(f"📋 Preview: {game.get('white', 'Unknown')} vs {game.get('black', 'Unknown')}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Game Information:**")
            st.markdown(f"• **White:** {game.get('white', 'Unknown')}")
            st.markdown(f"• **Black:** {game.get('black', 'Unknown')}")
            st.markdown(f"• **Result:** {game.get('result', '*')}")
            st.markdown(f"• **Date:** {game.get('date', 'Unknown')}")
        
        with col2:
            st.markdown("**Details:**")
            st.markdown(f"• **Event:** {game.get('event', 'Unknown')}")
            st.markdown(f"• **Moves:** {game.get('moves', 0)}")
            st.markdown(f"• **Opening:** {game.get('opening', 'Unknown')[:30]}...")
            st.markdown(f"• **ELOs:** {game.get('white_elo', '?')} / {game.get('black_elo', '?')}")


def start_analysis(game: chess.pgn.Game):
    """Start analyzing the given game with enhanced calculations."""
    st.session_state['ga_mode'] = 'analyzing'
    st.session_state['ga_current_game'] = game
    st.session_state['ga_position_index'] = 0
    
    # Calculate positions with enhanced analysis
    with st.spinner("🔄 Calculating positions and analysis..."):
        positions = calculate_enhanced_positions(game)
        st.session_state['ga_positions'] = positions
        
        # Pre-calculate critical positions
        critical_positions = identify_critical_positions(positions)
        st.session_state['ga_critical_positions'] = critical_positions
        
        # Calculate game statistics
        game_stats = calculate_comprehensive_game_statistics(positions)
        st.session_state['ga_game_stats'] = game_stats


def display_game_analysis_interface():
    """Display the main analysis interface."""
    game = st.session_state.get('ga_current_game')
    if not game:
        st.error("❌ No game loaded")
        return
    
    # Game header
    headers = game.headers
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; text-align: center;">
        <h2 style="margin: 0 0 1rem 0;">{headers.get('White', 'Unknown')} vs {headers.get('Black', 'Unknown')}</h2>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <span><strong>Event:</strong> {headers.get('Event', 'Unknown')}</span>
            <span><strong>Date:</strong> {headers.get('Date', 'Unknown')}</span>
            <span><strong>Result:</strong> {headers.get('Result', '*')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Analysis tabs with all advanced features
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Interactive Board", 
        "📊 Evaluation & Metrics", 
        "🔍 Critical Positions", 
        "🗺️ Spatial Analysis",
        "📈 Game Statistics",
        "💾 Save & Export"
    ])
    
    with tab1:
        display_enhanced_interactive_board()
    
    with tab2:
        display_evaluation_and_metrics()
    
    with tab3:
        display_critical_positions_analysis()
    
    with tab4:
        display_spatial_analysis_tab()
    
    with tab5:
        display_comprehensive_game_statistics()
    
    with tab6:
        display_advanced_export_options()


def display_enhanced_interactive_board():
    """Enhanced interactive board with comprehensive position analysis."""
    positions = st.session_state.get('ga_positions', [])
    if not positions:
        st.error("❌ No positions calculated")
        return
    
    current_index = st.session_state.get('ga_position_index', 0)
    max_index = len(positions) - 1
    
    # Navigation controls
    st.markdown("#### 🎯 Navigate Through Game")
    
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([4, 1, 1, 1, 1])
    
    with nav_col1:
        # Position slider with callback
        new_index = st.slider(
            "Move:",
            min_value=0,
            max_value=max_index,
            value=current_index,
            key="position_slider"
        )
        # Update position if slider changed
        if new_index != current_index:
            st.session_state['ga_position_index'] = new_index
            st.rerun()
    
    with nav_col2:
        if st.button("⏮️", help="First", disabled=current_index == 0):
            st.session_state['ga_position_index'] = 0
            st.rerun()
    
    with nav_col3:
        if st.button("⬅️", help="Previous", disabled=current_index == 0):
            st.session_state['ga_position_index'] = current_index - 1
            st.rerun()
    
    with nav_col4:
        if st.button("➡️", help="Next", disabled=current_index == max_index):
            st.session_state['ga_position_index'] = current_index + 1
            st.rerun()
    
    with nav_col5:
        if st.button("⏭️", help="Last", disabled=current_index == max_index):
            st.session_state['ga_position_index'] = max_index
            st.rerun()
    
    # Display current position with enhanced analysis
    if 0 <= current_index < len(positions):
        position = positions[current_index]
        
        board_col, analysis_col = st.columns([1, 1])
        
        with board_col:
            # Enhanced board display with piece notation
            display_enhanced_board(position)
        
        with analysis_col:
            # Comprehensive position analysis
            display_comprehensive_position_analysis(position, current_index, len(positions))


def display_enhanced_board(position: Dict):
    """
    Display an SVG chess board with optional flip toggle and
    move notation rendered with piece-icons.  No automatic
    flipping – the user controls orientation via the toggle.
    """
    try:
        board: chess.Board = position["board"]

        # ───────────────────────────────────────────────────────────
        # 1️⃣  Persist the user’s orientation choice in session state
        #     (initially False → White at bottom)
        # ───────────────────────────────────────────────────────────
        if "board_flipped" not in st.session_state:
            st.session_state.board_flipped = False

        # A small, non-intrusive toggle right above the board
        st.toggle(
            "Flip board",                 # label
            key="flip_board_toggle",      # unique widget key
            value=st.session_state.board_flipped,
            on_change=lambda: st.session_state.update(
                board_flipped=not st.session_state.board_flipped
            ),
            help="Show the board from the other side",
        )

        # Current orientation
        flipped = st.session_state.board_flipped

        # ───────────────────────────────────────────────────────────
        # 2️⃣  Render board SVG with the chosen orientation
        # ───────────────────────────────────────────────────────────
        board_svg = chess.svg.board(
            board=board,
            flipped=flipped,
            size=450,
            style="""
            .square.light { fill: #f0d9b5; }
            .square.dark {  fill: #b58863; }
            .square.light.lastmove { fill: #cdd26a; }
            .square.dark.lastmove  { fill: #aaa23a; }
            .piece { font-size: 45px; }
            """
        )
        st.markdown(board_svg, unsafe_allow_html=True)

        # ───────────────────────────────────────────────────────────
        # 3️⃣  Show move notation using piece-icons (unchanged)
        # ───────────────────────────────────────────────────────────
        move_text = position.get("move", "Start")
        if move_text != "Start":
            move_with_icons = convert_to_piece_icons(move_text)
            st.markdown(f"### {move_with_icons}")
        else:
            st.markdown("### Starting Position")

    except Exception as e:
        st.error(f"Error displaying board: {e}")


def display_comprehensive_position_analysis(position: Dict, index: int, total: int):
    """Display comprehensive analysis of the current position."""
    st.markdown(f"##### Move {position.get('move_number', index)}")
    
    board = position['board']
    
    # Basic position info
    st.markdown(f"**Turn:** {position.get('turn', 'white').title()}")
    st.markdown(f"**Position:** {index + 1} of {total}")
    st.markdown(f"**Legal Moves:** {len(list(board.legal_moves))}")
    
    # Game status indicators
    if board.is_check():
        st.warning("⚠️ Check!")
    if board.is_checkmate():
        st.error("🏁 Checkmate!")
    if board.is_stalemate():
        st.info("🤝 Stalemate!")
    
    # Material analysis
    material = calculate_enhanced_material(board)
    st.markdown("**Material Balance:**")
    st.markdown(f"• White: {material['white_total']} ({material['white_pieces']})")
    st.markdown(f"• Black: {material['black_total']} ({material['black_pieces']})")
    st.markdown(f"• Balance: {material['difference']:+.1f}")
    
    # Spatial metrics if available
    spatial_metrics = position.get('spatial_metrics', {})
    if spatial_metrics:
        display_position_spatial_summary(spatial_metrics)
    
    # Position evaluation
    display_position_evaluation_summary(position)
    
    # FEN and additional info
    with st.expander("📋 Technical Details"):
        st.markdown("**FEN:**")
        st.code(position['fen'])
        
        if spatial_metrics:
            st.markdown("**Spatial Data Available:**")
            st.json(spatial_metrics)


def display_position_spatial_summary(metrics: Dict[str, Any]):
    """Display spatial analysis summary for current position."""
    st.markdown("**Spatial Analysis:**")
    
    # Space control
    space_control = metrics.get('space_control', {})
    if space_control:
        white_space = space_control.get('white_space_percentage', 0)
        black_space = space_control.get('black_space_percentage', 0)
        space_advantage = space_control.get('space_advantage', 0)
        
        st.markdown(f"• Space Control: W{white_space:.0f}% - B{black_space:.0f}%")
        if space_advantage > 5:
            st.success(f"• White space advantage: +{space_advantage:.0f}")
        elif space_advantage < -5:
            st.error(f"• Black space advantage: +{abs(space_advantage):.0f}")
        else:
            st.info("• Space control balanced")
    
    # Center control
    center = metrics.get('center_control', {})
    if center:
        center_adv = center.get('center_advantage', 0)
        st.markdown(f"• Center advantage: {center_adv:+}")
    
    # King safety
    king_safety = metrics.get('king_safety', {})
    if king_safety:
        white_threats = king_safety.get('white', {}).get('threats', 0)
        black_threats = king_safety.get('black', {}).get('threats', 0)
        st.markdown(f"• King threats: W{white_threats} - B{black_threats}")


def display_position_evaluation_summary(position: Dict):
    """Display position evaluation summary."""
    st.markdown("**Position Assessment:**")
    
    board = position['board']
    
    # Mobility analysis
    white_moves = len([m for m in board.legal_moves if board.turn == chess.WHITE])
    black_moves = len([m for m in board.legal_moves if board.turn == chess.BLACK])
    
    # Switch turn to count opponent moves
    board.turn = not board.turn
    if board.turn == chess.WHITE:
        white_moves = len(list(board.legal_moves))
    else:
        black_moves = len(list(board.legal_moves))
    board.turn = not board.turn  # Switch back
    
    st.markdown(f"• Mobility: W{white_moves} - B{black_moves}")
    
    # Development assessment
    development_score = assess_development(board)
    st.markdown(f"• Development: {development_score}")
    
    # Overall assessment
    assessment = generate_position_assessment(position)
    st.info(f"**Overall:** {assessment}")


def display_evaluation_and_metrics():
    """Display comprehensive evaluation and metrics analysis."""
    st.markdown("#### 📊 Evaluation & Metrics Analysis")
    
    positions = st.session_state.get('ga_positions', [])
    if not positions:
        st.warning("⚠️ No position data available")
        return
    
    # Generate evaluation charts
    display_evaluation_charts(positions)
    
    # Display statistical summary
    display_statistical_summary(positions)


def display_evaluation_charts(positions: List[Dict]):
    """Generate and display evaluation charts."""
    if len(positions) < 2:
        return
    
    # Prepare data for charts
    moves = [p['move_number'] for p in positions]
    material_balance = []
    space_advantage = []
    
    for position in positions:
        # Material balance
        try:
            material_data = calculate_enhanced_material(position['board'])
            material_balance.append(material_data['difference'])
        except:
            material_balance.append(0)
        
        # Space advantage
        spatial_metrics = position.get('spatial_metrics', {})
        space_control = spatial_metrics.get('space_control', {})
        space_advantage.append(space_control.get('space_advantage', 0))
    
    # Create evaluation charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Material balance chart
        fig_material = go.Figure()
        fig_material.add_trace(go.Scatter(
            x=moves, y=material_balance,
            mode='lines+markers',
            name='Material Balance',
            line=dict(color='#1f77b4', width=3),
            hovertemplate='Move %{x}<br>Material: %{y:.1f}<extra></extra>'
        ))
        fig_material.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig_material.update_layout(
            title='Material Balance Throughout Game',
            xaxis_title='Move Number',
            yaxis_title='Material Advantage',
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_material, use_container_width=True)
    
    with chart_col2:
        # Space advantage chart
        fig_space = go.Figure()
        fig_space.add_trace(go.Scatter(
            x=moves, y=space_advantage,
            mode='lines+markers',
            name='Space Advantage',
            line=dict(color='#ff7f0e', width=3),
            hovertemplate='Move %{x}<br>Space: %{y:.0f}<extra></extra>'
        ))
        fig_space.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig_space.update_layout(
            title='Space Control Throughout Game',
            xaxis_title='Move Number',
            yaxis_title='Space Advantage',
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig_space, use_container_width=True)


def display_statistical_summary(positions: List[Dict]):
    """Display comprehensive statistical summary."""
    st.markdown("#### 📈 Statistical Summary")
    
    if not positions:
        return
    
    # Calculate statistics
    material_values = []
    space_values = []
    
    for position in positions:
        try:
            material_data = calculate_enhanced_material(position['board'])
            material_values.append(abs(material_data['difference']))
        except:
            material_values.append(0)
        
        spatial_metrics = position.get('spatial_metrics', {})
        space_control = spatial_metrics.get('space_control', {})
        space_values.append(abs(space_control.get('space_advantage', 0)))
    
    if material_values and space_values:
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.metric("Avg Material Imbalance", f"{sum(material_values)/len(material_values):.2f}")
        
        with stat_col2:
            st.metric("Max Material Difference", f"{max(material_values):.2f}")
        
        with stat_col3:
            st.metric("Avg Space Imbalance", f"{sum(space_values)/len(space_values):.1f}")
        
        with stat_col4:
            st.metric("Max Space Difference", f"{max(space_values):.1f}")


def display_critical_positions_analysis():
    """Display comprehensive critical positions analysis."""
    st.markdown("#### 🔍 Critical Positions Analysis")
    
    critical_positions = st.session_state.get('ga_critical_positions', [])
    
    if not critical_positions:
        st.info("📊 No critical positions identified in this game.")
        return
    
    st.markdown(f"Found **{len(critical_positions)}** critical positions:")
    
    # Display critical positions in enhanced cards
    for i, pos in enumerate(critical_positions):
        with st.container():
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #e53e3e;
                margin: 1rem 0;
            ">
                <h4 style="color: #e53e3e; margin: 0 0 1rem 0;">
                    🎯 Move {pos['move_number']}: {convert_to_piece_icons(pos['move'])}
                </h4>
                <p style="color: #744210; margin: 0;"><strong>Significance:</strong> {pos['reason']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Expandable detailed analysis
            with st.expander(f"📋 Detailed Analysis - Move {pos['move_number']}", expanded=False):
                detail_col1, detail_col2 = st.columns([1, 1])
                
                with detail_col1:
                    try:
                        board_svg = chess.svg.board(
                            board=pos['board'], 
                            size=350,
                            style="""
                            .square.light { fill: #f0d9b5; }
                            .square.dark { fill: #b58863; }
                            """
                        )
                        st.markdown(board_svg, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error displaying position: {e}")
                
                with detail_col2:
                    st.markdown("**Position Details:**")
                    st.markdown(f"• **Move:** {pos['move']}")
                    st.markdown(f"• **Evaluation:** {pos['current_evaluation']:+.2f}")
                    st.markdown(f"• **Material Change:** {pos['material_change']:+.2f}")
                    st.markdown(f"• **Reason:** {pos['reason']}")
                    
                    # Navigate to this position
                    if st.button(f"🎯 Go to Position", key=f"goto_critical_{i}"):
                        st.session_state['ga_position_index'] = pos['index']
                        st.rerun()
                    
                    # Additional analysis
                    st.markdown("**Analysis:**")
                    board = pos['board']
                    if board.is_check():
                        st.warning("⚠️ Position involves check")
                    if board.is_checkmate():
                        st.error("🏁 Position is checkmate")
                    
                    material_analysis = calculate_enhanced_material(board)
                    st.markdown(f"• Material: W{material_analysis['white_total']} - B{material_analysis['black_total']}")


def display_spatial_analysis_tab():
    """Display comprehensive spatial analysis."""
    st.markdown("#### 🗺️ Comprehensive Spatial Analysis")
    
    positions = st.session_state.get('ga_positions', [])
    if not positions:
        st.warning("⚠️ No position data available for spatial analysis.")
        return
    
    try:
        # Check if spatial analysis is available
        import spatial_analysis
        
        # Generate spatial evolution data
        spatial_data = extract_spatial_evolution_data(positions)
        
        if not spatial_data.empty:
            display_spatial_evolution_charts(spatial_data)
            display_space_control_visualization(positions)
            display_game_phase_analysis(spatial_data)
        else:
            st.warning("⚠️ Unable to generate spatial analysis data.")
            
    except ImportError:
        st.info("""
        🔧 **Spatial Analysis Module Not Available**
        
        The advanced spatial analysis features require the spatial_analysis module. 
        This module provides:
        
        • Territory control visualization
        • Piece activity mapping  
        • Strategic factor analysis
        • Advanced positional metrics
        
        Contact your administrator to enable these features.
        """)
    except Exception as e:
        st.error(f"Error in spatial analysis: {e}")


def extract_spatial_evolution_data(positions: List[Dict]) -> pd.DataFrame:
    """Extract spatial evolution data for analysis."""
    spatial_data = []
    
    for pos in positions:
        if pos['move_number'] % 3 == 0:  # Every 3rd move for performance
            metrics = pos.get('spatial_metrics', {})
            space_control = metrics.get('space_control', {})
            center_control = metrics.get('center_control', {})
            material = calculate_enhanced_material(pos['board'])
            king_safety = metrics.get('king_safety', {})
            
            spatial_data.append({
                'Move': pos['move_number'],
                'Space_Advantage': space_control.get('space_advantage', 0),
                'Material_Balance': material['difference'],
                'White_Space': space_control.get('white_space_percentage', 0),
                'Black_Space': space_control.get('black_space_percentage', 0),
                'Center_Control': center_control.get('center_advantage', 0),
                'White_King_Threats': king_safety.get('white', {}).get('threats', 0),
                'Black_King_Threats': king_safety.get('black', {}).get('threats', 0)
            })
    
    return pd.DataFrame(spatial_data)


def display_spatial_evolution_charts(df: pd.DataFrame):
    """Display spatial evolution charts."""
    if df.empty:
        return
    
    st.markdown("##### 📈 Spatial Metrics Evolution")
    
    # Space control evolution
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df['Move'], y=df['White_Space'],
        mode='lines+markers',
        name='White Space %',
        line=dict(color='#1f77b4', width=3)
    ))
    fig1.add_trace(go.Scatter(
        x=df['Move'], y=df['Black_Space'],
        mode='lines+markers',
        name='Black Space %',
        line=dict(color='#d62728', width=3)
    ))
    fig1.update_layout(
        title='Space Control Evolution',
        xaxis_title='Move Number',
        yaxis_title='Space Control %',
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Combined metrics chart
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df['Move'], y=df['Space_Advantage'],
        mode='lines+markers',
        name='Space Advantage',
        line=dict(color='#9467bd', width=2)
    ))
    fig2.add_trace(go.Scatter(
        x=df['Move'], y=df['Center_Control'],
        mode='lines+markers',
        name='Center Control',
        line=dict(color='#8c564b', width=2)
    ))
    fig2.add_trace(go.Scatter(
        x=df['Move'], y=df['Material_Balance'] * 10,
        mode='lines+markers',
        name='Material Balance (×10)',
        line=dict(color='#e377c2', width=2)
    ))
    fig2.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig2.update_layout(
        title='Combined Positional Metrics',
        xaxis_title='Move Number',
        yaxis_title='Advantage',
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)


def display_space_control_visualization(positions: List[Dict]):
    """Display space control visualization for current position."""
    st.markdown("##### 🎯 Current Position Space Control")
    
    current_index = st.session_state.get('ga_position_index', 0)
    if 0 <= current_index < len(positions):
        position = positions[current_index]
        spatial_metrics = position.get('spatial_metrics', {})
        
        if spatial_metrics.get('space_control'):
            try:
                # Try to generate space control board
                space_control_html = generate_space_control_board_html(spatial_metrics)
                st.components.v1.html(space_control_html, height=450, scrolling=False)
            except Exception as e:
                st.info("Space control visualization not available for this position.")
        else:
            st.info("No spatial data available for current position.")


def generate_space_control_board_html(metrics: Dict[str, Any]) -> str:
    """Generate space control board visualization as HTML."""
    space_control = metrics.get('space_control', {})
    control_matrix = space_control.get('control_matrix', [])
    
    if not control_matrix or len(control_matrix) != 8:
        return '<p style="text-align: center; color: #718096;">Space control data not available</p>'
    
    # Create HTML table representation
    board_html = '<div style="display: flex; justify-content: center; margin: 1rem 0;"><table style="border-collapse: collapse; border: 2px solid #e2e8f0;">'
    
    for rank in range(8):
        board_html += '<tr>'
        for file in range(8):
            control_value = control_matrix[7-rank][file]  # Flip rank for display
            
            # Determine background color and symbol
            if control_value == 1:  # White control
                bg_color = '#3b82f6'
                symbol = '🔵'
            elif control_value == -1:  # Black control
                bg_color = '#8b5cf6'
                symbol = '🟣'
            elif control_value == 2:  # Contested
                bg_color = '#f59e0b'
                symbol = '🟠'
            else:  # Neutral
                is_light = (rank + file) % 2 == 0
                bg_color = '#f0d9b5' if is_light else '#b58863'
                symbol = ''
            
            board_html += f'''
            <td style="
                width: 40px; 
                height: 40px; 
                background-color: {bg_color}; 
                text-align: center; 
                vertical-align: middle;
                border: 1px solid #d1d5db;
                font-size: 14px;
            ">{symbol}</td>
            '''
        
        board_html += '</tr>'
    
    board_html += '</table></div>'
    
    # Add legend and statistics
    legend_html = f"""
    <div style="text-align: center; margin: 1rem 0;">
        <p><strong>Legend:</strong> 🔵 White Control • 🟣 Black Control • 🟠 Contested • ⚪ Neutral</p>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; max-width: 400px; margin: 1rem auto;">
            <div><strong>White:</strong> {space_control.get('white_space_percentage', 0):.1f}%</div>
            <div><strong>Black:</strong> {space_control.get('black_space_percentage', 0):.1f}%</div>
            <div><strong>Contested:</strong> {space_control.get('contested_percentage', 0):.1f}%</div>
            <div><strong>Advantage:</strong> {space_control.get('space_advantage', 0):+.0f}</div>
        </div>
    </div>
    """
    
    return board_html + legend_html


def display_game_phase_analysis(df: pd.DataFrame):
    """Display comprehensive game phase analysis."""
    if df.empty:
        return
    
    st.markdown("##### 🎯 Game Phase Analysis")
    
    total_moves = len(df)
    if total_moves == 0:
        return
    
    # Analyze different game phases
    opening = df[df['Move'] <= 15]
    middlegame = df[(df['Move'] > 15) & (df['Move'] <= 40)]
    endgame = df[df['Move'] > 40]
    
    phase_col1, phase_col2, phase_col3 = st.columns(3)
    
    with phase_col1:
        st.markdown("**Opening (1-15 moves):**")
        if len(opening) > 0:
            avg_space = opening['Space_Advantage'].mean()
            avg_center = opening['Center_Control'].mean()
            st.markdown(f"• Avg Space Advantage: {avg_space:+.1f}")
            st.markdown(f"• Avg Center Control: {avg_center:+.1f}")
            character = 'Dynamic' if abs(avg_space) > 5 else 'Solid'
            st.markdown(f"• Character: {character}")
    
    with phase_col2:
        st.markdown("**Middlegame (16-40 moves):**")
        if len(middlegame) > 0:
            avg_space = middlegame['Space_Advantage'].mean()
            max_material = middlegame['Material_Balance'].abs().max()
            st.markdown(f"• Avg Space Advantage: {avg_space:+.1f}")
            st.markdown(f"• Max Material Swing: {max_material:.1f}")
            character = 'Sharp' if max_material > 2 else 'Positional'
            st.markdown(f"• Character: {character}")
    
    with phase_col3:
        st.markdown("**Endgame (40+ moves):**")
        if len(endgame) > 0:
            final_material = endgame['Material_Balance'].iloc[-1]
            avg_threats = (endgame['White_King_Threats'] + endgame['Black_King_Threats']).mean()
            st.markdown(f"• Final Material: {final_material:+.1f}")
            st.markdown(f"• Avg King Threats: {avg_threats:.1f}")
            character = 'Active' if avg_threats > 1 else 'Technical'
            st.markdown(f"• Character: {character}")


def display_comprehensive_game_statistics():
    """Display comprehensive game statistics and analysis."""
    st.markdown("#### 📈 Comprehensive Game Statistics")
    
    game_stats = st.session_state.get('ga_game_stats', {})
    positions = st.session_state.get('ga_positions', [])
    
    if not game_stats or not positions:
        st.warning("⚠️ Game statistics not available")
        return
    
    # Overview statistics
    st.markdown("##### 📊 Game Overview")
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("Total Moves", game_stats.get('total_moves', 0))
    
    with stat_col2:
        st.metric("Captures", game_stats.get('captures', 0))
    
    with stat_col3:
        st.metric("Checks", game_stats.get('checks', 0))
    
    with stat_col4:
        st.metric("Complexity", f"{game_stats.get('complexity_score', 0):.1f}/10")
    
    # Detailed analysis
    st.markdown("##### 📋 Detailed Analysis")
    
    detail_col1, detail_col2 = st.columns(2)
    
    with detail_col1:
        st.markdown("**Move Types:**")
        st.markdown(f"• Captures: {game_stats.get('captures', 0)}")
        st.markdown(f"• Checks: {game_stats.get('checks', 0)}")
        st.markdown(f"• Castling: {game_stats.get('castling_moves', 0)}")
        st.markdown(f"• Material swings: {game_stats.get('material_swings', 0)}")
        
        st.markdown("**Material Analysis:**")
        st.markdown(f"• Average imbalance: {game_stats.get('average_material_balance', 0):.2f}")
        st.markdown(f"• Maximum advantage: {game_stats.get('max_material_advantage', 0):.1f}")
    
    with detail_col2:
        phases = game_stats.get('game_phases', {})
        st.markdown("**Game Phases:**")
        st.markdown(f"• Opening: {phases.get('opening_length', 0)} moves")
        st.markdown(f"• Middlegame: {phases.get('middlegame_length', 0)} moves")
        st.markdown(f"• Endgame: {phases.get('endgame_length', 0)} moves")
        
        st.markdown("**Game Character:**")
        complexity = game_stats.get('complexity_score', 0)
        if complexity > 7:
            character = "Highly tactical and complex"
        elif complexity > 4:
            character = "Moderately complex with tactical elements"
        else:
            character = "Positional and strategic"
        st.markdown(f"• {character}")
    
    # Move list with enhanced formatting
    display_enhanced_move_list(positions)


def display_enhanced_move_list(positions: List[Dict]):
    """Display enhanced move list with analysis."""
    st.markdown("##### ♟️ Complete Move Analysis")
    
    moves_data = []
    for i in range(1, len(positions), 2):
        move_num = (i + 1) // 2
        white_pos = positions[i] if i < len(positions) else None
        black_pos = positions[i + 1] if i + 1 < len(positions) else None
        
        white_move = convert_to_piece_icons(white_pos['move']) if white_pos else ""
        black_move = convert_to_piece_icons(black_pos['move']) if black_pos else ""
        
        # Add move analysis
        white_analysis = ""
        black_analysis = ""
        
        if white_pos:
            if 'x' in white_pos['move']:
                white_analysis += " 🎯"
            if '+' in white_pos['move']:
                white_analysis += " ⚠️"
            if 'O-O' in white_pos['move']:
                white_analysis += " 🏰"
        
        if black_pos:
            if 'x' in black_pos['move']:
                black_analysis += " 🎯"
            if '+' in black_pos['move']:
                black_analysis += " ⚠️"
            if 'O-O' in black_pos['move']:
                black_analysis += " 🏰"
        
        moves_data.append({
            'Move': f"{move_num}.",
            'White': f"{white_move}{white_analysis}",
            'Black': f"{black_move}{black_analysis}"
        })
    
    # Display in a nice table
    df_moves = pd.DataFrame(moves_data)
    st.dataframe(df_moves, use_container_width=True, hide_index=True)
    
    # Legend
    st.markdown("""
    **Legend:** 🎯 Capture • ⚠️ Check • 🏰 Castling
    """)


def display_advanced_export_options():
    """Display advanced export and save options."""
    st.markdown("#### 💾 Save & Export Analysis")
    
    game = st.session_state.get('ga_current_game')
    if not game:
        st.warning("⚠️ No game loaded for export")
        return
    
    # Save analysis progress
    save_col1, save_col2 = st.columns(2)
    
    with save_col1:
        st.markdown("##### 💾 Save Analysis Progress")
        
        analysis_name = st.text_input(
            "Analysis name:",
            value=f"Analysis_{datetime.now().strftime('%Y%m%d_%H%M')}",
            key="save_analysis_name"
        )
        
        analysis_notes = st.text_area(
            "Analysis notes:",
            placeholder="Add your personal insights and observations...",
            height=100,
            key="save_analysis_notes"
        )
        
        if st.button("💾 Save Progress", use_container_width=True):
            save_analysis_progress(game, analysis_name, analysis_notes)
    
    with save_col2:
        st.markdown("##### 📤 Export Options")
        
        export_format = st.selectbox(
            "Export format:",
            ["HTML Study", "Enhanced PGN", "JSON Data", "PDF Report (Premium)"],
            key="export_format_select"
        )
        
        include_options = st.multiselect(
            "Include in export:",
            ["Position Analysis", "Spatial Metrics", "Critical Positions", "Charts", "Statistics", "Personal Notes"],
            default=["Position Analysis", "Critical Positions", "Charts"],
            key="export_include_options"
        )
        
        if st.button("📄 Generate Export", use_container_width=True, type="primary"):
            handle_advanced_export(game, export_format, include_options, analysis_notes)
    
    # Quick export buttons
    st.markdown("##### ⚡ Quick Actions")
    
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    
    with quick_col1:
        if st.button("🌐 HTML Study", use_container_width=True):
            generate_html_export(game)
    
    with quick_col2:
        if st.button("📋 Copy PGN", use_container_width=True):
            display_pgn_for_copy(game)
    
    with quick_col3:
        if st.button("📊 Analysis Summary", use_container_width=True):
            generate_analysis_summary()
    
    with quick_col4:
        if st.button("🔗 Share Link", use_container_width=True):
            st.info("🚧 Share functionality coming soon!")


def save_analysis_progress(game: chess.pgn.Game, analysis_name: str, notes: str):
    """Save analysis progress to database."""
    try:
        user_id = st.session_state.get('user_id')
        if not user_id:
            st.warning("⚠️ Login required to save analysis progress")
            return
        
        # Get current analysis state
        current_position = st.session_state.get('ga_position_index', 0)
        game_stats = st.session_state.get('ga_game_stats', {})
        critical_positions = st.session_state.get('ga_critical_positions', [])
        
        analysis_data = {
            'game_headers': dict(game.headers),
            'analysis_name': analysis_name,
            'notes': notes,
            'current_position': current_position,
            'game_statistics': game_stats,
            'critical_positions_count': len(critical_positions),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to session for now (implement database save as needed)
        st.session_state['saved_analysis'] = analysis_data
        
        st.success(f"✅ Analysis '{analysis_name}' saved successfully!")
        
    except Exception as e:
        st.error(f"❌ Failed to save analysis: {e}")


def handle_advanced_export(game: chess.pgn.Game, export_format: str, include_options: List[str], notes: str):
    """Handle advanced export generation."""
    try:
        if export_format == "HTML Study":
            generate_comprehensive_html_export(game, include_options, notes)
        elif export_format == "Enhanced PGN":
            generate_enhanced_pgn_export(game, notes)
        elif export_format == "JSON Data":
            generate_json_data_export(game, include_options)
        elif export_format == "PDF Report (Premium)":
            st.info("📄 PDF export is a premium feature. Contact support for access.")
    except Exception as e:
        st.error(f"❌ Export failed: {e}")


def generate_html_export(game: chess.pgn.Game):
    """Generate HTML export with enhanced features."""
    try:
        # Get analysis data
        notes = st.session_state.get('save_analysis_notes', '')
        critical_positions = st.session_state.get('ga_critical_positions', [])
        
        generator = GameHTMLGenerator()
        html_path = generator.generate(
            game, 
            analysis_notes=notes,
            critical_positions=critical_positions
        )
        
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        st.download_button(
            "⬇️ Download HTML Study",
            data=html_content,
            file_name=Path(html_path).name,
            mime="text/html",
            use_container_width=True
        )
        st.success("✅ HTML study generated!")
        
    except Exception as e:
        st.error(f"❌ Failed to generate HTML study: {e}")


def generate_comprehensive_html_export(game: chess.pgn.Game, include_options: List[str], notes: str):
    """Generate comprehensive HTML export with selected options."""
    try:
        critical_positions = st.session_state.get('ga_critical_positions', []) if "Critical Positions" in include_options else []
        
        generator = GameHTMLGenerator()
        html_path = generator.generate(
            game,
            analysis_notes=notes if "Personal Notes" in include_options else None,
            critical_positions=critical_positions,
            include_statistics="Statistics" in include_options
        )
        
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        st.download_button(
            "⬇️ Download Comprehensive Study",
            data=html_content,
            file_name=f"comprehensive_study_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            use_container_width=True
        )
        st.success("✅ Comprehensive HTML study generated!")
        
    except Exception as e:
        st.error(f"❌ Failed to generate comprehensive HTML: {e}")


def generate_enhanced_pgn_export(game: chess.pgn.Game, notes: str):
    """Generate enhanced PGN with analysis annotations."""
    try:
        headers = dict(game.headers)
        
        # Build enhanced PGN
        pgn_lines = []
        for key, value in headers.items():
            pgn_lines.append(f'[{key} "{value}"]')
        
        pgn_lines.append('')
        
        # Add moves with analysis
        moves_text = str(game.mainline())
        pgn_lines.append(moves_text)
        
        # Add analysis annotations
        if notes:
            pgn_lines.append(f"\n{{Analysis Notes: {notes}}}")
        
        # Add critical positions summary
        critical_positions = st.session_state.get('ga_critical_positions', [])
        if critical_positions:
            pgn_lines.append(f"\n{{Critical Positions: {len(critical_positions)} identified}}")
        
        # Add generation timestamp
        pgn_lines.append(f"\n{{Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}}")
        
        pgn_content = '\n'.join(pgn_lines)
        
        st.download_button(
            "⬇️ Download Enhanced PGN",
            data=pgn_content,
            file_name=f"enhanced_game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn",
            mime="text/plain",
            use_container_width=True
        )
        st.success("✅ Enhanced PGN ready!")
        
    except Exception as e:
        st.error(f"❌ Failed to generate enhanced PGN: {e}")


def generate_json_data_export(game: chess.pgn.Game, include_options: List[str]):
    """Generate comprehensive JSON data export."""
    try:
        export_data = {
            'game_headers': dict(game.headers),
            'moves': [str(move) for move in game.mainline_moves()],
            'export_timestamp': datetime.now().isoformat()
        }
        
        if "Statistics" in include_options:
            export_data['game_statistics'] = st.session_state.get('ga_game_stats', {})
        
        if "Critical Positions" in include_options:
            critical_positions = st.session_state.get('ga_critical_positions', [])
            export_data['critical_positions'] = [
                {
                    'move_number': pos['move_number'],
                    'move': pos['move'],
                    'reason': pos['reason'],
                    'fen': pos['fen']
                }
                for pos in critical_positions
            ]
        
        if "Personal Notes" in include_options:
            export_data['analysis_notes'] = st.session_state.get('save_analysis_notes', '')
        
        json_str = json.dumps(export_data, indent=2)
        
        st.download_button(
            "⬇️ Download JSON Data",
            data=json_str,
            file_name=f"game_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        st.success("✅ JSON data export ready!")
        
    except Exception as e:
        st.error(f"❌ Failed to generate JSON export: {e}")


def display_pgn_for_copy(game: chess.pgn.Game):
    """Display PGN for manual copying."""
    pgn_str = str(game)
    st.code(pgn_str, language="text")
    st.info("📋 PGN displayed above - select and copy manually")


def generate_analysis_summary():
    """Generate and display analysis summary."""
    st.markdown("#### 📊 Analysis Summary")
    
    game = st.session_state.get('ga_current_game')
    game_stats = st.session_state.get('ga_game_stats', {})
    critical_positions = st.session_state.get('ga_critical_positions', [])
    
    if not game:
        st.warning("⚠️ No game data available")
        return
    
    headers = game.headers
    
    summary_data = {
        'Game': f"{headers.get('White', 'Unknown')} vs {headers.get('Black', 'Unknown')}",
        'Event': headers.get('Event', 'Unknown'),
        'Date': headers.get('Date', 'Unknown'),
        'Result': headers.get('Result', '*'),
        'Total Moves': game_stats.get('total_moves', 0),
        'Captures': game_stats.get('captures', 0),
        'Checks': game_stats.get('checks', 0),
        'Critical Positions': len(critical_positions),
        'Complexity Score': f"{game_stats.get('complexity_score', 0):.1f}/10",
        'Analysis Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    st.json(summary_data)


# Helper Functions

def parse_pgn_content(pgn_content: str) -> List[chess.pgn.Game]:
    """Parse PGN content and return list of games."""
    games = []
    pgn_io = io.StringIO(pgn_content)
    
    while True:
        try:
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break
            games.append(game)
        except Exception as e:
            st.warning(f"⚠️ Error parsing game: {e}")
            break
    
    return games


def calculate_enhanced_positions(game: chess.pgn.Game) -> List[Dict[str, Any]]:
    """Calculate all positions with enhanced spatial analysis."""
    board = game.board()
    positions = []
    move_number = 1
    
    # Starting position with enhanced analysis
    try:
        import spatial_analysis
        start_metrics = spatial_analysis.calculate_comprehensive_spatial_metrics(board)
    except:
        start_metrics = {}
    
    positions.append({
        'move_number': 0,
        'move': 'Starting Position',
        'fen': board.fen(),
        'turn': 'white',
        'board': board.copy(),
        'spatial_metrics': start_metrics
    })
    
    # Process all moves with enhanced analysis
    for move in game.mainline_moves():
        color = 'white' if board.turn else 'black'
        san_move = board.san(move)
        board.push(move)
        
        # Calculate spatial metrics for each position
        try:
            import spatial_analysis
            metrics = spatial_analysis.calculate_comprehensive_spatial_metrics(board)
        except:
            metrics = {}
        
        positions.append({
            'move_number': move_number,
            'move': san_move,
            'fen': board.fen(),
            'turn': color,
            'board': board.copy(),
            'spatial_metrics': metrics
        })
        
        if color == 'black':
            move_number += 1
    
    return positions


def calculate_enhanced_material(board: chess.Board) -> Dict[str, Any]:
    """Calculate enhanced material analysis."""
    piece_values = {
        chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
    }
    
    white_pieces = []
    black_pieces = []
    white_total = 0
    black_total = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values.get(piece.piece_type, 0)
            piece_name = chess.piece_name(piece.piece_type)
            
            if piece.color == chess.WHITE:
                white_total += value
                white_pieces.append(piece_name[0].upper())
            else:
                black_total += value
                black_pieces.append(piece_name[0].upper())
    
    return {
        'white_total': white_total,
        'black_total': black_total,
        'difference': white_total - black_total,
        'white_pieces': ''.join(sorted(white_pieces)),
        'black_pieces': ''.join(sorted(black_pieces))
    }


def assess_development(board: chess.Board) -> str:
    """Assess piece development for current position."""
    # Simple development assessment
    developed_pieces = 0
    total_pieces = 0
    
    # Check minor pieces development
    for square in [chess.B1, chess.G1, chess.C1, chess.F1]:  # White starting squares
        if board.piece_at(square) is None:
            developed_pieces += 1
        total_pieces += 1
    
    for square in [chess.B8, chess.G8, chess.C8, chess.F8]:  # Black starting squares
        if board.piece_at(square) is None:
            developed_pieces += 1
        total_pieces += 1
    
    development_ratio = developed_pieces / total_pieces
    
    if development_ratio > 0.75:
        return "Well developed"
    elif development_ratio > 0.5:
        return "Moderately developed"
    else:
        return "Under-developed"


def generate_position_assessment(position: Dict) -> str:
    """Generate overall position assessment."""
    board = position['board']
    spatial_metrics = position.get('spatial_metrics', {})
    
    # Material assessment
    material = calculate_enhanced_material(board)
    material_diff = material['difference']
    
    # Space control assessment
    space_advantage = 0
    if spatial_metrics.get('space_control'):
        space_advantage = spatial_metrics['space_control'].get('space_advantage', 0)
    
    # Generate assessment
    if abs(material_diff) > 3:
        return f"Material advantage: {'White' if material_diff > 0 else 'Black'} clearly better"
    elif abs(material_diff) > 1:
        return f"Material edge: {'White' if material_diff > 0 else 'Black'} slightly better"
    elif abs(space_advantage) > 15:
        return f"Space advantage: {'White' if space_advantage > 0 else 'Black'} dominates"
    elif abs(space_advantage) > 5:
        return f"Slight space edge: {'White' if space_advantage > 0 else 'Black'}"
    else:
        return "Balanced position"


def identify_critical_positions(positions: List[Dict]) -> List[Dict]:
    """Identify critical positions based on evaluation changes."""
    if not positions:
        return []
    
    critical_positions = []
    previous_material = 0
    
    for i, position in enumerate(positions[1:], 1):  # Skip starting position
        try:
            board = position['board']
            material_data = calculate_enhanced_material(board)
            current_material = material_data['difference']
            
            # Calculate material change
            material_change = abs(current_material - previous_material)
            
            # Identify critical moments
            is_critical = False
            reason = ""
            
            if material_change > 3:
                is_critical = True
                reason = f"Major material swing: {material_change:.1f}"
            elif board.is_check():
                is_critical = True
                reason = "Check given"
            elif board.is_checkmate():
                is_critical = True
                reason = "Checkmate"
            elif i % 15 == 0:  # Periodic checkpoints
                is_critical = True
                reason = f"Strategic checkpoint (move {position['move_number']})"
            
            if is_critical:
                critical_positions.append({
                    'index': i,
                    'move_number': position['move_number'],
                    'move': position['move'],
                    'fen': position['fen'],
                    'board': position['board'],
                    'reason': reason,
                    'material_change': material_change,
                    'current_evaluation': current_material
                })
            
            previous_material = current_material
            
        except Exception:
            continue
    
    return critical_positions[:10]  # Limit to 10 critical positions


def calculate_comprehensive_game_statistics(positions: List[Dict]) -> Dict[str, Any]:
    """Calculate comprehensive game statistics."""
    if not positions:
        return {}
    
    stats = {
        'total_moves': len(positions) - 1,
        'captures': 0,
        'checks': 0,
        'castling_moves': 0,
        'material_swings': 0,
        'average_material_balance': 0,
        'max_material_advantage': 0,
        'game_phases': {},
        'complexity_score': 0
    }
    
    material_values = []
    previous_material = 0
    
    for i, position in enumerate(positions[1:], 1):
        move = position.get('move', '')
        
        # Count move types
        if 'x' in move:
            stats['captures'] += 1
        if '+' in move:
            stats['checks'] += 1
        if 'O-O' in move:
            stats['castling_moves'] += 1
        
        # Material analysis
        try:
            material_data = calculate_enhanced_material(position['board'])
            current_material = material_data['difference']
            material_values.append(abs(current_material))
            
            if abs(current_material - previous_material) > 2:
                stats['material_swings'] += 1
            
            previous_material = current_material
        except:
            pass
    
    # Calculate averages and statistics
    if material_values:
        stats['average_material_balance'] = sum(material_values) / len(material_values)
        stats['max_material_advantage'] = max(material_values)
    
    # Game complexity score
    stats['complexity_score'] = min(10, (
        stats['captures'] * 0.5 +
        stats['checks'] * 0.3 +
        stats['material_swings'] * 1.0
    ))
    
    # Game phases analysis
    total_moves = stats['total_moves']
    stats['game_phases'] = {
        'opening_length': min(15, total_moves),
        'middlegame_length': max(0, min(25, total_moves - 15)),
        'endgame_length': max(0, total_moves - 40)
    }
    
    return stats


def convert_to_piece_icons(move_string: str) -> str:
    """Convert move notation to use piece icons."""
    if not move_string:
        return move_string
    
    piece_icons = {
        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘'
    }
    
    result = move_string
    for piece, icon in piece_icons.items():
        result = result.replace(piece, icon)
    
    return result


def display_enhanced_games_grid(games: List[Dict]):
    """Display games in an enhanced grid with detailed information."""
    st.markdown(f"#### 📊 Found {len(games)} Games")
    
    # Pagination for large result sets
    games_per_page = 10
    total_pages = math.ceil(len(games) / games_per_page)
    
    if total_pages > 1:
        page = st.selectbox("Page:", range(1, total_pages + 1), key="games_pagination")
        start_idx = (page - 1) * games_per_page
        end_idx = start_idx + games_per_page
        display_games = games[start_idx:end_idx]
    else:
        display_games = games
    
    # Enhanced game cards
    for i, game in enumerate(display_games):
        with st.container():
            # Enhanced game card with more details
            st.markdown(f"""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #1a202c;">
                            {game.get('white', 'Unknown')} vs {game.get('black', 'Unknown')}
                        </h4>
                        <div style="color: #718096; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            <strong>Result:</strong> {game.get('result', '*')} • 
                            <strong>Moves:</strong> {game.get('moves', 0)} • 
                            <strong>Date:</strong> {game.get('date', 'Unknown')}
                        </div>
                        <div style="color: #4a5568; font-size: 0.85rem;">
                            <strong>Event:</strong> {game.get('event', 'Unknown')[:40]}{'...' if len(str(game.get('event', ''))) > 40 else ''}<br>
                            <strong>Opening:</strong> {game.get('opening', 'Unknown')[:40]}{'...' if len(str(game.get('opening', ''))) > 40 else ''}<br>
                            <strong>ELOs:</strong> {game.get('white_elo', '?')} / {game.get('black_elo', '?')}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Analyze button
            col1, col2, col3 = st.columns([2, 1, 1])
            with col2:
                if st.button("🎯 Analyze Game", key=f"analyze_{game['id']}_{i}", use_container_width=True, type="primary"):
                    load_game_from_database(game['id'])
            with col3:
                if st.button("👁️ Quick View", key=f"preview_{game['id']}_{i}", use_container_width=True):
                    show_game_preview(game)

