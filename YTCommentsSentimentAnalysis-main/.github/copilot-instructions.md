# YouTube Comments Sentiment Analyzer

This is a Flask web application that fetches comments from YouTube videos, analyzes their sentiment using Google's Gemini AI, and exports the results to an Excel file.

## Project Structure
- `app.py`: Main Flask application
- `templates/`: HTML templates
  - `index.html`: Home page with form to input YouTube URL
  - `results.html`: Page showing analysis results
- `static/`: Directory for static files and generated Excel files
- `requirements.txt`: Python dependencies

## Development Notes
- Uses Flask for the web framework
- Fetches YouTube comments using the YouTube Data API
- Analyzes sentiment using Google's Gemini AI (1.5 Flash version)
- Exports results to an Excel file using pandas and openpyxl
- Uses Bootstrap for UI styling

## API Requirements
- YouTube Data API key
- Google Gemini API key (stored in `.env` file)

## Features
- Fetch comments from any public YouTube video
- Classify comments as "Good" or "Bad" using Google's Gemini AI
- Export results to Excel file
- View sentiment statistics and analysis results