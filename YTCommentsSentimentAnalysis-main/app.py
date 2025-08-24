import os
import pandas as pd
import google.generativeai as genai
from flask import Flask, render_template, request, send_file
from googleapiclient.discovery import build
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure API keys
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API with error handling
model = None
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini API configured successfully")
except Exception as e:
    print(f"Error configuring Gemini API: {str(e)}")
    print("The application will use fallback keyword-based sentiment analysis")

def extract_video_id(youtube_url):
    """Extract YouTube video ID from URL"""
    # Regular expression pattern for YouTube URLs
    patterns = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=([^&]+)',
        r'^https?://(?:www\.)?youtu\.be/([^?]+)',
        r'^https?://(?:www\.)?youtube\.com/embed/([^?]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    return None

def get_youtube_comments(video_id, max_results=100):
    """Fetch comments from a YouTube video"""
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    comments = []
    next_page_token = None
    
    # Fetch comments with pagination
    while len(comments) < max_results:
        # Get the comments for the video
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=min(100, max_results - len(comments)),
            pageToken=next_page_token
        ).execute()
        
        # Process comments from current page
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'author': comment['authorDisplayName'],
                'text': comment['textDisplay'],
                'likes': comment['likeCount'],
                'published_at': comment['publishedAt']
            })
        
        # Check if there are more pages
        next_page_token = response.get('nextPageToken')
        if not next_page_token or len(comments) >= max_results:
            break
    
    return comments

def keyword_based_sentiment(comment):
    """Simple keyword-based sentiment analysis"""
    comment_lower = comment.lower()
    
    # Define positive and negative keywords
    positive_keywords = [
        'good', 'great', 'awesome', 'excellent', 'amazing', 'love', 'best',
        'nice', 'fantastic', 'wonderful', 'brilliant', 'perfect', 'thank', 
        'thanks', 'helpful', 'beautiful', 'enjoyed', 'like', 'recommend'
    ]
    
    negative_keywords = [
        'bad', 'terrible', 'awful', 'worst', 'hate', 'poor', 'waste',
        'disappointed', 'disappointing', 'horrible', 'useless', 'dislike',
        'unfortunately', 'boring', 'stupid', 'not good', 'sucks', 'wrong'
    ]
    
    # Count occurrences of positive and negative keywords
    positive_count = sum(1 for keyword in positive_keywords if keyword in comment_lower)
    negative_count = sum(1 for keyword in negative_keywords if keyword in comment_lower)
    
    # Determine sentiment based on keyword counts
    if positive_count > negative_count:
        return "Good"
    elif negative_count > positive_count:
        return "Bad"
    else:
        return "Neutral"

def analyze_sentiment(comment):
    """Analyze sentiment of a comment using Gemini AI with fallback mechanism"""
    # If model is None, it means Gemini API could not be configured
    if model is None:
        return keyword_based_sentiment(comment)
        
    try:
        # Try using Gemini AI
        prompt = f"""
        Analyze the sentiment of this YouTube comment and classify it as either 'Good' or 'Bad'.
        Return ONLY 'Good' or 'Bad' without any other text.
        
        Comment: {comment}
        """
        
        response = model.generate_content(prompt)
        sentiment = response.text.strip()
        
        # Ensure output is either "Good" or "Bad"
        if sentiment.lower() not in ["good", "bad"]:
            # Default to "Neutral" if the model doesn't return a clear result
            return "Neutral"
        
        return sentiment
        
    except Exception as e:
        # Log the error
        print(f"Gemini API error: {str(e)}")
        
        # Use the fallback mechanism
        return keyword_based_sentiment(comment)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # If Gemini API is not available, show a warning on the index page
        gemini_warning = None
        if model is None:
            gemini_warning = "Gemini API is not available (quota exceeded). The application will use keyword-based sentiment analysis."
        return render_template('index.html', gemini_warning=gemini_warning)
    
    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url')
        max_comments = int(request.form.get('max_comments', 100))
        use_fallback = request.form.get('use_fallback') == 'on'
        
        # If model is None (API not available), force fallback
        if model is None:
            use_fallback = True
        
        # Extract video ID from URL
        video_id = extract_video_id(youtube_url)
        
        if not video_id:
            return render_template('index.html', error="Invalid YouTube URL")
        
        try:
            # Get comments
            comments = get_youtube_comments(video_id, max_results=max_comments)
            
            # Analyze comments
            results = []
            api_error = None
            
            for comment in comments:
                try:
                    # If using fallback is requested or we've already encountered an API error, use fallback
                    if use_fallback:
                        # Use the keyword-based sentiment analysis
                        sentiment = keyword_based_sentiment(comment['text'])
                    else:
                        # Use normal Gemini-based sentiment analysis
                        sentiment = analyze_sentiment(comment['text'])
                    
                    comment['sentiment'] = sentiment
                    results.append(comment)
                    
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        api_error = "API quota exceeded. Using fallback sentiment analysis method."
                        # Switch to fallback method for remaining comments
                        use_fallback = True
                        # Process current comment with fallback
                        sentiment = keyword_based_sentiment(comment['text'])
                        comment['sentiment'] = sentiment
                        results.append(comment)
                    else:
                        # For other errors, just mark as neutral and continue
                        comment['sentiment'] = "Neutral"
                        results.append(comment)
            
            # Create DataFrame and export to Excel
            df = pd.DataFrame(results)
            excel_path = os.path.join('static', 'youtube_comments.xlsx')
            df.to_excel(excel_path, index=False)
            
            # Calculate statistics
            total = len(results)
            good = sum(1 for c in results if c['sentiment'].lower() == 'good')
            bad = sum(1 for c in results if c['sentiment'].lower() == 'bad')
            neutral = total - good - bad
            
            stats = {
                'total': total,
                'good': good,
                'bad': bad,
                'neutral': neutral,
                'good_percent': round(good/total*100, 1) if total > 0 else 0,
                'bad_percent': round(bad/total*100, 1) if total > 0 else 0,
                'neutral_percent': round(neutral/total*100, 1) if total > 0 else 0
            }
            
            # Determine which analysis method was used
            analysis_method = "keyword-based" if use_fallback or model is None else "Gemini AI"
            
            return render_template('results.html', 
                                  comments=results, 
                                  stats=stats, 
                                  excel_file='youtube_comments.xlsx',
                                  api_error=api_error,
                                  used_fallback=use_fallback,
                                  analysis_method=analysis_method)
            
        except Exception as e:
            return render_template('index.html', error=f"Error: {str(e)}")
    
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join('static', filename), as_attachment=True)

if __name__ == '__main__':
    # Create static folder if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)