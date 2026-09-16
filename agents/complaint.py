from state.state import GraphState
from prompts.complaint_prompt import complaint_agent_prompt
from pathlib import Path
from langgraph.types import interrupt
from langchain_core.messages import AIMessage
from db_queries.main import checkID,issue_solved,handle_pending_complaint
from LLM.agent import call_llm
from extractors.main import extract_complaint_ID


async def complaint_agent(state: GraphState):
    
    complaintID = extract_complaint_ID(state['user_query'])
    
    current = state['current_step']+1
    
    if complaintID == None:
        return {
            **state,
            'ai':[AIMessage(content=f"No Valid OrderID")],
            'current_step':current
        }
    
    already_resolved = await checkID(complaintID) 
    
    if already_resolved:
        return {
            **state,
            'ai':[AIMessage(content=f"Issue is already resolved for ID {complaintID}")],
            'current_step':current
        }
    
    
    
    path = Path("storage") / state["threadID"]
    
    path_string = str(path)
    
    answer = None
    
    path_exists = path.exists()
    
    if path_exists:

        answer = interrupt({
        "message": f"Please check the evidence at /storage/{state['threadID']} , type YES or NO to validate",
        "threadID": state["threadID"],
        "ID": complaintID,
        "type":"Complaint",
        "image_dir":path_string
    })


    if answer=='pending':

        await handle_pending_complaint({
        "message": f"Please check the evidence at /storage/{state['threadID']} , type YES or NO to validate",
        "threadID": state["threadID"],
        "ID": complaintID,
        "type":"Complaint",
        "image_dir":path_string,
        "status":"pending"
    })

        return {
                    **state,
                    'ai':[AIMessage(content=f"Your issue has been pending with Supervisor..")],
                    'current_step':current,
                    'status':"pending"
                }
    
    
    
    if path_exists and answer == 'NO':
        return {
            **state,
            'ai':[AIMessage(content=f"Please provide proper evidence...")],
            'current_step':current
        }
    
    await issue_solved(ID=complaintID)
    
    prompt = complaint_agent_prompt(state)
    
    result = call_llm(prompt)
    
    
    
    return {
        **state,
        'ai':[AIMessage(content=f"{result}")],
        'current_step':current
        
    }