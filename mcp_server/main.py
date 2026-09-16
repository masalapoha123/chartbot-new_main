from fastmcp import FastMCP
from mcp_tools.retrieve import retrieve
from mcp_tools.ocr import ocr_logic
import base64

mcp = FastMCP("RAG Server")


@mcp.tool
def rag_as_tool(userQuery: str) -> list[str]:
    return retrieve(userQuery)

@mcp.tool
def ocr_as_tool(image_base64: bytes) -> str:
    
    image_bytes = base64.b64decode(image_base64)

    return ocr_logic(image_bytes)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)