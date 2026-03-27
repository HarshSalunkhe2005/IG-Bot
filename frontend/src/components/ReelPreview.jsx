import { useState, useEffect } from "react";
import { buildReel } from "../services/api";

export default function ReelPreview({ postData, quote, vibe, font, onApprove, onRegenerate }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const generate = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await buildReel(postData.clean_bg_path, quote, vibe, font);
      setData(result);
    } catch (e) {
      setError("Failed to generate reel. Try again.");
    }
    setLoading(false);
  };

  useEffect(() => {
    generate();
  }, []);

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Your Reel</h2>

      {loading && <p style={styles.loading}>⌛ Building your reel... this takes ~30 seconds</p>}
      {error && <p style={styles.error}>{error}</p>}

      {data && !loading && (
        <>
          <video
            src={`http://127.0.0.1:8000/outputs/${data.reel_path.replace(/\\/g, "/")}`}
            controls
            autoPlay
            loop
            style={styles.video}
          />
          <div style={styles.caption}>
            <p style={styles.captionText}>{data.caption}</p>
          </div>
          <div style={styles.actions}>
            <button style={styles.regenBtn} onClick={onRegenerate}>
              ← Regenerate
            </button>
            <button style={styles.approveBtn} onClick={() => onApprove(data)}>
              Approve & Post →
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
  loading: { color: "#666", fontSize: "16px", margin: "40px 0", textAlign: "center" },
  error: { color: "#ff4444", fontSize: "16px" },
  video: {
    width: "100%",
    maxWidth: "480px",
    borderRadius: "12px",
    marginBottom: "24px",
  },
  caption: {
    background: "#111",
    border: "1px solid #333",
    borderRadius: "12px",
    padding: "20px",
    width: "100%",
    maxWidth: "480px",
    marginBottom: "24px",
    boxSizing: "border-box",
  },
  captionText: {
    color: "#aaa",
    fontSize: "14px",
    lineHeight: "1.6",
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