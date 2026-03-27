export default function CaptionReview({ reelData }) {
  return (
    <div style={styles.container}>
      <div style={styles.checkmark}>✓</div>
      <h2 style={styles.title}>Pipeline Complete</h2>
      <p style={styles.subtitle}>Your reel is ready to post</p>

      <div style={styles.card}>
        <p style={styles.label}>CAPTION</p>
        <p style={styles.captionText}>{reelData.caption}</p>
      </div>

      <div style={styles.card}>
        <p style={styles.label}>FILES</p>
        <p style={styles.path}>📹 {reelData.reel_path}</p>
        <p style={styles.path}>📝 {reelData.caption_path}</p>
      </div>

      <p style={styles.note}>
        Instagram posting agent coming soon. For now, upload the reel manually using the caption above.
      </p>
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
    textAlign: "center",
  },
  checkmark: {
    fontSize: "64px",
    color: "#4caf50",
    marginBottom: "16px",
  },
  title: { color: "#fff", fontSize: "32px", marginBottom: "8px" },
  subtitle: { color: "#666", fontSize: "15px", marginBottom: "40px" },
  card: {
    background: "#111",
    border: "1px solid #333",
    borderRadius: "12px",
    padding: "24px",
    width: "100%",
    marginBottom: "16px",
    textAlign: "left",
    boxSizing: "border-box",
  },
  label: {
    color: "#555",
    fontSize: "11px",
    letterSpacing: "3px",
    marginBottom: "12px",
  },
  captionText: { color: "#aaa", fontSize: "14px", lineHeight: "1.6" },
  path: { color: "#666", fontSize: "12px", marginBottom: "4px", wordBreak: "break-all" },
  note: {
    color: "#444",
    fontSize: "13px",
    marginTop: "24px",
    lineHeight: "1.6",
  },
};