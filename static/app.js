/* ETF Tournament — frontend controller */

let pollTimer = null;

// ── Polling ───────────────────────────────────────────────────────────────────

function poll() {
  fetch("/api/status")
    .then(r => r.json())
    .then(s => {
      document.getElementById("progress-bar").style.width = s.progress + "%";
      document.getElementById("loader-msg").textContent = s.message || "Working…";

      if (s.last_updated) {
        document.getElementById("last-updated").textContent = "Updated: " + s.last_updated;
      }
      if (s.n_etfs) {
        document.getElementById("etf-count").textContent = s.n_etfs + " ETFs";
      }

      if (s.status === "ready") {
        clearInterval(pollTimer);
        loadAllData();
      } else if (s.status === "error") {
        clearInterval(pollTimer);
        showError(s.message);
      }
    })
    .catch(() => {});
}

function startPolling() {
  pollTimer = setInterval(poll, 1500);
  poll();
}

// ── Data loading ──────────────────────────────────────────────────────────────

function loadAllData() {
  Promise.all([
    fetch("/api/equity").then(r => r.json()),
    fetch("/api/metrics").then(r => r.json()),
    fetch("/api/rankings").then(r => r.json()),
  ]).then(([equity, metrics, rankings]) => {
    renderEquityChart(equity);
    renderMetricsTable(metrics);
    renderRankingsTable(rankings);
    document.getElementById("loader").classList.add("hidden");
    document.getElementById("app").classList.remove("hidden");
  }).catch(err => showError(String(err)));
}

// ── Chart ─────────────────────────────────────────────────────────────────────

// 5 colours for Top-1…Top-5; improved uses same colour but solid/thicker
const COLORS = ["#58a6ff", "#3fb950", "#f0883e", "#d2a8ff", "#79c0ff"];

function renderEquityChart(equity) {
  const traces = [];
  const order = ["top_1","top_2","top_3","top_4","top_5",
                 "top_1_improved","top_2_improved","top_3_improved","top_4_improved","top_5_improved",
                 "benchmark"];

  order.forEach((key, idx) => {
    if (!equity[key]) return;
    const d = equity[key];
    const isImproved  = d.improved === true;
    const isBenchmark = key === "benchmark";
    const colorIdx = isBenchmark ? -1 : (parseInt(key.match(/\d+/)[0]) - 1);
    const color = isBenchmark ? "#8b949e" : COLORS[colorIdx];

    traces.push({
      x: d.dates,
      y: d.values,
      name: d.name,
      type: "scatter",
      mode: "lines",
      line: {
        color,
        width: isBenchmark ? 1.5 : (isImproved ? 2.5 : 1.2),
        dash:  isBenchmark ? "dot" : (isImproved ? "solid" : "dash"),
      },
      opacity: isBenchmark ? 0.8 : (isImproved ? 1 : 0.55),
    });
  });

  const layout = {
    paper_bgcolor: "#161b22",
    plot_bgcolor: "#161b22",
    font: { color: "#e6edf3", size: 12 },
    margin: { l: 70, r: 20, t: 10, b: 50 },
    legend: {
      bgcolor: "rgba(0,0,0,0)",
      bordercolor: "#30363d",
      borderwidth: 1,
      x: 0.01, y: 0.99,
      font: { size: 11 },
    },
    xaxis: { gridcolor: "#21262d", zeroline: false },
    yaxis: {
      gridcolor: "#21262d",
      zeroline: false,
      tickprefix: "$",
      tickformat: ",.0f",
    },
    hovermode: "x unified",
    annotations: [{
      x: 0.5, y: 1.04, xref: "paper", yref: "paper",
      text: "— Dashed = Original (daily rebalance)   |   ── Solid = Improved (vol-adj, 60/120d, 10-day hold, +inverse ETFs)   |   ··· = SPY",
      showarrow: false,
      font: { size: 11, color: "#8b949e" },
      xanchor: "center",
    }],
  };

  Plotly.newPlot("equity-chart", traces, layout, { responsive: true, displayModeBar: false });
}

// ── Tables ────────────────────────────────────────────────────────────────────

function pct(val, decimals = 2) {
  if (val === null || val === undefined) return '<span class="neutral">—</span>';
  const cls = val >= 0 ? "pos" : "neg";
  const sign = val >= 0 ? "+" : "";
  return `<span class="${cls}">${sign}${val.toFixed(decimals)}%</span>`;
}

function renderMetricsTable(metrics) {
  const tbody = document.getElementById("metrics-body");
  tbody.innerHTML = "";

  // Find best CAGR among all strategies
  const best = metrics[0];

  metrics.forEach(row => {
    const isBest     = row.strategy === best.strategy;
    const isImproved = row.strategy.includes("Improved");
    const isBenchmark = row.strategy === "SPY";
    const tr = document.createElement("tr");
    if (isBest) tr.classList.add("best-row");
    if (isImproved) tr.classList.add("improved-row");

    let badge = "";
    if (isBest)      badge = ' <span class="tag-best">★ Best</span>';
    if (isImproved)  badge += ' <span class="tag-improved">Improved</span>';
    if (isBenchmark) badge += ' <span class="tag-bm">Benchmark</span>';

    tr.innerHTML = `
      <td class="strategy-name">${row.strategy}${badge}</td>
      <td>${pct(row.total_return)}</td>
      <td>${pct(row.cagr)}</td>
      <td>${row.sharpe.toFixed(3)}</td>
      <td>${pct(row.max_drawdown)}</td>
      <td>${row.win_rate.toFixed(1)}%</td>
    `;
    tbody.appendChild(tr);
  });
}

function rankBadge(rank) {
  if (rank === 1) return `<span class="rank-badge gold">1</span>`;
  if (rank === 2) return `<span class="rank-badge silver">2</span>`;
  if (rank === 3) return `<span class="rank-badge bronze">3</span>`;
  return `<span class="rank-badge">${rank}</span>`;
}

function renderRankingsTable(rankings) {
  const tbody = document.getElementById("rankings-body");
  tbody.innerHTML = "";
  rankings.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${rankBadge(row.rank)}</td>
      <td class="ticker">${row.ticker}</td>
      <td>${row.score.toFixed(4)}</td>
      <td>${pct(row.ret_20d)}</td>
      <td>${pct(row.ret_60d)}</td>
      <td>${pct(row.ret_120d)}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ── Actions ───────────────────────────────────────────────────────────────────

function triggerRefresh() {
  document.getElementById("app").classList.add("hidden");
  document.getElementById("error-box").classList.add("hidden");
  document.getElementById("loader").classList.remove("hidden");
  document.getElementById("progress-bar").style.width = "0%";
  document.getElementById("loader-msg").textContent = "Refreshing data…";
  fetch("/api/refresh", { method: "POST" })
    .then(() => startPolling())
    .catch(err => showError(String(err)));
}

function showError(msg) {
  document.getElementById("loader").classList.add("hidden");
  document.getElementById("app").classList.add("hidden");
  document.getElementById("error-msg").textContent = msg;
  document.getElementById("error-box").classList.remove("hidden");
}

// ── Init ──────────────────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => startPolling());
