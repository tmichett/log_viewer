import sys
import yaml
import re
import os
import argparse
import time
import warnings

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, 
                           QVBoxLayout, QWidget, QPushButton, QFileDialog,
                           QHBoxLayout, QLineEdit, QLabel, QListWidget, 
                           QColorDialog, QDialog, QFormLayout,
                           QDialogButtonBox, QMessageBox, QInputDialog,
                           QProgressBar, QScrollBar, QPlainTextEdit)
from PyQt6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter, QPalette, QTextCursor
from PyQt6.QtCore import (Qt, QRunnable, QThreadPool, pyqtSignal, QObject, 
                         pyqtSlot, QTimer, QSize)

# Define constant values for Qt enums that might differ between PyQt versions
class QtConstants:
    # QTextCursor movement constants
    MoveStart = 11  # QTextCursor.Start
    MoveEnd = 12    # QTextCursor.End
    
    # QTextCursor move operation constants
    NextCharacter = 1   # QTextCursor.NextCharacter
    StartOfLine = 10    # QTextCursor.StartOfLine
    EndOfLine = 11      # QTextCursor.EndOfLine
    
    # QTextCursor move mode constants
    KeepAnchor = 1      # QTextCursor.KeepAnchor
    
    # Line wrap mode constants
    NoWrap = 0      # QPlainTextEdit.NoWrap
    WidgetWidth = 1 # QPlainTextEdit.WidgetWidth
    
    # Dialog result constants
    Accepted = 1    # QDialog.Accepted
    Rejected = 0    # QDialog.Rejected
    
    # Dialog button constants
    Ok = 0x00000400       # QDialogButtonBox.Ok
    Cancel = 0x00000800   # QDialogButtonBox.Cancel

class AnsiColorParser:
    def __init__(self):
        self.reset_format = QTextCharFormat()
        self.reset_format.setForeground(QColor(255, 255, 255))  # Default white text
        
        # ANSI color mapping
        self.colors = {
            30: QColor(0, 0, 0),        # Black
            31: QColor(255, 0, 0),      # Red
            32: QColor(0, 255, 0),      # Green
            33: QColor(255, 255, 0),    # Yellow
            34: QColor(0, 0, 255),      # Blue
            35: QColor(255, 0, 255),    # Magenta
            36: QColor(0, 255, 255),    # Cyan
            37: QColor(255, 255, 255),  # White
            90: QColor(128, 128, 128),  # Bright Black
            91: QColor(255, 128, 128),  # Bright Red
            92: QColor(128, 255, 128),  # Bright Green
            93: QColor(255, 255, 128),  # Bright Yellow
            94: QColor(128, 128, 255),  # Bright Blue
            95: QColor(255, 128, 255),  # Bright Magenta
            96: QColor(128, 255, 255),  # Bright Cyan
            97: QColor(255, 255, 255),  # Bright White
        }

    def parse_ansi(self, text):
        # Regular expression to match ANSI escape sequences
        ansi_pattern = re.compile(r'\x1b\[([0-9;]*)m')
        
        # Split text into segments based on ANSI codes
        segments = []
        last_end = 0
        current_format = self.reset_format
        
        for match in ansi_pattern.finditer(text):
            # Add text before the ANSI code
            if match.start() > last_end:
                segments.append((text[last_end:match.start()], current_format))
            
            # Parse the ANSI code
            code = match.group(1)
            if code == '0' or code == '':
                current_format = self.reset_format
            else:
                format = QTextCharFormat()
                codes = [int(c) for c in code.split(';')]
                for c in codes:
                    if c in self.colors:
                        format.setForeground(self.colors[c])
                current_format = format
            
            last_end = match.end()
        
        # Add any remaining text
        if last_end < len(text):
            segments.append((text[last_end:], current_format))
        
        return segments

class LogHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlight_terms = []
        self.default_highlight_format = QTextCharFormat()
        # Default cornflower blue color for highlighting with black text
        self.default_highlight_format.setBackground(QColor(100, 149, 237))
        self.default_highlight_format.setForeground(QColor(0, 0, 0))

    def set_highlight_terms(self, terms):
        self.highlight_terms = []
        for term in terms:
            if isinstance(term, dict):
                # New format with optional color
                highlight_format = QTextCharFormat()
                if 'color' in term:
                    # Convert hex color to QColor
                    color = QColor(term['color'])
                    highlight_format.setBackground(color)
                    # Set text color to black or white based on background brightness
                    if color.lightness() > 128:
                        highlight_format.setForeground(QColor(0, 0, 0))
                    else:
                        highlight_format.setForeground(QColor(255, 255, 255))
                else:
                    # Use default format if no color specified
                    highlight_format = self.default_highlight_format
                self.highlight_terms.append({
                    'term': term['term'].lower(),
                    'format': highlight_format
                })
            else:
                # Backward compatibility for simple string terms
                self.highlight_terms.append({
                    'term': term.lower(),
                    'format': self.default_highlight_format
                })
        self.rehighlight()

    def highlightBlock(self, text):
        for term_info in self.highlight_terms:
            if term_info['term'] in text.lower():
                self.setFormat(0, len(text), term_info['format'])

class ConfigDialog(QDialog):
    def __init__(self, parent=None, highlight_terms=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Highlighting")
        self.resize(400, 300)
        self.highlight_terms = highlight_terms or []
        
        # Set dark mode
        palette = self.parent().palette()
        self.setPalette(palette)
        
        layout = QVBoxLayout(self)
        
        # Terms list
        self.terms_list = QListWidget()
        self.terms_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3f3f3f;
            }
        """)
        self.update_terms_list()
        layout.addWidget(QLabel("Highlight Terms:"))
        layout.addWidget(self.terms_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Term")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
        """)
        add_btn.clicked.connect(self.add_term)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit Term")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
        """)
        edit_btn.clicked.connect(self.edit_term)
        btn_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("Remove Term")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
        """)
        remove_btn.clicked.connect(self.remove_term)
        btn_layout.addWidget(remove_btn)
        
        layout.addLayout(btn_layout)
        
        # Save/Load buttons
        config_btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Config")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
        """)
        save_btn.clicked.connect(self.save_config)
        config_btn_layout.addWidget(save_btn)
        
        layout.addLayout(config_btn_layout)
        
        # Dialog buttons
        # Use constants directly to avoid enum issues
        try:
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        except AttributeError:
            try:
                button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                            QDialogButtonBox.StandardButton.Cancel)
            except AttributeError:
                # Fallback to our constants
                button_box = QDialogButtonBox(QtConstants.Ok | QtConstants.Cancel)
                
        button_box.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
        """)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def update_terms_list(self):
        self.terms_list.clear()
        for term in self.highlight_terms:
            if isinstance(term, dict):
                display_text = term['term']
                if 'color' in term:
                    display_text += f" (Color: {term['color']})"
                self.terms_list.addItem(display_text)
            else:
                self.terms_list.addItem(term)
    
    def add_term(self):
        term, ok = QInputDialog.getText(self, "Add Term", "Enter term to highlight:")
        if ok and term:
            color_dialog = QColorDialog(self)
            color_dialog.setStyleSheet("""
                QColorDialog {
                    background-color: #3f3f3f;
                    color: white;
                }
            """)
            
            # Use try/except to handle different PyQt versions for dialog execution
            try:
                result = color_dialog.exec()
            except AttributeError:
                # For PyQt6 < 6.0
                try:
                    result = color_dialog.exec_()
                except AttributeError:
                    result = QtConstants.Rejected
                    print("Warning: Could not execute color dialog.")
            
            if result == QtConstants.Accepted:
                color = color_dialog.selectedColor()
                color_hex = color.name()
                self.highlight_terms.append({
                    'term': term,
                    'color': color_hex
                })
            else:
                self.highlight_terms.append(term)
            self.update_terms_list()
    
    def edit_term(self):
        current_row = self.terms_list.currentRow()
        if current_row >= 0:
            current_term = self.highlight_terms[current_row]
            
            if isinstance(current_term, dict):
                term = current_term['term']
                current_color = current_term.get('color', None)
            else:
                term = current_term
                current_color = None
                
            new_term, ok = QInputDialog.getText(self, "Edit Term", 
                                              "Edit term to highlight:", 
                                              text=term)
            if ok and new_term:
                color_dialog = QColorDialog(self)
                if current_color:
                    color_dialog.setCurrentColor(QColor(current_color))
                
                # Use try/except to handle different PyQt versions for dialog execution
                try:
                    result = color_dialog.exec()
                except AttributeError:
                    # For PyQt6 < 6.0
                    try:
                        result = color_dialog.exec_()
                    except AttributeError:
                        result = QtConstants.Rejected
                        print("Warning: Could not execute color dialog.")
                
                if result == QtConstants.Accepted:
                    color = color_dialog.selectedColor()
                    color_hex = color.name()
                    self.highlight_terms[current_row] = {
                        'term': new_term,
                        'color': color_hex
                    }
                else:
                    self.highlight_terms[current_row] = new_term
                    
                self.update_terms_list()
    
    def remove_term(self):
        current_row = self.terms_list.currentRow()
        if current_row >= 0:
            del self.highlight_terms[current_row]
            self.update_terms_list()
    
    def save_config(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration", "", "YAML Files (*.yml);;All Files (*)"
        )
        if file_name:
            try:
                config = {'highlight_terms': self.highlight_terms}
                with open(file_name, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                QMessageBox.information(self, "Success", f"Configuration saved to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")

# WorkerSignals class to enable signal communication from QRunnable worker
class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    chunk_ready = pyqtSignal(str, int, int)  # text, chunk_number, total_chunks

# FileLoaderWorker class to handle file loading in a separate thread
class FileLoaderWorker(QRunnable):
    def __init__(self, file_path, chunk_size=256*1024):  # Reduced chunk size to 256KB
        super().__init__()
        self.file_path = file_path
        self.signals = WorkerSignals()
        self.chunk_size = chunk_size
        
    @pyqtSlot()
    def run(self):
        try:
            # Get file size for progress calculation
            file_size = os.path.getsize(self.file_path)
            
            # Count total chunks for progress reporting
            total_chunks = (file_size // self.chunk_size) + (1 if file_size % self.chunk_size else 0)
            
            with open(self.file_path, 'r', errors='replace') as f:
                bytes_read = 0
                chunk_number = 0
                
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                        
                    chunk_number += 1
                    bytes_read += len(chunk.encode('utf-8'))
                    progress = int((bytes_read / file_size) * 100)
                    
                    # Emit the chunk for immediate display
                    self.signals.chunk_ready.emit(chunk, chunk_number, total_chunks)
                    
                    # Emit progress update
                    self.signals.progress.emit(progress)
                    
                    # Small sleep to allow UI updates
                    time.sleep(0.01)
            
            # Signal completion
            self.signals.finished.emit()
            
        except Exception as e:
            self.signals.error.emit(str(e))

# Optimized text editor that efficiently handles large files
class OptimizedTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        
        # Use try/except to handle different PyQt versions
        try:
            # Try with enum if available
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        except (AttributeError, TypeError):
            try:
                # Try with direct enum access
                self.setLineWrapMode(QPlainTextEdit.NoWrap)
            except (AttributeError, TypeError):
                # Fallback to function with no args (some PyQt versions default to NoWrap)
                print("Warning: Could not set line wrap mode, using default.")
        
        # Optimize display settings
        self.document().setMaximumBlockCount(100000)  # Limit maximum blocks for performance
        
    def append_text(self, text):
        """Append text more efficiently"""
        cursor = self.textCursor()
        
        # Use try/except to handle different PyQt versions
        try:
            cursor.movePosition(QtConstants.MoveEnd)  # Use our constant
        except (AttributeError, TypeError):
            try:
                # Try with enum
                cursor.movePosition(QTextCursor.End)
            except (AttributeError, TypeError):
                # Try with MoveOperation enum
                try:
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                except (AttributeError, TypeError):
                    print("Warning: Could not move cursor to end.")
        
        cursor.insertText(text)
        
        # Limit text updates for better performance
        self.setUpdatesEnabled(False)
        self.setTextCursor(cursor)
        self.setUpdatesEnabled(True)

# Compatibility helper functions
def safe_single_shot(ms, callback):
    """A wrapper for QTimer.singleShot that handles different PyQt versions"""
    try:
        QTimer.singleShot(ms, callback)
    except (AttributeError, TypeError):
        # Fallback: create a timer manually
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(callback)
        timer.start(ms)

class LogViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Viewer - Supports .log, .out, .txt files")
        self.setGeometry(100, 100, 1000, 700)  # Larger default window
        self.search_results = []
        self.current_search_index = -1
        self.search_highlight_format = QTextCharFormat()
        self.search_highlight_format.setBackground(QColor(255, 255, 0))
        self.search_highlight_format.setForeground(QColor(0, 0, 0))
        
        # Store the current highlighted line positions for clearing
        self.current_highlight_start = None
        self.current_highlight_end = None
        
        self.current_font_size = 12
        self.ansi_parser = AnsiColorParser()
        self.config_path = 'config.yml'
        self.highlight_terms = []
        self.loading_file = False
        self.current_file = None
        self.total_content = ""
        
        # Initialize thread pool for background tasks
        self.threadpool = QThreadPool()
        print(f"Maximum thread count: {self.threadpool.maxThreadCount()}")

        self.set_dark_mode()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create optimized text editor
        self.text_editor = OptimizedTextEdit()
        self.text_editor.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3f3f3f;
                font-size: {self.current_font_size}pt;
                font-family: monospace;
            }}
        """)
        layout.addWidget(self.text_editor)
        
        # Add progress bar for file loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
                background-color: #2b2b2b;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #3f7fbf;
                width: 10px;
            }
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Initialize the highlighter
        self.highlighter = LogHighlighter(self.text_editor.document())

        # Create search bar and buttons layout
        search_layout = QHBoxLayout()
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: white;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        self.search_input.returnPressed.connect(self.find_first)
        search_layout.addWidget(self.search_input)
        
        find_button = QPushButton("Find")
        find_button.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
        """)
        find_button.clicked.connect(self.find_first)
        search_layout.addWidget(find_button)

        find_prev_button = QPushButton("Find Previous")
        find_prev_button.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
        """)
        find_prev_button.clicked.connect(self.find_previous)
        search_layout.addWidget(find_prev_button)

        find_next_button = QPushButton("Find Next")
        find_next_button.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
        """)
        find_next_button.clicked.connect(self.find_next)
        search_layout.addWidget(find_next_button)
        
        layout.addLayout(search_layout)
        
        # Add font size controls
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Font Size:")
        font_size_label.setStyleSheet("color: white;")
        font_size_layout.addWidget(font_size_label)
        
        decrease_font_button = QPushButton("-")
        decrease_font_button.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
                min-width: 30px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
        """)
        decrease_font_button.clicked.connect(self.decrease_font_size)
        font_size_layout.addWidget(decrease_font_button)
        
        self.font_size_display = QLabel("12")
        self.font_size_display.setStyleSheet("""
            color: white;
            padding: 0 10px;
        """)
        font_size_layout.addWidget(self.font_size_display)
        
        increase_font_button = QPushButton("+")
        increase_font_button.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
                min-width: 30px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
        """)
        increase_font_button.clicked.connect(self.increase_font_size)
        font_size_layout.addWidget(increase_font_button)
        
        # Add configuration button
        config_button = QPushButton("Configure Highlighting")
        config_button.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
        """)
        config_button.clicked.connect(self.configure_highlighting)
        font_size_layout.addWidget(config_button)
        
        layout.addLayout(font_size_layout)
        
        # File actions layout
        file_layout = QHBoxLayout()
        
        open_button = QPushButton("Open Log File")
        open_button.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
        """)
        open_button.clicked.connect(self.open_file)
        file_layout.addWidget(open_button)
        
        load_config_button = QPushButton("Load Config")
        load_config_button.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
            QPushButton:pressed {
                background-color: #2f2f2f;
            }
        """)
        load_config_button.clicked.connect(self.load_custom_config)
        file_layout.addWidget(load_config_button)
        
        layout.addLayout(file_layout)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: white;")
        layout.addWidget(self.status_label)

        self.load_config()
        
        # Set up debounce timer for search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

    def set_dark_mode(self):
        # Set dark mode palette for the main window
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(43, 43, 43))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(63, 63, 63))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)

    def find_first(self):
        """Initiate a new search from the beginning of the document"""
        search_term = self.search_input.text()
        if not search_term:
            return
            
        # Start the debounced search
        self.search_timer.start(100)  # 100ms debounce
    
    def perform_search(self):
        """Perform the actual search after debounce delay"""
        search_term = self.search_input.text()
        if not search_term:
            return
            
        # Remove any existing highlights
        self.clear_search_highlights()
        
        # Reset search index and clear stored positions
        self.current_search_index = -1
        self.current_highlight_start = None
        self.current_highlight_end = None
        
        # Move to beginning of document
        cursor = self.text_editor.textCursor()
        
        # Use try/except to handle different PyQt versions
        try:
            cursor.movePosition(QtConstants.MoveStart)  # Use our constant
        except (AttributeError, TypeError):
            try:
                cursor.movePosition(QTextCursor.Start)
            except (AttributeError, TypeError):
                try:
                    cursor.movePosition(QTextCursor.MoveOperation.Start)
                except (AttributeError, TypeError):
                    print("Warning: Could not move cursor to start.")
                    
        self.text_editor.setTextCursor(cursor)
        
        # Find the first occurrence
        self.find_next()

    def find_next(self):
        """Find the next occurrence of the search term"""
        search_term = self.search_input.text()
        if not search_term:
            return
            
        if self.current_search_index == -1:
            # First search or new search term
            self.search_results = []
            start_cursor = self.text_editor.textCursor()
            
            # Use try/except to handle different PyQt versions
            try:
                start_cursor.movePosition(QtConstants.MoveStart)  # Use our constant
            except (AttributeError, TypeError):
                try:
                    start_cursor.movePosition(QTextCursor.Start)
                except (AttributeError, TypeError):
                    try:
                        start_cursor.movePosition(QTextCursor.MoveOperation.Start)
                    except (AttributeError, TypeError):
                        print("Warning: Could not move cursor to start.")
                        
            self.text_editor.setTextCursor(start_cursor)
            self.find_all_occurrences(search_term)
            
            if not self.search_results:
                self.status_label.setText(f"No matches found for '{search_term}'")
                return
                
        # Move to the next result
        if self.search_results:
            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            self.highlight_current_match()
    
    def find_previous(self):
        """Find the previous occurrence of the search term"""
        search_term = self.search_input.text()
        if not search_term:
            return
            
        if self.current_search_index == -1:
            # First search or new search term - start from end
            self.search_results = []
            start_cursor = self.text_editor.textCursor()
            
            # Use try/except to handle different PyQt versions
            try:
                start_cursor.movePosition(QtConstants.MoveStart)  # Use our constant
            except (AttributeError, TypeError):
                try:
                    start_cursor.movePosition(QTextCursor.Start)
                except (AttributeError, TypeError):
                    try:
                        start_cursor.movePosition(QTextCursor.MoveOperation.Start)
                    except (AttributeError, TypeError):
                        print("Warning: Could not move cursor to start.")
                        
            self.text_editor.setTextCursor(start_cursor)
            self.find_all_occurrences(search_term)
            
            if not self.search_results:
                self.status_label.setText(f"No matches found for '{search_term}'")
                return
            
            # Start from the last match
            self.current_search_index = len(self.search_results)
                
        # Move to the previous result
        if self.search_results:
            self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
            self.highlight_current_match()
    
    def highlight_current_match(self):
        """Highlight the current match line"""
        if not self.search_results:
            return
            
        # Clear previous highlight
        self.clear_current_highlight()
        
        search_term = self.search_input.text()
        position = self.search_results[self.current_search_index]
        
        # Navigate to the position and highlight the entire line
        cursor = self.text_editor.textCursor()
        cursor.setPosition(position)
        
        # Select the entire line
        try:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        except (AttributeError, TypeError):
            try:
                cursor.movePosition(QTextCursor.StartOfLine)
            except (AttributeError, TypeError):
                try:
                    cursor.movePosition(QtConstants.StartOfLine)
                except (AttributeError, TypeError):
                    print("Warning: Could not move to start of line.")
        
        # Select to end of line with compatibility handling
        try:
            cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        except (AttributeError, TypeError):
            try:
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            except (AttributeError, TypeError):
                try:
                    cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QtConstants.KeepAnchor)
                except (AttributeError, TypeError):
                    try:
                        cursor.movePosition(QtConstants.EndOfLine, QtConstants.KeepAnchor)
                    except (AttributeError, TypeError):
                        print("Warning: Could not select to end of line.")
        
        # Store the line positions for clearing later
        self.current_highlight_start = cursor.selectionStart()
        self.current_highlight_end = cursor.selectionEnd()
        
        # Apply yellow highlighting to the entire line
        cursor.setCharFormat(self.search_highlight_format)
        
        # Position cursor at the search term for visibility (but don't change selection)
        cursor.setPosition(position)
        self.text_editor.setTextCursor(cursor)
        self.text_editor.centerCursor()
        
        # Update status
        self.status_label.setText(f"Match {self.current_search_index + 1} of {len(self.search_results)}")
    
    def find_all_occurrences(self, search_term):
        """Find all occurrences of the search term in the document"""
        # Get the full text (more efficient than searching through the document)
        full_text = self.text_editor.toPlainText()
        
        # Find all occurrences
        start = 0
        while True:
            pos = full_text.find(search_term, start)
            if pos == -1:
                break
            self.search_results.append(pos)
            start = pos + len(search_term)
        
        # Update the UI to reflect the number of matches
        if self.search_results:
            self.status_label.setText(f"Found {len(self.search_results)} matches")
    
    def clear_search_highlights(self):
        """Clear all search highlights"""
        self.clear_current_highlight()
        
        # Clear the cursor selection
        cursor = self.text_editor.textCursor()
        cursor.clearSelection()
        self.text_editor.setTextCursor(cursor)
    
    def clear_current_highlight(self):
        """Clear the current line highlight"""
        if self.current_highlight_start is not None and self.current_highlight_end is not None:
            # Create a new cursor to clear the formatting
            cursor = self.text_editor.textCursor()
            cursor.setPosition(self.current_highlight_start)
            
            # Select the same range
            try:
                cursor.setPosition(self.current_highlight_end, QTextCursor.MoveMode.KeepAnchor)
            except (AttributeError, TypeError):
                try:
                    cursor.setPosition(self.current_highlight_end, QTextCursor.KeepAnchor)
                except (AttributeError, TypeError):
                    cursor.setPosition(self.current_highlight_end, QtConstants.KeepAnchor)
            
            # Clear the formatting by setting to default
            default_format = QTextCharFormat()
            default_format.setForeground(QColor(255, 255, 255))  # White text
            cursor.setCharFormat(default_format)
            
            # Clear the stored positions
            self.current_highlight_start = None
            self.current_highlight_end = None

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if 'highlight_terms' in config:
                        self.highlight_terms = config['highlight_terms']
                        self.highlighter.set_highlight_terms(self.highlight_terms)
                        self.status_label.setText(f"Config loaded from {self.config_path}")
            else:
                # Load default config if no custom config exists
                default_config_path = 'config.yml'
                if os.path.exists(default_config_path) and self.config_path != default_config_path:
                    with open(default_config_path, 'r') as f:
                        config = yaml.safe_load(f)
                        if 'highlight_terms' in config:
                            self.highlight_terms = config['highlight_terms']
                            self.highlighter.set_highlight_terms(self.highlight_terms)
                            self.status_label.setText("Default config loaded")
        except Exception as e:
            self.status_label.setText(f"Error loading config: {e}")
            print(f"Error loading config: {e}")

    def load_custom_config(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", "", "YAML Files (*.yml);;All Files (*)"
        )
        if file_name:
            try:
                self.config_path = file_name
                self.load_config()
                self.status_label.setText(f"Config loaded from {file_name}")
            except Exception as e:
                self.status_label.setText(f"Error loading config: {e}")
                QMessageBox.critical(self, "Error", f"Failed to load configuration: {str(e)}")

    def configure_highlighting(self):
        dialog = ConfigDialog(self, self.highlight_terms)
        
        # Use try/except to handle different PyQt versions for dialog execution
        try:
            result = dialog.exec()
        except AttributeError:
            # For PyQt6 < 6.0
            try:
                result = dialog.exec_()
            except AttributeError:
                result = QtConstants.Rejected
                print("Warning: Could not execute dialog.")
        
        # Compare with our constant for consistency
        if result == QtConstants.Accepted:
            self.highlight_terms = dialog.highlight_terms
            self.highlighter.set_highlight_terms(self.highlight_terms)
            self.status_label.setText("Highlight configuration updated")

    def increase_font_size(self):
        """Increase the font size of the text editor"""
        if self.current_font_size < 72:  # Maximum font size
            self.current_font_size += 1
            self.update_font_size()
    
    def decrease_font_size(self):
        """Decrease the font size of the text editor"""
        if self.current_font_size > 6:  # Minimum font size
            self.current_font_size -= 1
            self.update_font_size()
    
    def update_font_size(self):
        """Update the font size in the text editor"""
        # Update the display
        self.font_size_display.setText(str(self.current_font_size))
        
        # Update the text editor style
        self.text_editor.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3f3f3f;
                font-size: {self.current_font_size}pt;
                font-family: monospace;
            }}
        """)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Log File", 
            "", 
            "Log Files (*.log *.out *.txt);;Log Files (*.log);;Output Files (*.out);;Text Files (*.txt);;All Files (*)"
        )
        if file_name:
            self.load_file_async(file_name)
    
    def load_file_async(self, file_path):
        """Load a file asynchronously to prevent UI freezing"""
        if self.loading_file:
            QMessageBox.warning(self, "Loading in Progress", "Already loading a file. Please wait for the current operation to complete.")
            return
            
        self.loading_file = True
        self.current_file = file_path
        self.total_content = ""
        
        # Clear previous content
        self.text_editor.clear()
        self.status_label.setText(f"Loading file: {file_path}...")
        
        # Show progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Create worker with smaller chunk size
        worker = FileLoaderWorker(file_path)
        
        # Connect signals
        worker.signals.chunk_ready.connect(self.on_chunk_ready)
        worker.signals.error.connect(self.on_file_error)
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.on_loading_finished)
        
        # Execute worker
        self.threadpool.start(worker)
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def on_chunk_ready(self, chunk, chunk_number, total_chunks):
        """Handle a chunk of text from the file loader"""
        # Append to the total content
        self.total_content += chunk
        
        # Only update the display with this chunk, not the entire content
        self.text_editor.append_text(chunk)
        
        # Update status
        self.status_label.setText(f"Loading chunk {chunk_number}/{total_chunks}...")
    
    def on_loading_finished(self):
        """Handle completion of file loading"""
        self.loading_file = False
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"File loaded: {self.current_file}")
        
        # Apply highlighting after file is completely loaded
        safe_single_shot(100, self.load_config)
        
        # Move cursor to start for better performance
        cursor = self.text_editor.textCursor()
        
        # Use try/except to handle different PyQt versions
        try:
            cursor.movePosition(QtConstants.MoveStart)  # Use our constant
        except (AttributeError, TypeError):
            try:
                cursor.movePosition(QTextCursor.Start)
            except (AttributeError, TypeError):
                try:
                    cursor.movePosition(QTextCursor.MoveOperation.Start)
                except (AttributeError, TypeError):
                    print("Warning: Could not move cursor to start.")
                    
        self.text_editor.setTextCursor(cursor)
    
    def on_file_error(self, error_msg):
        """Handle file loading errors"""
        self.loading_file = False
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error opening file: {error_msg}")
        QMessageBox.critical(self, "Error", f"Failed to open file: {error_msg}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Log Viewer')
    parser.add_argument('--config', help='Path to custom config.yml file')
    parser.add_argument('file', nargs='?', help='Log file to open (.log, .out, .txt, or any text file)')
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    
    # Apply performance optimization settings
    app.setStyle('Fusion')  # Use Fusion style for better performance
    
    viewer = LogViewer()
    
    # Set custom config if provided
    if args.config:
        viewer.config_path = args.config
        viewer.load_config()
    
    # Show the viewer before loading file for responsiveness
    viewer.show()
    
    # Open file if provided
    if args.file and os.path.exists(args.file):
        # Use a short delay to ensure the UI is fully displayed first
        safe_single_shot(100, lambda: viewer.load_file_async(args.file))
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()