import { useState, useEffect, useRef } from "react";
import { renderPost } from "../services/api";

export default function PostPreview({ quote, vibe, font, onApprove, onRegenerate }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const hasFetched = useRef(false); // Fix: prevent StrictMode double call

  const generate = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await renderPost(quote, vibe, font);
      setData(result);
    } catch (e) {
      setError("Failed to generate post. Try again.");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;
    generate();
  }, []);

  // Fix: strip "outputs/" prefix since it's already in the mount path
  const getImageUrl = (path) => {
    const clean = path.replace(/\\/g, "/").replace(/^outputs\//, "");
    return `http://127.0.0.1:8000/outputs/${clean}`;
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Your Post</h2>
      {loading && <p style={styles.loading}>⌛ Generating your post...</p>}
      {error && (
        <>
          <p style={styles.error}>{error}</p>
          <button style={styles.retryBtn} onClick={generate}>Retry</button>
        </>
      )}
      {data && !loading && (
        <>
          <img
            src={getImageUrl(data.path)}
            alt="Generated Post"
            style={styles.image}
            onError={(e) => { e.target.style.display = "none"; }}
          />
          <div style={styles.actions}>
            <button style={styles.regenBtn} onClick={onRegenerate}>← Change animation</button>
            <button style={styles.approveBtn} onClick={() => onApprove(data)}>Approve & Make Reel →</button>
          </div>
        </>
      )}
    </div>
  );
}

const styles = {
  container: { display: "flex", flexDirection: "column", alignItems: "center", padding: "40px 20px", maxWidth: "600px", margin: "0 auto" },
  title: { color: "#fff", fontSize: "32px", marginBottom: "32px" },
  loading: { color: "#666", fontSize: "16px", margin: "40px 0" },
  error: { color: "#ff4444", fontSize: "16px", marginBottom: "12px" },
  retryBtn: { background: "transparent", border: "1px solid #444", borderRadius: "8px", color: "#aaa", padding: "10px 24px", cursor: "pointer", fontSize: "14px" },
  image: { width: "100%", maxWidth: "480px", borderRadius: "12px", marginBottom: "32px" },
  actions: { display: "flex", gap: "16px" },
  regenBtn: { background: "transparent", border: "1px solid #444", borderRadius: "8px", color: "#aaa", padding: "12px 24px", cursor: "pointer", fontSize: "14px" },
  approveBtn: { background: "#fff", color: "#000", border: "none", borderRadius: "8px", padding: "12px 32px", fontSize: "15px", fontWeight: "700", cursor: "pointer" },
};