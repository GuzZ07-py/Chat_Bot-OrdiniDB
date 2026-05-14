from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import google.generativeai as genai
import psycopg2

# Recupero chiave dalle varibile impostate su Render,come anche per le credenziali per accedere al database su Supabase
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

with open("guida_database" , "r" , encoding="utf-8") as f:
    database_guida= f.read()
    
def Invio_risposta(response,chat):
    for part in response.candidates[0].content.parts:
        if hasattr(part, "function_call") and part.function_call:

            call = part.function_call

            if call.name == "esegui_query":
                query = call.args["query"]

                risultato = esegui_query(query)
                
                response=chat.send_message({
                    "function_response":{
                        "name": "esegui_query",
                        "response": {"result":risultato}
                    }
                })
                return {"response": response.text}
    #se è domanda normale
    return{"response": response.text}

DATABASE_URL=os.getenv("DATABASE_URL")

def esegui_query(query: str):
    #sicurezza
    query_lower = query.lower()

    if not query_lower.strip().startswith("select"):
        return "Solo query SELECT consentite."
    
    #codice per query
    try:
        conn=psycopg2.connect(DATABASE_URL)
        cursor=conn.cursor()
        
        cursor.execute(query)
        result=cursor.fetchall()

        
        #print ("QUERY:",query)
        
        return str(result)
    
    except Exception as e:
        return f"Errore SQL:{e}"
    
    finally:
        conn.close()

SYSTEM_PROMT="""
    Se il messaggio che ricevi riguarda un ordine del databse:
    - DEVI OBBLIGATORIAMENTE chiamare la funzione esegui_query
    - NON puoi rispondere senza usare la funzione
    - NON inventare dati
    - genera SOLO query SQL SELECT valide
                            
    Usa questa guida del Database: {database_guida}
    
    Se la richiesta rigurda un ordine:
    - Inizia con : "Salve Gentile Cliente..."
    - Chiudi con : Assistenza di UniLira , Tel: +39 123231312 
   
    Se invece la richiesta NON rigurda un ordine rispondi con:
    - Rispondi Normalmente senza Gentile Cliente e senza Assistenza UniLira

    In OGNI risposta rispondi in modo professionale:
    - Rispondi anche alle richieste nelle altre lingue, usando la lingua utilizzata dal mittente
    
    """

TOOLS=[ {
        "function_declarations": [
            {
                "name": "esegui_query",
                "description": "Esegue una query SQL SELECT sul database ordini",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query SQL da eseguire"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    }]

model = genai.GenerativeModel(model_name="gemini-2.5-pro",
                              tools=TOOLS,
                              system_instruction=SYSTEM_PROMT)



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions={}

class ChatRequest(BaseModel):
    message: str
    user_id: str

@app.get("/")
def home():
    return {"status": "Chatbot Online"}


@app.post("/chat")
async def chat(req: ChatRequest):
    
    user_id=req.user_id
    if user_id not in sessions: #salvo le sessioni, cosi ogni utente ha il suo contesto
        sessions[user_id]=model.start_chat(enable_automatic_function_calling=True)
    
    chat = sessions[user_id]

    response = chat.send_message(req.message)
    
    
    
    print(response.candidates[0].content.parts)

    #pulizia  risposta


    return Invio_risposta(response,chat)











