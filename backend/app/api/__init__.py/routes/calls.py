from fastapi import APIRouter, Request, Response
from app.services.twilio_service import TwilioService
from app.services.conversation_manager import ConversationManager
from app.services.deepgram_service import DeepgramService

twilio_router = APIRouter()

@twilio_router.post("/voice")
async def twilio_voice_webhook(request: Request):
    """
    Handle incoming Twilio voice call webhook
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    from_number = form_data.get("From")
    to_number = form_data.get("To")
    
    # Find the user and configuration based on the Twilio number
    # Implementation would look up user_id and config
    
    # Initialize Twilio service
    twilio_service = TwilioService()
    
    # Generate TwiML response
    twiml = twilio_service.handle_incoming_call(call_sid, from_number, to_number)
    
    return Response(content=twiml, media_type="application/xml")

@twilio_router.post("/speech")
async def twilio_speech_webhook(request: Request):
    """
    Handle Twilio speech recognition webhook
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    speech_result = form_data.get("SpeechResult")
    
    # Find user_id and knowledge_base_id for this call
    # Implementation would lookup this information
    
    # Initialize conversation manager
    conversation_manager = ConversationManager(
        call_sid=call_sid,
        user_id="user_id_here",
        knowledge_base_id="knowledge_base_id_here"
    )
    
    # Process user input
    response = await conversation_manager.process_user_input(speech_result)
    
    # Generate TwiML with response
    twiml = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>{response}</Say>
        <Gather input="speech" action="/webhook/twilio/speech" method="POST" speechTimeout="auto" speechModel="phone_call">
            <Say>Anything else I can help you with?</Say>
        </Gather>
    </Response>
    """
    
    return Response(content=twiml, media_type="application/xml")
