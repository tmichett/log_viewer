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
        # Brighter blue color for highlighting
        self.highlight_format.setBackground(QColor(100, 149, 237))  # Cornflower blue

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
        self.current_search_index = 0
        self.search_highlight_format = QTextCharFormat()
        self.search_highlight_format.setBackground(QColor(255, 255, 0))  # Yellow
        self.search_highlight_format.setForeground(QColor(0, 0, 0))  # Black text

        # Set dark mode palette
        self.set_dark_mode()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create text editor
        self.text_editor = QTextEdit()
        self.text_editor.setReadOnly(True)
        # Set text editor colors for dark mode
        self.text_editor.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3f3f3f;
            }
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
        self.search_input.returnPressed.connect(self.find_next)
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
        find_button.clicked.connect(self.find_next)
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

    def find_next(self):
        search_term = self.search_input.text()
        if not search_term:
            return

        # Get current cursor position
        cursor = self.text_editor.textCursor()
        
        # Move cursor past the current match if there is one
        if cursor.hasSelection():
            cursor.setPosition(cursor.selectionEnd())
        elif cursor.atEnd():
            cursor.movePosition(cursor.MoveOperation.Start)
        
        self.text_editor.setTextCursor(cursor)
        
        # Find next occurrence
        found = self.text_editor.find(search_term)
        
        if found:
            # Get the current cursor position
            cursor = self.text_editor.textCursor()
            # Move to the start of the line
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            # Select the entire line
            cursor.movePosition(cursor.MoveOperation.EndOfLine, cursor.MoveMode.KeepAnchor)
            # Apply yellow highlight to the entire line
            cursor.mergeCharFormat(self.search_highlight_format)
            # Move cursor back to the found position
            cursor = self.text_editor.textCursor()
            cursor.setPosition(cursor.selectionStart())
            self.text_editor.setTextCursor(cursor)
        else:
            # If not found, start from the beginning
            cursor = self.text_editor.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            self.text_editor.setTextCursor(cursor)
            found = self.text_editor.find(search_term)
            
            if found:
                # Get the current cursor position
                cursor = self.text_editor.textCursor()
                # Move to the start of the line
                cursor.movePosition(cursor.MoveOperation.StartOfLine)
                # Select the entire line
                cursor.movePosition(cursor.MoveOperation.EndOfLine, cursor.MoveMode.KeepAnchor)
                # Apply yellow highlight to the entire line
                cursor.mergeCharFormat(self.search_highlight_format)
                # Move cursor back to the found position
                cursor = self.text_editor.textCursor()
                cursor.setPosition(cursor.selectionStart())
                self.text_editor.setTextCursor(cursor)
            else:
                # If still not found, show message
                self.text_editor.append("\nNo more matches found.")

    def load_config(self):
        try:
            with open('config.yml', 'r') as f:
                config = yaml.safe_load(f)
                if 'highlight_terms' in config:
                    self.highlighter.set_highlight_terms(config['highlight_terms'])
        except Exception as e:
            print(f"Error loading config: {e}")

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
            except Exception as e:
                self.text_editor.setText(f"Error opening file: {e}")

def main():
    app = QApplication(sys.argv)
    viewer = LogViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 