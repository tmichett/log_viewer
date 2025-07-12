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

### Configuration Files
- Default configuration: `config.yml` in the application directory
- Custom configurations: Load different configs for different log types
- YAML format with terms and optional colors

### Example Configuration
```yaml
highlight_terms:
  - term: "ERROR"
    color: "#ff0000"
  - term: "WARNING"
    color: "#ffff00"
  - "INFO"  # Uses default color
```

## User Interface

### Font Size
- Use "+" and "-" buttons to adjust text size
- Range: 6pt to 72pt
- Changes apply immediately

### Dark Theme
- Application uses a dark theme optimized for log viewing
- High contrast for better readability
- Consistent styling across all dialogs

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
- **Email**: tmichett@redhat.com
- **Organization**: Michette Technologies

## Version Information

This help system is for Log Viewer Application version 2.0.0. 