import os
import requests
import pandas as pd
import datetime
import json

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

if not NOTION_TOKEN or not DATABASE_ID:
    raise ValueError("NOTION_TOKEN ou DATABASE_ID não configurados.")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

BG = "#201c1c"

GLOW_CSS = """
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    html, body {
        background: #201c1c;
        color: #e8e0d8;
        font-family: 'Rajdhani', sans-serif;
        min-height: 100vh;
    }

    /* ── NAV ── */
    nav {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        padding: 22px 24px;
        border-bottom: 1px solid #2e2828;
        flex-wrap: wrap;
    }

    .nav-brand {
        font-family: 'Share Tech Mono', monospace;
        font-size: 13px;
        color: #5a5050;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-right: auto;
    }

    .glow-btn {
        position: relative;
        z-index: 0;
        padding: 0 22px;
        height: 38px;
        background: #111;
        color: #e8e0d8;
        border: none;
        border-radius: 8px;
        font-family: 'Rajdhani', sans-serif;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        cursor: pointer;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 7px;
        transition: color .2s;
    }

    .glow-btn.active {
        color: #fff;
    }

    .glow-btn::before {
        content: '';
        background: linear-gradient(45deg,#ff0000,#ff7300,#fffb00,#48ff00,#00ffd5,#002bff,#7a00ff,#ff00c8,#ff0000);
        position: absolute;
        top: -2px; left: -2px;
        background-size: 400%;
        z-index: -1;
        filter: blur(5px);
        width: calc(100% + 4px);
        height: calc(100% + 4px);
        animation: glowing 20s linear infinite;
        opacity: 0;
        transition: opacity .3s ease-in-out;
        border-radius: 8px;
    }

    .glow-btn::after {
        content: '';
        z-index: -1;
        position: absolute;
        width: 100%; height: 100%;
        background: #111;
        left: 0; top: 0;
        border-radius: 8px;
    }

    .glow-btn:hover::before,
    .glow-btn.active::before { opacity: 1; }

    .glow-btn:active { color: #000; }
    .glow-btn:active::after { background: transparent; }

    @keyframes glowing {
        0%   { background-position: 0 0; }
        50%  { background-position: 400% 0; }
        100% { background-position: 0 0; }
    }

    /* ── PAGE ── */
    .page-header {
        text-align: center;
        padding: 40px 24px 12px;
    }

    .page-header h1 {
        font-size: 36px;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #fff;
        line-height: 1;
    }

    .page-header .sub {
        font-family: 'Share Tech Mono', monospace;
        font-size: 11px;
        color: #5a5050;
        letter-spacing: 3px;
        margin-top: 6px;
    }

    /* ── CHART CARD ── */
    .chart-wrap {
        max-width: 680px;
        margin: 32px auto;
        padding: 0 20px 60px;
    }

    .card {
        background: #1a1616;
        border: 1px solid #2e2828;
        border-radius: 16px;
        padding: 32px 24px 24px;
        position: relative;
        overflow: hidden;
    }

    .card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #4a3f3f, transparent);
    }

    .chart-canvas-wrap {
        position: relative;
        width: 100%;
        max-width: 420px;
        margin: 0 auto;
    }

    .chart-center-label {
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        pointer-events: none;
    }

    .chart-center-label .total {
        font-family: 'Share Tech Mono', monospace;
        font-size: 28px;
        font-weight: 700;
        color: #fff;
        line-height: 1;
    }

    .chart-center-label .total-label {
        font-size: 11px;
        color: #5a5050;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 4px;
    }

    /* ── LEGEND ── */
    .legend {
        margin-top: 28px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        background: #201c1c;
        border: 1px solid #2e2828;
        border-radius: 8px;
        cursor: pointer;
        transition: border-color .2s, opacity .2s;
        user-select: none;
    }

    .legend-item:hover { border-color: #4a3f3f; }

    .legend-item.hidden {
        opacity: 0.35;
    }

    .legend-swatch {
        width: 12px; height: 12px;
        border-radius: 3px;
        flex-shrink: 0;
    }

    .legend-name {
        flex: 1;
        font-size: 15px;
        font-weight: 600;
        letter-spacing: 0.5px;
        color: #e8e0d8;
    }

    .legend-pct {
        font-family: 'Share Tech Mono', monospace;
        font-size: 13px;
        color: #8a7f7f;
    }

    .legend-count {
        font-family: 'Share Tech Mono', monospace;
        font-size: 13px;
        color: #5a5050;
    }

    /* ── TIMESTAMP ── */
    .timestamp {
        text-align: center;
        font-family: 'Share Tech Mono', monospace;
        font-size: 11px;
        color: #3a3333;
        letter-spacing: 2px;
        margin-top: 20px;
    }

    /* ── INDEX GRID ── */
    .index-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
        max-width: 500px;
        margin: 60px auto;
        padding: 0 24px;
    }

    .index-btn {
        position: relative;
        z-index: 0;
        width: 100%;
        aspect-ratio: 1;
        background: #111;
        color: #e8e0d8;
        border: none;
        border-radius: 16px;
        font-family: 'Rajdhani', sans-serif;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        cursor: pointer;
        text-decoration: none;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 10px;
        transition: color .2s;
    }

    .index-btn .icon { font-size: 32px; }

    .index-btn::before {
        content: '';
        background: linear-gradient(45deg,#ff0000,#ff7300,#fffb00,#48ff00,#00ffd5,#002bff,#7a00ff,#ff00c8,#ff0000);
        position: absolute;
        top: -2px; left: -2px;
        background-size: 400%;
        z-index: -1;
        filter: blur(8px);
        width: calc(100% + 4px);
        height: calc(100% + 4px);
        animation: glowing 20s linear infinite;
        opacity: 0;
        transition: opacity .35s ease-in-out;
        border-radius: 16px;
    }

    .index-btn::after {
        content: '';
        z-index: -1;
        position: absolute;
        width: 100%; height: 100%;
        background: #111;
        left: 0; top: 0;
        border-radius: 16px;
    }

    .index-btn:hover::before { opacity: 1; }
    .index-btn:hover { color: #fff; }
    .index-btn:active { color: #000; }
    .index-btn:active::after { background: transparent; }
"""

NAV_LINKS = [
    ("index.html", "🏠", "Home"),
    ("franquias.html", "🎮", "Franquias"),
    ("paises.html", "🌍", "Países"),
    ("consoles.html", "🕹️", "Consoles"),
    ("nei.html", "📊", "Experiência"),
]

# Palette cíclica dark/neon
PALETTE = [
    "#ff6b6b","#ffa94d","#ffd43b","#69db7c","#38d9a9",
    "#4dabf7","#748ffc","#da77f2","#f783ac","#a9e34b",
    "#63e6be","#74c0fc","#e599f7","#ffa8a8","#ffe066",
]


def get_value(props, nome):
    for key in props:
        key_norm = key.lower().replace("í","i").replace("é","e")
        nome_norm = nome.lower().replace("í","i").replace("é","e")
        if key_norm == nome_norm:
            try:
                prop = props[key]
                if prop["type"] == "select":
                    return prop["select"]["name"] if prop["select"] else "Não definido"
                elif prop["type"] == "multi_select":
                    return ", ".join([x["name"] for x in prop["multi_select"]]) or "Não definido"
                elif prop["type"] == "title":
                    return prop["title"][0]["plain_text"] if prop["title"] else "Sem título"
                elif prop["type"] == "rich_text":
                    return prop["rich_text"][0]["plain_text"] if prop["rich_text"] else "Não definido"
            except:
                return "Não definido"
    return "Não definido"


def carregar_dados_notion():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    all_results = []
    has_more = True
    next_cursor = None

    while has_more:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return None, None, f"Erro API: {response.status_code}"
        data = response.json()
        all_results.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    if not all_results:
        return None, None, "Base vazia"

    jogos = []
    consoles = []

    for item in all_results:
        if item.get("archived", False):
            continue
        props = item.get("properties", {})
        jogos.append({
            "Franquia": get_value(props, "Franquia"),
            "Pais": get_value(props, "Países"),
            "NEI": get_value(props, "NEI")
        })
        try:
            for c in props["Console"]["multi_select"]:
                consoles.append(c["name"])
        except:
            pass

    return pd.DataFrame(jogos), pd.DataFrame(consoles, columns=["Console"]), None


def build_nav(active_href):
    links = []
    for href, icon, label in NAV_LINKS:
        cls = 'glow-btn active' if href == active_href else 'glow-btn'
        links.append(f'<a href="{href}" class="{cls}">{icon} {label}</a>')
    return f'<nav><span class="nav-brand">// GAME.DB</span>{"".join(links)}</nav>'


def build_chart_page(title, subtitle, counts_dict, active_href):
    """
    counts_dict: { label: count }
    Generates a page with a Chart.js donut where hiding a slice
    keeps the percentages based on the FULL total (not just visible).
    """
    agora = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    total = sum(counts_dict.values())

    labels = list(counts_dict.keys())
    counts = list(counts_dict.values())
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]

    labels_json = json.dumps(labels, ensure_ascii=False)
    counts_json = json.dumps(counts)
    colors_json = json.dumps(colors)

    nav = build_nav(active_href)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Game.DB</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
{GLOW_CSS}
</style>
</head>
<body>

{nav}

<div class="page-header">
  <h1>{title}</h1>
  <p class="sub">{subtitle}</p>
</div>

<div class="chart-wrap">
  <div class="card">
    <div class="chart-canvas-wrap">
      <canvas id="myChart"></canvas>
      <div class="chart-center-label">
        <div class="total" id="centerTotal">{total}</div>
        <div class="total-label">total</div>
      </div>
    </div>

    <div class="legend" id="legend"></div>
  </div>

  <p class="timestamp">ATUALIZADO EM {agora}</p>
</div>

<script>
const LABELS  = {labels_json};
const COUNTS  = {counts_json};
const COLORS  = {colors_json};
const TOTAL   = {total};

const hidden = new Set();

const ctx = document.getElementById('myChart').getContext('2d');

function buildDataset() {{
  return COUNTS.map((c, i) => hidden.has(i) ? 0 : c);
}}

const chart = new Chart(ctx, {{
  type: 'doughnut',
  data: {{
    labels: LABELS,
    datasets: [{{
      data: buildDataset(),
      backgroundColor: COLORS,
      borderColor: '#201c1c',
      borderWidth: 3,
      hoverOffset: 8,
    }}]
  }},
  options: {{
    responsive: true,
    cutout: '62%',
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{
          label: (ctx) => {{
            const i = ctx.dataIndex;
            const pct = ((COUNTS[i] / TOTAL) * 100).toFixed(1);
            return ` ${{COUNTS[i]}} (${{pct}}%)`;
          }}
        }},
        backgroundColor: '#1a1616',
        titleColor: '#e8e0d8',
        bodyColor: '#8a7f7f',
        borderColor: '#2e2828',
        borderWidth: 1,
        padding: 12,
      }}
    }},
    animation: {{ duration: 500 }},
  }}
}});

function renderLegend() {{
  const leg = document.getElementById('legend');
  leg.innerHTML = '';
  LABELS.forEach((label, i) => {{
    const pct = ((COUNTS[i] / TOTAL) * 100).toFixed(1);
    const isHidden = hidden.has(i);
    const item = document.createElement('div');
    item.className = 'legend-item' + (isHidden ? ' hidden' : '');
    item.innerHTML = `
      <div class="legend-swatch" style="background:${{COLORS[i]}}"></div>
      <span class="legend-name">${{label}}</span>
      <span class="legend-pct">${{pct}}%</span>
      <span class="legend-count">${{COUNTS[i]}}</span>
    `;
    item.addEventListener('click', () => {{
      if (hidden.has(i)) hidden.delete(i);
      else hidden.add(i);
      chart.data.datasets[0].data = buildDataset();
      chart.update();
      renderLegend();
    }});
    leg.appendChild(item);
  }});
}}

renderLegend();
</script>
</body>
</html>"""


def gerar_index():
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Game.DB</title>
<style>
{GLOW_CSS}

body {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}}

.index-title {{
    font-family: 'Share Tech Mono', monospace;
    text-align: center;
    color: #3a3333;
    font-size: 11px;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 40px;
}}

.index-title strong {{
    display: block;
    font-family: 'Rajdhani', sans-serif;
    font-size: 42px;
    font-weight: 700;
    color: #fff;
    letter-spacing: 6px;
    margin-bottom: 4px;
}}
</style>
</head>
<body>

<div class="index-title">
  <strong>GAME.DB</strong>
  // dashboard de acervo
</div>

<div class="index-grid">
  <a href="franquias.html" class="index-btn">
    <span class="icon">🎮</span>
    Franquias
  </a>
  <a href="paises.html" class="index-btn">
    <span class="icon">🌍</span>
    Países
  </a>
  <a href="consoles.html" class="index-btn">
    <span class="icon">🕹️</span>
    Consoles
  </a>
  <a href="nei.html" class="index-btn">
    <span class="icon">📊</span>
    Experiência
  </a>
</div>

</body>
</html>""")


# ── EXECUÇÃO ──────────────────────────────────────────────

df_jogos, df_consoles, err = carregar_dados_notion()

if err:
    print(f"Erro: {err}")
else:
    def to_counts(series):
        return {k: int(v) for k, v in series.value_counts().items()}

    franquias = to_counts(df_jogos["Franquia"])
    paises    = to_counts(df_jogos["Pais"])
    nei       = to_counts(df_jogos["NEI"])
    consoles  = to_counts(df_consoles["Console"])

    total = len(df_jogos)

    with open("franquias.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Franquias", f"{total} jogos no acervo",
            franquias, "franquias.html"
        ))

    with open("paises.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Países", "origem dos jogos",
            paises, "paises.html"
        ))

    with open("consoles.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Consoles", "plataformas do acervo",
            consoles, "consoles.html"
        ))

    with open("nei.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Experiência", "nível de interesse (NEI)",
            nei, "nei.html"
        ))

    gerar_index()
    print("Páginas geradas com sucesso.")
