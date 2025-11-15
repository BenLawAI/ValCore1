"""
Main Window - Primary GUI for BookWritingTool
"""
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QMessageBox,
    QTabWidget,
    QFileDialog,
    QLineEdit,
    QSpinBox,
    QComboBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from loguru import logger

from app.models import Database, Project, Chapter
from app.core import LLMManager, LLMMode, LLMProvider, StyleEngine, Compiler, Exporter


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("BookWritingTool - Professional Writing Suite")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize data directory
        self.app_root = Path(__file__).parent.parent.parent
        self.data_dir = self.app_root / "data"
        self.projects_dir = self.app_root / "projects"
        self.projects_dir.mkdir(exist_ok=True)

        # Initialize database
        db_path = self.app_root / "config" / "app.db"
        db_path.parent.mkdir(exist_ok=True)
        self.db = Database(db_path)
        self.db.create_tables()

        # Initialize managers
        self.llm_manager: Optional[LLMManager] = None
        self.style_engine = StyleEngine(self.data_dir / "styles" / "author_profiles")
        self.current_project: Optional[Project] = None
        self.current_chapter: Optional[Chapter] = None
        self.compiler: Optional[Compiler] = None

        # Auto-save timer
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)

        # Setup UI
        self.setup_ui()

        logger.info("Main window initialized")

    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Top bar with project info
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # Tab widget for different sections
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Editor tab
        editor_tab = self.create_editor_tab()
        self.tabs.addTab(editor_tab, "✍️ Editor")

        # Style mixer tab
        style_tab = self.create_style_mixer_tab()
        self.tabs.addTab(style_tab, "🎨 Style Mixer")

        # Settings tab
        settings_tab = self.create_settings_tab()
        self.tabs.addTab(settings_tab, "⚙️ Settings")

        # Status bar
        self.statusBar().showMessage("Ready")

    def create_top_bar(self) -> QWidget:
        """Create top bar with project controls"""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Project label
        self.project_label = QLabel("No project loaded")
        self.project_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.project_label)

        layout.addStretch()

        # Word count
        self.word_count_label = QLabel("Words: 0")
        layout.addWidget(self.word_count_label)

        # New project button
        new_project_btn = QPushButton("📁 New Project")
        new_project_btn.clicked.connect(self.create_new_project)
        layout.addWidget(new_project_btn)

        # Export button
        export_btn = QPushButton("📤 Export")
        export_btn.clicked.connect(self.export_manuscript)
        layout.addWidget(export_btn)

        return widget

    def create_editor_tab(self) -> QWidget:
        """Create main editor tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Chapter selector
        chapter_bar = QHBoxLayout()
        chapter_bar.addWidget(QLabel("Chapter:"))

        self.chapter_selector = QComboBox()
        self.chapter_selector.currentTextChanged.connect(self.load_chapter)
        chapter_bar.addWidget(self.chapter_selector)

        new_chapter_btn = QPushButton("➕ New Chapter")
        new_chapter_btn.clicked.connect(self.create_new_chapter)
        chapter_bar.addWidget(new_chapter_btn)

        chapter_bar.addStretch()
        layout.addLayout(chapter_bar)

        # Editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier New", 11))
        self.editor.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.editor)

        # Bottom controls
        controls = QHBoxLayout()

        # Generate button
        generate_btn = QPushButton("🤖 Generate with AI")
        generate_btn.clicked.connect(self.generate_text)
        controls.addWidget(generate_btn)

        # Paste & compile button
        paste_compile_btn = QPushButton("📋 Paste & Compile")
        paste_compile_btn.clicked.connect(self.paste_and_compile)
        controls.addWidget(paste_compile_btn)

        # Save button
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_current_chapter)
        controls.addWidget(save_btn)

        controls.addStretch()

        layout.addLayout(controls)

        return widget

    def create_style_mixer_tab(self) -> QWidget:
        """Create style mixer tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Style Mixer - Select authors and adjust sliders"))

        # Author list
        layout.addWidget(QLabel("Available Authors:"))
        self.author_list_label = QLabel(", ".join(self.style_engine.list_authors()))
        layout.addWidget(self.author_list_label)

        # Simple style inputs (can be enhanced with sliders)
        layout.addWidget(QLabel("\nPrimary Author:"))
        self.primary_author = QComboBox()
        self.primary_author.addItems(self.style_engine.list_authors())
        layout.addWidget(self.primary_author)

        layout.addWidget(QLabel("Percentage (0-100):"))
        self.primary_percentage = QSpinBox()
        self.primary_percentage.setRange(0, 100)
        self.primary_percentage.setValue(100)
        layout.addWidget(self.primary_percentage)

        # Preview button
        preview_btn = QPushButton("👁️ Preview Style Prompt")
        preview_btn.clicked.connect(self.preview_style)
        layout.addWidget(preview_btn)

        # Preview area
        self.style_preview = QTextEdit()
        self.style_preview.setReadOnly(True)
        layout.addWidget(self.style_preview)

        layout.addStretch()

        return widget

    def create_settings_tab(self) -> QWidget:
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("LLM Settings"))

        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))

        self.online_mode_btn = QPushButton("☁️ Online")
        self.online_mode_btn.setCheckable(True)
        self.online_mode_btn.clicked.connect(lambda: self.set_llm_mode(LLMMode.ONLINE))
        mode_layout.addWidget(self.online_mode_btn)

        self.offline_mode_btn = QPushButton("💻 Offline")
        self.offline_mode_btn.setCheckable(True)
        self.offline_mode_btn.clicked.connect(lambda: self.set_llm_mode(LLMMode.OFFLINE))
        mode_layout.addWidget(self.offline_mode_btn)

        self.online_mode_btn.setChecked(True)  # Default

        layout.addLayout(mode_layout)

        # API keys
        layout.addWidget(QLabel("\nClaude API Key:"))
        self.claude_key_input = QLineEdit()
        self.claude_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.claude_key_input)

        layout.addWidget(QLabel("OpenAI API Key:"))
        self.openai_key_input = QLineEdit()
        self.openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.openai_key_input)

        # Initialize LLM button
        init_llm_btn = QPushButton("✅ Initialize LLM Manager")
        init_llm_btn.clicked.connect(self.initialize_llm)
        layout.addWidget(init_llm_btn)

        # Cost display
        self.cost_label = QLabel("Session Cost: $0.00")
        layout.addWidget(self.cost_label)

        layout.addStretch()

        return widget

    def create_new_project(self):
        """Create a new book project"""
        # Simple dialog (can be enhanced)
        from PyQt6.QtWidgets import QInputDialog

        title, ok = QInputDialog.getText(self, "New Project", "Enter book title:")

        if ok and title:
            session = self.db.get_session()

            project = Project(
                title=title, project_folder=str(self.projects_dir / title.replace(" ", "_"))
            )

            session.add(project)
            session.commit()

            self.current_project = project
            self.compiler = Compiler(Path(project.project_folder))

            self.project_label.setText(f"Project: {project.title}")
            self.statusBar().showMessage(f"Created project: {title}")

            # Start autosave
            self.autosave_timer.start(30000)  # 30 seconds

            session.close()
            logger.info(f"Created new project: {title}")

    def create_new_chapter(self):
        """Create a new chapter"""
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please create or load a project first")
            return

        from PyQt6.QtWidgets import QInputDialog

        title, ok = QInputDialog.getText(self, "New Chapter", "Enter chapter title:")

        if ok and title:
            session = self.db.get_session()

            # Get next order index
            existing_chapters = (
                session.query(Chapter)
                .filter(Chapter.project_id == self.current_project.id)
                .count()
            )

            chapter = Chapter(
                project_id=self.current_project.id,
                title=title,
                order_index=existing_chapters + 1,
                file_path=str(Path(self.current_project.project_folder) / "chapters" / f"{title.replace(' ', '_')}.md"),
            )

            session.add(chapter)
            session.commit()

            self.chapter_selector.addItem(f"{chapter.order_index}. {chapter.title}")
            self.statusBar().showMessage(f"Created chapter: {title}")

            session.close()
            logger.info(f"Created chapter: {title}")

    def load_chapter(self, chapter_text: str):
        """Load a chapter into the editor"""
        # This is simplified - in full version, load from database and file
        pass

    def generate_text(self):
        """Generate text using LLM"""
        if not self.llm_manager:
            QMessageBox.warning(self, "LLM Not Initialized", "Please configure LLM settings first")
            return

        # Get prompt from user
        from PyQt6.QtWidgets import QInputDialog

        prompt, ok = QInputDialog.getText(
            self, "Generate Text", "Enter your writing prompt:"
        )

        if ok and prompt:
            try:
                # Get style settings
                author = self.primary_author.currentText()
                percentage = self.primary_percentage.value() / 100.0

                style_mix = {author: percentage}

                # Generate style prompt
                full_prompt = self.style_engine.generate_prompt(
                    prompt, style_mix, tone=0.5, formality=0.5, sentence_length=0.5
                )

                # Generate with LLM
                self.statusBar().showMessage("Generating...")
                result = self.llm_manager.generate(full_prompt, max_tokens=2000)

                # Show result in a dialog
                QMessageBox.information(
                    self, "Generated Text", f"Copy this and paste into editor:\n\n{result['text'][:500]}..."
                )

                # Update cost
                if self.llm_manager:
                    cost = self.llm_manager.get_session_cost()
                    self.cost_label.setText(f"Session Cost: ${cost:.2f}")

                self.statusBar().showMessage("Generation complete")

            except Exception as e:
                logger.error(f"Generation failed: {e}")
                QMessageBox.critical(self, "Error", f"Generation failed: {e}")

    def paste_and_compile(self):
        """Paste clipboard content and compile into chapter"""
        from PyQt6.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if text:
            # Append to current editor
            self.editor.append("\n\n" + text)
            self.statusBar().showMessage("Text pasted and compiled")
        else:
            QMessageBox.warning(self, "Empty Clipboard", "Clipboard is empty")

    def save_current_chapter(self):
        """Save current chapter"""
        if not self.current_project:
            return

        content = self.editor.toPlainText()

        # Save to file (simplified - full version uses compiler)
        if self.compiler and self.current_chapter:
            chapter_file = Path(self.current_chapter.file_path)
            chapter_file.parent.mkdir(parents=True, exist_ok=True)
            chapter_file.write_text(content, encoding="utf-8")

            self.statusBar().showMessage("Chapter saved")
            logger.info("Chapter saved")

    def autosave(self):
        """Auto-save current work"""
        if self.current_project and self.current_chapter:
            self.save_current_chapter()
            logger.debug("Auto-save triggered")

    def on_text_changed(self):
        """Update word count when text changes"""
        text = self.editor.toPlainText()
        words = len(text.split())
        self.word_count_label.setText(f"Words: {words}")

    def initialize_llm(self):
        """Initialize LLM manager with API keys"""
        claude_key = self.claude_key_input.text()
        openai_key = self.openai_key_input.text()

        if not claude_key and not openai_key:
            QMessageBox.warning(self, "No API Keys", "Please enter at least one API key")
            return

        try:
            mode = LLMMode.ONLINE if self.online_mode_btn.isChecked() else LLMMode.OFFLINE

            self.llm_manager = LLMManager(
                mode=mode,
                claude_api_key=claude_key if claude_key else None,
                openai_api_key=openai_key if openai_key else None,
                primary_provider=LLMProvider.CLAUDE,
            )

            self.statusBar().showMessage("LLM Manager initialized")
            QMessageBox.information(self, "Success", "LLM Manager initialized successfully")
            logger.info(f"LLM Manager initialized in {mode.value} mode")

        except Exception as e:
            logger.error(f"LLM initialization failed: {e}")
            QMessageBox.critical(self, "Error", f"LLM initialization failed: {e}")

    def set_llm_mode(self, mode: LLMMode):
        """Set LLM mode"""
        if mode == LLMMode.ONLINE:
            self.online_mode_btn.setChecked(True)
            self.offline_mode_btn.setChecked(False)
        else:
            self.online_mode_btn.setChecked(False)
            self.offline_mode_btn.setChecked(True)

        if self.llm_manager:
            self.llm_manager.switch_mode(mode)
            self.statusBar().showMessage(f"Switched to {mode.value} mode")

    def preview_style(self):
        """Preview style-blended prompt"""
        author = self.primary_author.currentText()
        percentage = self.primary_percentage.value() / 100.0

        style_mix = {author: percentage}

        prompt = self.style_engine.blend_styles(
            style_mix, tone=0.5, formality=0.5, sentence_length=0.5
        )

        self.style_preview.setText(prompt)

    def export_manuscript(self):
        """Export manuscript to Word/PDF"""
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please create or load a project first")
            return

        # Get export path
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Manuscript",
            str(self.projects_dir / f"{self.current_project.title}.docx"),
            "Word Document (*.docx);;PDF Document (*.pdf);;Plain Text (*.txt)",
        )

        if file_path:
            try:
                exporter = Exporter()
                session = self.db.get_session()

                # Get all chapters
                chapters = (
                    session.query(Chapter)
                    .filter(Chapter.project_id == self.current_project.id)
                    .order_by(Chapter.order_index)
                    .all()
                )

                chapter_files = [Path(ch.file_path) for ch in chapters if Path(ch.file_path).exists()]

                if ".docx" in file_path:
                    exporter.export_to_word(
                        chapter_files,
                        Path(file_path),
                        title=self.current_project.title,
                        author="Author",
                    )
                elif ".pdf" in file_path:
                    exporter.export_to_pdf(
                        chapter_files,
                        Path(file_path),
                        title=self.current_project.title,
                        author="Author",
                    )
                else:
                    exporter.export_to_text(chapter_files, Path(file_path))

                self.statusBar().showMessage(f"Exported to {file_path}")
                QMessageBox.information(self, "Export Complete", f"Manuscript exported to:\n{file_path}")

                session.close()

            except Exception as e:
                logger.error(f"Export failed: {e}")
                QMessageBox.critical(self, "Export Error", f"Export failed: {e}")
