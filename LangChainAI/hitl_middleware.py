from typing import Any
from langchain.chat_models import LLM

class HITLMiddleware:
    def __init__(self, llm: LLM):
        self.llm = llm

    def __call__(self, ticket: Any):
        if ticket["priority"] == "critical":
            # Trigger HITL process
            print("HITL process triggered for critical ticket")
            # Add code here to handle the HITL process
        else:
            # Continue with normal processing
            print("Normal processing for non-critical ticket")
            # Add code here to handle normal processing