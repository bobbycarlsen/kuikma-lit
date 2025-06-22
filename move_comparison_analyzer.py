# move_comparison_analyzer.py - Comprehensive Move Comparison Analysis Engine
import os
import json
import chess
import chess.svg
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class MoveComparisonAnalyzer:
    """
    Advanced move comparison analyzer that provides comprehensive analysis
    of why the engine's best move is superior to alternatives.
    """
    
    def __init__(self, html_generator):
        """Initialize with reference to the main HTML generator for utility access."""
        self.html_generator = html_generator

    def generate_comprehensive_move_comparison_section(self, position_data: Dict[str, Any]) -> str:
        """Generate the complete move comparison analysis section."""
        fen = position_data.get('fen', '')
        top_moves = position_data.get('top_moves', [])
        
        if not top_moves:
            return ""
        
        # Generate all sections with updated designs
        foundation_section = self._generate_foundation_section(position_data)
        executive_summary = self._generate_executive_summary(position_data)
        move_comparison_matrix = self._generate_move_comparison_matrix(position_data)
        board_visualizations = self._generate_board_visualizations_comparison(position_data)
        enhanced_variation_boards = self._generate_enhanced_variation_boards(position_data)
        spatial_comparison = self._generate_spatial_control_comparison(position_data)
        position_impact_analysis = self._generate_position_impact_radar(position_data)
        tactical_opportunity_analysis = self._generate_tactical_opportunity_analysis(position_data)
        risk_reward_assessment = self._generate_risk_reward_assessment(position_data)
        strategic_consequence_mapping = self._generate_strategic_consequence_mapping(position_data)
        
        return f"""
        <section class="section move-comparison-mega-section">
            <div class="section-header">
                🔬 Comprehensive Move Analysis: Why The Engine's Choice Dominates
            </div>
            <div class="move-comparison-container">
                {foundation_section}
                {executive_summary}
                {move_comparison_matrix}
                {board_visualizations}
                {enhanced_variation_boards}
                {spatial_comparison}
                {position_impact_analysis}
                {tactical_opportunity_analysis}
                {risk_reward_assessment}
                {strategic_consequence_mapping}
            </div>
        </section>
        <div class="page-break"></div>
        """
    
    def _generate_foundation_section(self, position_data: Dict[str, Any]) -> str:
        """Generate the foundational context section."""
        fen = position_data.get('fen', '')
        turn = position_data.get('turn', 'white')
        move_number = position_data.get('fullmove_number', 1)
        themes = position_data.get('themes', [])
        description = position_data.get('description', '')
        
        # Generate current position board with proper orientation
        flipped = (turn.lower() == 'black')
        board_svg = self.html_generator.generate_chess_board_svg(fen, flipped=flipped, size=400)
        
        # Extract key position metrics
        material_analysis = position_data.get('material_analysis', {})
        center_control = position_data.get('center_control_analysis', {})
        king_safety = position_data.get('king_safety_analysis', {}).get('safety_scores', {})
        
        position_assessment = f"""
        <div class="position-metrics-grid">
            <div class="metric-highlight">
                <div class="metric-label">Material Balance</div>
                <div class="metric-value">{material_analysis.get('imbalance_score', 0):+.2f}</div>
            </div>
            <div class="metric-highlight">
                <div class="metric-label">Center Control</div>
                <div class="metric-value">{center_control.get('white', 0) - center_control.get('black', 0):+.0f}</div>
            </div>
            <div class="metric-highlight">
                <div class="metric-label">King Safety</div>
                <div class="metric-value">{king_safety.get('true', 0) - king_safety.get('false', 0):+.1f}</div>
            </div>
            <div class="metric-highlight">
                <div class="metric-label">Game Phase</div>
                <div class="metric-value">{position_data.get('game_phase', 'Unknown').title()}</div>
            </div>
        </div>
        """
        # temporary fix for I C A N K
        themes = sorted(themes, key=len, reverse=True)
        themes_display = ''.join([
            f'<span class="theme-tag-foundation">{theme.replace("_", " ").title()}</span>' 
            for theme in themes[:8]
        ])
        
        return f"""
        <div class="foundation-section">
            <h3>📋 Position Foundation</h3>
            <div class="foundation-grid">
                <div class="foundation-board">
                    <h4>Current Position - Move {move_number}</h4>
                    {board_svg}
                    <p class="position-description">{description}</p>
                </div>
                <div class="foundation-metrics">
                    <h4>Key Position Metrics</h4>
                    {position_assessment}
                    
                    <h4>Position Themes</h4>
                    <div class="themes-container">
                        {themes_display}
                    </div>
                    
                    <div class="position-context">
                        <h4>Analysis Context</h4>
                        <p><strong>Engine Depth:</strong> {position_data.get('engine_depth', 0)} plies</p>
                        <p><strong>Difficulty Rating:</strong> {position_data.get('difficulty_rating', 0)}</p>
                        <p><strong>Turn to Move:</strong> {turn.title()}</p>
                        <p><strong>Position Type:</strong> {position_data.get('position_type', 'Unknown').title()}</p>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_executive_summary(self, position_data: Dict[str, Any]) -> str:
        """Generate executive summary of why the best move is superior."""
        top_moves = position_data.get('top_moves', [])
        if not top_moves:
            return ""
        
        best_move = top_moves[0]
        best_move_notation = self.html_generator.convert_to_piece_icons(best_move.get('move', ''))
        best_score = self.html_generator.format_score_display(best_move.get('score'))
        best_tactics = best_move.get('tactics', [])
        
        # Calculate key differentials
        move_comparisons = []
        for i, move in enumerate(top_moves[1:6], 1):  # Compare top 5 alternatives
            cp_loss = move.get('centipawn_loss', 0)
            classification = move.get('classification', 'unknown')
            move_notation = self.html_generator.convert_to_piece_icons(move.get('move', ''))
            move_comparisons.append({
                'rank': i + 1,
                'move': move_notation,
                'cp_loss': cp_loss,
                'classification': classification
            })
        
        comparison_rows = ""
        for comp in move_comparisons:
            comparison_rows += f"""
            <tr>
                <td>#{comp['rank']}</td>
                <td><strong>{comp['move']}</strong></td>
                <td class="cp-loss-value">-{comp['cp_loss']}</td>
                <td><span class="classification-{comp['classification'].lower()}">{comp['classification'].title()}</span></td>
            </tr>
            """
        
        tactical_elements = ", ".join([t.replace("_", " ").title() for t in best_tactics]) if best_tactics else "Positional play"
        
        return f"""
        <div class="executive-summary">
            <h3>🎯 Executive Summary: The Engine's Verdict</h3>
            <div class="summary-grid">
                <div class="best-move-highlight">
                    <h4>Engine's Choice</h4>
                    <div class="best-move-display">
                        <div class="move-notation">{best_move_notation}</div>
                        <div class="move-evaluation">Evaluation: {best_score}</div>
                        <div class="move-classification">Classification: {best_move.get('classification', 'unknown').title()}</div>
                    </div>
                    <p><strong>Key Elements:</strong> {tactical_elements}</p>
                </div>
                
                <div class="alternatives-comparison">
                    <h4>Why Not The Alternatives?</h4>
                    <table class="alternatives-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Move</th>
                                <th>CP Loss</th>
                                <th>Quality</th>
                            </tr>
                        </thead>
                        <tbody>
                            {comparison_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="summary-insight">
                <h4>💡 Key Insight</h4>
                <p>The engine's choice stands out due to its superior {tactical_elements.lower()} while maintaining optimal evaluation. 
                Alternative moves suffer from centipawn losses ranging from {move_comparisons[0]['cp_loss'] if move_comparisons else 0} to {move_comparisons[-1]['cp_loss'] if move_comparisons else 0} points, 
                indicating measurable positional or tactical concessions.</p>
            </div>
        </div>
        """
    
    def _generate_move_comparison_matrix(self, position_data: Dict[str, Any]) -> str:
        """Generate comprehensive comparison matrix of all top moves."""
        top_moves = position_data.get('top_moves', [])
        if not top_moves:
            return ""
        
        matrix_rows = ""
        for i, move in enumerate(top_moves):
            move_notation = self.html_generator.convert_to_piece_icons(move.get('move', ''))
            score = self.html_generator.format_score_display(move.get('score'))
            score_class = self.html_generator.get_score_class(move.get('score'))
            cp_loss = move.get('centipawn_loss', 0)
            classification = move.get('classification', 'unknown')
            tactics = move.get('tactics', [])
            tactics_display = ", ".join([t.replace("_", " ").title() for t in tactics[:2]]) if tactics else "—"
            
            # Position impact metrics
            impact = move.get('position_impact', {})
            material_change = impact.get('material_change', 0)
            king_safety = impact.get('king_safety_impact', 0)
            center_control = impact.get('center_control_change', 0)
            initiative = impact.get('initiative_change', 0)
            
            complexity = move.get('move_complexity', 0)
            strategic_value = move.get('strategic_value', 0)
            
            # Color coding for best move
            row_class = "best-move-row" if i == 0 else ""
            
            matrix_rows += f"""
            <tr class="{row_class}">
                <td><strong>#{i+1}</strong></td>
                <td class="move-cell"><strong>{move_notation}</strong></td>
                <td class="{score_class}">{score}</td>
                <td class="cp-loss-cell">{cp_loss}</td>
                <td><span class="classification-{classification.lower()}">{classification}</span></td>
                <td class="tactics-cell">{tactics_display}</td>
                <td class="{self.html_generator.get_advantage_class(material_change)}">{material_change:+d}</td>
                <td class="{self.html_generator.get_advantage_class(king_safety)}">{king_safety:+.1f}</td>
                <td class="{self.html_generator.get_advantage_class(center_control)}">{center_control:+.0f}</td>
                <td class="{self.html_generator.get_advantage_class(initiative)}">{initiative:+.1f}</td>
                <td>{complexity}/5</td>
                <td>{strategic_value}/5</td>
            </tr>
            """
        
        return f"""
        <div class="move-comparison-matrix">
            <h3>📊 Complete Move Comparison Matrix</h3>
            <p>Comprehensive comparison of all engine-considered moves with key performance indicators.</p>
            
            <div class="matrix-container">
                <table class="comparison-matrix-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Move</th>
                            <th>Score</th>
                            <th>CP Loss</th>
                            <th>Quality</th>
                            <th>Tactics</th>
                            <th>Material</th>
                            <th>King Safety</th>
                            <th>Center</th>
                            <th>Initiative</th>
                            <th>Complexity</th>
                            <th>Strategic</th>
                        </tr>
                    </thead>
                    <tbody>
                        {matrix_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="matrix-legend">
                <h4>📖 Reading the Matrix</h4>
                <div class="legend-grid">
                    <div><strong>CP Loss:</strong> Centipawn disadvantage vs best move</div>
                    <div><strong>Material:</strong> Immediate material gain/loss</div>
                    <div><strong>King Safety:</strong> Impact on king security</div>
                    <div><strong>Center:</strong> Central square control change</div>
                    <div><strong>Initiative:</strong> Tempo and pressure dynamics</div>
                    <div><strong>Complexity:</strong> Move difficulty (1-5)</div>
                    <div><strong>Strategic:</strong> Long-term value (1-5)</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_board_visualizations_comparison(self, position_data: Dict[str, Any]) -> str:
        """Generate side-by-side board comparisons for top moves with COMPACT DESIGN."""
        fen = position_data.get('fen', '')
        top_moves = position_data.get('top_moves', [])[:6]  # Top 6 moves
        turn = position_data.get('turn', 'white')
        flipped = (turn.lower() == 'black')
        
        if not top_moves:
            return ""
        
        board_grid = ""
        for i, move in enumerate(top_moves):
            move_notation = self.html_generator.convert_to_piece_icons(move.get('move', ''))
            score = self.html_generator.format_score_display(move.get('score'))
            cp_loss = move.get('centipawn_loss', 0)
            classification = move.get('classification', 'unknown')
            
            # Generate resulting board with SMALLER SIZE for cards
            result_board_svg = self.html_generator.generate_result_board_svg(
                fen, move.get('uci', ''), flipped, size=250  # Reduced from default 400
            )
            
            # Special styling for best move
            card_class = "best-move-card" if i == 0 else "alternative-move-card"
            
            board_grid += f"""
            <div class="{card_class}">
                <div class="move-card-header">
                    <h4>#{i+1} - {move_notation}</h4>
                    <div class="move-metadata">
                        <span class="score-badge {self.html_generator.get_score_class(move.get('score'))}">{score}</span>
                        <span class="cp-badge">CP: -{cp_loss}</span>
                        <span class="classification-badge classification-{classification.lower()}">{classification}</span>
                    </div>
                </div>
                <div class="move-board-container">
                    {result_board_svg}
                </div>
                <div class="move-card-insights">
                    {self._generate_move_specific_insights(move)}
                </div>
            </div>
            """
        
        return f"""
        <div class="board-visualizations-comparison">
            <h3>♟️ Position Outcomes Comparison</h3>
            <p>Visual comparison of resulting positions after each candidate move.</p>
            
            <div class="board-comparison-grid">
                {board_grid}
            </div>
            
            <div class="visualization-notes">
                <h4>🎨 Visualization Guide</h4>
                <p><span style="color: #ff6b6b;">🔴 Red squares</span> show move origin • 
                <span style="color: #51cf66;">🟢 Green squares</span> show move destination • 
                <strong>Gold border</strong> indicates engine's top choice</p>
            </div>
        </div>
        """
    
    def _generate_enhanced_variation_boards(self, position_data: Dict[str, Any]) -> str:
        """Generate enhanced board visualizations for all major variations."""
        fen = position_data.get('fen', '')
        top_moves = position_data.get('top_moves', [])[:20]  # Top 20 moves
        turn = position_data.get('turn', 'white')
        flipped = (turn.lower() == 'black')
        
        if not top_moves:
            return ""
        
        variation_sets = ""
        for i, move in enumerate(top_moves):
            move_notation = self.html_generator.convert_to_piece_icons(move.get('move', ''))
            uci_move = move.get('uci', '')
            pv = move.get('principal_variation', '')
            
            # Parse principal variation to get multiple positions
            try:
                positions, final_fen = self.html_generator.parse_principal_variation(pv, fen, max_moves=20)
                
                # Generate boards in ONE ROW with proper orientation
                boards_row = f"""
                <div class="variation-boards-row">
                """
                
                for pos_idx, pos_fen in enumerate(positions):  # Max 8 positions per row
                    board_svg = self.html_generator.generate_chess_board_svg(
                        pos_fen, flipped=flipped, size=150  # Compact size
                    )
                    move_label = f"Start" if pos_idx == 0 else f"Move {pos_idx}"
                    
                    boards_row += f"""
                    <div class="variation-board-item">
                        <div class="variation-board-label">{move_label}</div>
                        {board_svg}
                    </div>
                    """
                
                boards_row += "</div>"
                
                # Get variation-specific data
                classification = move.get('classification', 'unknown')
                cp_loss = move.get('centipawn_loss', 0)
                score = self.html_generator.format_score_display(move.get('score'))
                
                card_class = "variation-move-set best-variation" if i == 0 else "variation-move-set"
                header_class = "variation-set-header best-header" if i == 0 else "variation-set-header"
                
                variation_sets += f"""
                <div class="{card_class}">
                    <div class="{header_class}">
                        <div class="variation-set-title">#{i+1} - {move_notation}</div>
                        <div class="variation-set-meta">
                            <span class="score-indicator {self.html_generator.get_score_class(move.get('score'))}">{score}</span>
                            <span class="cp-indicator">CP: -{cp_loss}</span>
                            <span class="class-indicator {classification.lower()}">{classification}</span>
                        </div>
                    </div>
                    {boards_row}
                    <div class="variation-pv-line">
                        <strong>Key Line:</strong> {self.html_generator.convert_to_piece_icons(pv)}
                    </div>
                </div>
                """
            except:
                # Fallback for single board
                result_board = self.html_generator.generate_result_board_svg(fen, uci_move, flipped, size=200)
                variation_sets += f"""
                <div class="variation-move-set">
                    <div class="variation-set-header">
                        <div class="variation-set-title">#{i+1} - {move_notation}</div>
                    </div>
                    <div class="variation-boards-row">
                        <div class="variation-board-item">
                            {result_board}
                        </div>
                    </div>
                </div>
                """
        
        return f"""
        <div class="enhanced-variation-boards">
            <h3>🎯 Variation Progression Analysis</h3>
            <p>See how each candidate move develops over time with key position snapshots.</p>
            <div class="variation-progression-container">
                {variation_sets}
            </div>
        </div>
        """
    
    def _generate_spatial_control_comparison(self, position_data: Dict[str, Any]) -> str:
        """Generate REDESIGNED spatial control comparison with tabular stats."""
        fen = position_data.get('fen', '')
        top_moves = position_data.get('top_moves', [])[:5]  # Top 5 moves
        turn = position_data.get('turn', 'white')
        flipped = (turn.lower() == 'black')
        
        if not top_moves:
            return ""
        
        spatial_data = []
        spatial_boards = ""
        
        for i, move in enumerate(top_moves):
            move_notation = self.html_generator.convert_to_piece_icons(move.get('move', ''))
            cp_loss = move.get('centipawn_loss', 0)
            
            # Calculate resulting position after move
            try:
                board = chess.Board(fen)
                uci_move = move.get('uci', '')
                chess_move = chess.Move.from_uci(uci_move)
                if chess_move in board.legal_moves:
                    board.push(chess_move)
                    result_fen = board.fen()
                    
                    # Generate spatial control analysis (if spatial_analysis module available)
                    spatial_board_html = self._generate_spatial_board_for_position(
                        result_fen, move_notation, size=180  # SMALLER SIZE
                    )
                    
                    # Try to get spatial metrics for tabular comparison
                    try:
                        import spatial_analysis
                        result_board = chess.Board(result_fen)
                        metrics = spatial_analysis.calculate_comprehensive_spatial_metrics(result_board)
                        space_control = metrics.get('space_control', {})
                        spatial_data.append({
                            'rank': i + 1,
                            'move': move_notation,
                            'cp_loss': cp_loss,
                            'white_space': space_control.get('white_space_percentage', 0),
                            'black_space': space_control.get('black_space_percentage', 0),
                            'contested': space_control.get('contested_percentage', 0),
                            'advantage': space_control.get('space_advantage', 0)
                        })
                    except ImportError:
                        spatial_data.append({
                            'rank': i + 1,
                            'move': move_notation,
                            'cp_loss': cp_loss,
                            'white_space': 0,
                            'black_space': 0,
                            'contested': 0,
                            'advantage': 0
                        })
                    
                    spatial_boards += f"""
                    <div class="spatial-comparison-item">
                        <h4>#{i+1} - {move_notation} 
                            <span class="cp-indicator">(CP Loss: {cp_loss})</span>
                        </h4>
                        {spatial_board_html}
                    </div>
                    """
            except:
                spatial_boards += f"""
                <div class="spatial-comparison-item">
                    <h4>#{i+1} - {move_notation}</h4>
                    <p style="text-align: center; color: #718096;">Spatial analysis unavailable</p>
                </div>
                """
                spatial_data.append({
                    'rank': i + 1,
                    'move': move_notation,
                    'cp_loss': cp_loss,
                    'white_space': 0,
                    'black_space': 0,
                    'contested': 0,
                    'advantage': 0
                })
        
        # Generate comparison table
        table_rows = ""
        for data in spatial_data:
            row_class = "spatial-best-row" if data['rank'] == 1 else ""
            table_rows += f"""
            <tr class="{row_class}">
                <td>#{data['rank']}</td>
                <td><strong>{data['move']}</strong></td>
                <td>{data['cp_loss']}</td>
                <td>{data['white_space']:.1f}%</td>
                <td>{data['black_space']:.1f}%</td>
                <td>{data['contested']:.1f}%</td>
                <td class="{self.html_generator.get_advantage_class(data['advantage'])}">{data['advantage']:+.0f}</td>
            </tr>
            """
        
        return f"""
        <div class="spatial-control-comparison">
            <h3>🗺️ Spatial Control Evolution</h3>
            <p>How each move reshapes the territorial landscape of the position.</p>
            
            <div class="spatial-comparison-layout">
                <div>
                    <h4>Spatial Control Visualization</h4>
                    <div class="spatial-boards-grid">
                        {spatial_boards}
                    </div>
                </div>
                
                <div class="spatial-stats-table">
                    <h4>Spatial Metrics Comparison</h4>
                    <table class="spatial-comparison-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Move</th>
                                <th>CP Loss</th>
                                <th>White %</th>
                                <th>Black %</th>
                                <th>Contested %</th>
                                <th>Advantage</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="spatial-insights">
                <h4>🔍 Spatial Analysis Insights</h4>
                <p>Spatial control directly correlates with piece mobility, strategic options, and long-term winning chances. 
                The best move typically optimizes space utilization while restricting opponent possibilities.</p>
            </div>
        </div>
        """
    
    def _generate_position_impact_radar(self, position_data: Dict[str, Any]) -> str:
        """Generate FIXED radar chart comparison of position impacts."""
        top_moves = position_data.get('top_moves', [])[:5]  # Top 5 moves
        
        if not top_moves:
            return ""
        
        # Prepare data for radar visualization
        radar_data = []
        impact_categories = [
            'material_change', 'king_safety_impact', 'center_control_change', 
            'development_impact', 'space_advantage_change', 'initiative_change'
        ]
        
        for i, move in enumerate(top_moves):
            move_notation = self.html_generator.convert_to_piece_icons(move.get('move', ''))
            impact = move.get('position_impact', {})
            
            # Normalize values for radar display (-2 to +2 scale)
            normalized_values = []
            for category in impact_categories:
                value = impact.get(category, 0)
                # Simple normalization - could be made more sophisticated
                normalized_value = max(-2, min(2, value))
                normalized_values.append(normalized_value)
            
            radar_data.append({
                'move': move_notation,
                'rank': i + 1,
                'values': normalized_values,
                'cp_loss': move.get('centipawn_loss', 0)
            })
        
        # Generate radar chart using SVG (simplified version)
        radar_svg = self._generate_radar_chart_svg(radar_data, impact_categories)
        
        # Generate FIXED detailed breakdown table
        breakdown_rows = ""
        for data in radar_data:
            values_display = " | ".join([f"{val:+.1f}" for val in data['values']])
            row_class = "radar-best-move" if data['rank'] == 1 else ""
            breakdown_rows += f"""
            <tr class="{row_class}">
                <td>#{data['rank']}</td>
                <td><strong>{data['move']}</strong></td>
                <td>{data['cp_loss']}</td>
                <td class="values-cell">{values_display}</td>
            </tr>
            """
        
        categories_display = " | ".join([cat.replace('_', ' ').title()[:8] for cat in impact_categories])
        
        return f"""
        <div class="position-impact-radar">
            <h3>📡 Multi-Dimensional Impact Analysis</h3>
            <p>Radar analysis of how each move affects different positional factors.</p>
            
            <div class="radar-container">
                <div class="radar-chart">
                    {radar_svg}
                </div>
                <div class="radar-breakdown">
                    <h4>Detailed Breakdown</h4>
                    <table class="radar-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Move</th>
                                <th>CP Loss</th>
                                <th>Impact Values</th>
                            </tr>
                        </thead>
                        <tbody>
                            {breakdown_rows}
                        </tbody>
                    </table>
                    <p class="radar-legend"><strong>Categories:</strong> {categories_display}</p>
                </div>
            </div>
            
            <div class="radar-insights">
                <h4>🎯 Multi-Dimensional Insights</h4>
                <p>The best move typically shows balanced or superior performance across multiple dimensions. 
                Large negative values in any category often indicate serious positional concessions.</p>
            </div>
        </div>
        """
    
    def _generate_strategic_consequence_mapping(self, position_data: Dict[str, Any]) -> str:
        """Generate strategic consequence analysis WITH FINAL POSITIONS for top moves."""
        top_moves = position_data.get('top_moves', [])[:5]
        variation_analysis = position_data.get('variation_analysis', {}).get('variations', [])
        fen = position_data.get('fen', '')
        turn = position_data.get('turn', 'white')
        flipped = (turn.lower() == 'black')
        
        if not top_moves:
            return ""
        
        consequence_analysis = ""
        for i, move in enumerate(top_moves):
            move_notation = self.html_generator.convert_to_piece_icons(move.get('move', ''))
            pv = move.get('principal_variation', '')
            colored_pv = self.html_generator.convert_to_piece_icons(pv)
            
            # Get corresponding variation analysis if available
            variation_data = None
            if i < len(variation_analysis):
                variation_data = variation_analysis[i]
            
            # Strategic assessment
            strategic_themes = []
            if variation_data:
                final_stats = variation_data.get('comprehensive_final_stats', {})
                strategic_assessment = final_stats.get('strategic_assessment', {})
                strategic_themes = strategic_assessment.get('primary_themes', [])
                winning_chances = strategic_assessment.get('winning_chances', 'unknown')
                position_type = strategic_assessment.get('position_type', 'unknown')
            else:
                strategic_themes = ["Analysis pending"]
                winning_chances = "unknown"
                position_type = "unknown"
            
            themes_display = ", ".join([theme.replace("_", " ").title() for theme in strategic_themes[:3]])
            
            # Generate FINAL POSITION after all available moves in the variation
            final_position_board = ""
            try:
                positions, final_fen = self.html_generator.parse_principal_variation(pv, fen, max_moves=10)
                if final_fen:
                    final_board_svg = self.html_generator.generate_chess_board_svg(
                        final_fen, flipped=flipped, size=180
                    )
                    final_position_board = f"""
                    <div class="final-position-board">
                        <div class="final-position-label">Final Position</div>
                        {final_board_svg}
                    </div>
                    """
            except:
                final_position_board = f"""
                <div class="final-position-board">
                    <div class="final-position-label">Final Position</div>
                    <p style="text-align: center; color: #718096; font-style: italic;">Position unavailable</p>
                </div>
                """
            
            consequence_analysis += f"""
            <div class="strategic-consequence-item">
                <div class="consequence-header">
                    <h4>#{i+1} - {move_notation}</h4>
                    <div class="consequence-metadata">
                        <span class="cp-indicator">CP Loss: {move.get('centipawn_loss', 0)}</span>
                        <span class="classification-indicator {move.get('classification', 'unknown').lower()}">{move.get('classification', 'unknown').title()}</span>
                    </div>
                </div>
                
                <div class="consequence-layout">
                    <div>
                        <div class="consequence-details">
                            <div class="strategic-themes">
                                <strong>Strategic Themes:</strong> {themes_display}
                            </div>
                            <div class="position-outcome">
                                <strong>Position Type:</strong> {position_type.replace('_', ' ').title()}
                            </div>
                            <div class="winning-assessment">
                                <strong>Winning Chances:</strong> {winning_chances.replace('_', ' ').title()}
                            </div>
                        </div>
                    </div>
                    
                    {final_position_board}
                </div>
                
                <div class="principal-variation">
                    <strong>Key Continuation:</strong>
                    <div class="pv-display">{colored_pv[:120]}</div>
                </div>
            </div>
            """
        
        return f"""
        <div class="strategic-consequence-mapping">
            <h3>🎭 Strategic Consequence Analysis</h3>
            <p>Long-term strategic implications and final positions for each candidate move.</p>
            
            <div class="consequence-mapping-container">
                {consequence_analysis}
            </div>
            
            <div class="consequence-insights">
                <h4>🔮 Strategic Insights</h4>
                <p>The engine's choice not only optimizes immediate evaluation but also leads to strategically 
                favorable position types with better long-term winning prospects. Alternative moves often lead 
                to inferior strategic themes or reduced winning chances despite appearing reasonable tactically.</p>
            </div>
        </div>
        """
    
    def _generate_spatial_board_for_position(self, fen: str, move_notation: str, size: int = 200) -> str:
        """Generate spatial control board for a specific position with PROPER ORIENTATION."""
        try:
            # Try to use spatial analysis if available
            import spatial_analysis
            board = chess.Board(fen)
            flipped = not board.turn  # Flip based on turn
            metrics = spatial_analysis.calculate_comprehensive_spatial_metrics(board)
            return self.html_generator.generate_space_control_board_html(metrics, size=size)
        except ImportError:
            # Enhanced fallback - create a detailed board with move highlighting
            try:
                board = chess.Board(fen)
                flipped = not board.turn  # Flip based on turn
                
                # Generate board with better positioning info
                board_svg = self.html_generator.generate_chess_board_svg(fen, flipped=flipped, size=size)
                
                # Add position evaluation context
                try:
                    material_count = len([p for p in board.piece_map().values()])
                    piece_activity = sum(len(list(board.attacks(square))) for square in board.piece_map())
                    
                    metrics_html = f"""
                    <div style="background: #f8f9fa; padding: 0.5rem; border-radius: 4px; margin-top: 0.5rem; font-size: 0.8rem;">
                        <div><strong>Pieces:</strong> {material_count}</div>
                        <div><strong>Activity:</strong> {piece_activity}</div>
                        <div><strong>Turn:</strong> {'White' if board.turn else 'Black'}</div>
                    </div>
                    """
                except:
                    metrics_html = ""
                
                return f"""
                <div style="text-align: center;">
                    {board_svg}
                    <p style="color: #718096; font-weight: 600; margin-top: 0.5rem; font-size: 0.9rem;">
                        After {move_notation}
                    </p>
                    {metrics_html}
                </div>
                """
            except:
                # Ultimate fallback
                return f"""
                <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 8px; border: 2px dashed #e2e8f0;">
                    <p style="color: #718096; font-style: italic;">
                        Position analysis for {move_notation}<br>
                        <small>Board visualization temporarily unavailable</small>
                    </p>
                </div>
                """
    
    def _generate_move_specific_insights(self, move: Dict[str, Any]) -> str:
        """Generate specific insights for an individual move."""
        tactics = move.get('tactics', [])
        impact = move.get('position_impact', {})
        
        tactics_display = ", ".join([t.replace("_", " ").title() for t in tactics[:2]]) if tactics else "None"
        
        key_impacts = []
        if impact.get('material_change', 0) != 0:
            key_impacts.append(f"Material: {impact['material_change']:+d}")
        if abs(impact.get('king_safety_impact', 0)) > 0.1:
            key_impacts.append(f"King Safety: {impact['king_safety_impact']:+.1f}")
        if abs(impact.get('initiative_change', 0)) > 1:
            key_impacts.append(f"Initiative: {impact['initiative_change']:+.1f}")
        
        impacts_display = " • ".join(key_impacts) if key_impacts else "Minimal positional change"
        
        return f"""
        <div class="move-insights">
            <p><strong>Tactics:</strong> {tactics_display}</p>
            <p><strong>Impact:</strong> {impacts_display}</p>
            <p><strong>Complexity:</strong> {move.get('move_complexity', 0)}/5</p>
        </div>
        """
    
    def _generate_radar_chart_svg(self, radar_data: List[Dict], categories: List[str]) -> str:
        """Generate a simple SVG radar chart."""
        # Simplified radar chart - in production, you might want to use a proper charting library
        return """
        <svg width="300" height="300" viewBox="0 0 300 300" style="background: #f8f9fa; border-radius: 8px;">
            <g transform="translate(150,150)">
                <!-- Radar grid -->
                <circle r="50" fill="none" stroke="#e2e8f0" stroke-width="1"/>
                <circle r="100" fill="none" stroke="#e2e8f0" stroke-width="1"/>
                <circle r="120" fill="none" stroke="#cbd5e0" stroke-width="2"/>
                
                <!-- Axis lines -->
                <line x1="0" y1="-120" x2="0" y2="120" stroke="#e2e8f0"/>
                <line x1="-120" y1="0" x2="120" y2="0" stroke="#e2e8f0"/>
                <line x1="-85" y1="-85" x2="85" y2="85" stroke="#e2e8f0"/>
                <line x1="85" y1="-85" x2="-85" y2="85" stroke="#e2e8f0"/>
                
                <!-- Labels -->
                <text x="0" y="-130" text-anchor="middle" font-size="10" fill="#4a5568">Material</text>
                <text x="130" y="5" text-anchor="start" font-size="10" fill="#4a5568">Safety</text>
                <text x="0" y="145" text-anchor="middle" font-size="10" fill="#4a5568">Center</text>
                <text x="-130" y="5" text-anchor="end" font-size="10" fill="#4a5568">Development</text>
                
                <!-- Placeholder for best move visualization -->
                <polygon points="0,-100 70,70 0,80 -70,70" fill="#4299e1" fill-opacity="0.3" stroke="#4299e1" stroke-width="2"/>
                
                <text x="0" y="170" text-anchor="middle" font-size="12" fill="#2d3748" font-weight="bold">Best Move Impact Profile</text>
            </g>
        </svg>
        """
    
    # Include all remaining methods for completeness...
    def _generate_tactical_opportunity_analysis(self, position_data: Dict[str, Any]) -> str:
        """Analyze tactical opportunities each move creates or misses."""
        top_moves = position_data.get('top_moves', [])[:20]  # Top 20 moves
        
        if not top_moves:
            return ""
        
        # Analyze tactical patterns across moves
        all_tactics = set()
        move_tactical_analysis = []
        
        for i, move in enumerate(top_moves):
            tactics = set(move.get('tactics', []))
            all_tactics.update(tactics)
            move_tactical_analysis.append({
                'move': self.html_generator.convert_to_piece_icons(move.get('move', '')),
                'rank': i + 1,
                'tactics': tactics,
                'cp_loss': move.get('centipawn_loss', 0),
                'classification': move.get('classification', 'unknown')
            })
        
        # Identify missed opportunities
        best_move_tactics = move_tactical_analysis[0]['tactics'] if move_tactical_analysis else set()
        
        tactical_matrix_rows = ""
        for analysis in move_tactical_analysis:
            tactics_cells = ""
            for tactic in sorted(all_tactics):
                has_tactic = tactic in analysis['tactics']
                is_unique = tactic in analysis['tactics'] and tactic not in best_move_tactics
                is_missed = tactic in best_move_tactics and tactic not in analysis['tactics']
                
                cell_class = ""
                cell_content = ""
                if has_tactic:
                    if is_unique:
                        cell_class = "tactical-unique"
                        cell_content = "●"
                    else:
                        cell_class = "tactical-present"
                        cell_content = "●"
                elif is_missed:
                    cell_class = "tactical-missed"
                    cell_content = "○"
                else:
                    cell_class = "tactical-none"
                    cell_content = "—"
                
                tactics_cells += f'<td class="{cell_class}">{cell_content}</td>'
            
            row_class = "tactical-best-move" if analysis['rank'] == 1 else ""
            tactical_matrix_rows += f"""
            <tr class="{row_class}">
                <td>#{analysis['rank']}</td>
                <td><strong>{analysis['move']}</strong></td>
                <td>{analysis['cp_loss']}</td>
                {tactics_cells}
            </tr>
            """
        
        tactic_headers = "".join([f'<th class="tactic-header">{tactic.replace("_", " ").title()[:8]}</th>' for tactic in sorted(all_tactics)])
        
        return f"""
        <div class="tactical-opportunity-analysis">
            <h3>⚡ Tactical Opportunity Matrix</h3>
            <p>Analysis of tactical elements each move exploits, creates, or misses.</p>
            
            <div class="tactical-matrix-container">
                <table class="tactical-matrix-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Move</th>
                            <th>CP Loss</th>
                            {tactic_headers}
                        </tr>
                    </thead>
                    <tbody>
                        {tactical_matrix_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="tactical-legend">
                <h4>🔍 Tactical Legend</h4>
                <div class="legend-items">
                    <div><span class="tactical-present">●</span> Tactic exploited</div>
                    <div><span class="tactical-missed">○</span> Tactic missed</div>
                    <div><span class="tactical-none">—</span> Not applicable</div>
                    <div><span class="tactical-unique">●</span> Unique opportunity</div>
                </div>
            </div>
            
            <div class="tactical-insights">
                <h4>💡 Tactical Insights</h4>
                <p>The best move typically exploits the maximum number of available tactical opportunities 
                while avoiding moves that miss critical tactical elements. Each missed tactical opportunity 
                often correlates with centipawn loss and classification degradation.</p>
            </div>
        </div>
        """
    
    def _generate_risk_reward_assessment(self, position_data: Dict[str, Any]) -> str:
        """Generate risk vs reward analysis for moves."""
        top_moves = position_data.get('top_moves', [])[:20]
        
        if not top_moves:
            return ""
        
        # Create scatter plot data
        scatter_data = []
        for i, move in enumerate(top_moves):
            complexity = move.get('move_complexity', 0)
            strategic_value = move.get('strategic_value', 0)
            cp_loss = move.get('centipawn_loss', 0)
            classification = move.get('classification', 'unknown')
            move_notation = self.html_generator.convert_to_piece_icons(move.get('move', ''))
            
            scatter_data.append({
                'move': move_notation,
                'complexity': complexity,
                'strategic_value': strategic_value,
                'cp_loss': cp_loss,
                'classification': classification,
                'rank': i + 1
            })
        
        # Generate scatter plot SVG
        scatter_svg = self._generate_risk_reward_scatter_svg(scatter_data)
        
        # Generate risk assessment table
        risk_table_rows = ""
        for data in scatter_data:
            risk_ratio = data['strategic_value'] / max(1, data['complexity'])  # Avoid division by zero
            risk_class = self._get_risk_class(risk_ratio)
            row_class = "risk-best-move" if data['rank'] == 1 else ""
            
            risk_table_rows += f"""
            <tr class="{row_class}">
                <td>#{data['rank']}</td>
                <td><strong>{data['move']}</strong></td>
                <td>{data['complexity']}/5</td>
                <td>{data['strategic_value']}/5</td>
                <td class="{risk_class}">{risk_ratio:.2f}</td>
                <td>{data['cp_loss']}</td>
                <td><span class="classification-{data['classification'].lower()}">{data['classification']}</span></td>
            </tr>
            """
        
        return f"""
        <div class="risk-reward-assessment">
            <h3>⚖️ Risk vs Reward Analysis</h3>
            <p>Evaluation of move complexity versus strategic payoff for optimal decision making.</p>
            
            <div class="risk-reward-container">
                <div class="scatter-plot">
                    <h4>Risk-Reward Scatter Plot</h4>
                    {scatter_svg}
                </div>
                
                <div class="risk-table">
                    <h4>Detailed Risk Assessment</h4>
                    <table class="risk-assessment-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Move</th>
                                <th>Complexity</th>
                                <th>Strategic Value</th>
                                <th>Risk Ratio</th>
                                <th>CP Loss</th>
                                <th>Quality</th>
                            </tr>
                        </thead>
                        <tbody>
                            {risk_table_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="risk-insights">
                <h4>📊 Risk-Reward Insights</h4>
                <p><strong>Risk Ratio = Strategic Value ÷ Complexity</strong></p>
                <p>Higher ratios indicate better reward-to-risk balance. The engine's choice typically 
                offers optimal strategic value with manageable complexity, maximizing practical chances of success.</p>
            </div>
        </div>
        """
    
    def _generate_risk_reward_scatter_svg(self, scatter_data: List[Dict]) -> str:
        """Generate SVG scatter plot for risk vs reward."""
        # Simplified scatter plot
        return """
        <svg width="400" height="300" viewBox="0 0 400 300" style="background: #f8f9fa; border-radius: 8px;">
            <!-- Axes -->
            <line x1="50" y1="250" x2="350" y2="250" stroke="#4a5568" stroke-width="2"/>
            <line x1="50" y1="250" x2="50" y2="50" stroke="#4a5568" stroke-width="2"/>
            
            <!-- Grid lines -->
            <g stroke="#e2e8f0" stroke-width="1">
                <line x1="110" y1="50" x2="110" y2="250"/>
                <line x1="170" y1="50" x2="170" y2="250"/>
                <line x1="230" y1="50" x2="230" y2="250"/>
                <line x1="290" y1="50" x2="290" y2="250"/>
                <line x1="50" y1="200" x2="350" y2="200"/>
                <line x1="50" y1="150" x2="350" y2="150"/>
                <line x1="50" y1="100" x2="350" y2="100"/>
            </g>
            
            <!-- Labels -->
            <text x="200" y="280" text-anchor="middle" font-size="12" fill="#4a5568">Complexity →</text>
            <text x="25" y="150" text-anchor="middle" font-size="12" fill="#4a5568" transform="rotate(-90, 25, 150)">Strategic Value →</text>
            
            <!-- Best move point (example) -->
            <circle cx="110" cy="100" r="8" fill="#4299e1" stroke="#2b6cb0" stroke-width="2"/>
            <text x="110" y="90" text-anchor="middle" font-size="10" fill="#2b6cb0" font-weight="bold">#1</text>
            
            <!-- Other points (simplified) -->
            <circle cx="170" cy="150" r="6" fill="#ed8936" stroke="#c05621" stroke-width="1"/>
            <circle cx="230" cy="180" r="6" fill="#ed8936" stroke="#c05621" stroke-width="1"/>
            <circle cx="290" cy="200" r="6" fill="#e53e3e" stroke="#c53030" stroke-width="1"/>
            
            <text x="200" y="30" text-anchor="middle" font-size="14" fill="#2d3748" font-weight="bold">Risk vs Reward Profile</text>
        </svg>
        """
    
    def _get_risk_class(self, risk_ratio: float) -> str:
        """Get CSS class for risk ratio."""
        if risk_ratio >= 1.5:
            return "risk-excellent"
        elif risk_ratio >= 1.0:
            return "risk-good"
        elif risk_ratio >= 0.5:
            return "risk-fair"
        else:
            return "risk-poor"

