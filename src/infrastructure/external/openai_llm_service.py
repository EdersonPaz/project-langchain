"""OpenAI LLM Service - Integration with OpenAI API"""

from langchain_openai import ChatOpenAI
from langchain.callbacks import StdOutCallbackHandler


class OpenAILLMService:
    """
    Service for integrating with OpenAI LLM.
    - Wraps ChatOpenAI from LangChain
    - Handles model selection and configuration
    """
    
    # Model recommendations by cost
    MODELS = {
        "gpt-3.5-turbo": {"cost_per_1m_input": 0.50, "cost_per_1m_output": 1.50, "tier": "budget"},
        "gpt-4o-mini": {"cost_per_1m_input": 0.15, "cost_per_1m_output": 0.60, "tier": "balanced"},
        "gpt-4-turbo": {"cost_per_1m_input": 10.00, "cost_per_1m_output": 30.00, "tier": "premium"},
        "gpt-4": {"cost_per_1m_input": 30.00, "cost_per_1m_output": 60.00, "tier": "enterprise"}
    }
    
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.5):
        """
        Initialize OpenAI LLM service.
        
        Args:
            model: Model name (default: lowest cost)
            temperature: Temperature for generation (0-1)
        """
        if model not in self.MODELS:
            raise ValueError(f"Unknown model: {model}. Available: {list(self.MODELS.keys())}")
        
        self.model = model
        self.temperature = temperature
        self._llm = None
    
    def get_llm(self) -> ChatOpenAI:
        """Get or create LLM instance"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                callbacks=[StdOutCallbackHandler()]
            )
        return self._llm
    
    @classmethod
    def get_model_info(cls, model: str) -> dict:
        """Get pricing and info for a model"""
        return cls.MODELS.get(model, {})
    
    @classmethod
    def recommend_model(cls, budget: str = "low") -> str:
        """Get recommended model based on budget"""
        tiers = {
            "low": "gpt-3.5-turbo",
            "medium": "gpt-4o-mini",
            "high": "gpt-4-turbo",
            "unlimited": "gpt-4"
        }
        return tiers.get(budget, "gpt-3.5-turbo")
