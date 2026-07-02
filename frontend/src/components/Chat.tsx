import { FormEvent, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import "./Chat.css";
import PropertyCard, { Property } from "./PropertyCard";
import MapComponent from "./MapComponent";

interface Message {
  role: "user" | "assistant";
  content: string;
  toolTrace?: ToolTraceEntry[];
  properties?: Property[];
}

interface ToolTraceEntry {
  tool: string;
  args: Record<string, unknown>;
  result_summary: string;
}

const EXAMPLE_PROMPTS = [
  "3BHK under ₹1.2 Cr in Whitefield, Bangalore. Good schools and metro nearby.",
  "My office is in Electronic City. Which shortlisted options have the shortest commute?",
  "Show me cheaper 2BHK options in Marathahalli under ₹80 lakh.",
];

function generateSessionId(): string {
  return crypto.randomUUID();
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your property discovery assistant. To help you find the perfect home in India, which city are you looking to buy in?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(generateSessionId);
  const [showTools, setShowTools] = useState(false);
  const [activePropertyId, setActivePropertyId] = useState<string | null>(null);
  const [isMapOpen, setIsMapOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Compute all properties from all messages to show on the map
  const mapProperties = messages
    .flatMap((m) => m.properties || [])
    .filter((v, i, a) => v && v.id && a.findIndex(t => (t.id === v.id)) === i);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(text: string) {
    if (!text.trim() || loading) return;

    const userMessage = text.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage, session_id: sessionId }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Request failed");
      }

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply,
          toolTrace: data.tool_trace,
          properties: data.properties,
        },
      ]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `**Error:** ${msg}. Make sure the backend is running and \`GEMINI_API_KEY\` is set.`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    sendMessage(input);
  }

  async function handleReset() {
    await fetch(`/api/reset?session_id=${sessionId}`, { method: "POST" });
    setMessages([
      {
        role: "assistant",
        content: "Conversation reset. Which city are you interested in looking for a home in?",
      },
    ]);
    setIsMapOpen(false);
    setActivePropertyId(null);
  }

  return (
    <div className={`chat-layout ${isMapOpen ? "map-active" : ""}`}>
      <div className="chat-container">
        <div className="chat-toolbar">
          {mapProperties.length > 0 && (
            <button type="button" className="btn-secondary" onClick={() => setIsMapOpen((v) => !v)}>
              {isMapOpen ? "Hide Map" : "Show Map"}
            </button>
          )}
          <button type="button" className="btn-secondary" onClick={() => setShowTools((v) => !v)}>
            {showTools ? "Hide" : "Show"} tool trace
          </button>
          <button type="button" className="btn-secondary" onClick={handleReset}>
            New conversation
          </button>
        </div>

      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="message-label">{msg.role === "user" ? "You" : "Agent"}</div>
            <div className="message-body">
              {msg.role === "assistant" ? (
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              ) : (
                <p>{msg.content}</p>
              )}
            </div>
            {msg.properties && msg.properties.length > 0 && (
              <div className="properties-grid">
                {msg.properties.map((prop, j) => (
                  <PropertyCard 
                    key={j} 
                    property={prop} 
                    onViewLocation={(p) => {
                      setActivePropertyId(p.id);
                      setIsMapOpen(true);
                    }}
                  />
                ))}
              </div>
            )}
            {showTools && msg.toolTrace && msg.toolTrace.length > 0 && (
              <div className="tool-trace">
                <strong>Tools used:</strong>
                <ul>
                  {msg.toolTrace.map((t, j) => (
                    <li key={j}>
                      <code>{t.tool}</code> — {t.result_summary}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message assistant loading">
            <div className="message-label">Agent</div>
            <div className="message-body">
              <span className="dots">Searching and reasoning</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="examples">
        {EXAMPLE_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            className="example-chip"
            onClick={() => sendMessage(prompt)}
            disabled={loading}
          >
            {prompt}
          </button>
        ))}
      </div>

      <form className="input-form" onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. 3BHK under 1.2 Cr in Whitefield, near metro, good schools..."
          rows={2}
          disabled={loading}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage(input);
            }
          }}
        />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
      
      <div className={`map-side ${isMapOpen ? "open" : "closed"}`}>
        <div className="map-side-header">
          <h3>Interactive Map</h3>
          <button className="btn-close-map" onClick={() => setIsMapOpen(false)} aria-label="Close Map">
            ✕
          </button>
        </div>
        <div className="map-side-content">
          {isMapOpen && (
            <MapComponent 
              properties={mapProperties} 
              activePropertyId={activePropertyId} 
              isOpen={isMapOpen}
              onMarkerClick={(p) => setActivePropertyId(p.id)} 
            />
          )}
          <button className="mobile-close-map-fab" onClick={() => setIsMapOpen(false)}>
            ✕ Close Map
          </button>
        </div>
      </div>
    </div>
  );
}
