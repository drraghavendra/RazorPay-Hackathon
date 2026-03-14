import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

const client = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
});

const parseError = (error) => {
  if (error.response?.data?.detail) return error.response.data.detail;
  return error.message || "Request failed";
};

export const generateBriefing = async ({ competitorA, competitorB }) => {
  try {
    const { data } = await client.post("/intelligence/briefing", {
      competitor_a: competitorA,
      competitor_b: competitorB,
    });
    return data;
  } catch (error) {
    throw new Error(parseError(error));
  }
};

export const getLatestBriefing = async ({ competitorA, competitorB }) => {
  try {
    const { data } = await client.get("/intelligence/latest", {
      params: { competitor_a: competitorA, competitor_b: competitorB },
    });
    return data;
  } catch (error) {
    throw new Error(parseError(error));
  }
};

export const getComparison = async ({ competitorA, competitorB }) => {
  try {
    const { data } = await client.get("/intelligence/comparison", {
      params: { competitor_a: competitorA, competitor_b: competitorB },
    });
    return data;
  } catch (error) {
    throw new Error(parseError(error));
  }
};

export const askIntelligenceChat = async ({ competitorA, competitorB, question, history }) => {
  try {
    const { data } = await client.post("/intelligence/chat", {
      competitor_a: competitorA,
      competitor_b: competitorB,
      question,
      history,
    });
    return data;
  } catch (error) {
    throw new Error(parseError(error));
  }
};