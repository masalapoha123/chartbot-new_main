from state.state import GraphState
from prompts.delivery_prompt import delivery_agent_prompt
from pathlib import Path
from langgraph.types import interrupt
from langchain_core.messages import AIMessage
from db_queries.main import checkID,issue_solved,handle_pending_complaint
from LLM.agent import call_llm
from extractors.main import extract_deliver_ID
import websockets
import json


async def delivery_agent(state: GraphState):
    
    deliverID = extract_deliver_ID(state['user_query'])
    
    current = state['current_step']+1
    
    if deliverID == None:
            return {
                **state,
                'ai':[AIMessage(content=f"No Valid DeliverID")],
                'current_step':current
            }
    already_resolved = await checkID(deliverID) 
    
    if already_resolved:
        return {
            **state,
            'ai':[AIMessage(content=f"Issue is already resolved for ID {deliverID}")],
            'current_step':current
        }
    
    path = Path("storage") / state["threadID"]
    
    answer = None
    
    path_string = str(path)
    
    path_exists = path.exists()
    
    print(path_exists)
    
    if path_exists:

        answer = interrupt({
        "message": f"Please check the evidence at /storage/{state['threadID']} , type YES or NO to validate",
        "threadID": state["threadID"],
        "ID": deliverID,
        "type":"Delivery",
        "image_dir":path_string
    })
        
        print("Waiting for manager to Aprrove....")
        
    if answer=='pending':
    
            await handle_pending_complaint({
            "message": f"Please check the evidence at /storage/{state['threadID']} , type YES or NO to validate",
            "threadID": state["threadID"],
            "ID": deliverID,
            "type":"Delivery",
            "image_dir":path_string,
            "status":"pending"
        })


    
    if path_exists and answer == 'NO':
        return {
            **state,
            'ai':[AIMessage(content=f"Please provide proper evidence...")],
            'current_step':current
        }
    
    await issue_solved(ID=deliverID)
    
    prompt = delivery_agent_prompt(state)
    
    result = call_llm(prompt)
    
    
    return {
        **state,
        'ai':[AIMessage(content=f"{result}")],
        'current_step':current
    }