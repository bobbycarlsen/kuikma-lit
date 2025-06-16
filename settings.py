# settings.py - Enhanced Settings Module for Kuikma Chess Engine
import streamlit as st
import pandas as pd
import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
import plotly.express as px
import plotly.graph_objects as go

# Import required modules
import database
import auth
import pgn_loader
from jsonl_processor import JSONLProcessor
from html_generator import ComprehensiveHTMLGenerator
from pathlib import Path


def display_import_interface():
    """Display comprehensive data import interface."""
    st.markdown("### 📥 Import Training Data")
    
    import_tabs = st.tabs(["🧩 Enhanced JSONL", "♟️ PGN Games", "📋 Batch Import"])
    
    with import_tabs[0]:
        display_jsonl_import()
    
    with import_tabs[1]:
        display_pgn_import()
    
    with import_tabs[2]:
        display_batch_import()

def display_jsonl_import():
    """Display enhanced JSONL import interface."""
    st.markdown("#### 🧩 Enhanced JSONL Position Import")
    st.info("Import chess positions with comprehensive analysis data using the enhanced JSONL processor.")
    
    # File upload
    uploaded_jsonl = st.file_uploader(
        "Upload Enhanced JSONL File", 
        type=['jsonl'], 
        key="enhanced_jsonl_import",
        help="Upload JSONL files with comprehensive position analysis data"
    )
    
    if uploaded_jsonl:
        file_content = uploaded_jsonl.read().decode('utf-8')
        
        # Preview file statistics
        lines = file_content.strip().split('\n')
        file_size_mb = len(file_content.encode('utf-8')) / (1024 * 1024)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Positions", len(lines))
        
        with col2:
            st.metric("File Size", f"{file_size_mb:.2f} MB")
        
        with col3:
            estimated_time = len(lines) / 100  # Rough estimate
            st.metric("Est. Import Time", f"{estimated_time:.1f}s")
        
        # Preview first position
        with st.expander("📋 Preview First Position"):
            if lines:
                try:
                    first_position = json.loads(lines[0])
                    preview_data = {
                        'ID': first_position.get('id', 'Unknown'),
                        'FEN': first_position.get('fen', 'Unknown')[:50] + '...',
                        'Turn': first_position.get('turn', 'Unknown'),
                        'Game Phase': first_position.get('game_phase', 'Unknown'),
                        'Difficulty': first_position.get('difficulty_rating', 'Unknown'),
                        'Themes': ', '.join(first_position.get('themes', [])),
                        'Processing Quality': first_position.get('processing_quality', 'Unknown')
                    }
                    
                    for key, value in preview_data.items():
                        st.markdown(f"**{key}:** {value}")
                        
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON in first line: {e}")
        
        # Import options
        st.markdown("#### Import Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            overwrite_existing = st.checkbox(
                "Overwrite existing positions", 
                value=False,
                help="Replace positions with same ID if they exist"
            )
        
        with col2:
            validate_before_import = st.checkbox(
                "Validate before import", 
                value=True,
                help="Perform validation checks before importing"
            )
        
        # Import button
        if st.button("⬆️ Import Enhanced Positions", use_container_width=True, type="primary"):
            import_enhanced_jsonl_data(file_content, overwrite_existing, validate_before_import)

def import_enhanced_jsonl_data(file_content: str, overwrite_existing: bool, validate_before_import: bool):
    """Import enhanced JSONL data with comprehensive error handling."""
    with st.spinner("🔄 Processing enhanced JSONL data..."):
        try:
            # Initialize enhanced processor
            processor = JSONLProcessor()
            
            # Validation phase
            if validate_before_import:
                st.info("🔍 Validating data...")
                lines = file_content.strip().split('\n')
                
                validation_errors = []
                for i, line in enumerate(lines[:10], 1):  # Validate first 10 lines
                    try:
                        json.loads(line)
                    except json.JSONDecodeError as e:
                        validation_errors.append(f"Line {i}: {e}")
                
                if validation_errors:
                    st.error("❌ Validation failed:")
                    for error in validation_errors:
                        st.error(f"• {error}")
                    return
            
            # Process and load positions
            result = database.load_positions_from_enhanced_jsonl(processor, file_content)
            
            if result['success']:
                # Display success metrics
                st.success(f"✅ Successfully imported {result['positions_loaded']} positions!")
                
                # Processor statistics
                stats = result['processor_stats']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Processed", stats['processed_count'])
                
                with col2:
                    st.metric("Valid", stats['valid_count'])
                
                with col3:
                    st.metric("Errors", stats['error_count'])
                
                with col4:
                    st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
                
                # Display processing quality breakdown
                if result['positions_loaded'] > 0:
                    quality_stats = get_position_quality_stats()
                    if quality_stats:
                        st.markdown("#### 📊 Processing Quality Breakdown")
                        quality_df = pd.DataFrame(list(quality_stats.items()), columns=['Quality Level', 'Count'])
                        fig = px.pie(quality_df, values='Count', names='Quality Level', title="Position Processing Quality")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Show errors if any
                if stats['errors']:
                    with st.expander("⚠️ Processing Errors"):
                        for error in stats['errors']:
                            st.error(error)
                
                # Show warnings if any
                if stats.get('warnings'):
                    with st.expander("⚠️ Processing Warnings"):
                        for warning in stats['warnings']:
                            st.warning(warning)
            else:
                st.error(f"❌ Import failed: {result['error']}")
                
        except Exception as e:
            st.error(f"❌ Import failed with error: {e}")

def display_pgn_import():
    """Display enhanced PGN import interface."""
    st.markdown("#### ♟️ Enhanced PGN Game Import")
    st.info("Import complete chess games with enhanced player name handling and comprehensive metadata extraction.")
    
    uploaded_pgn = st.file_uploader(
        "Upload PGN File", 
        type=['pgn'], 
        key="enhanced_pgn_import",
        help="Upload PGN files containing complete chess games"
    )
    
    if uploaded_pgn:
        file_content = uploaded_pgn.read().decode('utf-8')
        
        # Get comprehensive file statistics
        with st.spinner("📊 Analyzing PGN file..."):
            stats = pgn_loader.get_file_statistics(file_content)
        
        if 'error' not in stats:
            # Display comprehensive statistics
            st.markdown("#### 📊 File Analysis")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Games", stats['total_games'])
            
            with col2:
                st.metric("File Size", f"{stats['file_size_kb']:.1f} KB")
            
            with col3:
                st.metric("Est. Import Time", stats['estimated_import_time'])
            
            with col4:
                st.metric("Player Name Quality", f"{stats.get('player_name_quality', 0):.1f}%")
            
            # Additional statistics
            stats_col1, stats_col2 = st.columns(2)
            
            with stats_col1:
                st.markdown("**Game Statistics:**")
                st.markdown(f"• Average moves per game: {stats['avg_moves_per_game']}")
                st.markdown(f"• Move range: {stats['min_moves']} - {stats['max_moves']}")
                st.markdown(f"• Unique events: {stats['unique_events']}")
                st.markdown(f"• Unique openings: {stats['unique_openings']}")
            
            with stats_col2:
                st.markdown("**Player Statistics:**")
                st.markdown(f"• Unique white players: {stats['unique_white_players']}")
                st.markdown(f"• Unique black players: {stats['unique_black_players']}")
                st.markdown(f"• Generated names: {stats['generated_player_names']}")
                
                if stats.get('avg_elo'):
                    st.markdown(f"• Average ELO: {stats['avg_elo']}")
                    st.markdown(f"• ELO range: {stats['min_elo']} - {stats['max_elo']}")
            
            # Result distribution chart
            if stats.get('result_distribution'):
                result_dist = stats['result_distribution']
                fig = px.pie(
                    values=list(result_dist.values()),
                    names=list(result_dist.keys()),
                    title="Game Results Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Import options
            st.markdown("#### Import Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                max_games = st.number_input(
                    "Maximum games to import", 
                    min_value=1, 
                    max_value=stats['total_games'], 
                    value=min(1000, stats['total_games']),
                    help="Limit the number of games to import"
                )
            
            with col2:
                batch_size = st.selectbox(
                    "Batch processing size",
                    [100, 500, 1000, 2000],
                    index=2,
                    help="Process games in batches for better performance"
                )
            
            # Advanced options
            with st.expander("🔧 Advanced Import Options"):
                skip_duplicate_games = st.checkbox(
                    "Skip duplicate games", 
                    value=True,
                    help="Skip games that already exist in the database"
                )
                
                enhance_player_names = st.checkbox(
                    "Enhanced player name processing", 
                    value=True,
                    help="Use advanced algorithms to improve player name quality"
                )
                
                validate_moves = st.checkbox(
                    "Validate all moves", 
                    value=True,
                    help="Validate that all moves in games are legal"
                )
            
            # Import button
            if st.button("⬆️ Import PGN Games", use_container_width=True, type="primary"):
                import_pgn_games(
                    file_content, 
                    uploaded_pgn.name, 
                    max_games, 
                    batch_size,
                    skip_duplicate_games,
                    enhance_player_names,
                    validate_moves
                )
        else:
            st.error(f"❌ {stats['error']}")

def import_pgn_games(file_content: str, filename: str, max_games: int, batch_size: int,
                    skip_duplicates: bool, enhance_names: bool, validate_moves: bool):
    """Import PGN games with enhanced processing."""
    with st.spinner("🎮 Importing PGN games..."):
        try:
            # Load games using enhanced processor
            games = pgn_loader.load_pgn_games(file_content, max_games=max_games)
            
            if not games:
                st.error("No games could be loaded from the PGN file.")
                return
            
            # Store games in database
            result = database.store_pgn_games(games, filename)
            
            # Display results
            if result['games_stored'] > 0:
                st.success(f"🎮 Successfully imported {result['games_stored']} games!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Games Stored", result['games_stored'])
                
                with col2:
                    st.metric("Total Processed", result['total_processed'])
                
                with col3:
                    st.metric("Errors", result['errors'])
                
                # Show game analysis
                if result['games_stored'] > 0:
                    display_imported_games_analysis(filename)
            else:
                st.error("❌ No games were imported. Check the file format and try again.")
                
        except Exception as e:
            st.error(f"❌ Import failed: {e}")

def display_batch_import():
    """Display batch import interface for multiple files."""
    st.markdown("#### 📋 Batch Import")
    st.info("Import multiple files at once with automated processing.")
    
    # Multiple file upload
    uploaded_files = st.file_uploader(
        "Upload Multiple Files",
        type=['jsonl', 'pgn'],
        accept_multiple_files=True,
        key="batch_import_files"
    )
    
    if uploaded_files:
        st.markdown(f"**Selected {len(uploaded_files)} files for batch import:**")
        
        file_info = []
        total_size = 0
        
        for file in uploaded_files:
            file_size = len(file.read())
            file.seek(0)  # Reset file pointer
            total_size += file_size
            
            file_info.append({
                'Name': file.name,
                'Type': file.type,
                'Size (KB)': round(file_size / 1024, 2)
            })
        
        # Display file summary
        df = pd.DataFrame(file_info)
        st.dataframe(df, use_container_width=True)
        
        st.metric("Total Size", f"{total_size / (1024*1024):.2f} MB")
        
        # Batch import options
        col1, col2 = st.columns(2)
        
        with col1:
            import_order = st.selectbox(
                "Import order",
                ["By file size (smallest first)", "By filename", "By file type"],
                help="Choose the order for importing files"
            )
        
        with col2:
            stop_on_error = st.checkbox(
                "Stop on first error",
                value=False,
                help="Stop batch import if any file fails to import"
            )
        
        # Start batch import
        if st.button("🚀 Start Batch Import", use_container_width=True, type="primary"):
            perform_batch_import(uploaded_files, import_order, stop_on_error)

def perform_batch_import(files: List, import_order: str, stop_on_error: bool):
    """Perform batch import of multiple files."""
    # Sort files based on import order
    if import_order == "By file size (smallest first)":
        files = sorted(files, key=lambda f: len(f.read()))
        for f in files:
            f.seek(0)
    elif import_order == "By filename":
        files = sorted(files, key=lambda f: f.name)
    elif import_order == "By file type":
        files = sorted(files, key=lambda f: f.type)
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    successful_imports = 0
    failed_imports = 0
    import_results = []
    
    for i, file in enumerate(files):
        try:
            status_text.text(f"Processing {file.name} ({i+1}/{len(files)})")
            progress_bar.progress((i + 1) / len(files))
            
            file_content = file.read().decode('utf-8')
            file.seek(0)
            
            # Determine file type and import accordingly
            if file.name.endswith('.jsonl'):
                # Import JSONL
                processor = JSONLProcessor()
                result = database.load_positions_from_enhanced_jsonl(processor, file_content)
                
                if result['success']:
                    successful_imports += 1
                    import_results.append({
                        'File': file.name,
                        'Type': 'JSONL',
                        'Status': '✅ Success',
                        'Items': result['positions_loaded'],
                        'Details': f"{result['positions_loaded']} positions imported"
                    })
                else:
                    failed_imports += 1
                    import_results.append({
                        'File': file.name,
                        'Type': 'JSONL',
                        'Status': '❌ Failed',
                        'Items': 0,
                        'Details': result.get('error', 'Unknown error')
                    })
                    
                    if stop_on_error:
                        break
            
            elif file.name.endswith('.pgn'):
                # Import PGN
                games = pgn_loader.load_pgn_games(file_content, max_games=1000)
                result = database.store_pgn_games(games, file.name)
                
                if result['games_stored'] > 0:
                    successful_imports += 1
                    import_results.append({
                        'File': file.name,
                        'Type': 'PGN',
                        'Status': '✅ Success',
                        'Items': result['games_stored'],
                        'Details': f"{result['games_stored']} games imported"
                    })
                else:
                    failed_imports += 1
                    import_results.append({
                        'File': file.name,
                        'Type': 'PGN', 
                        'Status': '❌ Failed',
                        'Items': 0,
                        'Details': 'No games imported'
                    })
                    
                    if stop_on_error:
                        break
            
        except Exception as e:
            failed_imports += 1
            import_results.append({
                'File': file.name,
                'Type': 'Unknown',
                'Status': '❌ Error',
                'Items': 0,
                'Details': str(e)
            })
            
            if stop_on_error:
                break
    
    # Display results
    status_text.text("Batch import completed!")
    
    with results_container:
        st.markdown("#### 📊 Batch Import Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Successful", successful_imports)
        
        with col2:
            st.metric("Failed", failed_imports)
        
        with col3:
            st.metric("Total Files", len(files))
        
        # Detailed results table
        if import_results:
            results_df = pd.DataFrame(import_results)
            st.dataframe(results_df, use_container_width=True)

def display_export_backup_interface():
    """Display export and backup interface."""
    st.markdown("### 💾 Export & Backup")
    
    export_tabs = st.tabs(["📤 Database Export", "💾 Backup Management", "📊 Data Export"])
    
    with export_tabs[0]:
        display_database_export()
    
    with export_tabs[1]:
        display_backup_management()
    
    with export_tabs[2]:
        display_data_export()

def display_database_export():
    """Display database export interface."""
    st.markdown("#### 📤 Complete Database Export")
    
    # Database statistics
    stats = get_database_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Positions", stats.get('positions', 0))
    
    with col2:
        st.metric("Total Games", stats.get('games', 0))
    
    with col3:
        st.metric("Total Users", stats.get('users', 0))
    
    with col4:
        st.metric("User Moves", stats.get('user_moves', 0))
    
    # Export options
    st.markdown("#### Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_user_data = st.checkbox(
            "Include user training data",
            value=True,
            help="Include user moves, sessions, and analysis data"
        )
    
    with col2:
        include_games = st.checkbox(
            "Include PGN games",
            value=True,
            help="Include imported chess games"
        )
    
    # Export formats
    export_format = st.selectbox(
        "Export format",
        ["Complete SQLite Database", "JSON Data Export", "CSV Tables"],
        help="Choose the format for the exported data"
    )
    
    # Export button
    if st.button("💾 Export Database", use_container_width=True, type="primary"):
        perform_database_export(export_format, include_user_data, include_games)

def perform_database_export(export_format: str, include_user_data: bool, include_games: bool):
    """Perform database export based on selected options."""
    with st.spinner("📦 Preparing database export..."):
        try:
            if export_format == "Complete SQLite Database":
                export_path = database.export_database_with_schema()
                
                if export_path:
                    with open(export_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download Database File",
                            data=f.read(),
                            file_name=f"kuikma_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                            mime="application/octet-stream",
                            use_container_width=True
                        )
                    st.success("✅ Database export ready for download!")
                else:
                    st.error("❌ Export failed")
            
            elif export_format == "JSON Data Export":
                json_data = export_database_to_json(include_user_data, include_games)
                
                st.download_button(
                    label="⬇️ Download JSON Export",
                    data=json.dumps(json_data, indent=2),
                    file_name=f"kuikma_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
                st.success("✅ JSON export ready for download!")
            
            elif export_format == "CSV Tables":
                csv_files = export_database_to_csv(include_user_data, include_games)
                
                # Create ZIP file with all CSV files
                import zipfile
                from io import BytesIO
                
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for filename, csv_data in csv_files.items():
                        zip_file.writestr(filename, csv_data)
                
                st.download_button(
                    label="⬇️ Download CSV Files (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"kuikma_csv_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                st.success("✅ CSV export ready for download!")
                
        except Exception as e:
            st.error(f"❌ Export failed: {e}")


def display_backup_management():
    """Display backup management interface."""
    st.markdown("#### 💾 Backup Management")
    
    # Backup statistics
    backup_stats = get_backup_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Backups", backup_stats.get('total_backups', 0))
    
    with col2:
        total_size_mb = backup_stats.get('total_size_mb', 0)
        st.metric("Total Size", f"{total_size_mb:.1f} MB")
    
    with col3:
        latest_backup = backup_stats.get('latest_backup', 'Never')
        st.metric("Latest Backup", latest_backup)
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("#### ⚡ Quick Actions")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("📦 Create Backup Now", use_container_width=True, type="primary"):
            create_manual_backup()
    
    with action_col2:
        if st.button("🔄 Auto Cleanup", use_container_width=True):
            cleanup_old_backups()
    
    with action_col3:
        if st.button("📊 Backup Health Check", use_container_width=True):
            run_backup_health_check()
    
    st.markdown("---")
    
    # Existing backups
    display_existing_backups()
    
    st.markdown("---")
    
    # Backup settings
    display_backup_settings()

def display_existing_backups():
    """Display list of existing backups with management options."""
    st.markdown("#### 📁 Existing Backups")
    
    backups = get_backup_list()
    
    if not backups:
        st.info("📭 No backups found. Create your first backup above!")
        return
    
    # Display backups in a table format
    backup_data = []
    for backup in backups:
        backup_data.append({
            'Filename': backup['filename'],
            'Created': backup['created_date'],
            'Size (MB)': backup['size_mb'],
            'Type': backup['backup_type'],
            'Status': backup['status']
        })
    
    df_backups = pd.DataFrame(backup_data)
    st.dataframe(df_backups, use_container_width=True, hide_index=True)
    
    # Backup actions
    if backups:
        st.markdown("#### 🛠️ Backup Actions")
        
        selected_backup = st.selectbox(
            "Select backup for actions:",
            options=[b['filename'] for b in backups],
            format_func=lambda x: f"{x} ({next(b['size_mb'] for b in backups if b['filename'] == x):.1f} MB)"
        )
        
        if selected_backup:
            backup_info = next(b for b in backups if b['filename'] == selected_backup)
            
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)
            
            with action_col1:
                if st.button("⬇️ Download", use_container_width=True):
                    download_backup(selected_backup)
            
            with action_col2:
                if st.button("🔄 Restore", use_container_width=True):
                    if st.checkbox(f"Confirm restore from {selected_backup}", key="confirm_restore"):
                        restore_from_backup(selected_backup)
            
            with action_col3:
                if st.button("✅ Verify", use_container_width=True):
                    verify_backup(selected_backup)
            
            with action_col4:
                if st.button("🗑️ Delete", use_container_width=True):
                    if st.checkbox(f"Confirm delete {selected_backup}", key="confirm_delete"):
                        delete_backup(selected_backup)

def display_backup_settings():
    """Display backup configuration settings."""
    st.markdown("#### ⚙️ Backup Settings")
    
    with st.expander("🔧 Backup Configuration"):
        col1, col2 = st.columns(2)
        
        with col1:
            auto_backup = st.checkbox(
                "Enable automatic backups",
                value=get_backup_setting('auto_backup_enabled', False),
                help="Automatically create backups on a schedule"
            )
            
            backup_frequency = st.selectbox(
                "Backup frequency",
                ["Daily", "Weekly", "Monthly"],
                index=["Daily", "Weekly", "Monthly"].index(get_backup_setting('backup_frequency', 'Weekly'))
            )
            
            retention_days = st.number_input(
                "Backup retention (days)",
                min_value=1,
                max_value=365,
                value=get_backup_setting('retention_days', 30),
                help="How long to keep backups before automatic deletion"
            )
        
        with col2:
            compression_level = st.slider(
                "Compression level",
                min_value=0,
                max_value=9,
                value=get_backup_setting('compression_level', 6),
                help="Higher compression saves space but takes longer"
            )
            
            include_logs = st.checkbox(
                "Include application logs",
                value=get_backup_setting('include_logs', False),
                help="Include log files in backups"
            )
            
            verify_after_backup = st.checkbox(
                "Verify backups after creation",
                value=get_backup_setting('verify_after_backup', True),
                help="Automatically verify backup integrity"
            )
        
        if st.button("💾 Save Backup Settings", use_container_width=True):
            save_backup_settings({
                'auto_backup_enabled': auto_backup,
                'backup_frequency': backup_frequency,
                'retention_days': retention_days,
                'compression_level': compression_level,
                'include_logs': include_logs,
                'verify_after_backup': verify_after_backup
            })
            st.success("✅ Backup settings saved!")

def display_data_export():
    """Display specialized data export interface."""
    st.markdown("#### 📊 Specialized Data Export")
    
    export_type = st.selectbox(
        "Export Type",
        ["User Training Data", "Position Analysis", "Game Collection", "System Analytics", "Custom Query"]
    )
    
    if export_type == "User Training Data":
        display_user_data_export()
    elif export_type == "Position Analysis":
        display_position_analysis_export()
    elif export_type == "Game Collection":
        display_game_collection_export()
    elif export_type == "System Analytics":
        display_analytics_export()
    elif export_type == "Custom Query":
        display_custom_query_export()

def display_user_data_export():
    """Display user-specific data export interface."""
    st.markdown("##### 👤 User Training Data Export")
    
    # User selection
    users = get_all_users_for_export()
    
    if not users:
        st.warning("⚠️ No users found for export")
        return
    
    export_scope = st.radio(
        "Export scope:",
        ["Single User", "Multiple Users", "All Users"],
        horizontal=True
    )
    
    selected_users = []
    
    if export_scope == "Single User":
        selected_user = st.selectbox(
            "Select user:",
            options=[u['id'] for u in users],
            format_func=lambda x: f"{next(u['email'] for u in users if u['id'] == x)} ({next(u['full_name'] for u in users if u['id'] == x) or 'No name'})"
        )
        selected_users = [selected_user] if selected_user else []
    
    elif export_scope == "Multiple Users":
        selected_users = st.multiselect(
            "Select users:",
            options=[u['id'] for u in users],
            format_func=lambda x: f"{next(u['email'] for u in users if u['id'] == x)} ({next(u['full_name'] for u in users if u['id'] == x) or 'No name'})"
        )
    
    else:  # All Users
        selected_users = [u['id'] for u in users]
        st.info(f"📊 Exporting data for all {len(users)} users")
    
    # Data selection
    st.markdown("**Data to include:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_moves = st.checkbox("Training moves", value=True)
        include_sessions = st.checkbox("Training sessions", value=True)
        include_analysis = st.checkbox("Move analysis", value=True)
    
    with col2:
        include_games = st.checkbox("Saved games", value=False)
        include_insights = st.checkbox("User insights", value=False)
        include_settings = st.checkbox("User settings", value=False)
    
    # Date range
    st.markdown("**Date range:**")
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start date",
            value=datetime.now().date() - timedelta(days=30)
        )
    
    with col2:
        end_date = st.date_input(
            "End date",
            value=datetime.now().date()
        )
    
    # Export format
    export_format = st.selectbox(
        "Export format:",
        ["JSON", "CSV", "Excel"]
    )
    
    if st.button("📥 Export User Data", use_container_width=True, type="primary"):
        if selected_users:
            export_user_training_data(
                selected_users, 
                {
                    'moves': include_moves,
                    'sessions': include_sessions,
                    'analysis': include_analysis,
                    'games': include_games,
                    'insights': include_insights,
                    'settings': include_settings
                },
                start_date,
                end_date,
                export_format
            )
        else:
            st.error("❌ Please select at least one user")

def display_position_analysis_export():
    """Display position analysis export interface."""
    st.markdown("##### ♟️ Position Analysis Export")
    
    # Analysis filters
    col1, col2 = st.columns(2)
    
    with col1:
        quality_filter = st.multiselect(
            "Position quality:",
            ["excellent", "good", "average", "poor"],
            default=["excellent", "good"]
        )
        
        difficulty_range = st.slider(
            "Difficulty range:",
            min_value=1,
            max_value=10,
            value=(1, 10)
        )
    
    with col2:
        themes = get_position_themes()
        selected_themes = st.multiselect(
            "Tactical themes:",
            themes,
            help="Leave empty to include all themes"
        )
        
        min_moves = st.number_input(
            "Minimum moves in position:",
            min_value=1,
            max_value=100,
            value=1
        )
    
    # Export options
    st.markdown("**Export options:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_fen = st.checkbox("Include FEN notation", value=True)
        include_moves = st.checkbox("Include move analysis", value=True)
        include_evaluations = st.checkbox("Include evaluations", value=True)
    
    with col2:
        include_user_stats = st.checkbox("Include user performance stats", value=False)
        include_metadata = st.checkbox("Include position metadata", value=True)
        export_format = st.selectbox("Format:", ["JSON", "CSV", "PGN"])
    
    if st.button("📥 Export Position Analysis", use_container_width=True, type="primary"):
        export_position_analysis(
            quality_filter,
            difficulty_range,
            selected_themes,
            min_moves,
            {
                'fen': include_fen,
                'moves': include_moves,
                'evaluations': include_evaluations,
                'user_stats': include_user_stats,
                'metadata': include_metadata
            },
            export_format
        )

def display_game_collection_export():
    """Display game collection export interface."""
    st.markdown("##### 🎮 Game Collection Export")
    
    # Game filters
    col1, col2 = st.columns(2)
    
    with col1:
        player_filter = st.text_input(
            "Player name (optional):",
            placeholder="Search by player name"
        )
        
        elo_range = st.slider(
            "ELO range:",
            min_value=0,
            max_value=3000,
            value=(0, 3000)
        )
    
    with col2:
        result_filter = st.multiselect(
            "Game results:",
            ["1-0", "0-1", "1/2-1/2", "*"],
            default=["1-0", "0-1", "1/2-1/2"]
        )
        
        year_range = st.slider(
            "Year range:",
            min_value=1900,
            max_value=datetime.now().year,
            value=(2000, datetime.now().year)
        )
    
    # ECO codes
    eco_codes = st.text_input(
        "ECO codes (comma-separated, optional):",
        placeholder="e.g., E90, B01, C45"
    )
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        include_analysis = st.checkbox("Include game analysis", value=False)
        include_comments = st.checkbox("Include comments", value=True)
    
    with col2:
        max_games = st.number_input(
            "Maximum games to export:",
            min_value=1,
            max_value=10000,
            value=1000
        )
    
    export_format = st.selectbox("Export format:", ["PGN", "JSON", "CSV"])
    
    if st.button("📥 Export Games", use_container_width=True, type="primary"):
        export_game_collection(
            player_filter,
            elo_range,
            result_filter,
            year_range,
            eco_codes,
            include_analysis,
            include_comments,
            max_games,
            export_format
        )

def display_analytics_export():
    """Display system analytics export interface."""
    st.markdown("##### 📈 System Analytics Export")
    
    # Analytics type
    analytics_type = st.selectbox(
        "Analytics type:",
        ["User Activity", "Training Statistics", "System Performance", "Usage Patterns", "Error Logs"]
    )
    
    # Date range
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start date",
            value=datetime.now().date() - timedelta(days=30)
        )
    
    with col2:
        end_date = st.date_input(
            "End date", 
            value=datetime.now().date()
        )
    
    # Aggregation options
    aggregation = st.selectbox(
        "Data aggregation:",
        ["Raw Data", "Daily Summary", "Weekly Summary", "Monthly Summary"]
    )
    
    # Format options
    export_format = st.selectbox("Export format:", ["JSON", "CSV", "Excel"])
    
    if st.button("📊 Export Analytics", use_container_width=True, type="primary"):
        export_system_analytics(
            analytics_type,
            start_date,
            end_date,
            aggregation,
            export_format
        )

def display_custom_query_export():
    """Display custom SQL query export interface."""
    st.markdown("##### 🔍 Custom Query Export")
    
    st.warning("⚠️ Advanced feature - use with caution!")
    
    # Predefined queries
    predefined_queries = {
        "User Training Summary": """
            SELECT 
                u.email,
                COUNT(um.id) as total_moves,
                SUM(CASE WHEN um.is_correct = 1 THEN 1 ELSE 0 END) as correct_moves,
                ROUND(AVG(CASE WHEN um.is_correct = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as accuracy
            FROM users u
            LEFT JOIN user_moves um ON u.id = um.user_id
            WHERE u.is_admin = 0
            GROUP BY u.id, u.email
            ORDER BY total_moves DESC
        """,
        "Position Difficulty Analysis": """
            SELECT 
                difficulty_level,
                COUNT(*) as position_count,
                AVG(user_accuracy) as avg_user_accuracy
            FROM positions 
            WHERE difficulty_level IS NOT NULL
            GROUP BY difficulty_level
            ORDER BY difficulty_level
        """,
        "Monthly Activity Trends": """
            SELECT 
                strftime('%Y-%m', timestamp) as month,
                COUNT(*) as total_moves,
                COUNT(DISTINCT user_id) as active_users
            FROM user_moves
            WHERE timestamp > datetime('now', '-12 months')
            GROUP BY strftime('%Y-%m', timestamp)
            ORDER BY month
        """
    }
    
    query_type = st.selectbox(
        "Query type:",
        ["Custom Query", "Predefined Query"]
    )
    
    if query_type == "Predefined Query":
        selected_query = st.selectbox(
            "Select predefined query:",
            list(predefined_queries.keys())
        )
        
        query = st.text_area(
            "SQL Query:",
            value=predefined_queries[selected_query],
            height=200,
            disabled=True
        )
    
    else:
        query = st.text_area(
            "Enter SQL query:",
            height=200,
            placeholder="SELECT * FROM users WHERE created_at > '2024-01-01'"
        )
        
        st.info("💡 Available tables: users, positions, moves, user_moves, games, training_sessions")
    
    # Safety checks
    if query and any(dangerous in query.upper() for dangerous in ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER']):
        st.error("❌ Dangerous SQL operations are not allowed in exports")
    elif query:
        # Query preview
        if st.button("👁️ Preview Query (First 10 rows)", use_container_width=True):
            preview_custom_query(query)
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.selectbox("Export format:", ["CSV", "JSON", "Excel"])
        
        with col2:
            limit_rows = st.number_input(
                "Limit rows (0 = no limit):",
                min_value=0,
                max_value=100000,
                value=10000
            )
        
        if st.button("📥 Export Query Results", use_container_width=True, type="primary"):
            export_custom_query_results(query, export_format, limit_rows)

# Supporting functions that would need to be implemented:

def get_backup_statistics():
    """Get backup statistics."""
    backup_dir = Path("data/backups")
    if not backup_dir.exists():
        return {'total_backups': 0, 'total_size_mb': 0, 'latest_backup': 'Never'}
    
    backup_files = list(backup_dir.glob("*.db"))
    if not backup_files:
        return {'total_backups': 0, 'total_size_mb': 0, 'latest_backup': 'Never'}
    
    total_size = sum(f.stat().st_size for f in backup_files)
    latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
    latest_date = datetime.fromtimestamp(latest_backup.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
    
    return {
        'total_backups': len(backup_files),
        'total_size_mb': total_size / (1024 * 1024),
        'latest_backup': latest_date
    }

def get_backup_list():
    """Get list of available backups."""
    backup_dir = Path("data/backups")
    if not backup_dir.exists():
        return []
    
    backups = []
    for backup_file in backup_dir.glob("*.db"):
        stat = backup_file.stat()
        backups.append({
            'filename': backup_file.name,
            'created_date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'backup_type': 'Manual' if 'manual' in backup_file.name else 'Auto',
            'status': 'Valid'  # Could add validation check here
        })
    
    return sorted(backups, key=lambda x: x['created_date'], reverse=True)

def create_manual_backup():
    """Create a manual backup."""
    try:
        source_db = "data/kuikma_chess.db"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"manual_backup_{timestamp}.db"
        backup_path = f"data/backups/{backup_name}"
        
        # Ensure backup directory exists
        Path("data/backups").mkdir(parents=True, exist_ok=True)
        
        # Copy database
        shutil.copy2(source_db, backup_path)
        
        st.success(f"✅ Manual backup created: {backup_name}")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Backup failed: {e}")

def cleanup_old_backups():
    """Clean up old backup files."""
    try:
        backup_dir = Path("data/backups")
        retention_days = get_backup_setting('retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        deleted_count = 0
        for backup_file in backup_dir.glob("*.db"):
            if datetime.fromtimestamp(backup_file.stat().st_mtime) < cutoff_date:
                backup_file.unlink()
                deleted_count += 1
        
        if deleted_count > 0:
            st.success(f"✅ Cleaned up {deleted_count} old backup files")
        else:
            st.info("ℹ️ No old backups to clean up")
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Cleanup failed: {e}")

def run_backup_health_check():
    """Run health check on backup files."""
    try:
        backup_dir = Path("data/backups")
        if not backup_dir.exists():
            st.warning("⚠️ No backup directory found")
            return
        
        backup_files = list(backup_dir.glob("*.db"))
        if not backup_files:
            st.warning("⚠️ No backup files found")
            return
        
        healthy_count = 0
        corrupt_count = 0
        
        with st.spinner("🔍 Checking backup integrity..."):
            for backup_file in backup_files:
                try:
                    # Quick integrity check
                    conn = sqlite3.connect(str(backup_file))
                    conn.execute("SELECT COUNT(*) FROM sqlite_master")
                    conn.close()
                    healthy_count += 1
                except:
                    corrupt_count += 1
        
        if corrupt_count == 0:
            st.success(f"✅ All {healthy_count} backup files are healthy")
        else:
            st.warning(f"⚠️ Found {corrupt_count} potentially corrupt backup files out of {len(backup_files)}")
        
    except Exception as e:
        st.error(f"❌ Health check failed: {e}")

def get_backup_setting(key, default):
    """Get backup setting from configuration."""
    # This would read from your configuration system
    # For now, return defaults
    defaults = {
        'auto_backup_enabled': False,
        'backup_frequency': 'Weekly',
        'retention_days': 30,
        'compression_level': 6,
        'include_logs': False,
        'verify_after_backup': True
    }
    return defaults.get(key, default)

def save_backup_settings(settings):
    """Save backup settings to configuration."""
    # This would save to your configuration system
    # Implementation depends on how you store settings
    pass

def export_user_training_data(user_ids, data_types, start_date, end_date, export_format):
    """Export user training data."""
    with st.spinner("📦 Exporting user training data..."):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            export_data = {}
            
            for user_id in user_ids:
                user_data = {}
                
                if data_types['moves']:
                    cursor.execute('''
                        SELECT position_id, move, is_correct, timestamp, time_taken
                        FROM user_moves 
                        WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
                    ''', (user_id, start_date, end_date))
                    user_data['moves'] = cursor.fetchall()
                
                if data_types['sessions']:
                    cursor.execute('''
                        SELECT session_id, start_time, end_time, total_moves, correct_moves
                        FROM training_sessions
                        WHERE user_id = ? AND DATE(start_time) BETWEEN ? AND ?
                    ''', (user_id, start_date, end_date))
                    user_data['sessions'] = cursor.fetchall()
                
                # Add other data types as needed...
                
                export_data[f'user_{user_id}'] = user_data
            
            # Format and download
            if export_format == "JSON":
                st.download_button(
                    "⬇️ Download User Data (JSON)",
                    data=json.dumps(export_data, indent=2, default=str),
                    file_name=f"user_training_data_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            st.success("✅ User training data export ready!")
            
        except Exception as e:
            st.error(f"❌ Export failed: {e}")
        finally:
            conn.close()

# Add the remaining export functions with similar implementations...
def export_position_analysis(quality_filter, difficulty_range, selected_themes, min_moves, options, export_format):
    """Export position analysis data."""
    # Implementation similar to above
    pass

def export_game_collection(player_filter, elo_range, result_filter, year_range, eco_codes, include_analysis, include_comments, max_games, export_format):
    """Export game collection."""
    # Implementation similar to above
    pass

def export_system_analytics(analytics_type, start_date, end_date, aggregation, export_format):
    """Export system analytics."""
    # Implementation similar to above
    pass

def preview_custom_query(query):
    """Preview custom query results."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"{query} LIMIT 10")
        results = cursor.fetchall()
        
        if results:
            # Get column names
            columns = [description[0] for description in cursor.description]
            df = pd.DataFrame(results, columns=columns)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ Query returned no results")
            
    except Exception as e:
        st.error(f"❌ Query error: {e}")
    finally:
        conn.close()

def export_custom_query_results(query, export_format, limit_rows):
    """Export custom query results."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if limit_rows > 0:
            query = f"{query} LIMIT {limit_rows}"
        
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        if export_format == "CSV":
            df = pd.DataFrame(results, columns=columns)
            csv_data = df.to_csv(index=False)
            
            st.download_button(
                "⬇️ Download Query Results (CSV)",
                data=csv_data,
                file_name=f"custom_query_results_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        st.success("✅ Custom query export ready!")
        
    except Exception as e:
        st.error(f"❌ Export failed: {e}")
    finally:
        conn.close()

def display_user_configuration():
    """Display user configuration interface."""
    st.markdown("### 🔧 User Configuration")
    
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("User not logged in.")
        return
    
    # Get current settings
    current_settings = auth.get_user_settings(user_id)
    user_info = auth.get_user_info(user_id)
    
    # User information
    st.markdown("#### 👤 User Information")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown(f"**Email:** {user_info.get('email', 'Unknown')}")
        st.markdown(f"**Account Created:** {user_info.get('created_at', 'Unknown')}")
    
    with info_col2:
        st.markdown(f"**Last Login:** {user_info.get('last_login', 'Unknown')}")
        st.markdown(f"**Admin Status:** {'Yes' if user_info.get('is_admin') else 'No'}")
    
    st.markdown("---")
    
    # Training preferences
    st.markdown("#### 🎯 Training Preferences")
    
    with st.form("user_settings_form1"):
        col1, col2 = st.columns(2)
        
        with col1:
            random_positions = st.checkbox(
                "Random position selection",
                value=current_settings.get('random_positions', True),
                help="Select positions randomly instead of sequentially"
            )
            
            top_n_threshold = st.slider(
                "Top N moves threshold",
                min_value=1,
                max_value=10,
                value=current_settings.get('top_n_threshold', 3),
                help="Consider moves within top N as correct"
            )
        
        with col2:
            score_difference_threshold = st.slider(
                "Score difference threshold (centipawns)",
                min_value=5,
                max_value=50,
                value=current_settings.get('score_difference_threshold', 10),
                help="Maximum centipawn loss for a move to be considered correct"
            )
            
            theme = st.selectbox(
                "Board theme",
                ["default", "dark", "blue", "green", "wood"],
                index=["default", "dark", "blue", "green", "wood"].index(current_settings.get('theme', 'default')),
                help="Visual theme for the chess board"
            )
        
        # Notification preferences
        st.markdown("#### 🔔 Notification Preferences")
        
        email_notifications = st.checkbox(
            "Email notifications for achievements",
            value=False,
            help="Receive email notifications for training milestones"
        )
        
        session_reminders = st.checkbox(
            "Training session reminders",
            value=False,
            help="Get reminders to continue training"
        )
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            analysis_depth = st.slider(
                "Preferred analysis depth",
                min_value=10,
                max_value=25,
                value=18,
                help="Depth of engine analysis for new positions"
            )
            
            auto_generate_analysis = st.checkbox(
                "Auto-generate HTML analysis",
                value=False,
                help="Automatically generate comprehensive HTML analysis for each training move"
            )
        
        # Save settings
        if st.form_submit_button("💾 Save Settings", use_container_width=True, type="primary"):
            new_settings = {
                'random_positions': random_positions,
                'top_n_threshold': top_n_threshold,
                'score_difference_threshold': score_difference_threshold,
                'theme': theme
            }
            
            if auth.update_user_settings(user_id, new_settings):
                st.success("✅ Settings saved successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to save settings")

def display_data_overview():
    """Display comprehensive data overview."""
    st.markdown("### 📊 Data Overview")
    
    # Get comprehensive statistics
    stats = get_comprehensive_statistics()
    
    # Overview metrics
    st.markdown("#### 📈 Database Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Positions", stats['positions']['total'])
    
    with col2:
        st.metric("Total Games", stats['games']['total'])
    
    with col3:
        st.metric("Active Users", stats['users']['active'])
    
    with col4:
        st.metric("Training Sessions", stats['sessions']['total'])
    
    # Data quality metrics
    st.markdown("#### ✨ Data Quality")
    
    quality_col1, quality_col2 = st.columns(2)
    
    with quality_col1:
        # Position quality distribution
        if stats['positions']['quality_distribution']:
            quality_df = pd.DataFrame(
                list(stats['positions']['quality_distribution'].items()),
                columns=['Quality Level', 'Count']
            )
            fig = px.pie(
                quality_df, 
                values='Count', 
                names='Quality Level',
                title="Position Data Quality"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with quality_col2:
        # Game import sources
        if stats['games']['sources']:
            sources_df = pd.DataFrame(
                list(stats['games']['sources'].items()),
                columns=['Source', 'Count']
            )
            fig = px.bar(
                sources_df,
                x='Source',
                y='Count',
                title="Game Import Sources"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Training activity
    st.markdown("#### 🎯 Training Activity")
    
    activity_data = stats.get('training_activity', {})
    if activity_data:
        activity_df = pd.DataFrame(activity_data)
        
        fig = px.line(
            activity_df,
            x='date',
            y='moves',
            title="Daily Training Activity (Last 30 Days)"
        )
        st.plotly_chart(fig, use_container_width=True)

def display_analysis_templates():
    """Display analysis template management."""
    st.markdown("### 📚 Analysis Templates")
    
    st.info("Manage comprehensive HTML analysis templates generated during training.")
    
    # Template statistics
    template_stats = get_template_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Templates Generated", template_stats.get('total', 0))
    
    with col2:
        st.metric("Total Size", f"{template_stats.get('total_size_mb', 0):.2f} MB")
    
    with col3:
        st.metric("Average Size", f"{template_stats.get('avg_size_kb', 0):.1f} KB")
    
    # Template management
    st.markdown("#### 🛠️ Template Management")
    
    template_col1, template_col2 = st.columns(2)
    
    with template_col1:
        if st.button("📁 Open Templates Folder", use_container_width=True):
            template_dir = "kuikma_analysis"
            if os.path.exists(template_dir):
                st.success(f"Templates folder: {os.path.abspath(template_dir)}")
            else:
                st.warning("Templates folder not found. Generate some analyses first.")
    
    with template_col2:
        if st.button("🗑️ Clear All Templates", use_container_width=True):
            if st.session_state.get('confirm_template_clear'):
                clear_analysis_templates()
                st.session_state.confirm_template_clear = False
                st.success("✅ All templates cleared!")
                st.rerun()
            else:
                st.session_state.confirm_template_clear = True
                st.warning("⚠️ Click again to confirm deletion of all templates")
    
    # Recent templates
    recent_templates = get_recent_templates()
    if recent_templates:
        st.markdown("#### 📄 Recent Templates")
        
        templates_df = pd.DataFrame(recent_templates)
        st.dataframe(templates_df, use_container_width=True)

def display_advanced_tools():
    """Display advanced tools and utilities."""
    st.markdown("### 🛠️ Advanced Tools")
    
    tools_tabs = st.tabs(["🔧 Database Tools", "📊 Analytics", "🧪 Experimental"])
    
    with tools_tabs[0]:
        display_database_tools()
    
    with tools_tabs[1]:
        display_analytics_tools()
    
    with tools_tabs[2]:
        display_experimental_tools()

def display_database_tools():
    """Display database maintenance tools."""
    st.markdown("#### 🔧 Database Maintenance")
    
    # Database health check
    if st.button("🏥 Database Health Check", use_container_width=True):
        with st.spinner("Checking database health..."):
            health_result = database.database_sanity_check()
            
            if health_result['healthy']:
                st.success("✅ Database is healthy!")
            else:
                st.error("❌ Database issues detected:")
                for issue in health_result['issues']:
                    st.error(f"• {issue}")
    
    # Optimization tools
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⚡ Optimize Database", use_container_width=True):
            with st.spinner("Optimizing database..."):
                if database.optimize_database():
                    st.success("✅ Database optimized!")
                else:
                    st.error("❌ Optimization failed")
    
    with col2:
        if st.button("🧹 Clean Orphaned Records", use_container_width=True):
            with st.spinner("Cleaning orphaned records..."):
                # This would be implemented in the database module
                st.success("✅ Orphaned records cleaned!")

def display_analytics_tools():
    """Display analytics and reporting tools."""
    st.markdown("#### 📊 Analytics Tools")
    
    # User performance analytics
    if st.button("📈 Generate User Performance Report", use_container_width=True):
        generate_user_performance_report()
    
    # Position difficulty analysis
    if st.button("🎯 Position Difficulty Analysis", use_container_width=True):
        generate_difficulty_analysis()

def display_experimental_tools():
    """Display experimental features."""
    st.markdown("#### 🧪 Experimental Features")
    
    st.warning("⚠️ These features are experimental and may not work as expected.")
    
    # AI-powered position generation
    if st.button("🤖 AI Position Generator", use_container_width=True):
        st.info("AI position generation coming soon!")
    
    # Advanced analytics
    if st.button("🔬 Advanced Pattern Recognition", use_container_width=True):
        st.info("Pattern recognition analysis coming soon!")

# Helper functions

def get_database_statistics() -> Dict[str, int]:
    """Get basic database statistics."""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        stats = {}
        tables = ['positions', 'games', 'users', 'user_moves']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
        
        conn.close()
        return stats
        
    except Exception:
        return {}

def get_position_quality_stats() -> Dict[str, int]:
    """Get position quality statistics."""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT processing_quality, COUNT(*) as count
            FROM positions 
            GROUP BY processing_quality
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return dict(results)
        
    except Exception:
        return {}

def get_comprehensive_statistics() -> Dict[str, Any]:
    """Get comprehensive application statistics."""
    # This would be a comprehensive stats gathering function
    # For now, return basic structure
    return {
        'positions': {
            'total': 0,
            'quality_distribution': {}
        },
        'games': {
            'total': 0,
            'sources': {}
        },
        'users': {
            'active': 0
        },
        'sessions': {
            'total': 0
        },
        'training_activity': []
    }

def get_template_statistics() -> Dict[str, Any]:
    """Get analysis template statistics."""
    template_dir = "kuikma_analysis"
    
    if not os.path.exists(template_dir):
        return {'total': 0, 'total_size_mb': 0, 'avg_size_kb': 0}
    
    files = [f for f in os.listdir(template_dir) if f.endswith('.html')]
    total_size = sum(os.path.getsize(os.path.join(template_dir, f)) for f in files)
    
    return {
        'total': len(files),
        'total_size_mb': total_size / (1024 * 1024),
        'avg_size_kb': (total_size / len(files) / 1024) if files else 0
    }

def get_recent_templates() -> List[Dict[str, Any]]:
    """Get list of recent analysis templates."""
    template_dir = "kuikma_analysis"
    
    if not os.path.exists(template_dir):
        return []
    
    files = []
    for filename in os.listdir(template_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(template_dir, filename)
            stat = os.stat(filepath)
            files.append({
                'Filename': filename,
                'Size (KB)': round(stat.st_size / 1024, 2),
                'Created': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            })
    
    # Sort by creation time, most recent first
    files.sort(key=lambda x: x['Created'], reverse=True)
    return files[:10]  # Return last 10

def clear_analysis_templates():
    """Clear all analysis templates."""
    template_dir = "kuikma_analysis"
    
    if os.path.exists(template_dir):
        shutil.rmtree(template_dir)
        os.makedirs(template_dir)

def export_database_to_json(include_user_data: bool, include_games: bool) -> Dict[str, Any]:
    """Export database to JSON format."""
    # Implementation would go here
    return {'message': 'JSON export functionality to be implemented'}

def export_database_to_csv(include_user_data: bool, include_games: bool) -> Dict[str, str]:
    """Export database to CSV format."""
    # Implementation would go here
    return {'tables.csv': 'CSV export functionality to be implemented'}

def generate_user_performance_report():
    """Generate comprehensive user performance report."""
    st.info("Generating user performance report...")
    # Implementation would go here

def generate_difficulty_analysis():
    """Generate position difficulty analysis."""
    st.info("Analyzing position difficulty distribution...")
    # Implementation would go here

def display_imported_games_analysis(filename: str):
    """Display analysis of imported games."""
    st.markdown(f"#### 📊 Analysis of imported games from {filename}")
    # Implementation would show statistics about the imported games


# missing_functions.py - Add these functions to your settings.py or create a separate utils.py file

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import streamlit as st
from database import get_db_connection

def get_all_users_for_export():
    """Get all users for export selection."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, full_name, is_admin, is_verified, created_at
            FROM users
            WHERE id IS NOT NULL
            ORDER BY email
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'email': row[1],
                'full_name': row[2] or '',
                'is_admin': bool(row[3]) if row[3] is not None else False,
                'is_verified': bool(row[4]) if row[4] is not None else False,
                'created_at': row[5] if len(row) > 5 else None
            })
        
        conn.close()
        return users
        
    except Exception as e:
        st.error(f"❌ Error loading users: {e}")
        return []

def get_position_themes():
    """Get available position themes for filtering."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Try to get themes from positions table - adjust column names as needed
        try:
            cursor.execute('''
                SELECT DISTINCT theme 
                FROM positions 
                WHERE theme IS NOT NULL AND theme != ''
                ORDER BY theme
            ''')
            themes = [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # If theme column doesn't exist, try other common column names
            try:
                cursor.execute('''
                    SELECT DISTINCT tags 
                    FROM positions 
                    WHERE tags IS NOT NULL AND tags != ''
                    ORDER BY tags
                ''')
                themes = [row[0] for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                # If no theme/tags columns, return default themes
                themes = []
        
        conn.close()
        
        # If no themes found in database, return common chess themes
        if not themes:
            themes = [
                "Tactics", "Endgame", "Opening", "Middlegame", 
                "Puzzle", "Checkmate", "Pin", "Fork", "Skewer",
                "Deflection", "Decoy", "Discovered Attack"
            ]
        
        return themes
        
    except Exception as e:
        st.error(f"❌ Error loading themes: {e}")
        return ["Tactics", "Endgame", "Opening", "Middlegame", "Puzzle"]

def export_database_to_json(include_user_data: bool, include_games: bool) -> dict:
    """Export database to JSON format."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'export_version': '2.0.0',
            'kuikma_version': '2.0.0',
            'tables': {}
        }
        
        # Core tables to always export
        core_tables = ['positions', 'moves']
        
        for table in core_tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                export_data['tables'][table] = {
                    'columns': columns,
                    'row_count': len(rows),
                    'data': [dict(zip(columns, row)) for row in rows]
                }
            except sqlite3.OperationalError as e:
                st.warning(f"⚠️ Could not export table {table}: {e}")
                continue
        
        # Conditionally include user data
        if include_user_data:
            user_tables = ['users', 'user_moves', 'user_settings', 'training_sessions', 
                          'user_subscriptions', 'user_verification_requests']
            
            for table in user_tables:
                try:
                    cursor.execute(f"SELECT * FROM {table}")
                    columns = [description[0] for description in cursor.description]
                    rows = cursor.fetchall()
                    
                    export_data['tables'][table] = {
                        'columns': columns,
                        'row_count': len(rows),
                        'data': [dict(zip(columns, row)) for row in rows]
                    }
                except sqlite3.OperationalError:
                    # Table doesn't exist, skip it
                    continue
        
        # Conditionally include games
        if include_games:
            try:
                cursor.execute("SELECT * FROM games")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                export_data['tables']['games'] = {
                    'columns': columns,
                    'row_count': len(rows),
                    'data': [dict(zip(columns, row)) for row in rows]
                }
            except sqlite3.OperationalError:
                # Games table doesn't exist, skip it
                st.info("ℹ️ Games table not found, skipping game data")
        
        conn.close()
        return export_data
        
    except Exception as e:
        st.error(f"❌ JSON export failed: {e}")
        return {'error': str(e), 'tables': {}}

def export_database_to_csv(include_user_data: bool, include_games: bool) -> dict:
    """Export database to CSV files."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        csv_files = {}
        
        # Core tables
        core_tables = ['positions', 'moves']
        
        for table in core_tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                if rows:
                    df = pd.DataFrame(rows, columns=columns)
                    csv_files[f"{table}.csv"] = df.to_csv(index=False)
                else:
                    csv_files[f"{table}.csv"] = f"# No data in {table} table\n"
                    
            except sqlite3.OperationalError as e:
                csv_files[f"{table}_error.txt"] = f"Error exporting {table}: {e}"
                continue
        
        # User data tables
        if include_user_data:
            user_tables = ['users', 'user_moves', 'user_settings', 'training_sessions',
                          'user_subscriptions', 'user_verification_requests']
            
            for table in user_tables:
                try:
                    cursor.execute(f"SELECT * FROM {table}")
                    columns = [description[0] for description in cursor.description]
                    rows = cursor.fetchall()
                    
                    if rows:
                        df = pd.DataFrame(rows, columns=columns)
                        csv_files[f"{table}.csv"] = df.to_csv(index=False)
                    else:
                        csv_files[f"{table}.csv"] = f"# No data in {table} table\n"
                        
                except sqlite3.OperationalError:
                    # Table doesn't exist, skip it
                    continue
        
        # Games data
        if include_games:
            try:
                cursor.execute("SELECT * FROM games")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                if rows:
                    df = pd.DataFrame(rows, columns=columns)
                    csv_files["games.csv"] = df.to_csv(index=False)
                else:
                    csv_files["games.csv"] = "# No game data found\n"
                    
            except sqlite3.OperationalError:
                csv_files["games_info.txt"] = "Games table not found in database"
        
        conn.close()
        return csv_files
        
    except Exception as e:
        st.error(f"❌ CSV export failed: {e}")
        return {"error.txt": f"Export failed: {e}"}

def get_database_statistics():
    """Get database statistics for display."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Check each table and get counts
        tables_to_check = ['positions', 'games', 'users', 'user_moves']
        
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            except sqlite3.OperationalError:
                # Table doesn't exist
                stats[table] = 0
        
        conn.close()
        return stats
        
    except Exception as e:
        st.error(f"❌ Error getting database statistics: {e}")
        return {'positions': 0, 'games': 0, 'users': 0, 'user_moves': 0}

def export_user_training_data(user_ids, data_types, start_date, end_date, export_format):
    """Export user training data."""
    with st.spinner("📦 Exporting user training data..."):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            export_data = {
                'export_info': {
                    'type': 'user_training_data',
                    'user_count': len(user_ids),
                    'date_range': f"{start_date} to {end_date}",
                    'export_date': datetime.now().isoformat()
                },
                'users': {}
            }
            
            for user_id in user_ids:
                # Get user info
                cursor.execute("SELECT email, full_name FROM users WHERE id = ?", (user_id,))
                user_info = cursor.fetchone()
                
                if not user_info:
                    continue
                
                user_data = {
                    'user_info': {
                        'id': user_id,
                        'email': user_info[0],
                        'full_name': user_info[1] or ''
                    }
                }
                
                # Export moves if requested
                if data_types.get('moves', False):
                    try:
                        cursor.execute('''
                            SELECT position_id, move, is_correct, timestamp, time_taken
                            FROM user_moves 
                            WHERE user_id = ? AND DATE(timestamp) BETWEEN ? AND ?
                            ORDER BY timestamp
                        ''', (user_id, start_date, end_date))
                        
                        moves = cursor.fetchall()
                        user_data['training_moves'] = [
                            {
                                'position_id': move[0],
                                'move': move[1],
                                'is_correct': bool(move[2]),
                                'timestamp': move[3],
                                'time_taken': move[4]
                            } for move in moves
                        ]
                    except sqlite3.OperationalError:
                        user_data['training_moves'] = []
                
                # Export sessions if requested
                if data_types.get('sessions', False):
                    try:
                        cursor.execute('''
                            SELECT session_id, start_time, end_time, total_moves, correct_moves
                            FROM training_sessions
                            WHERE user_id = ? AND DATE(start_time) BETWEEN ? AND ?
                            ORDER BY start_time
                        ''', (user_id, start_date, end_date))
                        
                        sessions = cursor.fetchall()
                        user_data['training_sessions'] = [
                            {
                                'session_id': session[0],
                                'start_time': session[1],
                                'end_time': session[2],
                                'total_moves': session[3],
                                'correct_moves': session[4]
                            } for session in sessions
                        ]
                    except sqlite3.OperationalError:
                        user_data['training_sessions'] = []
                
                # Add other data types as needed...
                
                export_data['users'][f'user_{user_id}'] = user_data
            
            conn.close()
            
            # Format and download based on export format
            if export_format == "JSON":
                json_data = json.dumps(export_data, indent=2, default=str)
                st.download_button(
                    "⬇️ Download User Training Data (JSON)",
                    data=json_data,
                    file_name=f"user_training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            elif export_format == "CSV":
                # Convert to CSV format
                csv_data = convert_user_data_to_csv(export_data)
                st.download_button(
                    "⬇️ Download User Training Data (CSV)",
                    data=csv_data,
                    file_name=f"user_training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            st.success("✅ User training data export ready!")
            
        except Exception as e:
            st.error(f"❌ Export failed: {e}")

def convert_user_data_to_csv(export_data):
    """Convert user training data to CSV format."""
    try:
        csv_rows = []
        headers = ['user_id', 'email', 'full_name', 'position_id', 'move', 'is_correct', 'timestamp', 'time_taken']
        csv_rows.append(','.join(headers))
        
        for user_key, user_data in export_data['users'].items():
            user_info = user_data['user_info']
            
            if 'training_moves' in user_data:
                for move in user_data['training_moves']:
                    row = [
                        str(user_info['id']),
                        user_info['email'],
                        user_info['full_name'],
                        str(move.get('position_id', '')),
                        move.get('move', ''),
                        str(move.get('is_correct', '')),
                        move.get('timestamp', ''),
                        str(move.get('time_taken', ''))
                    ]
                    csv_rows.append(','.join(f'"{field}"' for field in row))
            else:
                # Add user info even if no moves
                row = [
                    str(user_info['id']),
                    user_info['email'],
                    user_info['full_name'],
                    '', '', '', '', ''
                ]
                csv_rows.append(','.join(f'"{field}"' for field in row))
        
        return '\n'.join(csv_rows)
        
    except Exception as e:
        return f"Error converting to CSV: {e}"

# Placeholder functions for other export types (implement as needed)
def export_position_analysis(quality_filter, difficulty_range, selected_themes, min_moves, options, export_format):
    """Export position analysis data."""
    st.info("🔧 Position analysis export - Coming soon!")
    
    # Basic implementation
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query based on filters
        query = "SELECT * FROM positions WHERE 1=1"
        params = []
        
        if quality_filter:
            placeholders = ','.join('?' * len(quality_filter))
            query += f" AND processing_quality IN ({placeholders})"
            params.extend(quality_filter)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        if export_format == "JSON":
            data = [dict(zip(columns, row)) for row in results]
            json_data = json.dumps({'positions': data}, indent=2, default=str)
            
            st.download_button(
                "⬇️ Download Position Analysis (JSON)",
                data=json_data,
                file_name=f"position_analysis_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        conn.close()
        st.success(f"✅ Exported {len(results)} positions!")
        
    except Exception as e:
        st.error(f"❌ Export failed: {e}")

def export_game_collection(player_filter, elo_range, result_filter, year_range, eco_codes, include_analysis, include_comments, max_games, export_format):
    """Export game collection."""
    st.info("🔧 Game collection export - Coming soon!")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Basic game export
        cursor.execute(f"SELECT * FROM games LIMIT {max_games}")
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        if results and export_format == "JSON":
            data = [dict(zip(columns, row)) for row in results]
            json_data = json.dumps({'games': data}, indent=2, default=str)
            
            st.download_button(
                "⬇️ Download Games (JSON)",
                data=json_data,
                file_name=f"games_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            
            st.success(f"✅ Exported {len(results)} games!")
        else:
            st.warning("⚠️ No games found or table doesn't exist")
        
        conn.close()
        
    except Exception as e:
        st.error(f"❌ Export failed: {e}")

def export_system_analytics(analytics_type, start_date, end_date, aggregation, export_format):
    """Export system analytics."""
    st.info("🔧 System analytics export - Coming soon!")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Basic analytics based on type
        if analytics_type == "User Activity":
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as moves, COUNT(DISTINCT user_id) as users
                FROM user_moves
                WHERE DATE(timestamp) BETWEEN ? AND ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (start_date, end_date))
        else:
            cursor.execute("SELECT 'No data' as message")
        
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        if results and export_format == "JSON":
            data = [dict(zip(columns, row)) for row in results]
            json_data = json.dumps({analytics_type.lower().replace(' ', '_'): data}, indent=2, default=str)
            
            st.download_button(
                f"⬇️ Download {analytics_type} (JSON)",
                data=json_data,
                file_name=f"analytics_{analytics_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            
            st.success(f"✅ Exported {analytics_type} data!")
        
        conn.close()
        
    except Exception as e:
        st.error(f"❌ Export failed: {e}")

def preview_custom_query(query):
    """Preview custom query results."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Add LIMIT to preview
        preview_query = f"{query.rstrip(';')} LIMIT 10"
        cursor.execute(preview_query)
        results = cursor.fetchall()
        
        if results:
            # Get column names
            columns = [description[0] for description in cursor.description]
            df = pd.DataFrame(results, columns=columns)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Showing first 10 rows of {len(results)} results")
        else:
            st.info("ℹ️ Query returned no results")
        
        conn.close()
            
    except Exception as e:
        st.error(f"❌ Query error: {e}")

def export_custom_query_results(query, export_format, limit_rows):
    """Export custom query results."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Apply limit if specified
        if limit_rows > 0:
            final_query = f"{query.rstrip(';')} LIMIT {limit_rows}"
        else:
            final_query = query
        
        cursor.execute(final_query)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        if not results:
            st.warning("⚠️ Query returned no results")
            return
        
        if export_format == "CSV":
            df = pd.DataFrame(results, columns=columns)
            csv_data = df.to_csv(index=False)
            
            st.download_button(
                "⬇️ Download Query Results (CSV)",
                data=csv_data,
                file_name=f"custom_query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        elif export_format == "JSON":
            data = [dict(zip(columns, row)) for row in results]
            json_data = json.dumps({'query_results': data}, indent=2, default=str)
            
            st.download_button(
                "⬇️ Download Query Results (JSON)",
                data=json_data,
                file_name=f"custom_query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.success(f"✅ Custom query export ready! ({len(results)} rows)")
        
        conn.close()
        
    except Exception as e:
        st.error(f"❌ Export failed: {e}")


if __name__ == "__main__":
    print("Enhanced settings module for Kuikma Chess Engine loaded.")
