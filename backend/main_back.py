from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import psycopg2

# Recupero chiave dalle varibile impostate su Render,come anche per le credenziali per accedere al database su Supabase
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

with open("guida_database.md" , "r" , encoding="utf-8") as f:
    database_guida= f.read()
    
def Invio_risposta(response,chat):
    for part in response.candidates[0].content.parts:
        if hasattr(part, "function_call") and part.function_call:

            call = part.function_call
            #print("argomenti: ", call.args)
            if call.name == "esegui_query":
                query = call.args["query"]

                risultato = esegui_query(query)

                tipo_grafico= call.args.get(
                    "tipo_grafico_consigliato"
                )

                asse_x= call.args.get("asse_x")
                asse_y= call.args.get("asse_y")

                response=chat.send_message({
                    "function_response":{
                        "name": "esegui_query",
                        "response": {"result":risultato}
                    }
                })


                asse_x = asse_x.split(".")[-1] if asse_x else None
                asse_y = asse_y.split(".")[-1] if asse_y else None
                return {

                    "response": response.text,

                    # nuovi campi
                    "chart": {
                        "enabled": bool(tipo_grafico),

                        "type": (
                            tipo_grafico.replace(" chart", "")
                            if tipo_grafico
                            else None
                        ),

                        "xAxis": asse_x,
                        "yAxis": asse_y,
                        "data": risultato if risultato else []
                    }
                }
        if getattr(part, "text", None):
            return {
                "response": part.text,
                "chart": {
                    "enabled": False
                }
            }
                


        
        

DATABASE_URL=os.getenv("DATABASE_URL") #RECUPERTO URL

def esegui_query(query: str):
    query_lower = query.lower()
    if not query_lower.strip().startswith("select"):
        return "Solo query SELECT consentite."
    try:
        conn = psycopg2.connect(DATABASE_URL) #APERTURA CONNESSIONE
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Lista di dizionari (per il grafico)
        result_dicts = []
        for row in rows:
            record = {}
            for col, val in zip(columns, row):
                if hasattr(val, 'isoformat'):
                    record[col] = val.isoformat()
                elif isinstance(val, (int, float)):
                    record[col] = float(val)
                else:
                    record[col] = val
            result_dicts.append(record)
        
        return result_dicts  
        
    except Exception as e:
        return f"Errore SQL: {e}"
    finally:
        conn.close()

SYSTEM_PROMT= f"""
    Se il messaggio che ricevi riguarda un ordine del database:
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
                "description": "Esegue query SQL PostgreSQL e può suggerire grafici",
                "parameters": {
                    "type": "object",

                    "properties": {

                        "query": {
                            "type": "string",
                            "description": "Query SQL SELECT PostgreSQL"
                        },

                        "tipo_grafico_consigliato": {
                            "type": "string",
                            "enum": [
                                "line chart",
                                "pie chart",
                                "bar chart"
                            ], 
                            
                            "description": "Grafico consigliato"
                        },

                        "asse_x" : {
                            "type": "string",
                            "description": "Campo Asse x"
                        },

                        "asse_y" : {
                            "type": "string",
                            "description": "Campo Asse y"
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



app = FastAPI() #CREAZIONE CANALE COMUNICAZIONE

app.add_middleware( #PERMESSI PER LA COMUNICAZIONE
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions={}

class ChatRequest(BaseModel): #RICHESTE CHE IL MESSAGGIO DEVE RISPETTARE
    message: str
    user_id: str

@app.get("/")
def home():
    return {"status": "Chatbot Online"}


@app.post("/chat") #CREZIONE DELLA PORTA PRIVATA CHAT 
async def chat(req: ChatRequest):
    
    user_id=req.user_id
    if user_id not in sessions: #salvo le sessioni, cosi ogni utente ha il suo contesto
        sessions[user_id]=model.start_chat(enable_automatic_function_calling=False)
    
    chat = sessions[user_id]

    response = chat.send_message(req.message)
    
    
    
    print(response.candidates[0].content.parts)

    #pulizia  risposta


    return Invio_risposta(response,chat)











