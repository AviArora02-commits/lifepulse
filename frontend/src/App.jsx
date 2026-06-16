import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  ArrowRight,
  BadgeCheck,
  BrainCircuit,
  Clock3,
  FileText,
  Gauge,
  Languages,
  LayoutDashboard,
  MessageCircle,
  Network,
  PhoneCall,
  Radar,
  ShieldCheck,
  Sparkles,
  Type,
  Zap
} from "lucide-react";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "";
const scenarios = [
  { id: "upi", label: "Stuck UPI", icon: Zap, text: "My UPI of Rs 8,500 to Rahul is stuck since yesterday" },
  { id: "statement", label: "Visa statement", icon: FileText, text: "Need 6 month bank statement for visa application" },
  { id: "frustrated", label: "RM handoff", icon: PhoneCall, text: "I've been waiting 3 days this is ridiculous" },
  { id: "life", label: "Life event", icon: Radar, text: "proactive life event check" }
];
const graphStates = ["INTAKE", "CLASSIFY", "ROUTE", "EXECUTE", "VERIFY", "RESOLVE", "ESCALATE"];

const demoResponses = {
  transaction: {
    session: { session_id: "static-upi", current_state: "CLOSE", rm_brief: null },
    messages: [
      { sender: "customer", type: "text", text: "My UPI of Rs 8,500 to Rahul is stuck since yesterday" },
      { sender: "agent", type: "text", text: "I found the UPI payment of Rs 8,500 to Rahul Verma. It is stuck at NPCI, so I filed dispute SR260616A91C and queued reversal REV-48C21F9A. Expected resolution: 2 hours." },
      { sender: "system", type: "action", text: "NPCI dispute filed: SR260616A91C" },
      { sender: "system", type: "receipt", text: "Resolution receipt generated", payload: { done: ["Fetched transaction UPI42698173", "Filed NPCI dispute SR260616A91C", "Queued reversal REV-48C21F9A", "Simulated SMS confirmation sent"], sr_number: "SR260616A91C" } }
    ]
  },
  statement: {
    session: { session_id: "static-doc", current_state: "CLOSE", rm_brief: null },
    messages: [
      { sender: "customer", type: "text", text: "Need 6 month bank statement for visa application" },
      { sender: "agent", type: "text", text: "Your 6-month bank statement for visa is ready as a digitally signed PDF. I have delivered it here and sent a copy to your registered email." },
      { sender: "system", type: "document", text: "Statement ready", payload: { offer: "I can also generate an ITR certificate for your visa file." } },
      { sender: "system", type: "receipt", text: "Resolution receipt generated", payload: { done: ["Generated DOC-91F2AC", "Digitally signed PDF", "Delivered to chat", "Simulated email delivery"] } }
    ]
  },
  escalation: {
    session: {
      session_id: "static-rm",
      current_state: "CLOSE",
      rm_brief: {
        customer_snapshot: { name: "Priya Sharma", tenure_years: 7, product_count: 2, ltv_segment: "premium" },
        issue_summary: "Customer is frustrated after waiting 3 days. They need acknowledgement, ownership, and a clear time commitment.",
        do_not_say: ["Please visit the branch", "Repeat the full issue again", "It is only a system delay"],
        recommended_resolution: "Take ownership, confirm SR, offer callback or immediate RM chat, and commit to a 6-hour update.",
        sentiment_score: 0.88
      }
    },
    messages: [
      { sender: "customer", type: "text", text: "I've been waiting 3 days this is ridiculous" },
      { sender: "agent", type: "text", text: "I am sorry you have had to wait. I am taking ownership now and preparing a human handoff with the full context, so you do not need to repeat yourself." },
      { sender: "system", type: "escalation", text: "Priority SR created: SR260616B7E2", payload: {} },
      { sender: "system", type: "receipt", text: "Escalation receipt generated", payload: { done: ["Created priority SR SR260616B7E2", "Prepared RM brief", "Notified RM dashboard"], sr_number: "SR260616B7E2" } }
    ]
  },
  life: {
    session: { session_id: "static-life", current_state: "CLOSE", rm_brief: null },
    messages: [
      { sender: "customer", type: "text", text: "proactive life event check" },
      { sender: "agent", type: "text", text: "Congratulations - it looks like you may have recently welcomed a baby. Am I right?" },
      { sender: "system", type: "recommendation", text: "Life event recommendations", payload: { why: ["Repeated baby-care purchases over the last 3 months", "Spouse recently appears as FD nominee", "Customer browsed child-plan calculator twice"], products: [
        { name: "Sukanya Samriddhi Yojana", summary: "Government-backed savings for a girl child's future." },
        { name: "Child Term Plan", summary: "Protects the family if income is disrupted." },
        { name: "Education SIP", summary: "Starts a small monthly investment for future education costs." }
      ] } }
    ]
  }
};

function endpoint(path) {
  return `${API}${path}`;
}

function staticDemo(message) {
  const m = message.toLowerCase();
  if (m.includes("upi") || m.includes("stuck")) return demoResponses.transaction;
  if (m.includes("statement") || m.includes("visa")) return demoResponses.statement;
  if (m.includes("ridiculous") || m.includes("waiting") || m.includes("human")) return demoResponses.escalation;
  if (m.includes("life") || m.includes("proactive") || m.includes("baby")) return demoResponses.life;
  return {
    session: { session_id: "static-general", current_state: "CLOSE", rm_brief: null },
    messages: [
      { sender: "customer", type: "text", text: message },
      { sender: "agent", type: "text", text: "I can help with stuck payments, statements, escalation, or proactive life-event review. Pick a judge scenario to see the full demo." }
    ]
  };
}

function Chip({ children, tone = "green" }) {
  return <span className={`chip ${tone}`}>{children}</span>;
}

function Message({ message }) {
  if (message.type === "action") return <div className="system"><Chip>{message.text}</Chip></div>;
  if (message.type === "escalation") return <div className="system"><Chip tone="red">{message.text}</Chip></div>;
  if (message.type === "document") return <div className="delivery-card"><b>Digitally signed statement</b><p>{message.text}</p><small>{message.payload?.offer}</small><button>Download PDF</button></div>;
  if (message.type === "otp") return <div className="delivery-card compact"><b>Inline OTP gate</b><input placeholder="Enter OTP" defaultValue="123456" /><button>Verify</button></div>;
  if (message.type === "recommendation") {
    return <div className="recommendation-card">
      <b>New baby signal detected</b>
      {message.payload.products.map((p) => <p key={p.name}><span>{p.name}</span>{p.summary}</p>)}
      <details><summary>Why are you telling me this?</summary>{message.payload.why.join("; ")}</details>
      <button>Start with one OTP</button>
    </div>;
  }
  if (message.type === "receipt") return <div className="delivery-card compact"><b>Resolution receipt</b><p>{message.payload.done?.join(" - ")}</p><small>SR: {message.payload.sr_number || "Not required"}</small></div>;
  return <div className={`bubble ${message.sender === "customer" ? "me" : "agent"}`}>{message.text}</div>;
}

function Hero() {
  return <section className="hero">
    <div className="hero-copy">
      <div className="eyebrow"><Sparkles size={16} /> Agentic AI and Emerging Tech for Banking</div>
      <h1>LifePulse turns branch work into resolved conversations.</h1>
      <p>Proactive life-event intelligence, autonomous resolution agents, and RM warm handoff in one auditable banking command layer.</p>
      <div className="hero-actions">
        <a href="#demo" className="primary">Try live demo <ArrowRight size={17} /></a>
        <a href="#architecture" className="secondary">View architecture</a>
      </div>
    </div>
    <div className="neural-panel" aria-label="Agent orchestration preview">
      <div className="pulse-core"><BrainCircuit size={56} /><span>LifePulse</span></div>
      {graphStates.slice(0, 6).map((state, index) => <span className={`node n${index}`} key={state}>{state}</span>)}
      <svg viewBox="0 0 620 420" aria-hidden="true">
        <path d="M310 210 C185 115 128 72 66 70" />
        <path d="M310 210 C420 94 470 58 556 76" />
        <path d="M310 210 C168 214 105 216 60 255" />
        <path d="M310 210 C455 198 520 210 575 260" />
        <path d="M310 210 C240 330 196 366 124 360" />
        <path d="M310 210 C405 330 462 366 540 350" />
      </svg>
    </div>
  </section>;
}

function MetricStrip({ metrics }) {
  return <section className="metric-strip">
    <article><span>{metrics?.avg_resolution_time || "4 minutes"}</span><p>LifePulse median resolution</p></article>
    <article><span>{metrics?.branch_visits_deflected || 176}</span><p>Branch visits deflected today</p></article>
    <article><span>0 repeats</span><p>RM receives full context brief</p></article>
    <article><span>RBI-ready</span><p>Every action has audit metadata</p></article>
  </section>;
}

function ChatWindow({ language, largeText, onEscalation }) {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([{ sender: "agent", text: "I am LifePulse. Pick a judge scenario or message me like a customer.", type: "text" }]);
  const [state, setState] = useState("INTAKE");
  const [text, setText] = useState("");
  const send = async (body) => {
    const customerMessage = body || text;
    if (!customerMessage.trim()) return;
    setText("");
    let data;
    try {
      const res = await fetch(endpoint("/api/chat/message"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, customer_id: "CUST1001", message: customerMessage, language })
      });
      if (!res.ok) throw new Error("api unavailable");
      data = await res.json();
    } catch {
      data = staticDemo(customerMessage);
    }
    setSessionId(data.session.session_id);
    setState(data.session.current_state);
    setMessages(data.session.messages);
    if (data.session.rm_brief) onEscalation(data.session.rm_brief);
  };
  return <section className={`phone ${largeText ? "large" : ""}`}>
    <header>
      <div><MessageCircle size={19} /><b>Customer channel</b></div>
      <span>{state}</span>
    </header>
    <div className="scenario-grid">{scenarios.map((s) => {
      const Icon = s.icon;
      return <button key={s.id} onClick={() => send(s.text)}><Icon size={18} />{s.label}</button>;
    })}</div>
    <main>{messages.map((m, i) => <Message key={i} message={m} />)}<div className="typing"><i></i><i></i><i></i></div></main>
    <footer><input value={text} onChange={(e) => setText(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} placeholder="Message LifePulse" /><button onClick={() => send()}>Send</button></footer>
  </section>;
}

function RMDashboard({ escalation, metrics }) {
  const [audit, setAudit] = useState([]);
  useEffect(() => {
    const fallbackAudit = [
      { agent_id: "orchestrator", action_type: "state_transition", confidence: 1 },
      { agent_id: "intent_classifier", action_type: "transaction_dispute", confidence: .92 },
      { agent_id: "transaction_resolver", action_type: "resolve", confidence: .91 },
      { agent_id: "audit_logger", action_type: "receipt", confidence: 1 }
    ];
    const load = () => fetch(endpoint("/api/audit")).then((r) => r.json()).then(setAudit).catch(() => setAudit(fallbackAudit));
    const id = setInterval(load, 2500);
    load();
    return () => clearInterval(id);
  }, []);
  return <section className="dashboard">
    <div className="dash-head"><LayoutDashboard /> RM Command Center <Chip tone="blue">Live</Chip></div>
    <div className="ops-grid">
      <article><b>{metrics?.resolved || 286}</b><span>Resolved today</span></article>
      <article><b>{metrics?.escalated || 31}</b><span>Warm handoffs</span></article>
      <article><b>92%</b><span>Automation confidence</span></article>
    </div>
    <h3>Active escalation brief</h3>
    {escalation ? <article className="rm-card active">
      <div className="rm-top"><b>{escalation.customer_snapshot.name}</b><Chip tone={escalation.sentiment_score > 0.8 ? "red" : "amber"}>Sentiment {Math.round(escalation.sentiment_score * 100)}%</Chip></div>
      <p>{escalation.issue_summary}</p>
      <p><b>Do not say:</b> {escalation.do_not_say.join(", ")}</p>
      <p><b>Recommended:</b> {escalation.recommended_resolution}</p>
      <button><PhoneCall size={16} /> Take this conversation</button>
    </article> : <article className="rm-card empty"><Clock3 /> Try the RM handoff scenario to light up the brief.</article>}
    <h3>Immutable audit stream</h3>
    <div className="audit">{audit.slice(-8).reverse().map((a, i) => <p key={i}><ShieldCheck size={14} /> {a.agent_id} / {a.action_type} / {Math.round(a.confidence * 100)}%</p>)}</div>
  </section>;
}

function Architecture() {
  return <section className="architecture" id="architecture">
    <div className="section-title"><Network /> Orchestration layer</div>
    <div className="state-row">{graphStates.map((n) => <span key={n}>{n}</span>)}</div>
    <div className="capability-grid">
      <article><BadgeCheck /><b>Consent gates</b><p>OTP before account-changing actions, with policy limits for high-value reversals.</p></article>
      <article><Gauge /><b>Confidence control</b><p>Low-confidence recommendations queue for RM review instead of customer action.</p></article>
      <article><ShieldCheck /><b>Audit trail</b><p>Agent, customer, action, confidence, and approval metadata are written per action.</p></article>
    </div>
  </section>;
}

function App() {
  const [language, setLanguage] = useState("en");
  const [largeText, setLargeText] = useState(false);
  const [escalation, setEscalation] = useState(null);
  const [metrics, setMetrics] = useState(null);
  useEffect(() => {
    const tick = () => fetch(endpoint("/api/metrics/live")).then((r) => r.json()).then(setMetrics).catch(() => setMetrics({
      avg_resolution_time: "4 minutes",
      branch_visits_deflected: 176,
      resolved: 286,
      escalated: 31
    }));
    tick();
    const id = setInterval(tick, 3000);
    return () => clearInterval(id);
  }, []);
  return <div className="app">
    <nav>
      <b><Activity /> LifePulse</b>
      <span>Branch deflection AI</span>
      <button onClick={() => setLanguage(language === "en" ? "hi" : "en")}><Languages size={16} /> {language.toUpperCase()}</button>
      <button onClick={() => setLargeText(!largeText)}><Type size={16} /> Large text</button>
    </nav>
    <Hero />
    <MetricStrip metrics={metrics} />
    <section className="workbench" id="demo">
      <ChatWindow language={language} largeText={largeText} onEscalation={setEscalation} />
      <RMDashboard escalation={escalation} metrics={metrics} />
    </section>
    <Architecture />
  </div>;
}

export default App;
createRoot(document.getElementById("root")).render(<App />);
