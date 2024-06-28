import re
import json

from fastapi import FastAPI, WebSocket
from autogen_chat import AutogenChat
import asyncio
import uvicorn
# from dotenv import load_dotenv, find_dotenv
# import openai
# import os

from src.classifier import Classifier

classifier = Classifier.from_pretrained("data/classifier_tfidflgbm")

# _ = load_dotenv(find_dotenv()) # read local .env file
# openai.api_key = os.environ['OPENAI_API_KEY']
# openai.log='debug'

app = FastAPI()
app.autogen_chat = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[AutogenChat] = []

    async def connect(self, autogen_chat: AutogenChat):
        await autogen_chat.websocket.accept()
        self.active_connections.append(autogen_chat)

    async def disconnect(self, autogen_chat: AutogenChat):
        autogen_chat.client_receive_queue.put_nowait("DO_FINISH")
        print(f"autogen_chat {autogen_chat.chat_id} disconnected")
        self.active_connections.remove(autogen_chat)


manager = ConnectionManager()


async def send_to_client(autogen_chat: AutogenChat):
    while True:
        reply = await autogen_chat.client_receive_queue.get()
        if reply and reply == "DO_FINISH":
            autogen_chat.client_receive_queue.task_done()
            break
        await autogen_chat.websocket.send_text(reply)
        autogen_chat.client_receive_queue.task_done()
        await asyncio.sleep(0.05)


async def receive_from_client(autogen_chat: AutogenChat):
    while True:
        data = await autogen_chat.websocket.receive_text()
        if data and data == "DO_FINISH":
            await autogen_chat.client_receive_queue.put("DO_FINISH")
            await autogen_chat.client_sent_queue.put("DO_FINISH")
            break
        await autogen_chat.client_sent_queue.put(data)
        await asyncio.sleep(0.05)


# Define a function to extract the case summary
def extract_case_summary(text):
    # Use regex to find the text starting with "Case Summary:" and ending before the next paragraph
    match = re.search(r"Case Summary:(.*?)(?:\n\n|$)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return None


@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    try:
        autogen_chat = AutogenChat(chat_id=chat_id, websocket=websocket)
        await manager.connect(autogen_chat)
        data = await autogen_chat.websocket.receive_text()
        _ = asyncio.gather(
            send_to_client(autogen_chat), receive_from_client(autogen_chat)
        )
        await autogen_chat.clarify(data)

        last_dona_message = autogen_chat.agent_dona.last_message()["content"]
        case_summary = extract_case_summary(last_dona_message)
        print(f"Case Summary: {case_summary}")

        # classify the case summary
        case_type = classifier.predict(case_summary)
        print(f"Case Type: {case_type}")

        # call the retrieve function
        # reply as rachel:
        reply = {
            "sender": "rachel",
            "content": f"""
            I gathered the following case summary: {case_summary}
            I detected your case as being {case_type}.
            """,
            "sources": [
                {
                    "name": "article1",
                    "url": "https://www.admin.ch/opc/en/classified-compilation/19995395/index.html",
                }
            ],
        }
        await autogen_chat.websocket.send_text(json.dumps(reply))
        await asyncio.sleep(0.05)
        # here add the next steps (classification ...)
        # await autogen_chat.research(data)
    except Exception as e:
        print("ERROR", str(e))
    finally:
        try:
            await manager.disconnect(autogen_chat)
        except:
            pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
