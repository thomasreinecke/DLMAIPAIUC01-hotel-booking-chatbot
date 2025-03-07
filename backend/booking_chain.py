import json
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from local_llm import LMStudioLLM
from prompts import BOOKING_CONTEXT_PROMPT

def update_booking_context(conversation_history: str, current_context: dict, last_user_input: str) -> Dict[str, Any]:
    """
    Uses a LangChain chain to update the booking context based on:
      - the full conversation history,
      - the current booking context (serialized as JSON),
      - the last user input.
    Returns a dictionary matching the booking context schema.
    
    If the LLM returns invalid JSON, retry up to 2 times with additional instructions.
    """
    template = PromptTemplate(
        input_variables=["history", "context", "last_user_input"],
        template=BOOKING_CONTEXT_PROMPT
    )
    llm = LMStudioLLM()
    chain = template | llm
    
    def run_chain(last_input: str) -> str:
        input_data = {
            "history": conversation_history,
            "context": json.dumps(current_context),
            "last_user_input": last_input
        }
        print("CHAIN INPUT:", input_data)
        return chain.invoke(input_data)
    
    attempts = 0
    max_attempts = 3
    current_input = last_user_input
    while attempts < max_attempts:
        chain_output = run_chain(current_input)
        print("CHAIN OUTPUT:", chain_output)
        try:
            state = json.loads(chain_output)
            return state
        except Exception as e:
            print("JSON parse error:", e)
            attempts += 1
            # On retry, append an instruction for correction to the last user input.
            current_input = f"{last_user_input}\n\nThe payload you returned was invalid JSON, this must be corrected."
    
    # Fallback if all attempts fail.
    return {
        "error": "Invalid JSON returned after multiple attempts.",
        "response": "I'm sorry, I didn't understand that. Could you please rephrase your last message?"
    }
