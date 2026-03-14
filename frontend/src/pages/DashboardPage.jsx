import { motion } from "framer-motion";
import {
  AlertTriangle,
  Bot,
  Briefcase,
  Building2,
  Newspaper,
  RefreshCw,
  Signal,
  Users,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { generateBriefing, getLatestBriefing } from "@/lib/api";
import {
  getStoredCompetitors,
  getStoredReport,
  setStoredCompetitors,
  setStoredReport,
} from "@/lib/storage";

const heroImage =
  "https://images.unsplash.com/photo-1702726001096-096efcf640b8?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1MDZ8MHwxfHNlYXJjaHw0fHx0ZWNoJTIwb2ZmaWNlJTIwYWJzdHJhY3QlMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzM0NzU4NDN8MA&ixlib=rb-4.1.0&q=85";

const cardAnimation = {
  initial: { opacity: 0, y: 18 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4 },
};

const DashboardPage = () => {
  const initialCompetitors = getStoredCompetitors();
  const [competitorA, setCompetitorA] = useState(initialCompetitors.competitorA);
  const [competitorB, setCompetitorB] = useState(initialCompetitors.competitorB);
  const [report, setReport] = useState(getStoredReport());
  const [isLoading, setIsLoading] = useState(false);

  const competitorAData = report?.competitor_a;
  const competitorBData = report?.competitor_b;

  const sentimentChart = useMemo(() => {
    if (!competitorAData?.sentiment_trend || !competitorBData?.sentiment_trend) return [];
    return competitorAData.sentiment_trend.map((point, index) => ({
      month: point.month,
      competitorA: point.rating,
      competitorB: competitorBData.sentiment_trend[index]?.rating ?? null,
    }));
  }, [competitorAData, competitorBData]);

  const loadLatest = async () => {
    setIsLoading(true);
    try {
      const data = await getLatestBriefing({ competitorA, competitorB });
      setReport(data);
      setStoredReport(data);
      setStoredCompetitors(competitorA, competitorB);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!report) {
      loadLatest();
    }
  }, []);

  const handleGenerate = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    try {
      const data = await generateBriefing({ competitorA, competitorB });
      setReport(data);
      setStoredReport(data);
      setStoredCompetitors(competitorA, competitorB);
      toast.success("Daily competitive briefing refreshed");
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section data-testid="dashboard-page" className="space-y-8">
      <motion.div
        {...cardAnimation}
        data-testid="dashboard-hero"
        className="relative overflow-hidden rounded-lg border border-primary/30 bg-card shadow-[0_0_16px_rgba(99,102,241,0.15)]"
      >
        <img
          src={heroImage}
          alt="Competitive intelligence dashboard"
          className="h-56 w-full object-cover opacity-30"
          data-testid="dashboard-hero-image"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-background via-background/80 to-transparent" />

        <div className="absolute inset-0 flex flex-col justify-center gap-4 px-6 md:px-10">
          <p
            data-testid="dashboard-hero-label"
            className="font-mono text-xs uppercase tracking-[0.24em] text-accent"
          >
            Morning Competitive Brief
          </p>
          <h2 data-testid="dashboard-hero-title" className="text-4xl font-extrabold md:text-6xl">
            {competitorA} vs {competitorB}
          </h2>
          <p data-testid="dashboard-hero-subtitle" className="max-w-3xl text-sm text-muted-foreground md:text-lg">
            ShadowIntel monitors hiring, social traction, company health, sentiment, and market news to
            predict threats and product opportunities.
          </p>
        </div>
      </motion.div>

      <motion.form
        {...cardAnimation}
        transition={{ duration: 0.4, delay: 0.08 }}
        onSubmit={handleGenerate}
        data-testid="competitor-input-form"
        className="grid grid-cols-1 gap-4 rounded-lg border border-border/60 bg-card/80 p-5 md:grid-cols-[1fr_1fr_auto_auto]"
      >
        <Input
          data-testid="competitor-a-input"
          value={competitorA}
          onChange={(event) => setCompetitorA(event.target.value)}
          placeholder="Competitor A"
          className="bg-background/50 font-mono"
          required
        />
        <Input
          data-testid="competitor-b-input"
          value={competitorB}
          onChange={(event) => setCompetitorB(event.target.value)}
          placeholder="Competitor B"
          className="bg-background/50 font-mono"
          required
        />
        <Button
          data-testid="generate-briefing-button"
          type="submit"
          disabled={isLoading}
          className="bg-primary text-primary-foreground hover:bg-primary/90"
        >
          {isLoading ? "Generating..." : "Generate Briefing"}
        </Button>
        <Button
          data-testid="load-latest-button"
          type="button"
          variant="outline"
          onClick={loadLatest}
          disabled={isLoading}
          className="border-border/80 bg-background/50"
        >
          <RefreshCw className="mr-2 h-4 w-4" />
          Latest
        </Button>
      </motion.form>

      {report && (
        <div data-testid="dashboard-bento-grid" className="grid grid-cols-1 gap-6 md:grid-cols-12">
          <motion.div
            {...cardAnimation}
            transition={{ duration: 0.4, delay: 0.12 }}
            className="md:col-span-8"
          >
            <Card data-testid="company-metrics-card" className="h-full border-border/60 bg-card/80">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-2xl">
                  <Building2 className="h-5 w-5 text-primary" /> Company Health Metrics
                </CardTitle>
                <CardDescription>
                  Headcount, hiring velocity, web traffic and employee sentiment benchmarks.
                </CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {[competitorAData, competitorBData].map((company, index) => (
                  <div
                    key={company.company_name}
                    data-testid={`company-metrics-${index}`}
                    className="rounded-md border border-border/60 bg-background/40 p-4"
                  >
                    <h3 data-testid={`company-metrics-name-${index}`} className="text-xl font-semibold">
                      {company.company_name}
                    </h3>
                    <div className="mt-3 space-y-2 font-mono text-sm">
                      <p data-testid={`company-headcount-${index}`}>
                        Headcount: <span className="text-accent">{company.company_metrics.headcount}</span>
                      </p>
                      <p data-testid={`company-jobs-${index}`}>
                        Open Roles: <span className="text-accent">{company.company_metrics.job_openings}</span>
                      </p>
                      <p data-testid={`company-growth-${index}`}>
                        Growth: <span className="text-accent">{company.company_metrics.headcount_growth_pct}%</span>
                      </p>
                      <p data-testid={`company-glassdoor-${index}`}>
                        Glassdoor: <span className="text-accent">{company.company_metrics.glassdoor_rating}</span>
                      </p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            {...cardAnimation}
            transition={{ duration: 0.4, delay: 0.15 }}
            className="md:col-span-4"
          >
            <Card data-testid="ai-insights-card" className="h-full border-border/60 bg-card/80">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Bot className="h-5 w-5 text-primary" /> AI Strategic Insights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-sm text-muted-foreground">
                <p data-testid="ai-daily-brief" className="text-foreground">
                  {report.ai_insights.daily_brief}
                </p>

                <div>
                  <p className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-accent">
                    <AlertTriangle className="h-4 w-4" /> Risk Alerts
                  </p>
                  <ul className="space-y-2">
                    {report.ai_insights.risk_alerts.map((risk, index) => (
                      <li key={risk} data-testid={`risk-alert-${index}`} className="rounded-sm bg-secondary/40 p-2">
                        {risk}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <p className="mb-2 text-xs uppercase tracking-[0.2em] text-accent">Opportunity Signals</p>
                  <ul className="space-y-2">
                    {report.ai_insights.opportunity_signals.map((signalItem, index) => (
                      <li
                        key={signalItem}
                        data-testid={`opportunity-signal-${index}`}
                        className="rounded-sm bg-secondary/40 p-2"
                      >
                        {signalItem}
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            {...cardAnimation}
            transition={{ duration: 0.4, delay: 0.18 }}
            className="md:col-span-6"
          >
            <Card data-testid="social-activity-card" className="h-full border-border/60 bg-card/80">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Signal className="h-5 w-5 text-primary" /> Social Activity Feed
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                {[competitorAData, competitorBData].map((company, index) => (
                  <div
                    key={company.company_name}
                    data-testid={`social-company-section-${index}`}
                    className="rounded-md border border-border/60 bg-background/30 p-3"
                  >
                    <p className="mb-2 font-semibold text-foreground">{company.company_name}</p>
                    {company.social_activity.slice(0, 2).map((post, postIndex) => (
                      <div key={`${company.company_name}-${postIndex}`} className="mb-2">
                        <p data-testid={`social-post-${index}-${postIndex}`} className="text-muted-foreground">
                          {post.post_content}
                        </p>
                        <p
                          data-testid={`social-reactors-${index}-${postIndex}`}
                          className="font-mono text-xs text-accent"
                        >
                          Reactors: {post.reactor_count}
                        </p>
                      </div>
                    ))}
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            {...cardAnimation}
            transition={{ duration: 0.4, delay: 0.21 }}
            className="md:col-span-6"
          >
            <Card data-testid="hiring-signals-card" className="h-full border-border/60 bg-card/80">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Briefcase className="h-5 w-5 text-primary" /> Hiring Signals
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                {[competitorAData, competitorBData].map((company, index) => (
                  <div
                    key={company.company_name}
                    data-testid={`hiring-company-section-${index}`}
                    className="rounded-md border border-border/60 bg-background/30 p-3"
                  >
                    <p className="mb-2 font-semibold text-foreground">{company.company_name}</p>
                    {company.hiring_signals.slice(0, 3).map((job, jobIndex) => (
                      <p
                        key={`${job.job_title}-${jobIndex}`}
                        data-testid={`hiring-job-${index}-${jobIndex}`}
                        className="mb-1 rounded-sm bg-secondary/40 p-2"
                      >
                        {job.job_title} · {job.location}
                      </p>
                    ))}
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            {...cardAnimation}
            transition={{ duration: 0.4, delay: 0.24 }}
            className="md:col-span-7"
          >
            <Card data-testid="sentiment-trend-card" className="h-full border-border/60 bg-card/80">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Users className="h-5 w-5 text-primary" /> Employee Sentiment Trend
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div data-testid="sentiment-chart" className="h-72 min-w-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={sentimentChart}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                      <XAxis dataKey="month" stroke="rgba(148,163,184,0.7)" />
                      <YAxis domain={[2.8, 5]} stroke="rgba(148,163,184,0.7)" />
                      <Tooltip
                        contentStyle={{
                          background: "#12141C",
                          border: "1px solid #2D3042",
                          borderRadius: "8px",
                        }}
                      />
                      <Line type="monotone" dataKey="competitorA" stroke="#6366F1" strokeWidth={2.5} />
                      <Line type="monotone" dataKey="competitorB" stroke="#22D3EE" strokeWidth={2.5} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            {...cardAnimation}
            transition={{ duration: 0.4, delay: 0.27 }}
            className="md:col-span-5"
          >
            <Card data-testid="news-digest-card" className="h-full border-border/60 bg-card/80">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Newspaper className="h-5 w-5 text-primary" /> News Digest
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-sm">
                {[competitorAData, competitorBData].map((company, index) => (
                  <div key={company.company_name} data-testid={`news-company-section-${index}`}>
                    <p className="mb-2 font-semibold text-foreground">{company.company_name}</p>
                    {company.news_coverage.slice(0, 2).map((newsItem, newsIndex) => (
                      <p
                        key={`${newsItem.title}-${newsIndex}`}
                        data-testid={`news-item-${index}-${newsIndex}`}
                        className="mb-2 rounded-sm bg-secondary/40 p-2"
                      >
                        {newsItem.title}
                      </p>
                    ))}
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      )}
    </section>
  );
};

export default DashboardPage;