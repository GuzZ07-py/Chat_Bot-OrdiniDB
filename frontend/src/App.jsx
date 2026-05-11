import { useState } from "react";

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
  
  return (
    <div style={styles.container}>
      <h2>Chat Demo</h2>

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
              <span style={styles.dot}></span>
              <span style={styles.dot}></span>
              <span style={styles.dot}></span>
          </div>
        )}
      </div>

      <div style={styles.inputArea}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Scrivi un messaggio..."
        />
        <button onClick={sendMessage}>Invia</button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: "500px",
    margin: "50px auto",
    fontFamily: "Arial"
  },
  chatBox: {
    display: "flex",
    flexDirection: "column",
    border: "1px solid #ccc",
    padding: "10px",
    height: "300px",
    overflowY: "auto",
    marginBottom: "10px"
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
  },
  dot: {
     width: "8px",
     height: "8px",
     borderRadius: "50%",
     backgroundColor: "#888",
     display: "inline-block"
  }
};