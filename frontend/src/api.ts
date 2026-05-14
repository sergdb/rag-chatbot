const apiBase = (import.meta.env.VITE_API_URL as string | undefined) ?? "/api";

async function parseError(res: Response): Promise<string> {
  try {
    const j = (await res.json()) as { detail?: string | { msg?: string }[] };
    if (typeof j.detail === "string") return j.detail;
    if (Array.isArray(j.detail)) return j.detail.map((d) => d.msg ?? "").filter(Boolean).join("; ") || res.statusText;
  } catch {
    /* ignore */
  }
  return res.statusText || "Request failed";
}

export async function uploadDocument(
  file: File,
): Promise<{ id: string; filename: string; chunk_count: number }> {
  const body = new FormData();
  body.append("file", file);
  const res = await fetch(`${apiBase}/documents`, { method: "POST", body });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json() as Promise<{ id: string; filename: string; chunk_count: number }>;
}

export type ChatRole = "user" | "assistant";

export async function sendChat(
  documentId: string,
  messages: { role: ChatRole; content: string }[],
): Promise<{ reply: string }> {
  const res = await fetch(`${apiBase}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, messages }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json() as Promise<{ reply: string }>;
}
