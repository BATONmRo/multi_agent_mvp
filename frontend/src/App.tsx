import { useEffect, useRef, useState } from "react";

type Message = {
  role: "user" | "assistant";
  text: string;
};

type PipelineTab =
  | "task_parser"
  | "route"
  | "methods"
  | "reagents"
  | "safety"
  | "result";

type Status = "idle" | "running" | "completed" | "failed";

type RunState = {
  status: Status;
  task_parser: {
    status: Status;
    task_type: string;
    target: string;
    starting_materials: string[];
    confidence: number;
  };
  route: {
    status: Status;
    target: string;
    route_count: number;
    confidence: number;
    routes: {
      id: string;
      summary: string;
    }[];
  };
  methods: {
    status: Status;
    results: string[];
    message: string;
  };
  reagents: {
    status: Status;
    results: string[];
    message: string;
  };
  safety: {
    status: Status;
    overall_assessment: string;
    recommended_route_id: string;
    route_assessments: {
      route_id: string;
      risk_level: string;
      score: number;
      justification: string;
    }[];
  };
  result: {
    final_answer: string;
  };
};

const initialRun: RunState = {
  status: "idle",
  task_parser: {
    status: "idle",
    task_type: "—",
    target: "—",
    starting_materials: [],
    confidence: 0,
  },
  route: {
    status: "idle",
    target: "—",
    route_count: 0,
    confidence: 0,
    routes: [],
  },
  methods: {
    status: "idle",
    results: [],
    message: "Ожидание запроса.",
  },
  reagents: {
    status: "idle",
    results: [],
    message: "Ожидание запроса.",
  },
  safety: {
    status: "idle",
    overall_assessment: "—",
    recommended_route_id: "—",
    route_assessments: [],
  },
  result: {
    final_answer: "Введите запрос, чтобы запустить pipeline.",
  },
};

export default function App() {
  const [input, setInput] = useState("");
  const [activeTab, setActiveTab] = useState<PipelineTab>("task_parser");
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
    if (tab === "task_parser") return run.task_parser.status;
    if (tab === "route") return run.route.status;
    if (tab === "methods") return run.methods.status;
    if (tab === "reagents") return run.reagents.status;
    if (tab === "safety") return run.safety.status;
    return run.status;
  };

  const handleSend = async () => {
  if (!input.trim()) return;

  const query = input.trim();

  setMessages((prev) => [...prev, { role: "user", text: query }]);
  setInput("");
  setActiveTab("task_parser");

  try {
    const response = await fetch("http://127.0.0.1:8000/run", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }

    const data = await response.json();

    setRun({
      status: "completed",
      task_parser: {
        status: "completed",
        task_type: data.task_parser?.task_type ?? "—",
        target: data.task_parser?.target ?? "—",
        starting_materials: data.task_parser?.starting_materials ?? [],
        confidence: data.task_parser?.confidence ?? 0,
      },
      route: {
        status: "completed",
        target: data.route?.target ?? "—",
        route_count: data.route?.route_count ?? 0,
        confidence: data.route?.confidence ?? 0,
        routes: (data.route?.routes ?? []).map((r: any) => ({
          id: r.id,
          summary: r.summary,
        })),
      },
      methods: {
        status: "completed",
        results: (data.methods?.methods_found ?? []).map((m: any) => m.reaction),
        message: data.methods?.message ?? "ok",
      },
      reagents: {
        status: "completed",
        results: data.reagents?.checked ?? [],
        message:
          data.reagents?.issues?.length > 0
            ? `Найдено проблем: ${data.reagents.issues.length}`
            : "Проблем не обнаружено",
      },
      safety: {
        status: "completed",
        overall_assessment: data.safety?.overall_assessment ?? "—",
        recommended_route_id: data.safety?.recommended_route_id ?? "—",
        route_assessments: (data.safety?.route_assessments ?? []).map((item: any) => ({
          route_id: item.route_id,
          risk_level: item.risk_level,
          score: item.score,
          justification: item.justification,
        })),
      },
      result: {
        final_answer: data.result?.final_answer ?? "Нет ответа",
      },
    });

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        text: data.result?.final_answer ?? "Нет ответа от backend.",
      },
    ]);

    setActiveTab("result");
  } catch (error) {
    console.error(error);
  }
};

  const renderPipelineContent = () => {
    if (activeTab === "task_parser") {
      return (
        <div className="pipeline-details">
          <h3>Task Parser</h3>
          <p><strong>Status:</strong> {run.task_parser.status}</p>
          <p><strong>Task type:</strong> {run.task_parser.task_type}</p>
          <p><strong>Target:</strong> {run.task_parser.target}</p>
          <p><strong>Starting materials:</strong> {run.task_parser.starting_materials.join(", ") || "—"}</p>
          <p><strong>Confidence:</strong> {run.task_parser.confidence}</p>
        </div>
      );
    }

    if (activeTab === "route") {
      return (
        <div className="pipeline-details">
          <h3>Route Agent</h3>
          <p><strong>Status:</strong> {run.route.status}</p>
          <p><strong>Target:</strong> {run.route.target}</p>
          <p><strong>Route count:</strong> {run.route.route_count}</p>
          <p><strong>Confidence:</strong> {run.route.confidence}</p>

          {run.route.routes.map((route) => (
            <div key={route.id} style={{ marginTop: "12px" }}>
              <p><strong>Route ID:</strong> {route.id}</p>
              <p><strong>Summary:</strong> {route.summary}</p>
            </div>
          ))}
        </div>
      );
    }

    if (activeTab === "methods") {
      return (
        <div className="pipeline-details">
          <h3>Methods Agent</h3>
          <p><strong>Status:</strong> {run.methods.status}</p>
          <p><strong>Results count:</strong> {run.methods.results.length}</p>
          <p><strong>Message:</strong> {run.methods.message || "—"}</p>
        </div>
      );
    }

    if (activeTab === "reagents") {
      return (
        <div className="pipeline-details">
          <h3>Reagents Agent</h3>
          <p><strong>Status:</strong> {run.reagents.status}</p>
          <p><strong>Results count:</strong> {run.reagents.results.length}</p>
          <p><strong>Message:</strong> {run.reagents.message || "—"}</p>
        </div>
      );
    }

    if (activeTab === "safety") {
      return (
        <div className="pipeline-details">
          <h3>Safety Agent</h3>
          <p><strong>Status:</strong> {run.safety.status}</p>
          <p><strong>Overall assessment:</strong> {run.safety.overall_assessment}</p>
          <p><strong>Recommended route:</strong> {run.safety.recommended_route_id || "—"}</p>

          {run.safety.route_assessments.map((item) => (
            <div key={item.route_id} style={{ marginTop: "12px" }}>
              <p><strong>Route ID:</strong> {item.route_id}</p>
              <p><strong>Risk level:</strong> {item.risk_level}</p>
              <p><strong>Score:</strong> {item.score}</p>
              <p><strong>Justification:</strong> {item.justification}</p>
            </div>
          ))}
        </div>
      );
    }

    return (
      <div className="pipeline-details">
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
                { key: "task_parser", label: "Task Parser" },
                { key: "route", label: "Route Agent" },
                { key: "methods", label: "Methods Agent" },
                { key: "reagents", label: "Reagents Agent" },
                { key: "safety", label: "Safety Agent" },
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

            <div className="pipeline-card">{renderPipelineContent()}</div>
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