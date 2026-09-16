import os
from fastmcp import Client
from langchain_core.messages import AIMessage
from state.state import GraphState
from LLM.agent import call_llm
from pathlib import Path
from prompts.enquiry_prompt import enquiry_agent_prompt
import base64


async def enquiry_agent(state: GraphState):

    image_text = ""
    chunks = []

    image_dir = Path("storage") / state["threadID"]
    
    current = state['current_step']+1

    async with Client("http://localhost:8001/mcp") as client:


        user_query = state["user_query"]


        image_text = ""

        if os.path.exists(image_dir):
            image_files = [
                os.path.join(image_dir, file)
                for file in os.listdir(image_dir)
            ]

            for image_path in image_files:

                with open(image_path, "rb") as f:
                    image_bytes = f.read()

                
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")

                ocr_result = await client.call_tool(
                    "ocr_as_tool",
                    {
                        "image_base64": image_base64
                    }
                )

                image_text += ocr_result.data + "\n"
                
                print(image_text)

        
        combined_query = user_query

        if image_text.strip():
            combined_query = f"""
    User Query:
    {user_query}

    Information extracted from attached images:
    {image_text}
    """

        
        rag_result = await client.call_tool(
            "rag_as_tool",
            {
                "userQuery": combined_query
            }
        )

        chunks = rag_result.data
    
    

    prompt = enquiry_agent_prompt(
        state=state,
        image_text=image_text,
        chunks=chunks
    )

    result = call_llm(prompt)

    return {
        "ai": [AIMessage(content=f"{result}")],
        'current_step':current
    }

