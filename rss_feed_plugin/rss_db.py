import sqlite3
import datetime
from traceback import print_exc
from logger import get_logger

logger = get_logger(__name__)

RSS_DB_PATH = "rss_feed.db"

def get_rss_db_connection():
    """Get connection to RSS database"""
    conn = sqlite3.connect(RSS_DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_rss_db():
    """Create RSS database and tables if they don't exist"""
    conn = None
    try:
        conn = get_rss_db_connection()
        cursor = conn.cursor()

        # Create RSS items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rss_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                published_date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index on published_date for faster sorting
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_published_date
            ON rss_items(published_date DESC)
        """)

        conn.commit()
        logger.info("RSS database initialized successfully")

    except Exception as e:
        logger.error(f"Error creating RSS database: {str(e)}", exc_info=True)
    finally:
        if conn:
            conn.close()

def add_rss_item(title, content, url, published_date=None):
    """Add new RSS item to database"""
    conn = None
    try:
        if published_date is None:
            published_date = datetime.datetime.now(datetime.timezone.utc)

        conn = get_rss_db_connection()
        cursor = conn.cursor()

        # Insert item (IGNORE duplicate URLs)
        cursor.execute("""
            INSERT OR IGNORE INTO rss_items (title, content, url, published_date)
            VALUES (?, ?, ?, ?)
        """, (title, content, url, published_date))

        if cursor.rowcount > 0:
            conn.commit()
            logger.debug(f"Added RSS item: {title}")
            return True
        else:
            logger.debug(f"RSS item already exists: {url}")
            return False

    except Exception as e:
        logger.error(f"Error adding RSS item: {str(e)}", exc_info=True)
        return False
    finally:
        if conn:
            conn.close()

def get_rss_items(limit=100):
    """Get RSS items from database, ordered by published_date DESC"""
    conn = None
    try:
        conn = get_rss_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT title, content, url, published_date
            FROM rss_items
            ORDER BY published_date DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

    except Exception as e:
        logger.error(f"Error getting RSS items: {str(e)}", exc_info=True)
        return []
    finally:
        if conn:
            conn.close()

def cleanup_old_rss_items(max_items=1000):
    """Remove old RSS items beyond max_items limit"""
    conn = None
    try:
        conn = get_rss_db_connection()
        cursor = conn.cursor()

        # Count total items
        cursor.execute("SELECT COUNT(*) FROM rss_items")
        total_items = cursor.fetchone()[0]

        if total_items > max_items:
            # Delete oldest items beyond the limit
            items_to_delete = total_items - max_items
            cursor.execute("""
                DELETE FROM rss_items
                WHERE id IN (
                    SELECT id FROM rss_items
                    ORDER BY published_date ASC
                    LIMIT ?
                )
            """, (items_to_delete,))

            conn.commit()
            logger.info(f"Cleaned up {cursor.rowcount} old RSS items")

    except Exception as e:
        logger.error(f"Error cleaning up RSS items: {str(e)}", exc_info=True)
    finally:
        if conn:
            conn.close()

def get_rss_items_count():
    """Get total count of RSS items"""
    conn = None
    try:
        conn = get_rss_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM rss_items")
        return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Error getting RSS items count: {str(e)}", exc_info=True)
        return 0
    finally:
        if conn:
            conn.close()

# Initialize database on module import
create_rss_db()