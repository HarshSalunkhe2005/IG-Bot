import { useState } from "react";
import { postToYoutube, retryFailedPost } from "../services/api";

export default function CaptionReview({ reelData }) {
  const [posting, setPosting] = useState(false);
  const [posted, setPosted] = useState(false);
  const [postUrl, setPostUrl] = useState(null);
  const [error, setError] = useState(null);
  const [suggestion, setSuggestion] = useState(null);

  const handlePostToYoutube = async () => {
    setPosting(true);
    setError(null);
    setSuggestion(null);
    try {
      const result = await postToYoutube(reelData.reel_path, reelData.caption);
      setPostUrl(result.post_url);
      setPosted(true);
    } catch (e) {
      const errorDetail = e.response?.data?.detail;
      setError(errorDetail?.error || "Failed to post to YouTube");
      setSuggestion(errorDetail?.suggestion || "Please try again later");
    } finally {
      setPosting(false);
    }
  };

  const handleRetry = async () => {
    setPosting(true);
    setError(null);
    setSuggestion(null);
    try {
      const result = await retryFailedPost(reelData.reel_path, reelData.caption);
      setPostUrl(result.post_url);
      setPosted(true);
    } catch (e) {
      const errorDetail = e.response?.data?.detail;
      setError(errorDetail?.error || "Retry failed");
      setSuggestion(errorDetail?.suggestion || "Please try again");
    } finally {
      setPosting(false);
    }
  };

  const handleNavigateBack = () => {
    window.location.reload();
  };

  if (posted) {
    return (
      <div style={styles.container}>
        <div style={styles.checkmark}>✓</div>
        <h2 style={styles.title}>Posted to YouTube!</h2>
        <p style={styles.subtitle}>Your Short is now live</p>

        <div style={styles.card}>
          <p style={styles.label}>POST URL</p>
          <a href={postUrl} target="_blank" rel="noopener noreferrer" style={styles.link}>
            {postUrl}
          </a>
        </div>

        <button style={styles.backBtn} onClick={handleNavigateBack}>
          ← Create New Post
        </button>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.errorIcon}>⚠️</div>
        <h2 style={styles.title}>Posting Failed</h2>

        <div style={styles.card}>
          <p style={styles.label}>ERROR</p>
          <p style={styles.errorText}>{error}</p>
        </div>

        <div style={styles.card}>
          <p style={styles.label}>SUGGESTION</p>
          <p style={styles.suggestionText}>{suggestion}</p>
        </div>

        <div style={styles.actions}>
          <button
            style={styles.retryBtn}
            onClick={handleRetry}
            disabled={posting}
          >
            {posting ? "⏳ Retrying..." : "🔄 Retry"}
          </button>
          <button style={styles.backBtn} onClick={handleNavigateBack}>
            ← Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.checkmark}>✓</div>
      <h2 style={styles.title}>Your Short is ready to post</h2>
      <p style={styles.subtitle}>Review caption and video before posting</p>

      <div style={styles.card}>
        <p style={styles.label}>CAPTION</p>
        <p style={styles.captionText}>{reelData.caption}</p>
      </div>

      <div style={styles.card}>
        <p style={styles.label}>FILES</p>
        <p style={styles.path}>📹 {reelData.reel_path}</p>
        <p style={styles.path}>📝 {reelData.caption_path}</p>
      </div>

      <div style={styles.actions}>
        <button
          style={styles.postBtn}
          onClick={handlePostToYoutube}
          disabled={posting}
        >
          {posting ? "⏳ Posting..." : "📤 Post to YouTube Now"}
        </button>
        <button style={styles.backBtn} onClick={handleNavigateBack}>
          ← Back
        </button>
      </div>
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
  errorIcon: {
    fontSize: "64px",
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
  errorText: { color: "#ff6b6b", fontSize: "14px", lineHeight: "1.6" },
  suggestionText: { color: "#ffa500", fontSize: "14px", lineHeight: "1.6" },
  path: { color: "#666", fontSize: "12px", marginBottom: "4px", wordBreak: "break-all" },
  link: {
    color: "#61dafb",
    textDecoration: "none",
    wordBreak: "break-all",
    fontSize: "13px",
  },
  actions: {
    display: "flex",
    gap: "12px",
    flexWrap: "wrap",
    justifyContent: "center",
  },
  postBtn: {
    background: "#fff",
    color: "#000",
    border: "none",
    borderRadius: "8px",
    padding: "12px 24px",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "pointer",
    transition: "background 0.3s",
  },
  retryBtn: {
    background: "#ffa500",
    color: "#000",
    border: "none",
    borderRadius: "8px",
    padding: "12px 24px",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "pointer",
  },
  backBtn: {
    background: "transparent",
    border: "1px solid #444",
    borderRadius: "8px",
    color: "#aaa",
    padding: "12px 24px",
    cursor: "pointer",
    fontSize: "14px",
  },
};