import { motion } from "framer-motion";
import { Bar, BarChart, CartesianGrid, Tooltip, XAxis, YAxis } from "recharts";
import { useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getComparison } from "@/lib/api";
import { getStoredCompetitors } from "@/lib/storage";

const ComparisonPage = () => {
  const stored = useMemo(() => getStoredCompetitors(), []);
  const [comparison, setComparison] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showChart, setShowChart] = useState(false);
  const [barChartSize, setBarChartSize] = useState({ width: 0, height: 0 });
  const barChartRef = useRef(null);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      try {
        const data = await getComparison({
          competitorA: stored.competitorA,
          competitorB: stored.competitorB,
        });
        setComparison(data);
      } catch (error) {
        toast.error(error.message);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, [stored.competitorA, stored.competitorB]);

  useEffect(() => {
    if (comparison) {
      const timer = setTimeout(() => setShowChart(true), 180);
      return () => clearTimeout(timer);
    }
    setShowChart(false);
    return undefined;
  }, [comparison]);

  useEffect(() => {
    if (!showChart || !barChartRef?.current) return undefined;
    const observer = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setBarChartSize({ width: Math.floor(width), height: Math.floor(height) });
    });
    observer.observe(barChartRef.current);
    return () => observer.disconnect();
  }, [showChart, barChartRef]);

  const chartData = comparison
    ? [
        {
          metric: "Headcount",
          [comparison.competitor_a]: comparison.metrics.headcount.a,
          [comparison.competitor_b]: comparison.metrics.headcount.b,
        },
        {
          metric: "Hiring",
          [comparison.competitor_a]: comparison.metrics.hiring_openings.a,
          [comparison.competitor_b]: comparison.metrics.hiring_openings.b,
        },
        {
          metric: "Engagement",
          [comparison.competitor_a]: comparison.metrics.social_engagement.a,
          [comparison.competitor_b]: comparison.metrics.social_engagement.b,
        },
      ]
    : [];

  return (
    <section data-testid="comparison-page" className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <h2 data-testid="comparison-page-title" className="text-4xl font-extrabold md:text-5xl">
          Competitor Comparison
        </h2>
        <p data-testid="comparison-page-description" className="mt-2 text-sm text-muted-foreground md:text-lg">
          Side-by-side comparison of strategic signals between your two tracked competitors.
        </p>
      </motion.div>

      {isLoading && (
        <Card data-testid="comparison-loading-card" className="border-border/60 bg-card/80">
          <CardContent className="py-10 font-mono text-sm text-muted-foreground">
            Loading comparison metrics...
          </CardContent>
        </Card>
      )}

      {comparison && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-12">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
            className="md:col-span-6"
          >
            <Card data-testid="comparison-company-a-card" className="h-full border-border/60 bg-card/80">
              <CardHeader>
                <CardTitle data-testid="comparison-company-a-title">{comparison.competitor_a}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 font-mono text-sm">
                <p data-testid="comparison-company-a-headcount">Headcount: {comparison.metrics.headcount.a}</p>
                <p data-testid="comparison-company-a-hiring">Hiring Openings: {comparison.metrics.hiring_openings.a}</p>
                <p data-testid="comparison-company-a-sentiment">Sentiment: {comparison.metrics.sentiment.a}</p>
                <p data-testid="comparison-company-a-social">
                  Social Engagement: {comparison.metrics.social_engagement.a}
                </p>
                <p data-testid="comparison-company-a-growth">
                  Headcount Growth: {comparison.metrics.headcount_growth.a}%
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.06 }}
            className="md:col-span-6"
          >
            <Card data-testid="comparison-company-b-card" className="h-full border-border/60 bg-card/80">
              <CardHeader>
                <CardTitle data-testid="comparison-company-b-title">{comparison.competitor_b}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 font-mono text-sm">
                <p data-testid="comparison-company-b-headcount">Headcount: {comparison.metrics.headcount.b}</p>
                <p data-testid="comparison-company-b-hiring">Hiring Openings: {comparison.metrics.hiring_openings.b}</p>
                <p data-testid="comparison-company-b-sentiment">Sentiment: {comparison.metrics.sentiment.b}</p>
                <p data-testid="comparison-company-b-social">
                  Social Engagement: {comparison.metrics.social_engagement.b}
                </p>
                <p data-testid="comparison-company-b-growth">
                  Headcount Growth: {comparison.metrics.headcount_growth.b}%
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.12 }}
            className="md:col-span-12"
          >
            <Card data-testid="comparison-chart-card" className="border-border/60 bg-card/80">
              <CardHeader>
                <CardTitle>Signal Magnitude Comparison</CardTitle>
              </CardHeader>
              <CardContent>
                <div ref={barChartRef} data-testid="comparison-bar-chart" className="h-80 min-w-0 w-full">
                  {showChart && barChartSize.width > 20 && barChartSize.height > 20 ? (
                    <div className="h-full w-full">
                      <BarChart
                        width={Math.max(barChartSize.width - 12, 300)}
                        height={Math.max(barChartSize.height - 12, 240)}
                        data={chartData}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
                        <XAxis dataKey="metric" stroke="rgba(148,163,184,0.7)" />
                        <YAxis stroke="rgba(148,163,184,0.7)" />
                        <Tooltip
                          contentStyle={{
                            background: "#12141C",
                            border: "1px solid #2D3042",
                            borderRadius: "8px",
                          }}
                        />
                        <Bar dataKey={comparison.competitor_a} fill="#6366F1" radius={[4, 4, 0, 0]} />
                        <Bar dataKey={comparison.competitor_b} fill="#22D3EE" radius={[4, 4, 0, 0]} />
                      </BarChart>
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
        </div>
      )}
    </section>
  );
};

export default ComparisonPage;