import streamlit as st
import requests
import uuid


API_URL = "http://localhost:8000/query"
CONVERSATION_URL = "http://localhost:8000/get-conversation"


st.set_page_config(
    page_title="E-Commerce Support",
    page_icon="💬"
)

st.title("💬 E-Commerce Support")


def to_display_messages(conv):
    """
    Convert a backend conversation shaped like:
        {"threadID": ..., "user": [{"role": "user", "content": ...}, ...],
                           "ai":   [{"role": "assistant", "content": ...}, ...]}
    into a single chronological list of {"role", "content"} for display.

    NOTE: the backend stores user/ai as separate lists with no timestamps,
    so true chronological interleaving isn't recoverable. We assume turns
    alternate 1:1 (one user msg -> one ai msg) and zip them in order.
    """
    if not conv:
        return []

    user_msgs = conv.get("user", [])
    ai_msgs = conv.get("ai", [])

    merged = []
    for i in range(max(len(user_msgs), len(ai_msgs))):
        if i < len(user_msgs):
            merged.append(user_msgs[i])
        if i < len(ai_msgs):
            merged.append(ai_msgs[i])

    return merged


if "threadID" not in st.session_state:
    st.session_state.threadID = str(uuid.uuid4())

if "conversations" not in st.session_state:

    response = requests.get(CONVERSATION_URL)

    if response.status_code == 200:
        # Expected shape: { thread_id: {"threadID":..., "user":[...], "ai":[...]}, ... }
        st.session_state.conversations = response.json()
    else:
        st.session_state.conversations = {}


with st.sidebar:

    st.header("Conversations")

    new_chat = st.button("New Chat")

    if new_chat:
        new_id = str(uuid.uuid4())
        st.session_state.threadID = new_id
        st.session_state.conversations[new_id] = {
            "threadID": new_id,
            "user": [],
            "ai": []
        }
        st.rerun()

    thread_ids = list(st.session_state.conversations.keys())

    if thread_ids:

        selected_thread = st.selectbox(
            "Select conversation",
            thread_ids,
            index=(
                thread_ids.index(st.session_state.threadID)
                if st.session_state.threadID in thread_ids
                else 0
            )
        )

        if selected_thread != st.session_state.threadID:
            st.session_state.threadID = selected_thread
            st.rerun()


current_conv = st.session_state.conversations.get(st.session_state.threadID)
messages = to_display_messages(current_conv)


for message in messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


uploaded_image = st.file_uploader(
    "Upload an image",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=False
)


user_query = st.chat_input("Describe your issue...")


if user_query:

    with st.chat_message("user"):
        st.write(user_query)

    data = {
        "userQuery": user_query,
        "threadID": st.session_state.threadID
    }

    files = None

    if uploaded_image:
        files = {
            "image": (
                uploaded_image.name,
                uploaded_image.getvalue(),
                uploaded_image.type
            )
        }

    response = requests.post(
        API_URL,
        data=data,
        files=files
    )

    if response.status_code == 200:

        result = response.json()

        ai_message = result["ai"][-1]["content"]

        with st.chat_message("assistant"):
            st.write(ai_message)

        # Keep local state in the SAME shape the backend uses:
        # {"threadID": ..., "user": [...], "ai": [...]}
        st.session_state.conversations.setdefault(
            st.session_state.threadID,
            {"threadID": st.session_state.threadID, "user": [], "ai": []}
        )

        st.session_state.conversations[st.session_state.threadID]["user"].append({
            "role": "user",
            "content": user_query
        })

        st.session_state.conversations[st.session_state.threadID]["ai"].append({
            "role": "assistant",
            "content": ai_message
        })

    else:
        st.error(f"Error {response.status_code}: {response.text}")