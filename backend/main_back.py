from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import mysql.connector
genai.configure(api_key="AIzaSyAh_xHfNUCbCmic9CwArAqW6Y8ibyE7nbE")

def controllo(response,chat):
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

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="ordini_db_tesina"
    )

def esegui_query(query: str):
    #sicurezza
    query_lower = query.lower()

    if not query_lower.strip().startswith("select"):
        return "Solo query SELECT consentite."
    
    #codice per query
    try:
        conn=get_db_connection()
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
   
    RELAZIONI:
                                 
    - ordini.cliente_id → clienti.id
    - ordini.corriere_id → corrieri.id
    - ordini.carta_id → carte.id

    ESEMPI DI QUERY SQL:

    -"Chi è il corriere del mio ordine con id 006" -> SELECT nome FROM corrieri c JOIN ordini o ON c.id = o.corriere_id WHERE o.id="006"
    
    -"Tempo medio di spedizione del corriere Bartolini" -> SELECT AVG(DATEDIFF(data_arrivo, data_spedizione)) FROM ordini JOIN corrieri ON ordini.corriere_id = corrieri.id WHERE corrieri.nome = 'Bartolini';
    
    
    


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

@app.post("/chat")
async def chat(req: ChatRequest):
    
    user_id=req.user_id
    if user_id not in sessions: #salvo le sessioni, cosi ogni utente ha il suo contesto
        sessions[user_id]=model.start_chat(enable_automatic_function_calling=True)
    
    chat = sessions[user_id]

    response = chat.send_message(req.message)
    
    
    
    print(response.candidates[0].content.parts)

    #pulizia  risposta


    return controllo(response,chat)


