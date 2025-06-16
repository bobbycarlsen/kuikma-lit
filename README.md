# Kuikma | Chess Trainer Application

A comprehensive, mobile-first chess training application that helps users improve their chess skills through targeted practice, complete game analysis, advanced insights, and spatial analysis.

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
pip (Python package manager)
```

### Installation
```bash
# Clone or download the application files
# Navigate to the application directory

# Install dependencies
pip install -r requirements.txt

# Run setup (creates database, admin user, etc.)
python setup.py

# Start the application
streamlit run app.py
```

### First Login
1. Open http://localhost:8501
2. Click "Admin" tab
3. Login with: admin@kuikma.com / passpass
4. Navigate to Settings to import your chess data

### First-Time Setup
1. **Initial Login**: Use `admin@kuikma.com` / `passpass`
2. **Import Data**: Navigate to Settings → Import Data
3. **Upload Positions**: Use JSONL files for training positions
4. **Import Games**: Upload PGN files for game analysis
5. **Start Training**: Go to Training tab and begin practice

## 📁 Project Structure

```
kuikma-chess-engine/
├── analysis.py                     # Advanced analysis tools
├── app.py                          # Main application
├── auth.py                         # Authentication and user management
├── chess_board.py                  # Chess board rendering
├── config.py                       # Application configuration
├── database.py                     # Enhanced database with full schema
├── game_analysis.py                # PGN game analysis
├── html_generator.py               # Single-file HTML template generator
├── insights.py                     # User insights and analytics
├── jsonl_processor.py              # Enhanced JSONL processor
├── pgn_loader.py                   # Fixed PGN import with name handling
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── settings.py                     # Comprehensive settings and import/export
├── setup.py                        # Setup and initialization script
├── spatial_analysis.py             # Spatial analysis tools (coming soon)
├── training.py                     # Training interface with HTML generation
└── data/
    ├── kuikma_chess.db             # Main database
    └── backups/                    # Database backups
└── kuikma_analysis/                # Generated HTML analyses
└── logs/                           # Application logs
```

# ♟️ Kuikma Chess Engine

**Advanced Chess Training & Analysis Platform**

A sophisticated chess training and analysis application built with Streamlit, featuring comprehensive position analysis, PGN game processing, and interactive learning tools with HTML export capabilities.

*[Screenshot/demo placeholder - Add screenshot of main interface]*

---

## 📑 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [Usage](#usage)
- [Modules Overview](#modules-overview)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Acknowledgements & Contact](#acknowledgements--contact)

---

## 🎯 Project Overview

**Kuikma Chess Engine** is an advanced chess training and analysis platform designed to help chess players improve their tactical and strategic skills. The application provides comprehensive position analysis, interactive training modules, and detailed performance insights with export capabilities.

### Key Highlights
- **Interactive Training**: Position-based training with move validation and feedback
- **Comprehensive Analysis**: Multi-dimensional chess position evaluation
- **PGN Support**: Import and analyze complete chess games
- **Performance Tracking**: Detailed user progress analytics
- **HTML Export**: Generate beautiful analysis reports
- **Multi-user Support**: User authentication and personalized experiences

---

## ✨ Features

### 3.1 🔐 Authentication
- **User Registration**: Sign up with email and password
- **Secure Login**: Session management with SHA-256 password hashing
- **Admin Access**: Separate admin role with database management capabilities
- **User Settings**: Personalized training preferences and themes
- **Session Management**: Automatic session tracking and timeout handling

### 3.2 🎯 Position Training Tab
- **Interactive Board**: FEN-based position display with SVG rendering
- **Smart Controls**: Next position, random selection, load by ID
- **Timer System**: Start/pause/resume with session tracking
- **Move Validation**: Real-time validation against engine best moves
- **Intelligent Feedback**: Centipawn loss calculation with classification badges (Excellent/Good/Okay/Poor)
- **Adaptive Learning**: Track user accuracy and adjust difficulty automatically
- **Previous Moves Display**: Complete move history with piece icons

### 3.3 📊 Comprehensive Analysis & HTML Export
- **Strategic Metrics**: 
  - Material balance and piece activity
  - Center control and spatial advantage
  - King safety and pawn structure analysis
  - Piece mobility and development evaluation
- **Variation Analysis**: Top-3 engine lines with detailed statistics
- **Learning Insights**: "What to look for next time" educational content
- **HTML Export**: Generate responsive, print-ready analysis reports
- **Offline Layout**: Mobile-friendly styling with page-break CSS optimization
- **Report Sections**: Problem statement, solution analysis, comparative statistics, and variation trees

### 3.4 📁 PGN Upload & Analysis
- **Multi-format Import**: Single file or batch PGN processing
- **Enhanced Parsing**: Robust move parsing with error handling
- **Player Name Correction**: Automatic handling of missing/invalid player names
- **Game Metadata**: Complete extraction of headers, ratings, and event information
- **Interactive Viewer**: Board visualization with move-by-move navigation
- **Automated Analysis**: Engine evaluation for each position

### 3.5 🔍 Game Search & Management
- **Advanced Filters**: 
  - Player names (White/Black)
  - Color preference and date ranges
  - Game results and ELO ratings
  - Opening ECO codes and events
- **Smart Pagination**: Efficient loading with customizable page sizes
- **Result Display**: Comprehensive table with sortable columns
- **Game Analytics**: Performance statistics and trend analysis
- **Save & Organize**: Personal game collections with tags and notes

---

## ⚙️ Configuration

### 4.1 Application Configuration (config.py)
The application uses configuration constants defined in `config.py`:

```python
# Database Configuration
DATABASE_PATH = "data/kuikma_chess.db"
BACKUP_PATH = "data/backups/"

# Admin Configuration
ADMIN_CONFIG = {
    'default_admin_email': 'admin@kuikma.com',
    'default_admin_password': 'passpass'
}

# Training Configuration
TRAINING_CONFIG = {
    'max_time_per_position': 300,  # 5 minutes
    'session_timeout': 3600,       # 1 hour
    'max_positions_per_session': 50
}

# HTML Export Configuration
HTML_CONFIG = {
    'output_directory': 'kuikma_analysis',
    'board_size': 400,
    'max_moves_display': 10
}
```
---

## 🗄️ Database Tables (SQLite)

### 5.1 **users** - User Management
### 5.2 **positions** - Chess Positions
### 5.3 **moves** - Position Moves & Analysis
### 5.4 **games** - Chess Games
### 5.5 **user_moves** - Training Session Data
### 5.6 **user_saved_games** - User Uploaded/Saved Games
### 5.7 **user_game_analysis** - User Analyzed Games
### 5.8 **user_game_sessions** - Session Tracking
### 5.9 **user_insights_cache** - User Insights Cache
### 5.10 **user_move_analysis** - User Move Analysis
### 5.11 **training_sessions** - Session Tracking
---

## 🧩 Modules Overview

### 6.1 **auth.py** - Authentication System
- User registration and login functionality
- SHA-256 password hashing with salt
- Session management and admin role checking
- User settings management (preferences, themes)
- Account deletion with cascade cleanup

### 6.2 **training.py** - Interactive Training
- Position loading with difficulty adaptation
- Move validation against engine analysis
- Timer functionality with pause/resume
- Performance feedback and classification
- HTML report generation for training sessions
- Session statistics and progress tracking

### 6.3 **analysis.py** - Chess Position Analysis
- Multi-dimensional position evaluation
- Engine interface for move analysis
- Strategic metrics computation (material, mobility, king safety)
- Variation extraction and comparative analysis
- Learning insights generation

### 6.4 **pgn_loader.py** - PGN Game Processing
- Robust PGN file parsing with error handling
- Enhanced player name extraction and correction
- Game metadata extraction (ELO, event, opening)
- Batch import capabilities with progress tracking
- Move sequence validation and storage

### 6.5 **database.py** - Database Operations
- SQLite connection management with connection pooling
- Schema creation and migration handling
- CRUD operations with transaction safety
- Database optimization and maintenance
- Export/import functionality with backup management

### 6.6 **chess_board.py** - Board Visualization
- SVG chess board rendering
- Interactive piece movement
- Position highlighting and move indicators
- Responsive design for mobile devices
- Custom piece sets and board themes

### 6.7 **html_generator.py** - Report Generation
- Comprehensive HTML analysis reports
- Responsive design with print optimization
- Interactive move trees and variation analysis
- CSS styling with mobile-friendly layouts
- Embedded board positions and statistics

### 6.8 **jsonl_processor.py** - Process Positions JSONL data into Positions Table, Moves Table etc.

### 6.9 **game_analysis.py** - Game Analysis module; more features to come
### 6.10 **settings.py** - Complete App Settings with Database Viewer (sanity check, optimize db, crud ops on all tables, export db, reset db etc.), Admin Panel (user management, system stats, maintenance), 
### 6.11 **setup.py** - One-time Setup
### 6.12 **spatial_analysis.py** - Complete Spatial Analysis of Chess Positions; more features to come
### 6.13 **insights.py** - Complete Insights of Chess Positions; more features to come

---


## 🔧 Troubleshooting

### 11.1 Common Installation Issues
- **Unicode Errors (Windows)**: Run `chcp 65001` in command prompt
- **Permission Errors**: Ensure write access to `data/` directory
- **Port Already in Use**: Use `--server.port 8080` to change port
- **Python Version**: Ensure Python 3.8+ is installed

### 11.2 Database Issues
- **Database Locked**: Close other connections, check for hanging processes
- **Corruption Recovery**: Use database backup from `data/backups/`
- **Migration Errors**: Delete database file and run `python setup.py`
- **Performance Issues**: Run database optimization in Admin panel

### 11.3 Engine Configuration
- **Engine Path**: Verify `ENGINE_PATH` in configuration
- **Permissions**: Ensure execute permissions on engine binary
- **Engine Not Found**: Install Stockfish or configure custom engine
- **Analysis Timeout**: Increase depth limits in advanced settings

### 11.4 Streamlit Configuration
- **Page Config Error**: Ensure `st.set_page_config()` is at the top of `app.py`
- **Session State Issues**: Clear browser cache and restart application
- **Memory Issues**: Reduce batch sizes in import configuration
- **CSS Not Loading**: Check static file paths and clear browser cache

### 11.5 Positions Issues
- **Incorrect or Empty Last Moves**
    - Execute
        -- 1. Get total count of bad entries
        -- 2. Delete those rows

```
SELECT COUNT(*) AS zero_last_move_count
FROM positions
WHERE json_extract(last_move, '$.move_number') = 0;
DELETE FROM positions
WHERE json_extract(last_move, '$.move_number') = 0;

```
---

## 🙏 Acknowledgements & Contact

### Libraries & Tools
- **[Streamlit](https://streamlit.io/)** - Web application framework
- **[python-chess](https://python-chess.readthedocs.io/)** - Chess library for Python
- **[SQLite3](https://www.sqlite.org/)** - Embedded database engine
- **[Plotly](https://plotly.com/python/)** - Interactive visualization library
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis

### Development Tools
- **[Black](https://black.readthedocs.io/)** - Code formatting
- **[pytest](https://pytest.org/)** - Testing framework
- **[Coverage.py](https://coverage.readthedocs.io/)** - Code coverage measurement

### Special Thanks
- Chess engine analysis powered by open-source chess engines
- Community contributors and beta testers
- Chess education resources and training methodologies

### 📧 Contact & Support
- **Maintainer**: [Your Name] <your.email@example.com>
- **Issues**: Report bugs via [GitHub Issues](https://github.com/yourusername/kuikma-chess-engine/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/yourusername/kuikma-chess-engine/discussions)
- **Documentation**: Comprehensive guides available in the [Wiki](https://github.com/yourusername/kuikma-chess-engine/wiki)

---

**🎯 Happy Chess Training with Kuikma Chess Engine!**

*Built with ♟️ for chess enthusiasts and developers*