"""
VALCORE1 Memory Compression
Daily/Monthly/Yearly conversation compression with semantic importance
"""

import logging
import json
import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not available")

logger = logging.getLogger(__name__)


class MemoryCompressor:
    """Manages memory compression with semantic importance scoring"""

    def __init__(self, config_path: str, librarian):
        """
        Initialize memory compressor

        Args:
            config_path: Path to compression strategy config
            librarian: Librarian instance for LLM summaries
        """
        self.config = self._load_config(config_path)
        self.librarian = librarian
        self.library_path = Path(librarian.library_path)

        # Initialize sentence transformer for importance scoring
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            logger.warning("Semantic importance scoring disabled")
            self.embedder = None

        # Scheduler thread
        self.scheduler_thread = None
        self.scheduler_running = False

        logger.info("Memory compressor initialized")

    def _load_config(self, path: str) -> dict:
        """Load compression strategy configuration"""
        with open(path, 'r') as f:
            return json.load(f)

    def score_semantic_importance(self, text: str, category: str) -> float:
        """
        Score text importance based on semantic content

        Args:
            text: Text to score
            category: Category (for boost/penalty)

        Returns:
            Importance score (0.0-1.0)
        """
        if not self.embedder:
            # Default scoring without embeddings
            if category in self.config['daily_compression']['preserve_categories']:
                return 0.9
            elif category in self.config['daily_compression']['discard_categories']:
                return 0.3
            else:
                return 0.5

        # Generate embeddings
        text_embedding = self.embedder.encode(text)

        # Importance keywords
        high_importance_keywords = [
            "decided", "critical", "error", "bug", "fix", "solution",
            "important", "must", "required", "action item", "todo"
        ]
        medium_importance_keywords = [
            "discussed", "explained", "example", "consider", "maybe",
            "option", "alternative", "suggestion"
        ]
        low_importance_keywords = [
            "hello", "thanks", "okay", "sure", "yeah", "hmm",
            "interesting", "cool", "nice"
        ]

        # Generate keyword embeddings
        high_embedding = self.embedder.encode(' '.join(high_importance_keywords))
        medium_embedding = self.embedder.encode(' '.join(medium_importance_keywords))
        low_embedding = self.embedder.encode(' '.join(low_importance_keywords))

        # Cosine similarity
        high_sim = np.dot(text_embedding, high_embedding) / (
            np.linalg.norm(text_embedding) * np.linalg.norm(high_embedding)
        )
        medium_sim = np.dot(text_embedding, medium_embedding) / (
            np.linalg.norm(text_embedding) * np.linalg.norm(medium_embedding)
        )
        low_sim = np.dot(text_embedding, low_embedding) / (
            np.linalg.norm(text_embedding) * np.linalg.norm(low_embedding)
        )

        # Category boost
        category_config = self.config['daily_compression']
        if category in category_config['preserve_categories']:
            return max(high_sim, 0.85)  # Minimum 0.85
        elif category in category_config['discard_categories']:
            return min(low_sim, 0.4)  # Maximum 0.4

        # Return highest similarity
        return max(high_sim, medium_sim, low_sim)

    def compress_daily_summary(self, date: datetime) -> Dict:
        """
        Compress day's conversations into summary

        Args:
            date: Date to compress

        Returns:
            Compressed summary dictionary
        """
        logger.info(f"Compressing daily summary for {date:%Y-%m-%d}")

        # Load day's conversations
        daily_file = self.library_path / f"daily/{date:%Y-%m-%d}.json"

        if not daily_file.exists():
            logger.warning(f"No data for {date:%Y-%m-%d}")
            return {}

        with open(daily_file, 'r') as f:
            conversations = json.load(f)

        # Backup before compression
        if self.config['backup_before_compression']:
            backup_file = self.library_path / f"backups/{date:%Y-%m-%d}_pre_compress.json"
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            with open(backup_file, 'w') as f:
                json.dump(conversations, f, indent=2)
            logger.info(f"Backup created: {backup_file}")

        # Compress
        compressed = {
            "date": date.isoformat(),
            "summary": "",
            "key_decisions": [],
            "action_items": [],
            "errors": [],
            "token_count": 0
        }

        strategy = self.config['daily_compression']

        for conv in conversations:
            text = conv.get('text', '')
            category = conv.get('category', 'general')

            # Score importance
            importance = self.score_semantic_importance(text, category)

            # Filter by importance thresholds
            if importance >= strategy['semantic_importance']['high']['threshold']:
                # Keep 100% of high importance
                if category == 'decision':
                    compressed['key_decisions'].append(text)
                elif category == 'action_item':
                    compressed['action_items'].append(text)
                elif category == 'error':
                    compressed['errors'].append(text)
                else:
                    compressed['summary'] += f"{text} "

            elif importance >= strategy['semantic_importance']['medium']['threshold']:
                # Keep percentage of medium importance
                keep_pct = strategy['semantic_importance']['medium']['keep_percentage']
                if np.random.random() * 100 < keep_pct:
                    compressed['summary'] += f"{text} "

            elif importance >= strategy['semantic_importance']['low']['threshold']:
                # Keep percentage of low importance
                keep_pct = strategy['semantic_importance']['low']['keep_percentage']
                if np.random.random() * 100 < keep_pct:
                    compressed['summary'] += f"{text} "

        # Trim to token budget
        max_tokens = strategy['target_tokens']
        compressed['summary'] = self._trim_to_token_budget(compressed['summary'], max_tokens)
        compressed['token_count'] = self._estimate_tokens(compressed['summary'])

        # Save compressed version
        compressed_file = self.library_path / f"daily/{date:%Y-%m-%d}_compressed.json"
        with open(compressed_file, 'w') as f:
            json.dump(compressed, f, indent=2)

        logger.info(f"Daily compression complete: {compressed['token_count']} tokens")

        return compressed

    def compress_monthly_rollup(self, year: int, month: int) -> Dict:
        """
        Compress month's daily summaries into monthly rollup

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Monthly rollup dictionary
        """
        logger.info(f"Compressing monthly rollup for {year}-{month:02d}")

        # Find all daily compressed files for this month
        daily_dir = self.library_path / "daily"
        pattern = f"{year}-{month:02d}-*_compressed.json"

        daily_files = list(daily_dir.glob(pattern))

        if not daily_files:
            logger.warning(f"No daily summaries for {year}-{month:02d}")
            return {}

        # Aggregate
        monthly = {
            "year": year,
            "month": month,
            "summary": "",
            "key_decisions": [],
            "action_items": [],
            "errors": [],
            "token_count": 0
        }

        for daily_file in sorted(daily_files):
            with open(daily_file, 'r') as f:
                daily = json.load(f)

            monthly['summary'] += daily.get('summary', '') + " "
            monthly['key_decisions'].extend(daily.get('key_decisions', []))
            monthly['action_items'].extend(daily.get('action_items', []))
            monthly['errors'].extend(daily.get('errors', []))

        # Trim to budget
        max_tokens = self.config['monthly_rollup']['target_tokens']
        monthly['summary'] = self._trim_to_token_budget(monthly['summary'], max_tokens)
        monthly['token_count'] = self._estimate_tokens(monthly['summary'])

        # Save monthly rollup
        monthly_dir = self.library_path / "monthly"
        monthly_dir.mkdir(parents=True, exist_ok=True)
        monthly_file = monthly_dir / f"{year}-{month:02d}.json"

        with open(monthly_file, 'w') as f:
            json.dump(monthly, f, indent=2)

        logger.info(f"Monthly rollup complete: {monthly['token_count']} tokens")

        return monthly

    def compress_yearly_archive(self, year: int) -> Dict:
        """
        Compress year's monthly rollups into yearly archive

        Args:
            year: Year

        Returns:
            Yearly archive dictionary
        """
        logger.info(f"Compressing yearly archive for {year}")

        # Find all monthly rollups for this year
        monthly_dir = self.library_path / "monthly"
        pattern = f"{year}-*.json"

        monthly_files = list(monthly_dir.glob(pattern))

        if not monthly_files:
            logger.warning(f"No monthly rollups for {year}")
            return {}

        # Aggregate
        yearly = {
            "year": year,
            "summary": "",
            "key_highlights": [],
            "token_count": 0,
            "statistics": {}
        }

        for monthly_file in sorted(monthly_files):
            with open(monthly_file, 'r') as f:
                monthly = json.load(f)

            yearly['summary'] += monthly.get('summary', '') + " "
            yearly['key_highlights'].extend(monthly.get('key_decisions', []))

        # Trim to budget
        max_tokens = self.config['yearly_archive']['target_tokens']
        yearly['summary'] = self._trim_to_token_budget(yearly['summary'], max_tokens)
        yearly['token_count'] = self._estimate_tokens(yearly['summary'])

        # Save yearly archive
        yearly_dir = self.library_path / "yearly"
        yearly_dir.mkdir(parents=True, exist_ok=True)
        yearly_file = yearly_dir / f"{year}.json"

        with open(yearly_file, 'w') as f:
            json.dump(yearly, f, indent=2)

        logger.info(f"Yearly archive complete: {yearly['token_count']} tokens")

        return yearly

    def _trim_to_token_budget(self, text: str, max_tokens: int) -> str:
        """
        Trim text to approximate token count

        Args:
            text: Text to trim
            max_tokens: Maximum tokens

        Returns:
            Trimmed text
        """
        # Approximate: 4 characters = 1 token
        max_chars = max_tokens * 4
        return text[:max_chars]

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count

        Args:
            text: Text

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def rollback_compression(self, date: datetime) -> bool:
        """
        Restore from backup if compression was faulty

        Args:
            date: Date to rollback

        Returns:
            True if successful
        """
        backup_file = self.library_path / f"backups/{date:%Y-%m-%d}_pre_compress.json"

        if not backup_file.exists():
            logger.error(f"No backup found for {date:%Y-%m-%d}")
            return False

        # Restore original file
        daily_file = self.library_path / f"daily/{date:%Y-%m-%d}.json"

        with open(backup_file, 'r') as f:
            original_data = json.load(f)

        with open(daily_file, 'w') as f:
            json.dump(original_data, f, indent=2)

        logger.info(f"Rollback complete for {date:%Y-%m-%d}")

        return True

    def daily_compression_job(self):
        """Job to run daily compression"""
        logger.info("Running daily compression job...")

        # Compress yesterday's data
        yesterday = datetime.now() - timedelta(days=1)
        self.compress_daily_summary(yesterday)

    def start_scheduler(self):
        """Start background compression scheduler"""
        # Schedule daily job
        schedule_time = self.config['daily']['time']
        schedule.every().day.at(schedule_time).do(self.daily_compression_job)

        # Run catch-up if needed
        self._catchup_compression()

        # Start scheduler thread
        def run_scheduler():
            self.scheduler_running = True
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()

        logger.info(f"Compression scheduler started (daily at {schedule_time})")

    def stop_scheduler(self):
        """Stop compression scheduler"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

        logger.info("Compression scheduler stopped")

    def _catchup_compression(self):
        """Run compression for any missed days"""
        logger.info("Checking for missed compressions...")

        try:
            # Find the last compressed date
            daily_path = self.library_path / "daily"

            if not daily_path.exists():
                logger.info("No daily directory - no catchup needed")
                return

            # Find all compressed files
            compressed_files = list(daily_path.glob("*_compressed.json"))

            if not compressed_files:
                logger.info("No previous compressions found - starting fresh")
                # Compress yesterday if we've never compressed before
                yesterday = datetime.now() - timedelta(days=1)
                self.compress_daily_summary(yesterday)
                return

            # Get the most recent compressed date
            dates = []
            for f in compressed_files:
                try:
                    # Extract date from filename like "2025-11-13_compressed.json"
                    date_str = f.stem.replace('_compressed', '')
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    dates.append(date)
                except ValueError:
                    continue

            if not dates:
                logger.warning("Could not parse any compression dates")
                return

            last_compressed = max(dates)
            yesterday = datetime.now() - timedelta(days=1)

            # Calculate days to catch up
            days_behind = (yesterday - last_compressed).days

            if days_behind <= 0:
                logger.info("Compression is up to date")
                return

            logger.info(f"Found {days_behind} days to catch up on compression")

            # Compress each missing day
            for i in range(1, days_behind + 1):
                date_to_compress = last_compressed + timedelta(days=i)

                # Don't compress today or future dates
                if date_to_compress >= datetime.now():
                    break

                logger.info(f"Running catchup compression for {date_to_compress:%Y-%m-%d}")
                self.compress_daily_summary(date_to_compress)

            logger.info("Catchup compression complete")

        except Exception as e:
            logger.error(f"Error during catchup compression: {e}", exc_info=True)
