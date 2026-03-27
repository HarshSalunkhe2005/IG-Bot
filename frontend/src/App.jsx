import { useState } from "react";
import VibePicker from "./components/VibePicker";
import QuoteSelector from "./components/QuoteSelector";
import FontPicker from "./components/FontPicker";
import PostPreview from "./components/PostPreview";
import ReelPreview from "./components/ReelPreview";
import CaptionReview from "./components/CaptionReview";

const STEPS = ["vibe", "quote", "font", "post", "reel", "done"];

export default function App() {
  const [step, setStep] = useState("vibe");
  const [vibe, setVibe] = useState(null);
  const [quoteData, setQuoteData] = useState(null);
  const [font, setFont] = useState(null);
  const [postData, setPostData] = useState(null);
  const [reelData, setReelData] = useState(null);

  return (
    <div style={styles.app}>
      {/* Step indicator */}
      <div style={styles.steps}>
        {STEPS.map((s, i) => (
          <div
            key={s}
            style={{
              ...styles.dot,
              background: STEPS.indexOf(step) >= i ? "#fff" : "#333",
            }}
          />
        ))}
      </div>

      {step === "vibe" && (
        <VibePicker
          onSelect={(v) => {
            setVibe(v);
            setStep("quote");
          }}
        />
      )}

      {step === "quote" && (
        <QuoteSelector
          vibe={vibe}
          onSelect={(data) => {
            setQuoteData(data);
            setStep("font");
          }}
        />
      )}

      {step === "font" && (
        <FontPicker
          quote={quoteData.quote}
          defaultFont={quoteData.font}
          onConfirm={(selectedFont) => {
            setFont(selectedFont);
            setStep("post");
          }}
        />
      )}

      {step === "post" && (
        <PostPreview
          quote={quoteData.quote}
          vibe={vibe}
          font={font}
          onApprove={(data) => {
            setPostData(data);
            setStep("reel");
          }}
          onRegenerate={() => setStep("font")}
        />
      )}

      {step === "reel" && (
        <ReelPreview
          postData={postData}
          quote={quoteData.quote}
          vibe={vibe}
          font={font}
          onApprove={(data) => {
            setReelData(data);
            setStep("done");
          }}
          onRegenerate={() => setStep("post")}
        />
      )}

      {step === "done" && <CaptionReview reelData={reelData} />}
    </div>
  );
}

const styles = {
  app: {
    minHeight: "100vh",
    background: "#0a0a0a",
    color: "#fff",
    fontFamily: "'Inter', sans-serif",
  },
  steps: {
    display: "flex",
    justifyContent: "center",
    gap: "8px",
    padding: "24px",
  },
  dot: {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    transition: "background 0.3s",
  },
};