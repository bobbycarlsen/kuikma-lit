# html_generator.py - Kuikma Comprehensive HTML Template Generator
import os
import re
import json
import chess
import chess.svg
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from move_comparison_analyzer import MoveComparisonAnalyzer


class ComprehensiveHTMLGenerator:
    """Enhanced HTML generator with spatial analysis, color-coded notation, and variation boards."""
    
    def __init__(self, output_dir: str = "kuikma_analysis", css_file_path: str = "comprehensive_chess_analysis.css"):
        self.output_dir = output_dir
        self.css_file_path = css_file_path
        self.ensure_output_directory()
        self.move_comparison_analyzer = MoveComparisonAnalyzer(self)

    def ensure_output_directory(self):
        """Ensure output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_chess_board_svg(self, fen: str, flipped: bool = None, size: int = 400, highlight_squares: List[str] = None) -> str:
        """Generate SVG representation of chess board with proper orientation and optional square highlighting."""
        try:
            board = chess.Board(fen)
            
            # Auto-determine flip based on turn if not specified
            if flipped is None:
                flipped = not board.turn  # Flip if black to move
            
            # Create highlight style for moves
            highlight_style = ""
            if highlight_squares:
                for i, square_name in enumerate(highlight_squares):
                    if square_name:
                        try:
                            square = chess.parse_square(square_name)
                            color = "#ff6b6b" if i == 0 else "#51cf66"  # Red for from, green for to
                            highlight_style += f'.square-{square_name} {{ fill: {color} !important; stroke: #2c3e50; stroke-width: 3; }} '
                        except:
                            pass
            
            svg = chess.svg.board(
                board=board,
                flipped=flipped,
                size=size,
                style=f"""
                .square.light {{ fill: #f0d9b5; }}
                .square.dark {{ fill: #b58863; }}
                .piece {{ font-size: {size * 0.11}px; }}
                {highlight_style}
                """
            )
            return svg
        except Exception as e:
            return f'<div style="border: 2px solid #ddd; padding: 20px; text-align: center;">Chess board generation failed: {str(e)}</div>'
    
    def generate_result_board_svg(self, fen: str, best_move_uci: str, flipped: bool = None, size: int = 400) -> str:
        """Generate board after best move is played with move highlighting and proper orientation."""
        try:
            board = chess.Board(fen)
            
            # Auto-determine flip based on turn if not specified
            if flipped is None:
                flipped = not board.turn  # Flip if black to move
                
            highlight_squares = []
            
            if best_move_uci:
                try:
                    move = chess.Move.from_uci(best_move_uci)
                    if move in board.legal_moves:
                        # Get from and to squares for highlighting
                        from_square = chess.square_name(move.from_square)
                        to_square = chess.square_name(move.to_square)
                        highlight_squares = [from_square, to_square]
                        board.push(move)
                except:
                    pass
            
            return self.generate_chess_board_svg(board.fen(), flipped=flipped, size=size, highlight_squares=highlight_squares)
        except:
            return '<div style="border: 2px dashed #ddd; padding: 20px; text-align: center;">Result position unavailable</div>'

    def convert_to_piece_icons(self, move_string: str) -> str:
        """Convert move notation to use piece icons instead of letters."""
        piece_icons = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘'
        }
        
        if not move_string:
            return move_string
        
        # Handle different move formats
        result = move_string
        
        # Replace piece letters with icons (but not pawns)
        for piece, icon in piece_icons.items():
            result = result.replace(piece, icon)
        
        return result


    def get_dynamic_task_description(self, position_data: Dict[str, Any]) -> str:
        """Generate dynamic task description based on position data."""
        turn = position_data.get('turn', 'white').lower()
        move_number = position_data.get('fullmove_number', 1)
        
        color_name = "White" if turn == 'white' else "Black"
        color_style = "color: #4299e1;" if turn == 'white' else "color: #805ad5;"
        
        return f"""
        <p style="font-size: 1.1rem; line-height: 1.6; color: #424242;">
            Find the best possible move for <strong style="{color_style}">{color_name}</strong> 
            in this position (Move {move_number}). Analyze the position carefully, considering 
            tactical opportunities, positional factors, and long-term strategic goals.
        </p>
        """

    def parse_principal_variation(self, pv_string: str, starting_fen: str, max_moves: int = 10) -> Tuple[List[str], str]:
        """Parse principal variation string and return list of positions."""
        positions = []
        final_fen = starting_fen
        
        try:
            board = chess.Board(starting_fen)
            
            if not pv_string:
                return [starting_fen], starting_fen
            
            # Clean the PV string
            pv_clean = pv_string.replace('...', '').strip()
            moves = pv_clean.split()
            moves_parsed = 0
            
            # Add starting position
            positions.append(board.fen())
            
            for move_str in moves:
                if moves_parsed >= max_moves:
                    break
                
                # Clean move string (remove move numbers, dots, annotations)
                clean_move = re.sub(r'^\d+\.+', '', move_str).strip()
                clean_move = re.sub(r'[!?]+$', '', clean_move).strip()
                
                if not clean_move or clean_move.isdigit():
                    continue
                
                try:
                    # Try to parse and make the move
                    move = board.parse_san(clean_move)
                    if move in board.legal_moves:
                        board.push(move)
                        positions.append(board.fen())
                        moves_parsed += 1
                    else:
                        break
                except (ValueError, chess.InvalidMoveError):
                    break
            
            final_fen = board.fen()
            
        except Exception as e:
            print(f"Error parsing principal variation: {e}")
            
        return positions, final_fen

    # === ADD THESE NEW METHODS TO THE EXISTING CLASS ===
    
    def generate_epic_analysis_report(self, position_data: Dict[str, Any], 
                                    selected_move_data: Dict[str, Any] = None) -> str:
        """
        Main method to generate the epic chess analysis report.
        This is the primary entry point for the enhanced analysis.
        """
        return self.generate_comprehensive_strategic_analysis(
            position_data=position_data,
            selected_move_data=selected_move_data,
            include_spatial_analysis=True,
            include_side_by_side=True,
            include_detailed_stats=True,
            print_optimized=True
        )

    def generate_comprehensive_strategic_analysis(self, position_data: Dict[str, Any], 
                                                selected_move_data: Dict[str, Any] = None,
                                                analysis_results: Dict[str, Any] = None,
                                                include_spatial_analysis: bool = True,
                                                include_side_by_side: bool = True,
                                                include_detailed_stats: bool = True,
                                                print_optimized: bool = True) -> str:
        """Generate comprehensive chess position analysis report with enhanced features."""
        
        # Extract basic position information
        position_id = position_data.get('id', 'unknown')
        fen = position_data.get('fen', '')
        turn = position_data.get('turn', 'white').lower()
        move_number = position_data.get('fullmove_number', 1)
        top_moves = position_data.get('top_moves', [])
        
        # Board orientation - flip based on turn
        flipped = (turn == 'black')
        
        # Get best move
        best_move = top_moves[0] if top_moves else {}
        best_move_notation = best_move.get('move', 'N/A')
        best_move_uci = best_move.get('uci', '')
        
        # Generate boards with move highlighting and proper orientation
        current_board_svg = self.generate_chess_board_svg(fen, flipped=flipped)
        result_board_svg = self.generate_result_board_svg(fen, best_move_uci, flipped)
        
        # Generate all sections
        problem_section = self._generate_problem_section(current_board_svg, position_data)
        solution_section = self._generate_solution_section(current_board_svg, result_board_svg, best_move_notation, position_data)
        comprehensive_move_comparison = self.move_comparison_analyzer.generate_comprehensive_move_comparison_section(position_data)
        comparative_analysis = self._generate_comparative_analysis_section(position_data, best_move)
        top_moves_section = self._generate_top_moves_section(top_moves, turn, move_number)
        
        # Enhanced variations with boards
        variations_section = self._generate_enhanced_principal_variations_section(position_data, fen)
        
        learning_insights_section = self._generate_comprehensive_learning_insights_section(position_data, selected_move_data)
        strategic_insights_section = self._generate_comprehensive_strategic_insights_section(position_data, selected_move_data)
        
        # Enhanced spatial analysis with comparison
        spatial_section = ""
        if include_spatial_analysis:
            # Calculate result position for spatial comparison
            result_fen = fen
            if best_move_uci:
                try:
                    result_board = chess.Board(fen)
                    move = chess.Move.from_uci(best_move_uci)
                    if move in result_board.legal_moves:
                        result_board.push(move)
                        result_fen = result_board.fen()
                except:
                    pass
            spatial_section = self._generate_spatial_comparison_section(fen, result_fen, best_move)
        
        # Read CSS content
        css_content = self._read_css_file()
        
        # Build complete HTML
        html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chess Position Analysis - {position_data.get('title', f'Position {position_id}')}</title>
        <style>
            {css_content}
        </style>
    </head>
    <body>
        <div class="analysis-container">
            <header class="report-header">
                <h1>🏆 Comprehensive Chess Position Analysis</h1>
                <div class="position-meta">
                    <span class="meta-item">Position #{position_id}</span>
                    <span class="meta-item">Move {move_number}</span>
                    <span class="meta-item">{turn.title()} to Move</span>
                    <span class="meta-item">{position_data.get('game_phase', 'Middlegame').title()}</span>
                    <span class="meta-item">Rating: {position_data.get('difficulty_rating', 1200)}</span>
                </div>
            </header>

            {problem_section}
            {solution_section}
            {comprehensive_move_comparison}
            {spatial_section}
            {strategic_insights_section}
            {comparative_analysis}
            {top_moves_section}
            {variations_section}
            {learning_insights_section}

            <footer class="report-footer">
                <p>Generated by Kuikma Chess Engine • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Enhanced comprehensive analysis with spatial comparison and variation boards</p>
            </footer>
        </div>
    </body>
    </html>
    """
        
        # Save and return path
        filename = f"enhanced_comprehensive_analysis_{position_id}_{int(datetime.now().timestamp())}.html"
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        return output_path

    def _read_css_file(self) -> str:
        """Read CSS from external file, fallback to basic CSS if file not found."""
        try:
            with open(self.css_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return """
            /* Fallback CSS */
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 20px; }
            .analysis-container { max-width: 1200px; margin: 0 auto; }
            .section { margin: 2rem 0; padding: 1rem; background: #f8f9fa; border-radius: 8px; }
            .section-header { font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem; }
            .analysis-table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
            .analysis-table th, .analysis-table td { padding: 0.5rem; border: 1px solid #ddd; }
            .analysis-table th { background: #4299e1; color: white; }
            """

    # === UTILITY METHODS ===
    
    def format_score_display(self, score) -> str:
        """Format score for display with proper handling of different score types."""
        if score is None:
            return "0.00"
        
        if isinstance(score, dict):
            if 'mate' in score:
                mate_value = score['mate']
                return f"M{mate_value}" if mate_value > 0 else f"M{abs(mate_value)}"
            elif 'cp' in score:
                return f"{score['cp']:.2f}"
            else:
                return "0.00"
        elif isinstance(score, (int, float)):
            if abs(score) > 900:  # Likely centipawns
                return f"{score:.2f}"
            else:
                return f"{score:.2f}"
        else:
            try:
                return f"{float(score):.2f}"
            except:
                return str(score)
    
    def get_score_class(self, score) -> str:
        """Get CSS class for score styling based on evaluation."""
        if score is None:
            return 'score-neutral'
        
        if isinstance(score, dict):
            if 'mate' in score:
                return 'score-positive' if score['mate'] > 0 else 'score-negative'
            elif 'cp' in score:
                cp = score['cp']
                if cp > 50:
                    return 'score-positive'
                elif cp < -50:
                    return 'score-negative'
                else:
                    return 'score-neutral'
        elif isinstance(score, (int, float)):
            if score > 0.5:
                return 'score-positive'
            elif score < -0.5:
                return 'score-negative'
            else:
                return 'score-neutral'
        
        return 'score-neutral'
    
    def get_advantage_class(self, value: float) -> str:
        """Get CSS class for advantage display."""
        if value > 0.1:
            return 'change-positive'
        elif value < -0.1:
            return 'change-negative'
        else:
            return 'change-neutral'

    def _generate_problem_section(self, board_svg: str, position_data: Dict[str, Any]) -> str:
        """Generate the problem presentation section with dynamic task description."""
        move_history = self._extract_move_history(position_data)
        themes = position_data.get('themes', [])
        # tmp fix for I K A N
        themes = sorted(themes, key=len, reverse=True)
        themes_html = ""
        if themes:
            theme_tags = ''.join([
                f'<span class="theme-tag">{theme.replace("_", " ").title()}</span>' 
                for theme in themes[:7]
            ])
            themes_html = f'<div style="margin-top: 1rem;">{theme_tags}</div>'
        
        # Get dynamic task description
        task_description = self.get_dynamic_task_description(position_data)
        
        return f"""
        <section class="section">
            <div class="section-header">
                🎯 The Challenge
            </div>
            <div class="side-by-side">
                <div>
                    <div class="board-container">
                        <div class="board-label">Current Position</div>
                        {board_svg}
                    </div>
                                        
                    <div style="background: #e3f2fd; padding: 1.5rem; border-radius: 12px; margin-top: 1.5rem; border-left: 4px solid #2196f3;">
                        <h4 style="color: #1976d2; margin-bottom: 1rem;">Your Task</h4>
                        {task_description}
                        {themes_html}
                    </div>
                </div>
                <div>
                    <h3>Position Information</h3>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-label">Difficulty Rating</div>
                            <div class="metric-value">{position_data.get('difficulty_rating', 1200)}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Game Phase</div>
                            <div class="metric-value">{position_data.get('game_phase', 'Middlegame').title()}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Position Type</div>
                            <div class="metric-value">{position_data.get('position_type', 'Tactical').title()}</div>
                        </div>
                    </div>

                    {move_history}
                </div>
            </div>
        </section>
        <div class="page-break"></div>
        """

    def _generate_solution_section(self, current_board_svg: str, result_board_svg: str, 
                                  best_move: str, position_data: Dict[str, Any]) -> str:
        """Generate the solution with side-by-side comparison and color-coded notation."""
        top_moves = position_data.get('top_moves', [])
        best_move_data = top_moves[0] if top_moves else {}
        
        score = best_move_data.get('score', 0)
        score_display = self.format_score_display(score)
        score_class = self.get_score_class(score)
        
        pv = best_move_data.get('principal_variation', '')
        colored_pv = self.convert_to_piece_icons(pv)
        colored_best_move = self.convert_to_piece_icons(best_move)
        
        tactics = best_move_data.get('tactics', [])
        
        tactics_html = ""
        if tactics:
            tactics_tags = ''.join([
                f'<span class="theme-tag">{tactic.replace("_", " ").title()}</span>' 
                for tactic in tactics
            ])
            tactics_html = f'<div style="margin-top: 1rem;"><strong>Tactical Elements:</strong><br>{tactics_tags}</div>'
        
        # Position impact analysis
        position_impact = best_move_data.get('position_impact', {})
        
        return f"""
        <section class="section">
            <div class="section-header">
                ✅ The Solution
            </div>
            <div class="side-by-side">
                <div>
                    <div class="board-container">
                        <div class="board-label">Current Position</div>
                        {current_board_svg}
                    </div>
                </div>
                <div>
                    <div class="board-container">
                        <div class="board-label">After Best Move: {colored_best_move}</div>
                        {result_board_svg}
                        <p style="text-align: center; font-size: 0.85rem; color: #666; margin-top: 0.5rem;">
                            🔴 From square &nbsp;&nbsp; 🟢 To square
                        </p>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 2rem;">
                <h3>Best Move Analysis</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Engine Evaluation</div>
                        <div class="metric-value {score_class}">{score_display}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Classification</div>
                        <div class="metric-value">{best_move_data.get('classification', 'N/A').title()}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Search Depth</div>
                        <div class="metric-value">{best_move_data.get('depth', 0)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Strategic Value</div>
                        <div class="metric-value">{best_move_data.get('strategic_value', 0)}/5</div>
                    </div>
                </div>
                
                <div style="margin-top: 1.5rem;">
                    <h4>Move Impact Analysis</h4>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-label">Material Change</div>
                            <div class="metric-value change-positive">+{position_impact.get('material_change', 0)}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">King Safety Impact</div>
                            <div class="metric-value {self.get_advantage_class(position_impact.get('king_safety_impact', 0))}">{position_impact.get('king_safety_impact', 0):+.1f}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Center Control</div>
                            <div class="metric-value {self.get_advantage_class(position_impact.get('center_control_change', 0))}">{position_impact.get('center_control_change', 0):+.1f}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Initiative Change</div>
                            <div class="metric-value {self.get_advantage_class(position_impact.get('initiative_change', 0))}">{position_impact.get('initiative_change', 0):+.1f}</div>
                        </div>
                    </div>
                </div>
                
                {tactics_html}
                
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; margin-top: 1.5rem; border: 1px solid #e2e8f0;">
                    <h4>Principal Variation</h4>
                    <div class="variation-moves">{colored_pv}</div>
                </div>
            </div>
        </section>
        <div class="page-break"></div>
        """

    def _generate_enhanced_principal_variations_section(self, position_data: Dict[str, Any], current_fen: str) -> str:
        """Generate enhanced principal variations section with board positions for each variation."""
        variation_analysis = position_data.get('variation_analysis', {})
        variations = variation_analysis.get('variations', [])
        top_moves = position_data.get('top_moves', [])  # Fallback to top moves
        turn = position_data.get('turn', 'white').lower()
        flipped = (turn == 'black')
        
        if not variations and not top_moves:
            return ""
        
        # Use variations if available, otherwise use top_moves
        moves_to_analyze = variations if variations else top_moves
        
        variations_html = ""
        for i, variation in enumerate(moves_to_analyze):
            if variations:
                # Using variation_analysis data
                initial_move = variation.get('initial_move', {})
                move_name = initial_move.get('move', f'Variation {i+1}')
                score = initial_move.get('score', 0)
                pv_notation = initial_move.get('pv', initial_move.get('principal_variation', move_name))
                tactics = initial_move.get('tactics', [])
                position_impact = initial_move.get('position_impact', {})
            else:
                # Using top_moves data
                move_name = variation.get('move', f'Variation {i+1}')
                score = variation.get('score', 0)
                pv_notation = variation.get('pv', variation.get('principal_variation', move_name))
                tactics = variation.get('tactics', [])
                position_impact = variation.get('position_impact', {})
            
            score_display = self.format_score_display(score)
            colored_pv = self.convert_to_piece_icons(pv_notation)
            colored_move_name = self.convert_to_piece_icons(move_name)
            tactics_text = ", ".join([t.replace("_", " ").title() for t in tactics]) if tactics else "None identified"
            
            # Parse the principal variation to get multiple board positions
            positions, final_fen = self.parse_principal_variation(pv_notation, current_fen, max_moves=20)
            
            # Generate boards for key positions
            boards_html = ""
            if len(positions) > 1:
                # Show first 8 positions of the variation with proper orientation
                positions_to_show = positions[:min(20, len(positions))]
                boards_html = f"""
                <div class="variation-boards-row">
                """
                
                for pos_idx, pos_fen in enumerate(positions_to_show):
                    board_svg = self.generate_chess_board_svg(pos_fen, flipped, 160)
                    move_label = f"Start" if pos_idx == 0 else f"Move {pos_idx}"
                    boards_html += f"""
                    <div class="variation-board-item">
                        <div class="variation-board-label">{move_label}</div>
                        {board_svg}
                    </div>
                    """
                
                boards_html += "</div>"
            else:
                # Fallback to single final position
                final_board_svg = self.generate_chess_board_svg(final_fen, flipped, 200)
                boards_html = f"""
                <div class="variation-boards-row">
                    <div class="variation-board-item">
                        <div class="variation-board-label">Final Position</div>
                        {final_board_svg}
                    </div>
                </div>
                """
            
            card_class = "variation-move-set best-variation" if i == 0 else "variation-move-set"
            header_class = "variation-set-header best-header" if i == 0 else "variation-set-header"
            
            variations_html += f"""
            <div class="{card_class}">
                <div class="{header_class}">
                    <div class="variation-set-title">#{i+1} - {colored_move_name}</div>
                    <div class="variation-set-meta">
                        <span class="score-badge {self.get_score_class(score)}">{score_display}</span>
                        <span class="cp-badge">CP Loss: {variation.get('centipawn_loss', 0)}</span>
                        <span class="classification-badge">{variation.get('classification', 'Unknown')}</span>
                    </div>
                </div>
                
                {boards_html}
                
                <div class="variation-pv-line">
                    <strong>Principal Variation:</strong> {colored_pv[:120]}
                </div>
            </div>
            """
        
        return f"""
        <section class="section enhanced-variation-boards">
            <div class="section-header">
                🎯 Variation Progression Analysis
            </div>
            <p>See how each candidate move develops over time with key position snapshots.</p>
            <div class="variation-progression-container">
                {variations_html}
            </div>
        </section>
        <div class="page-break"></div>
        """

    def _generate_spatial_comparison_section(self, current_fen: str, result_fen: str, best_move: Dict[str, Any]) -> str:
        """Generate spatial analysis comparison between current and result positions."""
        try:
            import spatial_analysis
            turn = chess.Board(current_fen).turn
            flipped = not turn  # Flip if black to move
            
            # Get spatial data for both positions
            current_board = chess.Board(current_fen)
            current_metrics = spatial_analysis.calculate_comprehensive_spatial_metrics(current_board)
            current_spatial = current_metrics.get('space_control', {})
            
            result_spatial = current_spatial  # Default fallback
            if result_fen and result_fen != current_fen:
                try:
                    result_board = chess.Board(result_fen)
                    result_metrics = spatial_analysis.calculate_comprehensive_spatial_metrics(result_board)
                    result_spatial = result_metrics.get('space_control', {})
                except:
                    pass
            
            # Generate comparison HTML
            current_board_html = self.generate_space_control_board_html({'space_control': current_spatial}, size=200)
            result_board_html = self.generate_space_control_board_html({'space_control': result_spatial}, size=200)
            
            colored_best_move = self.convert_to_piece_icons(best_move.get('move', 'N/A'))
            
            # Create spatial comparison table
            spatial_table = f"""
            <table class="spatial-comparison-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Current</th>
                        <th>After Move</th>
                        <th>Change</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="spatial-best-row">
                        <td><strong>White Territory</strong></td>
                        <td>{current_spatial.get('white_space_percentage', 0):.1f}%</td>
                        <td>{result_spatial.get('white_space_percentage', 0):.1f}%</td>
                        <td class="{self.get_advantage_class(result_spatial.get('white_space_percentage', 0) - current_spatial.get('white_space_percentage', 0))}">{result_spatial.get('white_space_percentage', 0) - current_spatial.get('white_space_percentage', 0):+.1f}%</td>
                    </tr>
                    <tr>
                        <td><strong>Black Territory</strong></td>
                        <td>{current_spatial.get('black_space_percentage', 0):.1f}%</td>
                        <td>{result_spatial.get('black_space_percentage', 0):.1f}%</td>
                        <td class="{self.get_advantage_class(current_spatial.get('black_space_percentage', 0) - result_spatial.get('black_space_percentage', 0))}">{result_spatial.get('black_space_percentage', 0) - current_spatial.get('black_space_percentage', 0):+.1f}%</td>
                    </tr>
                    <tr>
                        <td><strong>Contested</strong></td>
                        <td>{current_spatial.get('contested_percentage', 0):.1f}%</td>
                        <td>{result_spatial.get('contested_percentage', 0):.1f}%</td>
                        <td class="change-neutral">{result_spatial.get('contested_percentage', 0) - current_spatial.get('contested_percentage', 0):+.1f}%</td>
                    </tr>
                    <tr>
                        <td><strong>Space Advantage</strong></td>
                        <td>{current_spatial.get('space_advantage', 0):+.0f}</td>
                        <td>{result_spatial.get('space_advantage', 0):+.0f}</td>
                        <td class="{self.get_advantage_class(result_spatial.get('space_advantage', 0) - current_spatial.get('space_advantage', 0))}">{result_spatial.get('space_advantage', 0) - current_spatial.get('space_advantage', 0):+.0f}</td>
                    </tr>
                </tbody>
            </table>
            """
            
            return f"""
            <section class="section spatial-control-comparison">
                <div class="section-header">
                    🗺️ Spatial Control Evolution
                </div>
                <p>How each move reshapes the territorial landscape of the position.</p>
                
                <div class="spatial-comparison-layout">
                    <div>
                        <h3 style="margin-bottom: 20px; color: #4a5568;">Spatial Control Visualization</h3>
                        <div class="spatial-boards-grid">
                            <div class="spatial-comparison-item">
                                <h4>Current Position</h4>
                                {current_board_html}
                            </div>
                            <div class="spatial-comparison-item">
                                <h4>After {colored_best_move}</h4>
                                {result_board_html}
                            </div>
                        </div>
                    </div>
                    
                    <div class="spatial-stats-table">
                        <h3 style="margin-bottom: 20px; color: #4a5568;">Spatial Metrics</h3>
                        {spatial_table}
                    </div>
                </div>
                
                <div class="spatial-insights">
                    <h4>💡 Spatial Analysis Insights</h4>
                    <p>The best move {'improves' if result_spatial.get('space_advantage', 0) > current_spatial.get('space_advantage', 0) else 'maintains' if result_spatial.get('space_advantage', 0) == current_spatial.get('space_advantage', 0) else 'reduces'} 
                    White's space advantage by {abs(result_spatial.get('space_advantage', 0) - current_spatial.get('space_advantage', 0)):.0f} squares. 
                    Territory control shifts of more than 5% indicate significant positional changes.</p>
                </div>
            </section>
            <div class="page-break"></div>
            """
            
        except ImportError:
            colored_best_move = self.convert_to_piece_icons(best_move.get('move', 'N/A'))
            return f"""
            <section class="section spatial-control-comparison">
                <div class="section-header">
                    🗺️ Spatial Control Evolution
                </div>
                <div style="text-align: center; color: #718096; font-style: italic; padding: 3rem; background: #f8f9fa; border-radius: 12px; border: 2px dashed #e2e8f0;">
                    <h4 style="color: #4a5568; margin-bottom: 1rem;">Advanced Spatial Analysis Module</h4>
                    <p style="font-size: 1.1rem; line-height: 1.6;">
                        Enhanced spatial comparison between current position and position after best move: 
                        {colored_best_move}
                    </p>
                    <p style="margin-top: 1rem; color: #4a5568;">
                        <em>Module not currently available - contact administrator for advanced features.</em>
                    </p>
                </div>
            </section>
            <div class="page-break"></div>
            """

    # Continue with all the existing methods but with color-coded notation...
    # [Additional methods would follow the same pattern with color coding applied]
    
    def _extract_move_history(self, position_data: Dict[str, Any]) -> str:
        """Extract and format move history with color-coded notation."""
        move_history = position_data.get('move_history', '')
        if isinstance(move_history, str):
            try:
                history_data = json.loads(move_history)
                pgn = history_data.get('pgn', '')
                pgn = self.convert_to_piece_icons(pgn)
                if pgn:
                    return f"""
                    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; margin-top: 1.5rem; border: 1px solid #e2e8f0;">
                        <h4 style="color: #4a5568; margin-bottom: 1rem;">📜 Game History</h4>
                        <div style="font-family: 'Monaco', 'Menlo', monospace; font-size: 0.9rem; line-height: 1.8; color: #2d3748; background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0;">{pgn}</div>
                    </div>
                    """
            except:
                pass
        return ""

    def _generate_comparative_analysis_section(self, position_data: Dict[str, Any], best_move: Dict[str, Any]) -> str:
        """Generate comprehensive comparative analysis."""
        material_analysis = position_data.get('material_analysis', {})
        mobility_analysis = position_data.get('mobility_analysis', {})
        king_safety = position_data.get('king_safety_analysis', {})
        center_control = position_data.get('center_control_analysis', {})
        pawn_structure = position_data.get('pawn_structure_analysis', {})
        piece_development = position_data.get('piece_development_analysis', {})
        
        # Extract position impact from best move
        position_impact = best_move.get('position_impact', {})
        
        return f"""
        <section class="section">
            <div class="section-header">
                📊 Comprehensive Positional Analysis
            </div>
            
            <h3>Material Balance & Piece Activity</h3>
            <table class="analysis-table">
                <thead>
                    <tr>
                        <th>Aspect</th>
                        <th>White</th>
                        <th>Black</th>
                        <th>Balance</th>
                        <th>After Best Move</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Total Material</strong></td>
                        <td>{material_analysis.get('white_total', 0)}</td>
                        <td>{material_analysis.get('black_total', 0)}</td>
                        <td class="{self.get_advantage_class(material_analysis.get('imbalance_score', 0))}">{material_analysis.get('imbalance_score', 0):.2f}</td>
                        <td class="change-positive">+{position_impact.get('material_change', 0)}</td>
                    </tr>
                    <tr>
                        <td>Pawns</td>
                        <td>{int(material_analysis.get('white_pawns', 0))}</td>
                        <td>{int(material_analysis.get('black_pawns', 0))}</td>
                        <td>{int(material_analysis.get('white_pawns', 0)) - int(material_analysis.get('black_pawns', 0))}</td>
                        <td>—</td>
                    </tr>
                    <tr>
                        <td>Minor Pieces</td>
                        <td>{int(material_analysis.get('white_knights', 0)) + int(material_analysis.get('white_bishops', 0))}</td>
                        <td>{int(material_analysis.get('black_knights', 0)) + int(material_analysis.get('black_bishops', 0))}</td>
                        <td>{(int(material_analysis.get('white_knights', 0)) + int(material_analysis.get('white_bishops', 0))) - (int(material_analysis.get('black_knights', 0)) + int(material_analysis.get('black_bishops', 0)))}</td>
                        <td>—</td>
                    </tr>
                    <tr>
                        <td>Major Pieces</td>
                        <td>{int(material_analysis.get('white_rooks', 0)) + int(material_analysis.get('white_queens', 0))}</td>
                        <td>{int(material_analysis.get('black_rooks', 0)) + int(material_analysis.get('black_queens', 0))}</td>
                        <td>{(int(material_analysis.get('white_rooks', 0)) + int(material_analysis.get('white_queens', 0))) - (int(material_analysis.get('black_rooks', 0)) + int(material_analysis.get('black_queens', 0)))}</td>
                        <td>—</td>
                    </tr>
                </tbody>
            </table>
            
            <h3>Positional Factors</h3>
            <table class="analysis-table">
                <thead>
                    <tr>
                        <th>Factor</th>
                        <th>White</th>
                        <th>Black</th>
                        <th>Advantage</th>
                        <th>Move Impact</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Mobility</strong></td>
                        <td>{int(mobility_analysis.get('white_total', 0))}</td>
                        <td>{int(mobility_analysis.get('black_total', 0))}</td>
                        <td class="{self.get_advantage_class(mobility_analysis.get('white_total', 0) - mobility_analysis.get('black_total', 0))}">{int(mobility_analysis.get('white_total', 0)) - int(mobility_analysis.get('black_total', 0))}</td>
                        <td>{position_impact.get('space_advantage_change', 0):+.1f}</td>
                    </tr>
                    <tr>
                        <td><strong>King Safety</strong></td>
                        <td>{king_safety.get('safety_scores', {}).get('true', 0):.1f}</td>
                        <td>{king_safety.get('safety_scores', {}).get('false', 0):.1f}</td>
                        <td class="{self.get_advantage_class(king_safety.get('safety_scores', {}).get('true', 0) - king_safety.get('safety_scores', {}).get('false', 0))}">{king_safety.get('safety_scores', {}).get('true', 0) - king_safety.get('safety_scores', {}).get('false', 0):+.1f}</td>
                        <td>{position_impact.get('king_safety_impact', 0):+.1f}</td>
                    </tr>
                    <tr>
                        <td><strong>Center Control</strong></td>
                        <td>{center_control.get('white', 0):.0f}</td>
                        <td>{center_control.get('black', 0):.0f}</td>
                        <td class="{self.get_advantage_class(center_control.get('white', 0) - center_control.get('black', 0))}">{center_control.get('white', 0) - center_control.get('black', 0):+.0f}</td>
                        <td>{position_impact.get('center_control_change', 0):+.1f}</td>
                    </tr>
                    <tr>
                        <td><strong>Development</strong></td>
                        <td>{piece_development.get('white', 0):.2f}</td>
                        <td>{piece_development.get('black', 0):.2f}</td>
                        <td class="{self.get_advantage_class(piece_development.get('white', 0) - piece_development.get('black', 0))}">{piece_development.get('white', 0) - piece_development.get('black', 0):+.2f}</td>
                        <td>{position_impact.get('development_impact', 0):+.2f}</td>
                    </tr>
                </tbody>
            </table>
            
            <h3>Pawn Structure Analysis</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Open Files</div>
                    <div class="metric-value">{int(pawn_structure.get('open_files', 0))}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Half-Open Files</div>
                    <div class="metric-value">{int(pawn_structure.get('half_open_files', 0))}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Pawn Islands (W/B)</div>
                    <div class="metric-value">{int(pawn_structure.get('white_pawn_islands', 0))}/{int(pawn_structure.get('black_pawn_islands', 0))}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Passed Pawns (W/B)</div>
                    <div class="metric-value">{int(pawn_structure.get('white_passed_pawns', 0))}/{int(pawn_structure.get('black_passed_pawns', 0))}</div>
                </div>
            </div>
            
        </section>
        <div class="page-break"></div>
        """

    def _generate_top_moves_section(self, top_moves: List[Dict[str, Any]], turn: str, move_number: int) -> str:
        """Generate comprehensive top moves analysis with color-coded notation."""
        if not top_moves:
            return ""
        
        moves_html = ""
        for i, move in enumerate(top_moves[:20]):  # Top 10 moves
            score = move.get('score', 0)
            score_display = self.format_score_display(score)
            score_class = self.get_score_class(score)
            
            classification = move.get('classification', 'unknown')
            classification_class = f"classification-{classification.lower()}"
            
            centipawn_loss = move.get('centipawn_loss', 0)
            loss_class = "change-neutral" if centipawn_loss == 0 else "change-negative"
            
            tactics = move.get('tactics', [])
            tactics_text = ", ".join([t.replace("_", " ").title() for t in tactics[:3]]) if tactics else "—"
            
            pv = move.get('principal_variation', '')
            colored_pv = self.convert_to_piece_icons(pv)
            if len(colored_pv) > 200:  # Approximate HTML length limit
                colored_pv = colored_pv[:200] + "..."
            
            colored_move = self.convert_to_piece_icons(move.get('move', ''))
            
            strategic_value = move.get('strategic_value', 0)
            complexity = move.get('move_complexity', 0)
            
            moves_html += f"""
            <tr>
                <td><strong>#{i+1}</strong></td>
                <td><strong style="font-size: 1.1rem;">{colored_move}</strong></td>
                <td class="{score_class}">{score_display}</td>
                <td class="{loss_class}">{centipawn_loss}</td>
                <td><span class="move-classification {classification_class}">{classification}</span></td>
                <td>{tactics_text}</td>
                <td>{strategic_value}/5</td>
                <td>{complexity}/5</td>
                <td style="font-family: monospace; font-size: 0.85rem; width: 50%;">{colored_pv}</td>
            </tr>
            """
        
        return f"""
        <section class="section">
            <div class="section-header">
                🏆 Top Engine Moves Analysis
            </div>
            <p>Comprehensive analysis of the best moves in this position, ranked by engine evaluation depth and strategic value.</p>
            
            <table class="analysis-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Move</th>
                        <th>Score</th>
                        <th>CP Loss</th>
                        <th>Classification</th>
                        <th>Tactics</th>
                        <th>Strategic</th>
                        <th>Complexity</th>
                        <th>Principal Variation</th>
                    </tr>
                </thead>
                <tbody>
                    {moves_html}
                </tbody>
            </table>
            
            <div style="margin-top: 1.5rem; background: #f0f8f0; padding: 1rem; border-radius: 8px; border-left: 4px solid #48bb78;">
                <h4 style="color: #38a169;">Understanding the Rankings</h4>
                <p style="color: #2d3748; margin-top: 0.5rem;">
                    Moves are ranked by engine evaluation at depth {top_moves[0].get('depth', 0) if top_moves else 'N/A'}. 
                    Strategic value and complexity provide additional context for learning. 
                    Centipawn loss shows how much evaluation drops compared to the best move.
                </p>
            </div>
        </section>
        <div class="page-break"></div>
        """

    # Add all remaining methods here with color coding applied...
    # For brevity, including key helper methods

    def generate_space_control_board_html(self, metrics: Dict[str, Any], size: int = 400) -> str:
        """Generate space control board visualization as HTML with wooden layout and control icons."""
        try:
            space_control = metrics.get('space_control', {})
            control_matrix = space_control.get('control_matrix', [])

            # Validate data
            if not control_matrix or len(control_matrix) != 8:
                return '<p style="text-align: center; color: #718096;">Space control data not available</p>'

            # Define classic wooden board colors
            light_color = '#f0d9b5'
            dark_color = '#b58863'
            
            # Scale size for compact display
            cell_size = max(20, size // 10)

            # Start responsive container
            board_html = (
                f'<div style="overflow-x:auto; margin:0 auto; max-width:100%;">'
                f'<table style="border-collapse: collapse; border: 2px solid #e2e8f0; margin: 0 auto;">'
            )

            # Build board rows
            for rank in range(8):
                board_html += '<tr>'
                for file in range(8):
                    control_value = control_matrix[7 - rank][file]  # Flip for display order

                    # Determine square color
                    is_light = (rank + file) % 2 == 0
                    bg_color = light_color if is_light else dark_color

                    # Determine control icon
                    if control_value == 1:
                        symbol = '⚪'  # White control
                    elif control_value == -1:
                        symbol = '⚫'  # Black control
                    elif control_value == 2:
                        symbol = '🟠'  # Contested
                    else:
                        symbol = '🟢'  # Neutral

                    board_html += (
                        f'<td style="width:{cell_size}px; height:{cell_size}px; background-color:{bg_color}; '  
                        'text-align:center; vertical-align:middle; border:1px solid #d1d5db; '  
                        f'font-size:{cell_size//2}px; line-height:{cell_size}px;">'
                        f'{symbol}'
                        '</td>'
                    )
                board_html += '</tr>'

            board_html += '</table></div>'

            # Legend for control icons
            legend_html = (
                '<div style="display:flex; justify-content:center; gap:20px; margin-top:12px; '  
                'font-size:14px;">'
                '<div><span style="font-size:18px;">⚪</span> White Control</div>'
                '<div><span style="font-size:18px;">⚫</span> Black Control</div>'
                '<div><span style="font-size:18px;">🟠</span> Contested</div>'
                '<div><span style="font-size:18px;">🟢</span> Neutral</div>'
                '</div>'
            )

            # Summary statistics
            summary_html = f'''
            <div style="margin-top:20px; text-align:center;">
            <div style="display:inline-grid; grid-template-columns:repeat(5, auto); gap:20px; text-align:center;">
                <div><div style="font-weight:600; color:#3b82f6;">White Space</div>
                    <div style="font-size:1.2rem;">{space_control.get('white_space_percentage',0):.1f}%</div></div>
                <div><div style="font-weight:600; color:#8b5cf6;">Black Space</div>
                    <div style="font-size:1.2rem;">{space_control.get('black_space_percentage',0):.1f}%</div></div>
                <div><div style="font-weight:600; color:#f59e0b;">Contested</div>
                    <div style="font-size:1.2rem;">{space_control.get('contested_percentage',0):.1f}%</div></div>
                <div><div style="font-weight:600; color:#6b7280;">Neutral</div>
                    <div style="font-size:1.2rem;">{space_control.get('neutral_percentage',0):.1f}%</div></div>
                <div><div style="font-weight:600; color:#10b981;">Advantage</div>
                    <div style="font-size:1.2rem;">{space_control.get('space_advantage',0):+.1f}</div></div>
            </div>
            </div>
            '''

            return board_html + legend_html + summary_html
            
        except Exception as e:
            return f'<p style="text-align: center; color: #ef4444;">Error generating space control: {str(e)}</p>'

    # Include all remaining helper methods...
    def _generate_list_items(self, items: List[str]) -> str:
        """Generate HTML list items from a list of strings."""
        if not items:
            return "<li style='color: #718096; font-style: italic;'>No specific guidance available for this level.</li>"
        return "".join([f"<li>{item}</li>" for item in items])

    def _generate_theme_tags(self, themes: List[str]) -> str:
        """Generate theme tags HTML."""
        if not themes:
            return '<span class="theme-tag" style="background: #f0f0f0; color: #718096;">None identified</span>'
        return "".join([f'<span class="theme-tag">{theme.replace("_", " ").title()}</span>' for theme in themes])

    def _generate_comprehensive_strategic_insights_section(self, position_data: Dict[str, Any], selected_move_data: Dict[str, Any]) -> str:
        """Generate comprehensive insights and strategic section."""
        comprehensive_analysis = position_data.get('comprehensive_analysis', {})
        
        # Strategic themes and tactical motifs
        strategic_themes = comprehensive_analysis.get('strategic_themes', [])
        tactical_motifs = comprehensive_analysis.get('tactical_motifs', [])
        critical_squares = comprehensive_analysis.get('critical_squares', [])
        
        return f"""
        <section class="section">
            <div class="section-header">
                💡 Strategic Insights & Tactical Themes
            </div>

            <div style="margin: 2rem 0;">
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid #e2e8f0;">
                    <h4 style="color: #4299e1; margin-bottom: 0.5rem;">📈 Strategic Themes</h4>
                    <div>
                        {self._generate_theme_tags(strategic_themes)}
                    </div>
                </div>
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid #e2e8f0;">
                    <h4 style="color: #ed8936; margin-bottom: 0.5rem;">⚡ Tactical Motifs</h4>
                    <div>
                        {self._generate_theme_tags(tactical_motifs)}
                    </div>
                </div>
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0;">
                    <h4 style="color: #805ad5; margin-bottom: 0.5rem;">🎯 Critical Squares</h4>
                    <div style="font-family: 'Monaco', 'Menlo', monospace; font-size: 1.1rem; font-weight: 600; color: #2d3748;">
                        {", ".join(critical_squares) if critical_squares else "None identified"}
                    </div>
                </div>
            </div>
            
        </section>
        <div class="page-break"></div>
        """

    def _generate_comprehensive_learning_insights_section(self, position_data: Dict[str, Any], selected_move_data: Dict[str, Any]) -> str:
        """Generate comprehensive insights and learning section."""
        learning_insights = position_data.get('learning_insights', {})
        
        # Extract insights by skill level
        beginner = learning_insights.get('beginner', {})
        intermediate = learning_insights.get('intermediate', {})
        advanced = learning_insights.get('advanced', {})
        universal = learning_insights.get('universal', {})
        
        return f"""
        <section class="section">
            <div class="section-header">
                💡 Strategic Insights & Learning
            </div>
            
            <h3>Position Assessment</h3>
            <div style="background: linear-gradient(135deg, #e8f5e8, #c6f6d5); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; border-left: 5px solid #48bb78;">
                <p style="font-size: 1.1rem; line-height: 1.6; color: #2d3748;">
                    <strong>🔍 Engine Assessment:</strong> {universal.get('position_assessment', 'This is a complex position requiring careful analysis.')}
                </p>
            </div>
            
            <h3>Best Move Reasoning</h3>
            <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; border-left: 5px solid #4299e1;">
                <p style="font-size: 1.1rem; line-height: 1.6; color: #2d3748;">
                    <strong>🎯 Why this move:</strong> {universal.get('best_move_reasoning', 'The engine recommends this move based on tactical and positional considerations.')}
                </p>
            </div>
            
            <div class="insights-grid">
                <div class="insight-card">
                    <h4>🎓 For Beginners</h4>
                    <h5>Key Concepts</h5>
                    <ul>
                        {self._generate_list_items(beginner.get('key_concepts', []))}
                    </ul>
                    <h5>Development Tips</h5>
                    <ul>
                        {self._generate_list_items(beginner.get('development_tips', []))}
                    </ul>
                    <h5>Tactical Patterns</h5>
                    <ul>
                        {self._generate_list_items(beginner.get('tactical_patterns', [[]])[0] if beginner.get('tactical_patterns') else [])}
                    </ul>
                </div>
                
                <div class="insight-card">
                    <h4>📚 For Intermediate Players</h4>
                    <h5>Positional Concepts</h5>
                    <ul>
                        {self._generate_list_items(intermediate.get('positional_concepts', []))}
                    </ul>
                    <h5>Strategic Plans</h5>
                    <ul>
                        {self._generate_list_items(intermediate.get('strategic_plans', []))}
                    </ul>
                    <h5>Calculation Exercises</h5>
                    <ul>
                        {self._generate_list_items(intermediate.get('calculation_exercises', []))}
                    </ul>
                    <h5>Pattern Recognition</h5>
                    <ul>
                        {self._generate_list_items(intermediate.get('pattern_recognition', []))}
                    </ul>
                </div>
                
                <div class="insight-card">
                    <h4>🏆 For Advanced Players</h4>
                    <h5>Deep Strategy</h5>
                    <ul>
                        {self._generate_list_items(advanced.get('deep_strategy', []))}
                    </ul>
                    <h5>Subtle Tactics</h5>
                    <ul>
                        {self._generate_list_items(advanced.get('subtle_tactics', []))}
                    </ul>
                    <h5>Psychological Factors</h5>
                    <ul>
                        {self._generate_list_items(advanced.get('psychological_factors', []))}
                    </ul>
                    <h5>Endgame Theory</h5>
                    <ul>
                        {self._generate_list_items(advanced.get('endgame_theory', []))}
                    </ul>
                </div>
            </div>
            <div style="background: linear-gradient(135deg, #fff5f5, #fed7d7); padding: 1.5rem; border-radius: 12px; border-left: 5px solid #e53e3e;">
                <h3 style="color: #e53e3e;">⚠️ Common Mistakes to Avoid</h3>
                <ul>
                    {self._generate_list_items(universal.get('common_mistakes', ['Moving without a plan', 'Ignoring opponent threats', 'Poor time management']))}
                </ul>
            </div>
            
            <div style="background: linear-gradient(135deg, #f0fff4, #c6f6d5); padding: 1.5rem; border-radius: 12px; border-left: 5px solid #48bb78; margin-top: 1.5rem;">
                <h3 style="color: #48bb78;">🚀 Areas for Improvement</h3>
                <ul>
                    {self._generate_list_items(universal.get('improvement_areas', ['Pattern recognition', 'Calculation accuracy', 'Positional understanding']))}
                </ul>
            </div>
            
        </section>
        <div class="page-break"></div>
        """

