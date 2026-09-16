from state.state import GraphState
from langchain_core.messages import AIMessage



def human_escalation(state: GraphState):
    
    current = state['current_step']+1
    
    return {
        **state,
        "ai":[AIMessage(content=f"Our Human agent will contact u shortly...")],
        'current_step':current
    }

