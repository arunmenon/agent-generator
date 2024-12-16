# llm.py
from crewai import LLM

def create_llm(model="openai/gpt-4", temperature=0.2, verbose=False):
    return LLM(model=model, temperature=temperature, verbose=verbose)
