import type { CSSProperties, DragEvent } from "react";
import { useCallback, useRef, useState } from "react";
import { sendChat, uploadDocument, type ChatRole } from "./api";

type Msg = { role: ChatRole; content: string };

export default function App() {
  const [docId, setDocId] = useState<string | null>(null);
  const [docName, setDocName] = useState<string | null>(null);
  const [chunks, setChunks] = useState<number | null>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const onFiles = useCallback(async (files: FileList | null) => {
    if (busy || !files?.length) return;
    const file = files[0];
    setError(null);
    setBusy(true);
    try {
      const r = await uploadDocument(file);
      setDocId(r.id);
      setDocName(r.filename);
      setChunks(r.chunk_count);
      setMessages([]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }, [busy]);

  const onDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      void onFiles(e.dataTransfer.files);
    },
    [onFiles, busy],
  );

  const send = useCallback(async () => {
    if (!docId || !input.trim() || busy) return;
    const userMsg: Msg = { role: "user", content: input.trim() };
    const prev = messages;
    const next = [...prev, userMsg];
    setMessages(next);
    setInput("");
    setError(null);
    setBusy(true);
    try {
      const { reply } = await sendChat(docId, next);
      setMessages([...next, { role: "assistant", content: reply }]);
    } catch (e) {
      setMessages(prev);
      setError(e instanceof Error ? e.message : "Chat failed");
    } finally {
      setBusy(false);
    }
  }, [docId, input, busy, messages]);

  const canChat = Boolean(docId) && !busy;

  return (
    <div style={layout}>
      <header style={header}>
        <h1 style={{ margin: 0, fontSize: "1.35rem" }}>Document Q&A</h1>
        <p style={{ margin: "0.35rem 0 0", color: "#475569", fontSize: "0.9rem" }}>
          Upload a document, then ask questions. Chat is not saved — refreshing clears everything.
        </p>
      </header>

      <main style={main}>
        <section style={card}>
          <h2 style={h2}>1. Document</h2>
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
            style={dropzone}
            aria-label="Drop zone for document"
          >
            <p style={{ margin: 0 }}>Drag and drop a file here, or</p>
            <button
              type="button"
              style={btn}
              disabled={busy}
              onClick={() => fileInputRef.current?.click()}
            >
              Choose file
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.pdf,.docx"
              style={{ display: "none" }}
              onChange={(e) => void onFiles(e.target.files)}
            />
            <p style={{ margin: "0.75rem 0 0", fontSize: "0.8rem", color: "#64748b" }}>
              Supported: .txt, .pdf, .docx (max ~20 MB)
            </p>
          </div>
          {docId && (
            <p style={{ margin: "1rem 0 0", fontSize: "0.9rem" }}>
              <strong>Ready:</strong> {docName} — {chunks} chunks indexed.
            </p>
          )}
        </section>

        <section style={{ ...card, flex: 1, display: "flex", flexDirection: "column", minHeight: 360 }}>
          <h2 style={h2}>2. Ask questions</h2>
          {!docId && (
            <p style={{ color: "#64748b", margin: 0 }}>Upload a document to enable the chat.</p>
          )}
          <div style={chatLog}>
            {messages.map((m, i) => (
              <div
                key={i}
                style={{
                  alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                  maxWidth: "88%",
                  padding: "0.55rem 0.75rem",
                  borderRadius: 10,
                  background: m.role === "user" ? "#1d4ed8" : "#e2e8f0",
                  color: m.role === "user" ? "#fff" : "#0f172a",
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                }}
              >
                {m.content}
              </div>
            ))}
          </div>
          <div style={composer}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void send();
                }
              }}
              placeholder={docId ? "Ask about this document…" : "Upload a document first"}
              disabled={!canChat}
              rows={2}
              style={textarea}
            />
            <button type="button" style={btnPrimary} disabled={!canChat || !input.trim()} onClick={() => void send()}>
              {busy ? "Thinking…" : "Send"}
            </button>
          </div>
        </section>
      </main>

      {error && (
        <div style={errBanner} role="alert">
          {error}
        </div>
      )}
    </div>
  );
}

const layout: CSSProperties = {
  minHeight: "100vh",
  display: "flex",
  flexDirection: "column",
  maxWidth: 900,
  margin: "0 auto",
  padding: "1.25rem",
};

const header: CSSProperties = { marginBottom: "1rem" };

const main: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "1rem",
  flex: 1,
};

const card: CSSProperties = {
  background: "#fff",
  borderRadius: 12,
  padding: "1.25rem",
  boxShadow: "0 1px 3px rgb(0 0 0 / 0.08)",
  border: "1px solid #e2e8f0",
};

const h2: CSSProperties = { margin: "0 0 0.75rem", fontSize: "1rem" };

const dropzone: CSSProperties = {
  border: "2px dashed #94a3b8",
  borderRadius: 10,
  padding: "1.5rem",
  textAlign: "center",
  background: "#f8fafc",
};

const btn: CSSProperties = {
  marginTop: "0.75rem",
  padding: "0.45rem 1rem",
  borderRadius: 8,
  border: "1px solid #cbd5e1",
  background: "#fff",
  cursor: "pointer",
  fontSize: "0.95rem",
};

const btnPrimary: CSSProperties = {
  ...btn,
  background: "#0f172a",
  color: "#fff",
  borderColor: "#0f172a",
  alignSelf: "flex-end",
};

const chatLog: CSSProperties = {
  flex: 1,
  overflowY: "auto",
  display: "flex",
  flexDirection: "column",
  gap: "0.5rem",
  padding: "0.5rem 0",
  minHeight: 120,
};

const composer: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "0.5rem",
  marginTop: "auto",
  paddingTop: "0.75rem",
  borderTop: "1px solid #e2e8f0",
};

const textarea: CSSProperties = {
  width: "100%",
  resize: "vertical",
  borderRadius: 8,
  border: "1px solid #cbd5e1",
  padding: "0.5rem 0.65rem",
  fontFamily: "inherit",
  fontSize: "0.95rem",
};

const errBanner: CSSProperties = {
  position: "fixed",
  bottom: 16,
  left: "50%",
  transform: "translateX(-50%)",
  maxWidth: "min(90vw, 520px)",
  background: "#fef2f2",
  color: "#991b1b",
  border: "1px solid #fecaca",
  padding: "0.65rem 1rem",
  borderRadius: 8,
  boxShadow: "0 4px 12px rgb(0 0 0 / 0.12)",
};
