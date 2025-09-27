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
    return "4.0.5"  # Default fallback version

# Get application version
APP_VERSION = get_application_version()

from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, 
                           QVBoxLayout, QWidget, QPushButton, QFileDialog,
                           QHBoxLayout, QLineEdit, QLabel, QListWidget, 
                           QColorDialog, QDialog, QFormLayout,
                           QDialogButtonBox, QMessageBox, QInputDialog,
                           QProgressBar, QScrollBar, QPlainTextEdit, QMenuBar,
                           QMenu, QTextBrowser, QScrollArea, QCheckBox)
from PyQt6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter, QPalette, QTextCursor, QFont
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
        # Platform-specific detection methods
        system_platform = platform.system()
        
        # Try environment variables first (works on many Linux systems)
        if system_platform == 'Linux':
            # Check common environment variables for dark theme
            gtk_theme = os.environ.get('GTK_THEME', '').lower()
            kde_theme = os.environ.get('KDE_SESSION_VERSION', '')
            
            # Check for dark theme indicators in environment
            if 'dark' in gtk_theme or os.environ.get('GTK_APPLICATION_PREFER_DARK_THEME') == '1':
                print(f"Linux: Dark theme detected via GTK environment ({gtk_theme})")
                return True
            
            # Try to read GNOME/GTK settings (priority order)
            try:
                import subprocess
                
                # 1. Check modern GNOME color-scheme setting (GNOME 42+)
                result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    color_scheme = result.stdout.strip().strip("'\"")
                    if 'dark' in color_scheme.lower():
                        return True
                    elif 'light' in color_scheme.lower():
                        return False
                
                # 2. Check legacy GTK theme name
                result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    gtk_theme_name = result.stdout.strip().strip("'\"")
                    if 'dark' in gtk_theme_name.lower():
                        return True
                
                # 3. Check legacy prefer-dark-theme setting
                result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-application-prefer-dark-theme'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    prefer_dark = result.stdout.strip().lower()
                    if prefer_dark == 'true':
                        return True
                        
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                pass
        
        # Get the default application palette as fallback
        app = QApplication.instance()
        if app:
            palette = app.palette()
            # Check multiple colors for better detection
            window_color = palette.color(QPalette.ColorRole.Window)
            base_color = palette.color(QPalette.ColorRole.Base)
            text_color = palette.color(QPalette.ColorRole.WindowText)
            button_color = palette.color(QPalette.ColorRole.Button)
            
            # Calculate lightness for multiple elements
            window_lightness = window_color.lightness()
            base_lightness = base_color.lightness()
            text_lightness = text_color.lightness()
            button_lightness = button_color.lightness()
            
            # For debugging: uncomment the lines below
            # print(f"Qt palette detection - Window: {window_lightness}, Base: {base_lightness}, Text: {text_lightness}, Button: {button_lightness}")
            # print(f"Colors - Window: {window_color.name()}, Base: {base_color.name()}, Text: {text_color.name()}, Button: {button_color.name()}")
            
            # Improved dark theme detection logic:
            # 1. Text should be light in dark themes (lightness > 200)
            # 2. Multiple background elements should be dark (average < 100)
            # 3. High contrast between text and background
            
            avg_bg_lightness = (window_lightness + base_lightness + button_lightness) / 3
            contrast_ratio = abs(text_lightness - avg_bg_lightness)
            
            # More sophisticated detection
            is_dark = (
                text_lightness > 200 and avg_bg_lightness < 100  # High contrast, light text on dark bg
                or (avg_bg_lightness < 50 and contrast_ratio > 180)  # Very dark background with high contrast
                or (text_lightness > 220 and avg_bg_lightness < 120)  # Light text, somewhat dark background
            )
            
            # For debugging: uncomment the lines below
            # print(f"Analysis - Avg BG: {avg_bg_lightness:.1f}, Text: {text_lightness}, Contrast: {contrast_ratio:.1f}")
            # print(f"Qt fallback detected theme: {'DARK' if is_dark else 'LIGHT'}")
            return is_dark
        else:
            # Fallback: create a temporary QApplication to check system palette
            temp_app = QApplication([])
            palette = temp_app.palette()
            window_color = palette.color(QPalette.ColorRole.Window)
            lightness = window_color.lightness()
            temp_app.quit()
            # print(f"Temporary app detection - lightness: {lightness}")
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
    # First, check for user default config in home directory
    user_config_path = os.path.join(os.path.expanduser('~'), 'logviewer_config.yml')
    if os.path.exists(user_config_path):
        return user_config_path
    
    # If user default config doesn't exist, use platform-specific paths
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
        """Simple ANSI parser that strips codes and returns clean text"""
        # For now, just remove ANSI codes to prevent display issues
        # Future enhancement can add color rendering back safely
        import re
        
        # Remove ANSI escape sequences
        ansi_pattern = re.compile(r'(\x1b)?\[([0-9;]*)m')
        clean_text = ansi_pattern.sub('', text)
        
        # Return as a single segment with no special formatting
        return [(clean_text, QTextCharFormat())]

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
        
        # Bookmark highlighting
        self.bookmarked_lines = set()  # Set of bookmarked line numbers (1-based)
        self.bookmark_format = QTextCharFormat()
        # Default light blue background - will be updated by main window
        self.bookmark_format.setBackground(QColor(100, 200, 255))  
        self.bookmark_format.setForeground(QColor(0, 0, 0))

    def set_highlight_terms(self, terms):
        self.highlight_terms = []
        for term in terms:
            if isinstance(term, dict):
                # New format with optional color, text_color, and bold
                highlight_format = QTextCharFormat()
                
                # Set background color
                if 'color' in term:
                    # Convert hex color to QColor
                    color = QColor(term['color'])
                    highlight_format.setBackground(color)
                else:
                    # Use default background color
                    highlight_format.setBackground(QColor(100, 149, 237))
                
                # Set text color
                if 'text_color' in term:
                    # Use custom text color
                    text_color = QColor(term['text_color'])
                    highlight_format.setForeground(text_color)
                elif 'color' in term:
                    # Auto-select text color based on background brightness (legacy behavior)
                    bg_color = QColor(term['color'])
                    if bg_color.lightness() > 128:
                        highlight_format.setForeground(QColor(0, 0, 0))
                    else:
                        highlight_format.setForeground(QColor(255, 255, 255))
                else:
                    # Use default text color
                    highlight_format.setForeground(QColor(0, 0, 0))
                
                # Set bold formatting
                if term.get('bold', False):
                    try:
                        highlight_format.setFontWeight(QFont.Weight.Bold)
                    except AttributeError:
                        # Fallback for older PyQt versions
                        highlight_format.setFontWeight(700)  # Bold weight
                else:
                    try:
                        highlight_format.setFontWeight(QFont.Weight.Normal)
                    except AttributeError:
                        # Fallback for older PyQt versions
                        highlight_format.setFontWeight(400)  # Normal weight
                
                # Store both original term and processed term for comparison
                case_sensitive = term.get('case_sensitive', False)
                processed_term = term['term'] if case_sensitive else term['term'].lower()
                
                self.highlight_terms.append({
                    'term': processed_term,
                    'original_term': term['term'],
                    'case_sensitive': case_sensitive,
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
    
    def set_bookmarked_lines(self, bookmarked_lines):
        """Set the lines that should have bookmark highlighting"""
        self.bookmarked_lines = set(bookmarked_lines)
        self.rehighlight()
    
    def add_bookmark_line(self, line_number):
        """Add a line to bookmark highlighting"""
        self.bookmarked_lines.add(line_number)
        # Only rehighlight the specific block for performance
        if hasattr(self, 'document') and self.document():
            block = self.document().findBlockByNumber(line_number - 1)
            if block.isValid():
                self.rehighlightBlock(block)
    
    def remove_bookmark_line(self, line_number):
        """Remove a line from bookmark highlighting"""
        self.bookmarked_lines.discard(line_number)
        # Only rehighlight the specific block for performance
        if hasattr(self, 'document') and self.document():
            block = self.document().findBlockByNumber(line_number - 1)
            if block.isValid():
                self.rehighlightBlock(block)
    
    def update_bookmark_format(self, bookmark_format):
        """Update the bookmark highlighting format"""
        self.bookmark_format = bookmark_format
        # Rehighlight all bookmarked lines with the new format
        if self.bookmarked_lines and hasattr(self, 'document') and self.document():
            for line_number in self.bookmarked_lines:
                block = self.document().findBlockByNumber(line_number - 1)
                if block.isValid():
                    self.rehighlightBlock(block)

    def highlightBlock(self, text):
        # Get the current block's position in the document
        block = self.currentBlock()
        block_start = block.position()
        block_end = block_start + block.length()
        line_number = block.blockNumber() + 1  # 1-based line number
        
        # Check if this line is bookmarked (highest priority)
        if line_number in self.bookmarked_lines:
            self.setFormat(0, len(text), self.bookmark_format)
            return  # Bookmark highlighting takes precedence
        
        # Check if this block overlaps with search-highlighted area
        if (self.search_highlighted_start is not None and 
            self.search_highlighted_end is not None):
            # If this block overlaps with search highlighting, don't apply config highlighting
            if (block_start < self.search_highlighted_end and 
                block_end > self.search_highlighted_start):
                return
        
        # Apply config-based highlighting only if not in search-highlighted area
        for term_info in self.highlight_terms:
            # Check if term matches based on case sensitivity
            if term_info.get('case_sensitive', False):
                # Case-sensitive search
                if term_info['term'] in text:
                    self.setFormat(0, len(text), term_info['format'])
            else:
                # Case-insensitive search (default)
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
            
            <h2>Configuration Files</h2>
            <h3>Configuration Precedence</h3>
            <p>Log Viewer loads configuration files in the following order of precedence:</p>
            <ol>
                <li><strong>Command Line Config</strong> (Highest Priority): <code>log_viewer --config /path/to/config.yml</code></li>
                <li><strong>User Default Config</strong>: <code>~/logviewer_config.yml</code> (in your home directory)</li>
                <li><strong>Platform-Specific Config</strong> (Lowest Priority): See platform sections below</li>
            </ol>
            
            <h3>Creating a User Default Config</h3>
            <p>To create a personal configuration that applies to all Log Viewer sessions:</p>
            <ol>
                <li>Open the Configuration Dialog ("Configure Highlighting" button)</li>
                <li>Set up your preferred highlight terms and colors</li>
                <li>Click "Save Config" - it will default to <code>~/logviewer_config.yml</code></li>
                <li>Your settings will automatically load in future sessions</li>
            </ol>
            
            <h3>Configuration Structure</h3>
            <pre>highlight_terms:
  - term: "ERROR"
    color: "#ff0000"
  - term: "WARNING" 
    color: "#ffff00"
  - "INFO"  # Uses default color
theme: "system"  # Options: system, light, dark
line_wrap_enabled: false
line_numbers_enabled: false</pre>
            
            <h2>Themes and Display</h2>
            <h3>Theme Options</h3>
            <ul>
                <li><strong>System Theme:</strong> Automatically matches your operating system theme</li>
                <li><strong>Light Theme:</strong> Light background with dark text</li>
                <li><strong>Dark Theme:</strong> Dark background optimized for log viewing</li>
            </ul>
            
            <h3>Changing Themes</h3>
            <ol>
                <li>Go to <strong>View</strong> → <strong>Theme</strong> in the menu bar</li>
                <li>Select your preferred theme option</li>
                <li>The theme will change immediately and be saved to your configuration</li>
            </ol>
            
            <h3>Line Wrapping</h3>
            <ul>
                <li>Toggle line wrapping using <strong>View</strong> → <strong>Line Wrap</strong></li>
                <li>When enabled, long lines will wrap to fit the window width</li>
                <li>When disabled, long lines extend horizontally with a scrollbar</li>
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
                <li><strong>User Config:</strong> <code>~/logviewer_config.yml</code> (recommended)</li>
                <li><strong>System Config:</strong> <code>%APPDATA%\\LogViewer\\config.yml</code></li>
                <li>Use Windows-style paths (e.g., <code>C:\\path\\to\\file.log</code>)</li>
                <li>The application supports high DPI displays</li>
            </ul>
            
            <h3>macOS</h3>
            <ul>
                <li><strong>User Config:</strong> <code>~/logviewer_config.yml</code> (recommended)</li>
                <li><strong>System Config:</strong> <code>~/Library/Application Support/LogViewer/config.yml</code></li>
                <li>Use Unix-style paths (e.g., <code>/path/to/file.log</code>)</li>
                <li>The application supports Retina displays</li>
                <li>Use Cmd+O to open files and Cmd+Q to quit</li>
            </ul>
            
            <h3>Linux</h3>
            <ul>
                <li><strong>User Config:</strong> <code>~/logviewer_config.yml</code> (recommended)</li>
                <li><strong>System Config:</strong> <code>./config.yml</code> (current directory)</li>
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
        app_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_colors.text_color};
                font-size: 18pt;
                font-weight: bold;
                text-align: center;
            }}
        """)
        app_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_label)
        
        company_label = QLabel("Michette Technologies")
        company_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_colors.text_color};
                font-size: 14pt;
                text-align: center;
            }}
        """)
        company_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(company_label)
        
        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_colors.text_color};
                font-size: 12pt;
                text-align: center;
            }}
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Add some space
        layout.addSpacing(20)
        
        # Additional info
        info_label = QLabel("A powerful log file viewer with ANSI color support\nand configurable highlighting features.")
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_colors.window_text};
                font-size: 10pt;
                text-align: center;
            }}
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Add stretch to push button to bottom
        layout.addStretch()
        
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

class TermFormatDialog(QDialog):
    # Signal to notify when apply is pressed
    applied = pyqtSignal(dict)
    
    def __init__(self, parent=None, term="", bg_color=None, text_color=None, bold=False, case_sensitive=False):
        super().__init__(parent)
        self.setWindowTitle("Term Formatting")
        self.setModal(True)
        self.resize(450, 350)  # Increased size for new UI elements
        
        # Get theme colors from parent
        if parent and hasattr(parent, 'theme_colors'):
            self.theme_colors = parent.theme_colors
        elif parent and hasattr(parent, 'current_theme_colors'):
            self.theme_colors = parent.current_theme_colors
        else:
            # Fallback theme colors for dark mode
            self.theme_colors = type('', (), {
                'window_bg': '#2b2b2b',
                'window_text': '#ffffff',
                'button_bg': '#404040',
                'button_text': '#ffffff',
                'border_color': '#555555',
                'hover_color': '#505050',
                'pressed_color': '#606060'
            })()
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme_colors.window_bg};
                color: {self.theme_colors.window_text};
            }}
            QLabel {{
                color: {self.theme_colors.window_text};
                background: transparent;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Term input
        term_layout = QHBoxLayout()
        term_layout.addWidget(QLabel("Term:"))
        self.term_edit = QLineEdit(term)
        self.term_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme_colors.button_bg};
                color: {self.theme_colors.button_text};
                border: 1px solid {self.theme_colors.border_color};
                padding: 5px;
                border-radius: 3px;
            }}
        """)
        # Connect text change to smart color suggestions
        self.term_edit.textChanged.connect(self.on_term_text_changed)
        term_layout.addWidget(self.term_edit)
        layout.addLayout(term_layout)
        
        # Background color
        bg_layout = QVBoxLayout()
        bg_label_layout = QHBoxLayout()
        bg_label_layout.addWidget(QLabel("Background Color:"))
        bg_layout.addLayout(bg_label_layout)
        
        # Color selection buttons layout
        color_buttons_layout = QHBoxLayout()
        
        # Auto/Smart color presets
        self.smart_colors = {
            'Auto': None,  # Will be determined by term content
            'Error': '#FF4444',    # Red for errors
            'Warning': '#FFA500',  # Orange for warnings 
            'Info': '#4A90E2',     # Blue for info
            'Success': '#28A745',  # Green for success
            'Debug': '#6C757D'     # Gray for debug
        }
        
        # Add smart color buttons
        from PyQt6.QtWidgets import QComboBox
        self.bg_preset_combo = QComboBox()
        self.bg_preset_combo.addItem("Smart Colors...")
        for preset_name in self.smart_colors.keys():
            self.bg_preset_combo.addItem(preset_name)
        
        self.bg_preset_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme_colors.button_bg};
                color: {self.theme_colors.button_text};
                border: 1px solid {self.theme_colors.border_color};
                padding: 5px;
                border-radius: 3px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                background-color: {self.theme_colors.hover_color};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
        """)
        self.bg_preset_combo.currentTextChanged.connect(self.on_preset_color_changed)
        color_buttons_layout.addWidget(self.bg_preset_combo)
        
        # Custom color picker button
        self.bg_color_btn = QPushButton("Custom Color")
        self.bg_color = QColor(bg_color) if bg_color else QColor(100, 149, 237)
        self.update_bg_color_button()
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        color_buttons_layout.addWidget(self.bg_color_btn)
        
        bg_layout.addLayout(color_buttons_layout)
        layout.addLayout(bg_layout)
        
        # Text color
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("Text Color:"))
        self.text_color_btn = QPushButton("Choose Color")
        self.text_color = QColor(text_color) if text_color else None
        self.update_text_color_button()
        self.text_color_btn.clicked.connect(self.choose_text_color)
        text_layout.addWidget(self.text_color_btn)
        
        # Clear text color button
        self.clear_text_btn = QPushButton("Auto")
        self.clear_text_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_colors.button_bg};
                color: {self.theme_colors.button_text};
                border: 1px solid {self.theme_colors.border_color};
                padding: 8px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors.hover_color};
            }}
        """)
        self.clear_text_btn.clicked.connect(self.clear_text_color)
        text_layout.addWidget(self.clear_text_btn)
        layout.addLayout(text_layout)
        
        # Bold checkbox
        self.bold_checkbox = QCheckBox("Bold Text")
        self.bold_checkbox.setChecked(bold)
        self.bold_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {self.theme_colors.window_text};
                padding: 5px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {self.theme_colors.border_color};
                border-radius: 3px;
                background-color: {self.theme_colors.button_bg};
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {self.theme_colors.window_text};
                background-color: {self.theme_colors.hover_color};
            }}
            QCheckBox::indicator:checked {{
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                image: none;
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: #45a049;
                border: 2px solid #45a049;
            }}
        """)
        layout.addWidget(self.bold_checkbox)
        
        # Case sensitive checkbox
        self.case_sensitive_checkbox = QCheckBox("Case Sensitive")
        self.case_sensitive_checkbox.setChecked(case_sensitive)
        self.case_sensitive_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {self.theme_colors.window_text};
                padding: 5px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {self.theme_colors.border_color};
                border-radius: 3px;
                background-color: {self.theme_colors.button_bg};
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {self.theme_colors.window_text};
                background-color: {self.theme_colors.hover_color};
            }}
            QCheckBox::indicator:checked {{
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                image: none;
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: #45a049;
                border: 2px solid #45a049;
            }}
        """)
        layout.addWidget(self.case_sensitive_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Apply button
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_colors.button_bg};
                color: {self.theme_colors.button_text};
                border: 1px solid {self.theme_colors.border_color};
                padding: 8px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors.hover_color};
            }}
        """)
        apply_btn.clicked.connect(self.apply_changes)
        button_layout.addWidget(apply_btn)
        
        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_colors.button_bg};
                color: {self.theme_colors.button_text};
                border: 1px solid {self.theme_colors.border_color};
                padding: 8px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors.hover_color};
            }}
        """)
        ok_btn.clicked.connect(self.accept)
        
        # Cancel button  
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_colors.button_bg};
                color: {self.theme_colors.button_text};
                border: 1px solid {self.theme_colors.border_color};
                padding: 8px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors.hover_color};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Initialize color button appearance and smart suggestions
        self.update_bg_color_button()
        self.on_term_text_changed()  # Set initial smart color suggestion
    
    def on_preset_color_changed(self, preset_name):
        """Handle preset color selection from combo box"""
        if preset_name == "Smart Colors...":
            return
            
        if preset_name == "Auto":
            # Determine color based on term content
            self.bg_color = self.determine_smart_color()
        elif preset_name in self.smart_colors:
            color_hex = self.smart_colors[preset_name]
            if color_hex:
                self.bg_color = QColor(color_hex)
        
        self.update_bg_color_button()
        # Reset combo box to default
        self.bg_preset_combo.setCurrentIndex(0)
    
    def determine_smart_color(self):
        """Determine appropriate color based on term content"""
        term_lower = self.term_edit.text().lower()
        
        # Check for common log level patterns
        if any(keyword in term_lower for keyword in ['error', 'err', 'fatal', 'critical', 'fail']):
            return QColor('#FF4444')  # Red
        elif any(keyword in term_lower for keyword in ['warning', 'warn', 'caution']):
            return QColor('#FFA500')  # Orange
        elif any(keyword in term_lower for keyword in ['success', 'complete', 'done', 'ok']):
            return QColor('#28A745')  # Green
        elif any(keyword in term_lower for keyword in ['info', 'information']):
            return QColor('#4A90E2')  # Blue
        elif any(keyword in term_lower for keyword in ['debug', 'trace', 'verbose']):
            return QColor('#6C757D')  # Gray
        else:
            return QColor(100, 149, 237)  # Default cornflower blue
    
    def on_term_text_changed(self):
        """Handle term text changes to suggest smart colors"""
        # Update the "Auto" option in the combo box with suggested color info
        suggested_color = self.determine_smart_color()
        color_name = self.get_color_name(suggested_color)
        
        # Update the Auto option text to show the suggested color
        auto_index = self.bg_preset_combo.findText("Auto")
        if auto_index >= 0:
            self.bg_preset_combo.setItemText(auto_index, f"Auto ({color_name})")
    
    def get_color_name(self, color):
        """Get a human-readable name for a color"""
        color_hex = color.name().upper()
        color_map = {
            '#FF4444': 'Red',
            '#FFA500': 'Orange', 
            '#28A745': 'Green',
            '#4A90E2': 'Blue',
            '#6C757D': 'Gray'
        }
        return color_map.get(color_hex, 'Default')
    
    def update_bg_color_button(self):
        """Update the background color button appearance"""
        self.bg_color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.bg_color.name()};
                color: {'#000000' if self.bg_color.lightness() > 128 else '#ffffff'};
                border: 1px solid {self.theme_colors.border_color};
                padding: 8px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 2px solid {self.theme_colors.border_color};
            }}
        """)
    
    def choose_bg_color(self):
        color = QColorDialog.getColor(self.bg_color, self, "Choose Background Color")
        if color.isValid():
            self.bg_color = color
            self.update_bg_color_button()
    
    def choose_text_color(self):
        initial_color = self.text_color if self.text_color else QColor(0, 0, 0)
        color = QColorDialog.getColor(initial_color, self, "Choose Text Color")
        if color.isValid():
            self.text_color = color
            self.update_text_color_button()
    
    def clear_text_color(self):
        self.text_color = None
        self.update_text_color_button()
    
    def update_text_color_button(self):
        if self.text_color:
            self.text_color_btn.setText(f"Text Color: {self.text_color.name()}")
            self.text_color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.text_color.name()};
                    color: {'#000000' if self.text_color.lightness() > 128 else '#ffffff'};
                    border: 1px solid {self.theme_colors.border_color};
                    padding: 8px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    border: 2px solid {self.theme_colors.border_color};
                }}
            """)
        else:
            self.text_color_btn.setText("Auto Text Color")
            self.text_color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.theme_colors.button_bg};
                    color: {self.theme_colors.button_text};
                    border: 1px solid {self.theme_colors.border_color};
                    padding: 8px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background-color: {self.theme_colors.hover_color};
                }}
            """)
    
    def apply_changes(self):
        """Apply the current formatting changes without closing the dialog"""
        result = self.get_result()
        self.applied.emit(result)
    
    def get_result(self):
        result = {
            'term': self.term_edit.text(),
            'color': self.bg_color.name(),
            'bold': self.bold_checkbox.isChecked(),
            'case_sensitive': self.case_sensitive_checkbox.isChecked()
        }
        if self.text_color:
            result['text_color'] = self.text_color.name()
        return result

class ConfigDialog(QDialog):
    def __init__(self, parent=None, highlight_terms=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Highlighting")
        self.resize(400, 300)
        self.highlight_terms = highlight_terms or []
        # Store original terms for restoration on cancel
        self.original_highlight_terms = [term.copy() if isinstance(term, dict) else term for term in self.highlight_terms]
        
        # Use parent's theme
        if parent and hasattr(parent, 'current_theme_colors'):
            self.theme_colors = parent.current_theme_colors
        else:
            self.theme_colors = get_theme_colors(ThemeMode.SYSTEM)
        
        # Set palette from theme
        palette = self.parent().palette() if parent else QPalette()
        self.setPalette(palette)
        
        layout = QVBoxLayout(self)
        
        # Terms list
        self.terms_list = QListWidget()
        self.terms_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.theme_colors.base_bg};
                color: {self.theme_colors.text_color};
                border: 1px solid {self.theme_colors.border_color};
            }}
        """)
        self.update_terms_list()
        
        self.terms_label = QLabel("Highlight Terms:")
        self.terms_label.setStyleSheet(f"color: {self.theme_colors.text_color};")
        layout.addWidget(self.terms_label)
        layout.addWidget(self.terms_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        # Create themed button style
        button_style = f"""
            QPushButton {{
                background-color: {self.theme_colors.button_bg};
                color: {self.theme_colors.button_text};
                border: 1px solid {self.theme_colors.border_color};
                padding: 5px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.theme_colors.pressed_color};
            }}
        """
        
        add_btn = QPushButton("Add Term")
        add_btn.setStyleSheet(button_style)
        add_btn.clicked.connect(self.add_term)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit Term")
        edit_btn.setStyleSheet(button_style)
        edit_btn.clicked.connect(self.edit_term)
        btn_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("Remove Term")
        remove_btn.setStyleSheet(button_style)
        remove_btn.clicked.connect(self.remove_term)
        btn_layout.addWidget(remove_btn)
        
        layout.addLayout(btn_layout)
        
        # Save/Load buttons
        config_btn_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Config")
        save_btn.setStyleSheet(button_style)
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
                
        button_box.setStyleSheet(button_style)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def update_terms_list(self):
        self.terms_list.clear()
        for term in self.highlight_terms:
            if isinstance(term, dict):
                display_text = term['term']
                if 'color' in term:
                    display_text += f" (Bg: {term['color']})"
                if 'text_color' in term:
                    display_text += f" (Text: {term['text_color']})"
                if term.get('bold', False):
                    display_text += " (Bold)"
                if term.get('case_sensitive', False):
                    display_text += " (Case Sensitive)"
                self.terms_list.addItem(display_text)
            else:
                self.terms_list.addItem(term)
    
    def add_term(self):
        dialog = TermFormatDialog(self)
        
        # Connect apply signal to preview the changes
        dialog.applied.connect(lambda term_data: self.preview_term_changes(term_data, is_new=True))
        # Store original state for restoration if dialog is cancelled
        original_terms = [term.copy() if isinstance(term, dict) else term for term in self.highlight_terms]
        dialog.finished.connect(lambda result: self.restore_on_cancel(result, original_terms) if result == 0 else None)
        
        # Use try/except to handle different PyQt versions for dialog execution
        try:
            result = dialog.exec()
        except AttributeError:
            try:
                result = dialog.exec_()
            except AttributeError:
                result = QtConstants.Rejected
                print("Warning: Could not execute format dialog.")
        
        if result == QtConstants.Accepted:
            term_data = dialog.get_result()
            if term_data['term']:  # Only add if term is not empty
                self.highlight_terms.append(term_data)
                self.update_terms_list()
                # Apply changes to main window
                if hasattr(self.parent(), 'highlighter') and hasattr(self.parent(), 'highlighter'):
                    self.parent().highlighter.set_highlight_terms(self.highlight_terms)
    
    def edit_term(self):
        current_row = self.terms_list.currentRow()
        if current_row >= 0:
            current_term = self.highlight_terms[current_row]
            
            if isinstance(current_term, dict):
                term = current_term['term']
                bg_color = current_term.get('color', None)
                text_color = current_term.get('text_color', None)
                bold = current_term.get('bold', False)
                case_sensitive = current_term.get('case_sensitive', False)
            else:
                term = current_term
                bg_color = None
                text_color = None
                bold = False
                case_sensitive = False
            
            dialog = TermFormatDialog(self, term=term, bg_color=bg_color, 
                                    text_color=text_color, bold=bold, case_sensitive=case_sensitive)
            
            # Connect apply signal to preview the changes
            dialog.applied.connect(lambda term_data: self.preview_term_changes(term_data, is_new=False, index=current_row))
            # Store original state for restoration if dialog is cancelled
            original_terms = [term.copy() if isinstance(term, dict) else term for term in self.highlight_terms]
            dialog.finished.connect(lambda result: self.restore_on_cancel(result, original_terms) if result == 0 else None)
            
            # Use try/except to handle different PyQt versions for dialog execution
            try:
                result = dialog.exec()
            except AttributeError:
                try:
                    result = dialog.exec_()
                except AttributeError:
                    result = QtConstants.Rejected
                    print("Warning: Could not execute format dialog.")
            
            if result == QtConstants.Accepted:
                term_data = dialog.get_result()
                if term_data['term']:  # Only update if term is not empty
                    self.highlight_terms[current_row] = term_data
                    self.update_terms_list()
                    # Apply changes to main window
                    if hasattr(self.parent(), 'highlighter') and hasattr(self.parent(), 'highlighter'):
                        self.parent().highlighter.set_highlight_terms(self.highlight_terms)
    
    def preview_term_changes(self, term_data, is_new=False, index=None):
        """Preview term changes in the main window without permanently saving them"""
        if not term_data['term']:  # Don't preview empty terms
            return
            
        # Create a temporary copy of highlight terms for preview
        preview_terms = self.highlight_terms.copy()
        
        if is_new:
            # Add the new term temporarily
            preview_terms.append(term_data)
        else:
            # Update existing term temporarily
            if index is not None and 0 <= index < len(preview_terms):
                preview_terms[index] = term_data
        
        # Apply preview to main window highlighter
        if hasattr(self.parent(), 'highlighter'):
            self.parent().highlighter.set_highlight_terms(preview_terms)
            # Force a repaint to show the changes immediately
            if hasattr(self.parent(), 'text_editor'):
                self.parent().text_editor.update()
    
    def reject(self):
        """Override reject to restore original highlighting when cancelled"""
        # Restore original highlighting
        if hasattr(self.parent(), 'highlighter'):
            self.parent().highlighter.set_highlight_terms(self.original_highlight_terms)
            # Force a repaint to show the restored highlighting
            if hasattr(self.parent(), 'text_editor'):
                self.parent().text_editor.update()
        super().reject()
    
    def accept(self):
        """Override accept to ensure final changes are applied"""
        # Apply final changes to main window
        if hasattr(self.parent(), 'highlighter'):
            self.parent().highlighter.set_highlight_terms(self.highlight_terms)
        super().accept()
    
    def restore_on_cancel(self, result, original_terms):
        """Restore highlighting when TermFormatDialog is cancelled"""
        if result == 0:  # Dialog was rejected/cancelled
            if hasattr(self.parent(), 'highlighter'):
                self.parent().highlighter.set_highlight_terms(original_terms)
                if hasattr(self.parent(), 'text_editor'):
                    self.parent().text_editor.update()
    
    def remove_term(self):
        current_row = self.terms_list.currentRow()
        if current_row >= 0:
            del self.highlight_terms[current_row]
            self.update_terms_list()
    
    def save_config(self):
        # Default to user's home directory with standard config filename
        default_filename = "logviewer_config.yml"
        default_path = os.path.join(os.path.expanduser("~"), default_filename)
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration", 
            default_path,  # Provide default filename with .yml extension
            "YAML Files (*.yml);;All Files (*)"
        )
        if file_name:
            # Ensure .yml extension if not present
            if not file_name.lower().endswith(('.yml', '.yaml')):
                file_name += '.yml'
            
            try:
                config = {'highlight_terms': self.highlight_terms}
                with open(file_name, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False)
                QMessageBox.information(self, "Success", f"Configuration saved to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")

class BookmarkListDialog(QDialog):
    def __init__(self, parent=None, bookmarks=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks")
        self.resize(600, 400)
        self.bookmarks = bookmarks or []
        self.selected_bookmark = None
        
        # Use parent's theme
        if parent and hasattr(parent, 'current_theme_colors'):
            self.theme_colors = parent.current_theme_colors
        else:
            self.theme_colors = get_theme_colors(ThemeMode.SYSTEM)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Double-click a bookmark to navigate to it, or select and click 'Go To'.")
        instructions.setStyleSheet(f"color: {self.theme_colors.window_text};")
        layout.addWidget(instructions)
        
        # Bookmark list
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem
        self.bookmark_list = QListWidget()
        self.bookmark_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.theme_colors.base_bg};
                color: {self.theme_colors.text_color};
                border: 1px solid {self.theme_colors.border_color};
                selection-background-color: {self.theme_colors.highlight_bg};
            }}
        """)
        
        # Populate bookmark list
        for bookmark in self.bookmarks:
            line_content = bookmark['content'][:60]  # Limit display length
            item_text = f"Line {bookmark['line']:4d}: {line_content}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, bookmark)  # Store bookmark data
            self.bookmark_list.addItem(item)
        
        # Handle double-click to navigate
        self.bookmark_list.itemDoubleClicked.connect(self.on_bookmark_double_clicked)
        layout.addWidget(self.bookmark_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        goto_btn = QPushButton("Go To")
        goto_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_colors.button_bg};
                color: {self.theme_colors.button_text};
                border: 1px solid {self.theme_colors.border_color};
                padding: 8px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors.hover_color};
            }}
        """)
        goto_btn.clicked.connect(self.goto_selected)
        button_layout.addWidget(goto_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_colors.button_bg};
                color: {self.theme_colors.button_text};
                border: 1px solid {self.theme_colors.border_color};
                padding: 8px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors.hover_color};
            }}
        """)
        delete_btn.clicked.connect(self.delete_selected)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_colors.button_bg};
                color: {self.theme_colors.button_text};
                border: 1px solid {self.theme_colors.border_color};
                padding: 8px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors.hover_color};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Apply dialog theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.theme_colors.window_bg};
                color: {self.theme_colors.window_text};
            }}
        """)
    
    def on_bookmark_double_clicked(self, item):
        """Handle double-click on bookmark item"""
        bookmark = item.data(Qt.ItemDataRole.UserRole)
        if bookmark:
            self.selected_bookmark = bookmark
            self.accept()
    
    def goto_selected(self):
        """Go to the selected bookmark"""
        current_item = self.bookmark_list.currentItem()
        if current_item:
            bookmark = current_item.data(Qt.ItemDataRole.UserRole)
            if bookmark:
                self.selected_bookmark = bookmark
                self.accept()
    
    def delete_selected(self):
        """Delete the selected bookmark"""
        current_row = self.bookmark_list.currentRow()
        if current_row >= 0:
            bookmark = self.bookmarks[current_row]
            reply = QMessageBox.question(self, "Delete Bookmark", 
                                       f"Delete bookmark at line {bookmark['line']}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                # Remove from both the dialog list and parent's bookmark list
                self.bookmarks.pop(current_row)
                self.bookmark_list.takeItem(current_row)
                
                # Also remove from parent's bookmarks if available
                if self.parent() and hasattr(self.parent(), 'bookmarks'):
                    self.parent().bookmarks = [b for b in self.parent().bookmarks if b['line'] != bookmark['line']]
                    self.parent().update_bookmark_highlights()

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
        self.main_window = parent  # Store reference to main window
        
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
        """Append text more efficiently with ANSI processing"""
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
        
        # Process ANSI colors if enabled (check if main_window exists and has ANSI enabled)
        if (self.main_window and 
            hasattr(self.main_window, 'ansi_processing_enabled') and 
            self.main_window.ansi_processing_enabled):
            # Debug: Check if we're taking the ANSI processing path
            if '\x1b[' in text or '\033[' in text:
                print(f"ANSI processing path: processing text with ANSI codes")
            self.append_text_with_ansi(text, cursor)
        else:
            # Debug: Check why ANSI processing isn't enabled
            if self.main_window:
                print(f"ANSI processing disabled: enabled={getattr(self.main_window, 'ansi_processing_enabled', 'MISSING')}")
            else:
                print("ANSI processing disabled: no main_window reference")
            # Just clean and insert text
            clean_text = self.clean_text_basic(text)
            if clean_text:
                cursor.insertText(clean_text)
        
        # Limit text updates for better performance
        self.setUpdatesEnabled(False)
        self.setTextCursor(cursor)
        self.setUpdatesEnabled(True)
    
    def clean_text(self, text):
        """Clean text of problematic characters and escape sequences"""
        if not text:
            return text
            
        # Remove ANSI escape sequences that weren't parsed
        import re
        
        # Remove various ANSI escape sequences
        # Color sequences: \x1b[0m, \x1b[31m, etc.
        ansi_color = re.compile(r'\x1b\[[0-9;]*m')
        text = ansi_color.sub('', text)
        
        # Cursor movement: \x1b[H, \x1b[2J, etc. 
        ansi_cursor = re.compile(r'\x1b\[[0-9;]*[ABCDHJKfhl]')
        text = ansi_cursor.sub('', text)
        
        # Other escape sequences
        ansi_other = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
        text = ansi_other.sub('', text)
        
        # Remove bare escape characters
        text = text.replace('\x1b', '')
        
        # Handle problematic Unicode characters (actual Unicode, not escaped)
        problematic_chars = {
            '\u202a': '',  # Left-to-right embedding
            '\u202b': '',  # Right-to-left embedding  
            '\u202c': '',  # Pop directional formatting
            '\u202d': '',  # Left-to-right override
            '\u202e': '',  # Right-to-left override
            '\u200b': '',  # Zero-width space
            '\u200c': '',  # Zero-width non-joiner
            '\u200d': '',  # Zero-width joiner
            '\u2060': '',  # Word joiner
            '\ufeff': '',  # Zero-width no-break space (BOM)
            '\u2028': '\n',  # Line separator -> normal newline
            '\u2029': '\n',  # Paragraph separator -> normal newline
        }
        
        for char, replacement in problematic_chars.items():
            text = text.replace(char, replacement)
        
        # Normalize Unicode to remove combining characters that might cause issues
        try:
            import unicodedata
            text = unicodedata.normalize('NFKC', text)
        except:
            pass  # If unicodedata isn't available, continue without normalization
        
        return text
    
    def clean_text_basic(self, text):
        """Basic text cleaning to remove problematic characters"""
        if not text:
            return text
        
        import re
        
        # Remove ANSI escape sequences (both \x1b[...m and [...m formats)
        ansi_escape = re.compile(r'(\x1b)?\[([0-9;]*)m')
        text = ansi_escape.sub('', text)
        
        # Remove other escape sequences
        ansi_other = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
        text = ansi_other.sub('', text)
        
        # Remove problematic Unicode directional formatting
        text = text.replace('\u202a', '')  # Left-to-right embedding 
        text = text.replace('\u202c', '')  # Pop directional formatting
        
        return text
    
    def append_text_with_ansi(self, text, cursor):
        """Append text with simple ANSI color processing"""
        import re
        
        # Define colors directly here for safety
        ansi_colors = {
            30: QColor(0, 0, 0),        # Black
            31: QColor(255, 0, 0),      # Red
            32: QColor(0, 255, 0),      # Green  
            33: QColor(255, 255, 0),    # Yellow
            34: QColor(0, 0, 255),      # Blue
            35: QColor(255, 0, 255),    # Magenta
            36: QColor(0, 255, 255),    # Cyan
            37: QColor(255, 255, 255),  # White
            90: QColor(128, 128, 128),  # Bright Black (Gray)
            91: QColor(255, 128, 128),  # Bright Red
            92: QColor(128, 255, 128),  # Bright Green
            93: QColor(255, 255, 128),  # Bright Yellow
            94: QColor(128, 128, 255),  # Bright Blue
            95: QColor(255, 128, 255),  # Bright Magenta
            96: QColor(128, 255, 255),  # Bright Cyan
            97: QColor(255, 255, 255),  # Bright White
        }
        
        # Simple approach: handle the most common ANSI codes safely
        # Match ESC character (ASCII 27) followed by [ and color codes
        ansi_pattern = re.compile(r'\x1b\[([0-9;]*)m')
        
        # Debug: Check what we found
        matches = list(ansi_pattern.finditer(text))
        if matches:
            print(f"Found {len(matches)} ANSI matches in: {text[:50]}...")
        
        last_end = 0
        
        for match in matches:
            # Insert text before ANSI code with current formatting
            if match.start() > last_end:
                text_segment = text[last_end:match.start()]
                if text_segment:
                    clean_segment = self.clean_unicode_only(text_segment)
                    if clean_segment:
                        cursor.insertText(clean_segment)
            
            # Parse the ANSI code for colors and formatting
            code = match.group(1)
            if code:
                try:
                    # Split compound codes like "0;32" into individual codes
                    codes = [int(c) for c in code.split(';') if c.strip()]
                    format_obj = QTextCharFormat()
                    
                    # Process each code
                    for color_code in codes:
                        if color_code == 0:
                            # Reset formatting
                            format_obj = QTextCharFormat()
                        elif color_code == 1:
                            # Bold
                            try:
                                format_obj.setFontWeight(QFont.Weight.Bold)
                            except AttributeError:
                                format_obj.setFontWeight(700)
                        elif color_code in ansi_colors:
                            # Apply color
                            format_obj.setForeground(ansi_colors[color_code])
                    
                    cursor.setCharFormat(format_obj)
                except (ValueError, IndexError, AttributeError):
                    # If parsing fails, just continue without color
                    cursor.setCharFormat(QTextCharFormat())
            else:
                # Empty code means reset
                cursor.setCharFormat(QTextCharFormat())
            
            last_end = match.end()
        
        # Insert any remaining text
        if last_end < len(text):
            remaining_text = text[last_end:]
            if remaining_text:
                clean_remaining = self.clean_unicode_only(remaining_text)
                if clean_remaining:
                    cursor.insertText(clean_remaining)
    
    def clean_unicode_only(self, text):
        """Clean only Unicode issues, not ANSI codes (for pre-processed ANSI segments)"""
        if not text:
            return text
        
        # Handle problematic Unicode characters (actual Unicode, not escaped)
        problematic_chars = {
            '\u202a': '',  # Left-to-right embedding
            '\u202b': '',  # Right-to-left embedding  
            '\u202c': '',  # Pop directional formatting
            '\u202d': '',  # Left-to-right override
            '\u202e': '',  # Right-to-left override
            '\u200b': '',  # Zero-width space
            '\u200c': '',  # Zero-width non-joiner
            '\u200d': '',  # Zero-width joiner
            '\u2060': '',  # Word joiner
            '\ufeff': '',  # Zero-width no-break space (BOM)
            '\u2028': '\n',  # Line separator -> normal newline
            '\u2029': '\n',  # Paragraph separator -> normal newline
        }
        
        for char, replacement in problematic_chars.items():
            text = text.replace(char, replacement)
        
        # Normalize Unicode to remove combining characters that might cause issues
        try:
            import unicodedata
            text = unicodedata.normalize('NFKC', text)
        except:
            pass  # If unicodedata isn't available, continue without normalization
        
        return text
    
    def contextMenuEvent(self, event):
        """Handle right-click context menu for bookmarks"""
        if not self.main_window:
            return
        
        cursor = self.cursorForPosition(event.pos())
        line_number = cursor.blockNumber() + 1  # Line numbers are 1-based
        
        # Create context menu
        menu = QMenu(self)
        
        # Check if current line is bookmarked
        is_bookmarked = any(bookmark['line'] == line_number for bookmark in self.main_window.bookmarks)
        
        if is_bookmarked:
            action = menu.addAction("Remove Bookmark")
            action.triggered.connect(lambda: self.main_window.toggle_bookmark_at_line(line_number))
        else:
            action = menu.addAction("Add Bookmark")
            action.triggered.connect(lambda: self.main_window.toggle_bookmark_at_line(line_number))
        
        # Show menu at cursor position
        menu.exec(event.globalPos())

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
        
        # Line wrap state
        self.line_wrap_enabled = False
        
        # Line numbers state
        self.line_numbers_enabled = False
        self.current_line_number = 1  # Track current line number for chunk processing
        
        # Bookmark system
        self.bookmarks = []  # List of bookmark dictionaries with line numbers and content
        self.current_bookmark_index = -1  # Current bookmark for navigation
        self.bookmark_highlight_color = "#64C8FF"  # Default light blue color (100, 200, 255)
        self.bookmark_highlight_format = QTextCharFormat()
        self.update_bookmark_highlight_format()
        
        # Search system
        self.case_sensitive_search = False  # Case-sensitive search option
        
        # ANSI processing system
        self.ansi_processing_enabled = True  # Enable ANSI color processing by default
        
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
        self.text_editor = OptimizedTextEdit(self)
        # Style will be applied by theme system
        layout.addWidget(self.text_editor)
        
        # Add progress bar for file loading
        self.progress_bar = QProgressBar()
        # Style will be applied by theme system
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Initialize the highlighter
        self.highlighter = LogHighlighter(self.text_editor.document())
        # Set initial bookmark format
        self.highlighter.update_bookmark_format(self.bookmark_highlight_format)

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
        
        # Case sensitive checkbox
        self.case_sensitive_checkbox = QCheckBox("Case Sensitive")
        self.case_sensitive_checkbox.setChecked(self.case_sensitive_search)
        # Style will be applied by theme system - use basic style for now
        search_layout.addWidget(self.case_sensitive_checkbox)
        self.case_sensitive_checkbox.stateChanged.connect(self.on_case_sensitive_changed)
        
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
        
        # Add refresh system theme option
        theme_menu.addSeparator()
        refresh_theme_action = theme_menu.addAction("Refresh System Theme")
        refresh_theme_action.triggered.connect(self.refresh_system_theme)
        
        # Set initial theme selection
        self.theme_actions[self.current_theme_mode].setChecked(True)
        
        # Add separator and line wrap toggle
        view_menu.addSeparator()
        self.line_wrap_action = view_menu.addAction("Line Wrap")
        self.line_wrap_action.setCheckable(True)
        self.line_wrap_action.setChecked(self.line_wrap_enabled)
        self.line_wrap_action.triggered.connect(self.toggle_line_wrap)
        
        # Line numbers toggle
        self.line_numbers_action = view_menu.addAction("Line Numbers")
        self.line_numbers_action.setCheckable(True)
        self.line_numbers_action.setChecked(self.line_numbers_enabled)
        self.line_numbers_action.triggered.connect(self.toggle_line_numbers)
        
        # ANSI processing toggle
        self.ansi_processing_action = view_menu.addAction("ANSI Color Processing")
        self.ansi_processing_action.setCheckable(True)
        self.ansi_processing_action.setChecked(self.ansi_processing_enabled)
        self.ansi_processing_action.triggered.connect(self.toggle_ansi_processing)
        
        # Bookmarks menu
        bookmarks_menu = menubar.addMenu("Bookmarks")
        
        # Toggle bookmark action
        toggle_bookmark_action = bookmarks_menu.addAction("Toggle Bookmark")
        toggle_bookmark_action.setShortcut("Ctrl+B")
        toggle_bookmark_action.triggered.connect(self.toggle_bookmark)
        
        bookmarks_menu.addSeparator()
        
        # Navigate bookmarks
        next_bookmark_action = bookmarks_menu.addAction("Next Bookmark")
        next_bookmark_action.setShortcut("F2")
        next_bookmark_action.triggered.connect(self.next_bookmark)
        
        prev_bookmark_action = bookmarks_menu.addAction("Previous Bookmark")
        prev_bookmark_action.setShortcut("Shift+F2")
        prev_bookmark_action.triggered.connect(self.prev_bookmark)
        
        bookmarks_menu.addSeparator()
        
        # Bookmark list
        list_bookmarks_action = bookmarks_menu.addAction("List All Bookmarks")
        list_bookmarks_action.setShortcut("Ctrl+Shift+B")
        list_bookmarks_action.triggered.connect(self.list_bookmarks)
        
        # Clear all bookmarks
        clear_bookmarks_action = bookmarks_menu.addAction("Clear All Bookmarks")
        clear_bookmarks_action.triggered.connect(self.clear_all_bookmarks)
        
        bookmarks_menu.addSeparator()
        
        # Configure bookmark color
        config_bookmark_color_action = bookmarks_menu.addAction("Configure Bookmark Color")
        config_bookmark_color_action.triggered.connect(self.configure_bookmark_color)
        
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
        
        # Bookmark shortcuts (Ctrl+B is handled by menu action)
        next_bookmark_shortcut = QShortcut(QKeySequence("F2"), self)
        next_bookmark_shortcut.activated.connect(self.next_bookmark)
        
        prev_bookmark_shortcut = QShortcut(QKeySequence("Shift+F2"), self)
        prev_bookmark_shortcut.activated.connect(self.prev_bookmark)
        
        list_bookmarks_shortcut = QShortcut(QKeySequence("Ctrl+Shift+B"), self)
        list_bookmarks_shortcut.activated.connect(self.list_bookmarks)
        
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
    
    def on_case_sensitive_changed(self, state):
        """Handle case-sensitive checkbox state change"""
        self.case_sensitive_search = state == 2  # Qt.CheckState.Checked = 2
        # Clear current search results to force re-search with new setting
        if self.search_input.text():
            self.search_results = []
            self.current_search_index = -1
        # Save the preference
        self.save_app_config()

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
        if hasattr(self, 'text_editor') and self.text_editor:
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
        if hasattr(self, 'progress_bar') and self.progress_bar:
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
        if hasattr(self, 'search_input') and self.search_input:
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
        buttons = self.findChildren(QPushButton)
        for button in buttons:
            button.setStyleSheet(button_style)
        
        # Update status label style
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.setStyleSheet(f"color: {colors.text_color};")
        
        # Update font size display style
        self.font_size_display.setStyleSheet(f"""
            color: {colors.text_color};
            padding: 0 10px;
        """)
        
        # Update menu bar style
        menubar = self.menuBar()
        if menubar:
            menubar.setStyleSheet(f"""
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
        labels = self.findChildren(QLabel)
        for label in labels:
            if label != self.font_size_display:  # Skip font size display as it has special styling
                label.setStyleSheet(f"color: {colors.text_color};")
        
        # Update case-sensitive checkbox style
        if hasattr(self, 'case_sensitive_checkbox') and self.case_sensitive_checkbox:
            self.case_sensitive_checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {colors.text_color};
                    padding: 5px;
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {colors.border_color};
                    border-radius: 3px;
                    background-color: {colors.button_bg};
                }}
                QCheckBox::indicator:hover {{
                    border: 2px solid {colors.text_color};
                    background-color: {colors.hover_color};
                }}
                QCheckBox::indicator:checked {{
                    background-color: #4CAF50;
                    border: 2px solid #4CAF50;
                    image: none;
                }}
                QCheckBox::indicator:checked:hover {{
                    background-color: #45a049;
                    border: 2px solid #45a049;
                }}
            """)
    
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
    
    def refresh_system_theme(self):
        """Manually refresh system theme detection"""
        if self.current_theme_mode == ThemeMode.SYSTEM:
            # Force re-detection by re-applying the theme
            self.apply_theme()
            self.status_label.setText("System theme refreshed")
        else:
            self.status_label.setText("Theme refresh only works in System Default mode")

    def toggle_line_wrap(self):
        """Toggle line wrapping on/off in the text editor"""
        self.line_wrap_enabled = not self.line_wrap_enabled
        
        # Apply the new line wrap mode to the text editor
        try:
            if self.line_wrap_enabled:
                # Enable word wrapping
                try:
                    self.text_editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
                except (AttributeError, TypeError):
                    try:
                        self.text_editor.setLineWrapMode(QPlainTextEdit.WidgetWidth)
                    except (AttributeError, TypeError):
                        print("Warning: Could not enable line wrap mode.")
            else:
                # Disable word wrapping  
                try:
                    self.text_editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
                except (AttributeError, TypeError):
                    try:
                        self.text_editor.setLineWrapMode(QPlainTextEdit.NoWrap)
                    except (AttributeError, TypeError):
                        print("Warning: Could not disable line wrap mode.")
        except Exception as e:
            print(f"Error setting line wrap mode: {e}")
        
        # Update the menu action text if it exists
        if hasattr(self, 'line_wrap_action'):
            self.line_wrap_action.setChecked(self.line_wrap_enabled)
        
        # Save the preference
        self.save_app_config()
        
        # Update status
        wrap_status = "enabled" if self.line_wrap_enabled else "disabled"
        self.status_label.setText(f"Line wrap {wrap_status}")

    def toggle_line_numbers(self):
        """Toggle line numbers on/off in the text editor"""
        self.line_numbers_enabled = not self.line_numbers_enabled
        
        # Update the menu action state if it exists
        if hasattr(self, 'line_numbers_action'):
            self.line_numbers_action.setChecked(self.line_numbers_enabled)
        
        # If we have content loaded, refresh the display
        if hasattr(self, 'current_file') and self.current_file:
            self.refresh_display()
        
        # Save the preference
        self.save_app_config()
        
        # Update status
        numbers_status = "enabled" if self.line_numbers_enabled else "disabled"
        self.status_label.setText(f"Line numbers {numbers_status}")

    def toggle_ansi_processing(self):
        """Toggle ANSI color processing on/off"""
        self.ansi_processing_enabled = not self.ansi_processing_enabled
        
        # Update the menu action state if it exists
        if hasattr(self, 'ansi_processing_action'):
            self.ansi_processing_action.setChecked(self.ansi_processing_enabled)
        
        # If we have content loaded, refresh the display
        if hasattr(self, 'current_file') and self.current_file:
            self.refresh_display()
        
        # Save the preference
        self.save_app_config()
        
        # Update status
        ansi_status = "enabled" if self.ansi_processing_enabled else "disabled"
        self.status_label.setText(f"ANSI color processing {ansi_status}")

    def refresh_display(self):
        """Refresh the current file display with current settings"""
        if hasattr(self, 'current_file') and self.current_file and os.path.exists(self.current_file):
            # Reset line counter
            self.current_line_number = 1
            # Reload the file
            self.load_file_async(self.current_file)
    
    def add_line_numbers_to_chunk(self, chunk):
        """Add line numbers to a text chunk"""
        if not self.line_numbers_enabled:
            return chunk
        
        lines = chunk.split('\n')
        numbered_lines = []
        
        for i, line in enumerate(lines):
            # Don't add line number to the last empty line if chunk ends with \n
            if i == len(lines) - 1 and line == '':
                numbered_lines.append(line)
            else:
                # Format with 6 digits, right-aligned, followed by: and space
                numbered_lines.append(f"{self.current_line_number:6d}: {line}")
                self.current_line_number += 1
        
        return '\n'.join(numbered_lines)

    def apply_line_wrap_setting(self):
        """Apply the current line wrap setting without saving to config"""
        try:
            if self.line_wrap_enabled:
                # Enable word wrapping
                try:
                    self.text_editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
                except (AttributeError, TypeError):
                    try:
                        self.text_editor.setLineWrapMode(QPlainTextEdit.WidgetWidth)
                    except (AttributeError, TypeError):
                        print("Warning: Could not enable line wrap mode.")
            else:
                # Disable word wrapping  
                try:
                    self.text_editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
                except (AttributeError, TypeError):
                    try:
                        self.text_editor.setLineWrapMode(QPlainTextEdit.NoWrap)
                    except (AttributeError, TypeError):
                        print("Warning: Could not disable line wrap mode.")
        except Exception as e:
            print(f"Error setting line wrap mode: {e}")
        
        # Update the menu action state if it exists
        if hasattr(self, 'line_wrap_action'):
            self.line_wrap_action.setChecked(self.line_wrap_enabled)
    
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
            
            # Update line wrap preference
            config['line_wrap_enabled'] = self.line_wrap_enabled
            
            # Update line numbers preference  
            config['line_numbers_enabled'] = self.line_numbers_enabled
            
            # Update bookmark highlight color
            config['bookmark_highlight_color'] = self.bookmark_highlight_color
            
            # Update case-sensitive search preference
            config['case_sensitive_search'] = self.case_sensitive_search
            
            # Update ANSI processing preference
            config['ansi_processing_enabled'] = self.ansi_processing_enabled
            
            # Save bookmarks (only for current file if available)
            if hasattr(self, 'current_file') and self.current_file and self.bookmarks:
                if 'bookmarks' not in config:
                    config['bookmarks'] = {}
                config['bookmarks'][self.current_file] = self.bookmarks
            
            # Preserve highlight terms if they exist
            if self.highlight_terms:
                config['highlight_terms'] = self.highlight_terms
            
            # Ensure config path is valid
            if not self.config_path:
                print("Warning: Config path is empty, using default")
                self.config_path = get_config_path()
            
            # Save config
            config_dir = os.path.dirname(self.config_path)
            if config_dir:  # Only create directory if path has a directory component
                os.makedirs(config_dir, exist_ok=True)
            
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
        
        # Prepare search term and text based on case sensitivity
        if self.case_sensitive_search:
            search_text = full_text
            term_to_find = search_term
        else:
            search_text = full_text.lower()
            term_to_find = search_term.lower()
        
        # Find all occurrences
        start = 0
        while True:
            pos = search_text.find(term_to_find, start)
            if pos == -1:
                break
            self.search_results.append(pos)
            start = pos + len(term_to_find)
        
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
            
            # Clear the formatting by removing all character formatting
            default_format = QTextCharFormat()
            # Don't set any colors - let the theme handle it
            cursor.setCharFormat(default_format)
            
            # Clear the stored positions
            self.current_highlight_start = None
            self.current_highlight_end = None
            
            # Trigger rehighlighting to restore config-based highlights
            self.highlighter.rehighlight()

    # Bookmark functionality
    def toggle_bookmark(self):
        """Toggle bookmark at current cursor position"""
        cursor = self.text_editor.textCursor()
        line_number = cursor.blockNumber() + 1  # Line numbers are 1-based
        self.toggle_bookmark_at_line(line_number)
    
    def toggle_bookmark_at_line(self, line_number):
        """Toggle bookmark at specific line number"""
        # Check if bookmark already exists at this line
        existing_bookmark = None
        for bookmark in self.bookmarks:
            if bookmark['line'] == line_number:
                existing_bookmark = bookmark
                break
        
        if existing_bookmark:
            # Remove existing bookmark
            self.bookmarks.remove(existing_bookmark)
            self.status_label.setText(f"Bookmark removed from line {line_number}")
        else:
            # Add new bookmark
            # Get line content for display purposes
            block = self.text_editor.document().findBlockByNumber(line_number - 1)
            line_content = block.text()[:50]  # First 50 characters as preview
            if len(block.text()) > 50:
                line_content += "..."
            
            bookmark = {
                'line': line_number,
                'content': line_content,
                'timestamp': time.time()
            }
            self.bookmarks.append(bookmark)
            # Sort bookmarks by line number
            self.bookmarks.sort(key=lambda x: x['line'])
            self.status_label.setText(f"Bookmark added at line {line_number}")
        
        # Update visual indicators
        self.update_bookmark_highlights()
    
    def next_bookmark(self):
        """Navigate to next bookmark"""
        if not self.bookmarks:
            self.status_label.setText("No bookmarks available")
            return
        
        current_line = self.text_editor.textCursor().blockNumber() + 1
        
        # Find next bookmark after current line
        next_bookmark = None
        for bookmark in self.bookmarks:
            if bookmark['line'] > current_line:
                next_bookmark = bookmark
                break
        
        # If no bookmark after current line, wrap to first bookmark
        if not next_bookmark:
            next_bookmark = self.bookmarks[0]
        
        self.goto_bookmark(next_bookmark)
    
    def prev_bookmark(self):
        """Navigate to previous bookmark"""
        if not self.bookmarks:
            self.status_label.setText("No bookmarks available")
            return
        
        current_line = self.text_editor.textCursor().blockNumber() + 1
        
        # Find previous bookmark before current line
        prev_bookmark = None
        for bookmark in reversed(self.bookmarks):
            if bookmark['line'] < current_line:
                prev_bookmark = bookmark
                break
        
        # If no bookmark before current line, wrap to last bookmark
        if not prev_bookmark:
            prev_bookmark = self.bookmarks[-1]
        
        self.goto_bookmark(prev_bookmark)
    
    def goto_bookmark(self, bookmark):
        """Navigate to a specific bookmark"""
        line_number = bookmark['line']
        
        # Move cursor to the bookmarked line
        cursor = self.text_editor.textCursor()
        
        # Go to the specific line (line_number - 1 because it's 0-based internally)
        block = self.text_editor.document().findBlockByNumber(line_number - 1)
        cursor.setPosition(block.position())
        
        # Set cursor and center the view
        self.text_editor.setTextCursor(cursor)
        self.text_editor.centerCursor()
        
        # Update status
        self.status_label.setText(f"Navigated to bookmark at line {line_number}: {bookmark['content']}")
    
    def list_bookmarks(self):
        """Show dialog with all bookmarks"""
        if not self.bookmarks:
            QMessageBox.information(self, "Bookmarks", "No bookmarks available.")
            return
        
        dialog = BookmarkListDialog(self, self.bookmarks)
        result = dialog.exec()
        
        # If user selected a bookmark, navigate to it
        if result == QDialog.DialogCode.Accepted and dialog.selected_bookmark:
            self.goto_bookmark(dialog.selected_bookmark)
    
    def clear_all_bookmarks(self):
        """Clear all bookmarks after confirmation"""
        if not self.bookmarks:
            self.status_label.setText("No bookmarks to clear")
            return
        
        reply = QMessageBox.question(self, "Clear Bookmarks", 
                                   f"Are you sure you want to clear all {len(self.bookmarks)} bookmarks?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.bookmarks.clear()
            self.update_bookmark_highlights()
            self.status_label.setText("All bookmarks cleared")
    
    def configure_bookmark_color(self):
        """Open color picker dialog to configure bookmark highlight color"""
        current_color = QColor(self.bookmark_highlight_color)
        color = QColorDialog.getColor(current_color, self, "Choose Bookmark Highlight Color")
        
        if color.isValid():
            # Update bookmark color
            self.bookmark_highlight_color = color.name()
            self.update_bookmark_highlight_format()
            
            # Update existing bookmarks with new color
            if self.bookmarks:
                self.update_bookmark_highlights()
            
            # Save configuration
            self.save_app_config()
            
            # Update status
            self.status_label.setText(f"Bookmark highlight color changed to {color.name()}")
    
    def update_bookmark_highlight_format(self):
        """Update the bookmark highlight format based on configured color"""
        color = QColor(self.bookmark_highlight_color)
        self.bookmark_highlight_format.setBackground(color)
        # Auto-select text color based on background brightness
        if color.lightness() > 128:
            self.bookmark_highlight_format.setForeground(QColor(0, 0, 0))  # Dark text
        else:
            self.bookmark_highlight_format.setForeground(QColor(255, 255, 255))  # Light text
        
        # Update highlighter if it exists
        if hasattr(self, 'highlighter'):
            self.highlighter.update_bookmark_format(self.bookmark_highlight_format)
    
    def update_bookmark_highlights(self):
        """Update visual highlighting for bookmarked lines"""
        if hasattr(self, 'highlighter'):
            # Extract line numbers from bookmarks
            bookmarked_lines = [bookmark['line'] for bookmark in self.bookmarks]
            self.highlighter.set_bookmarked_lines(bookmarked_lines)
    
    def load_bookmarks_for_current_file(self):
        """Load bookmarks for the currently open file"""
        if not hasattr(self, 'current_file') or not self.current_file:
            return
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
                    if 'bookmarks' in config and self.current_file in config['bookmarks']:
                        self.bookmarks = config['bookmarks'][self.current_file]
                        self.update_bookmark_highlights()
                        if self.bookmarks:
                            self.status_label.setText(f"Loaded {len(self.bookmarks)} bookmarks for this file")
        except Exception as e:
            print(f"Error loading bookmarks: {e}")

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
                    
                    # Load line wrap preference if present
                    if 'line_wrap_enabled' in config:
                        self.line_wrap_enabled = config['line_wrap_enabled']
                        # Apply the loaded line wrap setting
                        self.apply_line_wrap_setting()
                    
                    # Load line numbers preference if present
                    if 'line_numbers_enabled' in config:
                        self.line_numbers_enabled = config['line_numbers_enabled']
                    
                    # Load bookmark highlight color if present
                    if 'bookmark_highlight_color' in config:
                        self.bookmark_highlight_color = config['bookmark_highlight_color']
                        self.update_bookmark_highlight_format()
                    
                    # Load case-sensitive search preference if present
                    if 'case_sensitive_search' in config:
                        self.case_sensitive_search = config['case_sensitive_search']
                        # Update checkbox if it exists
                        if hasattr(self, 'case_sensitive_checkbox'):
                            self.case_sensitive_checkbox.setChecked(self.case_sensitive_search)
                    
                    # Load ANSI processing preference if present
                    if 'ansi_processing_enabled' in config:
                        self.ansi_processing_enabled = config['ansi_processing_enabled']
                        # Update menu action if it exists
                        if hasattr(self, 'ansi_processing_action'):
                            self.ansi_processing_action.setChecked(self.ansi_processing_enabled)
                    
                    # Load bookmarks for current file if present
                    if hasattr(self, 'current_file') and self.current_file and 'bookmarks' in config:
                        file_bookmarks = config['bookmarks'].get(self.current_file, [])
                        if file_bookmarks:
                            self.bookmarks = file_bookmarks
                            self.update_bookmark_highlights()
                    
                    # Display which config file was loaded
                    user_config_path = os.path.join(os.path.expanduser('~'), 'logviewer_config.yml')
                    if self.config_path == user_config_path:
                        self.status_label.setText("User default config loaded from ~/logviewer_config.yml")
                    else:
                        self.status_label.setText(f"Config loaded from {self.config_path}")
            else:
                # No configuration file found, use defaults
                self.status_label.setText("No configuration file found, using defaults")
                        
            # Ensure we always have a valid theme mode
            if not hasattr(self, 'current_theme_mode') or self.current_theme_mode is None:
                self.current_theme_mode = ThemeMode.SYSTEM
            
            # Apply the loaded (or default) theme
            self.apply_theme()
            
            # Update theme menu selection if it exists
            if hasattr(self, 'theme_actions'):
                for mode, action in self.theme_actions.items():
                    action.setChecked(mode == self.current_theme_mode)
            
            # Update line wrap menu action if it exists
            if hasattr(self, 'line_wrap_action'):
                self.line_wrap_action.setChecked(self.line_wrap_enabled)
                
            # Update line numbers menu action if it exists
            if hasattr(self, 'line_numbers_action'):
                self.line_numbers_action.setChecked(self.line_numbers_enabled)
                
            # Apply line wrap setting if text editor exists
            if hasattr(self, 'text_editor'):
                self.apply_line_wrap_setting()
                    
        except Exception as e:
            self.status_label.setText(f"Error loading config: {e}")
            print(f"Error loading config: {e}")
            # Apply default theme on error
            self.current_theme_mode = ThemeMode.SYSTEM
            self.apply_theme()

    def load_custom_config(self):
        # Start in user's home directory with focus on .yml files
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", 
            os.path.expanduser("~"),  # Start in user's home directory
            "YAML Files (*.yml *.yaml);;All Files (*)"
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
        
        # Clear previous bookmarks and reset line counter
        self.bookmarks.clear()
        self.current_line_number = 1
        
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
        # Append to the total content (always store original content)
        self.total_content += chunk
        
        # Process chunk with line numbers if enabled
        display_chunk = self.add_line_numbers_to_chunk(chunk)
        
        # Update the display with this chunk using proper ANSI processing
        self.text_editor.append_text(display_chunk)
        
        # Update status
        self.status_label.setText(f"Loading chunk {chunk_number}/{total_chunks}...")
    
    def on_loading_finished(self):
        """Handle completion of file loading"""
        self.loading_file = False
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"File loaded: {self.current_file}")
        
        # Apply highlighting after file is completely loaded
        safe_single_shot(100, self.load_config)
        
        # Load bookmarks for this file
        safe_single_shot(200, self.load_bookmarks_for_current_file)
        
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