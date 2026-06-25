from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import psycopg2
import logging
import traceback
import json

# =========================
# 🔥 ULTRA DEBUG LOGGING
# =========================
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("GEMINI_DEBUG")

# =========================
# 🔐 API KEY DEBUG (SAFE)
# =========================
api_key = os.getenv("GEMINI_API_KEY")

logger.info("========== GEMINI AUTH DEBUG ==========")

if api_key:
    logger.info("API KEY STATUS: FOUND")
    logger.info(f"API KEY LENGTH: {len(api_key)}")
    logger.info(f"API KEY PREFIX: {api_key[:8]}...")
else:
    logger.error("API KEY STATUS: MISSING")

genai.configure(api_key=api_key)

# =========================
# 📦 LOAD DB GUIDE
# =========================
with open("guida_database.md", "r", encoding="utf-8") as f:
    database_guida = f.read()

logger.info(f"DB GUIDE LOADED: {len(database_guida)} chars")

# =========================
# 🧠 SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = f"""
Se il messaggio riguarda un ordine del database:
- DEVI chiamare esegui_query
- NON inventare dati
- SOLO SQL SELECT

Usa guida DB: {len(database_guida)} chars
"""

# =========================
# 🛠 TOOLS
# =========================
TOOLS = [{
    "function_declarations": [{
        "name": "esegui_query",
        "description": "Esegue query SQL PostgreSQL",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "tipo_grafico_consigliato": {"type": "string"},
                "asse_x": {"type": "string"},
                "asse_y": {"type": "string"}
            },
            "required": ["query"]
        }
    }]
}]

# =========================
# 🤖 MODEL INIT
# =========================
MODEL_NAME = "gemini-2.5-flash"

logger.info("========== MODEL DEBUG ==========")
logger.info(f"MODEL USED: {MODEL_NAME}")
logger.info(f"TOOLS ENABLED: {json.dumps(TOOLS, indent=2)}")

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    tools=TOOLS,
    system_instruction=SYSTEM_PROMPT
)

# =========================
# 🚀 FASTAPI
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

# =========================
# 📩 REQUEST MODEL
# =========================
class ChatRequest(BaseModel):
    message: str
    user_id: str

# =========================
# 🏠 HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"status": "Chatbot Online"}

# =========================
# 🧠 MAIN DEBUG ROUTE
# =========================
@app.post("/chat")
async def chat(req: ChatRequest):

    logger.info("========================================")
    logger.info("NEW REQUEST RECEIVED")
    logger.info(f"user_id: {req.user_id}")
    logger.info(f"message: {req.message}")

    try:
        # -------------------------
        # SESSION DEBUG
        # -------------------------
        if req.user_id not in sessions:
            logger.info("CREATING NEW SESSION")
            sessions[req.user_id] = model.start_chat(
                enable_automatic_function_calling=False
            )
        else:
            logger.info("USING EXISTING SESSION")

        chat = sessions[req.user_id]

        logger.info("SENDING MESSAGE TO GEMINI...")

        response = chat.send_message(req.message)

        # -------------------------
        # RAW RESPONSE DEBUG
        # -------------------------
        logger.info("RESPONSE RECEIVED")
        logger.info(f"response type: {type(response)}")

        try:
            logger.debug("FULL RESPONSE DUMP:")
            logger.debug(response)
        except Exception as e:
            logger.warning(f"Could not dump full response: {e}")

        # -------------------------
        # PARTS DEBUG
        # -------------------------
        if response.candidates:
            for i, candidate in enumerate(response.candidates):
                logger.info(f"Candidate {i}")

                if hasattr(candidate, "content"):
                    for j, part in enumerate(candidate.content.parts):
                        logger.info(f"  Part {j}: {part}")

                        if hasattr(part, "text"):
                            logger.info(f"    TEXT: {part.text}")

                        if hasattr(part, "function_call"):
                            logger.info("    FUNCTION CALL DETECTED")
                            logger.info(f"    NAME: {part.function_call.name}")
                            logger.info(f"    ARGS: {part.function_call.args}")

        # -------------------------
        # RETURN PROCESSING
        # -------------------------
        result = Invio_risposta(response, chat)

        logger.info("FINAL RESPONSE GENERATED SUCCESSFULLY")
        logger.info("========================================")

        return result

    except Exception as e:
        logger.error("🔥 ERROR OCCURRED DURING GEMINI CALL")

        logger.error("TYPE:")
        logger.error(type(e))

        logger.error("STRING:")
        logger.error(str(e))

        logger.error("TRACEBACK:")
        logger.error(traceback.format_exc())

        # Try extracting HTTP/grpc metadata if available
        if hasattr(e, "metadata"):
            logger.error("METADATA:")
            logger.error(e.metadata)

        if hasattr(e, "response"):
            logger.error("RAW ERROR RESPONSE:")
            logger.error(e.response)

        return {
            "error": str(e),
            "type": str(type(e)),
            "trace": traceback.format_exc()
        }