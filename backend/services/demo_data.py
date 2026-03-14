from datetime import datetime, timezone
import random
from typing import Dict, List


def _rng(seed_value: str) -> random.Random:
    return random.Random(abs(hash(seed_value)) % (10**7))


def _sentiment_series(base: float, jitter: random.Random) -> List[Dict[str, float | str]]:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    current = base
    points = []
    for month in months:
        current = max(2.8, min(4.8, current + jitter.uniform(-0.25, 0.2)))
        points.append({"month": month, "rating": round(current, 1)})
    return points


def generate_company_demo(company: str, rival: str) -> Dict:
    jitter = _rng(company)
    headcount = jitter.randint(1800, 13000)
    headcount_growth = jitter.randint(-4, 34)
    job_openings = jitter.randint(45, 290)
    traffic_index = round(jitter.uniform(70, 140), 1)
    glassdoor = round(jitter.uniform(3.3, 4.6), 1)

    sentiment = _sentiment_series(glassdoor, jitter)
    now_iso = datetime.now(timezone.utc).isoformat()

    return {
        "company_name": company,
        "social_activity": [
            {
                "post_content": f"{company} published an update about AI-led payment workflows.",
                "reactor_count": jitter.randint(70, 450),
                "top_reactors": [
                    {
                        "name": "Taylor Kim",
                        "title": "VP Product",
                        "company": "PayPal",
                    },
                    {
                        "name": "Jordan Singh",
                        "title": "Director of GTM",
                        "company": "Shopify",
                    },
                    {
                        "name": "Morgan Lee",
                        "title": "Head of Risk",
                        "company": rival,
                    },
                ],
            },
            {
                "post_content": f"Engineering leaders at {company} discussed production AI observability.",
                "reactor_count": jitter.randint(40, 250),
                "top_reactors": [
                    {
                        "name": "Casey Tran",
                        "title": "Principal Engineer",
                        "company": "Square",
                    }
                ],
            },
        ],
        "keyword_trends": [
            {"keyword": f"{company} AI payments", "mentions": jitter.randint(35, 160)},
            {
                "keyword": f"{company} fraud detection",
                "mentions": jitter.randint(22, 130),
            },
            {"keyword": "OpenAI fintech", "mentions": jitter.randint(15, 95)},
        ],
        "people_intelligence": [
            {
                "name": "Avery Patel",
                "current_company": "Global Bank Co",
                "previous_company": company,
                "title": "Director, Product Strategy",
            },
            {
                "name": "Sam O'Neill",
                "current_company": "CloudPay",
                "previous_company": company,
                "title": "Senior PM, Platform",
            },
        ],
        "company_metrics": {
            "headcount": headcount,
            "headcount_growth_pct": headcount_growth,
            "job_openings": job_openings,
            "web_traffic_index": traffic_index,
            "glassdoor_rating": glassdoor,
        },
        "hiring_signals": [
            {
                "job_title": "Senior AI Fraud Engineer",
                "department": "Risk & ML",
                "location": "Remote",
                "posting_date": "2026-03-10",
            },
            {
                "job_title": "Staff Product Manager, AI Payments",
                "department": "Product",
                "location": "New York",
                "posting_date": "2026-03-08",
            },
            {
                "job_title": "Applied Research Scientist",
                "department": "Data Science",
                "location": "London",
                "posting_date": "2026-03-07",
            },
        ],
        "sentiment_trend": sentiment,
        "news_coverage": [
            {
                "title": f"{company} expands enterprise AI payment toolkit",
                "source": "Fintech Chronicle",
                "published_at": "2026-03-11",
                "url": "https://example.com/news-1",
            },
            {
                "title": f"What {company} hiring means for payment ops",
                "source": "Product Weekly",
                "published_at": "2026-03-09",
                "url": "https://example.com/news-2",
            },
        ],
        "product_changes": [
            {
                "page": "Pricing",
                "change_summary": "Added enterprise AI risk scoring tier.",
                "detected_at": now_iso,
            },
            {
                "page": "Release Notes",
                "change_summary": "Launched explainable fraud model dashboard.",
                "detected_at": now_iso,
            },
        ],
        "executive_movements": [
            {
                "name": "Riley Gomez",
                "movement": f"Joined {company} as VP Product, Risk Intelligence",
                "date": "2026-03-03",
            }
        ],
        "source": "demo-fallback",
    }