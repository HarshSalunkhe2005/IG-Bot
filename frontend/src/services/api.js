import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000/api";

export const draftQuotes = async (vibe) => {
  // Generate 3 quote options
  const requests = [1, 2, 3].map(() =>
    axios.post(`${BASE_URL}/draft`, { vibe })
  );
  const results = await Promise.all(requests);
  return results.map((r) => r.data);
};

export const renderPost = async (text, vibe, font) => {
  const res = await axios.post(`${BASE_URL}/render`, {
    text,
    vibe,
    bg_type: "ai_generated",
    font,
  });
  return res.data;
};

export const buildReel = async (image_path, quote, vibe, font) => {
  const res = await axios.post(`${BASE_URL}/reel`, {
    image_path,
    quote,
    vibe,
    font,
  });
  return res.data;
};