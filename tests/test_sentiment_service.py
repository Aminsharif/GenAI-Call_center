import pytest
from app.services.sentiment_service import SentimentService

@pytest.fixture
def sentiment_service():
    return SentimentService()

def test_analyze_text_positive(sentiment_service):
    text = "I'm really happy with the excellent service!"
    result = sentiment_service.analyze_text(text)
    assert result["compound"] > 0
    assert result["pos"] > result["neg"]

def test_analyze_text_negative(sentiment_service):
    text = "This is terrible, I'm very disappointed."
    result = sentiment_service.analyze_text(text)
    assert result["compound"] < 0
    assert result["neg"] > result["pos"]

def test_analyze_text_neutral(sentiment_service):
    text = "The call is being transferred."
    result = sentiment_service.analyze_text(text)
    assert abs(result["compound"]) < 0.05
    assert result["neu"] > result["pos"] and result["neu"] > result["neg"]

def test_get_sentiment_label(sentiment_service):
    assert sentiment_service.get_sentiment_label(0.5) == "positive"
    assert sentiment_service.get_sentiment_label(-0.5) == "negative"
    assert sentiment_service.get_sentiment_label(0.0) == "neutral"

def test_analyze_conversation(sentiment_service):
    messages = [
        {"role": "user", "content": "I'm very happy with the service!"},
        {"role": "assistant", "content": "I'm glad you're satisfied."},
        {"role": "user", "content": "Everything works perfectly."}
    ]
    
    result = sentiment_service.analyze_conversation(messages)
    assert "overall_sentiment" in result
    assert "sentiment_scores" in result
    assert result["overall_sentiment"] == "positive"
    assert result["sentiment_scores"]["pos"] > result["sentiment_scores"]["neg"]

def test_analyze_empty_conversation(sentiment_service):
    messages = []
    result = sentiment_service.analyze_conversation(messages)
    assert result["overall_sentiment"] == "neutral"
    assert result["sentiment_scores"]["neu"] == 1
    assert result["sentiment_scores"]["pos"] == 0
    assert result["sentiment_scores"]["neg"] == 0 