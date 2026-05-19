import { useState } from "react";
import "./App.css";
import { ArrowUp, Brain, LogOut } from "lucide-react";
import {Chart as ChartJS,CategoryScale,LinearScale,PointElement,LineElement,BarElement,ArcElement,Tooltip, Legend
} from "chart.js";

ChartJS.register(CategoryScale,LinearScale,PointElement,LineElement,BarElement,ArcElement,
  Tooltip,
  Legend
);
import DynamicChart from "./DynamicChart.jsx";
// ─── Utenti di esempio (sostituisci con una vera chiamata API) ───────────────
const FAKE_USERS = [
  { email: "user@demo.it", password: "1234", name: "Mario" },
];

// ─── Schermata di Login ──────────────────────────────────────────────────────
function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = () => {
    const found = FAKE_USERS.find(
      (u) => u.email === email && u.password === password
    );
    if (found) {
      onLogin(found);
    } else {
      setError("Email o password non corretti.");
    }
  };

  return (
    <div style={styles.container}>
      <Brain size={30} color="#2563EB" />
      <h2 style={styles.title}>Assistente AI E-Commerce</h2>

      <div style={styles.loginBox}>
        <p style={styles.loginTitle}>Accedi</p>

        <div style={styles.field}>
          <label style={styles.label}>Email</label>
          <input
            style={styles.input}
            type="email"
            placeholder="user@demo.it"
            value={email}
            onChange={(e) => { setEmail(e.target.value); setError(""); }}
            onKeyDown={(e) => e.key === "Enter" && handleLogin()}
          />
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Password</label>
          <input
            style={styles.input}
            type="password"
            placeholder="••••"
            value={password}
            onChange={(e) => { setPassword(e.target.value); setError(""); }}
            onKeyDown={(e) => e.key === "Enter" && handleLogin()}
          />
        </div>

        {error && <p style={styles.error}>{error}</p>}

        <button style={styles.loginBtn} onClick={handleLogin}>
          Accedi
        </button>

        <p style={styles.hint}>Demo: user@demo.it / 1234</p>
      </div>
    </div>
  );
}








// ─── App principale ──────────────────────────────────────────────────────────
export default function App() {
  const [user, setUser] = useState(null); // null = non autenticato
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  // Se non loggato, mostra login
  if (!user) {
    return <LoginPage onLogin={(userData) => setUser(userData)} />;
  }

  async function sendMessage() {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    const userid = user.email; // usa l'email reale dell'utente
    setIsTyping(true);

    try {
      const res = await fetch("https://chat-bot-ordinidb-2.onrender.com/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, user_id: userid }),
      });

      const data = await res.json();
      const botMsg = { role: "bot", text: data.response, chart: data.chart };

      setIsTyping(false);
      setMessages([...messages, userMsg, botMsg]);
      setInput("");
    } catch (error) {
      console.error("Errore:", error);
      setIsTyping(false);
    }
  }

  const invio_automatico = (e) => {
    if (e.key === "Enter") sendMessage();
  };

 return (
   <div style={styles.container}>
    
    {/*HEADER */}
    <div style={styles.header}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <Brain size={30} color="#2563EB"/>
        <h2 style={styles.title}>Assistente AI E-Commerce</h2>
      </div>
      <div style={styles.userInfo}>
        <button
          style={styles.logoutBtn}
          onClick={() => { setUser(null); setMessages([]); }}
        >
          <LogOut size={20} color="#000000"/>
        </button>
      </div>
    </div>

    {/*blocco centrale */}
    <div style={{...styles.mainContent, flexWrap: "wrap"}}>
      
      {/* Chat */}
      <div style={{ flex: "1 1 100%", display: "flex", flexDirection: "column", gap: "10px" }}>
        <div style={styles.chatBox}>
          {messages.map((m, i) => (
            <div
              key={i}
              style={{
                ...styles.message,
                alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                background: m.role === "user" ? "#2563EB" : "#F1F5F9",
                color: m.role === "user" ? "white" : "#0F172A",
              }}
            >
              {m.text}
            </div>
          ))}
          
          {isTyping && (
            <div style={{ ...styles.message, alignSelf: "flex-start", background: "#334155", display: "flex", gap: "6px" }}>
              <span className="dot"></span><span className="dot"></span><span className="dot"></span>
            </div>
          )}
        </div>

        {/* zona input */}
        <div style={styles.inputArea}>
          <input
            style={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={invio_automatico}
            placeholder="Scrivi un messaggio..."
          />
          <button style={styles.button} onClick={sendMessage}>
            <ArrowUp size={18} />
          </button>
        </div>
      </div>

    </div> 

    {/* grafico sotto la chat */}
    {messages.some((m) => m.chart?.enabled) && (
      <div style={styles.graficiArea}>
        {messages.map((m, i) =>
          m.chart?.enabled ? (
            <div key={i} style={styles.grafico}>
              <DynamicChart chart={m.chart} />
            </div>
          ) : null
        )}
      </div>
    )}
  </div>
);
}
        
      


// ─── Stili ───────────────────────────────────────────────────────────────────
const styles = {
  container: {
    maxWidth: "1300px",
    margin: "50px auto",
    fontFamily: "Arial",
    padding: "0 20px",
    backgroundColor: "#bcebf3",
  },
  grafico: {
    width: "100%",
    height: "300px",
    margin: "0 auto",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    borderRadius: "20px",
    padding: "20px",
    backgroundColor: "#ffffff",
     boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
  },
  graficoArea: {
    display: "flex",
    flexDirection: "column",
    gap: "20px",
    marginTop: "20px",
    width: "100%",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: "10px",
  },
  title: {
    color: "#0F172A",
    fontSize: "22px",
    fontWeight: "600",
    margin: 0,
  },
  userInfo: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  userName: {
    fontSize: "14px",
    color: "#0F172A",
  },
  logoutBtn: {
    background: "transparent",
    border: "1px solid #94a3b8",
    borderRadius: "8px",
    padding: "4px 8px",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    color: "#0F172A",
  },
  // Login
  loginBox: {
    background: "#ffffff",
    borderRadius: "20px",
    padding: "32px",
    maxWidth: "380px",
    margin: "0 auto",
    boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
  },
  loginTitle: {
    fontSize: "20px",
    fontWeight: "600",
    color: "#0F172A",
    marginBottom: "20px",
  },
  field: {
    marginBottom: "14px",
  },
  label: {
    display: "block",
    fontSize: "16px",
    color: "#0F172A",
    marginBottom: "5px",
  },
  error: {
    fontSize: "13px",
    color: "#dc2626",
    marginBottom: "10px",
  },
  hint: {
    fontSize: "12px",
    color: "#94a3b8",
    textAlign: "center",
    marginTop: "12px",
  },
  loginBtn: {
    width: "100%",
    padding: "11px",
    backgroundColor: "#2563EB",
    color: "white",
    border: "none",
    borderRadius: "12px",
    fontSize: "15px",
    fontWeight: "600",
    cursor: "pointer",
  },
  mainContent: {
    display: "flex",
    gap: "20px",              // Spazio tra chat e grafico
    alignItems: "flex-start", // Allinea in alto
    width: "100%",
  },
  // Chat
  chatBox: {
    flex: 2,
    display: "flex",
    flexDirection: "column",
    border: "1px solid #D6E6F5",
    borderRadius: "20px",
    padding: "20px",
    height: "500px",
    overflowY: "auto",
    marginBottom: "15px",
    backgroundColor: "#ffffff",
    boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
  },
  message: {
    padding: "12px 16px",
    borderRadius: "18px",
    margin: "8px 0",
    maxWidth: "75%",
    fontSize: "15px",
    lineHeight: "1.5",
    boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
    wordBreak: "break-word",
  },
  inputArea: {
    display: "flex",
    gap: "10px",
    padding: "10px",
    backgroundColor: "#FFFFFF",
    borderRadius: "30px",
    border: "1px solid #D6E6F5",
    boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
  },
  input: {
    flex: 1,
    padding: "10px 15px",
    border: "none",
    outline: "none",
    fontSize: "16px",
    backgroundColor: "transparent",
    color: "#0F172A",
  },
  button: {
    backgroundColor: "#2563EB",
    color: "white",
    border: "none",
    borderRadius: "50%",
    width: "40px",
    height: "40px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    transition: "background 0.2s",
  },
};