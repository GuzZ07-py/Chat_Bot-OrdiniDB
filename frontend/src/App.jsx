import { useState } from "react";
import "./App.css";
import { ArrowUp } from "lucide-react";
import { Brain } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  async function sendMessage() {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    const userid = "user123";
    setIsTyping(true);
    try {
      const res = await fetch("https://chat-bot-ordinidb-2.onrender.com/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: input, user_id: userid })
      });

      const data = await res.json();
      const botMsg = { role: "bot", text: data.response };

      setIsTyping(false);

      setMessages([...messages, userMsg, botMsg]);
      setInput("");
    } catch (error) {
      console.error("Errore:", error);
    }
    
  }
  
  const invio_automatico = (e) => {
    if (e.key === "Enter")
      sendMessage();
  }
  return (
    <div style={styles.container}>
      <Brain size={25}></Brain>
      <h2 style={styles.title}>Assistente AI E-Commerce</h2>

      <div style={styles.chatBox}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              ...styles.message,
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              background: m.role === "user" ? "#2563EB" : "#F1F5F9",
              color: m.role === "user" ? "white" : "#0F172A"
            }}
          >
            {m.text}
          </div>
        ))}
        {isTyping &&(
          <div
            style={{
              ...styles.message,
              alignSelf: "flex-start",
              background: "#334155",
              display: "flex",
              gap: "6px",
              padding: "12px 16px"
            }}
            >
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
          </div>
        )}
      </div>

      <div style={styles.inputArea}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={invio_automatico}
          placeholder="Scrivi un messaggio..."
          
        />
        <button style={styles.button} onClick={sendMessage}> <ArrowUp size={18}></ArrowUp></button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: "800px",
    margin: "50px auto",
    fontFamily: "Arial",
    padding: "0 20px", //spazio a lato
    backgroundColor: "#EAF4FF"
  },
  title: {
     color: "#0F172A",
    fontSize: "22px",
    fontWeight: "600",
    marginBottom: "10px"
  },
  chatBox: {
    display: "flex",
    flexDirection: "column",
    border: "1px solid #D6E6F5",
    borderRadius: "20px",
    padding: "20px",
    height: "500px",
    overflowY: "auto",
    marginBottom: "15px",
    backgroundColor: "#ffffff",
    boxShadow: "0 4px 15px rgba(0,0,0,0.1)"
  },
  message: {
    padding: "12px 16px",
    borderRadius: "18px", // Bordi molto smussati per un look "bubble"
    margin: "8px 0",
    maxWidth: "75%",      // Un po' più largo visto che il contenitore è aumentato
    fontSize: "15px",
    lineHeight: "1.5",
    boxShadow: "0 1px 2px rgba(0,0,0,0.05)", // Ombra leggerissima sotto i messaggi
    wordBreak: "break-word", // Evita che il testo lungo esca dalla bolla
  },
  inputArea: {
    display: "flex",
    gap: "10px",          // Più spazio tra input e bottone
    padding: "10px",
    backgroundColor: "#FFFFFF",
    borderRadius: "30px", // Barra di input arrotondata (stile WhatsApp/Telegram)
    border: "1px solid #D6E6F5",
    boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
  },
  input: {
    flex: 1,
    padding: "10px 15px",
    border: "none",       // Rimosso bordo interno perché c'è quello dell'inputArea
    outline: "none",      // Rimosso il contorno blu quando clicchi
    fontSize: "16px",
    backgroundColor: "transparent",
    color: "#0F172A"
  },
  button: {
    backgroundColor: "#2563EB", // Blu stile iOS o scegli il tuo colore
    color: "white",
    border: "none",
    borderRadius: "50%",
    width: "40px",
    height: "40px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    transition: "background 0.2s"

  }
  /*dot: {
     width: "8px",
     height: "8px",
     borderRadius: "50%",
     backgroundColor: "#888",
     display: "inline-block",

     animation: "bounce 1.4 infinite ease-in-out"
  },*/
  

};
