import "@/App.css";
import { BrainCircuit, GitCompareArrows, LayoutDashboard } from "lucide-react";
import { Toaster } from "@/components/ui/sonner";
import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";

import ChatPage from "@/pages/ChatPage";
import ComparisonPage from "@/pages/ComparisonPage";
import DashboardPage from "@/pages/DashboardPage";

const navItems = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard, testId: "nav-dashboard-link" },
  {
    path: "/comparison",
    label: "Comparison",
    icon: GitCompareArrows,
    testId: "nav-comparison-link",
  },
  { path: "/chat", label: "AI Chat", icon: BrainCircuit, testId: "nav-chat-link" },
];

function App() {
  return (
    <BrowserRouter>
      <div
        data-testid="app-shell"
        className="min-h-screen bg-background text-foreground antialiased"
      >
        <div className="mx-auto flex w-full max-w-[1600px] flex-col px-6 py-6 md:px-12 md:py-12">
          <header
            data-testid="top-navigation"
            className="mb-8 flex flex-wrap items-center justify-between gap-6 rounded-lg border border-border/60 bg-card/80 p-4 backdrop-blur-xl"
          >
            <div className="space-y-2">
              <p
                data-testid="brand-tagline"
                className="font-mono text-xs uppercase tracking-[0.25em] text-muted-foreground"
              >
                ShadowIntel · Competitive Intelligence
              </p>
              <h1 data-testid="brand-title" className="text-3xl font-extrabold md:text-4xl">
                Confidence in Competitive Chaos
              </h1>
            </div>

            <nav
              data-testid="primary-navigation"
              className="flex flex-wrap items-center gap-2 rounded-md border border-border/60 bg-background/70 p-1"
            >
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    data-testid={item.testId}
                    className={({ isActive }) =>
                      [
                        "flex items-center gap-2 rounded-sm px-4 py-2 text-sm font-medium transition-colors",
                        isActive
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:bg-accent/10 hover:text-accent",
                      ].join(" ")
                    }
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </NavLink>
                );
              })}
            </nav>
          </header>

          <main data-testid="main-content-area" className="min-h-[70vh]">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/comparison" element={<ComparisonPage />} />
              <Route path="/chat" element={<ChatPage />} />
            </Routes>
          </main>
        </div>
      </div>
      <Toaster />
    </BrowserRouter>
  );
}

export default App;
