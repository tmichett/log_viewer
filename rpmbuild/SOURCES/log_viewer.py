import sys
import yaml
import re
import os
import argparse
import time
import warnings
import platform
from enum import Enum

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def get_application_version():
    """Read version from Build_Version file or return default"""
    try:
        # Try to read from Build_Version file (bundled with app)
        with open('Build_Version', 'r') as f:
            for line in f:
                if line.startswith('VERSION='):
                    return line.split('=')[1].strip()
    except FileNotFoundError:
        try:
            # Fallback: try to read from script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            version_file = os.path.join(script_dir, 'Build_Version')
            with open(version_file, 'r') as f:
                for line in f:
                    if line.startswith('VERSION='):
                        return line.split('=')[1].strip()
        except FileNotFoundError:
            pass
    return "3.0.0"  # Default fallback version

# Get application version
APP_VERSION = get_application_version()

from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, 
                           QVBoxLayout, QWidget, QPushButton, QFileDialog,
                           QHBoxLayout, QLineEdit, QLabel, QListWidget, 
                           QColorDialog, QDialog, QFormLayout,
                           QDialogButtonBox, QMessageBox, QInputDialog,
                           QProgressBar, QScrollBar, QPlainTextEdit, QMenuBar,
                           QMenu, QTextBrowser, QScrollArea)
from PyQt6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter, QPalette, QTextCursor
from PyQt6.QtCore import (Qt, QRunnable, QThreadPool, pyqtSignal, QObject, 
                         pyqtSlot, QTimer, QSize, QStandardPaths)
from PyQt6.QtGui import QShortcut, QKeySequence

# Windows-specific font handling
def get_monospace_font():
    """Get the best monospace font for the current platform"""
    if platform.system() == 'Windows':
        # Windows preferred monospace fonts in order of preference
        fonts = ['Consolas', 'Courier New', 'Lucida Console', 'monospace']
    elif platform.system() == 'Darwin':  # macOS
        fonts = ['Monaco', 'Menlo', 'Courier New', 'monospace']
    else:  # Linux and others
        fonts = ['DejaVu Sans Mono', 'Liberation Mono', 'monospace']
    
    # Return the first font in the list (CSS will fall back to next if not available)
    return ', '.join(fonts)

# Theme system
class ThemeMode(Enum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"

class ThemeColors:
    def __init__(self, 
                 window_bg="#ffffff", 
                 window_text="#000000", 
                 base_bg="#ffffff", 
                 alt_base_bg="#f5f5f5", 
                 text_color="#000000", 
                 button_bg="#e1e1e1", 
                 button_text="#000000", 
                 border_color="#c0c0c0",
                 hover_color="#d0d0d0",
                 pressed_color="#b0b0b0",
                 editor_bg="#ffffff",
                 editor_text="#000000",
                 highlight_bg="#3399ff",
                 highlight_text="#ffffff",
                 menu_bg="#ffffff",
                 menu_text="#000000",
                 menu_hover="#e0e0e0"):
        self.window_bg = window_bg
        self.window_text = window_text
        self.base_bg = base_bg
        self.alt_base_bg = alt_base_bg
        self.text_color = text_color
        self.button_bg = button_bg
        self.button_text = button_text
        self.border_color = border_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.editor_bg = editor_bg
        self.editor_text = editor_text
        self.highlight_bg = highlight_bg
        self.highlight_text = highlight_text
        self.menu_bg = menu_bg
        self.menu_text = menu_text
        self.menu_hover = menu_hover

# Predefined theme configurations
THEME_LIGHT = ThemeColors(
    window_bg="#ffffff",
    window_text="#000000",
    base_bg="#ffffff",
    alt_base_bg="#f5f5f5",
    text_color="#000000",
    button_bg="#e1e1e1",
    button_text="#000000",
    border_color="#c0c0c0",
    hover_color="#d0d0d0",
    pressed_color="#b0b0b0",
    editor_bg="#ffffff",
    editor_text="#000000",
    highlight_bg="#3399ff",
    highlight_text="#ffffff",
    menu_bg="#ffffff",
    menu_text="#000000",
    menu_hover="#e0e0e0"
)

THEME_DARK = ThemeColors(
    window_bg="#2b2b2b",
    window_text="#ffffff",
    base_bg="#2b2b2b",
    alt_base_bg="#3f3f3f",
    text_color="#ffffff",
    button_bg="#3f3f3f",
    button_text="#ffffff",
    border_color="#555555",
    hover_color="#4f4f4f",
    pressed_color="#2f2f2f",
    editor_bg="#2b2b2b",
    editor_text="#ffffff",
    highlight_bg="#42a5f5",
    highlight_text="#ffffff",
    menu_bg="#3f3f3f",
    menu_text="#ffffff",
    menu_hover="#4f4f4f"
)

def detect_system_theme():
    """Detect if the system is using a dark theme"""
    try:
        # Get the default application palette
        app = QApplication.instance()
        if app:
            palette = app.palette()
            # Check the window background color lightness
            window_color = palette.color(QPalette.ColorRole.Window)
            lightness = window_color.lightness()
            # If lightness < 128, it's likely a dark theme
            return lightness < 128
        else:
            # Fallback: create a temporary QApplication to check system palette
            temp_app = QApplication([])
            palette = temp_app.palette()
            window_color = palette.color(QPalette.ColorRole.Window)
            lightness = window_color.lightness()
            temp_app.quit()
            return lightness < 128
    except Exception as e:
        print(f"Error detecting system theme: {e}")
        # Default to light theme if detection fails
        return False

def get_theme_colors(theme_mode):
    """Get theme colors based on the selected mode"""
    if theme_mode == ThemeMode.SYSTEM:
        return THEME_DARK if detect_system_theme() else THEME_LIGHT
    elif theme_mode == ThemeMode.DARK:
        return THEME_DARK
    else:  # LIGHT
        return THEME_LIGHT

# Cross-platform configuration path handling
def get_config_path():
    """Get the appropriate configuration file path for the current platform"""
    if platform.system() == 'Windows':
        # Use Windows AppData directory for configuration
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        config_dir = os.path.join(app_data, 'LogViewer')
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except OSError:
                pass
        return os.path.join(config_dir, 'config.yml')
    elif platform.system() == 'Darwin':  # macOS
        # Use macOS Application Support directory
        app_support = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
        config_dir = os.path.join(app_support, 'LogViewer')
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except OSError:
                pass
        return os.path.join(config_dir, 'config.yml')
    else:
        # Use current directory for other platforms (Linux, etc.)
        return 'config.yml'

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
        # Track search-highlighted areas to avoid overriding them
        self.search_highlighted_start = None
        self.search_highlighted_end = None

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

    def set_search_highlight_range(self, start_pos, end_pos):
        """Set the range that is currently search-highlighted to avoid overriding it"""
        self.search_highlighted_start = start_pos
        self.search_highlighted_end = end_pos

    def clear_search_highlight_range(self):
        """Clear the search-highlighted range"""
        self.search_highlighted_start = None
        self.search_highlighted_end = None

    def highlightBlock(self, text):
        # Get the current block's position in the document
        block = self.currentBlock()
        block_start = block.position()
        block_end = block_start + block.length()
        
        # Check if this block overlaps with search-highlighted area
        if (self.search_highlighted_start is not None and 
            self.search_highlighted_end is not None):
            # If this block overlaps with search highlighting, don't apply config highlighting
            if (block_start < self.search_highlighted_end and 
                block_end > self.search_highlighted_start):
                return
        
        # Apply config-based highlighting only if not in search-highlighted area
        for term_info in self.highlight_terms:
            if term_info['term'] in text.lower():
                self.setFormat(0, len(text), term_info['format'])

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Viewer Help")
        self.resize(800, 600)
        
        # Use parent's theme
        if parent and hasattr(parent, 'current_theme_colors'):
            self.theme_colors = parent.current_theme_colors
        else:
            self.theme_colors = get_theme_colors(ThemeMode.SYSTEM)
        
        # Set palette from theme
        palette = self.parent().palette() if parent else QPalette()
        self.setPalette(palette)
        
        layout = QVBoxLayout(self)
        
        # Create a text browser for the help content
        self.help_browser = QTextBrowser()
        self.help_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {self.theme_colors.editor_bg};
                color: {self.theme_colors.editor_text};
                border: 1px solid {self.theme_colors.border_color};
                font-family: {get_monospace_font()};
                font-size: 12pt;
            }}
        """)
        
        # Load help content
        self.load_help_content()
        
        layout.addWidget(self.help_browser)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_colors.button_bg};
                color: {self.theme_colors.button_text};
                border: 1px solid {self.theme_colors.border_color};
                padding: 8px;
                border-radius: 3px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors.hover_color};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
    
    def load_help_content(self):
        """Load help content from file or provide built-in content"""
        # Determine header colors based on theme
        if self.theme_colors.editor_bg == "#2b2b2b":  # Dark theme
            h1_color = "#4a9eff"
            h2_color = "#6ab7ff"
            h3_color = "#8ac5ff"
        else:  # Light theme
            h1_color = "#1976d2"
            h2_color = "#1e88e5"
            h3_color = "#42a5f5"
        
        help_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: monospace; color: {self.theme_colors.editor_text}; background-color: {self.theme_colors.editor_bg}; }}
                h1 {{ color: {h1_color}; }}
                h2 {{ color: {h2_color}; }}
                h3 {{ color: {h3_color}; }}
                code {{ background-color: {self.theme_colors.alt_base_bg}; color: {self.theme_colors.text_color}; padding: 2px 4px; border-radius: 2px; }}
                pre {{ background-color: {self.theme_colors.alt_base_bg}; color: {self.theme_colors.text_color}; padding: 10px; border-radius: 5px; }}
                ul {{ margin-left: 20px; }}
                li {{ margin-bottom: 5px; }}
            </style>
        </head>
        <body>
            <h1>Log Viewer Help</h1>
            
            <h2>Getting Started</h2>
            <h3>Opening Files</h3>
            <ul>
                <li><strong>Open File Button:</strong> Click "Open Log File" to browse and select a file</li>
                <li><strong>Command Line:</strong> Run <code>log_viewer.py /path/to/file.log</code> to open a specific file</li>
                <li><strong>Windows:</strong> Run <code>python log_viewer.py C:\\path\\to\\file.log</code></li>
                <li><strong>Supported Formats:</strong> .log, .out, .txt, and other text files</li>
            </ul>
            
            <h3>Basic Navigation</h3>
            <ul>
                <li><strong>Scroll:</strong> Use mouse wheel or scrollbar to navigate through the file</li>
                <li><strong>Home/End:</strong> Jump to beginning or end of file</li>
                <li><strong>Page Up/Down:</strong> Navigate by pages</li>
            </ul>
            
            <h2>Search Functionality</h2>
            <h3>Basic Search</h3>
            <ol>
                <li>Type your search term in the search box</li>
                <li>Press Enter or click "Find" to start searching</li>
                <li>Use "Find Next" and "Find Previous" to navigate through results</li>
                <li>The entire line containing your search term will be highlighted in yellow</li>
            </ol>
            
            <h3>Search Tips</h3>
            <ul>
                <li>Search is case-insensitive</li>
                <li>Use specific terms to reduce result sets</li>
                <li>The status bar shows current match position and total matches</li>
                <li>Search results are cached for fast navigation</li>
            </ul>
            
            <h2>Text Highlighting</h2>
            <h3>Configurable Highlighting</h3>
            <ol>
                <li>Click "Configure Highlighting" button</li>
                <li>Add terms you want to highlight in log files</li>
                <li>Choose custom colors for each term</li>
                <li>Save configurations for reuse</li>
            </ol>
            
            <h3>Managing Highlight Terms</h3>
            <ul>
                <li><strong>Add:</strong> Click "Add Term" and enter the text to highlight</li>
                <li><strong>Edit:</strong> Select a term and click "Edit Term" to modify it</li>
                <li><strong>Remove:</strong> Select a term and click "Remove Term" to delete it</li>
                <li><strong>Colors:</strong> Use the color picker to choose highlight colors</li>
            </ul>
            
            <h2>Keyboard Shortcuts</h2>
            <h3>File Operations</h3>
            <ul>
                <li><strong>Ctrl+O:</strong> Open file</li>
                <li><strong>Ctrl+Q:</strong> Quit application</li>
            </ul>
            
            <h3>Search Operations</h3>
            <ul>
                <li><strong>Ctrl+F:</strong> Focus search box</li>
                <li><strong>Enter:</strong> Find first/next</li>
                <li><strong>F3:</strong> Find next</li>
                <li><strong>Shift+F3:</strong> Find previous</li>
                <li><strong>Escape:</strong> Clear search</li>
            </ul>
            
            <h2>Performance</h2>
            <h3>Large Files</h3>
            <ul>
                <li>Files are loaded in chunks to prevent UI freezing</li>
                <li>Progress bar shows loading status</li>
                <li>Memory usage is optimized for large files</li>
            </ul>
            
            <h2>Platform-Specific Notes</h2>
            <h3>Windows</h3>
            <ul>
                <li>Configuration files are stored in <code>%APPDATA%\\LogViewer\\</code></li>
                <li>Use Windows-style paths (e.g., <code>C:\\path\\to\\file.log</code>)</li>
                <li>The application supports high DPI displays</li>
            </ul>
            
            <h3>macOS</h3>
            <ul>
                <li>Configuration files are stored in <code>~/Library/Application Support/LogViewer/</code></li>
                <li>Use Unix-style paths (e.g., <code>/path/to/file.log</code>)</li>
                <li>The application supports Retina displays</li>
                <li>Use Cmd+O to open files and Cmd+Q to quit</li>
            </ul>
            
            <h3>Linux</h3>
            <ul>
                <li>Configuration files are stored in the current directory</li>
                <li>Use Unix-style paths (e.g., <code>/path/to/file.log</code>)</li>
                <li>The application supports high DPI displays</li>
            </ul>
            
            <h2>Support</h2>
            <p>For additional help or to report issues:</p>
            <ul>
                <li><strong>Email:</strong> travis@michettetech.com</li>
                <li><strong>Organization:</strong> Michette Technologies</li>
            </ul>
        </body>
        </html>
        """
        self.help_browser.setHtml(help_content)

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Log Viewer")
        self.resize(350, 200)
        
        # Use parent's theme
        if parent and hasattr(parent, 'current_theme_colors'):
            self.theme_colors = parent.current_theme_colors
        else:
            self.theme_colors = get_theme_colors(ThemeMode.SYSTEM)
        
        # Set palette from theme
        palette = self.parent().palette() if parent else QPalette()
        self.setPalette(palette)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Application info
        app_label = QLabel("Log Viewer Application")
        app_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18pt;
                font-weight: bold;
                text-align: center;
            }
        """)
        app_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_label)
        
        company_label = QLabel("Michette Technologies")
        company_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14pt;
                text-align: center;
            }
        """)
        company_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(company_label)
        
        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12pt;
                text-align: center;
            }
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Add some space
        layout.addSpacing(20)
        
        # Additional info
        info_label = QLabel("A powerful log file viewer with ANSI color support\nand configurable highlighting features.")
        info_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 10pt;
                text-align: center;
            }
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Add stretch to push button to bottom
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                border: 1px solid #555555;
                padding: 8px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4f4f4f;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

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
            self, "Save Configuration", 
            os.path.expanduser("~"),  # Start in user's home directory
            "YAML Files (*.yml);;All Files (*)"
        )
        if file_name:
            try:
                config = {'highlight_terms': self.highlight_terms}
                with open(file_name, 'w', encoding='utf-8') as f:
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
            
            # Try different encodings for Windows compatibility
            encodings = ['utf-8', 'utf-16', 'cp1252', 'latin-1']
            file_opened = False
            
            for encoding in encodings:
                try:
                    with open(self.file_path, 'r', encoding=encoding, errors='replace') as f:
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
                        
                        file_opened = True
                        break
                        
                except UnicodeDecodeError:
                    continue
            
            if not file_opened:
                # Fallback to binary mode if all encodings fail
                with open(self.file_path, 'rb') as f:
                    bytes_read = 0
                    chunk_number = 0
                    
                    while True:
                        chunk_bytes = f.read(self.chunk_size)
                        if not chunk_bytes:
                            break
                            
                        # Decode bytes to string, replacing invalid characters
                        chunk = chunk_bytes.decode('utf-8', errors='replace')
                        
                        chunk_number += 1
                        bytes_read += len(chunk_bytes)
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
        self.config_path = get_config_path()  # Use platform-appropriate config path
        self.highlight_terms = []
        self.loading_file = False
        self.current_file = None
        self.total_content = ""
        
        # Theme system
        self.current_theme_mode = ThemeMode.SYSTEM
        self.current_theme_colors = get_theme_colors(self.current_theme_mode)
        
        # Initialize thread pool for background tasks
        self.threadpool = QThreadPool()
        print(f"Maximum thread count: {self.threadpool.maxThreadCount()}")

        # Create menu bar
        self.create_menu_bar()

        # Create keyboard shortcuts
        self.create_shortcuts()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create optimized text editor
        self.text_editor = OptimizedTextEdit()
        # Style will be applied by theme system
        layout.addWidget(self.text_editor)
        
        # Add progress bar for file loading
        self.progress_bar = QProgressBar()
        # Style will be applied by theme system
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
        # Style will be applied by theme system
        self.search_input.returnPressed.connect(self.find_first)
        # Add keyboard shortcut for search
        self.search_input.setToolTip("Press Ctrl+F to focus search box")
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
        # Style will be applied by theme system
        layout.addWidget(self.status_label)

        # Apply initial theme after all UI elements are created
        self.apply_theme()

        self.load_config()
        
        # Set up debounce timer for search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

    def create_menu_bar(self):
        """Create the menu bar with File and Help menus"""
        menubar = self.menuBar()
        # Style will be applied by theme system
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Open action
        open_action = file_menu.addAction("Open...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        # Theme submenu
        theme_menu = view_menu.addMenu("Theme")
        
        # Theme options
        system_theme_action = theme_menu.addAction("System Default")
        system_theme_action.setCheckable(True)
        system_theme_action.triggered.connect(lambda: self.change_theme(ThemeMode.SYSTEM))
        
        light_theme_action = theme_menu.addAction("Light")
        light_theme_action.setCheckable(True)
        light_theme_action.triggered.connect(lambda: self.change_theme(ThemeMode.LIGHT))
        
        dark_theme_action = theme_menu.addAction("Dark")
        dark_theme_action.setCheckable(True)
        dark_theme_action.triggered.connect(lambda: self.change_theme(ThemeMode.DARK))
        
        # Create action group for exclusive selection
        from PyQt6.QtGui import QActionGroup
        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.addAction(system_theme_action)
        self.theme_action_group.addAction(light_theme_action)
        self.theme_action_group.addAction(dark_theme_action)
        
        # Store theme actions for later reference
        self.theme_actions = {
            ThemeMode.SYSTEM: system_theme_action,
            ThemeMode.LIGHT: light_theme_action,
            ThemeMode.DARK: dark_theme_action
        }
        
        # Set initial theme selection
        self.theme_actions[self.current_theme_mode].setChecked(True)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        # Help action
        help_action = help_menu.addAction("Help")
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        
        # About action
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    def show_help(self):
        """Show the help dialog"""
        help_dialog = HelpDialog(self)
        help_dialog.exec()

    def show_about(self):
        """Show the about dialog"""
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def create_shortcuts(self):
        """Create keyboard shortcuts"""
        # Search shortcuts
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.focus_search)
        
        find_next_shortcut = QShortcut(QKeySequence("F3"), self)
        find_next_shortcut.activated.connect(self.find_next)
        
        find_prev_shortcut = QShortcut(QKeySequence("Shift+F3"), self)
        find_prev_shortcut.activated.connect(self.find_previous)
        
        # Clear search shortcut
        clear_search_shortcut = QShortcut(QKeySequence("Escape"), self)
        clear_search_shortcut.activated.connect(self.clear_search)

    def focus_search(self):
        """Focus the search input box"""
        self.search_input.setFocus()
        self.search_input.selectAll()

    def clear_search(self):
        """Clear the search input and highlights"""
        self.search_input.clear()
        self.clear_search_highlights()
        # Clear the search highlight range from LogHighlighter
        self.highlighter.clear_search_highlight_range()
        self.search_results = []
        self.current_search_index = -1
        self.status_label.setText("Search cleared")

    def apply_theme(self):
        """Apply the current theme to all UI elements"""
        # Get current theme colors
        colors = get_theme_colors(self.current_theme_mode)
        self.current_theme_colors = colors
        
        # Set palette for the main window
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(colors.window_bg))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors.window_text))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors.base_bg))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors.alt_base_bg))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors.base_bg))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors.text_color))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors.text_color))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors.button_bg))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors.button_text))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors.highlight_bg))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors.highlight_bg))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors.highlight_text))
        self.setPalette(palette)
        
        # Update all UI elements with themed styles
        self.update_ui_styles()
    
    def update_ui_styles(self):
        """Update all UI element styles with current theme"""
        colors = self.current_theme_colors
        
        # Update text editor style
        self.text_editor.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {colors.editor_bg};
                color: {colors.editor_text};
                border: 1px solid {colors.border_color};
                font-size: {self.current_font_size}pt;
                font-family: {get_monospace_font()};
            }}
        """)
        
        # Update progress bar style
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {colors.border_color};
                border-radius: 3px;
                text-align: center;
                background-color: {colors.base_bg};
                color: {colors.text_color};
            }}
            QProgressBar::chunk {{
                background-color: {colors.highlight_bg};
                width: 10px;
            }}
        """)
        
        # Update search input style
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors.button_bg};
                color: {colors.button_text};
                border: 1px solid {colors.border_color};
                padding: 5px;
                border-radius: 3px;
            }}
        """)
        
        # Update all buttons with themed style
        button_style = f"""
            QPushButton {{
                background-color: {colors.button_bg};
                color: {colors.button_text};
                border: 1px solid {colors.border_color};
                padding: 5px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {colors.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {colors.pressed_color};
            }}
        """
        
        # Apply to all buttons in the main window
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)
        
        # Update status label style
        self.status_label.setStyleSheet(f"color: {colors.text_color};")
        
        # Update font size display style
        self.font_size_display.setStyleSheet(f"""
            color: {colors.text_color};
            padding: 0 10px;
        """)
        
        # Update menu bar style
        self.menuBar().setStyleSheet(f"""
            QMenuBar {{
                background-color: {colors.menu_bg};
                color: {colors.menu_text};
                border: 1px solid {colors.border_color};
            }}
            QMenuBar::item {{
                background-color: {colors.menu_bg};
                color: {colors.menu_text};
                padding: 4px 8px;
            }}
            QMenuBar::item:selected {{
                background-color: {colors.menu_hover};
            }}
            QMenu {{
                background-color: {colors.menu_bg};
                color: {colors.menu_text};
                border: 1px solid {colors.border_color};
            }}
            QMenu::item {{
                background-color: {colors.menu_bg};
                color: {colors.menu_text};
                padding: 4px 20px;
            }}
            QMenu::item:selected {{
                background-color: {colors.menu_hover};
            }}
        """)
        
        # Update all labels
        for label in self.findChildren(QLabel):
            if label != self.font_size_display:  # Skip font size display as it has special styling
                label.setStyleSheet(f"color: {colors.text_color};")
    
    def set_theme_mode(self, theme_mode):
        """Set the theme mode and apply the theme"""
        if isinstance(theme_mode, str):
            try:
                theme_mode = ThemeMode(theme_mode)
            except ValueError:
                theme_mode = ThemeMode.SYSTEM
        
        self.current_theme_mode = theme_mode
        self.apply_theme()
    
    def change_theme(self, theme_mode):
        """Change theme and update UI, called from menu actions"""
        self.set_theme_mode(theme_mode)
        
        # Update menu selection
        for mode, action in self.theme_actions.items():
            action.setChecked(mode == theme_mode)
        
        # Save theme preference to config
        self.save_app_config()
        
        self.status_label.setText(f"Theme changed to {theme_mode.value}")
    
    def save_app_config(self):
        """Save application configuration including theme preference"""
        try:
            # Load existing config or create new one
            config = {}
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f) or {}
                except Exception:
                    config = {}
            
            # Update theme preference
            config['theme'] = self.current_theme_mode.value
            
            # Preserve highlight terms if they exist
            if self.highlight_terms:
                config['highlight_terms'] = self.highlight_terms
            
            # Save config
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
                
        except Exception as e:
            print(f"Error saving config: {e}")
            self.status_label.setText(f"Error saving configuration: {e}")

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
        
        # Clear the search highlight range from LogHighlighter
        self.highlighter.clear_search_highlight_range()
        
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
        
        # Inform the LogHighlighter about the search-highlighted range
        self.highlighter.set_search_highlight_range(self.current_highlight_start, self.current_highlight_end)
        
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
            # Clear the search highlight range from LogHighlighter first
            self.highlighter.clear_search_highlight_range()
            
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
            
            # Trigger rehighlighting to restore config-based highlights
            self.highlighter.rehighlight()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    if 'highlight_terms' in config:
                        self.highlight_terms = config['highlight_terms']
                        self.highlighter.set_highlight_terms(self.highlight_terms)
                    
                    # Load theme preference if present
                    if 'theme' in config:
                        try:
                            self.current_theme_mode = ThemeMode(config['theme'])
                        except (ValueError, KeyError):
                            self.current_theme_mode = ThemeMode.SYSTEM
                    
                    self.status_label.setText(f"Config loaded from {self.config_path}")
            else:
                # Load default config if no custom config exists
                default_config_path = 'config.yml'
                if os.path.exists(default_config_path) and self.config_path != default_config_path:
                    with open(default_config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                        if 'highlight_terms' in config:
                            self.highlight_terms = config['highlight_terms']
                            self.highlighter.set_highlight_terms(self.highlight_terms)
                        
                        # Load theme preference if present in default config
                        if 'theme' in config:
                            try:
                                self.current_theme_mode = ThemeMode(config['theme'])
                            except (ValueError, KeyError):
                                self.current_theme_mode = ThemeMode.SYSTEM
                        
                        self.status_label.setText("Default config loaded")
                        
            # Apply the loaded (or default) theme
            self.apply_theme()
            
            # Update theme menu selection if it exists
            if hasattr(self, 'theme_actions'):
                for mode, action in self.theme_actions.items():
                    action.setChecked(mode == self.current_theme_mode)
                    
        except Exception as e:
            self.status_label.setText(f"Error loading config: {e}")
            print(f"Error loading config: {e}")
            # Apply default theme on error
            self.current_theme_mode = ThemeMode.SYSTEM
            self.apply_theme()

    def load_custom_config(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", 
            os.path.expanduser("~"),  # Start in user's home directory
            "YAML Files (*.yml);;All Files (*)"
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
                font-family: {get_monospace_font()};
            }}
        """)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Log File", 
            os.path.expanduser("~"),  # Start in user's home directory
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
    parser = argparse.ArgumentParser(description='Log Viewer - Cross-Platform Compatible')
    parser.add_argument('--config', help='Path to custom config.yml file')
    parser.add_argument('file', nargs='?', help='Log file to open (.log, .out, .txt, or any text file)')
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    
    # Set application properties for all platforms
    app.setOrganizationName("Michette Technologies")
    app.setApplicationName("Log Viewer")
    app.setApplicationVersion(APP_VERSION)
    
    # Platform-specific application settings
    if platform.system() == 'Windows':
        # Enable high DPI support for Windows (with error handling for different PyQt6 versions)
        try:
            # Try PyQt6 style first
            app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            try:
                # Try alternative PyQt6 attribute names
                app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
                app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            except AttributeError:
                # If high DPI attributes don't exist, continue without them
                print("Note: High DPI scaling attributes not available in this PyQt6 version")
    elif platform.system() == 'Darwin':  # macOS
        # Enable high DPI support for macOS
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            try:
                app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
                app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            except AttributeError:
                print("Note: High DPI scaling attributes not available in this PyQt6 version")
        
        # Set macOS-specific application properties
        app.setApplicationDisplayName("Log Viewer")
    
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