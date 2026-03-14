import { motion } from "framer-motion";
import {
  CheckCircle2,
  CircleDashed,
  AlertTriangle,
  Bot,
  Briefcase,
  Building2,
  ChevronRight,
  ClipboardList,
  Newspaper,
  RefreshCw,
  Signal,
  Users,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { generateBriefing } from "@/lib/api";
import { getStoredCompetitors, setStoredCompetitors, setStoredReport } from "@/lib/storage";

const heroImage =
  "https://images.unsplash.com/photo-1702726001096-096efcf640b8?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1MDZ8MHwxfHNlYXJjaHw0fHx0ZWNoJTIwb2ZmaWNlJTIwYWJzdHJhY3QlMjBkYXJrJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3NzM0NzU4NDN8MA&ixlib=rb-4.1.0&q=85";

const cardAnimation = {
  initial: { opacity: 0, y: 18 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4 },
};

const processingSteps = [
  "Validating competitor inputs",
  "Collecting social, hiring, and people signals",
  "Aggregating company metrics and sentiment",
  "Generating AI strategic battlecard",
];

const StageCard = ({ children, testId }) => (
  <motion.div {...cardAnimation} data-testid={testId} className="rounded-lg border border-border/60 bg-card/80 p-6">
    {children}
  </motion.div>
);

const DashboardPage = () => {
  const initialCompetitors = getStoredCompetitors();
  const [competitorA, setCompetitorA] = useState(initialCompetitors.competitorA);
  const [competitorB, setCompetitorB] = useState(initialCompetitors.competitorB);
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [stage, setStage] = useState("form");
  const [activeStep, setActiveStep] = useState(0);
  const [showCharts, setShowCharts] = useState(false);
  const [sentimentChartSize, setSentimentChartSize] = useState({ width: 0, height: 0 });
  const stepTimerRef = useRef(null);
  const sentimentChartRef = useRef(null);

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

  useEffect(() => {
    if (stage === "results") {
      const timer = setTimeout(() => setShowCharts(true), 180);
      return () => clearTimeout(timer);
    }
    setShowCharts(false);
    return undefined;
  }, [stage]);

  useEffect(() => {
    if (!showCharts || !sentimentChartRef.current) return undefined;
    const observer = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setSentimentChartSize({ width: Math.floor(width), height: Math.floor(height) });
    });
    observer.observe(sentimentChartRef.current);
    return () => observer.disconnect();
  }, [showCharts]);

  const clearStepTimer = () => {
    if (stepTimerRef.current) {
      clearInterval(stepTimerRef.current);
      stepTimerRef.current = null;
    }
  };

  const runBattlecard = async () => {
    setIsLoading(true);
    setStage("processing");
    setActiveStep(0);

    clearStepTimer();
    stepTimerRef.current = setInterval(() => {
      setActiveStep((previous) => (previous < processingSteps.length - 1 ? previous + 1 : previous));
    }, 850);

    const minimumProcessingTime = new Promise((resolve) => {
      setTimeout(resolve, 3200);
    });

    try {
      const [data] = await Promise.all([
        generateBriefing({ competitorA, competitorB }),
        minimumProcessingTime,
      ]);
      setReport(data);
      setStoredReport(data);
      setStoredCompetitors(competitorA, competitorB);
      setStage("results");
      toast.success("Battlecard is ready");
    } catch (error) {
      setStage("form");
      toast.error(error.message);
    } finally {
      clearStepTimer();
      setIsLoading(false);
    }
  };

  const handleGenerate = async (event) => {
    event.preventDefault();
    await runBattlecard();
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
        <div className="absolute inset-0 bg-gradient-to-r from-background via-background/85 to-transparent" />
        <div className="absolute inset-0 flex flex-col justify-center gap-4 px-6 md:px-10">
          <p data-testid="dashboard-hero-label" className="font-mono text-xs uppercase tracking-[0.24em] text-accent">
            Battlecard Intelligence Flow
          </p>
          <h2 data-testid="dashboard-hero-title" className="text-4xl font-extrabold md:text-6xl">
            Enter Competitors. Watch Signals. Get Strategy.
          </h2>
          <p data-testid="dashboard-hero-subtitle" className="max-w-3xl text-sm text-muted-foreground md:text-lg">
            A guided experience: input competitors, process intelligence signals, and view a polished
            strategic battlecard.
          </p>
        </div>
      </motion.div>

      {stage === "form" && (
        <StageCard testId="battlecard-form-stage">
          <div className="mb-6 flex items-center gap-3">
            <ClipboardList className="h-6 w-6 text-primary" />
            <h3 data-testid="battlecard-form-title" className="text-2xl font-bold">
              Build Competitor Battlecard
            </h3>
          </div>

          <form
            onSubmit={handleGenerate}
            data-testid="competitor-input-form"
            className="grid grid-cols-1 gap-4 md:grid-cols-[1fr_1fr_auto]"
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
              Start Battlecard <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
          </form>
        </StageCard>
      )}

      {stage === "processing" && (
        <StageCard testId="processing-stage">
          <div className="mb-6 flex items-center gap-3">
            <CircleDashed className="h-6 w-6 animate-spin text-primary" />
            <h3 data-testid="processing-title" className="text-2xl font-bold">
              Processing Battlecard
            </h3>
          </div>

          <p data-testid="processing-description" className="mb-6 text-sm text-muted-foreground md:text-lg">
            We’re collecting live competitive intelligence for {competitorA} vs {competitorB}.
          </p>

          <div data-testid="processing-steps" className="space-y-3">
            {processingSteps.map((step, index) => {
              const isDone = index < activeStep;
              const isCurrent = index === activeStep;
              return (
                <div
                  key={step}
                  data-testid={`processing-step-${index}`}
                  className={[
                    "flex items-center gap-3 rounded-md border p-3",
                    isDone
                      ? "border-emerald-500/40 bg-emerald-500/10"
                      : isCurrent
                        ? "border-primary/40 bg-primary/10"
                        : "border-border/60 bg-background/50",
                  ].join(" ")}
                >
                  {isDone ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  ) : (
                    <CircleDashed className={isCurrent ? "h-5 w-5 animate-spin text-primary" : "h-5 w-5 text-muted-foreground"} />
                  )}
                  <span className="text-sm md:text-base">{step}</span>
                </div>
              );
            })}
          </div>
        </StageCard>
      )}

      {stage === "results" && report && (
        <div data-testid="dashboard-bento-grid" className="grid grid-cols-1 gap-6 md:grid-cols-12">
          <motion.div
            {...cardAnimation}
            transition={{ duration: 0.4, delay: 0.05 }}
            className="md:col-span-12"
          >
            <Card data-testid="battlecard-results-header" className="border-border/60 bg-card/80">
              <CardContent className="flex flex-wrap items-center justify-between gap-4 pt-6">
                <div>
                  <p className="font-mono text-xs uppercase tracking-[0.2em] text-accent">Battlecard Result</p>
                  <h3 data-testid="results-title" className="text-3xl font-extrabold md:text-4xl">
                    {competitorAData.company_name} vs {competitorBData.company_name}
                  </h3>
                </div>
                <div className="flex gap-3">
                  <Button
                    data-testid="new-battlecard-button"
                    variant="outline"
                    onClick={() => setStage("form")}
                    className="border-border/70 bg-background/50"
                  >
                    New Battlecard
                  </Button>
                  <Button
                    data-testid="refresh-battlecard-button"
                    onClick={runBattlecard}
                    disabled={isLoading}
                    className="bg-primary text-primary-foreground"
                  >
                    <RefreshCw className="mr-2 h-4 w-4" /> Refresh
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>

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
                  {report.ai_insights.risk_alerts.length > 0 ? (
                    <ul className="space-y-2">
                      {report.ai_insights.risk_alerts.map((risk, index) => (
                        <li key={risk} data-testid={`risk-alert-${index}`} className="rounded-sm bg-secondary/40 p-2">
                          {risk}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p data-testid="risk-alert-empty" className="rounded-sm bg-secondary/30 p-2 text-xs">
                      No live risk alerts returned.
                    </p>
                  )}
                </div>

                <div>
                  <p className="mb-2 text-xs uppercase tracking-[0.2em] text-accent">Opportunity Signals</p>
                  {report.ai_insights.opportunity_signals.length > 0 ? (
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
                  ) : (
                    <p data-testid="opportunity-signal-empty" className="rounded-sm bg-secondary/30 p-2 text-xs">
                      No live opportunity signals returned.
                    </p>
                  )}
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
                    {company.social_activity.length > 0 ? (
                      company.social_activity.slice(0, 2).map((post, postIndex) => (
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
                      ))
                    ) : (
                      <p data-testid={`social-empty-${index}`} className="text-xs text-muted-foreground">
                        No live social posts returned.
                      </p>
                    )}
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
                    {company.hiring_signals.length > 0 ? (
                      company.hiring_signals.slice(0, 3).map((job, jobIndex) => (
                        <p
                          key={`${job.job_title}-${jobIndex}`}
                          data-testid={`hiring-job-${index}-${jobIndex}`}
                          className="mb-1 rounded-sm bg-secondary/40 p-2"
                        >
                          {job.job_title} · {job.location}
                        </p>
                      ))
                    ) : (
                      <p data-testid={`hiring-empty-${index}`} className="text-xs text-muted-foreground">
                        No live hiring signals returned.
                      </p>
                    )}
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
                <div ref={sentimentChartRef} data-testid="sentiment-chart" className="h-72 min-w-0 w-full">
                  {sentimentChart.length === 0 ? (
                    <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                      No live sentiment trend returned.
                    </div>
                  ) : showCharts && sentimentChartSize.width > 20 && sentimentChartSize.height > 20 ? (
                    <div className="h-full w-full">
                      <LineChart
                        width={Math.max(sentimentChartSize.width - 12, 280)}
                        height={Math.max(sentimentChartSize.height - 12, 220)}
                        data={sentimentChart}
                      >
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
                    </div>
                  ) : (
                    <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                      Preparing chart...
                    </div>
                  )}
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
                    {company.news_coverage.length > 0 ? (
                      company.news_coverage.slice(0, 2).map((newsItem, newsIndex) => (
                        <p
                          key={`${newsItem.title}-${newsIndex}`}
                          data-testid={`news-item-${index}-${newsIndex}`}
                          className="mb-2 rounded-sm bg-secondary/40 p-2"
                        >
                          {newsItem.title}
                        </p>
                      ))
                    ) : (
                      <p data-testid={`news-empty-${index}`} className="text-xs text-muted-foreground">
                        No live news items returned.
                      </p>
                    )}
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