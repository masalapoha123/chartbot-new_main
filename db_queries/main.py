import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import AIMessage
from LLM.agent import call_llm
from prompts.pending_prompt import pending_prompt


DB_PATH = "./db/queries.db"
DB_PENDING_PATH="./db/pendings.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                ID TEXT PRIMARY KEY
            )
        """)

        await conn.commit()

    async with aiosqlite.connect(DB_PENDING_PATH) as conn:
        await conn.execute("""
    CREATE TABLE IF NOT EXISTS pending (
        threadID   TEXT PRIMARY KEY,
        image_path TEXT NOT NULL,
        message    TEXT NOT NULL,
        status     TEXT NOT NULL
    )
""")
        
        await conn.commit()
        


async def checkID(ID: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT 1 FROM queries WHERE ID = ? LIMIT 1",
            (ID,)
        )

        result = await cursor.fetchone()

        return result is not None


async def issue_solved(ID: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO queries (ID) VALUES (?)",
            (ID,)
        )

        await conn.commit()

        return True
    
    
async def get_all_conversations():
    conn = await aiosqlite.connect("./db/checkpoints.db")
    checkpointer = AsyncSqliteSaver(conn)

    conversations = {}
    seen_threads = set()

    async for checkpoint in checkpointer.alist(None):
        thread_id = checkpoint.config["configurable"]["thread_id"]

        if thread_id in seen_threads:
            continue
        seen_threads.add(thread_id)

        state = checkpoint.checkpoint.get("channel_values", {})

        user_messages = state.get("user", [])
        ai_messages = state.get("ai", [])

        conversations[thread_id] = {
            "threadID": thread_id,
            "user": [
                {"role": "user", "content": m.content}
                for m in user_messages
            ],
            "ai": [
                {"role": "assistant", "content": m.content}
                for m in ai_messages
            ],
        }

    await conn.close()
    

    return conversations


async def handle_pending_complaint(data):
    conn = await aiosqlite.connect("./db/pendings.db")

    print(data)
    
    cursor = await conn.execute(
            """
            INSERT INTO pending (
                image_path,
                message,
                status,
                threadID
            )
            VALUES (?, ?, ?,?)
            """,
            (
                data.get("image_dir"),
                data.get("message"),
                data.get("status"),
                data.get("threadID")
            )
        )

    await conn.commit()

    await conn.close()

    return

async def get_pending_cases_db():
    conn = await aiosqlite.connect("./db/pendings.db")

    try:
        conn.row_factory = aiosqlite.Row

        cursor = await conn.execute("""
            SELECT
                threadID,
                image_path,
                message
            FROM pending
            WHERE status = 'pending'
        """)

        rows = await cursor.fetchall()
        await cursor.close()

        return [dict(row) for row in rows]

    finally:
        await conn.close()


async def delete_pending_case(threadID):
    async with aiosqlite.connect(DB_PENDING_PATH) as conn:
        await conn.execute(
            """
            DELETE FROM pending
            WHERE threadID = ?
            """,
            (threadID,)
        )
        await conn.commit()



