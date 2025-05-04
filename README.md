# Log Viewer

A simple log file viewer with highlighting functionality based on configurable terms.

## Features

- Open and view any text file
- Highlight lines containing specified terms
- Configurable highlight terms through config.yml
- Case-insensitive term matching
- Light blue highlighting for matched lines

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the highlight terms in `config.yml`:
```yaml
highlight_terms:
  - warn
  - err
  - fatal
  - alert
  - fail
```

## Usage

1. Run the application:
```bash
python log_viewer.py
```

2. Click the "Open Log File" button to select a log file
3. The application will automatically highlight any lines containing the terms specified in config.yml

## Configuration

Edit the `config.yml` file to add or remove terms to highlight. The format is:
```yaml
highlight_terms:
  - term1
  - term2
  - term3
``` # log_viewer
