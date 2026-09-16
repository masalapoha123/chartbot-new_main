from fastapi import FastAPI, UploadFile, File, Form,WebSocket,WebSocketDisconnect
from graph import init_graph,get_images
from graph import start_graph,edit_conversation
from pathlib import Path
import shutil
from rag_engine.main import handler
from contextlib import asynccontextmanager
from db_queries.main import init_db,get_pending_cases_db
from db_queries.main import get_all_conversations,delete_pending_case
import json
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body


stateful_data = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_graph()
    
    yield



app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def start_agent(
    userQuery: str = Form(...),
    threadID: str = Form(...),
    image: UploadFile = File(None)
):
    if image:
        storage_path = Path(f"storage/{threadID}")
        storage_path.mkdir(parents=True, exist_ok=True)

        image_path = storage_path / image.filename

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    result = await start_graph(
        userQuery=userQuery,
        threadID=threadID
    )

    return result

@app.post("/upload-pdf")
async def create_knowledge_base(
    pdf: UploadFile = File(...)
):
    pdf_bytes = await pdf.read()

    handler(pdf_bytes=pdf_bytes)

    return "knowledge_base done"




@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    socket_id = str(uuid4())

    print(f"{socket_id} connected")
    

    while True:
        try:
            message = await websocket.receive_text()
            
            data = json.loads(message)
            
            
            if data['type']=='iniatiate_cc':
                print(True)
                stateful_data['manager']=websocket
                continue
            
            if data['type']=='Validation':
                await stateful_data['agent'].send_text(json.dumps(data))
                
            
            if data['type'] == 'Query':
                stateful_data['agent']=websocket

                if "manager" not in stateful_data:
                    await stateful_data['agent'].send_text(json.dumps({
                        "message":"pending"
                    }))

                else:

                    await stateful_data['manager'].send_text(json.dumps(data))
                
            
           
        except Exception as e:
            print(str(e))
            break
        except WebSocketDisconnect as e:
            print(f"Disconnected {socket_id}")
            break
            
        



@app.get("/get-conversation")
async def get_conversation():

    conversation = await get_all_conversations()
    
    
    return conversation

@app.get("/get-pending-cases")
async def get_pending_cases():

    cases = await get_pending_cases_db()

    message=[]

    for data in cases:
        images = get_images(data['image_path'])
        message.append({
                        'type':'Query',
                        'images':images,
                        'message':"Please get pending cases....",
                        'threadID':data['threadID']
                        })

    return message




@app.post("/handle-pending-cases")
async def handle_cases(data: dict = Body(...)):
    thread_id = data.get("threadID")
    answer = data.get("answer")

    if not thread_id or not answer:
        return {
            "success": False,
            "message": "threadID and answer are required"
        }

    await delete_pending_case(threadID=thread_id)
    await edit_conversation(
        threadID=thread_id,
        answer=answer
    )

    return {
        "success": True,
        "message": "Pending case handled successfully"
    }

    

    





