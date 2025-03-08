from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import Call, Message
from app.core.logger import logger

class AnalyticsService:
    @staticmethod
    def get_call_statistics(db: Session) -> Dict[str, Any]:
        """Get general call statistics."""
        try:
            total_calls = db.query(Call).count()
            avg_duration = db.query(func.avg(Call.duration)).scalar() or 0
            total_messages = db.query(Message).count()
            
            return {
                "total_calls": total_calls,
                "average_duration": round(float(avg_duration), 2),
                "total_messages": total_messages
            }
        except Exception as e:
            logger.error(f"Error getting call statistics: {str(e)}")
            return {}
    
    @staticmethod
    def get_call_history(db: Session, call_id: int) -> Dict[str, Any]:
        """Get detailed history for a specific call."""
        try:
            call = db.query(Call).filter(Call.id == call_id).first()
            if not call:
                return {}
            
            messages = db.query(Message).filter(Message.call_id == call_id).all()
            
            return {
                "call_details": {
                    "from": call.from_number,
                    "to": call.to_number,
                    "duration": call.duration,
                    "status": call.status,
                    "created_at": call.created_at.isoformat()
                },
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.created_at.isoformat()
                    }
                    for msg in messages
                ]
            }
        except Exception as e:
            logger.error(f"Error getting call history: {str(e)}")
            return {}
    
    @staticmethod
    def analyze_conversation(messages: List[Message]) -> Dict[str, Any]:
        """Analyze conversation patterns and metrics."""
        try:
            user_messages = [msg for msg in messages if msg.role == "user"]
            assistant_messages = [msg for msg in messages if msg.role == "assistant"]
            
            return {
                "message_count": {
                    "user": len(user_messages),
                    "assistant": len(assistant_messages)
                },
                "average_response_length": {
                    "user": sum(len(msg.content) for msg in user_messages) / len(user_messages) if user_messages else 0,
                    "assistant": sum(len(msg.content) for msg in assistant_messages) / len(assistant_messages) if assistant_messages else 0
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing conversation: {str(e)}")
            return {} 