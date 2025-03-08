from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from typing import Optional

class TwilioService:
    def __init__(self, account_sid: str, auth_token: str, phone_number: str):
        self.client = Client(account_sid, auth_token)
        self.phone_number = phone_number
        
    def create_twiml_response(self, message: Optional[str] = None) -> str:
        """
        Create a TwiML response for Twilio.
        
        Args:
            message: Optional message to speak
            
        Returns:
            str: TwiML response
        """
        response = VoiceResponse()
        
        if message:
            response.say(message)
            
        # Gather speech input
        gather = Gather(
            input='speech',
            action='/api/voice/process-speech',
            method='POST',
            language='en-US',
            speechTimeout='auto'
        )
        
        gather.say("Please speak after the tone.")
        response.append(gather)
        
        # Add a fallback message
        response.say("I didn't catch that. Please try again.")
        response.redirect('/api/voice/handle-call')
        
        return str(response)
        
    def make_call(self, to_number: str) -> str:
        """
        Initiate a call to a phone number.
        
        Args:
            to_number: The phone number to call
            
        Returns:
            str: Call SID
        """
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url='http://your-domain.com/api/voice/handle-call'  # Replace with your domain
            )
            return call.sid
        except Exception as e:
            print(f"Error making call: {str(e)}")
            return "" 