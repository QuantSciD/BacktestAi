"use client";

import React, { useState } from "react";
import "./page.css";

type Suggestion = {
  title: string;
  description: string;
  risk_note?: string | null;
};

type BacktestResponse = {
  metrics: Record<string, number | string>;
  plot_url?: string | null;
  suggestions: Suggestion[];
};

export default function HomePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BacktestResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!file) {
      setError("Please select a CSV file.");
      return;
    }

    setError(null);
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/backtest", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        setError(text || "Request failed");
        return;
      }

      const data = (await res.json()) as BacktestResponse;
      setResult(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unexpected error";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <div className="app-pill">Backtest Lab</div>
          <h1 className="app-title">CSV Backtest + AI Experiments</h1>
          <p className="app-subtitle">
            Upload a CSV with a <code>price</code> column to run a baseline
            backtest.
          </p>
        </div>
      </header>

      <form onSubmit={handleSubmit} className="upload-bar">
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <button type="submit" disabled={loading} className="button-primary">
          {loading ? "Running..." : "Run backtest"}
        </button>
      </form>

      {error && <div className="error-banner">{error}</div>}

      {result && (
        <>
          <h2 className="section-title">Metrics</h2>
          <div className="metrics-grid">
            {Object.entries(result.metrics).map(([k, v]) => (
              <div key={k} className="metric-card">
                <div className="metric-label">{k}</div>
                <div className="metric-value">{String(v)}</div>
              </div>
            ))}
          </div>

          {result.plot_url && (
            <>
              <h2 className="section-title">Equity curve</h2>
              <img
                src={`http://localhost:8000${result.plot_url}`}
                alt="Equity curve"
                style={{ width: "100%", borderRadius: 12, marginTop: 8 }}
              />
            </>
          )}

          {result.suggestions?.length > 0 && (
            <>
              <h2 className="section-title">AI experiment suggestions</h2>
              <div className="suggestions-grid">
                {result.suggestions.map((s, idx) => (
                  <div key={idx} className="suggestion-card">
                    <div className="suggestion-title">{s.title}</div>
                    <p>{s.description}</p>
                    {s.risk_note && (
                      <p className="suggestion-risk">{s.risk_note}</p>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </main>
  );
}
