import React, { useState } from "react";

type Props = {
  healthUrl?: string;
};

export const CallCenterHUD: React.FC<Props> = ({ healthUrl = "/health" }) => {
  const [demoActive, setDemoActive] = useState(false);
  const [health, setHealth] = useState<"unknown" | "checking" | "online" | "error">("unknown");

  async function checkHealth() {
    setHealth("checking");
    try {
      const response = await fetch(healthUrl);
      if (!response.ok) throw new Error("Health endpoint returned an error");
      setHealth("online");
    } catch {
      setHealth("error");
    }
  }

  return (
    <main style={{ background: "#f8fafc", color: "#0f172a", padding: 24, fontFamily: "system-ui, sans-serif" }}>
      <header style={{ background: "#0f172a", color: "white", padding: 16 }}>
        <strong>HRGEN Voice Operations</strong>
        <span style={{ marginLeft: 16 }}>Provider and call status are reported separately</span>
      </header>
      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 24, marginTop: 24 }}>
        <article style={{ background: "white", border: "1px solid #e2e8f0", padding: 24 }}>
          <h2>Backend health</h2>
          <p>Status: <strong>{health}</strong></p>
          <button onClick={checkHealth}>Check backend</button>
          <p style={{ color: "#64748b" }}>This checks the health endpoint; it does not place a call.</p>
        </article>
        <article style={{ background: "white", border: "1px solid #e2e8f0", padding: 24 }}>
          <h2>UI demo state</h2>
          <p>{demoActive ? "Demo toggle enabled" : "Demo toggle disabled"}</p>
          <button onClick={() => setDemoActive((value) => !value)}>
            {demoActive ? "Disable demo toggle" : "Enable demo toggle"}
          </button>
          <p style={{ color: "#64748b" }}>No SIP, WhatsApp, or telephone connection is initiated by this control.</p>
        </article>
      </section>
    </main>
  );
};
