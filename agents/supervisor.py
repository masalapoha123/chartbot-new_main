from state.state import GraphState
from prompts.supervisor_prompt import supervisor_prompt
from LLM.agent import call_llm
import json
from langchain_core.messages import AIMessage


def supervisor_agent(state: GraphState):
    
    print("SUPERVISOR is Running....")
    
    prompt = supervisor_prompt(state)
    
    # result = call_llm(prompt)
    
    # data = json.loads(result)
    
    # message = data["message"]

    # plan = data['plan']

    plan = ['C',"END"]
    
    return {
        **state,
        'plan':plan,
        'current_step':0
        }
    
