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
      <h2>Assistente AI E-Commerce</h2>

      <div style={styles.chatBox}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              ...styles.message,
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              background: m.role === "user" ? "#DCF8C6" : "#EEE"
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
              background: "#EEE",
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
        <button onClick={sendMessage}> <ArrowUp size={18}></ArrowUp></button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: "800px",
    margin: "50px auto",
    fontFamily: "Arial",
    padding: "0 20px"
  },
  chatBox: {
    display: "flex",
    flexDirection: "column",
    border: "1px solid #e0e0e0",
    borderRadius: "20px",
    padding: "20px",
    height: "500px",
    overflowY: "auto",
    marginBottom: "15px",
    backgroundColor: "#f9f9f9",
    boxShadow: "0 4px 15px rgba(0,0,0,0.1)"
  },
  message: {
    padding: "8px",
    borderRadius: "8px",
    margin: "5px 0",
    maxWidth: "70%"
  },
  inputArea: {
    display: "flex",
    gap: "5px"
  },
  input: {
    flex: 1,
    padding: "8px"
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
