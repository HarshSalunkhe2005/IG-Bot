import { useState, useEffect, useRef } from "react";
import { draftQuotes } from "../services/api";

export default function QuoteSelector({ vibe, onSelect }) {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [custom, setCustom] = useState("");
  const hasFetched = useRef(false);

  const fetchQuotes = async () => {
    setLoading(true);
    try {
      const results = await draftQuotes(vibe);
      setQuotes(results.filter(q => q.quote)); // filter out any failed ones
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;
    fetchQuotes();
  }, []);

  const handleSelect = (quote, font, caption) => {
    onSelect({ quote, font, caption: caption || "Reflections" });
  };

  const handleCustomSubmit = () => {
    if (custom.trim()) {
      onSelect({ quote: custom.trim(), font: "Playfair Display", caption: "Reflections" });
    }
  };

  return (
    <div style={styles.container}>
      <p style={styles.vibe}>Vibe: {vibe}</p>
      <h2 style={styles.title}>Pick your quote</h2>

      {loading ? (
        <p style={styles.loading}>✨ Generating quotes... this may take a moment</p>
      ) : (
        <div style={styles.list}>
          {quotes.length === 0 && (
            <p style={styles.empty}>No quotes generated. Try refreshing.</p>
          )}
          {quotes.map((q, i) => (
            <button
              key={i}
              style={styles.quoteCard}
              onClick={() => handleSelect(q.quote, q.font, q.caption)}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = "#fff")}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = "#333")}
            >
              <p style={styles.quoteText}>{q.quote}</p>
              <span style={styles.fontTag}>Font: {q.font}</span>
            </button>
          ))}
        </div>
      )}

      <button style={styles.refreshBtn} onClick={fetchQuotes} disabled={loading}>
        ↻ Refresh quotes
      </button>

      <div style={styles.divider}>
        <span style={styles.dividerText}>or write your own</span>
      </div>

      <textarea
        style={styles.textarea}
        placeholder="Type your quote here..."
        value={custom}
        onChange={(e) => setCustom(e.target.value)}
        rows={3}
      />
      <button
        style={styles.customBtn}
        onClick={handleCustomSubmit}
        disabled={!custom.trim()}
      >
        Use my quote →
      </button>
    </div>
  );
}

const styles = {
  container: { display: "flex", flexDirection: "column", alignItems: "center", padding: "40px 20px", maxWidth: "800px", margin: "0 auto" },
  vibe: { color: "#666", fontSize: "13px", textTransform: "uppercase", letterSpacing: "3px", marginBottom: "8px" },
  title: { color: "#fff", fontSize: "32px", marginBottom: "32px" },
  loading: { color: "#666", fontSize: "16px", margin: "40px 0", textAlign: "center" },
  empty: { color: "#555", fontSize: "15px", textAlign: "center", padding: "20px" },
  list: { display: "flex", flexDirection: "column", gap: "12px", width: "100%" },
  quoteCard: { background: "#111", border: "1px solid #333", borderRadius: "12px", padding: "24px", cursor: "pointer", textAlign: "left", transition: "border-color 0.2s" },
  quoteText: { color: "#fff", fontSize: "18px", lineHeight: "1.6", marginBottom: "8px" },
  fontTag: { color: "#555", fontSize: "12px" },
  refreshBtn: { marginTop: "24px", background: "transparent", border: "1px solid #444", borderRadius: "8px", color: "#aaa", padding: "10px 24px", cursor: "pointer", fontSize: "14px" },
  divider: { width: "100%", textAlign: "center", margin: "32px 0 16px", borderTop: "1px solid #333", paddingTop: "16px" },
  dividerText: { color: "#555", fontSize: "13px", textTransform: "uppercase", letterSpacing: "2px" },
  textarea: { width: "100%", background: "#111", border: "1px solid #333", borderRadius: "12px", color: "#fff", padding: "16px", fontSize: "16px", resize: "vertical", outline: "none", boxSizing: "border-box" },
  customBtn: { marginTop: "12px", background: "#fff", color: "#000", border: "none", borderRadius: "8px", padding: "12px 32px", fontSize: "15px", cursor: "pointer", fontWeight: "600" },
};