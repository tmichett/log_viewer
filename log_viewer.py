import sys
import yaml
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, 
                           QVBoxLayout, QWidget, QPushButton, QFileDialog,
                           QHBoxLayout, QLineEdit, QLabel)
from PyQt6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter, QPalette
from PyQt6.QtCore import Qt

class LogHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlight_terms = []
        self.highlight_format = QTextCharFormat()
        # Brighter blue color for highlighting with black text
        self.highlight_format.setBackground(QColor(100, 149, 237))  # Cornflower blue
        self.highlight_format.setForeground(QColor(0, 0, 0))  # Black text for better visibility

    def set_highlight_terms(self, terms):
        self.highlight_terms = terms
        self.rehighlight()

    def highlightBlock(self, text):
        for term in self.highlight_terms:
            if term.lower() in text.lower():
                self.setFormat(0, len(text), self.highlight_format)

class LogViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Viewer")
        self.setGeometry(100, 100, 800, 600)
        self.search_results = []
        self.current_search_index = -1  # No search performed yet
        self.search_highlight_format = QTextCharFormat()
        self.search_highlight_format.setBackground(QColor(255, 255, 0))  # Yellow
        self.search_highlight_format.setForeground(QColor(0, 0, 0))  # Black text
        
        # Initial font size
        self.current_font_size = 12

        # Set dark mode palette
        self.set_dark_mode()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create text editor
        self.text_editor = QTextEdit()
        self.text_editor.setReadOnly(True)
        # Set text editor colors for dark mode and initial font size
        self.text_editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3f3f3f;
                font-size: {self.current_font_size}pt;
            }}
        """)
        layout.addWidget(self.text_editor)

        # Create highlighter
        self.highlighter = LogHighlighter(self.text_editor.document())

        # Create search bar and buttons layout
        search_layout = QHBoxLayout()
        
        # Search label
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: white;")
        search_layout.addWidget(search_label)
        
        # Search input
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
        
        # Find button
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

        # Find Next button
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
        
        # Font size controls
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Font Size:")
        font_size_label.setStyleSheet("color: white;")
        font_size_layout.addWidget(font_size_label)
        
        # Decrease font size button
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
        
        # Current font size display
        self.font_size_display = QLabel("12")
        self.font_size_display.setStyleSheet("""
            color: white;
            padding: 0 10px;
        """)
        font_size_layout.addWidget(self.font_size_display)
        
        # Increase font size button
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
        
        # Add font size controls to search layout
        search_layout.addLayout(font_size_layout)
        
        # Add search layout to main layout
        layout.addLayout(search_layout)

        # Create open file button with dark mode styling
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
        layout.addWidget(open_button)

        # Status bar for search info
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: white;")
        layout.addWidget(self.status_label)

        # Load highlight terms from config
        self.load_config()

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
            
        # Remove any existing highlights
        self.clear_search_highlights()
        
        # Reset search index
        self.current_search_index = -1
        
        # Move to beginning of document
        cursor = self.text_editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
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
            start_cursor.movePosition(start_cursor.MoveOperation.Start)
            self.text_editor.setTextCursor(start_cursor)
            self.find_all_occurrences(search_term)
            
            if not self.search_results:
                self.status_label.setText(f"No matches found for '{search_term}'")
                return
                
        # Move to the next result
        if self.search_results:
            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            position = self.search_results[self.current_search_index]
            
            # Navigate to the position
            cursor = self.text_editor.textCursor()
            cursor.setPosition(position)
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            line_start_pos = cursor.position()
            cursor.movePosition(cursor.MoveOperation.EndOfLine)
            line_end_pos = cursor.position()
            
            # Select and highlight the entire line
            cursor.setPosition(line_start_pos)
            cursor.setPosition(line_end_pos, cursor.MoveMode.KeepAnchor)
            self.text_editor.setTextCursor(cursor)
            
            # Apply highlight to the line
            format = self.search_highlight_format
            cursor.mergeCharFormat(format)
            
            # Position cursor at the beginning of the found term
            cursor.setPosition(position)
            self.text_editor.setTextCursor(cursor)
            
            # Ensure the found term is visible
            self.text_editor.ensureCursorVisible()
            
            # Update status
            self.status_label.setText(f"Match {self.current_search_index + 1} of {len(self.search_results)}")

    def find_all_occurrences(self, search_term):
        """Find all occurrences of the search term in the document"""
        # Start from the beginning
        cursor = self.text_editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self.text_editor.setTextCursor(cursor)
        
        # Find all occurrences
        while self.text_editor.find(search_term):
            # Get the position of the found term
            cursor = self.text_editor.textCursor()
            self.search_results.append(cursor.selectionStart())
        
        # Reset cursor to the beginning
        cursor.movePosition(cursor.MoveOperation.Start)
        self.text_editor.setTextCursor(cursor)

    def clear_search_highlights(self):
        """Clear all search highlights from the document"""
        # Reset the document formatting
        cursor = self.text_editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        
        # Create a default format (no highlighting)
        default_format = QTextCharFormat()
        cursor.setCharFormat(default_format)
        
        # Reset the cursor
        cursor.clearSelection()
        self.text_editor.setTextCursor(cursor)

    def load_config(self):
        try:
            with open('config.yml', 'r') as f:
                config = yaml.safe_load(f)
                if 'highlight_terms' in config:
                    self.highlighter.set_highlight_terms(config['highlight_terms'])
        except Exception as e:
            print(f"Error loading config: {e}")

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
            QTextEdit {{
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3f3f3f;
                font-size: {self.current_font_size}pt;
            }}
        """)
    
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Log File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    self.text_editor.setText(f.read())
                # Reset search when loading a new file
                self.current_search_index = -1
                self.search_results = []
                self.status_label.setText(f"Loaded {file_name}")
            except Exception as e:
                self.text_editor.setText(f"Error opening file: {e}")
                self.status_label.setText(f"Error opening file")

def main():
    app = QApplication(sys.argv)
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()