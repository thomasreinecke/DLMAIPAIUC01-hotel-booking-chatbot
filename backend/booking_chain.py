import json
from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from local_llm import LMStudioLLM
from prompts import BOOKING_STATE_PROMPT

def update_booking_state(conversation_history: str) -> Dict[str, Any]:
    """
    Uses a LangChain chain (with our local LLM) to update the booking state based on the full conversation history.
    """
    template = PromptTemplate(
        input_variables=["history"],
        template=BOOKING_STATE_PROMPT
    )
    llm = LMStudioLLM()
    chain = template | llm
    input_data = {"history": conversation_history}
    print("CHAIN INPUT:", input_data)
    chain_output = chain.invoke(input_data)
    print("CHAIN OUTPUT:", chain_output)
    try:
        state = json.loads(chain_output)
        return state
    except Exception as e:
        print(e)
        return {
            "error": str(e),
            "response": "I'm sorry, I didn't understand that. Could you please rephrase your last message?"
        }
