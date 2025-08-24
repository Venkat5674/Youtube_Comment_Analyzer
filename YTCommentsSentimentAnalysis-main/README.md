# YouTube Comments Sentiment Analyzer

A Flask web application that fetches comments from YouTube videos, analyzes their sentiment using Google's Gemini AI, and exports the results to an Excel file.

## Features

- Fetch comments from any public YouTube video
- Classify comments as "Good" or "Bad" using Google's Gemini AI
- Export results to Excel file
- View sentiment statistics and analysis results in an interactive dashboard
- Filter comments by sentiment

## Prerequisites

- Python 3.8 or higher
- YouTube Data API v3 key
- Google Gemini API key

## Setup Instructions

1. Clone this repository:
   ```
   git clone <repository-url>
   cd YTCommentsSentimentAnalysis
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root directory with your API keys:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your web browser and navigate to `http://127.0.0.1:5000`

## How to Get API Keys

### YouTube Data API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the YouTube Data API v3
4. Create an API key
5. Copy the key to your `.env` file

### Gemini API Key
1. Go to [Google AI Studio](https://ai.google.dev/)
2. Create or sign in to your account
3. Navigate to API keys
4. Create a new API key
5. Copy the key to your `.env` file

## Usage

1. Enter a valid YouTube video URL in the input field
2. Specify the maximum number of comments to analyze (default is 100)
3. Click "Analyze Comments" button
4. View the sentiment analysis results
5. Download the Excel file with detailed results

## Tech Stack

- Flask: Web framework
- Google's Gemini AI: Sentiment analysis
- YouTube Data API v3: Fetching comments
- Pandas: Data processing and Excel export
- Bootstrap 5: Frontend styling

## License

This project is licensed under the MIT License - see the LICENSE file for details.