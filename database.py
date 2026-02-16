import sqlite3
import hashlib
from datetime import datetime
import os

DB_FILE = 'mirror_x.db'

def init_database():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create study_sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            hours REAL NOT NULL,
            difficulty TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create score_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS score_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reality_score INTEGER NOT NULL,
            discipline_score INTEGER NOT NULL,
            avoidance_score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create latest_user_scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS latest_user_scores (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            discipline_score INTEGER,
            consistency REAL,
            total_hours REAL,
            current_streak INTEGER,
            longest_streak INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create daily_task_completions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_task_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash a password"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute(
        'SELECT * FROM users WHERE username = ? AND password_hash = ?',
        (username, password_hash)
    )
    user = cursor.fetchone()
    conn.close()
    
    return user

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    return user

def save_study_session(user_id, subject, hours, difficulty):
    """Save a study session for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    from datetime import datetime
    date = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute(
        'INSERT INTO study_sessions (user_id, date, subject, hours, difficulty) VALUES (?, ?, ?, ?, ?)',
        (user_id, date, subject, hours, difficulty)
    )
    conn.commit()
    conn.close()

def get_user_study_sessions(user_id):
    """Get all study sessions for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM study_sessions WHERE user_id = ? ORDER BY date DESC',
        (user_id,)
    )
    sessions = cursor.fetchall()
    conn.close()
    
    return [dict(session) for session in sessions]

def save_score_history(user_id, reality_score, discipline_score, avoidance_score):
    """Save score history for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO score_history (user_id, reality_score, discipline_score, avoidance_score) VALUES (?, ?, ?, ?)',
        (user_id, reality_score, discipline_score, avoidance_score)
    )
    conn.commit()
    conn.close()

def get_user_score_history(user_id):
    """Get score history for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM score_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 10',
        (user_id,)
    )
    history = cursor.fetchall()
    conn.close()
    
    return [dict(entry) for entry in history]

def get_leaderboard_data(limit=50):
    """Get global leaderboard data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get latest scores for each user
    cursor.execute('''
        SELECT 
            u.id,
            u.username,
            MAX(sh.discipline_score) as discipline_score,
            MAX(sh.consistency) as consistency,
            MAX(sh.total_hours) as total_hours,
            MAX(sh.current_streak) as current_streak
        FROM users u
        LEFT JOIN (
            SELECT 
                user_id,
                discipline_score,
                consistency,
                total_hours,
                current_streak
            FROM latest_user_scores
        ) sh ON u.id = sh.user_id
        GROUP BY u.id, u.username
        ORDER BY discipline_score DESC, consistency DESC
        LIMIT ?
    ''', (limit,))
    
    leaderboard = cursor.fetchall()
    conn.close()
    
    return [dict(entry) for entry in leaderboard]

def update_user_scores():
    """Update the latest_user_scores table with current user stats"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS latest_user_scores (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            discipline_score INTEGER,
            consistency REAL,
            total_hours REAL,
            current_streak INTEGER,
            longest_streak INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Calculate streaks for each user
    cursor.execute('''
        INSERT OR REPLACE INTO latest_user_scores (user_id, username, discipline_score, consistency, total_hours, current_streak, longest_streak)
        SELECT 
            u.id,
            u.username,
            COALESCE(MAX(sh.discipline_score), 0) as discipline_score,
            COALESCE(AVG(CASE 
                WHEN julianday(date, 'weekday', 0) BETWEEN 0 AND 4 THEN 1 
                ELSE 0 
            END) * 100, 0) as consistency,
            COALESCE(SUM(ss.hours), 0) as total_hours,
            COALESCE(
                (SELECT COUNT(*) FROM (
                    SELECT date, COUNT(*) as day_count
                    FROM study_sessions 
                    WHERE user_id = u.id
                    GROUP BY date
                    HAVING day_count > 0
                    ORDER BY date DESC
                ) WHERE date >= date('now', '-7 days')
            ), 0
            ) as current_streak,
            COALESCE(
                (SELECT MAX(streak_length) FROM (
                    SELECT date, COUNT(*) as day_count,
                           ROW_NUMBER() OVER (ORDER BY date) as rn,
                           COUNT(*) OVER (PARTITION BY date) as streak_length
                    FROM study_sessions 
                    WHERE user_id = u.id
                    GROUP BY date
                )), 0
            ) as longest_streak
        FROM users u
        LEFT JOIN score_history sh ON u.id = sh.user_id
        LEFT JOIN study_sessions ss ON u.id = ss.user_id
        GROUP BY u.id, u.username
    ''')
    
    conn.commit()
    conn.close()

def get_user_streak(user_id):
    """Get current and longest streak for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT current_streak, longest_streak 
        FROM latest_user_scores 
        WHERE user_id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'current_streak': result[0] or 0,
            'longest_streak': result[1] or 0
        }
    return {'current_streak': 0, 'longest_streak': 0}

def update_streak(user_id, studied_today):
    """Update user's streak based on whether they studied today"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current streak
    cursor.execute('''
        SELECT current_streak, longest_streak 
        FROM latest_user_scores 
        WHERE user_id = ?
    ''', (user_id,))
    
    result = cursor.fetchone()
    
    if result:
        current_streak, longest_streak = result[0] or 0, result[1] or 0
        
        if studied_today:
            new_streak = current_streak + 1
            new_longest = max(new_streak, longest_streak)
        else:
            new_streak = 0
            new_longest = longest_streak
        
        cursor.execute('''
            UPDATE latest_user_scores 
            SET current_streak = ?, longest_streak = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (new_streak, new_longest, user_id))
    else:
        # New user, start streak
        new_streak = 1 if studied_today else 0
        new_longest = new_streak
        
        cursor.execute('''
            INSERT INTO latest_user_scores (user_id, current_streak, longest_streak)
            VALUES (?, ?, ?)
        ''', (user_id, new_streak, new_longest))
    
    conn.commit()
    conn.close()
    
    return {
        'current_streak': new_streak,
        'longest_streak': new_longest,
        'broke_streak': not studied_today and current_streak > 0
    }
