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
                            
    Rispondi usando gli ordini contenuti nel database
    
    Il database è strutturato in questo modo: 

    TABELLE:

    clienti(id, nome, email, indirizzo)
    corrieri(id, nome)
    carte(id, cliente_id, last4, circuito, scadenza, token)
    ordini(id, data_spedizione, data_arrivo, tracking, stato, origine, cliente_id, corriere_id, carta_id)
    prodotti(id,nome,descrizione,quantita_in_magazzino,prezzo)
    ordini_prodotti(ordine_id,prodotto_id,quantita)
                                 
    RELAZIONI:
                                 
    - ordini.cliente_id → clienti.id
    - ordini.corriere_id → corrieri.id
    - ordini.carta_id → carte.id
    - ordini_prodotti.ordine_id -> ordini.id
    - ordini_prodotti.prodotto_id -> prodotti.id

    ESEMPI:

    - " Chi è il corriere del mio ordine con ID 6" -> SELECT nome FROM corrieri c JOIN ordini o ON c.corriere_id = o.corriere_id WHERE o.id='ORD006'
    
    - "Tempo medio di spedizione del corriere Bartolini" -> SELECT AVG(data_arrivo - data_spedizione) FROM ordini JOIN corrieri ON ordini.corriere_id = corrieri.id WHERE corrieri.nome = 'Bartolini';
    
    - "Quale è il prezzo del mio prodotto con id 18" -> SELECT prezzo FROM prodotti p JOIN ordini_prodotto op ON op.prodotto_id=p.id AND op.ordine_id= 18

    - "Quale è la quantita rimasta nel magazzino del prodotto  Smartphone X10" -> SELECT   quantita_in_magazzino FROM prodotti WHERE nome='Smartphone X10'
    
    
    


    Se NON serve il database e la richiesta non riguarda un ordine:
    -rispondi normalmente
    
    
    Rispondi sempre in modo professionale 
    - Inizia con : "Salve Gentile Cliente..."
    - Chiudi con : GG +39 123231312
    - Rispondi anche alle richieste nelle altre lingue, usando la lingua utilizzata dal mittente"""

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











