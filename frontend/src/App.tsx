import { useEffect, useRef, useState } from "react";
import { generateMockRun } from "./mock_run";

type Message = {
  role: "user" | "assistant";
  text: string;
};

type PipelineTab = "route" | "validator" | "result";
type Status = "idle" | "running" | "completed" | "failed";

type RunState = {
  status: Status;
  route: {
    status: Status;
    selected_path: string;
    reasoning: string;
  };
  validator: {
    status: Status;
    is_valid: boolean;
    comment: string;
  };
  result: {
    final_answer: string;
  };
};

const initialRun: RunState = {
  status: "idle",
  route: {
    status: "idle",
    selected_path: "—",
    reasoning: "Ожидание запроса.",
  },
  validator: {
    status: "idle",
    is_valid: false,
    comment: "Ожидание проверки.",
  },
  result: {
    final_answer: "Введите запрос, чтобы запустить pipeline.",
  },
};

export default function App() {
  const [input, setInput] = useState("");
  const [activeTab, setActiveTab] = useState<PipelineTab>("route");
  const [run, setRun] = useState<RunState>(initialRun);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      text: "Здравствуйте! Введите запрос, и я покажу ответ и прохождение по pipeline.",
    },
  ]);

  const chatBoxRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const getTabStatus = (tab: PipelineTab) => {
    if (tab === "route") return run.route.status;
    if (tab === "validator") return run.validator.status;
    return run.status;
  };

  const handleSend = () => {
    if (!input.trim()) return;

    const query = input.trim();

    setMessages((prev) => [...prev, { role: "user", text: query }]);
    setInput("");
    setActiveTab("route");

    setRun({
      status: "running",
      route: {
        status: "running",
        selected_path: "Определяется...",
        reasoning: "Route Agent анализирует запрос.",
      },
      validator: {
        status: "idle",
        is_valid: false,
        comment: "Ожидание этапа валидации.",
      },
      result: {
        final_answer: "Формирование ответа...",
      },
    });

    const simulated = generateMockRun(query);

    setTimeout(() => {
      setRun((prev) => ({
        ...prev,
        route: {
          status: "completed",
          selected_path: simulated.route.selected_path,
          reasoning: simulated.route.reasoning,
        },
        validator: {
          ...prev.validator,
          status: "running",
          comment: "Validator Agent проверяет результат.",
        },
      }));
      setActiveTab("validator");
    }, 900);

    setTimeout(() => {
      setRun({
        status: simulated.status as Status,
        route: {
          status: simulated.route.status as Status,
          selected_path: simulated.route.selected_path,
          reasoning: simulated.route.reasoning,
        },
        validator: {
          status: simulated.validator.status as Status,
          is_valid: simulated.validator.is_valid,
          comment: simulated.validator.comment,
        },
        result: {
          final_answer: simulated.result.final_answer,
        },
      });
      setActiveTab("result");

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: simulated.result.final_answer },
      ]);
    }, 1800);
  };

  const renderPipelineContent = () => {
    if (activeTab === "route") {
      return (
        <div className="pipeline-details fade-in">
          <h3>Route Agent</h3>
          <p><strong>Status:</strong> {run.route.status}</p>
          <p><strong>Selected path:</strong> {run.route.selected_path}</p>
          <p><strong>Reasoning:</strong> {run.route.reasoning}</p>
        </div>
      );
    }

    if (activeTab === "validator") {
      return (
        <div className="pipeline-details fade-in">
          <h3>Validator Agent</h3>
          <p><strong>Status:</strong> {run.validator.status}</p>
          <p><strong>Valid:</strong> {String(run.validator.is_valid)}</p>
          <p><strong>Comment:</strong> {run.validator.comment}</p>
        </div>
      );
    }

    return (
      <div className="pipeline-details fade-in">
        <h3>Result</h3>
        <p><strong>Status:</strong> {run.status}</p>
        <p><strong>Final answer:</strong> {run.result.final_answer}</p>
      </div>
    );
  };

  return (
    <div className="page">
      <div className="app-shell">
        <div className="hero">
          <h1>Multi-Agent Pipeline</h1>
          <p>AI assistant with transparent routing and validation</p>
        </div>

        <div className="content">
          <aside className="sidebar">
            <h2>Pipeline</h2>

            <div className="pipeline-buttons">
              {[
                { key: "route", label: "Route Agent" },
                { key: "validator", label: "Validator Agent" },
                { key: "result", label: "Result" },
              ].map((tab) => {
                const currentTab = tab.key as PipelineTab;
                const isActive = activeTab === currentTab;
                const status = getTabStatus(currentTab);

                return (
                  <button
                    key={tab.key}
                    className={`pipeline-button ${isActive ? "active" : ""}`}
                    onClick={() => setActiveTab(currentTab)}
                  >
                    <div className="pipeline-button-title">{tab.label}</div>
                    <div
                      className={`status-pill ${
                        status === "completed"
                          ? "status-completed"
                          : status === "failed"
                          ? "status-failed"
                          : status === "running"
                          ? "status-running"
                          : "status-idle"
                      }`}
                    >
                      {status}
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="pipeline-card">
              {renderPipelineContent()}
            </div>
          </aside>

          <section className="chat-section">
            <h2>Chat</h2>

            <div className="chat-box" ref={chatBoxRef}>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`message ${message.role === "user" ? "user" : "assistant"} fade-in`}
                >
                  <strong>{message.role === "user" ? "User" : "Assistant"}:</strong>{" "}
                  {message.text}
                </div>
              ))}
            </div>

            <div className="input-row">
              <textarea
                className="chat-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Введите запрос..."
                rows={3}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
              />
              <button className="send-button" onClick={handleSend}>
                Send
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}