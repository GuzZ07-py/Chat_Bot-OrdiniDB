import os
import base64
import google.generativeai as genai
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import requests
import urllib.parse
import mysql.connector
# --- CONFIGURAZIONE ---
API_KEY_GEMINI = "AIzaSyAh_xHfNUCbCmic9CwArAqW6Y8ibyE7nbE"


GOOGLE_MAPS_API_KEY="AIzaSyB3eWwYSNSaU2rvuFeXAFRGcyKkY_hK8P4"
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    
]

genai.configure(api_key=API_KEY_GEMINI)


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

        conn.close()

        return str(result)
    
    except Exception as e:
        return f"Errore SQL:{e}"


def stima_consegna(orig, dest):
    try:
        orig = urllib.parse.quote(orig)
        dest = urllib.parse.quote(dest)

        url = "https://maps.googleapis.com/maps/api/distancematrix/json"

        params = {
            "origins": orig,
            "destinations": dest,
            "departure_time": "now",
            "key": GOOGLE_MAPS_API_KEY
        }

        res = requests.get(url, params=params).json()

        elemento = res['rows'][0]['elements'][0]

        distanza = elemento['distance']['text']
        durata = elemento.get('duration_in_traffic', elemento['duration'])['text']

        return distanza, durata

    except Exception as e:
        return None, None

# 1. FUNZIONE COMPLICATA (IL TOOL)
#def traccia_spedizione(id_ordine: str):
    """Cerca lo stato di un ordine leggendo direttamente da Google Sheets."""
    try:
        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)

        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()

        values = result.get('values', [])

        if not values:
            return "Il database ordini è vuoto."

        # Salta intestazione (prima riga)
        for row in values[1:]:
            if len(row) > 0 and row[0].strip().upper() == id_ordine.strip().upper():

                quando_spedito = row[1] if len(row) > 1 else "N/D"
                da_dove = row[2] if len(row) > 2 else "N/D"
                tracking = row[3] if len(row) > 3 else "N/D"
                arrivo = row[4] if len(row) > 4 else "N/D"
                corriere = row[5] if len(row) > 5 else "N/D"
                destinazione = row[6] if len(row) > 6 else "N/D"
                stato = row[7] if len(row) > 7 else "N/D"

                return (
                    f"Ordine {id_ordine}:\n"
                    f"- Spedito: {quando_spedito}\n"
                    f"- Da: {da_dove}\n"
                    f"- Corriere: {corriere}\n"
                    f"- Tracking: {tracking}\n"
                    f"- Arrivo stimato: {arrivo}\n"
                    f"- Indirizzo del Destinatario: {destinazione}\n"
                    f"- Stato della Consegna: {stato}\n"
                )

        return f"Ordine {id_ordine} non trovato."

    except Exception as e:
        return f"Errore nel recupero dati: {e}"

# 2. AUTENTICAZIONE GMAIL

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials5.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
    
# 3. LOGICA PRINCIPALE
def process_last_email():
    
    
    creds=get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    



    # Cerca l'ultima email non letta
    results = service.users().messages().list(userId='me', q='is:unread', maxResults=1).execute()
    messages = results.get('messages', [])

    if not messages:
        print("Nessuna nuova email non letta.")
        return

    msg = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
    
    # Estrazione testo (semplificata)
    payload = msg['payload']
    parts = payload.get('parts')
    body = ""
    if parts:
        data = parts[0]['body'].get('data')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')

    print(f"--- Email Ricevuta ---\n{body}\n----------------------")

    # Inizializza Gemini con la funzione di tracciamento
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash', # La tua versione
        tools=[stima_consegna,esegui_query]
    )
    
    chat = model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message(f"""
    
                                 
    Se l'email riguarda un ordine rispondi con la funzione:
    -esegui_query
                            
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

    ESEMPI:

    - " Chi è il corriere del mio ordine con ID ORD006" -> SELECT nome FROM corrieri c JOIN ordini o ON c.corriere_id = o.corriere_id WHERE o.id="ORD006"
    
    - "Tempo medio di spedizione del corriere Bartolini" -> SELECT AVG(DATEDIFF(data_arrivo, data_spedizione)) FROM ordini JOIN corrieri ON ordini.corriere_id = corrieri.id WHERE corrieri.nome = 'Bartolini';
    
    Rispondi anche alle richieste nelle altre lingue, usando la lingua utilizzata dal mittente,
    
    
    Rispondi sempre ringraziando e in modo professionale. All'inizio di ogni email va detto: Salve Gentile Cliente grazie delle domanda , rispondi e infine chiudi il nome della mia azienda (GG) e il numero di assistenza (+39 2131231242)
    EMAIL:
    {body}
    """)

    #print(f"\n--- Risposta Suggerita da Gemini ---\n{response.text}")
    








    #PARTE DELLA RISPOSTA AUTOMATICA

    risposta_ai=response.text
    
    headers = msg['payload'].get('headers', [])
    subject = next(h['value'] for h in headers if h['name'] == 'Subject')
    sender = next(h['value'] for h in headers if h['name'] == 'From')
    thread_id = msg['threadId']

    # 2. Prepariamo il messaggio email
    message = MIMEText(risposta_ai)
    message['to'] = sender
    message['subject'] = f"Re: {subject}"
    
    # Codifica in base64 richiesta da Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    # 3. Invio effettivo
    try:
        service.users().messages().send(
            userId='me', 
            body={'raw': raw_message, 'threadId': thread_id}
        ).execute()
        print(f"Risposta inviata con successo a: {sender}")
        
        # 4. SEGNA COME LETTA (Importante per non rispondere due volte!)
        service.users().messages().batchModify(
            userId='me', 
            body={'removeLabelIds': ['UNREAD'], 'ids': [messages[0]['id']]}
        ).execute()
        
    except Exception as e:
        print(f"Errore durante l'invio: {e}")
    
    # Opzionale: Segna come letta per non riprocessarla
    # service.users().messages().batchModify(userId='me', body={'removeLabelIds': ['UNREAD'], 'ids': [messages[0]['id']]}).execute()

if __name__ == "__main__":
    process_last_email()