"""LLM factory for creating LLM instances based on provider."""
from typing import Optional, Any
from shared.config import BaseConfig


class LLMFactory:
    """Factory for creating LLM instances based on provider configuration."""
    
    @staticmethod
    def create(config: Optional[BaseConfig] = None, provider: Optional[str] = None, **kwargs) -> Any:
        """
        Create an LLM instance based on the provider.
        
        Args:
            config: Configuration object (optional, will load from env if not provided)
            provider: Override provider from config (optional)
            **kwargs: Additional arguments to pass to the LLM constructor
            
        Returns:
            Configured LLM instance
        """
        if config is None:
            from shared.config import load_config
            config = load_config()
        
        provider = provider or config.llm_provider
        
        if provider == "openai":
            return LLMFactory._create_openai(config, **kwargs)
        elif provider == "anthropic":
            return LLMFactory._create_anthropic(config, **kwargs)
        elif provider == "azure":
            return LLMFactory._create_azure(config, **kwargs)
        elif provider == "huggingface":
            return LLMFactory._create_huggingface(config, **kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    @staticmethod
    def _create_openai(config: BaseConfig, model: str = "gpt-4o-mini", **kwargs) -> Any:
        """Create OpenAI LLM instance."""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("langchain-openai is required for OpenAI provider. Install with: pip install langchain-openai")
        
        return ChatOpenAI(
            model=model,
            api_key=config.openai_api_key,
            temperature=kwargs.get("temperature", 0.7),
            **{k: v for k, v in kwargs.items() if k != "temperature"}
        )
    
    @staticmethod
    def _create_anthropic(config: BaseConfig, model: str = "claude-3-5-sonnet-20241022", **kwargs) -> Any:
        """Create Anthropic LLM instance."""
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("langchain-anthropic is required for Anthropic provider. Install with: pip install langchain-anthropic")
        
        return ChatAnthropic(
            model=model,
            api_key=config.anthropic_api_key,
            temperature=kwargs.get("temperature", 0.7),
            **{k: v for k, v in kwargs.items() if k != "temperature"}
        )
    
    @staticmethod
    def _create_azure(config: BaseConfig, **kwargs) -> Any:
        """Create Azure OpenAI LLM instance."""
        try:
            from langchain_openai import AzureChatOpenAI
        except ImportError:
            raise ImportError("langchain-openai is required for Azure OpenAI provider. Install with: pip install langchain-openai")
        
        # Azure requires additional environment variables
        import os
        return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=kwargs.get("temperature", 0.7),
            **{k: v for k, v in kwargs.items() if k != "temperature"}
        )
    
    @staticmethod
    def _create_huggingface(config: BaseConfig, model: str = "meta-llama/Llama-3.2-3B-Instruct", **kwargs) -> Any:
        """Create Hugging Face LLM instance."""
        try:
            from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
            from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
            import torch
        except ImportError:
            raise ImportError(
                "langchain-huggingface, transformers, and torch are required for Hugging Face provider. "
                "Install with: pip install langchain-huggingface transformers torch"
            )
        
        # Determine device
        device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model, token=config.huggingface_token)
        
        # Model loading configuration
        model_kwargs = {
            "token": config.huggingface_token,
            "low_cpu_mem_usage": True,
        }
        
        if device == "mps":
            model_kwargs["torch_dtype"] = torch.bfloat16
            model_kwargs["device_map"] = device
        elif device == "cuda":
            model_kwargs["torch_dtype"] = torch.float16
            model_kwargs["device_map"] = "auto"
        else:
            model_kwargs["torch_dtype"] = torch.float32
        
        model_instance = AutoModelForCausalLM.from_pretrained(model, **model_kwargs)
        
        # Create pipeline
        pipe = pipeline(
            "text-generation",
            model=model_instance,
            tokenizer=tokenizer,
            max_new_tokens=kwargs.get("max_new_tokens", 2048),
            do_sample=kwargs.get("do_sample", False),
            repetition_penalty=kwargs.get("repetition_penalty", 1.1),
        )
        
        llm_pipeline = HuggingFacePipeline(pipeline=pipe)
        return ChatHuggingFace(llm=llm_pipeline)


__all__ = ["LLMFactory"]
