# chess_engine/database.py - Enhanced Database for Kuikma Chess Engine
import sqlite3
import json
import hashlib
from datetime import datetime
import os
import shutil
from typing import Dict, Any, List, Optional, Tuple

from datetime import datetime, timedelta
from pathlib import Path

# Import existing database functionality and extend it
from config import config


def create_admin_user():
    """Create default admin user if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if admin user exists
        cursor.execute('SELECT id FROM users WHERE email = ?', ('admin@kuikma.com',))
        if cursor.fetchone():
            conn.close()
            return
        
        # Create admin user
        password_hash = hashlib.sha256('passpass'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (email, password_hash, created_at, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin@kuikma.com', password_hash, datetime.now().isoformat(), True))
        
        conn.commit()
        print("✅ Admin user created: admin@kuikma.com / passpass")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        conn.close()

def init_db():
    """Initialize the enhanced database tables for Kuikma Chess Engine."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enhanced Users table with admin flag
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_admin BOOLEAN DEFAULT FALSE
    )
    ''')
    
    # Enhanced Positions table with comprehensive JSONL data support
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY,
        fen TEXT NOT NULL,
        turn TEXT NOT NULL,
        fullmove_number INTEGER NOT NULL,
        halfmove_clock INTEGER DEFAULT 0,
        castling_rights TEXT,
        en_passant TEXT,
        
        -- Move history data
        move_history TEXT,
        last_move TEXT,
        
        -- Engine analysis data
        engine_depth INTEGER,
        analysis_time REAL,
        
        -- Position metrics (Rich JSONL Data)
        material_analysis TEXT,
        mobility_analysis TEXT,
        king_safety_analysis TEXT,
        center_control_analysis TEXT,
        pawn_structure_analysis TEXT,
        piece_development_analysis TEXT,
        
        -- Comprehensive analysis
        comprehensive_analysis TEXT,
        variation_analysis TEXT,
        learning_insights TEXT,
        
        -- Visualization data
        visualization_data TEXT,
        
        -- Position classification
        position_classification TEXT,
        game_phase TEXT NOT NULL DEFAULT 'middlegame',
        difficulty_rating INTEGER DEFAULT 1200,
        themes TEXT,
        position_type TEXT DEFAULT 'tactical',
        
        -- Source information
        source_type TEXT DEFAULT 'upload',
        title TEXT,
        description TEXT,
        solution_moves TEXT,
        
        -- Processing metadata
        timestamp TEXT,
        processed_timestamp TEXT,
        processing_quality TEXT DEFAULT 'standard',
        
        UNIQUE(fen)
    )
    ''')
    
    # Enhanced Moves table with comprehensive move analysis
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS moves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        position_id INTEGER NOT NULL,
        move TEXT NOT NULL,
        uci TEXT NOT NULL,
        score INTEGER NOT NULL,
        depth INTEGER NOT NULL,
        centipawn_loss INTEGER NOT NULL,
        classification TEXT NOT NULL,
        principal_variation TEXT,
        tactics TEXT,
        position_impact TEXT,
        ml_evaluation TEXT,
        move_complexity REAL,
        strategic_value REAL,
        rank INTEGER NOT NULL,
        FOREIGN KEY (position_id) REFERENCES positions (id),
        UNIQUE(position_id, move)
    )
    ''')
    
    # Enhanced UserMoves table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_moves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        position_id INTEGER NOT NULL,
        move_id INTEGER NOT NULL,
        time_taken REAL NOT NULL,
        result TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        openai_analysis TEXT,
        session_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (position_id) REFERENCES positions (id),
        FOREIGN KEY (move_id) REFERENCES moves (id)
    )
    ''')
    
    # User Settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_settings (
        user_id INTEGER PRIMARY KEY,
        random_positions BOOLEAN DEFAULT TRUE,
        top_n_threshold INTEGER DEFAULT 3,
        score_difference_threshold INTEGER DEFAULT 10,
        theme TEXT DEFAULT 'default',
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Enhanced analysis tracking table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_move_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        move_record_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        analysis_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (move_record_id) REFERENCES user_moves (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # User insights cache table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_insights_cache (
        user_id INTEGER PRIMARY KEY,
        insights_data TEXT NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Training sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS training_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_id TEXT NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        total_moves INTEGER DEFAULT 0,
        correct_moves INTEGER DEFAULT 0,
        session_metadata TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Enhanced Games table with better player name handling
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pgn_source TEXT,
        game_index INTEGER,
        white_player TEXT NOT NULL DEFAULT 'Unknown',
        black_player TEXT NOT NULL DEFAULT 'Unknown',
        white_elo INTEGER,
        black_elo INTEGER,
        result TEXT,
        date TEXT,
        event TEXT,
        site TEXT,
        round TEXT,
        opening TEXT,
        eco_code TEXT,
        time_control TEXT,
        total_moves INTEGER,
        pgn_text TEXT,
        moves_data TEXT,
        positions_data TEXT,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # User game analysis table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_game_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        analysis_status TEXT DEFAULT 'not_started',
        current_move_index INTEGER DEFAULT 0,
        total_time_spent REAL DEFAULT 0,
        moves_analyzed INTEGER DEFAULT 0,
        correct_moves INTEGER DEFAULT 0,
        notes TEXT,
        analysis_data TEXT,
        last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (game_id) REFERENCES games (id),
        UNIQUE(user_id, game_id)
    )
    ''')
    
    # Saved games table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_saved_games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        tags TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (game_id) REFERENCES games (id),
        UNIQUE(user_id, game_id)
    )
    ''')
    
    # User game sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_game_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_type TEXT DEFAULT 'game_analysis',
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        games_analyzed INTEGER DEFAULT 0,
        total_moves_analyzed INTEGER DEFAULT 0,
        session_metadata TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create performance indexes
    index_statements = [
        'CREATE INDEX IF NOT EXISTS idx_user_moves_user_id ON user_moves(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_user_moves_timestamp ON user_moves(timestamp)',
        'CREATE INDEX IF NOT EXISTS idx_user_move_analysis_user_id ON user_move_analysis(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_positions_fullmove ON positions(fullmove_number)',
        'CREATE INDEX IF NOT EXISTS idx_positions_difficulty ON positions(difficulty_rating)',
        'CREATE INDEX IF NOT EXISTS idx_positions_game_phase ON positions(game_phase)',
        'CREATE INDEX IF NOT EXISTS idx_moves_position_rank ON moves(position_id, rank)',
        'CREATE INDEX IF NOT EXISTS idx_games_white_player ON games(white_player)',
        'CREATE INDEX IF NOT EXISTS idx_games_black_player ON games(black_player)',
        'CREATE INDEX IF NOT EXISTS idx_games_date ON games(date)',
        'CREATE INDEX IF NOT EXISTS idx_games_result ON games(result)',
        'CREATE INDEX IF NOT EXISTS idx_games_opening ON games(opening)',
        'CREATE INDEX IF NOT EXISTS idx_user_game_analysis_user_id ON user_game_analysis(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_user_game_analysis_status ON user_game_analysis(analysis_status)',
        'CREATE INDEX IF NOT EXISTS idx_user_saved_games ON user_saved_games(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_games_players ON games(white_player, black_player)',
        'CREATE INDEX IF NOT EXISTS idx_user_moves_result ON user_moves(user_id, result)',
        'CREATE INDEX IF NOT EXISTS idx_user_moves_position ON user_moves(position_id)',
        'CREATE INDEX IF NOT EXISTS idx_moves_score ON moves(position_id, score DESC)',
        'CREATE INDEX IF NOT EXISTS idx_positions_turn ON positions(turn)',
        'CREATE INDEX IF NOT EXISTS idx_analysis_user_created ON user_move_analysis(user_id, created_at DESC)'
    ]
    
    for index_sql in index_statements:
        try:
            cursor.execute(index_sql)
        except sqlite3.Error as e:
            print(f"Index creation warning: {e}")
    
    conn.commit()
    conn.close()

def load_positions_from_enhanced_jsonl(jsonl_processor, jsonl_content: str) -> Dict[str, Any]:
    """
    Load positions from enhanced JSONL content using the new processor.
    
    Args:
        jsonl_processor: Instance of enhanced JSONLProcessor
        jsonl_content: String content of JSONL file
        
    Returns:
        Dictionary with loading results
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Process JSONL content using enhanced processor
        positions = jsonl_processor.process_jsonl_content(jsonl_content)
        
        positions_loaded = 0
        errors_encountered = 0
        
        for position_data in positions:
            try:
                # Insert position with all enhanced fields
                cursor.execute('''
                    INSERT OR REPLACE INTO positions (
                        id, fen, turn, fullmove_number, halfmove_clock, castling_rights, en_passant,
                        move_history, last_move, engine_depth, analysis_time,
                        material_analysis, mobility_analysis, king_safety_analysis, center_control_analysis,
                        pawn_structure_analysis, piece_development_analysis, comprehensive_analysis,
                        variation_analysis, learning_insights, visualization_data, position_classification,
                        game_phase, difficulty_rating, themes, position_type, source_type, title,
                        description, solution_moves, timestamp, processed_timestamp, processing_quality
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    position_data.get('id'),
                    position_data['fen'],
                    position_data['turn'],
                    position_data['fullmove_number'],
                    position_data.get('halfmove_clock', 0),
                    position_data.get('castling_rights'),
                    position_data.get('en_passant'),
                    json.dumps(position_data.get('move_history', {})),
                    json.dumps(position_data.get('last_move', {})),
                    position_data.get('engine_depth'),
                    position_data.get('analysis_time'),
                    json.dumps(position_data.get('material_analysis', {})),
                    json.dumps(position_data.get('mobility_analysis', {})),
                    json.dumps(position_data.get('king_safety_analysis', {})),
                    json.dumps(position_data.get('center_control_analysis', {})),
                    json.dumps(position_data.get('pawn_structure_analysis', {})),
                    json.dumps(position_data.get('piece_development_analysis', {})),
                    json.dumps(position_data.get('comprehensive_analysis', {})),
                    json.dumps(position_data.get('variation_analysis', {})),
                    json.dumps(position_data.get('learning_insights', {})),
                    json.dumps(position_data.get('visualization_data', {})),
                    json.dumps(position_data.get('position_classification', [])),
                    position_data['game_phase'],
                    position_data['difficulty_rating'],
                    json.dumps(position_data.get('themes', [])),
                    position_data.get('position_type', 'tactical'),
                    position_data.get('source_type', 'upload'),
                    position_data.get('title', ''),
                    position_data.get('description', ''),
                    json.dumps(position_data.get('solution_moves', [])),
                    position_data.get('timestamp'),
                    position_data.get('processed_timestamp'),
                    position_data.get('processing_quality', 'standard')
                ))
                
                position_id = position_data.get('id') or cursor.lastrowid
                
                # Insert enhanced top moves
                for move_data in position_data.get('top_moves', []):
                    cursor.execute('''
                        INSERT OR REPLACE INTO moves (
                            position_id, move, uci, score, depth, centipawn_loss, classification,
                            principal_variation, tactics, position_impact, ml_evaluation,
                            move_complexity, strategic_value, rank
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        position_id,
                        move_data.get('move'),
                        move_data.get('uci', ''),
                        move_data.get('score', 0),
                        move_data.get('depth', 0),
                        move_data.get('centipawn_loss', 0),
                        move_data.get('classification', 'unknown'),
                        move_data.get('pv', ''),
                        json.dumps(move_data.get('tactics', [])),
                        json.dumps(move_data.get('position_impact', {})),
                        json.dumps(move_data.get('ml_evaluation', {})),
                        round(move_data.get('move_complexity', 0.0), 3),
                        round(move_data.get('strategic_value', 0.0), 3),
                        move_data.get('rank', 1)
                    ))
                
                positions_loaded += 1
                
            except Exception as e:
                errors_encountered += 1
                print(f"Error loading position: {e}")
                continue
        
        conn.commit()
        
        # Get processor statistics
        stats = jsonl_processor.get_processing_stats()
        
        return {
            'success': True,
            'positions_loaded': positions_loaded,
            'errors_encountered': errors_encountered,
            'processor_stats': stats
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'positions_loaded': 0
        }
    finally:
        conn.close()

def store_pgn_games(games_data, pgn_source="uploaded"):
    """
    Enhanced PGN games storage with better player name handling.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    games_stored = 0
    errors = 0
    
    for game_index, game_data in enumerate(games_data):
        try:
            headers = game_data.get('headers', {})
            moves = game_data.get('moves', [])
            positions = game_data.get('positions', [])
            
            # Enhanced player name extraction with fallback handling
            white_player = headers.get('White', '').strip()
            black_player = headers.get('Black', '').strip()
            
            # Handle empty or missing player names
            if not white_player or white_player in ['', '?', '-']:
                white_player = f"White Player {game_index + 1}"
            if not black_player or black_player in ['', '?', '-']:
                black_player = f"Black Player {game_index + 1}"
            
            # Extract other game information
            result = headers.get('Result', '*')
            date = headers.get('Date', 'Unknown')
            event = headers.get('Event', 'Unknown')
            site = headers.get('Site', 'Unknown')
            round_num = headers.get('Round', 'Unknown')
            opening = headers.get('Opening', '')
            eco_code = headers.get('ECO', '')
            time_control = headers.get('TimeControl', '')
            
            # Parse ELO ratings safely
            try:
                white_elo = int(headers.get('WhiteElo', 0)) if headers.get('WhiteElo', '').replace('-', '').isdigit() else None
                black_elo = int(headers.get('BlackElo', 0)) if headers.get('BlackElo', '').replace('-', '').isdigit() else None
            except (ValueError, TypeError):
                white_elo = None
                black_elo = None
            
            total_moves = len(moves)
            
            # Create enhanced metadata
            metadata = {
                'termination': headers.get('Termination', 'Unknown'),
                'annotator': headers.get('Annotator', ''),
                'ply_count': headers.get('PlyCount', ''),
                'setup': headers.get('Setup', ''),
                'variant': headers.get('Variant', ''),
                'imported_at': datetime.now().isoformat(),
                'source_file': pgn_source
            }
            
            # Insert game with enhanced data
            cursor.execute('''
                INSERT INTO games (
                    pgn_source, game_index, white_player, black_player, 
                    white_elo, black_elo, result, date, event, site, round,
                    opening, eco_code, time_control, total_moves,
                    moves_data, positions_data, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pgn_source, game_index, white_player, black_player,
                white_elo, black_elo, result, date, event, site, round_num,
                opening, eco_code, time_control, total_moves,
                json.dumps(moves), json.dumps(positions), json.dumps(metadata)
            ))
            
            games_stored += 1
            
        except Exception as e:
            errors += 1
            print(f"Error storing game {game_index}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    return {
        'games_stored': games_stored,
        'errors': errors,
        'total_processed': len(games_data)
    }

def get_all_tables():
    """Get list of all tables in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return tables

def get_table_info(table_name: str):
    """Get schema information for a specific table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        return {
            'columns': columns,
            'row_count': row_count
        }
    except Exception as e:
        return {'error': str(e)}
    finally:
        conn.close()

def get_table_data(table_name: str, limit: int = 100, offset: int = 0):
    """Get data from a specific table with pagination."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get data with limit and offset
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (limit, offset))
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = [dict(row) for row in rows]
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        
        return {
            'data': data,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        }
    except Exception as e:
        return {'error': str(e)}
    finally:
        conn.close()

def delete_table_row(table_name: str, row_id: int):
    """Delete a specific row from a table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting row: {e}")
        return False
    finally:
        conn.close()

def update_table_row(table_name: str, row_id: int, data: Dict[str, Any]):
    """Update a specific row in a table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build UPDATE query dynamically
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = list(data.values()) + [row_id]
        
        cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating row: {e}")
        return False
    finally:
        conn.close()

def reset_database(reset_type: str = "complete"):
    """
    Reset database with different options.
    
    Args:
        reset_type: 'complete', 'positions_only', 'users_only', 'games_only'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if reset_type == "complete":
            # Drop all tables and recreate
            tables = get_all_tables()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            conn.commit()
            conn.close()
            init_db()
            create_admin_user()
            return True
            
        elif reset_type == "positions_only":
            cursor.execute("DELETE FROM user_moves")
            cursor.execute("DELETE FROM moves")
            cursor.execute("DELETE FROM positions")
            cursor.execute("DELETE FROM user_move_analysis")
            cursor.execute("DELETE FROM training_sessions")
            
        elif reset_type == "users_only":
            cursor.execute("DELETE FROM user_moves")
            cursor.execute("DELETE FROM user_move_analysis")
            cursor.execute("DELETE FROM user_settings")
            cursor.execute("DELETE FROM training_sessions")
            cursor.execute("DELETE FROM user_game_analysis")
            cursor.execute("DELETE FROM user_saved_games")
            cursor.execute("DELETE FROM user_game_sessions")
            cursor.execute("DELETE FROM user_insights_cache")
            cursor.execute("DELETE FROM users")
            
        elif reset_type == "games_only":
            cursor.execute("DELETE FROM user_game_analysis")
            cursor.execute("DELETE FROM user_saved_games")
            cursor.execute("DELETE FROM user_game_sessions")
            cursor.execute("DELETE FROM games")
        
        conn.commit()
        
        # Recreate admin user if users were reset
        if reset_type in ["complete", "users_only"]:
            conn.close()
            create_admin_user()
        else:
            conn.close()
            
        return True
        
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False

def database_sanity_check():
    """Perform comprehensive database sanity check."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    issues = []
    stats = {}
    
    try:
        # Check all tables exist
        tables = get_all_tables()
        expected_tables = [
            'users', 'positions', 'moves', 'user_moves', 'user_settings',
            'games', 'user_game_analysis', 'user_saved_games', 'training_sessions'
        ]
        
        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            issues.append(f"Missing tables: {missing_tables}")
        
        # Check table counts and integrity
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
                
                # Check for orphaned records
                if table == 'moves':
                    cursor.execute('''
                        SELECT COUNT(*) FROM moves m 
                        LEFT JOIN positions p ON m.position_id = p.id 
                        WHERE p.id IS NULL
                    ''')
                    orphaned = cursor.fetchone()[0]
                    if orphaned > 0:
                        issues.append(f"Found {orphaned} orphaned moves")
                
                elif table == 'user_moves':
                    cursor.execute('''
                        SELECT COUNT(*) FROM user_moves um 
                        LEFT JOIN users u ON um.user_id = u.id 
                        WHERE u.id IS NULL
                    ''')
                    orphaned = cursor.fetchone()[0]
                    if orphaned > 0:
                        issues.append(f"Found {orphaned} orphaned user moves")
                        
            except Exception as e:
                issues.append(f"Error checking table {table}: {e}")
        
        # Check for positions without moves
        cursor.execute('''
            SELECT COUNT(*) FROM positions p 
            LEFT JOIN moves m ON p.id = m.position_id 
            WHERE m.id IS NULL
        ''')
        positions_without_moves = cursor.fetchone()[0]
        if positions_without_moves > 0:
            issues.append(f"Found {positions_without_moves} positions without moves")
        
        return {
            'healthy': len(issues) == 0,
            'issues': issues,
            'stats': stats,
            'total_tables': len(tables)
        }
        
    except Exception as e:
        return {
            'healthy': False,
            'issues': [f"Sanity check failed: {e}"],
            'stats': stats
        }
    finally:
        conn.close()

def export_database_with_schema():
    """Export complete database with schema and data."""
    try:
        source_path = 'data/kuikma_chess.db'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = f'data/kuikma_export_{timestamp}.db'
        
        # Copy database file
        shutil.copy2(source_path, export_path)
        
        return export_path
    except Exception as e:
        print(f"Error exporting database: {e}")
        return None

def optimize_database():
    """Optimize database performance."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Analyze tables for query optimization
        cursor.execute("ANALYZE")
        
        # Vacuum database to reclaim space
        cursor.execute("VACUUM")
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error optimizing database: {e}")
        return False
    finally:
        conn.close()

def get_db_connection():
    """Get database connection with enhanced configuration."""
    db_path = config.DATABASE_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA journal_mode = WAL')

    return conn

def create_enhanced_tables():
    """Create enhanced tables for user verification and subscription management."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Enhanced users table (modify existing)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_admin BOOLEAN DEFAULT FALSE,
            is_verified BOOLEAN DEFAULT FALSE,
            verification_status TEXT DEFAULT 'pending',
            verified_at TIMESTAMP,
            verified_by INTEGER,
            full_name TEXT,
            profile_notes TEXT,
            account_status TEXT DEFAULT 'active',
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            FOREIGN KEY (verified_by) REFERENCES users (id)
        )
        ''')
        
        # User verification requests table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_verification_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            request_type TEXT DEFAULT 'manual_verification',
            request_data TEXT,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            reviewed_by INTEGER,
            status TEXT DEFAULT 'pending',
            admin_notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (reviewed_by) REFERENCES users (id)
        )
        ''')
        
        # User subscriptions/limits table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            subscription_type TEXT DEFAULT 'basic',
            position_limit INTEGER DEFAULT 100,
            analysis_limit INTEGER DEFAULT 50,
            game_upload_limit INTEGER DEFAULT 20,
            positions_used INTEGER DEFAULT 0,
            analyses_used INTEGER DEFAULT 0,
            games_uploaded INTEGER DEFAULT 0,
            reset_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (updated_by) REFERENCES users (id)
        )
        ''')
        
        # Feature access control table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_feature_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            feature_name TEXT NOT NULL,
            access_granted BOOLEAN DEFAULT FALSE,
            granted_at TIMESTAMP,
            granted_by INTEGER,
            expires_at TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (granted_by) REFERENCES users (id),
            UNIQUE(user_id, feature_name)
        )
        ''')
        
        # Admin audit log table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_user_id INTEGER,
            target_resource TEXT,
            action_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (admin_user_id) REFERENCES users (id),
            FOREIGN KEY (target_user_id) REFERENCES users (id)
        )
        ''')
        
        # User session tracking table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT NOT NULL UNIQUE,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create indexes for performance
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
            'CREATE INDEX IF NOT EXISTS idx_users_verification_status ON users(verification_status)',
            'CREATE INDEX IF NOT EXISTS idx_verification_requests_user_id ON user_verification_requests(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_verification_requests_status ON user_verification_requests(status)',
            'CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON user_subscriptions(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_feature_access_user_id ON user_feature_access(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_audit_log_admin_user ON admin_audit_log(admin_user_id)',
            'CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON admin_audit_log(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token)',
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error creating enhanced tables: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def upgrade_existing_database():
    """Upgrade existing database to support new features."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if we need to add new columns to existing users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        new_columns = [
            ('is_verified', 'BOOLEAN DEFAULT FALSE'),
            ('verification_status', 'TEXT DEFAULT "pending"'),
            ('verified_at', 'TIMESTAMP'),
            ('verified_by', 'INTEGER'),
            ('full_name', 'TEXT'),
            ('profile_notes', 'TEXT'),
            ('account_status', 'TEXT DEFAULT "active"'),
            ('failed_login_attempts', 'INTEGER DEFAULT 0'),
            ('locked_until', 'TIMESTAMP'),
        ]
        
        for col_name, col_def in new_columns:
            if col_name not in columns:
                cursor.execute(f'ALTER TABLE users ADD COLUMN {col_name} {col_def}')
                print(f"Added column {col_name} to users table")
        
        # Create new tables
        create_enhanced_tables()
        
        # Auto-verify admin users and existing users if configured
        if config.AUTO_APPROVE_USERS:
            cursor.execute('''
                UPDATE users 
                SET is_verified = TRUE, verification_status = 'approved', verified_at = ?
                WHERE is_verified IS NULL OR is_verified = FALSE
            ''', (datetime.now().isoformat(),))
            print("Auto-approved existing users")
        
        # Ensure admin user is always verified
        cursor.execute('''
            UPDATE users 
            SET is_verified = TRUE, verification_status = 'approved', verified_at = ?
            WHERE is_admin = TRUE
        ''', (datetime.now().isoformat(),))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error upgrading database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_user_subscription(user_id: int, admin_user_id: Optional[int] = None) -> bool:
    """Create default subscription for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if subscription already exists
        cursor.execute('SELECT id FROM user_subscriptions WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            return True  # Already exists
        
        # Create default subscription
        reset_date = (datetime.now() + timedelta(days=30)).date()
        
        cursor.execute('''
            INSERT INTO user_subscriptions (
                user_id, subscription_type, position_limit, analysis_limit, 
                game_upload_limit, reset_date, updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 'basic',
            config.DEFAULT_POSITION_LIMIT,
            config.DEFAULT_ANALYSIS_LIMIT,
            config.DEFAULT_GAME_UPLOAD_LIMIT,
            reset_date,
            admin_user_id
        ))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error creating user subscription: {e}")
        return False
    finally:
        conn.close()

def log_admin_action(admin_user_id: int, action: str, target_user_id: Optional[int] = None, 
                    target_resource: Optional[str] = None, action_data: Optional[Dict] = None) -> bool:
    """Log admin action for audit trail."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO admin_audit_log (
                admin_user_id, action, target_user_id, target_resource, action_data
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            admin_user_id, action, target_user_id, target_resource,
            json.dumps(action_data) if action_data else None
        ))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error logging admin action: {e}")
        return False
    finally:
        conn.close()

def get_user_verification_stats() -> Dict[str, int]:
    """Get user verification statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        stats['total_users'] = cursor.fetchone()[0]
        
        # Verified users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_verified = TRUE')
        stats['verified_users'] = cursor.fetchone()[0]
        
        # Pending verification
        cursor.execute('SELECT COUNT(*) FROM users WHERE verification_status = "pending"')
        stats['pending_verification'] = cursor.fetchone()[0]
        
        # Admin users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = TRUE')
        stats['admin_users'] = cursor.fetchone()[0]
        
        # Recent registrations (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM users WHERE created_at > ?', (week_ago,))
        stats['recent_registrations'] = cursor.fetchone()[0]
        
        return stats
        
    except Exception as e:
        print(f"Error getting verification stats: {e}")
        return {}
    finally:
        conn.close()

def get_subscription_usage_stats() -> Dict[str, Any]:
    """Get subscription usage statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        # Average usage
        cursor.execute('''
            SELECT 
                AVG(positions_used) as avg_positions,
                AVG(analyses_used) as avg_analyses,
                AVG(games_uploaded) as avg_games
            FROM user_subscriptions
        ''')
        result = cursor.fetchone()
        if result:
            stats['average_usage'] = {
                'positions': round(result[0] or 0, 2),
                'analyses': round(result[1] or 0, 2),
                'games': round(result[2] or 0, 2)
            }
        
        # Users near limits
        cursor.execute('''
            SELECT COUNT(*) FROM user_subscriptions 
            WHERE positions_used >= position_limit * 0.9
        ''')
        stats['users_near_position_limit'] = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM user_subscriptions 
            WHERE analyses_used >= analysis_limit * 0.9
        ''')
        stats['users_near_analysis_limit'] = cursor.fetchone()[0]
        
        return stats
        
    except Exception as e:
        print(f"Error getting subscription stats: {e}")
        return {}
    finally:
        conn.close()

# Initialize enhanced database on import
if __name__ == "__main__":

    # Initialize the enhanced database
    init_db()
    
    # Create admin user
    create_admin_user()
    
    # Optimize database
    optimize_database()

    print("Initializing enhanced database...")
    create_enhanced_tables()
    upgrade_existing_database()
    print("Enhanced database initialization complete.")
    print("✅ Enhanced Kuikma Chess Engine database initialized successfully!")
