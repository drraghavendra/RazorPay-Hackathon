import { motion } from "framer-motion";
import { Bot, SendHorizontal, User } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { askIntelligenceChat } from "@/lib/api";
import { getStoredCompetitors } from "@/lib/storage";

const ChatPage = () => {
  const competitors = getStoredCompetitors();
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Ask me anything about competitor hiring, social signals, executive movements, and likely roadmap direction.",
    },
  ]);

  const history = useMemo(
    () => messages.map((message) => ({ role: message.role, content: message.content })),
    [messages],
  );

  const handleAsk = async (event) => {
    event.preventDefault();
    if (!question.trim()) return;

    const userMessage = { role: "user", content: question.trim() };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setQuestion("");
    setIsLoading(true);

    try {
      const response = await askIntelligenceChat({
        competitorA: competitors.competitorA,
        competitorB: competitors.competitorB,
        question: userMessage.content,
        history,
      });
      setMessages([...nextMessages, { role: "assistant", content: response.answer }]);
    } catch (error) {
      toast.error(error.message);
      setMessages([
        ...nextMessages,
        {
          role: "assistant",
          content: "I hit an issue while generating that answer. Try again in a moment.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section data-testid="chat-page" className="space-y-8">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <h2 data-testid="chat-page-title" className="text-4xl font-extrabold md:text-5xl">
          AI Intelligence Chat
        </h2>
        <p data-testid="chat-page-description" className="mt-2 text-sm text-muted-foreground md:text-lg">
          Ask strategic questions about {competitors.competitorA} and {competitors.competitorB}.
        </p>
      </motion.div>

      <Card data-testid="chat-window-card" className="border-border/60 bg-card/80">
        <CardHeader>
          <CardTitle className="font-mono text-sm uppercase tracking-[0.22em] text-accent">
            Intelligence Terminal
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div
            data-testid="chat-message-list"
            className="max-h-[420px] space-y-3 overflow-y-auto rounded-md border border-border/60 bg-background/50 p-4"
          >
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                data-testid={`chat-message-${index}`}
                className={[
                  "rounded-sm border p-3 text-sm",
                  message.role === "assistant"
                    ? "border-primary/30 bg-primary/10 text-foreground"
                    : "border-accent/30 bg-accent/10 text-foreground",
                ].join(" ")}
              >
                <div className="mb-2 flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-muted-foreground">
                  {message.role === "assistant" ? (
                    <>
                      <Bot className="h-4 w-4" /> ShadowIntel AI
                    </>
                  ) : (
                    <>
                      <User className="h-4 w-4" /> You
                    </>
                  )}
                </div>
                <p>{message.content}</p>
              </div>
            ))}
          </div>

          <form onSubmit={handleAsk} data-testid="chat-question-form" className="space-y-3">
            <Textarea
              data-testid="chat-question-input"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              className="min-h-24 border-border/70 bg-background/50 font-mono"
              placeholder="Example: What signals indicate competitor expansion into fraud detection?"
              required
            />
            <Button
              data-testid="chat-send-button"
              type="submit"
              disabled={isLoading}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              <SendHorizontal className="mr-2 h-4 w-4" />
              {isLoading ? "Analyzing..." : "Ask ShadowIntel"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </section>
  );
};

export default ChatPage;