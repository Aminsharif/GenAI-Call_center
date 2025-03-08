from typing import Dict, List
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from app.core.logger import logger

class SentimentService:
    def __init__(self):
        try:
            nltk.download('vader_lexicon', quiet=True)
            self.analyzer = SentimentIntensityAnalyzer()
        except Exception as e:
            logger.error(f"Error initializing sentiment analyzer: {str(e)}")
            self.analyzer = None

    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze the sentiment of a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with sentiment scores (pos, neg, neu, compound)
        """
        try:
            if not self.analyzer:
                return {"pos": 0, "neg": 0, "neu": 1, "compound": 0}
            
            return self.analyzer.polarity_scores(text)
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {"pos": 0, "neg": 0, "neu": 1, "compound": 0}

    def get_sentiment_label(self, compound_score: float) -> str:
        """
        Get a sentiment label based on the compound score.
        
        Args:
            compound_score: The compound sentiment score
            
        Returns:
            str: Sentiment label (positive, neutral, negative)
        """
        if compound_score >= 0.05:
            return "positive"
        elif compound_score <= -0.05:
            return "negative"
        else:
            return "neutral"

    def analyze_conversation(self, messages: List[Dict[str, str]]) -> Dict[str, any]:
        """
        Analyze the sentiment of an entire conversation.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Dict with overall sentiment metrics
        """
        try:
            user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
            
            if not user_messages:
                return {
                    "overall_sentiment": "neutral",
                    "sentiment_scores": {"pos": 0, "neg": 0, "neu": 1, "compound": 0}
                }
            
            # Analyze each message
            sentiments = [self.analyze_text(msg) for msg in user_messages]
            
            # Calculate average scores
            avg_scores = {
                "pos": sum(s["pos"] for s in sentiments) / len(sentiments),
                "neg": sum(s["neg"] for s in sentiments) / len(sentiments),
                "neu": sum(s["neu"] for s in sentiments) / len(sentiments),
                "compound": sum(s["compound"] for s in sentiments) / len(sentiments)
            }
            
            return {
                "overall_sentiment": self.get_sentiment_label(avg_scores["compound"]),
                "sentiment_scores": avg_scores
            }
        except Exception as e:
            logger.error(f"Error analyzing conversation sentiment: {str(e)}")
            return {
                "overall_sentiment": "neutral",
                "sentiment_scores": {"pos": 0, "neg": 0, "neu": 1, "compound": 0}
            } 