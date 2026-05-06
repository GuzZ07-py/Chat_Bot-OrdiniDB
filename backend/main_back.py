from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os

# Configurazione API Key (da impostare su Render)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

app = FastAPI()

# Configurazione CORS per parlare con il frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modello per la richiesta
class ChatMessage(BaseModel):
    message: str

# Inizializzazione modello
model = genai.GenerativeModel("gemini-2.5-pro")

@app.post("/chat")
def home():
    return {"status": "Chatbot Online"}

@app.post("/chat")
async def chat_endpoint(chat: ChatMessage):
    try:
        response = model.generate_content(chat.message)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
