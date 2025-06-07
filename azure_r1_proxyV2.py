#!/usr/bin/env python3
"""
DeepSeek-R1 ➜ OpenAI-style proxy
--------------------------------
• Listens locally on  http://127.0.0.1:3333/v1/chat/completions
• Forwards every request to your Azure AI Inference deployment.

Usage
-----
1.  Replace AZURE_KEY below with **your own** key (between the quotes).
2.  Save the file, press “Run” in VS Code.  Leave it running.
3.  In a second terminal, start AgenticSeek:
        python api.py          # or python cli.py
   Make sure   provider_server_address = http://127.0.0.1:3333
   in config.ini.

Dependencies (already in your venv if you followed the guide):
    pip install azure-ai-inference fastapi uvicorn==0.29.0
"""

from fastapi import FastAPI
from pydantic import BaseModel
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
import uvicorn
import typing as T

# ---------------------------------------------------------------------
# !!!  HARD-CODED  CREDENTIALS – EDIT JUST THESE TWO LINES  !!!
AZURE_ENDPOINT = "https://ai-ouchyoakaz2002ai109957169787.services.ai.azure.com/models"
AZURE_KEY      = "FZZoOkELyvYrOg9rfzceJhGePYoT8mdgW9nDkwK90sTgfyPyl6vuJQQJ99BEACfhMk5XJ3w3AAAAACOGp9mW"
MODEL_NAME     = "DeepSeek-R1"          # deployment name on the Azure page
# ---------------------------------------------------------------------

client = ChatCompletionsClient(
    endpoint   = AZURE_ENDPOINT,
    credential = AzureKeyCredential(AZURE_KEY),
    api_version= "2024-05-01-preview"
)

# --------------------------- FastAPI glue ----------------------------
app = FastAPI(title="DeepSeek-R1 proxy", version="1.0")

class _Msg(BaseModel):
    role: str
    content: str

class _ChatReq(BaseModel):
    messages: T.List[_Msg]
    max_tokens: int | None = 2048

@app.post("/v1/chat/completions")
def chat(req: _ChatReq):
    role_map = {"system": SystemMessage,
                "user": UserMessage,
                "assistant": AssistantMessage}
    msgs = [role_map[m.role](content=m.content) for m in req.messages]

    resp = client.complete(messages=msgs,
                           model=MODEL_NAME,
                           max_tokens=req.max_tokens or 2048)

    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": resp.choices[0].message.content
            }
        }]
    }

# Simple health check for peace of mind
@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}

# ------------------------------ Runner -------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3333, log_level="info")
