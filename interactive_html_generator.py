# interactive_html_generator.py - Interactive HTML Template Generator
import os
import re
import json
import chess
import chess.svg
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

class InteractiveHTMLGenerator:
    """Enhanced mobile-first interactive chess analyzer with superior UX for learning."""
    
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
        """Generate the epic interactive chess analysis report - ENTRY POINT."""
        return self.generate_comprehensive_strategic_analysis(
            position_data=position_data,
            selected_move_data=selected_move_data
        )
    
    def generate_comprehensive_strategic_analysis(self, position_data: Dict[str, Any], 
                                                selected_move_data: Dict[str, Any] = None,
                                                **kwargs) -> str:
        """Generate comprehensive mobile-first interactive chess position analysis."""
        
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
        
        # Generate comprehensive HTML with mobile-first design
        html_content = self._generate_mobile_first_html_template(
            position_data, selected_move_data, top_moves, fen, result_fen, 
            current_spatial_data, result_spatial_data
        )
        
        # Save and return path
        timestamp = int(datetime.now().timestamp())
        filename = f"mobile_chess_analyzer_{position_id}_{timestamp}.html"
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

    def _generate_mobile_first_html_template(self, position_data: Dict[str, Any], 
                                           selected_move_data: Dict[str, Any], 
                                           top_moves: List[Dict], 
                                           current_fen: str, 
                                           result_fen: str,
                                           current_spatial_data: Dict[str, Any],
                                           result_spatial_data: Dict[str, Any]) -> str:
        """Generate mobile-first HTML template with enhanced UX for learning."""
        
        position_id = position_data.get('id', 'unknown')
        turn = position_data.get('turn', 'white')
        move_number = position_data.get('fullmove_number', 1)
        best_move = top_moves[0] if top_moves else {}
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Chess Learning Lab - Position {position_id}</title>
    
    <!-- External Libraries -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://unpkg.com/chess.js@1.0.0-alpha.0/chess.min.js"></script>
    <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Hammer.js for touch gestures -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.min.js"></script>
    
    <style>
        {self._generate_mobile_first_css()}
    </style>
</head>
<body>
    <div id="app" class="app-container">
        <!-- Mobile Header -->
        <header class="mobile-header">
            <div class="header-content">
                <div class="header-top">
                    <h1><i class="fas fa-chess"></i> Chess Learning Lab</h1>
                    <div class="position-badge">#{position_id}</div>
                </div>
                <div class="header-info">
                    <span class="move-info">Move {move_number} • {turn.title()} to play</span>
                    <div class="difficulty-badge">
                        <i class="fas fa-star"></i> {position_data.get('difficulty_rating', 1200)}
                    </div>
                </div>
            </div>
        </header>

        <!-- Learning Progress Bar -->
        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-fill" id="learning-progress"></div>
            </div>
            <div class="progress-steps">
                <span class="step active" data-step="problem">🧩</span>
                <span class="step" data-step="solution">💡</span>
                <span class="step" data-step="analysis">📊</span>
                <span class="step" data-step="variations">🔀</span>
            </div>
        </div>

        <!-- Mobile Navigation -->
        <nav class="mobile-nav">
            <div class="nav-slider" id="nav-slider">
                <button class="nav-btn active" data-section="problem">
                    <i class="fas fa-puzzle-piece"></i>
                    <span>Problem</span>
                </button>
                <button class="nav-btn" data-section="solution">
                    <i class="fas fa-lightbulb"></i>
                    <span>Solution</span>
                </button>
                <button class="nav-btn" data-section="analysis">
                    <i class="fas fa-chart-bar"></i>
                    <span>Analysis</span>
                </button>
                <button class="nav-btn" data-section="moves">
                    <i class="fas fa-list-ol"></i>
                    <span>Moves</span>
                </button>
                <button class="nav-btn" data-section="spatial">
                    <i class="fas fa-map"></i>
                    <span>Spatial</span>
                </button>
                <button class="nav-btn" data-section="variations">
                    <i class="fas fa-code-branch"></i>
                    <span>Variations</span>
                </button>
            </div>
        </nav>

        <!-- Main Content Container -->
        <main class="main-content">
            
            <!-- Problem Section: Learn by Solving -->
            <section id="problem-section" class="content-section active">
                {self._generate_mobile_problem_section(position_data, current_fen)}
            </section>

            <!-- Solution Section: Reveal and Learn -->
            <section id="solution-section" class="content-section">
                {self._generate_mobile_solution_section(position_data, best_move, current_fen, result_fen)}
            </section>

            <!-- Analysis Section: Deep Dive -->
            <section id="analysis-section" class="content-section">
                {self._generate_mobile_analysis_section(position_data, best_move)}
            </section>

            <!-- Top Moves Section: Compare Options -->
            <section id="moves-section" class="content-section">
                {self._generate_mobile_moves_section(top_moves, current_fen)}
            </section>

            <!-- Spatial Analysis: Territory Control -->
            <section id="spatial-section" class="content-section">
                {self._generate_mobile_spatial_section(current_fen, result_fen, current_spatial_data, result_spatial_data, best_move)}
            </section>

            <!-- Variations: What If Analysis -->
            <section id="variations-section" class="content-section">
                {self._generate_mobile_variations_section(position_data, current_fen)}
            </section>

        </main>

        <!-- Floating Action Button -->
        <div class="fab-container">
            <button class="fab" id="main-fab">
                <i class="fas fa-chess-board"></i>
            </button>
            <div class="fab-menu" id="fab-menu">
                <button class="fab-item" onclick="flipAllBoards()">
                    <i class="fas fa-sync-alt"></i>
                </button>
                <button class="fab-item" onclick="resetToStart()">
                    <i class="fas fa-home"></i>
                </button>
                <button class="fab-item" onclick="toggleFullscreen()">
                    <i class="fas fa-expand"></i>
                </button>
                <button class="fab-item" onclick="showHints()">
                    <i class="fas fa-question"></i>
                </button>
            </div>
        </div>

        <!-- SVG Board Fallbacks -->
        <div id="svg-boards" style="display: none;">
            <div id="svg-current-board">{self._generate_chess_board_svg(current_fen, False, 350)}</div>
            <div id="svg-result-board">{self._generate_chess_board_svg(result_fen or current_fen, False, 350)}</div>
        </div>

        <!-- Mobile Learning Footer -->
        <footer class="mobile-footer">
            <div class="footer-content">
                <p><i class="fas fa-brain"></i> Generated by Chess Learning Lab • {current_time}</p>
                <div class="footer-stats">
                    <span><i class="fas fa-chess-pawn"></i> {len(top_moves)} moves analyzed</span>
                    <span><i class="fas fa-map"></i> Spatial analysis included</span>
                </div>
            </div>
        </footer>
    </div>

    <!-- Touch/Swipe Overlay -->
    <div class="touch-overlay" id="touch-overlay"></div>

    <script>
        {self._generate_mobile_javascript(current_fen, result_fen, top_moves, current_spatial_data, result_spatial_data)}
    </script>
</body>
</html>"""
        
        return html_template

    def _generate_mobile_first_css(self) -> str:
        """Generate mobile-first CSS with touch-friendly design."""
        return """
        /* === MOBILE-FIRST RESET & BASE === */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        html {
            font-size: 16px;
            scroll-behavior: smooth;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
            line-height: 1.5;
            color: #1a202c;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* === APP CONTAINER === */
        .app-container {
            min-height: 100vh;
            background: #ffffff;
            position: relative;
            max-width: 100%;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
        }

        /* === MOBILE HEADER === */
        .mobile-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }

        .header-content {
            max-width: 100%;
        }

        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }

        .header-top h1 {
            font-size: 1.25rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .position-badge {
            background: rgba(255,255,255,0.2);
            padding: 0.375rem 0.75rem;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 600;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.3);
        }

        .header-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.875rem;
        }

        .difficulty-badge {
            background: rgba(255,215,0,0.9);
            color: #1a202c;
            padding: 0.25rem 0.75rem;
            border-radius: 10px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }

        /* === LEARNING PROGRESS === */
        .progress-container {
            background: white;
            padding: 1rem;
            border-bottom: 1px solid #e2e8f0;
        }

        .progress-bar {
            width: 100%;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 1rem;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #34d399);
            width: 25%;
            transition: width 0.5s ease;
            border-radius: 3px;
        }

        .progress-steps {
            display: flex;
            justify-content: space-between;
            padding: 0 0.5rem;
        }

        .step {
            font-size: 1.25rem;
            padding: 0.5rem;
            border-radius: 50%;
            background: #f7fafc;
            border: 2px solid #e2e8f0;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .step.active {
            background: #10b981;
            border-color: #10b981;
            color: white;
            transform: scale(1.1);
        }

        /* === MOBILE NAVIGATION === */
        .mobile-nav {
            background: white;
            border-bottom: 1px solid #e2e8f0;
            overflow-x: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
            position: sticky;
            top: calc(100px + 1rem);
            z-index: 90;
        }

        .mobile-nav::-webkit-scrollbar {
            display: none;
        }

        .nav-slider {
            display: flex;
            gap: 0.5rem;
            padding: 1rem;
            min-width: max-content;
        }

        .nav-btn {
            background: #f7fafc;
            border: 2px solid #e2e8f0;
            color: #4a5568;
            padding: 0.75rem 1rem;
            border-radius: 12px;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 600;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.25rem;
            min-width: 70px;
            white-space: nowrap;
        }

        .nav-btn i {
            font-size: 1.1rem;
        }

        .nav-btn span {
            font-size: 0.75rem;
        }

        .nav-btn:hover, .nav-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        /* === MAIN CONTENT === */
        .main-content {
            flex: 1;
            padding: 1rem;
            max-width: 100%;
            background: #f7fafc;
        }

        .content-section {
            display: none;
            animation: slideInUp 0.4s ease-out;
        }

        .content-section.active {
            display: block;
        }

        @keyframes slideInUp {
            from { 
                opacity: 0; 
                transform: translateY(20px); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }

        /* === MOBILE CARDS === */
        .mobile-card {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .mobile-card:active {
            transform: scale(0.98);
        }

        .mobile-card h3 {
            color: #1a202c;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.1rem;
            font-weight: 700;
        }

        .mobile-card h3 i {
            color: #667eea;
            font-size: 1.2rem;
        }

        /* === BOARD CONTAINERS === */
        .board-container {
            background: white;
            border-radius: 16px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
        }

        .board-label {
            text-align: center;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 1rem;
            font-size: 1rem;
            padding: 0.75rem;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border-radius: 12px;
            border: 2px solid rgba(102, 126, 234, 0.2);
        }

        .board-wrapper {
            display: flex;
            justify-content: center;
            margin: 1rem 0;
            touch-action: manipulation;
        }

        .chessboard {
            max-width: 100%;
            width: 100%;
            max-width: min(90vw, 400px);
            border: 3px solid #667eea;
            border-radius: 8px;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25);
            touch-action: manipulation;
        }

        /* === SIDE BY SIDE LAYOUT === */
        .side-by-side {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin: 1rem 0;
        }

        .comparison-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1rem;
            margin: 1rem 0;
        }

        /* === METRICS GRID === */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 0.75rem;
            margin: 1rem 0;
        }

        .metric-card {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(102, 126, 234, 0.1);
            border-top: 3px solid #667eea;
            transition: all 0.2s ease;
        }

        .metric-card:active {
            transform: scale(0.95);
        }

        .metric-label {
            font-size: 0.75rem;
            color: #64748b;
            font-weight: 600;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-size: 1.25rem;
            font-weight: 800;
            color: #1a202c;
        }

        /* === MOBILE TABLES === */
        .mobile-table {
            width: 100%;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            margin: 1rem 0;
        }

        .table-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            font-weight: 700;
            text-align: center;
        }

        .table-row {
            padding: 1rem;
            border-bottom: 1px solid #e2e8f0;
            transition: background-color 0.2s ease;
            cursor: pointer;
            touch-action: manipulation;
        }

        .table-row:active {
            background: rgba(102, 126, 234, 0.1);
        }

        .table-row:last-child {
            border-bottom: none;
        }

        .row-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }

        .row-details {
            font-size: 0.875rem;
            color: #64748b;
            line-height: 1.4;
        }

        /* === SPATIAL VISUALIZATION === */
        .spatial-container {
            background: white;
            border-radius: 16px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }

        .spatial-grid {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 1px;
            max-width: min(90vw, 350px);
            margin: 0 auto;
            aspect-ratio: 1;
            border: 3px solid #667eea;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
        }

        .spatial-square {
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            transition: all 0.2s ease;
            cursor: pointer;
            font-size: 0.9rem;
            touch-action: manipulation;
        }

        .spatial-square:active {
            transform: scale(1.1);
            z-index: 10;
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
            margin-top: 1rem;
            font-size: 0.75rem;
            color: #1a202c;
            font-weight: 600;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .spatial-legend div {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 0.75rem;
            background: #f7fafc;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }

        /* === FLOATING ACTION BUTTON === */
        .fab-container {
            position: fixed;
            bottom: 1rem;
            right: 1rem;
            z-index: 1000;
        }

        .fab {
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .fab:active {
            transform: scale(0.9);
        }

        .fab-menu {
            position: absolute;
            bottom: 70px;
            right: 0;
            display: none;
            flex-direction: column;
            gap: 0.5rem;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
        }

        .fab-menu.show {
            display: flex;
            opacity: 1;
            transform: translateY(0);
        }

        .fab-item {
            width: 48px;
            height: 48px;
            background: white;
            border: 2px solid #667eea;
            border-radius: 50%;
            color: #667eea;
            font-size: 1.2rem;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .fab-item:active {
            transform: scale(0.9);
            background: #667eea;
            color: white;
        }

        /* === MOBILE FOOTER === */
        .mobile-footer {
            background: #f7fafc;
            border-top: 1px solid #e2e8f0;
            padding: 1rem;
            text-align: center;
            margin-top: 2rem;
        }

        .footer-content p {
            color: #64748b;
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }

        .footer-stats {
            display: flex;
            justify-content: center;
            gap: 1rem;
            font-size: 0.75rem;
            color: #64748b;
            flex-wrap: wrap;
        }

        /* === TOUCH OVERLAY === */
        .touch-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 2000;
            display: none;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .touch-overlay.show {
            display: block;
            opacity: 1;
        }

        /* === ENHANCED MOVE NOTATION === */
        .enhanced-move {
            font-family: 'SF Mono', 'Monaco', monospace;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-weight: 600;
            line-height: 1.6;
            font-size: 0.9rem;
            box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
            margin: 0.5rem 0;
            touch-action: manipulation;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .enhanced-move:active {
            transform: scale(0.98);
        }

        .clickable-move {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 0.5rem 0.75rem;
            margin: 0.25rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: 600;
            font-size: 0.875rem;
            touch-action: manipulation;
        }

        .clickable-move:active {
            transform: scale(0.95);
            background: #764ba2;
        }

        .clickable-move.best-move {
            background: #10b981;
        }

        .clickable-move.best-move:active {
            background: #059669;
        }

        /* === TAGS === */
        .tag {
            display: inline-block;
            background: linear-gradient(135deg, #ddd6fe 0%, #c4b5fd 100%);
            color: #5b21b6;
            padding: 0.5rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 0.25rem;
            border: 1px solid #8b5cf6;
            transition: all 0.2s ease;
        }

        .tag:active {
            transform: scale(0.95);
        }

        /* === RESPONSIVE BREAKPOINTS === */
        @media (min-width: 768px) {
            .app-container {
                max-width: 768px;
                margin: 1rem auto;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            
            .side-by-side {
                flex-direction: row;
                gap: 1.5rem;
            }
            
            .comparison-container {
                grid-template-columns: 1fr 1fr;
                gap: 1.5rem;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 1rem;
            }
            
            .mobile-nav {
                position: relative;
                top: 0;
            }
            
            .nav-slider {
                justify-content: center;
                padding: 1.5rem;
            }
            
            .nav-btn {
                min-width: 80px;
                padding: 1rem 1.25rem;
            }
        }

        @media (min-width: 1024px) {
            .app-container {
                max-width: 1024px;
            }
            
            .comparison-container {
                grid-template-columns: 1fr 1fr 1fr;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            }
        }

        /* === SCORE STYLING === */
        .score-positive { color: #10b981; font-weight: 700; }
        .score-negative { color: #ef4444; font-weight: 700; }
        .score-neutral { color: #6b7280; font-weight: 700; }

        /* === UTILITY CLASSES === */
        .text-center { text-align: center; }
        .mb-1 { margin-bottom: 0.5rem; }
        .mb-2 { margin-bottom: 1rem; }
        .mt-1 { margin-top: 0.5rem; }
        .mt-2 { margin-top: 1rem; }
        .font-bold { font-weight: 700; }
        .text-sm { font-size: 0.875rem; }
        .text-xs { font-size: 0.75rem; }
        """

    def _generate_mobile_javascript(self, current_fen: str, result_fen: str, 
                                  top_moves: List[Dict], current_spatial_data: Dict[str, Any], 
                                  result_spatial_data: Dict[str, Any]) -> str:
        """Generate mobile-optimized JavaScript with touch gestures."""
        
        # Convert numpy types safely
        top_moves_clean = self._convert_numpy_types(top_moves)
        current_spatial_clean = self._convert_numpy_types(current_spatial_data)
        result_spatial_clean = self._convert_numpy_types(result_spatial_data)
        
        for move in top_moves_clean:
            if not move.get('pv') and move.get('principal_variation'):
                move['pv'] = move['principal_variation']
            elif not move.get('pv'):
                move['pv'] = move.get('move', '')
        
        top_moves_json = json.dumps(top_moves_clean)
        current_spatial_json = json.dumps(current_spatial_clean)
        result_spatial_json = json.dumps(result_spatial_clean)
        
        js_code = f"""
        // Global variables for mobile chess analyzer
        let boards = {{}};
        let variationBoards = {{}};
        let currentFen = '{current_fen}';
        let resultFen = '{result_fen}';
        let topMoves = {top_moves_json};
        let currentSpatialData = {current_spatial_json};
        let resultSpatialData = {result_spatial_json};
        let globalOrientation = 'white';
        let usingSVGFallback = false;
        let currentSection = 'problem';
        let learningProgress = 25;
        let fabOpen = false;

        // Initialize mobile chess analyzer
        $(document).ready(function() {{
            console.log('Initializing Mobile Chess Learning Lab...');
            
            // Check libraries and initialize
            if (typeof Chessboard === 'undefined' || typeof Chess === 'undefined') {{
                console.warn('Chess libraries not loaded, using SVG fallback');
                usingSVGFallback = true;
                initializeSVGBoards();
            }} else {{
                setTimeout(initializeInteractiveBoards, 200);
            }}
            
            // Initialize mobile features
            setTimeout(function() {{
                initializeMobileNavigation();
                initializeTouchGestures();
                initializeSpatialVisualization();
                initializeMoveAnalysis();
                initializeFAB();
                updateLearningProgress();
            }}, 400);
        }});

        // MOBILE NAVIGATION SYSTEM
        function initializeMobileNavigation() {{
            console.log('Initializing mobile navigation...');
            
            // Navigation button handlers
            document.querySelectorAll('.nav-btn').forEach(btn => {{
                btn.addEventListener('click', function() {{
                    const section = this.getAttribute('data-section');
                    showMobileSection(section);
                }});
            }});
            
            // Progress step handlers
            document.querySelectorAll('.step').forEach(step => {{
                step.addEventListener('click', function() {{
                    const stepType = this.getAttribute('data-step');
                    showMobileSection(stepType);
                }});
            }});
        }}

        function showMobileSection(sectionName) {{
            try {{
                console.log('Showing mobile section:', sectionName);
                
                // Hide all sections
                document.querySelectorAll('.content-section').forEach(section => {{
                    section.classList.remove('active');
                }});

                // Show target section
                const targetSection = document.getElementById(sectionName + '-section');
                if (targetSection) {{
                    setTimeout(() => {{
                        targetSection.classList.add('active');
                    }}, 100);
                }}

                // Update navigation
                document.querySelectorAll('.nav-btn').forEach(nav => {{
                    nav.classList.remove('active');
                }});
                
                document.querySelector(`[data-section="${{sectionName}}"]`)?.classList.add('active');
                
                // Update progress steps
                document.querySelectorAll('.step').forEach(step => {{
                    step.classList.remove('active');
                }});
                
                document.querySelector(`[data-step="${{sectionName}}"]`)?.classList.add('active');

                // Update learning progress
                currentSection = sectionName;
                updateLearningProgress();

                // Resize boards after section change
                if (!usingSVGFallback) {{
                    setTimeout(resizeAllBoards, 300);
                }}

                // Section-specific initialization
                if (sectionName === 'spatial') {{
                    setTimeout(initializeSpatialVisualization, 300);
                }} else if (sectionName === 'variations') {{
                    setTimeout(initializeVariationBoards, 300);
                }}
                
                // Smooth scroll to top
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
                
            }} catch (e) {{
                console.error('Error showing mobile section:', e);
            }}
        }}

        function updateLearningProgress() {{
            const progressMap = {{
                'problem': 25,
                'solution': 50,
                'analysis': 75,
                'moves': 85,
                'spatial': 90,
                'variations': 100
            }};
            
            learningProgress = progressMap[currentSection] || 25;
            
            const progressFill = document.getElementById('learning-progress');
            if (progressFill) {{
                progressFill.style.width = learningProgress + '%';
            }}
        }}

        // TOUCH GESTURE SUPPORT
        function initializeTouchGestures() {{
            try {{
                if (typeof Hammer !== 'undefined') {{
                    const mainContent = document.querySelector('.main-content');
                    if (mainContent) {{
                        const hammer = new Hammer(mainContent);
                        
                        // Enable swipe gestures
                        hammer.get('swipe').set({{ direction: Hammer.DIRECTION_HORIZONTAL }});
                        
                        hammer.on('swipeleft', function() {{
                            navigateNext();
                        }});
                        
                        hammer.on('swiperight', function() {{
                            navigatePrevious();
                        }});
                        
                        console.log('Touch gestures initialized');
                    }}
                }} else {{
                    console.warn('Hammer.js not available, touch gestures disabled');
                }}
            }} catch (e) {{
                console.error('Error initializing touch gestures:', e);
            }}
        }}

        function navigateNext() {{
            const sections = ['problem', 'solution', 'analysis', 'moves', 'spatial', 'variations'];
            const currentIndex = sections.indexOf(currentSection);
            if (currentIndex < sections.length - 1) {{
                showMobileSection(sections[currentIndex + 1]);
            }}
        }}

        function navigatePrevious() {{
            const sections = ['problem', 'solution', 'analysis', 'moves', 'spatial', 'variations'];
            const currentIndex = sections.indexOf(currentSection);
            if (currentIndex > 0) {{
                showMobileSection(sections[currentIndex - 1]);
            }}
        }}

        // INTERACTIVE BOARD INITIALIZATION
        function initializeInteractiveBoards() {{
            try {{
                console.log('Initializing mobile-optimized chess boards...');
                
                const config = {{
                    position: currentFen,
                    orientation: globalOrientation,
                    draggable: false,
                    showNotation: true,
                    pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{{piece}}.png'
                }};

                const boardConfigs = [
                    {{ id: 'problem-board', fen: currentFen }},
                    {{ id: 'solution-current-board', fen: currentFen }},
                    {{ id: 'solution-result-board', fen: resultFen }},
                    {{ id: 'analysis-board', fen: currentFen }},
                    {{ id: 'moves-board', fen: currentFen }},
                    {{ id: 'spatial-current-board', fen: currentFen }},
                    {{ id: 'spatial-result-board', fen: resultFen }},
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
                            console.log('Initialized mobile board:', boardConfig.id);
                            
                            // Set position after initialization
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

        // SVG FALLBACK SYSTEM
        function initializeSVGBoards() {{
            console.log('Initializing mobile SVG fallback boards...');
            
            const boardContainers = document.querySelectorAll('.board-wrapper');
            boardContainers.forEach((container) => {{
                const boardElement = container.querySelector('[id*="board"]');
                if (boardElement) {{
                    const boardId = boardElement.id;
                    let svgContent = '';
                    
                    if (boardId && boardId.includes('result')) {{
                        svgContent = document.getElementById('svg-result-board').innerHTML;
                    }} else {{
                        svgContent = document.getElementById('svg-current-board').innerHTML;
                    }}
                    
                    if (svgContent) {{
                        boardElement.innerHTML = svgContent;
                        boardElement.className = 'chessboard svg-board';
                        console.log('SVG board added to:', boardId);
                    }}
                }}
            }});
        }}

        // SPATIAL ANALYSIS SYSTEM
        function initializeSpatialVisualization() {{
            try {{
                console.log('Initializing mobile spatial visualization...');
                
                initializeSingleSpatialBoard('spatial-current-grid', currentSpatialData, 'Current Position');
                
                if (resultSpatialData && JSON.stringify(resultSpatialData) !== JSON.stringify(currentSpatialData)) {{
                    initializeSingleSpatialBoard('spatial-result-grid', resultSpatialData, 'After Best Move');
                }}
                
                console.log('Mobile spatial visualization initialized');
            }} catch (e) {{
                console.error('Error initializing mobile spatial visualization:', e);
            }}
        }}

        function initializeSingleSpatialBoard(boardId, spatialData, title) {{
            try {{
                const spatialGrid = document.getElementById(boardId);
                if (!spatialGrid || !spatialData || !spatialData.control_matrix) {{
                    console.warn(`Spatial data not available for ${{boardId}}`);
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
                            
                            // Touch-friendly click handler
                            square.addEventListener('click', function() {{
                                showMobileSquareInfo(file, rank, controlValue, title);
                            }});
                        }} else {{
                            const isLight = (rank + file) % 2 === 0;
                            square.classList.add('neutral', isLight ? 'light' : 'dark');
                        }}
                        
                        spatialGrid.appendChild(square);
                    }}
                }}
                
                console.log(`Mobile spatial board initialized: ${{boardId}}`);
            }} catch (e) {{
                console.error(`Error initializing spatial board ${{boardId}}:`, e);
            }}
        }}

        function showMobileSquareInfo(file, rank, controlValue, boardTitle) {{
            try {{
                const squareName = String.fromCharCode(97 + file) + (rank + 1);
                let controlText = 'Neutral';
                let emoji = '⬜';
                
                if (controlValue === 1) {{
                    controlText = 'White Control';
                    emoji = '♔';
                }} else if (controlValue === -1) {{
                    controlText = 'Black Control';
                    emoji = '♚';
                }} else if (controlValue === 2) {{
                    controlText = 'Contested';
                    emoji = '⚡';
                }}
                
                // Create mobile-friendly notification
                showMobileNotification(`${{emoji}} ${{squareName}}: ${{controlText}}`, 2000);
            }} catch (e) {{
                console.error('Error showing square info:', e);
            }}
        }}

        // MOVE ANALYSIS SYSTEM
        function initializeMoveAnalysis() {{
            try {{
                console.log('Initializing mobile move analysis...');
                
                // Make move rows clickable
                document.querySelectorAll('.table-row').forEach((row, index) => {{
                    row.addEventListener('click', function() {{
                        showMoveOnMobileBoard(index + 1);
                        this.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
                        
                        // Reset other rows
                        document.querySelectorAll('.table-row').forEach(r => {{
                            if (r !== this) r.style.backgroundColor = '';
                        }});
                    }});
                }});
                
                // Make clickable moves work
                document.querySelectorAll('.clickable-move').forEach(moveElement => {{
                    moveElement.addEventListener('click', function() {{
                        const moveNotation = this.getAttribute('data-move');
                        const moveFen = this.getAttribute('data-fen');
                        if (moveNotation && moveFen) {{
                            loadPositionOnMobileBoard('moves-board', moveFen, moveNotation);
                        }}
                    }});
                }});
                
                console.log('Mobile move analysis initialized');
            }} catch (e) {{
                console.error('Error initializing mobile move analysis:', e);
            }}
        }}

        function showMoveOnMobileBoard(moveIndex) {{
            try {{
                if (!topMoves[moveIndex - 1]) {{
                    console.warn('Move not found for index:', moveIndex);
                    return;
                }}
                
                const move = topMoves[moveIndex - 1];
                const moveUci = move.uci || '';
                
                console.log('Showing move on mobile board:', move.move, 'Index:', moveIndex);
                
                // Load position on board
                if (!usingSVGFallback && boards['moves-board']) {{
                    boards['moves-board'].position(currentFen);
                    
                    if (moveUci && moveUci.length >= 4) {{
                        const fromSquare = moveUci.substring(0, 2);
                        const toSquare = moveUci.substring(2, 4);
                        
                        setTimeout(() => {{
                            highlightMoveOnBoard('moves-board', fromSquare, toSquare);
                        }}, 100);
                    }}
                }}
                
                // Show mobile notification
                showMobileNotification(`Move #${{moveIndex}}: ${{convertToPieceIcons(move.move)}} (${{formatScore(move.score)}})`, 3000);
                
            }} catch (e) {{
                console.error('Error showing move on mobile board:', e);
            }}
        }}

        function loadPositionOnMobileBoard(boardId, fen, moveDescription) {{
            try {{
                if (!usingSVGFallback && boards[boardId]) {{
                    boards[boardId].position(fen);
                    console.log(`Loaded position on mobile board ${{boardId}} for move: ${{moveDescription}}`);
                    
                    showMobileNotification(`Loaded: ${{convertToPieceIcons(moveDescription)}}`, 2000);
                }}
            }} catch (e) {{
                console.error('Error loading position on mobile board:', e);
            }}
        }}

        // VARIATION ANALYSIS SYSTEM
        function initializeVariationBoards() {{
            try {{
                if (usingSVGFallback) {{
                    console.log('Variation boards not available in SVG mode');
                    return;
                }}
                
                console.log('Initializing mobile variation boards...');
                
                // Clear existing boards
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
                
                // Initialize top 3 variations
                topMoves.slice(0, 3).forEach((move, index) => {{
                    const boardId = `variation-board-${{index + 1}}`;
                    const element = document.getElementById(boardId);
                    
                    if (element && typeof Chessboard !== 'undefined') {{
                        try {{
                            const variationFen = calculateVariationPosition(currentFen, move.pv || move.principal_variation || move.move);
                            
                            const config = {{
                                position: variationFen,
                                orientation: globalOrientation,
                                draggable: false,
                                showNotation: false,
                                pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{{piece}}.png'
                            }};
                            
                            variationBoards[boardId] = Chessboard(boardId, config);
                            console.log('Initialized mobile variation board:', boardId);
                            
                        }} catch (e) {{
                            console.error('Failed to initialize variation board:', boardId, e);
                        }}
                    }}
                }});
                
                console.log('Mobile variation boards initialized');
            }} catch (e) {{
                console.error('Error initializing mobile variation boards:', e);
            }}
        }}

        // FLOATING ACTION BUTTON SYSTEM
        function initializeFAB() {{
            try {{
                const fab = document.getElementById('main-fab');
                const fabMenu = document.getElementById('fab-menu');
                
                if (fab && fabMenu) {{
                    fab.addEventListener('click', function() {{
                        toggleFAB();
                    }});
                    
                    // Close FAB when clicking outside
                    document.addEventListener('click', function(e) {{
                        if (!fab.contains(e.target) && !fabMenu.contains(e.target)) {{
                            closeFAB();
                        }}
                    }});
                }}
                
                console.log('FAB initialized');
            }} catch (e) {{
                console.error('Error initializing FAB:', e);
            }}
        }}

        function toggleFAB() {{
            const fabMenu = document.getElementById('fab-menu');
            const overlay = document.getElementById('touch-overlay');
            
            fabOpen = !fabOpen;
            
            if (fabOpen) {{
                fabMenu.classList.add('show');
                overlay.classList.add('show');
            }} else {{
                fabMenu.classList.remove('show');
                overlay.classList.remove('show');
            }}
        }}

        function closeFAB() {{
            const fabMenu = document.getElementById('fab-menu');
            const overlay = document.getElementById('touch-overlay');
            
            fabOpen = false;
            fabMenu.classList.remove('show');
            overlay.classList.remove('show');
        }}

        // UTILITY FUNCTIONS
        function flipAllBoards() {{
            try {{
                globalOrientation = globalOrientation === 'white' ? 'black' : 'white';
                console.log('Flipping all mobile boards to:', globalOrientation);
                
                Object.keys(boards).forEach(id => {{
                    if (boards[id] && typeof boards[id].orientation === 'function') {{
                        try {{
                            boards[id].orientation(globalOrientation);
                        }} catch (e) {{
                            console.warn('Failed to flip board:', id, e);
                        }}
                    }}
                }});
                
                Object.keys(variationBoards).forEach(id => {{
                    if (variationBoards[id] && typeof variationBoards[id].orientation === 'function') {{
                        try {{
                            variationBoards[id].orientation(globalOrientation);
                        }} catch (e) {{
                            console.warn('Failed to flip variation board:', id, e);
                        }}
                    }}
                }});
                
                showMobileNotification('Boards flipped!', 1500);
                closeFAB();
                
            }} catch (e) {{
                console.error('Error flipping boards:', e);
            }}
        }}

        function resetToStart() {{
            showMobileSection('problem');
            closeFAB();
            showMobileNotification('Reset to start!', 1500);
        }}

        function toggleFullscreen() {{
            try {{
                if (!document.fullscreenElement) {{
                    document.documentElement.requestFullscreen();
                    showMobileNotification('Fullscreen enabled', 1500);
                }} else {{
                    document.exitFullscreen();
                    showMobileNotification('Fullscreen disabled', 1500);
                }}
                closeFAB();
            }} catch (e) {{
                console.error('Fullscreen not supported');
                showMobileNotification('Fullscreen not supported', 1500);
            }}
        }}

        function showHints() {{
            const hints = [
                'Swipe left/right to navigate sections',
                'Tap squares on spatial board for details',
                'Click moves to see positions',
                'Use FAB for quick actions',
                'Progress bar shows learning completion'
            ];
            
            const randomHint = hints[Math.floor(Math.random() * hints.length)];
            showMobileNotification('💡 ' + randomHint, 4000);
            closeFAB();
        }}

        function showMobileNotification(message, duration = 3000) {{
            // Create notification element
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 20px;
                border-radius: 25px;
                z-index: 10000;
                font-weight: 600;
                font-size: 14px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                opacity: 0;
                transition: all 0.3s ease;
                max-width: 90vw;
                text-align: center;
            `;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            // Animate in
            setTimeout(() => {{
                notification.style.opacity = '1';
                notification.style.transform = 'translateX(-50%) translateY(0)';
            }}, 10);
            
            // Remove after duration
            setTimeout(() => {{
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(-50%) translateY(-20px)';
                setTimeout(() => {{
                    document.body.removeChild(notification);
                }}, 300);
            }}, duration);
        }}

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

        function highlightMoveOnBoard(boardId, fromSquare, toSquare) {{
            try {{
                // Simple highlight for mobile
                showMobileNotification(`Move: ${{fromSquare}} → ${{toSquare}}`, 2000);
            }} catch (e) {{
                console.error('Error highlighting move:', e);
            }}
        }}

        function calculateVariationPosition(startFen, pvString) {{
            try {{
                if (!pvString || typeof Chess === 'undefined') {{
                    return startFen;
                }}
                
                const chess = new Chess(startFen);
                const moves = pvString.trim().split(/\\s+/);
                
                for (let i = 0; i < Math.min(moves.length, 4); i++) {{
                    const moveStr = moves[i].replace(/\\d+\\./, '').trim();
                    if (moveStr && moveStr !== '') {{
                        try {{
                            const move = chess.move(moveStr);
                            if (!move) break;
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

        // Initialize single SVG board fallback
        function initializeSingleSVGBoard(container, fen) {{
            try {{
                const boardDiv = document.createElement('div');
                boardDiv.className = 'chessboard svg-board';
                boardDiv.innerHTML = '<div style="width: 100%; aspect-ratio: 1; background: #f0d9b5; border: 2px solid #8B4513; display: flex; align-items: center; justify-content: center; color: #8B4513; font-size: 14px; text-align: center;">Chess Board<br>FEN: ' + fen.substring(0, 15) + '...</div>';
                
                container.innerHTML = '';
                container.appendChild(boardDiv);
                
                console.log('Mobile SVG fallback board created');
            }} catch (e) {{
                console.error('Error creating mobile SVG fallback:', e);
            }}
        }}

        // Handle viewport changes
        window.addEventListener('resize', function() {{
            setTimeout(resizeAllBoards, 300);
        }});

        // Handle orientation changes
        window.addEventListener('orientationchange', function() {{
            setTimeout(function() {{
                resizeAllBoards();
                initializeSpatialVisualization();
            }}, 500);
        }});

        console.log('Mobile Chess Learning Lab JavaScript loaded successfully!');
        """
        
        return js_code

    def _generate_mobile_problem_section(self, position_data: Dict[str, Any], fen: str) -> str:
        """Generate mobile-optimized problem section for learning."""
        themes = position_data.get('themes', [])
        themes_html = ''.join([f'<span class="tag">{theme.replace("_", " ").title()}</span>' for theme in themes[:4]])
        
        return f"""
        <div class="mobile-card">
            <h3><i class="fas fa-puzzle-piece"></i> Your Challenge</h3>
            <p style="font-size: 1.1rem; line-height: 1.6; color: #4a5568; margin-bottom: 1.5rem;">
                {position_data.get('description', 'Analyze this position and find the best move for the side to play.')}
            </p>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Difficulty</div>
                    <div class="metric-value">{position_data.get('difficulty_rating', 1200)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Phase</div>
                    <div class="metric-value">{position_data.get('game_phase', 'Middle').title()}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Type</div>
                    <div class="metric-value">{position_data.get('position_type', 'Tactical').title()}</div>
                </div>
            </div>
            
            {f'<div class="mt-2"><h4 style="color: #1a202c; margin-bottom: 0.75rem;"><i class="fas fa-tags"></i> Tactical Themes</h4><div>{themes_html}</div></div>' if themes_html else ''}
        </div>
        
        <div class="board-container">
            <div class="board-label">🎯 Find the Best Move!</div>
            <div class="board-wrapper">
                <div id="problem-board" class="chessboard"></div>
            </div>
            <div style="text-align: center; margin-top: 1rem;">
                <button onclick="showMobileSection('solution')" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 1rem 2rem; border-radius: 12px; font-weight: 600; font-size: 1rem; cursor: pointer; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3); transition: all 0.2s ease;">
                    <i class="fas fa-lightbulb"></i> Reveal Solution
                </button>
            </div>
        </div>
        
        <div class="mobile-card">
            <h3><i class="fas fa-brain"></i> Think About</h3>
            <ul style="list-style: none; padding: 0; color: #4a5568; line-height: 1.6;">
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 0.75rem;">
                    <i class="fas fa-chess-king" style="color: #667eea;"></i>
                    What are the immediate threats?
                </li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 0.75rem;">
                    <i class="fas fa-crosshairs" style="color: #667eea;"></i>
                    Are there any tactical motifs?
                </li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 0.75rem;">
                    <i class="fas fa-chess-queen" style="color: #667eea;"></i>
                    Which pieces can be improved?
                </li>
                <li style="padding: 0.5rem 0; display: flex; align-items: center; gap: 0.75rem;">
                    <i class="fas fa-flag-checkered" style="color: #667eea;"></i>
                    What's the main objective here?
                </li>
            </ul>
        </div>
        """

    def _generate_mobile_solution_section(self, position_data: Dict[str, Any], 
                                        best_move: Dict[str, Any], 
                                        current_fen: str, 
                                        result_fen: str) -> str:
        """Generate mobile solution section with side-by-side comparison."""
        best_move_notation = best_move.get('move', 'N/A')
        score = best_move.get('score', 0)
        score_display = self.format_score_display(score)
        pv = best_move.get('pv') or best_move.get('principal_variation') or best_move_notation
        
        return f"""
        <div class="mobile-card" style="background: linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%); border-left: 5px solid #10b981;">
            <h3><i class="fas fa-lightbulb"></i> Solution Revealed!</h3>
            <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 12px; color: white; margin-bottom: 1.5rem;">
                <div style="font-size: 1.5rem; font-weight: 800; margin-bottom: 0.5rem;">
                    {self.convert_to_piece_icons(best_move_notation)}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">
                    Engine Evaluation: {score_display}
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Quality</div>
                    <div class="metric-value">{best_move.get('classification', 'Best').title()}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Depth</div>
                    <div class="metric-value">{best_move.get('depth', 20)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Value</div>
                    <div class="metric-value">{best_move.get('strategic_value', 5)}/5</div>
                </div>
            </div>
        </div>

        <div class="comparison-container">
            <div class="board-container">
                <div class="board-label">📍 Current Position</div>
                <div class="board-wrapper">
                    <div id="solution-current-board" class="chessboard"></div>
                </div>
            </div>
            
            <div class="board-container">
                <div class="board-label">✨ After Best Move</div>
                <div class="board-wrapper">
                    <div id="solution-result-board" class="chessboard"></div>
                </div>
                <div style="text-align: center; margin-top: 1rem;">
                    <button onclick="animateBestMove()" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; touch-action: manipulation;">
                        <i class="fas fa-play"></i> Animate Move
                    </button>
                </div>
            </div>
        </div>
        
        <div class="mobile-card">
            <h3><i class="fas fa-chess-board"></i> Principal Variation</h3>
            <div class="enhanced-move" onclick="showMobileNotification('Principal variation shows the best line of play', 3000)">
                {self.convert_to_piece_icons(pv)}
            </div>
            <p style="color: #64748b; font-size: 0.875rem; margin-top: 1rem; line-height: 1.5;">
                This sequence shows the most likely continuation if both sides play optimally from this position.
            </p>
        </div>
        """

    def _generate_mobile_analysis_section(self, position_data: Dict[str, Any], best_move: Dict[str, Any]) -> str:
        """Generate mobile analysis section with key insights."""
        material_analysis = position_data.get('material_analysis', {})
        
        return f"""
        <div class="mobile-card">
            <h3><i class="fas fa-chart-bar"></i> Position Analysis</h3>
            
            <div class="board-container">
                <div class="board-label">Analysis Board</div>
                <div class="board-wrapper">
                    <div id="analysis-board" class="chessboard"></div>
                </div>
            </div>
        </div>
        
        <div class="mobile-card">
            <h3><i class="fas fa-balance-scale"></i> Key Factors</h3>
            <div class="mobile-table">
                <div class="table-header">Position Evaluation</div>
                <div class="table-row">
                    <div class="row-header">
                        <span><i class="fas fa-coins"></i> Material Balance</span>
                        <span class="score-neutral">{material_analysis.get('imbalance_score', 0):.2f}</span>
                    </div>
                    <div class="row-details">
                        White: {material_analysis.get('white_total', 0)} • Black: {material_analysis.get('black_total', 0)}
                    </div>
                </div>
                <div class="table-row">
                    <div class="row-header">
                        <span><i class="fas fa-shield-alt"></i> King Safety</span>
                        <span class="score-positive">Good</span>
                    </div>
                    <div class="row-details">
                        Both kings are reasonably safe with adequate pawn cover
                    </div>
                </div>
                <div class="table-row">
                    <div class="row-header">
                        <span><i class="fas fa-chess-knight"></i> Piece Activity</span>
                        <span class="score-neutral">Moderate</span>
                    </div>
                    <div class="row-details">
                        Several pieces can be improved with better positioning
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mobile-card">
            <h3><i class="fas fa-lightbulb"></i> Why This Move?</h3>
            <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #0ea5e9;">
                <p style="color: #1e293b; line-height: 1.6; margin: 0;">
                    {position_data.get('learning_insights', {}).get('universal', {}).get('best_move_reasoning', 'This move improves the position by addressing key weaknesses and creating new opportunities.')}
                </p>
            </div>
        </div>
        """

    def _generate_mobile_moves_section(self, top_moves: List[Dict], fen: str) -> str:
        """Generate mobile moves section with touch-friendly interface."""
        return f"""
        <div class="mobile-card">
            <h3><i class="fas fa-list-ol"></i> Engine Analysis</h3>
            
            <div class="board-container">
                <div class="board-label">Move Analysis Board</div>
                <div class="board-wrapper">
                    <div id="moves-board" class="chessboard"></div>
                </div>
            </div>
        </div>
        
        <div class="mobile-card">
            <h3><i class="fas fa-trophy"></i> Top Engine Moves</h3>
            <div class="mobile-table">
                <div class="table-header">Touch a move to analyze</div>
                {self._generate_mobile_moves_table(top_moves[:8])}
            </div>
        </div>
        
        <div class="mobile-card">
            <h3><i class="fas fa-info-circle"></i> Move Classifications</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                <div style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🏆</div>
                    <div style="font-weight: 600; color: #166534;">Best Move</div>
                    <div style="font-size: 0.75rem; color: #166534;">Engine's top choice</div>
                </div>
                <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">👍</div>
                    <div style="font-weight: 600; color: #92400e;">Good Move</div>
                    <div style="font-size: 0.75rem; color: #92400e;">Reasonable option</div>
                </div>
                <div style="background: linear-gradient(135deg, #fed7d7 0%, #fbb6ce 100%); padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⚠️</div>
                    <div style="font-weight: 600; color: #b91c1c;">Inaccuracy</div>
                    <div style="font-size: 0.75rem; color: #b91c1c;">Slight loss</div>
                </div>
                <div style="background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); padding: 1rem; border-radius: 8px; text-align: center;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🤔</div>
                    <div style="font-weight: 600; color: #3730a3;">Dubious</div>
                    <div style="font-size: 0.75rem; color: #3730a3;">Questionable</div>
                </div>
            </div>
        </div>
        """

    def _generate_mobile_moves_table(self, moves: List[Dict]) -> str:
        """Generate mobile-optimized moves table."""
        table_html = ""
        for i, move in enumerate(moves, 1):
            score_display = self.format_score_display(move.get('score', 0))
            pv = move.get('pv') or move.get('principal_variation') or move.get('move', '')
            classification = move.get('classification', 'Unknown').title()
            
            # Determine classification color
            if classification.lower() == 'best':
                class_color = '#10b981'
                class_bg = '#dcfce7'
            elif classification.lower() == 'good':
                class_color = '#f59e0b'
                class_bg = '#fef3c7'
            else:
                class_color = '#6b7280'
                class_bg = '#f3f4f6'
            
            table_html += f"""
            <div class="table-row">
                <div class="row-header">
                    <span style="font-weight: 800; color: #1a202c;">#{i} {self.convert_to_piece_icons(move.get('move', ''))}</span>
                    <span style="background: {class_bg}; color: {class_color}; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{classification}</span>
                </div>
                <div class="row-details">
                    <strong>Score:</strong> {score_display} • <strong>CP Loss:</strong> {move.get('centipawn_loss', 0)}<br>
                    <div class="enhanced-move" style="margin-top: 0.5rem; padding: 0.5rem; font-size: 0.8rem;">
                        {self.convert_to_piece_icons(pv[:40] + ('...' if len(pv) > 40 else ''))}
                    </div>
                </div>
            </div>
            """
        
        return table_html

    def _generate_mobile_spatial_section(self, current_fen: str, result_fen: str, 
                                       current_spatial_data: Dict[str, Any], 
                                       result_spatial_data: Dict[str, Any],
                                       best_move: Dict[str, Any]) -> str:
        """Generate mobile spatial analysis section."""
        return f"""
        <div class="mobile-card">
            <h3><i class="fas fa-map"></i> Space Control Analysis</h3>
            <p style="color: #64748b; line-height: 1.5; margin-bottom: 1.5rem;">
                Spatial control shows which player dominates different areas of the board. Tap squares for details.
            </p>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">White Territory</div>
                    <div class="metric-value">{current_spatial_data.get('white_space_percentage', 0):.0f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Black Territory</div>
                    <div class="metric-value">{current_spatial_data.get('black_space_percentage', 0):.0f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Contested</div>
                    <div class="metric-value">{current_spatial_data.get('contested_percentage', 0):.0f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Space Edge</div>
                    <div class="metric-value">{current_spatial_data.get('space_advantage', 0):+.0f}</div>
                </div>
            </div>
        </div>

        <div class="comparison-container">
            <div class="spatial-container">
                <div class="board-label">📍 Current Position</div>
                <div class="board-wrapper">
                    <div id="spatial-current-board" class="chessboard"></div>
                </div>
            </div>
            
            <div class="spatial-container">
                <div class="board-label">📊 Space Control Map</div>
                <div id="spatial-current-grid" class="spatial-grid"></div>
                <div class="spatial-legend">
                    <div><span style="width: 12px; height: 12px; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); display: inline-block; border-radius: 2px;"></span> White</div>
                    <div><span style="width: 12px; height: 12px; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); display: inline-block; border-radius: 2px;"></span> Black</div>
                    <div><span style="width: 12px; height: 12px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); display: inline-block; border-radius: 2px;"></span> Fight</div>
                </div>
            </div>
        </div>

        <div class="comparison-container">
            <div class="spatial-container">
                <div class="board-label">✨ After Best Move</div>
                <div class="board-wrapper">
                    <div id="spatial-result-board" class="chessboard"></div>
                </div>
            </div>
            
            <div class="spatial-container">
                <div class="board-label">📈 Updated Control</div>
                <div id="spatial-result-grid" class="spatial-grid"></div>
                <div class="spatial-legend">
                    <div><span style="width: 12px; height: 12px; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); display: inline-block; border-radius: 2px;"></span> White</div>
                    <div><span style="width: 12px; height: 12px; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); display: inline-block; border-radius: 2px;"></span> Black</div>
                    <div><span style="width: 12px; height: 12px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); display: inline-block; border-radius: 2px;"></span> Fight</div>
                </div>
            </div>
        </div>
        
        <div class="mobile-card">
            <h3><i class="fas fa-chart-line"></i> Spatial Changes</h3>
            <div class="mobile-table">
                <div class="table-header">Impact of Best Move</div>
                <div class="table-row">
                    <div class="row-header">
                        <span>White Territory Change</span>
                        <span class="{'score-positive' if result_spatial_data.get('white_space_percentage', 0) > current_spatial_data.get('white_space_percentage', 0) else 'score-negative' if result_spatial_data.get('white_space_percentage', 0) < current_spatial_data.get('white_space_percentage', 0) else 'score-neutral'}">{result_spatial_data.get('white_space_percentage', 0) - current_spatial_data.get('white_space_percentage', 0):+.1f}%</span>
                    </div>
                    <div class="row-details">
                        From {current_spatial_data.get('white_space_percentage', 0):.1f}% to {result_spatial_data.get('white_space_percentage', 0):.1f}%
                    </div>
                </div>
                <div class="table-row">
                    <div class="row-header">
                        <span>Black Territory Change</span>
                        <span class="{'score-negative' if result_spatial_data.get('black_space_percentage', 0) > current_spatial_data.get('black_space_percentage', 0) else 'score-positive' if result_spatial_data.get('black_space_percentage', 0) < current_spatial_data.get('black_space_percentage', 0) else 'score-neutral'}">{result_spatial_data.get('black_space_percentage', 0) - current_spatial_data.get('black_space_percentage', 0):+.1f}%</span>
                    </div>
                    <div class="row-details">
                        From {current_spatial_data.get('black_space_percentage', 0):.1f}% to {result_spatial_data.get('black_space_percentage', 0):.1f}%
                    </div>
                </div>
            </div>
        </div>
        """

    def _generate_mobile_variations_section(self, position_data: Dict[str, Any], current_fen: str) -> str:
        """Generate mobile variations section with progressive disclosure."""
        top_moves = position_data.get('top_moves', [])[:3]
        
        variations_html = ""
        for i, move in enumerate(top_moves, 1):
            move_name = move.get('move', f'Variation {i}')
            score_display = self.format_score_display(move.get('score', 0))
            pv_notation = move.get('pv') or move.get('principal_variation') or move_name
            classification = move.get('classification', 'Unknown').title()
            
            # Determine card color based on move quality
            if i == 1:  # Best move
                card_bg = 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)'
                border_color = '#10b981'
                icon = '🏆'
            elif i == 2:
                card_bg = 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)'
                border_color = '#f59e0b'
                icon = '👍'
            else:
                card_bg = 'linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)'
                border_color = '#6b7280'
                icon = '🤔'
            
            clickable_pv = self._create_mobile_clickable_moves(pv_notation, current_fen, i)
            
            variations_html += f"""
            <div class="mobile-card" style="background: {card_bg}; border-left: 4px solid {border_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4 style="margin: 0; color: #1a202c; font-size: 1.1rem;">
                        {icon} Variation {i}: {self.convert_to_piece_icons(move_name)}
                    </h4>
                    <div style="background: rgba(255,255,255,0.8); padding: 0.5rem 0.75rem; border-radius: 8px; font-weight: 700; color: #1a202c;">
                        {score_display}
                    </div>
                </div>
                
                <div class="metrics-grid" style="margin-bottom: 1rem;">
                    <div class="metric-card" style="background: rgba(255,255,255,0.7);">
                        <div class="metric-label">Quality</div>
                        <div class="metric-value" style="font-size: 1rem;">{classification}</div>
                    </div>
                    <div class="metric-card" style="background: rgba(255,255,255,0.7);">
                        <div class="metric-label">CP Loss</div>
                        <div class="metric-value" style="font-size: 1rem;">{move.get('centipawn_loss', 0)}</div>
                    </div>
                    <div class="metric-card" style="background: rgba(255,255,255,0.7);">
                        <div class="metric-label">Depth</div>
                        <div class="metric-value" style="font-size: 1rem;">{move.get('depth', 20)}</div>
                    </div>
                </div>
                
                <div class="comparison-container">
                    <div class="board-container" style="background: rgba(255,255,255,0.8);">
                        <div class="board-label">After Variation {i}</div>
                        <div class="board-wrapper">
                            <div id="variation-board-{i}" class="chessboard"></div>
                        </div>
                    </div>
                    
                    <div class="spatial-container" style="background: rgba(255,255,255,0.8);">
                        <div class="board-label">Space Control</div>
                        <div id="variation-spatial-board-{i}" class="spatial-grid"></div>
                    </div>
                </div>
                
                <div>
                    <h5 style="color: #1a202c; margin-bottom: 0.75rem;"><i class="fas fa-chess-board"></i> Principal Variation</h5>
                    <div class="enhanced-move">{clickable_pv}</div>
                </div>
            </div>
            """
        
        return f"""
        <div class="mobile-card">
            <h3><i class="fas fa-code-branch"></i> Variation Analysis</h3>
            <p style="color: #64748b; line-height: 1.5; margin-bottom: 1.5rem;">
                Compare the top engine moves and understand why each variation leads to different evaluations.
            </p>
            
            <div class="board-container">
                <div class="board-label">Main Analysis Board</div>
                <div class="board-wrapper">
                    <div id="variations-board" class="chessboard"></div>
                </div>
                <div style="text-align: center; margin-top: 1rem;">
                    <button onclick="initializeVariationBoards()" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer;">
                        <i class="fas fa-refresh"></i> Update Boards
                    </button>
                </div>
            </div>
        </div>
        
        {variations_html}
        """

    def _create_mobile_clickable_moves(self, pv_string: str, starting_fen: str, variation_num: int) -> str:
        """Create mobile-optimized clickable moves from PV string."""
        if not pv_string:
            return ""
        
        try:
            moves = pv_string.strip().split()
            clickable_moves = []
            current_fen = starting_fen
            
            for i, move in enumerate(moves[:6]):  # Limit to 6 moves for mobile
                clean_move = re.sub(r'^\d+\.+', '', move).strip()
                if not clean_move:
                    continue
                
                try:
                    board = chess.Board(current_fen)
                    chess_move = board.parse_san(clean_move)
                    board.push(chess_move)
                    move_fen = board.fen()
                    
                    piece_icon_move = self.convert_to_piece_icons(clean_move)
                    is_first_move = i == 0
                    
                    clickable_moves.append(
                        f'<span class="clickable-move{"" if not is_first_move else " best-move"}" '
                        f'data-move="{clean_move}" data-fen="{move_fen}" '
                        f'onclick="loadPositionOnMobileBoard(\'variation-board-{variation_num}\', \'{move_fen}\', \'{clean_move}\')">'
                        f'{piece_icon_move}</span>'
                    )
                    
                    current_fen = move_fen
                    
                except Exception as e:
                    piece_icon_move = self.convert_to_piece_icons(clean_move)
                    clickable_moves.append(f'<span style="color: #64748b;">{piece_icon_move}</span>')
            
            return ' '.join(clickable_moves)
            
        except Exception as e:
            return self.convert_to_piece_icons(pv_string[:50] + ('...' if len(pv_string) > 50 else ''))

    # Continue with remaining utility methods
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
                # Final fallback with demo data
                return {
                    'control_matrix': [[0 for _ in range(8)] for _ in range(8)],
                    'white_space_percentage': 28.1,
                    'black_space_percentage': 26.6,
                    'contested_percentage': 18.8,
                    'neutral_percentage': 26.5,
                    'space_advantage': 1
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

    def _generate_chess_board_svg(self, fen: str, flipped: bool = False, size: int = 350) -> str:
        """Generate SVG representation of chess board for mobile fallback."""
        try:
            board = chess.Board(fen)
            svg = chess.svg.board(
                board=board,
                flipped=flipped,
                size=size,
                style="""
                .square.light { fill: #f0d9b5; stroke: #999; stroke-width: 0.5; }
                .square.dark { fill: #b58863; stroke: #999; stroke-width: 0.5; }
                .piece { font-size: 40px; }
                """
            )
            return svg
        except Exception as e:
            return f'<div style="border: 2px solid #ddd; padding: 20px; text-align: center; background: #f8f9fa; border-radius: 8px;">Chess board generation failed: {str(e)}</div>'

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
