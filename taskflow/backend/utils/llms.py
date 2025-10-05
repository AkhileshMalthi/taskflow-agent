from langchain.chat_models import init_chat_model
from enum import Enum

def get_llm(model_provider: str, model_name: str):
    return init_chat_model(model=model_name, model_provider=model_provider)

def get_groq_llm(model_name: str):
	return get_llm(model_provider="groq", model_name=model_name)

def get_openai_llm(model_name: str):
	return get_llm(model_provider="openai", model_name=model_name)

def get_anthropic_llm(model_name: str):
	return get_llm(model_provider="anthropic", model_name=model_name)

def get_google_llm(model_name: str):
	return get_llm(model_provider="google", model_name=model_name)