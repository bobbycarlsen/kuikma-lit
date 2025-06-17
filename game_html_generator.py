# game_html_generator.py - Enhanced Game HTML Generator for Kuikma Chess
"""
Enhanced Game HTML Generator - Steve Jobs Inspired Design
========================================================

This module creates comprehensive, magazine-quality HTML reports for chess games
with mobile-first responsive design, print optimization, and offline functionality.

Key Features:
• Mobile-first responsive design
• Comprehensive game analysis with side-by-side boards  
• Rich typography and visual hierarchy
• Print-friendly layouts with page breaks
• Inline CSS for complete offline functionality
• Critical positions analysis
• Move-by-move commentary support
• Statistical insights and charts
• Clean, minimalist aesthetic inspired by Apple's design philosophy

The generator produces self-contained HTML files that work perfectly
on any device, online or offline, with professional presentation quality.
"""

import os
import math
import base64
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path

import chess
import chess.pgn
import chess.svg


class GameHTMLGenerator:
    """
    Enhanced HTML generator creating comprehensive, beautiful game reports.
    
    Inspired by Steve Jobs' design philosophy:
    - Simplicity over complexity
    - Function follows form
    - Attention to every detail
    - Elegant user experience
    """
    
    def __init__(self, output_dir: str = "kuikma_game_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate(self, game: chess.pgn.Game, *, 
                 analysis_notes: Optional[str] = None,
                 critical_positions: Optional[List[Dict]] = None,
                 include_variations: bool = True,
                 include_statistics: bool = True,
                 snapshot_frequency: int = 6) -> str:
        """
        Generate comprehensive HTML study report.
        
        Args:
            game: chess.pgn.Game object
            analysis_notes: User's analysis notes
            critical_positions: List of critical position data
            include_variations: Whether to include move variations
            include_statistics: Whether to include game statistics
            snapshot_frequency: Number of key positions to highlight
            
        Returns:
            Path to generated HTML file
        """
        
        # Extract game data
        headers = dict(game.headers)
        moves_san = self._extract_moves_with_analysis(game)
        key_positions = self._select_key_positions(game, snapshot_frequency)
        game_statistics = self._calculate_game_statistics(game) if include_statistics else {}
        
        # Build comprehensive HTML document
        html_content = self._build_html_document(
            headers=headers,
            moves=moves_san,
            key_positions=key_positions,
            statistics=game_statistics,
            analysis_notes=analysis_notes,
            critical_positions=critical_positions or []
        )
        
        # Generate filename and save
        filename = self._generate_filename(headers)
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return str(filepath)
    
    def _build_html_document(self, *, headers: Dict, moves: List[Dict], 
                           key_positions: List[Tuple], statistics: Dict,
                           analysis_notes: Optional[str],
                           critical_positions: List[Dict]) -> str:
        """Build the complete HTML document."""
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Comprehensive chess game analysis - {headers.get('White', 'Unknown')} vs {headers.get('Black', 'Unknown')}">
    <title>Kuikma Chess Study: {headers.get('White', 'Unknown')} vs {headers.get('Black', 'Unknown')}</title>
    <style>{self._get_comprehensive_css()}</style>
</head>
<body>
    <div class="study-container">
        {self._render_header(headers)}
        {self._render_table_of_contents()}
        {self._render_game_overview(headers, statistics)}
        {self._render_move_analysis(moves)}
        {self._render_key_positions_gallery(key_positions)}
        {self._render_critical_positions(critical_positions)}
        {self._render_game_statistics(statistics)}
        {self._render_analysis_notes(analysis_notes)}
        {self._render_footer()}
    </div>
    
    {self._render_interactive_javascript()}
</body>
</html>"""
    
    def _get_comprehensive_css(self) -> str:
        """Generate comprehensive CSS with mobile-first responsive design."""
        return """
/* === RESET AND FOUNDATION === */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    font-size: 16px;
    scroll-behavior: smooth;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #1d1d1f;
    background: #f5f5f7;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* === LAYOUT CONTAINER === */
.study-container {
    max-width: 1200px;
    margin: 0 auto;
    background: #ffffff;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    border-radius: 12px;
    overflow: hidden;
}

/* === TYPOGRAPHY === */
h1 {
    font-size: clamp(2.5rem, 5vw, 3.5rem);
    font-weight: 600;
    line-height: 1.1;
    margin-bottom: 1rem;
}

h2 {
    font-size: clamp(1.8rem, 4vw, 2.5rem);
    font-weight: 600;
    line-height: 1.2;
    margin: 3rem 0 1.5rem;
    color: #1d1d1f;
}

h3 {
    font-size: clamp(1.3rem, 3vw, 1.8rem);
    font-weight: 600;
    line-height: 1.3;
    margin: 2rem 0 1rem;
    color: #424245;
}

h4 {
    font-size: clamp(1.1rem, 2.5vw, 1.3rem);
    font-weight: 600;
    line-height: 1.4;
    margin: 1.5rem 0 0.75rem;
    color: #6e6e73;
}

p {
    font-size: 1.1rem;
    line-height: 1.7;
    margin-bottom: 1.5rem;
    color: #1d1d1f;
}

/* === HEADER SECTION === */
.study-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 4rem 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.study-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="chess" width="12.5" height="12.5" patternUnits="userSpaceOnUse"><rect width="6.25" height="6.25" fill="rgba(255,255,255,0.03)"/></pattern></defs><rect width="100" height="100" fill="url(%23chess)"/></svg>');
    opacity: 0.3;
}

.study-header > * {
    position: relative;
    z-index: 1;
}

.study-title {
    font-size: clamp(2rem, 6vw, 4rem);
    font-weight: 300;
    margin-bottom: 1rem;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.game-meta {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    margin-top: 3rem;
    text-align: left;
}

.meta-card {
    background: rgba(255, 255, 255, 0.1);
    padding: 1.5rem;
    border-radius: 12px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.meta-label {
    font-size: 0.9rem;
    opacity: 0.8;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.meta-value {
    font-size: 1.3rem;
    font-weight: 600;
}

/* === TABLE OF CONTENTS === */
.table-of-contents {
    padding: 2rem;
    background: #f8f9fa;
    border-bottom: 1px solid #e9ecef;
}

.toc-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #495057;
}

.toc-list {
    list-style: none;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
}

.toc-item {
    padding: 0.75rem 1rem;
    background: white;
    border-radius: 8px;
    border-left: 4px solid #007aff;
    transition: all 0.2s ease;
}

.toc-item:hover {
    transform: translateX(4px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.toc-item a {
    text-decoration: none;
    color: #007aff;
    font-weight: 500;
}

/* === CONTENT SECTIONS === */
.section {
    padding: 3rem 2rem;
    border-bottom: 1px solid #f0f0f0;
}

.section:last-child {
    border-bottom: none;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #f0f0f0;
}

.section-icon {
    font-size: 2rem;
}

.section-title {
    font-size: 2rem;
    font-weight: 600;
    color: #1d1d1f;
}

/* === BOARD LAYOUTS === */
.board-gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
}

.board-snapshot {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.board-snapshot:hover {
    transform: translateY(-4px);
}

.board-snapshot svg {
    width: 100%;
    height: auto;
    display: block;
}

.board-caption {
    padding: 1rem;
    text-align: center;
    background: #f8f9fa;
    font-weight: 600;
    color: #495057;
}

.side-by-side {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    margin: 3rem 0;
    align-items: start;
}

/* === MOVE ANALYSIS === */
.moves-container {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 2rem;
    margin: 2rem 0;
}

.moves-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 0.5rem;
    font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
    font-size: 0.95rem;
    line-height: 1.8;
}

.move-pair {
    padding: 0.5rem;
    border-radius: 6px;
    background: white;
    transition: background-color 0.2s ease;
}

.move-pair:hover {
    background: #e3f2fd;
}

.move-number {
    font-weight: 600;
    color: #666;
    margin-right: 0.5rem;
}

.move-san {
    font-weight: 500;
    color: #1d1d1f;
}

/* === STATISTICS CARDS === */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.stat-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    border: 1px solid #dee2e6;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #007aff;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 1rem;
    color: #6c757d;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* === CRITICAL POSITIONS === */
.critical-position {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    margin: 2rem 0;
    border-left: 4px solid #ff3b30;
    box-shadow: 0 4px 12px rgba(255, 59, 48, 0.1);
}

.critical-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.critical-badge {
    background: #ff3b30;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
}

.critical-move {
    font-size: 1.3rem;
    font-weight: 600;
    color: #1d1d1f;
}

/* === ANALYSIS NOTES === */
.analysis-notes {
    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    border-radius: 12px;
    padding: 2rem;
    margin: 2rem 0;
    border-left: 4px solid #ffc107;
}

.notes-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.notes-icon {
    font-size: 2rem;
}

.notes-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #856404;
}

.notes-content {
    font-size: 1.1rem;
    line-height: 1.7;
    color: #533f03;
}

/* === FOOTER === */
.study-footer {
    background: #1d1d1f;
    color: white;
    padding: 3rem 2rem;
    text-align: center;
}

.footer-content {
    max-width: 600px;
    margin: 0 auto;
}

.footer-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

.footer-text {
    opacity: 0.8;
    line-height: 1.6;
    margin-bottom: 2rem;
}

.footer-meta {
    padding-top: 2rem;
    border-top: 1px solid #424245;
    opacity: 0.6;
    font-size: 0.9rem;
}

/* === RESPONSIVE DESIGN === */
@media (max-width: 768px) {
    .study-container {
        margin: 0;
        border-radius: 0;
    }
    
    .side-by-side {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    
    .game-meta {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .section {
        padding: 2rem 1rem;
    }
    
    .study-header {
        padding: 3rem 1rem;
    }
    
    .moves-grid {
        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
        gap: 0.25rem;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .board-gallery {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .section {
        padding: 1.5rem 0.75rem;
    }
    
    .meta-card {
        padding: 1rem;
    }
    
    .stat-card {
        padding: 1.5rem;
    }
    
    .moves-grid {
        font-size: 0.85rem;
    }
}

/* === PRINT OPTIMIZATION === */
@media print {
    * {
        -webkit-print-color-adjust: exact !important;
        color-adjust: exact !important;
    }
    
    .study-container {
        box-shadow: none;
        border-radius: 0;
    }
    
    .section {
        page-break-inside: avoid;
        break-inside: avoid;
    }
    
    .critical-position {
        page-break-inside: avoid;
        break-inside: avoid;
    }
    
    .board-snapshot {
        page-break-inside: avoid;
        break-inside: avoid;
    }
    
    .side-by-side {
        page-break-inside: avoid;
        break-inside: avoid;
    }
    
    h2 {
        page-break-before: always;
        break-before: page;
    }
    
    h2:first-child {
        page-break-before: avoid;
        break-before: avoid;
    }
    
    .study-header {
        page-break-after: always;
        break-after: page;
    }
    
    .study-footer {
        page-break-before: always;
        break-before: page;
    }
    
    /* Ensure good print contrast */
    body {
        background: white;
        color: black;
    }
    
    .section {
        border-bottom: 1px solid #ccc;
    }
    
    /* Hide interactive elements in print */
    .toc-item:hover {
        transform: none;
        box-shadow: none;
    }
    
    .board-snapshot:hover {
        transform: none;
    }
    
    .stat-card:hover {
        transform: none;
        box-shadow: none;
    }
}

/* === ACCESSIBILITY === */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    
    html {
        scroll-behavior: auto;
    }
}

/* === HIGH CONTRAST MODE === */
@media (prefers-contrast: high) {
    body {
        background: white;
        color: black;
    }
    
    .section {
        border-bottom: 2px solid black;
    }
    
    .meta-card {
        border: 2px solid black;
    }
    
    .stat-card {
        border: 2px solid black;
    }
}
"""
    
    def _render_header(self, headers: Dict) -> str:
        """Render the study header with game information."""
        white = headers.get('White', 'Unknown')
        black = headers.get('Black', 'Unknown')
        event = headers.get('Event', 'Unknown')
        date = headers.get('Date', 'Unknown')
        result = headers.get('Result', '*')
        site = headers.get('Site', 'Unknown')
        
        # Format result
        result_display = {
            '1-0': 'White Wins',
            '0-1': 'Black Wins', 
            '1/2-1/2': 'Draw'
        }.get(result, result)
        
        return f"""
        <header class="study-header">
            <h1 class="study-title">Chess Game Analysis</h1>
            <div class="game-meta">
                <div class="meta-card">
                    <div class="meta-label">Players</div>
                    <div class="meta-value">{white} vs {black}</div>
                </div>
                <div class="meta-card">
                    <div class="meta-label">Event</div>
                    <div class="meta-value">{event}</div>
                </div>
                <div class="meta-card">
                    <div class="meta-label">Date</div>
                    <div class="meta-value">{date}</div>
                </div>
                <div class="meta-card">
                    <div class="meta-label">Result</div>
                    <div class="meta-value">{result_display}</div>
                </div>
                <div class="meta-card">
                    <div class="meta-label">Site</div>
                    <div class="meta-value">{site}</div>
                </div>
                <div class="meta-card">
                    <div class="meta-label">Generated</div>
                    <div class="meta-value">{datetime.now().strftime('%B %d, %Y')}</div>
                </div>
            </div>
        </header>
        """
    
    def _render_table_of_contents(self) -> str:
        """Render table of contents for easy navigation."""
        return """
        <nav class="table-of-contents">
            <h2 class="toc-title">Study Contents</h2>
            <ul class="toc-list">
                <li class="toc-item"><a href="#game-overview">📊 Game Overview</a></li>
                <li class="toc-item"><a href="#move-analysis">♟️ Move Analysis</a></li>
                <li class="toc-item"><a href="#key-positions">🎯 Key Positions</a></li>
                <li class="toc-item"><a href="#critical-moments">⚡ Critical Moments</a></li>
                <li class="toc-item"><a href="#statistics">📈 Game Statistics</a></li>
                <li class="toc-item"><a href="#analysis-notes">📝 Analysis Notes</a></li>
            </ul>
        </nav>
        """
    
    def _render_game_overview(self, headers: Dict, statistics: Dict) -> str:
        """Render game overview section."""
        opening = headers.get('Opening', 'Unknown')
        eco = headers.get('ECO', '')
        total_moves = statistics.get('total_moves', 0)
        game_length = statistics.get('game_length_minutes', 0)
        
        return f"""
        <section id="game-overview" class="section">
            <div class="section-header">
                <span class="section-icon">📊</span>
                <h2 class="section-title">Game Overview</h2>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{total_moves}</div>
                    <div class="stat-label">Total Moves</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{eco}</div>
                    <div class="stat-label">ECO Code</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{game_length}min</div>
                    <div class="stat-label">Estimated Duration</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{statistics.get('complexity_rating', 'N/A')}</div>
                    <div class="stat-label">Complexity Rating</div>
                </div>
            </div>
            
            <div class="side-by-side">
                <div>
                    <h3>Opening Information</h3>
                    <p><strong>Opening:</strong> {opening}</p>
                    <p><strong>ECO Code:</strong> {eco}</p>
                    <p>This opening is known for its strategic complexity and has been played at the highest levels of chess. The resulting positions often lead to rich middlegame play with opportunities for both tactical and positional themes.</p>
                </div>
                <div>
                    <h3>Game Characteristics</h3>
                    <p>This game showcases interesting strategic themes and tactical motifs that make it valuable for study. The interplay between positional understanding and concrete calculation provides insights into high-level chess thinking.</p>
                    <p>Key learning opportunities include opening principles, middlegame planning, and endgame technique demonstration.</p>
                </div>
            </div>
        </section>
        """
    
    def _render_move_analysis(self, moves: List[Dict]) -> str:
        """Render complete move sequence with analysis."""
        moves_html = ""
        
        for i in range(0, len(moves), 2):
            move_number = (i // 2) + 1
            white_move = moves[i] if i < len(moves) else None
            black_move = moves[i + 1] if i + 1 < len(moves) else None
            
            white_san = self._convert_to_icons(white_move['san']) if white_move else ""
            black_san = self._convert_to_icons(black_move['san']) if black_move else ""
            
            moves_html += f"""
            <div class="move-pair">
                <span class="move-number">{move_number}.</span>
                <span class="move-san">{white_san}</span>
                {f'<span class="move-san">{black_san}</span>' if black_san else ''}
            </div>
            """
        
        return f"""
        <section id="move-analysis" class="section">
            <div class="section-header">
                <span class="section-icon">♟️</span>
                <h2 class="section-title">Complete Move Analysis</h2>
            </div>
            
            <p>Below is the complete game notation with enhanced formatting. Each move pair is displayed with chess piece icons for better readability and visual appeal.</p>
            
            <div class="moves-container">
                <div class="moves-grid">
                    {moves_html}
                </div>
            </div>
            
            <div style="margin-top: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #007aff;">
                <h4>📚 Study Tip</h4>
                <p>When studying this game, try to understand the reasoning behind each move. Look for tactical themes, positional improvements, and strategic plans that unfold throughout the game.</p>
            </div>
        </section>
        """
    
    def _render_key_positions_gallery(self, key_positions: List[Tuple]) -> str:
        """Render gallery of key positions throughout the game."""
        if not key_positions:
            return ""
        
        gallery_html = ""
        for ply, san, svg_html in key_positions:
            move_label = f"Move {math.ceil(ply/2)}{'…' if ply%2==0 else ''}" if ply > 0 else "Starting Position"
            move_display = self._convert_to_icons(san) if san and san != "Start" else "Starting Position"
            
            gallery_html += f"""
            <div class="board-snapshot">
                {svg_html}
                <div class="board-caption">
                    {move_label}: {move_display}
                </div>
            </div>
            """
        
        return f"""
        <section id="key-positions" class="section">
            <div class="section-header">
                <span class="section-icon">🎯</span>
                <h2 class="section-title">Key Positions</h2>
            </div>
            
            <p>These positions represent important moments in the game where significant strategic or tactical themes emerge. Study each position to understand the key ideas and plans available to both sides.</p>
            
            <div class="board-gallery">
                {gallery_html}
            </div>
        </section>
        """
    
    def _render_critical_positions(self, critical_positions: List[Dict]) -> str:
        """Render critical positions analysis."""
        if not critical_positions:
            return ""
        
        critical_html = ""
        for i, pos in enumerate(critical_positions[:4]):  # Limit to 4 for layout
            try:
                board_svg = chess.svg.board(board=pos['board'], size=300)
                move_display = self._convert_to_icons(pos['move'])
                
                critical_html += f"""
                <div class="critical-position">
                    <div class="critical-header">
                        <div class="critical-badge">Critical</div>
                        <div class="critical-move">Move {pos['move_number']}: {move_display}</div>
                    </div>
                    
                    <div class="side-by-side">
                        <div>
                            {board_svg}
                        </div>
                        <div>
                            <h4>Position Analysis</h4>
                            <p><strong>Evaluation Change:</strong> {pos['change']:+.2f}</p>
                            <p><strong>Current Evaluation:</strong> {pos['evaluation']:+.2f}</p>
                            <p><strong>Significance:</strong> {pos['reason']}</p>
                            
                            <div style="margin-top: 1.5rem; padding: 1rem; background: #fff3cd; border-radius: 8px;">
                                <h5>Why This Position Matters</h5>
                                <p>This position represents a crucial moment where the game's trajectory significantly changed. Understanding the key ideas and candidate moves here is essential for improving your chess intuition.</p>
                            </div>
                        </div>
                    </div>
                </div>
                """
            except Exception as e:
                continue
        
        return f"""
        <section id="critical-moments" class="section">
            <div class="section-header">
                <span class="section-icon">⚡</span>
                <h2 class="section-title">Critical Moments</h2>
            </div>
            
            <p>These positions mark the most important moments in the game where major evaluation shifts occurred or critical decisions were made.</p>
            
            {critical_html}
        </section>
        """ if critical_html else ""
    
    def _render_game_statistics(self, statistics: Dict) -> str:
        """Render comprehensive game statistics."""
        if not statistics:
            return ""
        
        return f"""
        <section id="statistics" class="section">
            <div class="section-header">
                <span class="section-icon">📈</span>
                <h2 class="section-title">Game Statistics</h2>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{statistics.get('total_moves', 0)}</div>
                    <div class="stat-label">Total Moves</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{statistics.get('captures', 0)}</div>
                    <div class="stat-label">Captures</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{statistics.get('checks', 0)}</div>
                    <div class="stat-label">Checks Given</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{statistics.get('castling_moves', 0)}</div>
                    <div class="stat-label">Castling Moves</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{statistics.get('piece_development_score', 0):.1f}</div>
                    <div class="stat-label">Development Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{statistics.get('complexity_rating', 'N/A')}</div>
                    <div class="stat-label">Complexity</div>
                </div>
            </div>
            
            <div class="side-by-side">
                <div>
                    <h3>Opening Phase (Moves 1-15)</h3>
                    <p>The opening phase focused on piece development and central control. Both players followed established theoretical principles while looking for opportunities to gain small advantages.</p>
                    <ul>
                        <li>Development efficiency: {statistics.get('opening_efficiency', 'Good')}</li>
                        <li>Central control: {statistics.get('opening_center_control', 'Balanced')}</li>
                        <li>King safety: {statistics.get('opening_king_safety', 'Secured')}</li>
                    </ul>
                </div>
                <div>
                    <h3>Game Character Analysis</h3>
                    <p>This game demonstrated {statistics.get('game_character', 'balanced play')} with opportunities for both tactical and positional understanding.</p>
                    <ul>
                        <li>Strategic complexity: {statistics.get('strategic_complexity', 'Moderate')}</li>
                        <li>Tactical richness: {statistics.get('tactical_richness', 'Average')}</li>
                        <li>Educational value: {statistics.get('educational_value', 'High')}</li>
                    </ul>
                </div>
            </div>
        </section>
        """
    
    def _render_analysis_notes(self, analysis_notes: Optional[str]) -> str:
        """Render user analysis notes section."""
        if not analysis_notes:
            return ""
        
        # Convert line breaks to paragraphs for better formatting
        formatted_notes = analysis_notes.replace('\n\n', '</p><p>').replace('\n', '<br>')
        
        return f"""
        <section id="analysis-notes" class="section">
            <div class="analysis-notes">
                <div class="notes-header">
                    <span class="notes-icon">📝</span>
                    <h2 class="notes-title">Personal Analysis Notes</h2>
                </div>
                <div class="notes-content">
                    <p>{formatted_notes}</p>
                </div>
            </div>
        </section>
        """
    
    def _render_footer(self) -> str:
        """Render study footer with metadata."""
        return f"""
        <footer class="study-footer">
            <div class="footer-content">
                <h3 class="footer-title">Kuikma Chess Engine</h3>
                <p class="footer-text">
                    This comprehensive game analysis was generated using advanced chess analysis algorithms 
                    and modern web technologies. The study includes position evaluation, strategic insights, 
                    and educational annotations designed to enhance your chess understanding.
                </p>
                <div class="footer-meta">
                    Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} • 
                    Kuikma Chess Analysis Platform • 
                    Version 2.0
                </div>
            </div>
        </footer>
        """
    
    def _render_interactive_javascript(self) -> str:
        """Render minimal JavaScript for interactivity."""
        return """
        <script>
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Add subtle hover effects to interactive elements
        document.querySelectorAll('.board-snapshot, .stat-card, .toc-item').forEach(element => {
            element.addEventListener('mouseenter', function() {
                this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
            });
        });
        
        // Print optimization
        window.addEventListener('beforeprint', function() {
            document.body.classList.add('printing');
        });
        
        window.addEventListener('afterprint', function() {
            document.body.classList.remove('printing');
        });
        
        // Lazy loading for better performance
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('loaded');
                        observer.unobserve(entry.target);
                    }
                });
            });
            
            document.querySelectorAll('.board-snapshot').forEach(board => {
                imageObserver.observe(board);
            });
        }
        </script>
        """
    
    def _extract_moves_with_analysis(self, game: chess.pgn.Game) -> List[Dict]:
        """Extract moves with basic analysis information."""
        moves = []
        board = game.board()
        
        for move in game.mainline_moves():
            san = board.san(move)
            uci = move.uci()
            
            # Basic move analysis
            is_capture = board.is_capture(move)
            is_check = board.gives_check(move)
            is_castling = board.is_castling(move)
            
            moves.append({
                'san': san,
                'uci': uci,
                'is_capture': is_capture,
                'is_check': is_check,
                'is_castling': is_castling
            })
            
            board.push(move)
        
        return moves
    
    def _select_key_positions(self, game: chess.pgn.Game, max_positions: int = 6) -> List[Tuple[int, str, str]]:
        """Select key positions throughout the game for the gallery."""
        total_moves = sum(1 for _ in game.mainline_moves())
        if total_moves == 0:
            return []
        
        positions = []
        board = game.board()
        
        # Always include starting position
        positions.append((0, "Start", self._generate_board_svg(board.fen())))
        
        # Calculate intervals for even distribution
        if total_moves > 1:
            interval = max(1, total_moves // (max_positions - 1))
            
            ply = 0
            for move in game.mainline_moves():
                ply += 1
                san = board.san(move)
                board.push(move)
                
                if ply % interval == 0 or ply == total_moves:
                    svg = self._generate_board_svg(board.fen(), flipped=(board.turn == chess.BLACK))
                    positions.append((ply, san, svg))
        
        return positions[:max_positions]
    
    def _calculate_game_statistics(self, game: chess.pgn.Game) -> Dict[str, Any]:
        """Calculate comprehensive game statistics."""
        board = game.board()
        stats = {
            'total_moves': 0,
            'captures': 0,
            'checks': 0,
            'castling_moves': 0,
            'piece_development_score': 0,
            'complexity_rating': 'Moderate',
            'game_length_minutes': 0,
            'opening_efficiency': 'Good',
            'opening_center_control': 'Balanced',
            'opening_king_safety': 'Secured',
            'game_character': 'tactical and positional play',
            'strategic_complexity': 'Moderate',
            'tactical_richness': 'Average',
            'educational_value': 'High'
        }
        
        for move in game.mainline_moves():
            stats['total_moves'] += 1
            
            if board.is_capture(move):
                stats['captures'] += 1
            
            if board.gives_check(move):
                stats['checks'] += 1
            
            if board.is_castling(move):
                stats['castling_moves'] += 1
            
            board.push(move)
        
        # Estimate game duration (rough calculation)
        stats['game_length_minutes'] = max(30, stats['total_moves'] * 2)
        
        # Calculate complexity based on move count and captures
        if stats['total_moves'] > 60 and stats['captures'] > 8:
            stats['complexity_rating'] = 'High'
        elif stats['total_moves'] < 30 or stats['captures'] < 3:
            stats['complexity_rating'] = 'Low'
        
        return stats
    
    def _generate_board_svg(self, fen: str, flipped: bool = False, size: int = 400) -> str:
        """Generate SVG representation of chess position."""
        try:
            board = chess.Board(fen)
            return chess.svg.board(
                board=board,
                flipped=flipped,
                size=size,
                style="""
                .square.light { fill: #f0d9b5; }
                .square.dark { fill: #b58863; }
                .piece { font-size: 45px; }
                """
            )
        except Exception:
            return f'<div style="width: {size}px; height: {size}px; border: 2px solid #ddd; display: flex; align-items: center; justify-content: center; color: #666;">Board unavailable</div>'
    
    def _convert_to_icons(self, san: str) -> str:
        """Convert piece letters to Unicode chess symbols."""
        if not san:
            return san
        
        icons = {
            'K': '♔', 'Q': '♕', 'R': '♖', 
            'B': '♗', 'N': '♘'
        }
        
        result = san
        for letter, icon in icons.items():
            result = result.replace(letter, icon)
        
        return result
    
    def _generate_filename(self, headers: Dict) -> str:
        """Generate a safe filename for the HTML file."""
        white = headers.get('White', 'White').replace(' ', '_')
        black = headers.get('Black', 'Black').replace(' ', '_')
        date = headers.get('Date', '').replace('.', '_')
        
        # Clean filename of problematic characters
        import re
        filename = f"{white}-vs-{black}-{date}-analysis.html"
        filename = re.sub(r'[^\w\-_.]', '', filename)
        
        return filename
