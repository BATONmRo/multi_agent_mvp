type Props = {
  title: string;
  status: string;
  children?: React.ReactNode;
};

export function AgentCard({ title, status, children }: Props) {
  return (
    <div
      style={{
        border: "1px solid #ccc",
        borderRadius: "8px",
        padding: "16px",
        marginBottom: "12px",
      }}
    >
      <h3>{title}</h3>
      <p>Status: {status}</p>
      <div>{children}</div>
    </div>
  );
}