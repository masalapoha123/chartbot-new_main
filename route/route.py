from state.state import GraphState
from langgraph.graph import END

def router(state: GraphState):
    
    route = state['plan']
    current = state['current_step']
    
    
    if current == len(route):
        return "END"
    else:
        return route[current]
        
    
    
    

