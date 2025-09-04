# Log Viewer Help

## Getting Started

### Opening Files
- **Open File Button**: Click "Open Log File" to browse and select a file
- **Command Line**: Run `log_viewer /path/to/file.log` to open a specific file
- **Supported Formats**: .log, .out, .txt, and other text files

### Basic Navigation
- **Scroll**: Use mouse wheel or scrollbar to navigate through the file
- **Home/End**: Jump to beginning or end of file
- **Page Up/Down**: Navigate by pages

## Search Functionality

### Basic Search
1. Type your search term in the search box
2. Press Enter or click "Find" to start searching
3. Use "Find Next" and "Find Previous" to navigate through results
4. The entire line containing your search term will be highlighted in yellow

### Search Tips
- Search is case-insensitive
- Use specific terms to reduce result sets
- The status bar shows current match position and total matches
- Search results are cached for fast navigation

## Text Highlighting

### Configurable Highlighting
1. Click "Configure Highlighting" button
2. Add terms you want to highlight in log files
3. Customize formatting with multiple options:
   - **Background Color**: Choose highlight background color
   - **Text Color**: Set custom text color or use automatic selection
   - **Bold Formatting**: Make highlighted text bold for emphasis
4. Save configurations for reuse

### Managing Highlight Terms
- **Add**: Click "Add Term" to open the Term Formatting dialog
- **Edit**: Select a term and click "Edit Term" to modify formatting
- **Remove**: Select a term and click "Remove Term" to delete it

### Term Formatting Dialog
The enhanced formatting dialog provides complete control over text appearance:
- **Term**: Enter the text to highlight
- **Background Color**: Multiple selection options:
  - **Smart Colors**: Dropdown with intelligent color suggestions:
    - **Auto**: Automatically selects color based on term content (e.g., red for "ERROR", orange for "WARNING")
    - **Error**: Red background for error-related terms
    - **Warning**: Orange background for warning-related terms
    - **Info**: Blue background for informational terms
    - **Success**: Green background for success-related terms
    - **Debug**: Gray background for debug/trace terms
  - **Custom Color**: Choose any color using the color picker
- **Text Color**: 
  - Select custom text color with color picker
  - Use "Auto" for automatic color selection based on background brightness
- **Bold Text**: Check to make highlighted text bold
- **Preview**: Buttons show live preview of your formatting choices
- **Smart Suggestions**: As you type the term, the "Auto" option updates to show the suggested color

### Formatting Priority
- Custom text color overrides automatic color selection
- Automatic selection chooses black or white text based on background lightness
- Bold formatting applies independently of color choices

### Common Formatting Examples
#### Using Smart Colors
- **Error Messages**: Use "Error" preset (red background) + auto text + bold
- **Warnings**: Use "Warning" preset (orange background) + auto text
- **Success Messages**: Use "Success" preset (green background) + auto text + bold
- **Information**: Use "Info" preset (blue background) + auto text
- **Debug Output**: Use "Debug" preset (gray background) + auto text
- **Auto Detection**: Type "ERROR", "WARNING", etc., and use "Auto" for intelligent color selection

#### Using Custom Colors
- **Critical Issues**: Custom dark red background + auto text color + bold for urgency
- **Status Updates**: Custom text colors to categorize different types of status messages
- **Department Codes**: Custom colors to match organizational color schemes
- **Severity Levels**: Gradient of colors from green (low) to red (high) severity

## Configuration

### Configuration Precedence
Log Viewer loads configuration files in the following order of precedence:
1. **Command Line Config** (Highest Priority): `log_viewer --config /path/to/config.yml`
2. **User Default Config**: `~/logviewer_config.yml` (in your home directory)
3. **Platform-Specific Config** (Lowest Priority): See platform sections

### Creating a User Default Config
To create a personal configuration that applies to all Log Viewer sessions:
1. Open the Configuration Dialog ("Configure Highlighting" button)
2. Set up your preferred highlight terms and colors
3. Click "Save Config" - it will default to `~/logviewer_config.yml`
4. Your settings will automatically load in future sessions

### Configuration Structure
```yaml
highlight_terms:
  # Simple terms (backward compatible)
  - "INFO"      # Uses default formatting
  - "DEBUG"     # Uses default formatting
  
  # Enhanced formatting with full control
  - term: "ERROR"
    color: "#FF0000"        # Red background
    text_color: "#FFFFFF"   # White text
    bold: true              # Bold formatting
  
  - term: "WARNING"
    color: "#FFAA00"        # Orange background
    text_color: "#000000"   # Black text
    bold: false             # Normal weight
  
  - term: "CRITICAL"
    color: "#800000"        # Dark red background
    bold: true              # Bold with auto text color
  
  - term: "SUCCESS"
    text_color: "#00FF00"   # Green text only (no background)
    bold: true

theme: "system"               # Options: system, light, dark
line_wrap_enabled: false
line_numbers_enabled: false
bookmark_highlight_color: "#64C8FF"  # Bookmark highlight color
```

### Configuration Properties
- **term**: The text to highlight (required for enhanced format)
- **color**: Background color as hex code (optional, defaults to cornflower blue)
- **text_color**: Text color as hex code (optional, auto-selects based on background if not specified)
- **bold**: Boolean for bold text formatting (optional, defaults to false)
- **Simple format**: Just the term string for default highlighting (backward compatible)

## User Interface

### Font Size
- Use "+" and "-" buttons to adjust text size
- Range: 6pt to 72pt
- Changes apply immediately

### Themes and Display
#### Theme Options
- **System Theme**: Automatically matches your operating system theme
- **Light Theme**: Light background with dark text  
- **Dark Theme**: Dark background optimized for log viewing

#### Changing Themes
1. Go to **View** → **Theme** in the menu bar
2. Select your preferred theme option
3. The theme will change immediately and be saved to your configuration

#### Line Wrapping
- Toggle line wrapping using **View** → **Line Wrap**
- When enabled, long lines will wrap to fit the window width
- When disabled, long lines extend horizontally with a scrollbar

#### Line Numbers
- Toggle line numbers using **View** → **Line Numbers**
- When enabled, each line displays with a right-aligned line number (e.g., "     1: content")
- Line numbers help with navigation and reference when discussing log contents
- Setting is automatically saved to your configuration file
- Can be toggled while viewing files - display refreshes automatically

## Bookmarks

### Overview
Bookmarks allow you to mark important lines in log files for quick navigation and reference. Each bookmark stores the line number, content preview, and creation timestamp.

### Adding Bookmarks
- **Keyboard**: Place cursor on desired line and press **Ctrl+B**
- **Menu**: **Bookmarks** → **Toggle Bookmark**
- **Right-click**: Context menu → **Add Bookmark**

### Navigating Bookmarks
- **Next Bookmark**: Press **F2** or use **Bookmarks** → **Next Bookmark**
- **Previous Bookmark**: Press **Shift+F2** or use **Bookmarks** → **Previous Bookmark**
- **List All**: Press **Ctrl+Shift+B** or use **Bookmarks** → **List All Bookmarks**

### Bookmark Management
#### List All Bookmarks Dialog
- View all bookmarks with line numbers and content previews
- Double-click any bookmark to navigate directly to that line
- Use "Delete" button to remove individual bookmarks
- Use "Go To" button to navigate to selected bookmark

#### Removing Bookmarks
- **Toggle off**: Use **Ctrl+B** on a bookmarked line to remove the bookmark
- **Context menu**: Right-click on bookmarked line → **Remove Bookmark**
- **Clear all**: **Bookmarks** → **Clear All Bookmarks** (requires confirmation)

### Visual Indicators
- Bookmarked lines are highlighted with a light blue background
- Bookmark highlighting takes priority over other highlighting (search, syntax)
- Visual indicators update immediately when bookmarks are added or removed

### Customization
#### Configure Bookmark Color
- Use **Bookmarks** → **Configure Bookmark Color** to customize the highlight color
- Choose any color using the color picker dialog
- Text color automatically adjusts (black/white) based on background brightness
- Color preference is saved to your configuration file
- Changes apply immediately to all existing bookmarks

### Configuration File
Bookmark color can be configured in your YAML configuration file:
```yaml
bookmark_highlight_color: "#64C8FF"  # Light blue (default)
# Other color examples:
# bookmark_highlight_color: "#FFD700"  # Gold
# bookmark_highlight_color: "#98FB98"  # Pale green
# bookmark_highlight_color: "#FFB6C1"  # Light pink
```

### Persistence
- Bookmarks are automatically saved to your configuration file
- Each file maintains its own set of bookmarks
- Bookmarks are restored when you reopen a file
- Bookmarks survive application restarts
- Bookmark color preference persists across sessions

## Performance

### Large Files
- Files are loaded in chunks to prevent UI freezing
- Progress bar shows loading status
- Memory usage is optimized for large files

### Search Performance
- Search results are cached for fast navigation
- Debounced search prevents excessive operations
- Efficient text scanning algorithms

## Keyboard Shortcuts

### File Operations
- **Ctrl+O**: Open file
- **Ctrl+Q**: Quit application

### Search Operations
- **Ctrl+F**: Focus search box
- **Enter**: Find first/next
- **F3**: Find next
- **Shift+F3**: Find previous
- **Escape**: Clear search

### Navigation
- **Home**: Go to beginning of file
- **End**: Go to end of file
- **Ctrl+Home**: Go to very beginning
- **Ctrl+End**: Go to very end
- **Page Up/Down**: Navigate by pages

### Bookmark Operations
- **Ctrl+B**: Toggle bookmark at current line
- **F2**: Navigate to next bookmark
- **Shift+F2**: Navigate to previous bookmark
- **Ctrl+Shift+B**: List all bookmarks

## File Formats

### Supported Formats
- **Log files**: .log, .out, .txt
- **Any text file**: The application can open any text-based file
- **Large files**: Optimized for files of any size

### ANSI Color Support
- Parses ANSI escape sequences
- Displays colors as intended in the original logs
- Maintains formatting and color information

## Troubleshooting

### Common Issues
- **Slow loading**: Normal for very large files - wait for progress to complete
- **Search not working**: Ensure file is fully loaded before searching
- **Highlighting not showing**: Check configuration file format and ensure terms match exactly
- **Application won't start**: Verify Python and PyQt6 installation
- **Bold checkbox not clickable**: Ensure you're using the latest version with enhanced dark mode support
- **Text color not applying**: Check that text_color property is properly formatted as hex code (e.g., "#FF0000")
- **Configuration not saving**: Ensure you have write permissions to the configuration directory
- **Colors too similar**: Use sufficient contrast between background and text colors for readability

### Performance Tips
- Close other applications when viewing very large files
- Use specific search terms to reduce result sets
- Consider the configuration system to highlight only relevant terms
- Allow time for large files to load completely

## Advanced Features

### Command Line Options
```bash
# Open specific file
log_viewer /path/to/file.log

# Use custom configuration
log_viewer --config /path/to/config.yml /path/to/file.log
```

### Configuration Management
- Save multiple configurations for different log types
- Load configurations through the GUI
- Share configurations across team members

### Advanced Formatting Options
- **Background Colors**: Custom background colors for each highlight term
- **Text Colors**: Independent text color control with color picker interface
- **Bold Formatting**: Toggle bold styling for enhanced visibility
- **Automatic Text Color**: Intelligent black/white text selection based on background brightness
- **Mixed Formatting**: Combine background color, text color, and bold formatting
- **Text-Only Highlighting**: Apply text color and bold formatting without background color
- **Live Preview**: Buttons show real-time preview of formatting choices

## Support

For additional help or to report issues:
- **Email**: travis@michettetech.com
- **Organization**: Michette Technologies

## Version Information

This help system is for Log Viewer Application. 