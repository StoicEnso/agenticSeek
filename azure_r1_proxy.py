"""
A 15-line bridge that lets AgenticSeek (OpenAI-style JSON)
talk to an Azure AI Inference DeepSeek-R1 deployment.

Start with:
    AZURE_R1_ENDPOINT="https://<your-resource>.services.ai.azure.com/models"
    AZURE_R1_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    uvicorn azure_r1_proxy:app --host 0.0.0.0 --port 3333
"""

from fastapi import FastAPI
from pydantic import BaseModel
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential
import os, typing as T

# ---- Azure client -----------------------------------------------------------
client = ChatCompletionsClient(
    endpoint=os.environ["AZURE_R1_ENDPOINT"],           # “…/models”
    credential=AzureKeyCredential(os.environ["AZURE_R1_KEY"]),
    api_version="2024-05-01-preview"
)
MODEL_NAME = "DeepSeek-R1"                              # ← your deployment name

# ---- FastAPI glue -----------------------------------------------------------
app = FastAPI()

class _Msg(BaseModel):
    role: str
    content: str

class _ChatReq(BaseModel):
    messages: T.List[_Msg]
    max_tokens: int = 2048

@app.post("/v1/chat/completions")
def chat(req: _ChatReq):
    role_map = {"system": SystemMessage,
                "user": UserMessage,
                "assistant": AssistantMessage}
    msgs = [role_map[m.role](content=m.content) for m in req.messages]

    resp = client.complete(messages=msgs, model=MODEL_NAME, max_tokens=req.max_tokens)
    return {
        "choices": [{
            "message": {"content": resp.choices[0].message.content}
        }]
    }
