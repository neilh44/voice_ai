import openai
from app.core.config import settings
from app.models.integration import LLMConfig
from app.db.crud import get_user_integration

class LLMService:
    def __init__(self, provider="openai", user_id=None, integration_id=None):
        self.provider = provider
        
        if user_id and integration_id:
            # Get user-specific LLM config
            llm_config = get_user_integration(user_id, provider, integration_id)
            if not llm_config:
                raise ValueError(f"{provider} integration not found")
            
            self.api_key = llm_config.api_key
            self.model = llm_config.model
        else:
            # Use default platform LLM config
            if provider == "openai":
                self.api_key = settings.OPENAI_API_KEY
                self.model = settings.OPENAI_MODEL
        
        # Configure client
        if provider == "openai":
            openai.api_key = self.api_key
    
    async def generate_response(self, prompt, conversation_history=None, system_prompt=None):
        """
        Generate a response from the LLM
        """
        if self.provider == "openai":
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({"role": "user", "content": prompt})
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")

