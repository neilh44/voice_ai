from typing import List, Dict, Any
from app.models.call import CallSession
from app.services.llm_service import LLMService
from app.services.knowledge_service import KnowledgeService
from app.db.crud import save_message, get_call_session

class ConversationManager:
    def __init__(self, call_sid: str, user_id: str, knowledge_base_id: str = None):
        self.call_sid = call_sid
        self.user_id = user_id
        self.knowledge_base_id = knowledge_base_id
        
        # Initialize services
        self.llm_service = LLMService(user_id=user_id)
        self.knowledge_service = KnowledgeService()
        
        # Get or create call session
        self.session = get_call_session(call_sid) or self._create_call_session()
    
    def _create_call_session(self) -> CallSession:
        """
        Create a new call session
        """
        # Implementation would save to database
        return CallSession(call_sid=self.call_sid)
    
    async def process_user_input(self, user_input: str) -> str:
        """
        Process user input and generate a response
        """
        # Save user message
        save_message(
            call_sid=self.call_sid,
            role="user",
            content=user_input
        )
        
        # Query knowledge base if available
        context = ""
        if self.knowledge_base_id:
            knowledge_results = await self.knowledge_service.query_knowledge(
                knowledge_base_id=self.knowledge_base_id,
                query=user_input
            )
            context = "\n\n".join([result.text for result in knowledge_results])
        
        # Get conversation history
        history = self._get_conversation_history()
        
        # Build prompt with context
        system_prompt = self._build_system_prompt(context)
        
        # Generate response
        response = await self.llm_service.generate_response(
            prompt=user_input,
            conversation_history=history,
            system_prompt=system_prompt
        )
        
        # Save assistant message
        save_message(
            call_sid=self.call_sid,
            role="assistant",
            content=response
        )
        
        return response
    
    def _get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history for this call
        """
        # Implementation would fetch from database
        pass
    
    def _build_system_prompt(self, context: str) -> str:
        """
        Build the system prompt with context and instructions
        """
        system_prompt = "You are a helpful voice assistant for scheduling appointments."
        
        if context:
            system_prompt += f"\n\nHere is some relevant information from the knowledge base:\n{context}"
        
        return system_prompt
