"""
Compiler Module - Handles copy-paste-compile workflow
Assembles text into chapters and manages manuscript compilation
"""
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from loguru import logger


class Compiler:
    """Manages text compilation and chapter assembly"""

    def __init__(self, project_folder: Path):
        """Initialize compiler for a project

        Args:
            project_folder: Root folder for the project
        """
        self.project_folder = project_folder
        self.chapters_folder = project_folder / "chapters"
        self.chapters_folder.mkdir(parents=True, exist_ok=True)

    def append_to_chapter(
        self, chapter_file: Path, text: str, auto_save: bool = True, dedup_check: bool = True
    ) -> bool:
        """Append text to a chapter file

        Args:
            chapter_file: Path to chapter markdown file
            text: Text to append
            auto_save: Whether to save immediately
            dedup_check: Check if text was already pasted

        Returns:
            True if text was appended, False if duplicate detected
        """
        # Clean input text
        text = text.strip()
        if not text:
            logger.warning("Empty text provided, nothing to append")
            return False

        # Read existing content
        existing_content = ""
        if chapter_file.exists():
            existing_content = chapter_file.read_text(encoding="utf-8")

        # Deduplication check
        if dedup_check and text in existing_content:
            logger.warning("Duplicate text detected, not appending")
            return False

        # Append with proper spacing
        if existing_content and not existing_content.endswith("\n\n"):
            separator = "\n\n" if existing_content.endswith("\n") else "\n\n"
        else:
            separator = ""

        new_content = existing_content + separator + text + "\n"

        if auto_save:
            chapter_file.write_text(new_content, encoding="utf-8")
            logger.info(f"Appended {len(text)} characters to {chapter_file.name}")

        return True

    def compile_manuscript(
        self, chapter_files: List[Path], output_file: Path, include_chapter_headers: bool = True
    ) -> Path:
        """Compile multiple chapters into a single manuscript file

        Args:
            chapter_files: List of chapter files in order
            output_file: Output file path for compiled manuscript
            include_chapter_headers: Whether to add "# Chapter N" headers

        Returns:
            Path to compiled file
        """
        compiled_content = []

        for idx, chapter_file in enumerate(chapter_files, start=1):
            if not chapter_file.exists():
                logger.warning(f"Chapter file not found: {chapter_file}")
                continue

            chapter_text = chapter_file.read_text(encoding="utf-8")

            if include_chapter_headers:
                chapter_title = chapter_file.stem.replace("_", " ").title()
                header = f"# Chapter {idx}: {chapter_title}\n\n"
                compiled_content.append(header)

            compiled_content.append(chapter_text)
            compiled_content.append("\n\n---\n\n")  # Chapter separator

        # Write compiled manuscript
        output_file.parent.mkdir(parents=True, exist_ok=True)
        final_text = "".join(compiled_content)
        output_file.write_text(final_text, encoding="utf-8")

        logger.info(f"Compiled {len(chapter_files)} chapters to {output_file}")
        return output_file

    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())

    def get_chapter_word_count(self, chapter_file: Path) -> int:
        """Get word count for a chapter file"""
        if not chapter_file.exists():
            return 0

        content = chapter_file.read_text(encoding="utf-8")
        return self.count_words(content)

    def create_backup(self, chapter_file: Path) -> Path:
        """Create timestamped backup of chapter

        Args:
            chapter_file: Chapter file to backup

        Returns:
            Path to backup file
        """
        if not chapter_file.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {chapter_file}")

        backup_folder = self.project_folder / "backups"
        backup_folder.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{chapter_file.stem}_{timestamp}.md"
        backup_file = backup_folder / backup_name

        content = chapter_file.read_text(encoding="utf-8")
        backup_file.write_text(content, encoding="utf-8")

        logger.info(f"Created backup: {backup_file.name}")
        return backup_file

    def insert_text(
        self,
        chapter_file: Path,
        text: str,
        position: int = -1,
        create_backup: bool = True,
    ) -> bool:
        """Insert text at specific position in chapter

        Args:
            chapter_file: Chapter file
            text: Text to insert
            position: Character position (default -1 = append)
            create_backup: Create backup before modifying

        Returns:
            True if successful
        """
        if not chapter_file.exists():
            logger.warning(f"Chapter file doesn't exist: {chapter_file}")
            return False

        # Backup first
        if create_backup:
            self.create_backup(chapter_file)

        content = chapter_file.read_text(encoding="utf-8")

        if position == -1 or position >= len(content):
            # Append
            new_content = content + "\n\n" + text.strip() + "\n"
        else:
            # Insert at position
            new_content = content[:position] + text + content[position:]

        chapter_file.write_text(new_content, encoding="utf-8")
        logger.info(f"Inserted text into {chapter_file.name}")
        return True

    def replace_text(
        self, chapter_file: Path, old_text: str, new_text: str, create_backup: bool = True
    ) -> bool:
        """Replace text in chapter

        Args:
            chapter_file: Chapter file
            old_text: Text to find and replace
            new_text: Replacement text
            create_backup: Create backup before modifying

        Returns:
            True if replacement made
        """
        if not chapter_file.exists():
            logger.warning(f"Chapter file doesn't exist: {chapter_file}")
            return False

        # Backup first
        if create_backup:
            self.create_backup(chapter_file)

        content = chapter_file.read_text(encoding="utf-8")

        if old_text not in content:
            logger.warning(f"Text not found in chapter: '{old_text[:50]}...'")
            return False

        new_content = content.replace(old_text, new_text)
        chapter_file.write_text(new_content, encoding="utf-8")

        logger.info(f"Replaced text in {chapter_file.name}")
        return True
