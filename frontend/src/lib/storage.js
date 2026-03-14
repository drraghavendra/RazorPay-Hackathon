const COMPETITOR_KEY = "shadowintel_competitors";
const REPORT_KEY = "shadowintel_latest_report";

export const getStoredCompetitors = () => {
  try {
    const raw = localStorage.getItem(COMPETITOR_KEY);
    if (!raw) {
      return { competitorA: "Stripe", competitorB: "Adyen" };
    }
    const parsed = JSON.parse(raw);
    return {
      competitorA: parsed.competitorA || "Stripe",
      competitorB: parsed.competitorB || "Adyen",
    };
  } catch {
    return { competitorA: "Stripe", competitorB: "Adyen" };
  }
};

export const setStoredCompetitors = (competitorA, competitorB) => {
  localStorage.setItem(COMPETITOR_KEY, JSON.stringify({ competitorA, competitorB }));
};

export const getStoredReport = () => {
  try {
    const raw = localStorage.getItem(REPORT_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const setStoredReport = (report) => {
  localStorage.setItem(REPORT_KEY, JSON.stringify(report));
};