from langgraph.graph import StateGraph,START,END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from typing import List, Dict,Annotated
from typing_extensions import TypedDict
from enum import Enum
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage


class ComplaintType(Enum):
    damaged_product = "damaged_product"
    delivery_issue = "delivery_issue"


class query_type(Enum):
    enquiry = "enquiry"
    complaint = "complaint"
       
    

class GraphState(TypedDict):
    user: Annotated[List[BaseMessage], add_messages]
    ai: Annotated[List[BaseMessage], add_messages]
    user_query: str
    completed: bool
    threadID: str
    plan: List[str]
    current_step: int
    status: str
    



