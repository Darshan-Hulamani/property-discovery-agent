import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import "./Chat.css";
import PropertyCard, { Property } from "./PropertyCard";
import MapComponent from "./MapComponent";

interface Message {
  role: "user" | "assistant";
  content: string;
  toolTrace?: ToolTraceEntry[];
  properties?: Property[];
  failedPrompt?: string;
}

interface ToolTraceEntry {
  tool: string;
  args: Record<string, unknown>;
  result_summary: string;
}

const EXAMPLE_PROMPTS = [
  "3BHK under Rs 1.2 Cr in Whitefield with metro and good schools.",
  "I work in Electronic City. Rank options by commute and family safety.",
  "Find affordable 2BHK homes for rental investment near an IT corridor.",
  "Compare ready-to-move gated communities with strong schools.",
];

function generateSessionId(): string {
  if ("randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function uniqueProperties(messages: Message[]): Property[] {
  const seen = new Set<string>();
  return messages
    .flatMap((message) => message.properties || [])
    .filter((property) => {
      if (!property?.id || seen.has(property.id)) return false;
      seen.add(property.id);
      return true;
    });
}

function shouldShowPropertyCards(userPrompt: string, toolTrace?: ToolTraceEntry[]): boolean {
  const usedSearch = toolTrace?.some((trace) => trace.tool === "search_properties") ?? false;
  if (!usedSearch) return false;

  const prompt = userPrompt.toLowerCase();
  const searchAction = /\b(find|search|recommend|suggest|shortlist|list)\b/.test(prompt);
  const showAction = /\bshow\b/.test(prompt);
  const listingNoun = /\b(homes?|properties|listings?|options?|apartments?|flats?|villas?|communities|projects)\b/.test(prompt);
  const listingConstraint = /\b\d+\s*bhk\b|\bbhk\b|\bunder\b|\bbudget\b|\baffordable\b|\bluxury\b|\bready-to-move\b|\bunder construction\b|\bnear\b/.test(prompt);
  const asksForNewInventory =
    (searchAction && (listingNoun || listingConstraint)) ||
    (showAction && listingNoun) ||
    (listingNoun && listingConstraint);
  const asksForFollowUpAnalysis = [
    "emi",
    "mortgage",
    "loan",
    "commute",
    "distance",
    "travel time",
    "neighbourhood",
    "neighborhood",
    "details",
    "coordinate",
    "coordinates",
    "latitude",
    "longitude",
    "compare",
    "comparison",
  ].some((term) => prompt.includes(term));

  return asksForNewInventory && (!asksForFollowUpAnalysis || listingConstraint);
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Tell me the city, budget, BHK, and what matters most. I will rank homes by fit and explain the trade-offs.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(generateSessionId);
  const [showTools, setShowTools] = useState(false);
  const [activePropertyId, setActivePropertyId] = useState<string | null>(null);
  const [isMapOpen, setIsMapOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const mapProperties = useMemo(() => uniqueProperties(messages), [messages]);
  const bestScore = useMemo(() => {
    return mapProperties.reduce((max, property) => Math.max(max, property.score || 0), 0);
  }, [mapProperties]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
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
      const visibleProperties = shouldShowPropertyCards(userMessage, data.tool_trace)
        ? data.properties
        : [];
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.reply,
          toolTrace: data.tool_trace,
          properties: visibleProperties,
        },
      ]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `**Error:** ${msg}. Check that the backend is running and GEMINI_API_KEY is configured.`,
          failedPrompt: userMessage,
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
        content: "Conversation reset. Which city and budget should we start with?",
      },
    ]);
    setInput("");
    setIsMapOpen(false);
    setActivePropertyId(null);
  }

  return (
    <div className={`chat-layout ${isMapOpen ? "map-active" : ""}`}>
      <section className="advisor-panel" aria-label="Property advisor">
        <div className="chat-toolbar">
          <div className="toolbar-summary">
            <span>{mapProperties.length} shortlisted</span>
            <span>{bestScore ? `${bestScore}/100 best fit` : "No ranking yet"}</span>
          </div>
          <div className="toolbar-actions">
            {mapProperties.length > 0 && (
              <button id="map" type="button" className="btn-secondary" onClick={() => setIsMapOpen((v) => !v)}>
                {isMapOpen ? "Hide map" : "Show map"}
              </button>
            )}
            <button type="button" className="btn-secondary" onClick={() => setShowTools((v) => !v)}>
              {showTools ? "Hide trace" : "Show trace"}
            </button>
            <button type="button" className="btn-secondary" onClick={handleReset}>
              New chat
            </button>
          </div>
        </div>

        <div className="messages" aria-live="polite">
          {messages.map((msg, i) => (
            <article key={`${msg.role}-${i}`} className={`message ${msg.role}`}>
              <div className="message-avatar" aria-hidden="true">
                {msg.role === "user" ? "You" : "AI"}
              </div>
              <div className="message-content">
                <div className="message-label">{msg.role === "user" ? "You" : "Advisor"}</div>
                <div className="message-body">
                  {msg.role === "assistant" ? <ReactMarkdown>{msg.content}</ReactMarkdown> : <p>{msg.content}</p>}
                  {msg.failedPrompt && (
                    <button className="retry-btn" type="button" onClick={() => sendMessage(msg.failedPrompt || "")}>
                      Retry
                    </button>
                  )}
                </div>
                {msg.properties && msg.properties.length > 0 && (
                  <div id="shortlist" className="properties-grid">
                    {msg.properties.map((property) => (
                      <PropertyCard
                        key={property.id}
                        property={property}
                        onViewLocation={(selected) => {
                          setActivePropertyId(selected.id);
                          setIsMapOpen(true);
                        }}
                      />
                    ))}
                  </div>
                )}
                {showTools && msg.toolTrace && msg.toolTrace.length > 0 && (
                  <div className="tool-trace">
                    <strong>Tool trace</strong>
                    <ul>
                      {msg.toolTrace.map((trace, j) => (
                        <li key={`${trace.tool}-${j}`}>
                          <code>{trace.tool}</code> {trace.result_summary}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </article>
          ))}
          {loading && (
            <article className="message assistant loading">
              <div className="message-avatar" aria-hidden="true">
                AI
              </div>
              <div className="message-content">
                <div className="message-label">Advisor</div>
                <div className="thinking-card">
                  <span className="thinking-pulse" />
                  <div>
                    <strong>Ranking the shortlist</strong>
                    <p>Checking budget fit, locality quality, commute signals, and buyer preferences.</p>
                  </div>
                </div>
                <div className="skeleton-stack" aria-hidden="true">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            </article>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="prompt-strip" aria-label="Example prompts">
          {EXAMPLE_PROMPTS.map((prompt) => (
            <button key={prompt} type="button" className="example-chip" onClick={() => sendMessage(prompt)} disabled={loading}>
              {prompt}
            </button>
          ))}
        </div>

        <form className="input-form" onSubmit={handleSubmit}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask for homes by budget, commute, schools, safety, metro, or investment potential..."
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
      </section>

      <aside className={`map-side ${isMapOpen ? "open" : "closed"}`} aria-label="Interactive property map">
        <div className="map-side-header">
          <div>
            <h2>Property map</h2>
            <p>{mapProperties.length ? `${mapProperties.length} homes with coordinates` : "Open after a shortlist"}</p>
          </div>
          <button className="btn-close-map" onClick={() => setIsMapOpen(false)} aria-label="Close map">
            Close
          </button>
        </div>
        <div className="map-side-content">
          {isMapOpen && (
            <MapComponent
              properties={mapProperties}
              activePropertyId={activePropertyId}
              isOpen={isMapOpen}
              onMarkerClick={(property) => setActivePropertyId(property.id)}
            />
          )}
        </div>
      </aside>
    </div>
  );
}
