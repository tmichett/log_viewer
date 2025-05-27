import sys
import yaml
import re
import os
import argparse
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, 
                           QVBoxLayout, QWidget, QPushButton, QFileDialog,
                           QHBoxLayout, QLineEdit, QLabel, QListWidget, 
                           QColorDialog, QDialog, QFormLayout,
                           QDialogButtonBox, QMessageBox, QInputDialog)
from PyQt6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter, QPalette
from PyQt6.QtCore import Qt

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
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                      QDialogButtonBox.StandardButton.Cancel)
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
            if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
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
                
                if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
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

class LogViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Viewer - Supports .log, .out, .txt files")
        self.setGeometry(100, 100, 800, 600)
        self.search_results = []
        self.current_search_index = -1
        self.search_highlight_format = QTextCharFormat()
        self.search_highlight_format.setBackground(QColor(255, 255, 0))
        self.search_highlight_format.setForeground(QColor(0, 0, 0))
        
        self.current_font_size = 12
        self.ansi_parser = AnsiColorParser()
        self.config_path = 'config.yml'
        self.highlight_terms = []

        self.set_dark_mode()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create text editor
        self.text_editor = QTextEdit()
        self.text_editor.setReadOnly(True)
        self.text_editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3f3f3f;
                font-size: {self.current_font_size}pt;
                font-family: monospace;
            }}
        """)
        layout.addWidget(self.text_editor)

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
        if dialog.exec() == QDialog.DialogCode.Accepted:
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
            "Log Files (*.log *.out *.txt);;Log Files (*.log);;Output Files (*.out);;Text Files (*.txt);;All Files (*)"
        )
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    content = f.read()
                    self.text_editor.clear()
                    self.text_editor.setPlainText(content)
                    # Reload config after opening new file to ensure highlighting is applied
                    self.load_config()
            except Exception as e:
                print(f"Error opening file: {e}")
                self.status_label.setText(f"Error opening file: {e}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Log Viewer')
    parser.add_argument('--config', help='Path to custom config.yml file')
    parser.add_argument('file', nargs='?', help='Log file to open (.log, .out, .txt, or any text file)')
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    viewer = LogViewer()
    
    # Set custom config if provided
    if args.config:
        viewer.config_path = args.config
        viewer.load_config()
    
    # Open file if provided
    if args.file and os.path.exists(args.file):
        try:
            with open(args.file, 'r') as f:
                content = f.read()
                viewer.text_editor.setPlainText(content)
                viewer.status_label.setText(f"Opened file: {args.file}")
        except Exception as e:
            print(f"Error opening file: {e}")
            viewer.status_label.setText(f"Error opening file: {e}")
    
    viewer.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()