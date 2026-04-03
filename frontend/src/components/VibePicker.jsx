const VIBES = ["melancholic", "modern", "personal", "bold", "minimalist"];

const VIBE_DESCRIPTIONS = {
  melancholic: "Deep, emotional, poetic",
  modern: "Clean, sharp, confident",
  personal: "Warm, handwritten, intimate",
  bold: "Strong, dramatic, powerful",
  minimalist: "Simple, airy, refined",
};

export default function VibePicker({ onSelect }) {
  return (
    <div style={styles.container}>
      <h1 style={styles.title}>YT-Bot</h1>
      <p style={styles.subtitle}>Choose your vibe</p>
      <div style={styles.grid}>
        {VIBES.map((vibe) => (
          <button
            key={vibe}
            style={styles.card}
            onClick={() => onSelect(vibe)}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = "#fff")}
            onMouseLeave={(e) =>
              (e.currentTarget.style.borderColor = "#333")
            }
          >
            <span style={styles.vibeName}>{vibe}</span>
            <span style={styles.vibeDesc}>{VIBE_DESCRIPTIONS[vibe]}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100vh",
    padding: "40px 20px",
  },
  title: {
    fontSize: "48px",
    fontWeight: "700",
    color: "#fff",
    marginBottom: "8px",
    letterSpacing: "2px",
  },
  subtitle: {
    fontSize: "16px",
    color: "#888",
    marginBottom: "48px",
    letterSpacing: "4px",
    textTransform: "uppercase",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "16px",
    width: "100%",
    maxWidth: "900px",
  },
  card: {
    background: "#111",
    border: "1px solid #333",
    borderRadius: "12px",
    padding: "32px 24px",
    cursor: "pointer",
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    transition: "border-color 0.2s",
    textAlign: "left",
  },
  vibeName: {
    fontSize: "20px",
    fontWeight: "600",
    color: "#fff",
    textTransform: "capitalize",
  },
  vibeDesc: {
    fontSize: "13px",
    color: "#666",
  },
};