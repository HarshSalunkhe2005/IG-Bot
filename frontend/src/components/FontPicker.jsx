import { useState, useEffect } from "react";

const FONTS = [
  "Playfair Display",
  "Cormorant Garamond",
  "Lora",
  "Dancing Script",
  "Great Vibes",
  "Bodoni Moda",
  "DM Sans",
  "Josefin Sans",
  "Raleway",
  "Bebas Neue",
  "Pacifico",
  "Righteous",
  "Nunito",
  "Space Grotesk",
  "Quicksand",
];

function loadGoogleFont(fontName) {
  const id = `gfont-${fontName.replace(/\s+/g, "-")}`;
  if (document.getElementById(id)) return;
  const link = document.createElement("link");
  link.id = id;
  link.rel = "stylesheet";
  link.href = `https://fonts.googleapis.com/css2?family=${fontName.replace(/\s+/g, "+")}:wght@400;700&display=swap`;
  document.head.appendChild(link);
}

export default function FontPicker({ quote, defaultFont, onConfirm }) {
  const [selected, setSelected] = useState(defaultFont || FONTS[0]);

  // Load all fonts on mount
  useEffect(() => {
    FONTS.forEach(loadGoogleFont);
  }, []);

  // Load default font if it's not in our list
  useEffect(() => {
    if (defaultFont) loadGoogleFont(defaultFont);
    setSelected(defaultFont || FONTS[0]);
  }, [defaultFont]);

  const handleSelect = (font) => {
    setSelected(font);
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Choose your font</h2>
      <p style={styles.subtitle}>Click any font — preview updates instantly</p>

      {/* Live Preview */}
      <div style={styles.preview}>
        <p style={{ ...styles.previewText, fontFamily: `'${selected}', serif` }}>
          {quote}
        </p>
      </div>

      {/* Font Grid */}
      <div style={styles.fontGrid}>
        {FONTS.map((font) => (
          <button
            key={font}
            style={{
              ...styles.fontBtn,
              borderColor: selected === font ? "#fff" : "#2a2a2a",
              background: selected === font ? "#1a1a1a" : "#0f0f0f",
            }}
            onClick={() => handleSelect(font)}
          >
            <span style={{ fontFamily: `'${font}', serif`, fontSize: "15px", color: "#fff" }}>
              {font}
            </span>
            <span style={{ fontFamily: `'${font}', serif`, fontSize: "12px", color: "#555", marginTop: "4px" }}>
              Aa Bb Cc
            </span>
          </button>
        ))}
      </div>

      {/* AI Suggested font badge */}
      {defaultFont && FONTS.includes(defaultFont) && (
        <p style={styles.aiBadge}>✦ AI suggested: {defaultFont}</p>
      )}

      <button style={styles.confirmBtn} onClick={() => onConfirm(selected)}>
        Generate Post with "{selected}" →
      </button>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "40px 20px",
    maxWidth: "900px",
    margin: "0 auto",
  },
  title: { color: "#fff", fontSize: "32px", marginBottom: "8px" },
  subtitle: { color: "#555", fontSize: "13px", marginBottom: "32px", letterSpacing: "1px" },
  preview: {
    background: "#0f0f0f",
    border: "1px solid #222",
    borderRadius: "16px",
    padding: "40px",
    width: "100%",
    minHeight: "130px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "32px",
    boxSizing: "border-box",
    transition: "all 0.3s",
  },
  previewText: {
    color: "#fff",
    fontSize: "22px",
    lineHeight: "1.8",
    textAlign: "center",
    transition: "font-family 0.2s",
  },
  fontGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
    gap: "10px",
    width: "100%",
    marginBottom: "24px",
  },
  fontBtn: {
    border: "1px solid #2a2a2a",
    borderRadius: "10px",
    padding: "12px 14px",
    cursor: "pointer",
    display: "flex",
    flexDirection: "column",
    transition: "border-color 0.15s, background 0.15s",
    textAlign: "left",
  },
  aiBadge: {
    color: "#555",
    fontSize: "12px",
    marginBottom: "20px",
    letterSpacing: "1px",
  },
  confirmBtn: {
    background: "#fff",
    color: "#000",
    border: "none",
    borderRadius: "10px",
    padding: "14px 40px",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "pointer",
    marginTop: "8px",
  },
};