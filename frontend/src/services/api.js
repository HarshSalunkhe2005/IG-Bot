import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000/api";

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

export const draftQuotes = async (vibe) => {
  const results = [];
  for (let i = 0; i < 3; i++) {
    try {
      const res = await axios.post(`${BASE_URL}/draft`, { vibe }, { timeout: 60000 });
      results.push(res.data);
    } catch (e) {
      console.error(`Draft ${i + 1} failed:`, e);
    }
    if (i < 2) await sleep(2000); // 2s gap between calls
  }
  return results;
};

export const renderPost = async (text, vibe, font) => {
  const res = await axios.post(
    `${BASE_URL}/render`,
    { text, vibe, bg_type: "ai_generated", font },
    { timeout: 120000 }
  );
  return res.data;
};

export const buildReel = async (image_path, quote, vibe, font, animation) => {
  const res = await axios.post(
    `${BASE_URL}/reel`,
    { image_path, quote, vibe, font, animation },
    { timeout: 300000 } // 5 min — reel + caption retry can take time
  );
  return res.data;
};