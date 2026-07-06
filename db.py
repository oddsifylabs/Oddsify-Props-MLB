"""SQLite database operations for bet tracking and caching."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path.home() / ".pitcher-ks" / "data.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class Database:
    """Handle all database operations."""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Bets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                pitcher_name TEXT NOT NULL,
                pitcher_id INTEGER,
                team TEXT NOT NULL,
                opponent TEXT NOT NULL,
                prop_line REAL,
                prop_type TEXT,  -- 'over' or 'under'
                odds INTEGER,
                bet_amount REAL,
                confidence REAL,
                ev_percent REAL,
                result TEXT,  -- 'win', 'loss', 'push', NULL if not settled
                actual_strikeouts REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Pitcher stats cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pitcher_stats (
                pitcher_id INTEGER PRIMARY KEY,
                pitcher_name TEXT,
                season_k9 REAL,
                recent_k9 REAL,
                era REAL,
                games_pitched INTEGER,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Game cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                date TEXT,
                away_team TEXT,
                home_team TEXT,
                away_pitcher TEXT,
                away_pitcher_id INTEGER,
                home_pitcher TEXT,
                home_pitcher_id INTEGER,
                away_prob_pitcher_id INTEGER,
                home_prob_pitcher_id INTEGER,
                game_time TEXT,
                status TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_bet(self, bet_data: Dict) -> int:
        """Add a new bet to tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO bets (
                date, pitcher_name, pitcher_id, team, opponent,
                prop_line, prop_type, odds, bet_amount, confidence,
                ev_percent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bet_data.get("date"),
            bet_data.get("pitcher_name"),
            bet_data.get("pitcher_id"),
            bet_data.get("team"),
            bet_data.get("opponent"),
            bet_data.get("prop_line"),
            bet_data.get("prop_type"),
            bet_data.get("odds"),
            bet_data.get("bet_amount"),
            bet_data.get("confidence"),
            bet_data.get("ev_percent"),
        ))
        
        conn.commit()
        bet_id = cursor.lastrowid
        conn.close()
        return bet_id
    
    def get_bets(self, date: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Get bets from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if date:
            cursor.execute("SELECT * FROM bets WHERE date = ? ORDER BY created_at DESC LIMIT ?", 
                          (date, limit))
        else:
            cursor.execute("SELECT * FROM bets ORDER BY created_at DESC LIMIT ?", (limit,))
        
        bets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return bets
    
    def update_bet_result(self, bet_id: int, result: str, actual_strikeouts: float):
        """Update bet result after game settles."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE bets
            SET result = ?, actual_strikeouts = ?
            WHERE id = ?
        """, (result, actual_strikeouts, bet_id))
        
        conn.commit()
        conn.close()
    
    def cache_pitcher_stats(self, pitcher_id: int, pitcher_name: str, stats: Dict):
        """Cache pitcher stats."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO pitcher_stats
            (pitcher_id, pitcher_name, season_k9, recent_k9, era, games_pitched)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            pitcher_id,
            pitcher_name,
            stats.get("season_k9"),
            stats.get("recent_k9"),
            stats.get("era"),
            stats.get("games_pitched"),
        ))
        
        conn.commit()
        conn.close()
    
    def get_cached_pitcher_stats(self, pitcher_id: int) -> Optional[Dict]:
        """Get cached pitcher stats."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM pitcher_stats WHERE pitcher_id = ?", (pitcher_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_stats_summary(self, date: Optional[str] = None) -> Dict:
        """Get summary stats (win rate, ROI, etc.)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if date:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
                    SUM(CASE WHEN result = 'push' THEN 1 ELSE 0 END) as pushes,
                    SUM(bet_amount) as total_wagered,
                    AVG(confidence) as avg_confidence,
                    AVG(ev_percent) as avg_ev
                FROM bets
                WHERE date = ?
            """, (date,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
                    SUM(CASE WHEN result = 'push' THEN 1 ELSE 0 END) as pushes,
                    SUM(bet_amount) as total_wagered,
                    AVG(confidence) as avg_confidence,
                    AVG(ev_percent) as avg_ev
                FROM bets
            """)
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total_bets": row[0] or 0,
            "wins": row[1] or 0,
            "losses": row[2] or 0,
            "pushes": row[3] or 0,
            "total_wagered": row[4] or 0,
            "avg_confidence": row[5] or 0,
            "avg_ev": row[6] or 0,
        }
