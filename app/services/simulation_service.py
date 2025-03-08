from typing import Dict, Optional, List
from datetime import datetime
from app.services.llm_service import LLMService
from app.core.logger import logger

class CallSimulation:
    def __init__(self, simulation_id: str):
        self.simulation_id = simulation_id
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.messages: List[Dict] = []
        self.is_active = True
        self.is_recording = False
        self.transferred_to = None
        self.transfer_reason = None
        self.notes: List[Dict] = []
        self.tags: List[Dict] = []
        self.status = "in-progress"
        self.quality_metrics = {
            "latency": 0,
            "packet_loss": 0,
            "jitter": 0,
            "quality_score": 100,
            "sentiment_score": 0,
            "resolution_time": 0
        }

class SimulationService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.active_simulations: Dict[str, CallSimulation] = {}
        self.available_agents = [
            {"id": "agent1", "name": "John Smith", "department": "Technical Support"},
            {"id": "agent2", "name": "Sarah Johnson", "department": "Billing"},
            {"id": "agent3", "name": "Mike Wilson", "department": "Customer Service"}
        ]

    def start_simulation(self, simulation_id: str) -> bool:
        """Start a new call simulation."""
        try:
            if simulation_id in self.active_simulations:
                return False
            
            self.active_simulations[simulation_id] = CallSimulation(simulation_id)
            logger.info(f"Started simulation {simulation_id}")
            return True
        except Exception as e:
            logger.error(f"Error starting simulation: {str(e)}")
            return False

    def end_simulation(self, simulation_id: str, reason: str = "completed") -> bool:
        """End an active call simulation."""
        try:
            simulation = self.active_simulations.get(simulation_id)
            if not simulation:
                return False
            
            simulation.is_active = False
            simulation.end_time = datetime.utcnow()
            simulation.status = reason
            logger.info(f"Ended simulation {simulation_id} with reason: {reason}")
            return True
        except Exception as e:
            logger.error(f"Error ending simulation: {str(e)}")
            return False

    async def process_message(self, simulation_id: str, message: str) -> Optional[str]:
        """Process a message in the simulation and get AI response."""
        try:
            simulation = self.active_simulations.get(simulation_id)
            if not simulation or not simulation.is_active:
                return None

            # Add user message to history
            simulation.messages.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Simulate network conditions and update metrics
            self._update_quality_metrics(simulation)
            self._analyze_sentiment(simulation, message)

            # Get AI response
            messages = [{"role": m["role"], "content": m["content"]} for m in simulation.messages]
            response = self.llm_service.get_response(messages)

            # Add AI response to history
            simulation.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.utcnow().isoformat()
            })

            return response
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return None

    def transfer_call(self, simulation_id: str, agent_id: str, reason: str) -> bool:
        """Transfer the call to another agent."""
        try:
            simulation = self.active_simulations.get(simulation_id)
            if not simulation or not simulation.is_active:
                return False

            agent = next((a for a in self.available_agents if a["id"] == agent_id), None)
            if not agent:
                return False

            simulation.transferred_to = agent
            simulation.transfer_reason = reason
            simulation.status = "transferred"
            
            # Add transfer note
            self.add_note(simulation_id, f"Call transferred to {agent['name']} ({agent['department']}) - Reason: {reason}")
            
            return True
        except Exception as e:
            logger.error(f"Error transferring call: {str(e)}")
            return False

    def add_note(self, simulation_id: str, content: str) -> bool:
        """Add a note to the call."""
        try:
            simulation = self.active_simulations.get(simulation_id)
            if not simulation:
                return False

            simulation.notes.append({
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })
            return True
        except Exception as e:
            logger.error(f"Error adding note: {str(e)}")
            return False

    def add_tag(self, simulation_id: str, tag_name: str, tag_type: str = "default") -> bool:
        """Add a tag to the call."""
        try:
            simulation = self.active_simulations.get(simulation_id)
            if not simulation:
                return False

            simulation.tags.append({
                "name": tag_name,
                "type": tag_type,
                "timestamp": datetime.utcnow().isoformat()
            })
            return True
        except Exception as e:
            logger.error(f"Error adding tag: {str(e)}")
            return False

    def get_simulation_details(self, simulation_id: str) -> Optional[Dict]:
        """Get details about a simulation."""
        try:
            simulation = self.active_simulations.get(simulation_id)
            if not simulation:
                return None

            duration = None
            if simulation.end_time:
                duration = (simulation.end_time - simulation.start_time).seconds
            elif simulation.is_active:
                duration = (datetime.utcnow() - simulation.start_time).seconds

            return {
                "simulation_id": simulation.simulation_id,
                "start_time": simulation.start_time.isoformat(),
                "end_time": simulation.end_time.isoformat() if simulation.end_time else None,
                "duration": duration,
                "is_active": simulation.is_active,
                "is_recording": simulation.is_recording,
                "status": simulation.status,
                "transferred_to": simulation.transferred_to,
                "transfer_reason": simulation.transfer_reason,
                "message_count": len(simulation.messages),
                "quality_metrics": simulation.quality_metrics,
                "messages": simulation.messages,
                "notes": simulation.notes,
                "tags": simulation.tags
            }
        except Exception as e:
            logger.error(f"Error getting simulation details: {str(e)}")
            return None

    def toggle_recording(self, simulation_id: str) -> bool:
        """Toggle call recording status."""
        try:
            simulation = self.active_simulations.get(simulation_id)
            if not simulation or not simulation.is_active:
                return False

            simulation.is_recording = not simulation.is_recording
            return simulation.is_recording
        except Exception as e:
            logger.error(f"Error toggling recording: {str(e)}")
            return False

    def _update_quality_metrics(self, simulation: CallSimulation) -> None:
        """Update simulated call quality metrics."""
        try:
            import random
            
            # Simulate network conditions
            simulation.quality_metrics["latency"] = random.uniform(10, 100)
            simulation.quality_metrics["packet_loss"] = random.uniform(0, 2)
            simulation.quality_metrics["jitter"] = random.uniform(0, 20)
            
            # Calculate quality score
            latency_score = max(0, 100 - simulation.quality_metrics["latency"])
            packet_loss_score = max(0, 100 - (simulation.quality_metrics["packet_loss"] * 50))
            jitter_score = max(0, 100 - (simulation.quality_metrics["jitter"] * 5))
            
            simulation.quality_metrics["quality_score"] = (
                latency_score * 0.4 +
                packet_loss_score * 0.4 +
                jitter_score * 0.2
            )

            # Update resolution time
            if simulation.end_time:
                simulation.quality_metrics["resolution_time"] = (
                    simulation.end_time - simulation.start_time
                ).seconds
        except Exception as e:
            logger.error(f"Error updating quality metrics: {str(e)}")
            simulation.quality_metrics["quality_score"] = 100

    def _analyze_sentiment(self, simulation: CallSimulation, message: str) -> None:
        """Analyze message sentiment and update metrics."""
        try:
            # Simple sentiment analysis (replace with more sophisticated analysis if needed)
            positive_words = ["happy", "great", "excellent", "good", "thanks", "helpful"]
            negative_words = ["bad", "poor", "terrible", "unhappy", "frustrated", "angry"]
            
            words = message.lower().split()
            positive_count = sum(1 for w in words if w in positive_words)
            negative_count = sum(1 for w in words if w in negative_words)
            
            if positive_count + negative_count > 0:
                sentiment = (positive_count - negative_count) / (positive_count + negative_count)
                # Convert to 0-100 scale
                simulation.quality_metrics["sentiment_score"] = (sentiment + 1) * 50
            else:
                simulation.quality_metrics["sentiment_score"] = 50
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            simulation.quality_metrics["sentiment_score"] = 50 