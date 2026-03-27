import { useState, useEffect } from "react";
import { renderPost } from "../services/api";

export default function PostPreview({ quote, vibe, font, onApprove, onRegenerate }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

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
    generate();
  }, []);

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Your Post</h2>

      {loading && <p style={styles.loading}>⌛ Generating your post...</p>}
      {error && <p style={styles.error}>{error}</p>}

      {data && !loading && (
        <>
          <img
            src={`http://127.0.0.1:8000/outputs/${data.path.replace(/\\/g, "/")}`}
            alt="Generated Post"
            style={styles.image}
          />
          <div style={styles.actions}>
            <button style={styles.regenBtn} onClick={onRegenerate}>
              ← Change font
            </button>
            <button style={styles.approveBtn} onClick={() => onApprove(data)}>
              Approve & Make Reel →
            </button>
          </div>
        </>
      )}
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "40px 20px",
    maxWidth: "600px",
    margin: "0 auto",
  },
  title: { color: "#fff", fontSize: "32px", marginBottom: "32px" },
  loading: { color: "#666", fontSize: "16px", margin: "40px 0" },
  error: { color: "#ff4444", fontSize: "16px" },
  image: {
    width: "100%",
    maxWidth: "480px",
    borderRadius: "12px",
    marginBottom: "32px",
  },
  actions: { display: "flex", gap: "16px" },
  regenBtn: {
    background: "transparent",
    border: "1px solid #444",
    borderRadius: "8px",
    color: "#aaa",
    padding: "12px 24px",
    cursor: "pointer",
    fontSize: "14px",
  },
  approveBtn: {
    background: "#fff",
    color: "#000",
    border: "none",
    borderRadius: "8px",
    padding: "12px 32px",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "pointer",
  },
};