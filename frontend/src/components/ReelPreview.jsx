import { useState, useEffect, useRef } from "react";
import { buildShort } from "../services/api";

export default function ReelPreview({ quote, vibe, font, animation, caption, onApprove, onRegenerate }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const hasFetched = useRef(false);

  const generate = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await buildShort(quote, vibe, font, animation, caption);
      setData(result);
    } catch (e) {
      setError("Failed to generate short. Try again.");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;
    generate();
  }, []);

  const getVideoUrl = (path) => {
    const clean = path.replace(/\\/g, "/").replace(/^outputs\//, "");
    return `http://127.0.0.1:8000/outputs/${clean}`;
  };

  const isErrorCaption = (cap) => cap && cap.startsWith("Error:");

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Your Short</h2>
      {loading && <p style={styles.loading}>⌛ Building your short... this may take ~30 seconds</p>}
      {error && (
        <>
          <p style={styles.error}>{error}</p>
          <button style={styles.retryBtn} onClick={generate}>Retry</button>
        </>
      )}
      {data && !loading && (
        <>
          <video
            src={getVideoUrl(data.reel_path)}
            controls
            autoPlay
            loop
            style={styles.video}
          />

          <div style={styles.caption}>
            <p style={styles.captionLabel}>CAPTION</p>
            {isErrorCaption(data.caption) ? (
              <p style={styles.captionFallback}>
                Caption generation hit a rate limit. Check the .txt file in outputs/reels/ or retry.
              </p>
            ) : (
              <p style={styles.captionText}>{data.caption}</p>
            )}
          </div>

          <div style={styles.actions}>
            <button style={styles.regenBtn} onClick={onRegenerate}>← Regenerate</button>
            <button style={styles.approveBtn} onClick={() => onApprove(data)}>Approve & Post →</button>
          </div>
        </>
      )}
    </div>
  );
}

const styles = {
  container: { display: "flex", flexDirection: "column", alignItems: "center", padding: "40px 20px", maxWidth: "600px", margin: "0 auto" },
  title: { color: "#fff", fontSize: "32px", marginBottom: "32px" },
  loading: { color: "#666", fontSize: "16px", margin: "40px 0", textAlign: "center" },
  error: { color: "#ff4444", fontSize: "16px", marginBottom: "12px" },
  retryBtn: { background: "transparent", border: "1px solid #444", borderRadius: "8px", color: "#aaa", padding: "10px 24px", cursor: "pointer", fontSize: "14px" },
  video: { width: "100%", maxWidth: "420px", borderRadius: "12px", marginBottom: "24px" },
  caption: { background: "#111", border: "1px solid #333", borderRadius: "12px", padding: "20px", width: "100%", maxWidth: "420px", marginBottom: "24px", boxSizing: "border-box" },
  captionLabel: { color: "#444", fontSize: "11px", letterSpacing: "3px", marginBottom: "10px" },
  captionText: { color: "#aaa", fontSize: "14px", lineHeight: "1.6" },
  captionFallback: { color: "#555", fontSize: "13px", fontStyle: "italic" },
  actions: { display: "flex", gap: "16px" },
  regenBtn: { background: "transparent", border: "1px solid #444", borderRadius: "8px", color: "#aaa", padding: "12px 24px", cursor: "pointer", fontSize: "14px" },
  approveBtn: { background: "#fff", color: "#000", border: "none", borderRadius: "8px", padding: "12px 32px", fontSize: "15px", fontWeight: "700", cursor: "pointer" },
}; 