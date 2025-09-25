from flask import Flask, Response, request
import threading, time, db, datetime, html
from queue import Empty as QueueEmpty
from logger import get_logger
from feedgen.feed import FeedGenerator

# Import RSS database functions
try:
    from .rss_db import add_rss_item, get_rss_items, cleanup_old_rss_items
except ImportError:
    # Fallback for when running as main module
    from rss_feed_plugin.rss_db import add_rss_item, get_rss_items, cleanup_old_rss_items

# Get logger for this module
logger = get_logger(__name__)


class RSSFeed:
    def __init__(self, queue):
        self.app = Flask(__name__)
        self.queue = queue
        # Do not cache max_items; fetch from DB when needed

        # RSS feed will be generated dynamically from database

        # Set up routes
        self.app.route('/')(self.serve_rss)

        # Start thread to check queue
        self.thread = threading.Thread(target=self.run_check_queue)
        self.thread.daemon = True
        self.thread.start()

        # Periodic cleanup of old items
        self.cleanup_thread = threading.Thread(target=self.periodic_cleanup)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()

    def run_check_queue(self):
        while True:
            try:
                # Drain the queue without relying on Queue.empty(), which is unreliable
                processed = 0
                while True:
                    try:
                        content, url, text, buy_url, buy_text = self.queue.get_nowait()
                        self.add_item_to_feed(content, url)
                        processed += 1
                    except QueueEmpty:
                        break
                    except Exception as e:
                        logger.error(f"Error getting item from RSS queue: {str(e)}", exc_info=True)
                        break
                if processed == 0:
                    time.sleep(0.1)  # Small sleep to prevent high CPU usage when idle
            except Exception as e:
                logger.error(f"Error checking RSS queue: {str(e)}", exc_info=True)

    def periodic_cleanup(self):
        """Periodically clean up old RSS items"""
        while True:
            try:
                time.sleep(3600)  # Run cleanup every hour
                # Re-read max_items from DB to honor config changes without restart
                try:
                    max_items = int(db.get_parameter("rss_max_items"))
                except Exception:
                    max_items = 100
                cleanup_old_rss_items(max_items * 10)  # Keep 10x max for buffer
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {str(e)}", exc_info=True)

    def check_rss_queue(self):
        # Deprecated by run_check_queue drain logic; keep for backward compatibility
        try:
            while True:
                content, url, text, buy_url, buy_text = self.queue.get_nowait()
                self.add_item_to_feed(content, url)
        except QueueEmpty:
            return
        except Exception as e:
            logger.error(f"Error processing item for RSS feed: {str(e)}", exc_info=True)

    def add_item_to_feed(self, content, url):
        # Extract title from content (assuming it's in the format from configuration_values.MESSAGE)
        title = "New Vinted Item"
        try:
            # Try to extract title from the content
            title_start = content.find('🆕 Title : ') + len('🆕 Title : ')
            if title_start > len('🆕 Title : '):
                title_end = content.find('\n', title_start)
                if title_end > 0:
                    title = content[title_start:title_end]
        except:
            pass

        # Add item to RSS database
        published_date = datetime.datetime.now(datetime.timezone.utc)
        success = add_rss_item(title, content, url, published_date)

        if success:
            logger.debug(f"Added RSS item to database: {title}")
        else:
            logger.debug(f"RSS item already exists in database: {url}")

    def serve_rss(self):
        """Generate RSS feed dynamically from database"""
        try:
            # Create fresh feed generator
            fg = FeedGenerator()
            fg.title('Vinted Notifications')
            fg.description('Latest items from Vinted matching your search queries')
            # Use the actual host seen by the client instead of localhost
            fg.link(href=request.host_url.rstrip('/'))
            fg.language('en')

            # Get items from database
            try:
                max_items = int(db.get_parameter("rss_max_items"))
            except Exception:
                max_items = 100
            items = get_rss_items(limit=max_items)

            # Add each item to the feed
            for title, content, url, published_date in items:
                fe = fg.add_entry()
                fe.id(url)
                fe.title(title)
                fe.link(href=url)
                fe.description(html.escape(content))

                # Parse published_date if it's a string
                if isinstance(published_date, str):
                    try:
                        published_date = datetime.datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                    except:
                        published_date = datetime.datetime.now(datetime.timezone.utc)

                fe.published(published_date)

            return Response(fg.rss_str(), mimetype='application/rss+xml')

        except Exception as e:
            logger.error(f"Error generating RSS feed: {str(e)}", exc_info=True)
            # Return empty feed on error
            fg = FeedGenerator()
            fg.title('Vinted Notifications')
            fg.description('Error generating feed')
            fg.link(href=request.host_url.rstrip('/'))
            fg.language('en')
            return Response(fg.rss_str(), mimetype='application/rss+xml')

    def run(self):

        try:
            # Ensure port is an int
            try:
                port = int(db.get_parameter("rss_port"))
            except Exception:
                port = 8001
            logger.info(f"Starting RSS feed server on port {port}")
            self.app.run(host='0.0.0.0', port=port)
        except Exception as e:
            logger.error(f"Error starting RSS feed server: {str(e)}", exc_info=True)


def rss_feed_process(queue):
    """
    Process function for the RSS feed.
    
    Args:
        queue (Queue): The queue to get new items from
    """
    logger.info("RSS feed process started")
    try:
        feed = RSSFeed(queue)
        feed.run()
    except (KeyboardInterrupt, SystemExit):
        logger.info("RSS feed process stopped")
    except Exception as e:
        logger.error(f"Error in RSS feed process: {e}", exc_info=True)
