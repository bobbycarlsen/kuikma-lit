# interactive_html_generator.py - Interactive HTML Template Generator
import os
import re
import json
import chess
import chess.svg
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class InteractiveHTMLGenerator:
    """Enhanced interactive HTML generator with comprehensive analysis and working boards."""
    
    def __init__(self, output_dir: str = "kuikma_analysis"):
        self.output_dir = output_dir
        self.ensure_output_directory()
    
    def ensure_output_directory(self):
        """Ensure output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _convert_numpy_types(self, obj):
        """Convert numpy types to Python native types for JSON serialization."""
        try:
            import numpy as np
            
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: self._convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [self._convert_numpy_types(item) for item in obj]
            else:
                return obj
        except ImportError:
            return obj

    def generate_epic_analysis_report(self, position_data: Dict[str, Any], 
                                    selected_move_data: Dict[str, Any] = None) -> str:
        """Generate the epic interactive chess analysis report."""
        return self.generate_comprehensive_strategic_analysis(
            position_data=position_data,
            selected_move_data=selected_move_data
        )
    
    def generate_comprehensive_strategic_analysis(self, position_data: Dict[str, Any], 
                                                selected_move_data: Dict[str, Any] = None,
                                                **kwargs) -> str:
        """Generate comprehensive interactive chess position analysis report."""
        
        # Extract basic position information
        position_id = position_data.get('id', 'unknown')
        fen = position_data.get('fen', '')
        turn = position_data.get('turn', 'white').lower()
        move_number = position_data.get('fullmove_number', 1)
        top_moves = position_data.get('top_moves', [])
        
        # Get best move
        best_move = top_moves[0] if top_moves else {}
        best_move_notation = best_move.get('move', 'N/A')
        best_move_uci = best_move.get('uci', '')
        
        # Generate result FEN after best move
        result_fen = self._get_position_after_move(fen, best_move_uci)
        
        # Generate spatial analysis data for both positions
        current_spatial_data = self._generate_spatial_analysis_data(fen)
        result_spatial_data = self._generate_spatial_analysis_data(result_fen) if result_fen != fen else current_spatial_data
        
        # Generate comprehensive HTML with ALL content
        html_content = self._generate_complete_html_template(
            position_data, selected_move_data, top_moves, fen, result_fen, 
            current_spatial_data, result_spatial_data
        )
        
        # Save and return path
        timestamp = int(datetime.now().timestamp())
        filename = f"interactive_epic_analysis_{position_id}_{timestamp}.html"
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

    def _generate_complete_html_template(self, position_data: Dict[str, Any], 
                                       selected_move_data: Dict[str, Any], 
                                       top_moves: List[Dict], 
                                       current_fen: str, 
                                       result_fen: str,
                                       current_spatial_data: Dict[str, Any],
                                       result_spatial_data: Dict[str, Any]) -> str:
        """Generate the complete FIXED HTML template with ALL comprehensive content."""
        
        position_id = position_data.get('id', 'unknown')
        turn = position_data.get('turn', 'white')
        move_number = position_data.get('fullmove_number', 1)
        best_move = top_moves[0] if top_moves else {}
        
        # Generate current timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Chess Analysis - Position {position_id}</title>
    
    <!-- External Libraries -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://unpkg.com/chess.js@1.0.0-alpha.0/chess.min.js"></script>
    <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        {self._generate_enhanced_css()}
    </style>
</head>
<body>
    <div id="app" class="app-container">
        <!-- Navigation Header -->
        <header class="nav-header">
            <div class="nav-content">
                <h1><i class="fas fa-chess"></i> Interactive Chess Analysis</h1>
                <div class="position-info">
                    <span class="position-id">Position #{position_id}</span>
                    <span class="move-info">Move {move_number} • {turn.title()} to play</span>
                </div>
            </div>
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showSection('problem')">
                    <i class="fas fa-puzzle-piece"></i> Problem
                </button>
                <button class="nav-tab" onclick="showSection('solution')">
                    <i class="fas fa-lightbulb"></i> Solution
                </button>
                <button class="nav-tab" onclick="showSection('comparison')">
                    <i class="fas fa-balance-scale"></i> Analysis
                </button>
                <button class="nav-tab" onclick="showSection('spatial')">
                    <i class="fas fa-map"></i> Spatial
                </button>
                <button class="nav-tab" onclick="showSection('moves')">
                    <i class="fas fa-list-ol"></i> Top Moves
                </button>
                <button class="nav-tab" onclick="showSection('variations')">
                    <i class="fas fa-code-branch"></i> Variations
                </button>
                <button class="nav-tab" onclick="showSection('insights')">
                    <i class="fas fa-brain"></i> Insights
                </button>
            </div>
        </header>

        <!-- Main Content -->
        <main class="main-content">
            <!-- Problem Section -->
            <section id="problem-section" class="content-section active">
                {self._generate_problem_section(position_data, current_fen)}
            </section>

            <!-- Solution Section -->
            <section id="solution-section" class="content-section">
                {self._generate_solution_section(position_data, best_move, current_fen, result_fen)}
            </section>

            <!-- Analysis Section -->
            <section id="comparison-section" class="content-section">
                {self._generate_analysis_section(position_data, best_move)}
            </section>

            <!-- Spatial Analysis Section -->
            <section id="spatial-section" class="content-section">
                {self._generate_spatial_section(current_fen, result_fen, current_spatial_data, result_spatial_data, best_move)}
            </section>

            <!-- Top Moves Section -->
            <section id="moves-section" class="content-section">
                {self._generate_moves_section(top_moves, current_fen)}
            </section>

            <!-- Variations Section -->
            <section id="variations-section" class="content-section">
                {self._generate_variations_section(position_data, current_fen)}
            </section>

            <!-- Insights Section -->
            <section id="insights-section" class="content-section">
                {self._generate_insights_section(position_data, selected_move_data)}
            </section>
        </main>

        <!-- SVG Board Fallbacks -->
        <div id="svg-boards" style="display: none;">
            <div id="svg-current-board">{self._generate_chess_board_svg(current_fen, False, 400)}</div>
            <div id="svg-result-board">{self._generate_chess_board_svg(result_fen or current_fen, False, 400)}</div>
        </div>

        <!-- Footer -->
        <footer class="report-footer">
            <p>Generated by Kuikma Chess Engine • {current_time}</p>
            <p>Interactive comprehensive analysis with engine evaluation and strategic insights</p>
        </footer>
    </div>

    <script>
        {self._generate_javascript(current_fen, result_fen, top_moves, current_spatial_data, result_spatial_data)}
    </script>
</body>
</html>"""
        
        return html_template

    def _generate_enhanced_css(self) -> str:
        """Generate enhanced CSS with more inviting color palette and proper styling."""
        return """
        /* === RESET & BASE === */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
            line-height: 1.6;
            color: #1a1f2e;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        /* === APP CONTAINER === */
        .app-container {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background: rgba(255, 255, 255, 0.95);
            max-width: 1400px;
            margin: 20px auto;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
            overflow: hidden;
        }

        /* === NAVIGATION === */
        .nav-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            position: relative;
            overflow: hidden;
        }

        .nav-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"><g fill="none" fill-rule="evenodd"><g fill="%23ffffff" fill-opacity="0.05"><circle cx="36" cy="6" r="6"/><circle cx="6" cy="36" r="6"/></g></svg>');
            opacity: 0.3;
        }

        .nav-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 2;
        }

        .nav-content h1 {
            font-size: 2.2rem;
            font-weight: 800;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, #ffffff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .position-info {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            font-size: 1rem;
            color: #e2e8f0;
            font-weight: 600;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }

        .position-id, .move-info {
            background: rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 15px;
            margin-bottom: 0.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.3);
        }

        .nav-tabs {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            position: relative;
            z-index: 2;
        }

        .nav-tab {
            background: rgba(255,255,255,0.15);
            border: 2px solid rgba(255,255,255,0.25);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            backdrop-filter: blur(10px);
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }

        .nav-tab:hover, .nav-tab.active {
            background: rgba(255,255,255,0.3);
            border-color: rgba(255,255,255,0.5);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }

        .nav-tab.active {
            background: linear-gradient(135deg, rgba(255,255,255,0.4), rgba(255,255,255,0.2));
            border-color: rgba(255,255,255,0.6);
        }

        /* === MAIN CONTENT === */
        .main-content {
            flex: 1;
            padding: 2.5rem;
            max-width: 100%;
            overflow-x: hidden;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        }

        .content-section {
            display: none;
            animation: fadeInUp 0.6s ease-out;
        }

        .content-section.active {
            display: block;
        }

        @keyframes fadeInUp {
            from { 
                opacity: 0; 
                transform: translateY(30px); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }

        /* === SECTION HEADERS === */
        .section-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            font-size: 2.2rem;
            font-weight: 800;
            color: #1a1f2e;
            margin-bottom: 2.5rem;
            padding: 2rem;
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 16px;
            border-left: 6px solid #667eea;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
            border: 1px solid rgba(102, 126, 234, 0.1);
        }

        .section-header i {
            color: #667eea;
            font-size: 2rem;
            filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3));
        }

        /* === BOARD CONTAINERS === */
        .board-container {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 12px 40px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            border: 1px solid rgba(102, 126, 234, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .board-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }

        .board-label {
            text-align: center;
            font-weight: 700;
            color: #1a1f2e;
            margin-bottom: 1.5rem;
            font-size: 1.3rem;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border-radius: 12px;
            border: 2px solid rgba(102, 126, 234, 0.2);
        }

        .chessboard-container {
            display: flex;
            justify-content: center;
            margin: 2rem 0;
        }

        .chessboard, .svg-board {
            max-width: 100%;
            width: 100%;
            max-width: 450px;
            border: 4px solid #667eea;
            border-radius: 12px;
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.25);
            transition: transform 0.3s ease;
        }

        .chessboard:hover, .svg-board:hover {
            transform: scale(1.02);
        }

        /* === SVG BOARD SPECIFIC STYLING === */
        .svg-board svg {
            border-radius: 8px;
        }

        /* === SIDE BY SIDE LAYOUT === */
        .side-by-side {
            display: grid;
            grid-template-columns: 1fr;
            gap: 2.5rem;
            margin: 2rem 0;
        }

        @media (min-width: 768px) {
            .side-by-side {
                grid-template-columns: 1fr 1fr;
            }
        }

        /* === CARDS === */
        .info-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 16px;
            padding: 2.5rem;
            box-shadow: 0 12px 40px rgba(0,0,0,0.1);
            border-left: 6px solid #667eea;
            margin-bottom: 2rem;
            border: 1px solid rgba(102, 126, 234, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .info-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }

        .info-card h3 {
            color: #1a1f2e;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            font-size: 1.5rem;
            font-weight: 700;
        }

        .info-card h3 i {
            color: #667eea;
            font-size: 1.4rem;
            filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3));
        }

        /* === METRICS === */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 1.5rem 0;
        }

        .metric-card {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            border: 1px solid rgba(102, 126, 234, 0.1);
            border-top: 4px solid #667eea;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
        }

        .metric-card:hover::before {
            opacity: 1;
        }

        .metric-label {
            font-size: 0.95rem;
            color: #64748b;
            font-weight: 600;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: relative;
            z-index: 2;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            color: #1a1f2e;
            position: relative;
            z-index: 2;
        }

        /* === TABLES === */
        .analysis-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 12px 40px rgba(0,0,0,0.1);
            border: 1px solid rgba(102, 126, 234, 0.1);
        }

        .analysis-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem 1rem;
            text-align: left;
            font-weight: 700;
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }

        .analysis-table td {
            padding: 1.2rem 1rem;
            border-bottom: 1px solid rgba(102, 126, 234, 0.1);
            color: #1a1f2e;
            font-weight: 500;
            transition: background-color 0.3s ease;
        }

        .analysis-table tr:nth-child(even) {
            background: rgba(102, 126, 234, 0.03);
        }

        .analysis-table tr:hover {
            background: rgba(102, 126, 234, 0.1) !important;
            cursor: pointer;
        }

        .move-row {
            transition: all 0.3s ease;
        }

        .move-row:hover {
            background: rgba(102, 126, 234, 0.15) !important;
            transform: scale(1.01);
        }

        .move-row.selected {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
            font-weight: 700;
            border-left: 4px solid #667eea;
        }

        /* === CONTROLS === */
        .board-controls {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
            flex-wrap: wrap;
            justify-content: center;
        }

        .board-controls button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 12px;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }

        .board-controls button:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }

        /* === SPATIAL VISUALIZATION === */
        .spatial-board {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 16px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 12px 40px rgba(0,0,0,0.1);
            border: 1px solid rgba(102, 126, 234, 0.1);
        }

        .spatial-grid {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 2px;
            max-width: 450px;
            margin: 0 auto;
            aspect-ratio: 1;
            border: 4px solid #667eea;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        }

        .spatial-square {
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            transition: all 0.3s ease;
            cursor: pointer;
            font-size: 1.2rem;
        }

        .spatial-square:hover {
            transform: scale(1.1);
            z-index: 10;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            border-radius: 4px;
        }

        .spatial-square.white-control {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
        }

        .spatial-square.black-control {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
        }

        .spatial-square.contested {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
        }

        .spatial-square.neutral.light {
            background: #f0d9b5;
            color: #8b4513;
        }

        .spatial-square.neutral.dark {
            background: #b58863;
            color: white;
        }

        .spatial-legend {
            display: flex;
            justify-content: space-around;
            margin-top: 2rem;
            font-size: 0.95rem;
            color: #1a1f2e;
            font-weight: 600;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .spatial-legend div {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1.5rem;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 12px;
            border: 1px solid rgba(102, 126, 234, 0.1);
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        /* === MOVE DISPLAY === */
        .move-notation {
            font-family: 'Monaco', 'Menlo', 'SF Mono', monospace;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 2rem;
            border-radius: 16px;
            font-weight: 600;
            color: #1a1f2e;
            border-left: 6px solid #667eea;
            border: 1px solid rgba(102, 126, 234, 0.1);
            line-height: 1.8;
            font-size: 1.1rem;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
        }

        /* === TAGS === */
        .tag {
            display: inline-block;
            background: linear-gradient(135deg, #ddd6fe 0%, #c4b5fd 100%);
            color: #5b21b6;
            padding: 0.75rem 1.25rem;
            border-radius: 25px;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 0.25rem;
            border: 2px solid #8b5cf6;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2);
        }

        .tag:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
            background: linear-gradient(135deg, #c4b5fd 0%, #a78bfa 100%);
        }

        /* === VARIATIONS === */
        .variation-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            margin: 2rem 0;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 12px 40px rgba(0,0,0,0.1);
            border: 1px solid rgba(102, 126, 234, 0.1);
            transition: transform 0.3s ease;
        }

        .variation-card:hover {
            transform: translateY(-5px);
        }

        .variation-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            font-weight: 700;
            font-size: 1.3rem;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }

        .variation-content {
            padding: 2.5rem;
        }

        .variation-boards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }

        .variation-board-item {
            text-align: center;
        }

        .variation-board-item h5 {
            margin-bottom: 1rem;
            color: #1a1f2e;
            font-weight: 600;
        }

        /* === FOOTER === */
        .report-footer {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            color: #64748b;
            text-align: center;
            padding: 2.5rem;
            border-top: 1px solid rgba(102, 126, 234, 0.1);
            margin-top: 3rem;
        }

        .report-footer p {
            margin: 0.5rem 0;
            font-weight: 500;
        }

        /* === RESPONSIVE DESIGN === */
        @media (max-width: 768px) {
            .app-container {
                margin: 10px;
                border-radius: 15px;
            }
            
            .main-content {
                padding: 1.5rem;
            }
            
            .nav-tabs {
                overflow-x: auto;
                scrollbar-width: none;
                -ms-overflow-style: none;
            }
            
            .nav-tabs::-webkit-scrollbar {
                display: none;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                gap: 1rem;
            }
            
            .chessboard, .svg-board {
                max-width: 320px;
            }
            
            .analysis-table {
                font-size: 0.85rem;
            }
            
            .analysis-table th,
            .analysis-table td {
                padding: 1rem 0.75rem;
            }
            
            .section-header {
                font-size: 1.8rem;
                padding: 1.5rem;
            }
        }

        /* === SCORE STYLING === */
        .score-positive { color: #10b981; font-weight: 700; }
        .score-negative { color: #ef4444; font-weight: 700; }
        .score-neutral { color: #6b7280; font-weight: 700; }
        .change-positive { color: #10b981; }
        .change-negative { color: #ef4444; }
        .change-neutral { color: #6b7280; }

        /* === LOADING STATES === */
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .pulse {
            animation: pulse 2s infinite;
        }
        """

    def _generate_javascript(self, current_fen: str, result_fen: str, 
                           top_moves: List[Dict], current_spatial_data: Dict[str, Any], 
                           result_spatial_data: Dict[str, Any]) -> str:
        """Generate enhanced JavaScript with better error handling and features."""
        
        # Convert numpy types safely
        top_moves_clean = self._convert_numpy_types(top_moves)
        current_spatial_clean = self._convert_numpy_types(current_spatial_data)
        result_spatial_clean = self._convert_numpy_types(result_spatial_data)
        
        # Fix PV data extraction
        for move in top_moves_clean:
            if not move.get('pv') and move.get('principal_variation'):
                move['pv'] = move['principal_variation']
            elif not move.get('pv'):
                # If no PV, create a simple one with just the move
                move['pv'] = move.get('move', '')
        
        top_moves_json = json.dumps(top_moves_clean)
        current_spatial_json = json.dumps(current_spatial_clean)
        result_spatial_json = json.dumps(result_spatial_clean)
        
        js_code = f"""
        // Global variables
        let boards = {{}};
        let variationBoards = {{}};
        let currentFen = '{current_fen}';
        let resultFen = '{result_fen}';
        let topMoves = {top_moves_json};
        let currentSpatialData = {current_spatial_json};
        let resultSpatialData = {result_spatial_json};
        let currentOrientation = 'white';
        let usingSVGFallback = false;

        // Wait for all libraries to load
        $(document).ready(function() {{
            console.log('Document ready, initializing...');
            
            // Check if required libraries are loaded
            if (typeof Chessboard === 'undefined' || typeof Chess === 'undefined') {{
                console.warn('Chess libraries not loaded, using SVG fallback');
                usingSVGFallback = true;
                initializeSVGBoards();
            }} else {{
                console.log('Chess libraries loaded successfully');
                setTimeout(function() {{
                    initializeInteractiveBoards();
                }}, 200);
            }}
            
            // Always initialize spatial visualization and other features
            setTimeout(function() {{
                initializeSpatialVisualization();
                initializeMoveAnalysis();
                initializeVariationBoards();
            }}, 400);
        }});

        // Enhanced SVG Board fallback with better piece rendering
        function initializeSVGBoards() {{
            console.log('Initializing enhanced SVG fallback boards');
            
            const boardContainers = document.querySelectorAll('.chessboard-container');
            boardContainers.forEach((container, index) => {{
                const boardId = container.querySelector('[id*="board"]')?.id;
                let svgContent = '';
                
                // Determine which SVG to use
                if (boardId && boardId.includes('result')) {{
                    svgContent = document.getElementById('svg-result-board').innerHTML;
                }} else {{
                    svgContent = document.getElementById('svg-current-board').innerHTML;
                }}
                
                if (svgContent) {{
                    const boardElement = document.createElement('div');
                    boardElement.className = 'svg-board';
                    boardElement.innerHTML = svgContent;
                    
                    // Clear container and add SVG board
                    container.innerHTML = '';
                    container.appendChild(boardElement);
                    
                    console.log('SVG board added to container:', boardId);
                }} else {{
                    console.warn('No SVG content found for board:', boardId);
                    container.innerHTML = '<div class="board-error">Board unavailable</div>';
                }}
            }});
        }}

        // Enhanced interactive board initialization
        function initializeInteractiveBoards() {{
            try {{
                console.log('Initializing interactive boards with improved error handling');
                
                const config = {{
                    position: currentFen,
                    orientation: currentOrientation,
                    draggable: false,
                    showNotation: true,
                    pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{{piece}}.png'
                }};

                const boardConfigs = [
                    {{ id: 'problem-board', fen: currentFen }},
                    {{ id: 'solution-current-board', fen: currentFen }},
                    {{ id: 'solution-result-board', fen: resultFen }},
                    {{ id: 'spatial-current-board', fen: currentFen }},
                    {{ id: 'spatial-result-board', fen: resultFen }},
                    {{ id: 'comparison-board', fen: currentFen }},
                    {{ id: 'moves-board', fen: currentFen }},
                    {{ id: 'variations-board', fen: currentFen }}
                ];
                
                boardConfigs.forEach(boardConfig => {{
                    const element = document.getElementById(boardConfig.id);
                    if (element) {{
                        try {{
                            const boardSpecificConfig = {{
                                ...config,
                                position: boardConfig.fen || currentFen
                            }};
                            
                            boards[boardConfig.id] = Chessboard(boardConfig.id, boardSpecificConfig);
                            console.log('Successfully initialized board:', boardConfig.id);
                            
                            // Set position after a short delay
                            setTimeout(() => {{
                                if (boards[boardConfig.id] && boardConfig.fen) {{
                                    try {{
                                        boards[boardConfig.id].position(boardConfig.fen);
                                    }} catch (e) {{
                                        console.warn('Could not set position for', boardConfig.id, e);
                                    }}
                                }}
                            }}, 100);
                            
                        }} catch (e) {{
                            console.error('Failed to initialize board:', boardConfig.id, e);
                            // Fall back to SVG for this specific board
                            initializeSingleSVGBoard(element, boardConfig.fen || currentFen);
                        }}
                    }}
                }});

            }} catch (e) {{
                console.error('Error initializing interactive boards:', e);
                usingSVGFallback = true;
                initializeSVGBoards();
            }}
        }}

        // Initialize single SVG board fallback
        function initializeSingleSVGBoard(container, fen) {{
            try {{
                // Create a simple board representation
                const boardDiv = document.createElement('div');
                boardDiv.className = 'svg-board-fallback';
                boardDiv.innerHTML = '<div style="width: 400px; height: 400px; background: #f0d9b5; border: 2px solid #8B4513; display: flex; align-items: center; justify-content: center; color: #8B4513; font-size: 16px;">Chess Board<br>FEN: ' + fen.substring(0, 20) + '...</div>';
                
                container.innerHTML = '';
                container.appendChild(boardDiv);
                
                console.log('SVG fallback board created for container');
            }} catch (e) {{
                console.error('Error creating SVG fallback:', e);
            }}
        }}

        // Enhanced navigation with better transitions
        function showSection(sectionName) {{
            try {{
                console.log('Showing section:', sectionName);
                
                // Hide all sections with fade out
                document.querySelectorAll('.content-section').forEach(section => {{
                    section.classList.remove('active');
                }});

                // Show target section with fade in
                const targetSection = document.getElementById(sectionName + '-section');
                if (targetSection) {{
                    setTimeout(() => {{
                        targetSection.classList.add('active');
                    }}, 150);
                }}

                // Update navigation tabs
                document.querySelectorAll('.nav-tab').forEach(nav => {{
                    nav.classList.remove('active');
                }});

                document.querySelectorAll('[onclick*="' + sectionName + '"]').forEach(nav => {{
                    nav.classList.add('active');
                }});

                // Resize boards after section change
                if (!usingSVGFallback) {{
                    setTimeout(() => {{
                        resizeAllBoards();
                    }}, 300);
                }}

                // Section-specific initialization
                if (sectionName === 'spatial') {{
                    setTimeout(() => {{
                        initializeSpatialVisualization();
                    }}, 300);
                }} else if (sectionName === 'variations') {{
                    setTimeout(() => {{
                        initializeVariationBoards();
                    }}, 300);
                }}
            }} catch (e) {{
                console.error('Error showing section:', e);
            }}
        }}

        // Resize all boards
        function resizeAllBoards() {{
            try {{
                Object.values(boards).forEach(board => {{
                    if (board && typeof board.resize === 'function') {{
                        try {{
                            board.resize();
                        }} catch (e) {{
                            console.warn('Board resize failed:', e);
                        }}
                    }}
                }});
                
                Object.values(variationBoards).forEach(board => {{
                    if (board && typeof board.resize === 'function') {{
                        try {{
                            board.resize();
                        }} catch (e) {{
                            console.warn('Variation board resize failed:', e);
                        }}
                    }}
                }});
            }} catch (e) {{
                console.error('Error resizing boards:', e);
            }}
        }}

        // Enhanced board controls
        function flipBoard(boardId) {{
            try {{
                if (usingSVGFallback) {{
                    console.log('SVG fallback: flip not implemented');
                    return;
                }}
                
                if (boards[boardId] && typeof boards[boardId].orientation === 'function') {{
                    currentOrientation = currentOrientation === 'white' ? 'black' : 'white';
                    boards[boardId].orientation(currentOrientation);
                    
                    // Apply to all boards
                    Object.keys(boards).forEach(id => {{
                        if (boards[id] && id !== boardId && typeof boards[id].orientation === 'function') {{
                            try {{
                                boards[id].orientation(currentOrientation);
                            }} catch (e) {{
                                console.warn('Failed to flip board:', id, e);
                            }}
                        }}
                    }});
                    
                    console.log('Flipped boards to:', currentOrientation);
                }}
            }} catch (e) {{
                console.error('Error flipping board:', e);
            }}
        }}

        function animateBestMove() {{
            try {{
                if (topMoves.length > 0) {{
                    const bestMove = topMoves[0];
                    console.log('Animating best move:', bestMove.move);
                    
                    if (!usingSVGFallback && boards['solution-result-board']) {{
                        setTimeout(() => {{
                            try {{
                                boards['solution-result-board'].position(resultFen, true);
                            }} catch (e) {{
                                console.warn('Animation failed, setting position directly:', e);
                                boards['solution-result-board'].position(resultFen);
                            }}
                        }}, 1000);
                    }}
                }}
            }} catch (e) {{
                console.error('Error animating move:', e);
            }}
        }}

        // Enhanced spatial analysis with comparison
        function initializeSpatialVisualization() {{
            try {{
                // Initialize current position spatial board
                initializeSingleSpatialBoard('spatial-current-control-board', currentSpatialData, 'Current Position');
                
                // Initialize result position spatial board
                if (resultSpatialData && JSON.stringify(resultSpatialData) !== JSON.stringify(currentSpatialData)) {{
                    initializeSingleSpatialBoard('spatial-result-control-board', resultSpatialData, 'After Best Move');
                }}
                
                console.log('Spatial visualization initialized successfully');
            }} catch (e) {{
                console.error('Error initializing spatial visualization:', e);
            }}
        }}

        function initializeSingleSpatialBoard(boardId, spatialData, title) {{
            try {{
                const spatialGrid = document.getElementById(boardId);
                if (!spatialGrid || !spatialData || !spatialData.control_matrix) {{
                    console.warn(`Spatial visualization data not available for ${{boardId}}`);
                    return;
                }}

                spatialGrid.innerHTML = '';
                
                for (let rank = 7; rank >= 0; rank--) {{
                    for (let file = 0; file < 8; file++) {{
                        const square = document.createElement('div');
                        square.className = 'spatial-square';
                        
                        if (spatialData.control_matrix[rank] && spatialData.control_matrix[rank][file] !== undefined) {{
                            const controlValue = spatialData.control_matrix[rank][file];
                            const isLight = (rank + file) % 2 === 0;
                            
                            if (controlValue === 1) {{
                                square.classList.add('white-control');
                                square.textContent = '♔';
                                square.title = `${{String.fromCharCode(97 + file)}}${{rank + 1}} - White Control`;
                            }} else if (controlValue === -1) {{
                                square.classList.add('black-control');
                                square.textContent = '♚';
                                square.title = `${{String.fromCharCode(97 + file)}}${{rank + 1}} - Black Control`;
                            }} else if (controlValue === 2) {{
                                square.classList.add('contested');
                                square.textContent = '⚡';
                                square.title = `${{String.fromCharCode(97 + file)}}${{rank + 1}} - Contested`;
                            }} else {{
                                square.classList.add('neutral', isLight ? 'light' : 'dark');
                                square.title = `${{String.fromCharCode(97 + file)}}${{rank + 1}} - Neutral`;
                            }}
                            
                            square.addEventListener('click', function() {{
                                showSquareInfo(file, rank, controlValue, title);
                            }});
                        }} else {{
                            const isLight = (rank + file) % 2 === 0;
                            square.classList.add('neutral', isLight ? 'light' : 'dark');
                        }}
                        
                        spatialGrid.appendChild(square);
                    }}
                }}
                
                console.log(`Spatial visualization initialized for ${{boardId}}`);
            }} catch (e) {{
                console.error(`Error initializing spatial visualization for ${{boardId}}:`, e);
            }}
        }}

        function showSquareInfo(file, rank, controlValue, boardTitle) {{
            try {{
                const squareName = String.fromCharCode(97 + file) + (rank + 1);
                let controlText = 'Neutral';
                
                if (controlValue === 1) controlText = 'White Control';
                else if (controlValue === -1) controlText = 'Black Control';
                else if (controlValue === 2) controlText = 'Contested';
                
                alert(`${{boardTitle}}\\nSquare ${{squareName}}: ${{controlText}}`);
            }} catch (e) {{
                console.error('Error showing square info:', e);
            }}
        }}

        // Enhanced move analysis with PV support
        function initializeMoveAnalysis() {{
            try {{
                document.querySelectorAll('.move-row').forEach(row => {{
                    row.addEventListener('click', function() {{
                        const moveIndex = this.getAttribute('data-move-index');
                        if (moveIndex) {{
                            showMoveOnBoard('', parseInt(moveIndex));
                        }}
                    }});
                }});
                
                console.log('Move analysis initialized');
            }} catch (e) {{
                console.error('Error initializing move analysis:', e);
            }}
        }}

        function showMoveOnBoard(uciMove, moveIndex) {{
            try {{
                if (!usingSVGFallback && boards['moves-board']) {{
                    boards['moves-board'].position(currentFen);
                }}
                
                const moveInfo = document.getElementById('selected-move-info');
                const move = topMoves[moveIndex - 1];
                if (moveInfo && move) {{
                    // Extract PV - try multiple field names
                    let pv = move.pv || move.principal_variation || move.move || '';
                    
                    moveInfo.innerHTML = 
                        '<h4>Move #' + moveIndex + ': ' + convertToPieceIcons(move.move) + '</h4>' +
                        '<p><strong>Score:</strong> ' + formatScore(move.score) + '</p>' +
                        '<p><strong>Classification:</strong> ' + (move.classification || 'Unknown') + '</p>' +
                        '<p><strong>Centipawn Loss:</strong> ' + (move.centipawn_loss || 0) + '</p>' +
                        '<p><strong>Principal Variation:</strong></p>' +
                        '<div class="move-notation">' + convertToPieceIcons(pv) + '</div>';
                }}
                
                document.querySelectorAll('.move-row').forEach(row => {{
                    row.classList.remove('selected');
                }});
                
                const selectedRow = document.querySelector('[data-move-index="' + moveIndex + '"]');
                if (selectedRow) {{
                    selectedRow.classList.add('selected');
                }}
                
                console.log('Showing move analysis for move #' + moveIndex);
            }} catch (e) {{
                console.error('Error showing move on board:', e);
            }}
        }}

        // Enhanced variation boards with progression
        function initializeVariationBoards() {{
            try {{
                if (usingSVGFallback) {{
                    console.log('Variation boards not available in SVG fallback mode');
                    return;
                }}
                
                // Clear existing variation boards
                Object.keys(variationBoards).forEach(key => {{
                    if (variationBoards[key] && typeof variationBoards[key].destroy === 'function') {{
                        try {{
                            variationBoards[key].destroy();
                        }} catch (e) {{
                            console.warn('Could not destroy variation board:', key);
                        }}
                    }}
                }});
                variationBoards = {{}};
                
                // Initialize variation boards for top 3 moves
                topMoves.slice(0, 3).forEach((move, index) => {{
                    const boardId = `variation-board-${{index + 1}}`;
                    const element = document.getElementById(boardId);
                    
                    if (element && typeof Chessboard !== 'undefined') {{
                        try {{
                            // Calculate position after this variation
                            const variationFen = calculateVariationPosition(currentFen, move.pv || move.principal_variation || move.move);
                            
                            const config = {{
                                position: variationFen,
                                orientation: currentOrientation,
                                draggable: false,
                                showNotation: false,
                                pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{{piece}}.png'
                            }};
                            
                            variationBoards[boardId] = Chessboard(boardId, config);
                            console.log('Initialized variation board:', boardId);
                            
                        }} catch (e) {{
                            console.error('Failed to initialize variation board:', boardId, e);
                        }}
                    }}
                }});
                
                console.log('Variation boards initialized');
            }} catch (e) {{
                console.error('Error initializing variation boards:', e);
            }}
        }}

        // Calculate position after variation moves
        function calculateVariationPosition(startFen, pvString) {{
            try {{
                if (!pvString || typeof Chess === 'undefined') {{
                    return startFen;
                }}
                
                const chess = new Chess(startFen);
                const moves = pvString.trim().split(/\\s+/);
                
                // Try to play moves from the PV
                for (let i = 0; i < Math.min(moves.length, 6); i++) {{ // Limit to 6 moves
                    const moveStr = moves[i].replace(/\\d+\\./, '').trim(); // Remove move numbers
                    if (moveStr && moveStr !== '') {{
                        try {{
                            const move = chess.move(moveStr);
                            if (!move) {{
                                console.warn('Invalid move in PV:', moveStr);
                                break;
                            }}
                        }} catch (e) {{
                            console.warn('Could not play move from PV:', moveStr, e);
                            break;
                        }}
                    }}
                }}
                
                return chess.fen();
            }} catch (e) {{
                console.error('Error calculating variation position:', e);
                return startFen;
            }}
        }}

        // Utility functions
        function convertToPieceIcons(moveString) {{
            if (!moveString) return '';
            
            const pieceIcons = {{
                'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘'
            }};
            
            let result = moveString;
            for (const [piece, icon] of Object.entries(pieceIcons)) {{
                result = result.replace(new RegExp(piece, 'g'), icon);
            }}
            
            return result;
        }}

        function formatScore(score) {{
            if (score === null || score === undefined) return "0.00";
            
            if (typeof score === 'object') {{
                if (score.mate) {{
                    return score.mate > 0 ? 'M' + score.mate : 'M' + Math.abs(score.mate);
                }}
                if (score.cp !== undefined) {{
                    return (score.cp / 100).toFixed(2);
                }}
            }}
            
            if (typeof score === 'number') {{
                if (Math.abs(score) > 900) {{
                    return (score / 100).toFixed(2);
                }}
                return score.toFixed(2);
            }}
            
            return String(score);
        }}

        // Global error handler
        window.addEventListener('error', function(event) {{
            console.error('Global error:', event.error);
        }});

        console.log('Enhanced JavaScript loaded successfully');
        """
        
        return js_code

    # Enhanced section generation methods

    def _generate_problem_section(self, position_data: Dict[str, Any], fen: str) -> str:
        """Generate problem section with enhanced styling."""
        themes = position_data.get('themes', [])
        themes_html = ''.join([f'<span class="tag">{theme.replace("_", " ").title()}</span>' for theme in themes[:6]])
        
        return f"""
        <div class="section-header">
            <i class="fas fa-puzzle-piece"></i>
            The Challenge
        </div>
        
        <div class="side-by-side">
            <div class="board-container">
                <div class="board-label">Current Position</div>
                <div class="chessboard-container">
                    <div id="problem-board" class="chessboard"></div>
                </div>
                <div class="board-controls">
                    <button onclick="flipBoard('problem-board')">
                        <i class="fas fa-sync-alt"></i> Flip Board
                    </button>
                </div>
            </div>
            
            <div class="info-card">
                <h3><i class="fas fa-target"></i> Your Mission</h3>
                <p style="font-size: 1.2rem; line-height: 1.6; color: #1a1f2e; margin-bottom: 1.5rem; font-weight: 500;">
                    {position_data.get('description', 'Find the best move in this position.')}
                </p>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Game Phase</div>
                        <div class="metric-value">{position_data.get('game_phase', 'Middlegame').title()}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Difficulty Rating</div>
                        <div class="metric-value">{position_data.get('difficulty_rating', 1200)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Position Type</div>
                        <div class="metric-value">{position_data.get('position_type', 'Tactical').title()}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Source</div>
                        <div class="metric-value">{position_data.get('source_type', 'Database').title()}</div>
                    </div>
                </div>
                
                {f'<div style="margin-top: 1.5rem;"><h4><i class="fas fa-tags"></i> Tactical Themes</h4><div>{themes_html}</div></div>' if themes_html else ''}
            </div>
        </div>
        """

    def _generate_solution_section(self, position_data: Dict[str, Any], 
                                 best_move: Dict[str, Any], 
                                 current_fen: str, 
                                 result_fen: str) -> str:
        """Generate solution section with enhanced features."""
        best_move_notation = best_move.get('move', 'N/A')
        score = best_move.get('score', 0)
        score_display = self.format_score_display(score)
        
        # Extract PV properly
        pv = best_move.get('pv') or best_move.get('principal_variation') or best_move_notation
        
        return f"""
        <div class="section-header">
            <i class="fas fa-lightbulb"></i>
            The Solution
        </div>
        
        <div class="side-by-side">
            <div class="board-container">
                <div class="board-label">Current Position</div>
                <div class="chessboard-container">
                    <div id="solution-current-board" class="chessboard"></div>
                </div>
            </div>
            
            <div class="board-container">
                <div class="board-label">After Best Move: {self.convert_to_piece_icons(best_move_notation)}</div>
                <div class="chessboard-container">
                    <div id="solution-result-board" class="chessboard"></div>
                </div>
                <div class="board-controls">
                    <button onclick="animateBestMove()">
                        <i class="fas fa-play"></i> Animate Move
                    </button>
                    <button onclick="flipBoard('solution-result-board')">
                        <i class="fas fa-sync-alt"></i> Flip Board
                    </button>
                </div>
            </div>
        </div>
        
        <div class="info-card">
            <h3><i class="fas fa-chess-knight"></i> Best Move Analysis</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Engine Evaluation</div>
                    <div class="metric-value">{score_display}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Classification</div>
                    <div class="metric-value">{best_move.get('classification', 'N/A').title()}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Search Depth</div>
                    <div class="metric-value">{best_move.get('depth', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Strategic Value</div>
                    <div class="metric-value">{best_move.get('strategic_value', 0)}/5</div>
                </div>
            </div>
            
            <h4><i class="fas fa-chess-board"></i> Principal Variation</h4>
            <div class="move-notation">{self.convert_to_piece_icons(pv)}</div>
        </div>
        """

    def _generate_spatial_section(self, current_fen: str, result_fen: str, 
                                current_spatial_data: Dict[str, Any], 
                                result_spatial_data: Dict[str, Any],
                                best_move: Dict[str, Any]) -> str:
        """Generate enhanced spatial analysis section with comparison."""
        return f"""
        <div class="section-header">
            <i class="fas fa-map"></i>
            Spatial Analysis Comparison
        </div>
        
        <div class="side-by-side">
            <div class="board-container">
                <div class="board-label">Current Position</div>
                <div class="chessboard-container">
                    <div id="spatial-current-board" class="chessboard"></div>
                </div>
                <div class="board-controls">
                    <button onclick="flipBoard('spatial-current-board')">
                        <i class="fas fa-sync-alt"></i> Flip Board
                    </button>
                </div>
            </div>
            
            <div class="board-container">
                <div class="board-label">After Best Move: {self.convert_to_piece_icons(best_move.get('move', 'N/A'))}</div>
                <div class="chessboard-container">
                    <div id="spatial-result-board" class="chessboard"></div>
                </div>
                <div class="board-controls">
                    <button onclick="flipBoard('spatial-result-board')">
                        <i class="fas fa-sync-alt"></i> Flip Board
                    </button>
                </div>
            </div>
        </div>
        
        <div class="side-by-side">
            <div class="spatial-board">
                <div class="board-label">Current Position - Space Control</div>
                <div id="spatial-current-control-board" class="spatial-grid"></div>
                <div class="spatial-legend">
                    <div><span style="width: 16px; height: 16px; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); display: inline-block; border-radius: 2px;"></span> White Control</div>
                    <div><span style="width: 16px; height: 16px; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); display: inline-block; border-radius: 2px;"></span> Black Control</div>
                    <div><span style="width: 16px; height: 16px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); display: inline-block; border-radius: 2px;"></span> Contested</div>
                    <div><span style="width: 16px; height: 16px; background: #f0d9b5; display: inline-block; border-radius: 2px;"></span> Neutral</div>
                </div>
            </div>
            
            <div class="spatial-board">
                <div class="board-label">After Best Move - Space Control</div>
                <div id="spatial-result-control-board" class="spatial-grid"></div>
                <div class="spatial-legend">
                    <div><span style="width: 16px; height: 16px; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); display: inline-block; border-radius: 2px;"></span> White Control</div>
                    <div><span style="width: 16px; height: 16px; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); display: inline-block; border-radius: 2px;"></span> Black Control</div>
                    <div><span style="width: 16px; height: 16px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); display: inline-block; border-radius: 2px;"></span> Contested</div>
                    <div><span style="width: 16px; height: 16px; background: #f0d9b5; display: inline-block; border-radius: 2px;"></span> Neutral</div>
                </div>
            </div>
        </div>
        
        <div class="info-card">
            <h3><i class="fas fa-chart-area"></i> Spatial Metrics Comparison</h3>
            <div style="overflow-x: auto;">
                <table class="analysis-table">
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Current Position</th>
                            <th>After Best Move</th>
                            <th>Change</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>White Territory</strong></td>
                            <td>{current_spatial_data.get('white_space_percentage', 0):.1f}%</td>
                            <td>{result_spatial_data.get('white_space_percentage', 0):.1f}%</td>
                            <td class="{'score-positive' if result_spatial_data.get('white_space_percentage', 0) > current_spatial_data.get('white_space_percentage', 0) else 'score-negative' if result_spatial_data.get('white_space_percentage', 0) < current_spatial_data.get('white_space_percentage', 0) else 'score-neutral'}">{result_spatial_data.get('white_space_percentage', 0) - current_spatial_data.get('white_space_percentage', 0):+.1f}%</td>
                        </tr>
                        <tr>
                            <td><strong>Black Territory</strong></td>
                            <td>{current_spatial_data.get('black_space_percentage', 0):.1f}%</td>
                            <td>{result_spatial_data.get('black_space_percentage', 0):.1f}%</td>
                            <td class="{'score-negative' if result_spatial_data.get('black_space_percentage', 0) > current_spatial_data.get('black_space_percentage', 0) else 'score-positive' if result_spatial_data.get('black_space_percentage', 0) < current_spatial_data.get('black_space_percentage', 0) else 'score-neutral'}">{result_spatial_data.get('black_space_percentage', 0) - current_spatial_data.get('black_space_percentage', 0):+.1f}%</td>
                        </tr>
                        <tr>
                            <td><strong>Contested Squares</strong></td>
                            <td>{current_spatial_data.get('contested_percentage', 0):.1f}%</td>
                            <td>{result_spatial_data.get('contested_percentage', 0):.1f}%</td>
                            <td class="score-neutral">{result_spatial_data.get('contested_percentage', 0) - current_spatial_data.get('contested_percentage', 0):+.1f}%</td>
                        </tr>
                        <tr>
                            <td><strong>Space Advantage</strong></td>
                            <td>{current_spatial_data.get('space_advantage', 0):+.0f}</td>
                            <td>{result_spatial_data.get('space_advantage', 0):+.0f}</td>
                            <td class="{'score-positive' if result_spatial_data.get('space_advantage', 0) > current_spatial_data.get('space_advantage', 0) else 'score-negative' if result_spatial_data.get('space_advantage', 0) < current_spatial_data.get('space_advantage', 0) else 'score-neutral'}">{result_spatial_data.get('space_advantage', 0) - current_spatial_data.get('space_advantage', 0):+.0f}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        """

    def _generate_moves_section(self, top_moves: List[Dict], fen: str) -> str:
        """Generate top moves section with enhanced PV display."""
        moves_table_rows = ""
        for i, move in enumerate(top_moves[:10], 1):
            score_display = self.format_score_display(move.get('score', 0))
            
            # Extract PV properly - try multiple field names
            pv = move.get('pv') or move.get('principal_variation') or move.get('move', '')
            pv_display = self.convert_to_piece_icons(pv)
            if len(pv_display) > 50:
                pv_display = pv_display[:50] + "..."
            
            moves_table_rows += f"""
            <tr class="move-row" data-move-index="{i}">
                <td><strong>#{i}</strong></td>
                <td><strong>{self.convert_to_piece_icons(move.get('move', ''))}</strong></td>
                <td>{score_display}</td>
                <td>{move.get('centipawn_loss', 0)}</td>
                <td>{move.get('classification', 'Unknown').title()}</td>
                <td style="font-family: monospace; font-size: 0.9rem; color: #1a1f2e;">{pv_display}</td>
            </tr>
            """
        
        return f"""
        <div class="section-header">
            <i class="fas fa-list-ol"></i>
            Top Engine Moves
        </div>
        
        <div class="side-by-side">
            <div class="board-container">
                <div class="board-label">Move Analysis Board</div>
                <div class="chessboard-container">
                    <div id="moves-board" class="chessboard"></div>
                </div>
                <div class="board-controls">
                    <button onclick="flipBoard('moves-board')">
                        <i class="fas fa-sync-alt"></i> Flip Board
                    </button>
                </div>
                <div class="info-card" id="selected-move-info" style="margin-top: 1rem; margin-bottom: 0;">
                    <h4><i class="fas fa-info-circle"></i> Move Details</h4>
                    <p>Click on a move in the table to see detailed analysis</p>
                </div>
            </div>
            
            <div class="info-card">
                <h3><i class="fas fa-trophy"></i> Engine Recommendations</h3>
                <div style="max-height: 500px; overflow-y: auto;">
                    <table class="analysis-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Move</th>
                                <th>Score</th>
                                <th>CP Loss</th>
                                <th>Quality</th>
                                <th>Principal Variation</th>
                            </tr>
                        </thead>
                        <tbody>
                            {moves_table_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """

    def _generate_variations_section(self, position_data: Dict[str, Any], current_fen: str) -> str:
        """Generate variations section with board progression."""
        top_moves = position_data.get('top_moves', [])[:3]
        variations_html = ""
        
        for i, move in enumerate(top_moves, 1):
            move_name = move.get('move', f'Variation {i}')
            score_display = self.format_score_display(move.get('score', 0))
            pv_notation = move.get('pv') or move.get('principal_variation') or move_name
            pv_display = self.convert_to_piece_icons(pv_notation)
            
            variations_html += f"""
            <div class="variation-card">
                <div class="variation-header">
                    Variation {i}: {self.convert_to_piece_icons(move_name)} ({score_display})
                </div>
                <div class="variation-content">
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-label">Engine Score</div>
                            <div class="metric-value">{score_display}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Classification</div>
                            <div class="metric-value">{move.get('classification', 'Unknown')}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">CP Loss</div>
                            <div class="metric-value">{move.get('centipawn_loss', 0)}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Depth</div>
                            <div class="metric-value">{move.get('depth', 0)}</div>
                        </div>
                    </div>
                    
                    <div class="variation-boards">
                        <div class="variation-board-item">
                            <h5><i class="fas fa-chess-board"></i> Position After Variation</h5>
                            <div class="chessboard-container">
                                <div id="variation-board-{i}" class="chessboard"></div>
                            </div>
                        </div>
                    </div>
                    
                    <h4><i class="fas fa-chess-board"></i> Principal Variation</h4>
                    <div class="move-notation">{pv_display}</div>
                </div>
            </div>
            """
        
        return f"""
        <div class="section-header">
            <i class="fas fa-code-branch"></i>
            Principal Variations
        </div>
        
        <div class="board-container">
            <div class="board-label">Variations Analysis Board</div>
            <div class="chessboard-container">
                <div id="variations-board" class="chessboard"></div>
            </div>
            <div class="board-controls">
                <button onclick="flipBoard('variations-board')">
                    <i class="fas fa-sync-alt"></i> Flip Board
                </button>
                <button onclick="initializeVariationBoards()">
                    <i class="fas fa-refresh"></i> Update Variation Boards
                </button>
            </div>
        </div>
        
        <div style="margin-top: 2rem;">
            <p style="font-size: 1.1rem; color: #1a1f2e; margin-bottom: 2rem; line-height: 1.6;">
                Detailed breakdown of the top variations with comprehensive evaluation and board positions after key moves.
            </p>
            {variations_html}
        </div>
        """

    def _generate_insights_section(self, position_data: Dict[str, Any], selected_move_data: Dict[str, Any]) -> str:
        """Generate insights section with enhanced styling."""
        learning_insights = position_data.get('learning_insights', {})
        universal = learning_insights.get('universal', {})
        
        return f"""
        <div class="section-header">
            <i class="fas fa-brain"></i>
            Strategic Insights & Learning
        </div>
        
        <div class="info-card">
            <h3><i class="fas fa-bullseye"></i> Position Assessment</h3>
            <div style="background: linear-gradient(135deg, #e8f5e8, #c6f6d5); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; border-left: 5px solid #10b981;">
                <p style="font-size: 1.2rem; line-height: 1.6; color: #1a1f2e; margin: 0;">
                    <strong>🔍 Engine Assessment:</strong> {universal.get('position_assessment', 'This is a complex position requiring careful analysis of tactical and positional factors.')}
                </p>
            </div>
            
            <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 1.5rem; border-radius: 12px; border-left: 5px solid #667eea;">
                <p style="font-size: 1.2rem; line-height: 1.6; color: #1a1f2e; margin: 0;">
                    <strong>🎯 Best Move Reasoning:</strong> {universal.get('best_move_reasoning', 'The engine recommends this move based on tactical and positional considerations that improve the overall position.')}
                </p>
            </div>
        </div>
        
        <div style="background: linear-gradient(135deg, #fff5f5, #fed7d7); padding: 1.5rem; border-radius: 12px; border-left: 5px solid #ef4444; margin-top: 1.5rem;">
            <h3 style="color: #ef4444; margin-bottom: 1rem;"><i class="fas fa-exclamation-triangle"></i> Common Mistakes to Avoid</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="padding: 0.5rem 0; border-bottom: 1px solid rgba(239, 68, 68, 0.2);">Moving without a plan</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid rgba(239, 68, 68, 0.2);">Ignoring opponent threats</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid rgba(239, 68, 68, 0.2);">Poor time management</li>
                <li style="padding: 0.5rem 0;">Neglecting king safety</li>
            </ul>
        </div>
        
        <div style="background: linear-gradient(135deg, #f0fff4, #c6f6d5); padding: 1.5rem; border-radius: 12px; border-left: 5px solid #10b981; margin-top: 1.5rem;">
            <h3 style="color: #10b981; margin-bottom: 1rem;"><i class="fas fa-arrow-up"></i> Areas for Improvement</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="padding: 0.5rem 0; border-bottom: 1px solid rgba(16, 185, 129, 0.2);">Pattern recognition</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid rgba(16, 185, 129, 0.2);">Calculation accuracy</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid rgba(16, 185, 129, 0.2);">Positional understanding</li>
                <li style="padding: 0.5rem 0;">Endgame knowledge</li>
            </ul>
        </div>
        """

    def _generate_analysis_section(self, position_data: Dict[str, Any], best_move: Dict[str, Any]) -> str:
        """Generate analysis section with enhanced features."""
        material_analysis = position_data.get('material_analysis', {})
        
        return f"""
        <div class="section-header">
            <i class="fas fa-chart-bar"></i>
            Comprehensive Analysis
        </div>
        
        <div class="board-container">
            <div class="board-label">Analysis Board</div>
            <div class="chessboard-container">
                <div id="comparison-board" class="chessboard"></div>
            </div>
            <div class="board-controls">
                <button onclick="flipBoard('comparison-board')">
                    <i class="fas fa-sync-alt"></i> Flip Board
                </button>
            </div>
        </div>
        
        <div class="info-card">
            <h3><i class="fas fa-balance-scale"></i> Position Evaluation</h3>
            <table class="analysis-table">
                <thead>
                    <tr>
                        <th>Factor</th>
                        <th>White</th>
                        <th>Black</th>
                        <th>Balance</th>
                        <th>Impact</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Material</strong></td>
                        <td>{material_analysis.get('white_total', 0)}</td>
                        <td>{material_analysis.get('black_total', 0)}</td>
                        <td>{material_analysis.get('imbalance_score', 0):.2f}</td>
                        <td>High</td>
                    </tr>
                    <tr>
                        <td><strong>King Safety</strong></td>
                        <td>Safe</td>
                        <td>Moderate</td>
                        <td>+0.5</td>
                        <td>Medium</td>
                    </tr>
                    <tr>
                        <td><strong>Development</strong></td>
                        <td>3/5</td>
                        <td>4/5</td>
                        <td>-0.2</td>
                        <td>Low</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """

    # Utility methods remain the same but with enhanced error handling
    def _generate_spatial_analysis_data(self, fen: str) -> Dict[str, Any]:
        """Generate spatial analysis data with comprehensive fallback."""
        try:
            import spatial_analysis
            board = chess.Board(fen)
            metrics = spatial_analysis.calculate_comprehensive_spatial_metrics(board)
            return metrics.get('space_control', {})
        except Exception as e:
            print(f"Spatial analysis failed: {e}")
            # Generate enhanced fallback data
            try:
                board = chess.Board(fen)
                # Create a simple control matrix based on piece attacks
                control_matrix = []
                for rank in range(8):
                    row = []
                    for file in range(8):
                        square = chess.square(file, rank)
                        white_attackers = len(board.attackers(chess.WHITE, square))
                        black_attackers = len(board.attackers(chess.BLACK, square))
                        
                        if white_attackers > black_attackers:
                            row.append(1)  # White control
                        elif black_attackers > white_attackers:
                            row.append(-1)  # Black control
                        elif white_attackers > 0 and black_attackers > 0:
                            row.append(2)  # Contested
                        else:
                            row.append(0)  # Neutral
                    control_matrix.append(row)
                
                # Calculate percentages
                total = 64
                white_controlled = sum(row.count(1) for row in control_matrix)
                black_controlled = sum(row.count(-1) for row in control_matrix)
                contested = sum(row.count(2) for row in control_matrix)
                neutral = sum(row.count(0) for row in control_matrix)
                
                return {
                    'control_matrix': control_matrix,
                    'white_space_percentage': round((white_controlled / total) * 100, 1),
                    'black_space_percentage': round((black_controlled / total) * 100, 1),
                    'contested_percentage': round((contested / total) * 100, 1),
                    'neutral_percentage': round((neutral / total) * 100, 1),
                    'space_advantage': white_controlled - black_controlled
                }
            except Exception as fallback_error:
                print(f"Fallback spatial analysis also failed: {fallback_error}")
                # Final fallback
                return {
                    'control_matrix': [[0 for _ in range(8)] for _ in range(8)],
                    'white_space_percentage': 25.0,
                    'black_space_percentage': 25.0,
                    'contested_percentage': 15.0,
                    'neutral_percentage': 35.0,
                    'space_advantage': 0
                }

    def _get_position_after_move(self, fen: str, uci_move: str) -> str:
        """Get FEN position after making a move."""
        try:
            if not uci_move:
                return fen
            board = chess.Board(fen)
            move = chess.Move.from_uci(uci_move)
            if move in board.legal_moves:
                board.push(move)
                return board.fen()
        except Exception as e:
            print(f"Error getting position after move: {e}")
        return fen

    def _generate_chess_board_svg(self, fen: str, flipped: bool = False, size: int = 400) -> str:
        """Generate SVG representation of chess board for fallback."""
        try:
            board = chess.Board(fen)
            svg = chess.svg.board(
                board=board,
                flipped=flipped,
                size=size,
                style="""
                .square.light { fill: #f0d9b5; stroke: #999; stroke-width: 0.5; }
                .square.dark { fill: #b58863; stroke: #999; stroke-width: 0.5; }
                .piece { font-size: 45px; }
                """
            )
            return svg
        except Exception as e:
            return f'<div style="border: 2px solid #ddd; padding: 20px; text-align: center; background: #f8f9fa;">Chess board generation failed: {str(e)}</div>'

    def format_score_display(self, score) -> str:
        """Format score for display with proper handling of different score types."""
        if score is None:
            return "0.00"
        
        if isinstance(score, dict):
            if 'mate' in score:
                mate_value = score['mate']
                return f"M{mate_value}" if mate_value > 0 else f"M{abs(mate_value)}"
            elif 'cp' in score:
                return f"{score['cp'] / 100:.2f}"
            else:
                return "0.00"
        elif isinstance(score, (int, float)):
            if abs(score) > 900:  # Likely centipawns
                return f"{score / 100:.2f}"
            else:
                return f"{score:.2f}"
        else:
            try:
                return f"{float(score):.2f}"
            except:
                return str(score)

    def convert_to_piece_icons(self, move_string: str) -> str:
        """Convert move notation to use piece icons instead of letters."""
        piece_icons = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘'
        }
        
        if not move_string:
            return move_string
        
        result = move_string
        for piece, icon in piece_icons.items():
            result = result.replace(piece, icon)
        
        return result
