#!/usr/bin/env python3
"""
Azure DeepSeek-R1 → OpenAI-style proxy
--------------------------------------
• Listens on  http://127.0.0.1:3333/v1/chat/completions
• Forwards to Azure AI Inference and returns OpenAI-compatible JSON
"""

import uuid
import logging
import typing as T
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
import uvicorn

# ──────────────── EDIT ONLY THESE ────────────────
AZURE_ENDPOINT = "https://ai-ouchyoakaz2002ai109957169787.services.ai.azure.com/models"
AZURE_KEY      = "FZZoOkELyvYrOg9rfzceJhGePYoT8mdgW9nDkwK90sTgfyPyl6vuJQQJ99BEACfhMk5XJ3w3AAAAACOGp9mW"
MODEL_NAME     = "DeepSeek-R1"          # deployment *name* in Azure portal
# ────────────────────────────────────────────────

# ---- Azure client ----------------------------------------------------
# ChatCompletionsClient automatically appends “/models” internally,
# so we give it the *bare* resource URL (strip only a trailing slash).
az_client = ChatCompletionsClient(
    endpoint   = AZURE_ENDPOINT.rstrip("/"),
    credential = AzureKeyCredential(AZURE_KEY),
    api_version= "2024-05-01-preview"
)

# ---- FastAPI glue ----------------------------------------------------
app = FastAPI(title="DeepSeek-R1 proxy", version="1.1")

class _Msg(BaseModel):
    role   : str  = Field(pattern="^(system|user|assistant)$")
    content: str

class _ChatReq(BaseModel):
    messages  : T.List[_Msg]
    max_tokens: int | None = 2048

@app.post("/v1/chat/completions")
def chat(req: _ChatReq):
    role_map = {
        "system":    SystemMessage,
        "user":      UserMessage,
        "assistant": AssistantMessage,
    }
    msgs = [role_map[m.role](content=m.content) for m in req.messages]

    try:
        resp = az_client.complete(
            messages   = msgs,
            model      = MODEL_NAME,
            max_tokens = req.max_tokens or 2048
        )
    except Exception as e:
        logging.exception("Azure call failed")
        raise HTTPException(status_code=500, detail=str(e))

    answer = resp.choices[0].message.content
    return {
        "id"     : str(uuid.uuid4()),
        "object" : "chat.completion",
        "model"  : MODEL_NAME,
        "choices": [{
            "index"        : 0,
            "finish_reason": "stop",
            "message"      : {"role": "assistant", "content": answer}
        }]
    }

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}

# ---- Runner ----------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3333, log_level="info")
