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
3. Choose custom colors for each term
4. Save configurations for reuse

### Managing Highlight Terms
- **Add**: Click "Add Term" and enter the text to highlight
- **Edit**: Select a term and click "Edit Term" to modify it
- **Remove**: Select a term and click "Remove Term" to delete it
- **Colors**: Use the color picker to choose highlight colors

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
  - term: "ERROR"
    color: "#ff0000"
  - term: "WARNING"
    color: "#ffff00"
  - "INFO"  # Uses default color
theme: "system"  # Options: system, light, dark
line_wrap_enabled: false
```

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
- **Highlighting not showing**: Check configuration file format
- **Application won't start**: Verify Python and PyQt6 installation

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

### Color Customization
- Custom colors for each highlight term
- Color picker interface for easy selection
- Automatic text color adjustment based on background

## Support

For additional help or to report issues:
- **Email**: travis@michettetech.com
- **Organization**: Michette Technologies

## Version Information

This help system is for Log Viewer Application. 