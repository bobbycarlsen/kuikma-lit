# game_analysis.py - Game Analysis Module for Kuikma Chess Engine
import streamlit as st
import sqlite3
import chess
import chess.pgn
import math
import io
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import database
import spatial_analysis

def display_game_analysis():
    """Enhanced game analysis interface with comprehensive features."""
    st.markdown("## 🎮 Game Analysis")
    
    # Analysis mode tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 PGN Analysis", "🔍 Position Explorer", "📊 Game Browser", "⚙️ Batch Processing"
    ])
    
    with tab1:
        display_pgn_analysis_interface()
    
    with tab2:
        display_position_explorer()
    
    with tab3:
        display_game_browser()
    
    with tab4:
        display_batch_processing()

def display_pgn_analysis_interface():
    """Display PGN analysis interface with step-through functionality."""
    st.markdown("### 📝 PGN Game Analysis")
    
    # PGN input methods
    input_method = st.radio(
        "Choose input method:",
        ["📋 Paste PGN", "📁 Upload PGN File", "🗄️ Load from Database"]
    )
    
    pgn_content = None
    
    if input_method == "📋 Paste PGN":
        pgn_content = st.text_area(
            "Paste PGN here:",
            height=200,
            placeholder="""[Event "Example Game"]
[Site "Chess.com"]
[Date "2024.01.01"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6 5.O-O Be7..."""
        )
    
    elif input_method == "📁 Upload PGN File":
        uploaded_file = st.file_uploader(
            "Choose PGN file",
            type=['pgn'],
            help="Upload a PGN file containing one or more games"
        )
        
        if uploaded_file:
            try:
                pgn_content = uploaded_file.read().decode('utf-8')
                st.success(f"✅ Loaded {uploaded_file.name}")
            except Exception as e:
                st.error(f"❌ Error reading file: {e}")
    
    else:  # Load from database
        display_database_game_selector()
    
    # Process PGN if available
    if pgn_content:
        try:
            games = parse_pgn_content(pgn_content)
            if games:
                analyze_pgn_games(games)
            else:
                st.warning("⚠️ No valid games found in PGN")
        except Exception as e:
            st.error(f"❌ Error parsing PGN: {e}")

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

def analyze_pgn_games(games: List[chess.pgn.Game]):
    """Analyze parsed PGN games with comprehensive features."""
    st.markdown(f"### 🎯 Analysis Results ({len(games)} game{'s' if len(games) != 1 else ''})")
    
    if len(games) == 1:
        # Single game analysis
        analyze_single_game(games[0])
    else:
        # Multiple games analysis
        analyze_multiple_games(games)

def analyze_single_game(game: chess.pgn.Game):
    """Comprehensive analysis of a single game."""
    # Game header information
    display_game_header(game)
    
    # Analysis tabs
    analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
        "🎯 Move by Move", "📊 Evaluation Graph", "🔍 Critical Positions", "🏰 Spatial Evolution"
    ])
    
    with analysis_tab1:
        display_move_by_move_analysis(game)
    
    with analysis_tab2:
        display_evaluation_graph(game)
    
    with analysis_tab3:
        display_critical_positions(game)
    
    with analysis_tab4:
        display_spatial_evolution(game)

def display_game_header(game: chess.pgn.Game):
    """Display game header information."""
    headers = game.headers
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏆 Game Information")
        st.markdown(f"**Event:** {headers.get('Event', 'Unknown')}")
        st.markdown(f"**Site:** {headers.get('Site', 'Unknown')}")
        st.markdown(f"**Date:** {headers.get('Date', 'Unknown')}")
        st.markdown(f"**Round:** {headers.get('Round', 'Unknown')}")
    
    with col2:
        st.markdown("#### 👥 Players")
        st.markdown(f"**White:** {headers.get('White', 'Unknown')}")
        st.markdown(f"**Black:** {headers.get('Black', 'Unknown')}")
        st.markdown(f"**Result:** {headers.get('Result', 'Unknown')}")
        
        # Player ratings if available
        white_elo = headers.get('WhiteElo')
        black_elo = headers.get('BlackElo')
        if white_elo:
            st.markdown(f"**White Rating:** {white_elo}")
        if black_elo:
            st.markdown(f"**Black Rating:** {black_elo}")
    
    with col3:
        st.markdown("#### ⏱️ Time Control")
        time_control = headers.get('TimeControl', 'Unknown')
        st.markdown(f"**Time Control:** {time_control}")
        
        # ECO opening if available
        eco = headers.get('ECO')
        opening = headers.get('Opening')
        if eco:
            st.markdown(f"**ECO:** {eco}")
        if opening:
            st.markdown(f"**Opening:** {opening}")

def display_move_by_move_analysis(game: chess.pgn.Game):
    """Display move-by-move analysis with spatial visualization."""
    st.markdown("#### 🎯 Move by Move Analysis")
    
    # Collect all positions
    board = game.board()
    positions = []
    move_number = 1
    
    # Add starting position
    positions.append({
        'move_number': 0,
        'move': 'Starting Position',
        'fen': board.fen(),
        'turn': 'white',
        'board': board.copy()
    })
    
    # Collect moves
    for move in game.mainline_moves():
        color = 'white' if board.turn else 'black'
        san_move = board.san(move)
        board.push(move)
        
        positions.append({
            'move_number': move_number,
            'move': san_move,
            'fen': board.fen(),
            'turn': color,
            'board': board.copy()
        })
        
        if color == 'black':
            move_number += 1
    
    # Position selector
    st.markdown("##### 📍 Navigate Through Game")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        position_index = st.slider(
            "Select position:",
            min_value=0,
            max_value=len(positions) - 1,
            value=0,
            format="Move %d"
        )
    
    with col2:
        if st.button("⏮️ First"):
            position_index = 0
            st.rerun()
    
    with col3:
        if st.button("⏭️ Last"):
            position_index = len(positions) - 1
            st.rerun()
    
    # Display selected position
    if 0 <= position_index < len(positions):
        current_position = positions[position_index]
        display_game_position_analysis(current_position, position_index, len(positions))

def display_game_position_analysis(position: Dict[str, Any], index: int, total: int):
    """Display comprehensive analysis for a game position."""
    st.markdown(f"##### Move {position['move_number']}: {convert_to_piece_icons(position['move'])}")
    
    # Position layout
    board_col, analysis_col = st.columns([1, 1])
    
    with board_col:
        # Display board
        board = position['board']
        flipped = (position['turn'] == 'black')
        
        try:
            board_svg = chess.svg.board(
                board=board,
                flipped=flipped,
                size=400,
                style="""
                .square.light { fill: #f0d9b5; }
                .square.dark { fill: #b58863; }
                .square.light.lastmove { fill: #cdd26a; }
                .square.dark.lastmove { fill: #aaa23a; }
                """
            )
            st.markdown(board_svg, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying board: {e}")
        
        # Position info
        st.markdown(f"**Turn:** {position['turn'].title()}")
        st.markdown(f"**Position:** {index + 1} of {total}")
        
        with st.expander("📋 FEN"):
            st.code(position['fen'])
    
    with analysis_col:
        # Spatial analysis for this position
        try:
            metrics = spatial_analysis.calculate_comprehensive_spatial_metrics(board)
            display_position_spatial_summary(metrics)
        except Exception as e:
            st.warning(f"Spatial analysis unavailable: {e}")
        
        # Legal moves
        legal_moves = list(board.legal_moves)
        st.markdown(f"**Legal Moves:** {len(legal_moves)}")
        
        # Material count
        material = calculate_simple_material(board)
        st.markdown(f"**Material:** White {material['white']} - Black {material['black']}")
        
        # Check status
        if board.is_check():
            st.warning("⚠️ Check!")
        if board.is_checkmate():
            st.error("🏁 Checkmate!")
        if board.is_stalemate():
            st.info("🤝 Stalemate!")

def display_position_spatial_summary(metrics: Dict[str, Any]):
    """Display compact spatial analysis summary."""
    st.markdown("##### 🔍 Position Analysis")
    
    # Space control
    space_control = metrics.get('space_control', {})
    white_space = space_control.get('white_space_percentage', 0)
    black_space = space_control.get('black_space_percentage', 0)
    
    space_col1, space_col2 = st.columns(2)
    with space_col1:
        st.metric("White Space", f"{white_space:.1f}%")
    with space_col2:
        st.metric("Black Space", f"{black_space:.1f}%")
    
    # Center control
    center = metrics.get('center_control', {})
    center_advantage = center.get('center_advantage', 0)
    st.metric("Center Control", f"{center_advantage:+}")
    
    # Material
    material = metrics.get('material_balance', {})
    material_diff = material.get('material_difference', 0)
    st.metric("Material Balance", f"{material_diff:+.1f}")

def display_evaluation_graph(game: chess.pgn.Game):
    """Display evaluation graph throughout the game."""
    st.markdown("#### 📊 Evaluation Graph")
    
    # Note: This would require engine analysis for each position
    # For now, we'll show a placeholder
    st.info("📈 Evaluation graph requires engine analysis of each position. This feature will analyze the game with an engine to show evaluation changes throughout the game.")
    
    # Placeholder data for demonstration
    moves = list(range(1, 41))  # 40 moves
    evaluations = [0.2 * i + 0.1 * (i % 5) for i in range(40)]  # Sample data
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=moves,
        y=evaluations,
        mode='lines+markers',
        name='Position Evaluation',
        line=dict(color='#667eea', width=3)
    ))
    
    fig.update_layout(
        title='Game Evaluation Progress',
        xaxis_title='Move Number',
        yaxis_title='Evaluation (pawns)',
        hovermode='x unified'
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    st.plotly_chart(fig, use_container_width=True)

def display_critical_positions(game: chess.pgn.Game):
    """Identify and display critical positions in the game."""
    st.markdown("#### 🔍 Critical Positions")
    
    st.info("🎯 This feature will identify the most critical positions in the game based on evaluation changes, tactical opportunities, and strategic turning points.")
    
    # For now, show some key positions
    board = game.board()
    positions = []
    move_count = 0
    
    # Sample critical positions (every 10 moves for demo)
    for move in game.mainline_moves():
        move_count += 1
        san_move = board.san(move)
        board.push(move)
        
        if move_count % 10 == 0:  # Every 10th move as "critical"
            positions.append({
                'move_number': move_count,
                'move': san_move,
                'fen': board.fen(),
                'reason': f'Strategic turning point at move {move_count}'
            })
    
    if positions:
        for i, pos in enumerate(positions[:5]):  # Show first 5
            with st.expander(f"Move {pos['move_number']}: {convert_to_piece_icons(pos['move'])}"):
                st.markdown(f"**Reason:** {pos['reason']}")
                
                try:
                    board = chess.Board(pos['fen'])
                    board_svg = chess.svg.board(board=board, size=300)
                    st.markdown(board_svg, unsafe_allow_html=True)
                except:
                    st.error("Error displaying position")

def display_spatial_evolution(game: chess.pgn.Game):
    """Show spatial control evolution throughout the game."""
    st.markdown("#### 🏰 Spatial Evolution")
    
    try:
        # Analyze spatial metrics at key points
        board = game.board()
        spatial_data = []
        move_number = 0
        
        # Analyze every 5th move to show evolution
        for i, move in enumerate(game.mainline_moves()):
            board.push(move)
            move_number += 1
            
            if move_number % 5 == 0:  # Every 5 moves
                try:
                    metrics = spatial_analysis.calculate_comprehensive_spatial_metrics(board)
                    space_control = metrics.get('space_control', {})
                    
                    spatial_data.append({
                        'Move': move_number,
                        'White Space': space_control.get('white_space_percentage', 0),
                        'Black Space': space_control.get('black_space_percentage', 0),
                        'Center Control': metrics.get('center_control', {}).get('center_advantage', 0),
                        'Material Balance': metrics.get('material_balance', {}).get('material_difference', 0)
                    })
                except:
                    pass  # Skip positions that can't be analyzed
        
        if spatial_data:
            df = pd.DataFrame(spatial_data)
            
            # Space control evolution
            fig1 = px.line(
                df, 
                x='Move', 
                y=['White Space', 'Black Space'],
                title='Space Control Evolution',
                labels={'value': 'Space Control %', 'variable': 'Player'}
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Center control evolution
            fig2 = px.line(
                df,
                x='Move',
                y='Center Control',
                title='Center Control Evolution',
                labels={'Center Control': 'Center Advantage'}
            )
            fig2.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            st.plotly_chart(fig2, use_container_width=True)
            
            # Data table
            st.markdown("##### 📊 Spatial Metrics Data")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("⚠️ No spatial data available for this game")
            
    except Exception as e:
        st.error(f"Error in spatial evolution analysis: {e}")

def display_position_explorer():
    """Position explorer for analyzing specific positions."""
    st.markdown("### 🔍 Position Explorer")
    
    st.info("🎯 Explore specific positions from your games or set up custom positions for deep analysis.")
    
    # Position input
    position_input = st.radio(
        "Choose position input:",
        ["📋 FEN Input", "♟️ Board Editor", "🗄️ Database Position"]
    )
    
    if position_input == "📋 FEN Input":
        fen = st.text_input(
            "Enter FEN:",
            value="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        
        if fen:
            try:
                board = chess.Board(fen)
                analyze_position_detailed(board, fen)
            except Exception as e:
                st.error(f"❌ Invalid FEN: {e}")
    
    elif position_input == "♟️ Board Editor":
        st.info("🚧 Visual board editor coming soon! For now, please use FEN input.")
    
    else:  # Database position
        position_id = st.number_input("Position ID:", min_value=1, value=1)
        if st.button("Load Position"):
            position_data = load_position_from_database(position_id)
            if position_data:
                fen = position_data.get('fen')
                if fen:
                    board = chess.Board(fen)
                    analyze_position_detailed(board, fen)

def analyze_position_detailed(board: chess.Board, fen: str):
    """Detailed analysis of a specific position."""
    st.markdown("#### 🎯 Position Analysis")
    
    # Display board and basic info
    board_col, info_col = st.columns([1, 1])
    
    with board_col:
        flipped = not board.turn  # Flip if black to move
        
        board_svg = chess.svg.board(
            board=board,
            flipped=flipped,
            size=400,
            style="""
            .square.light { fill: #f0d9b5; }
            .square.dark { fill: #b58863; }
            """
        )
        st.markdown(board_svg, unsafe_allow_html=True)
        
        # Board orientation
        orientation = "White to move (White at bottom)" if board.turn else "Black to move (Black at bottom)"
        st.caption(f"📋 {orientation}")
    
    with info_col:
        st.markdown("##### 📊 Position Information")
        st.markdown(f"**Turn:** {'White' if board.turn else 'Black'}")
        st.markdown(f"**Legal Moves:** {len(list(board.legal_moves))}")
        
        material = calculate_simple_material(board)
        st.markdown(f"**Material Balance:** {material['white']} - {material['black']} = {material['white'] - material['black']:+}")
        
        # Game status
        if board.is_check():
            st.warning("⚠️ In Check")
        if board.is_checkmate():
            st.error("🏁 Checkmate")
        if board.is_stalemate():
            st.info("🤝 Stalemate")
        
        # Castling rights
        castling = []
        if board.has_kingside_castling_rights(chess.WHITE):
            castling.append("K")
        if board.has_queenside_castling_rights(chess.WHITE):
            castling.append("Q")
        if board.has_kingside_castling_rights(chess.BLACK):
            castling.append("k")
        if board.has_queenside_castling_rights(chess.BLACK):
            castling.append("q")
        
        castling_str = "".join(castling) if castling else "None"
        st.markdown(f"**Castling Rights:** {castling_str}")
        
        # En passant
        ep_square = board.ep_square
        if ep_square:
            st.markdown(f"**En Passant:** {chess.square_name(ep_square)}")
    
    # Detailed analysis tabs
    detail_tab1, detail_tab2, detail_tab3 = st.tabs([
        "🔍 Spatial Analysis", "⚡ Legal Moves", "📈 Engine Analysis"
    ])
    
    with detail_tab1:
        try:
            metrics = spatial_analysis.calculate_comprehensive_spatial_metrics(board)
            display_comprehensive_spatial_metrics(metrics)
        except Exception as e:
            st.error(f"Spatial analysis error: {e}")
    
    with detail_tab2:
        display_legal_moves_analysis(board)
    
    with detail_tab3:
        st.info("🚧 Engine analysis integration coming soon!")

def display_comprehensive_spatial_metrics(metrics: Dict[str, Any]):
    """Display comprehensive spatial metrics."""
    # Space control
    space_control = metrics.get('space_control', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        white_space = space_control.get('white_space_percentage', 0)
        st.metric("White Space", f"{white_space:.1f}%")
    
    with col2:
        black_space = space_control.get('black_space_percentage', 0)
        st.metric("Black Space", f"{black_space:.1f}%")
    
    with col3:
        contested = space_control.get('contested_percentage', 0)
        st.metric("Contested", f"{contested:.1f}%")
    
    with col4:
        advantage = space_control.get('space_advantage', 0)
        st.metric("Space Advantage", f"{advantage:+.0f}")
    
    # Center control
    st.markdown("##### 🎯 Center Control")
    center = metrics.get('center_control', {})
    
    center_col1, center_col2, center_col3 = st.columns(3)
    
    with center_col1:
        center_adv = center.get('center_advantage', 0)
        st.metric("Center Advantage", f"{center_adv:+}")
    
    with center_col2:
        extended_adv = center.get('extended_advantage', 0)
        st.metric("Extended Center", f"{extended_adv:+}")
    
    with center_col3:
        occupation_adv = center.get('occupation_advantage', 0)
        st.metric("Center Occupation", f"{occupation_adv:+}")

def display_legal_moves_analysis(board: chess.Board):
    """Display analysis of legal moves."""
    legal_moves = list(board.legal_moves)
    
    st.markdown(f"##### ⚡ Legal Moves ({len(legal_moves)})")
    
    if legal_moves:
        # Group moves by piece type
        move_groups = {}
        
        for move in legal_moves:
            piece = board.piece_at(move.from_square)
            if piece:
                piece_name = chess.piece_name(piece.piece_type)
                if piece_name not in move_groups:
                    move_groups[piece_name] = []
                
                san_move = board.san(move)
                move_groups[piece_name].append({
                    'move': san_move,
                    'from': chess.square_name(move.from_square),
                    'to': chess.square_name(move.to_square),
                    'uci': move.uci()
                })
        
        # Display by piece type
        for piece_type, moves in move_groups.items():
            with st.expander(f"{piece_type.title()} moves ({len(moves)})"):
                move_cols = st.columns(min(4, len(moves)))
                
                for i, move_data in enumerate(moves[:8]):  # Show first 8 moves
                    col_idx = i % 4
                    with move_cols[col_idx]:
                        formatted_move = convert_to_piece_icons(move_data['move'])
                        st.markdown(f"**{formatted_move}**")
                        st.caption(f"{move_data['from']} → {move_data['to']}")

def search_database_games(
    player_filter: Optional[str] = None,
    result_filter: Optional[str] = None,
    date_from: Optional[Any] = None,
    date_to: Optional[Any] = None,
    event_filter: Optional[str] = None,
    opening_filter: Optional[str] = None,
    min_elo: Optional[int] = None,
    max_elo: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Search games in the DB with a bunch of filters.
    - result_filter="All" means any of 1-0, 0-1, 1/2-1/2
    - Only applies min_elo/max_elo if you pass a positive int.
    """
    conn = None
    try:
        conn = database.get_db_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        base_sql = """
            SELECT
                id,
                white_player   AS white,
                black_player   AS black,
                white_elo,
                black_elo,
                event,
                opening,
                result,
                date,
                total_moves    AS moves
            FROM games
        """
        where_clauses: List[str] = []
        params: Dict[str, Any] = {}

        if player_filter:
            where_clauses.append("(white_player LIKE :player OR black_player LIKE :player)")
            params["player"] = f"%{player_filter}%"

        if result_filter and result_filter.lower() != "all":
            where_clauses.append("result = :result")
            params["result"] = result_filter
        elif result_filter and result_filter.lower() == "all":
            where_clauses.append("result IN ('1-0','0-1','1/2-1/2')")

        if date_from:
            where_clauses.append("date >= :date_from")
            params["date_from"] = date_from
        if date_to:
            where_clauses.append("date <= :date_to")
            params["date_to"] = date_to

        if event_filter:
            where_clauses.append("event LIKE :event")
            params["event"] = f"%{event_filter}%"
        if opening_filter:
            where_clauses.append("opening LIKE :opening")
            params["opening"] = f"%{opening_filter}%"

        # Only add the Elo filters if user actually set something > 0
        if isinstance(min_elo, int) and min_elo > 0:
            where_clauses.append("(white_elo >= :min_elo AND black_elo >= :min_elo)")
            params["min_elo"] = min_elo
        if isinstance(max_elo, int) and max_elo > 0:
            where_clauses.append("(white_elo <= :max_elo AND black_elo <= :max_elo)")
            params["max_elo"] = max_elo

        sql = base_sql
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " ORDER BY date DESC"

        # --- DEBUG: show exactly what we're sending to SQLite ---
        st.write("🔍 Query:", sql)
        st.write("🔢 Params:", params)

        cur.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    except Exception as e:
        st.error(f"Error loading games: {e}")
        return []
    finally:
        if conn:
            conn.close()

def display_game_browser():
    """Game browser with filters, sensible defaults, and working pagination."""
    st.markdown("### 📊 Game Browser")
    st.info("🗄️ Browse and filter games stored in your database.")

    # --- Search form ---
    with st.form("game_search"):
        col1, col2, col3 = st.columns(3)
        with col1:
            player_filter = st.text_input("Player (White or Black):", key="filter_player")
        with col2:
            result_filter = st.selectbox(
                "Result:", ["All", "1-0", "0-1", "1/2-1/2"],
                index=0, key="filter_result"
            )
        with col3:
            date_filter = st.date_input("Date (any):", value=None, key="filter_date")

        col4, col5, col6, col7 = st.columns(4)
        with col4:
            event_filter = st.text_input("Event (any):", key="filter_event")
        with col5:
            opening_filter = st.text_input("Opening (any):", key="filter_opening")
        with col6:
            min_elo = st.number_input("Min ELO:", min_value=0, value=0, step=1, key="filter_min_elo")
        with col7:
            max_elo = st.number_input("Max ELO:", min_value=0, value=9999, step=1, key="filter_max_elo")

        per_page = st.selectbox("Games per page:", [5, 10, 20], index=1, key="per_page")

        submitted = st.form_submit_button("🔍 Search Games")

    if submitted:
        games = search_database_games(
            player_filter=player_filter.strip() or None,
            result_filter=result_filter,
            date_from=date_filter if date_filter else None,
            date_to=date_filter if date_filter else None,
            event_filter=event_filter.strip() or None,
            opening_filter=opening_filter.strip() or None,
            min_elo=min_elo if min_elo > 0 else None,
            max_elo=max_elo if max_elo < 9999 else None
        )
        st.session_state.games = games
        # initialize page to 1 before widget
        st.session_state.page = 1

    games: List[Dict[str, Any]] = st.session_state.get("games", [])
    if not games:
        return

    total = len(games)
    pages = math.ceil(total / st.session_state.per_page)

    # Ensure page exists for selectbox initial index
    if "page" not in st.session_state:
        st.session_state.page = 1

    # Create the selectbox (this manages session_state.page for us)
    st.selectbox(
        "Page:",
        options=list(range(1, pages + 1)),
        index=st.session_state.page - 1,
        key="page"
    )

    # Read the selected page
    page = st.session_state.page
    start = (page - 1) * st.session_state.per_page
    end = start + st.session_state.per_page

    display_game_search_results(games[start:end])


def display_game_search_results(games: List[Dict[str, Any]]):
    """Show a page of search results."""
    st.markdown(f"##### 🎯 Showing {len(games)} games")
    for g in games:
        header = f"{g['white']} vs {g['black']} – {g['result']} – {g['date']}"
        with st.expander(header):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Event:** {g.get('event', '–')}")
                st.markdown(f"**Opening:** {g.get('opening', '–')}")
            with c2:
                st.markdown(f"**Moves:** {g['moves']}")
                st.markdown(f"**ELOs:** {g.get('white_elo', '–')} / {g.get('black_elo', '–')}")
            with c3:
                if st.button("Analyze", key=f"analyze_{g['id']}"):
                    st.info(f"Loading game {g['id']} for analysis...")


def display_batch_processing():
    """Batch processing interface."""
    st.markdown("### ⚙️ Batch Processing")
    
    st.info("🔄 Process multiple games at once for comprehensive analysis.")
    
    # Processing options
    st.markdown("#### Processing Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        process_spatial = st.checkbox("Include spatial analysis", value=True)
        process_tactics = st.checkbox("Tactical analysis", value=False)
        process_openings = st.checkbox("Opening classification", value=False)
    
    with col2:
        max_games = st.number_input("Max games to process:", min_value=1, max_value=100, value=10)
        depth_limit = st.number_input("Analysis depth:", min_value=10, max_value=25, value=15)
    
    if st.button("🚀 Start Batch Processing"):
        st.info("🚧 Batch processing will be implemented to analyze multiple games efficiently.")

# Utility functions
def convert_to_piece_icons(move_string: str) -> str:
    """Convert move notation to use piece icons."""
    piece_icons = {
        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘'
    }
    
    if not move_string:
        return move_string
    
    result = move_string
    for piece, icon in piece_icons.items():
        result = result.replace(piece, icon)
    
    return result

def calculate_simple_material(board: chess.Board) -> Dict[str, int]:
    """Calculate simple material count."""
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    
    white_total = 0
    black_total = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                white_total += value
            else:
                black_total += value
    
    return {
        'white': white_total,
        'black': black_total
    }

def load_position_from_database(position_id: int) -> Optional[Dict[str, Any]]:
    """Load position from database."""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM positions WHERE id = ?', (position_id,))
        position_row = cursor.fetchone()
        
        if position_row:
            return dict(position_row)
        
        conn.close()
        return None
        
    except Exception as e:
        st.error(f"Error loading position: {e}")
        return None

def display_database_game_selector():
    """Display interface for selecting games from database."""
    st.info("🗄️ Game database integration coming soon! This will allow you to select and analyze games stored in your database.")
    
    # Placeholder for database game selection
    game_id = st.number_input("Game ID:", min_value=1, value=1)
    if st.button("Load Game"):
        st.info(f"Loading game {game_id} from database...")
