import { useState, useEffect } from "react";

const ANIMATIONS = [
  {
    id: "line_fade",
    name: "Line Fade",
    description: "Each line fades in elegantly",
  },
  {
    id: "word_fade",
    name: "Word Fade",
    description: "Words appear one by one",
  },
  {
    id: "typewriter",
    name: "Typewriter",
    description: "Characters typed out live",
  },
  {
    id: "slide_up",
    name: "Slide Up",
    description: "Lines rise up into place",
  },
  {
    id: "zoom_in",
    name: "Zoom In",
    description: "Text scales in from center",
  },
];

export default function AnimationPicker({ quote, font, onConfirm }) {
  const [selected, setSelected] = useState("line_fade");
  const [previewKey, setPreviewKey] = useState(0);

  // Restart preview animation on selection change
  useEffect(() => {
    setPreviewKey((k) => k + 1);
  }, [selected]);

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Choose your animation</h2>
      <p style={styles.subtitle}>Pick how your text appears in the reel</p>

      {/* Live CSS Preview */}
      <div style={styles.preview}>
        <AnimationPreview
          key={previewKey}
          quote={quote}
          font={font}
          animation={selected}
        />
      </div>

      {/* Animation Options */}
      <div style={styles.grid}>
        {ANIMATIONS.map((anim) => (
          <button
            key={anim.id}
            style={{
              ...styles.animBtn,
              borderColor: selected === anim.id ? "#fff" : "#2a2a2a",
              background: selected === anim.id ? "#1a1a1a" : "#0f0f0f",
            }}
            onClick={() => setSelected(anim.id)}
          >
            <span style={styles.animName}>{anim.name}</span>
            <span style={styles.animDesc}>{anim.description}</span>
          </button>
        ))}
      </div>

      <button style={styles.confirmBtn} onClick={() => onConfirm(selected)}>
        Generate Reel with {ANIMATIONS.find((a) => a.id === selected)?.name} →
      </button>
    </div>
  );
}

// CSS-based preview component
function AnimationPreview({ quote, font, animation }) {
  const words = quote.split(" ");
  const lines = chunkArray(words, 4).map((w) => w.join(" "));

  const getLineStyle = (i) => {
    const base = {
      fontFamily: `'${font}', serif`,
      fontSize: "18px",
      color: "#fff",
      lineHeight: "1.8",
      display: "block",
    };

    const delay = `${i * 0.6}s`;

    switch (animation) {
      case "line_fade":
        return {
          ...base,
          animation: `fadein 0.8s ease forwards ${delay}`,
          opacity: 0,
        };
      case "word_fade":
        return {
          ...base,
          animation: `fadein 0.5s ease forwards ${delay}`,
          opacity: 0,
        };
      case "typewriter":
        return {
          ...base,
          overflow: "hidden",
          whiteSpace: "nowrap",
          width: 0,
          animation: `typewriter 1s steps(20) forwards ${delay}`,
        };
      case "slide_up":
        return {
          ...base,
          animation: `slideup 0.7s ease forwards ${delay}`,
          opacity: 0,
          transform: "translateY(20px)",
        };
      case "zoom_in":
        return {
          ...base,
          animation: `zoomin 0.6s ease forwards ${delay}`,
          opacity: 0,
          transform: "scale(0.8)",
        };
      default:
        return base;
    }
  };

  return (
    <>
      <style>{`
        @keyframes fadein {
          to { opacity: 1; }
        }
        @keyframes slideup {
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes zoomin {
          to { opacity: 1; transform: scale(1); }
        }
        @keyframes typewriter {
          to { width: 100%; }
        }
      `}</style>
      <div style={{ textAlign: "center" }}>
        {lines.map((line, i) => (
          <span key={i} style={getLineStyle(i)}>
            {line}
          </span>
        ))}
      </div>
    </>
  );
}

function chunkArray(arr, size) {
  const chunks = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
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
  subtitle: {
    color: "#555",
    fontSize: "13px",
    marginBottom: "32px",
    letterSpacing: "1px",
  },
  preview: {
    background: "#0f0f0f",
    border: "1px solid #222",
    borderRadius: "16px",
    padding: "40px",
    width: "100%",
    minHeight: "150px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "32px",
    boxSizing: "border-box",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
    gap: "10px",
    width: "100%",
    marginBottom: "32px",
  },
  animBtn: {
    border: "1px solid #2a2a2a",
    borderRadius: "10px",
    padding: "16px 14px",
    cursor: "pointer",
    display: "flex",
    flexDirection: "column",
    gap: "6px",
    transition: "border-color 0.15s, background 0.15s",
    textAlign: "left",
  },
  animName: {
    fontSize: "15px",
    fontWeight: "600",
    color: "#fff",
  },
  animDesc: {
    fontSize: "12px",
    color: "#555",
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
  },
};