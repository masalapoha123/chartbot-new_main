from state.state import GraphState
from langgraph.graph import StateGraph
from agents.complaint import complaint_agent
from agents.enquiry import enquiry_agent
from agents.supervisor import supervisor_agent
from route.route import router
from agents.human_escalation import human_escalation
from langgraph.graph import END
from agents.delivery import delivery_agent
from langgraph.types import Command
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import websockets
import json
import os
import base64
from langchain_core.messages import AIMessage
from LLM.agent import call_llm
from prompts.pending_prompt import pending_prompt
from typing import cast
    
builder = StateGraph(GraphState)


builder.add_node('S',supervisor_agent)
builder.add_node('C',complaint_agent)
builder.add_node('E',enquiry_agent)
builder.add_node('H',human_escalation)
builder.add_node('D',delivery_agent)


builder.set_entry_point('S')


mapping = {
  
    'S':'S',
    'C':'C',
    'H':'H',
    'E':'E',
    'END':END,
    'D':'D'    

}


builder.add_conditional_edges(
    "S",
    router,
    mapping
)

builder.add_conditional_edges(
    "C",
    router,
    mapping
)

builder.add_conditional_edges(
    "E",
    router,
    mapping
)

builder.add_conditional_edges(
    "D",
    router,
    mapping
)

builder.add_conditional_edges(
    "H",
    router,
    mapping
)


graph = None
conn = None


async def init_graph():
    global graph, conn

    conn = await aiosqlite.connect("./db/checkpoints.db")

    checkpointer = AsyncSqliteSaver(conn)

    graph = builder.compile(
        checkpointer=checkpointer
    )

from langchain_core.messages import HumanMessage
from langgraph.types import Command

def get_graph():
    global graph

    return graph

async def start_graph(userQuery: str, threadID: str):

    config = {
        "configurable": {
            "thread_id": threadID
        }
    }

    existing_state = await graph.aget_state(config)

    if existing_state.values:

        state = {
            "user_query": userQuery,
            "user": [
                HumanMessage(content=userQuery)
            ]
        }

    else:

        state = {
            "user_query": userQuery,
            "threadID": threadID,
            "plan": [],
            "current_step": 0,
            "completed": False,
            "user": [
                HumanMessage(content=userQuery)
            ],
            "ai": [],
            "status":"completed"
        }

    result = await graph.ainvoke(
        state,
        config=config
    )

    if "__interrupt__" in result:

        interrupt_data = result["__interrupt__"][0].value

        if interrupt_data["type"] == "Delivery":
            print(
                f"Asked By Delivery Agent: ID{interrupt_data['ID']}"
            )
        else:
            print(
                f"Asked By Complaint Agent: Product ID{interrupt_data['ID']}"
            )

        images = get_images(interrupt_data['image_dir'])
        
        async with websockets.connect(
                "ws://localhost:8000/ws"
            ) as websocket:
        
                    await websocket.send(json.dumps({
                        "type":"Query",
                        "message":"Please check this evideneces...",
                        "images":images
                    }))
        
                    response = await websocket.recv()
                    
                    response = json.loads(response)
                    
                    answer = response['message']
        
        human_answer = answer

        result = await graph.ainvoke(
            Command(resume=human_answer),
            config=config
        )

    return result



def get_images(image_dir):
    
    images = []
    
    if os.path.exists(image_dir):
                image_files = [
                    os.path.join(image_dir, file)
                    for file in os.listdir(image_dir)
                ]
    
                for image_path in image_files:
    
                    with open(image_path, "rb") as f:
                        image_bytes = f.read()
    
                    
                    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                    
                    images.append(image_base64)
    
    return images


async def edit_conversation(threadID,answer):

    global graph

    config = {
        "configurable": {
            "thread_id": threadID
        }
    }

    state = await graph.aget_state(config)

    state.values["ai"].pop(-1)

    if answer == "NO":
        state.values["ai"].append(
        AIMessage(content="Please Provide Proper Evidence")
    )

    else:
        prompt = pending_prompt(cast(GraphState,state.values))

        response = call_llm(prompt)

        state.values["ai"].append(
                AIMessage(content=f"{response}")
            )



    await graph.aupdate_state(
        config,
        {"ai": state.values["ai"]}
    )

    


