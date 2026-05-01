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

PALETTE = [
    "#ff6b6b","#ffa94d","#ffd43b","#69db7c","#38d9a9",
    "#4dabf7","#748ffc","#da77f2","#f783ac","#a9e34b",
    "#63e6be","#74c0fc","#e599f7","#ffa8a8","#ffe066",
]

# ── CSS base compartilhado ─────────────────────────────────
SHARED_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
    background: #201c1c;
    color: #e8e0d8;
    font-family: 'Rajdhani', sans-serif;
    min-height: 100vh;
}

@keyframes glowing {
    0%   { background-position: 0 0; }
    50%  { background-position: 400% 0; }
    100% { background-position: 0 0; }
}

/* ── SIDEBAR ── */
.sidebar {
    position: fixed;
    top: 0; left: 0;
    height: 100vh;
    width: 56px;
    background: #140f0f;
    border-right: 1px solid #2e2828;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 18px 0;
    gap: 8px;
    z-index: 100;
    transition: width .3s ease;
    overflow: hidden;
}

.sidebar.open {
    width: 260px;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: flex-start;
    padding: 14px 12px;
    gap: 10px;
    height: auto;
    bottom: auto;
    border-radius: 0 0 16px 0;
    border-bottom: 1px solid #2e2828;
}

.sidebar-toggle {
    width: 36px; height: 36px;
    border-radius: 8px;
    border: none;
    background: #1a1616;
    color: #8a7f7f;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
    transition: color .2s;
    margin-bottom: 4px;
}
.sidebar-toggle:hover { color: #fff; }
.sidebar.open .sidebar-toggle { margin-bottom: 0; }

.sidebar-brand {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #5a5050;
    letter-spacing: 2px;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity .2s;
    flex: 1;
    align-self: center;
}
.sidebar.open .sidebar-brand { opacity: 1; }

.sidebar-divider {
    width: 32px; height: 1px;
    background: #2e2828;
    flex-shrink: 0;
    transition: width .3s;
}
.sidebar.open .sidebar-divider { display: none; }

/* ── NAV BUTTONS inside sidebar ── */
.glow-btn {
    position: relative;
    z-index: 0;
    width: 36px; height: 36px;
    padding: 0;
    background: #111;
    color: #e8e0d8;
    border: none;
    border-radius: 8px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    cursor: pointer;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: color .2s, width .3s, padding .3s;
    white-space: nowrap;
    overflow: hidden;
    flex-shrink: 0;
}

.sidebar.open .glow-btn {
    width: auto;
    padding: 0 14px;
    height: 36px;
}

.glow-btn .btn-label {
    display: none;
    font-size: 13px;
}
.sidebar.open .glow-btn .btn-label { display: inline; }

.glow-btn.active { color: #fff; }

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
    transition: opacity .3s;
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

/* ── MAIN CONTENT offset ── */
.main {
    margin-left: 56px;
    min-height: 100vh;
}

/* ── PAGE HEADER ── */
.page-header {
    text-align: center;
    padding: 40px 24px 12px;
}
.page-header h1 {
    font-size: 34px;
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

/* ── CHART LAYOUT ── */
.chart-outer {
    max-width: 900px;
    margin: 28px auto;
    padding: 0 20px 60px;
}

.card {
    background: #1a1616;
    border: 1px solid #2e2828;
    border-radius: 16px;
    padding: 28px 24px;
    position: relative;
    overflow: hidden;
    display: flex;
    gap: 32px;
    align-items: flex-start;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #4a3f3f, transparent);
    pointer-events: none;
}

/* grafico tamanho fixo */
.chart-col {
    flex-shrink: 0;
    width: 280px;
    position: relative;
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
    font-size: 26px;
    font-weight: 700;
    color: #fff;
    line-height: 1;
}
.chart-center-label .total-label {
    font-size: 10px;
    color: #5a5050;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* legenda scroll independente */
.legend-col {
    flex: 1;
    min-width: 0;
    max-height: 280px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 7px;
    padding-right: 4px;
}

.legend-col::-webkit-scrollbar { width: 4px; }
.legend-col::-webkit-scrollbar-track { background: transparent; }
.legend-col::-webkit-scrollbar-thumb { background: #2e2828; border-radius: 4px; }

.legend-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    background: #201c1c;
    border: 1px solid #2e2828;
    border-radius: 8px;
    cursor: pointer;
    transition: border-color .2s, opacity .2s;
    user-select: none;
    flex-shrink: 0;
}
.legend-item:hover { border-color: #4a3f3f; }
.legend-item.hidden { opacity: .35; }

.legend-swatch {
    width: 10px; height: 10px;
    border-radius: 3px;
    flex-shrink: 0;
}
.legend-name {
    flex: 1;
    font-size: 14px;
    font-weight: 600;
    color: #e8e0d8;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.legend-pct {
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #8a7f7f;
    flex-shrink: 0;
}
.legend-count {
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #5a5050;
    flex-shrink: 0;
}

/* ── TIMESTAMP ── */
.timestamp {
    text-align: center;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #3a3333;
    letter-spacing: 2px;
    margin-top: 16px;
}

/* ── INDEX ── */
.index-wrap {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 40px 24px;
}

.greeting {
    text-align: center;
    margin-bottom: 48px;
}
.greeting .time-msg {
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #5a5050;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.greeting h1 {
    font-size: clamp(28px, 5vw, 52px);
    font-weight: 700;
    letter-spacing: 2px;
    color: #fff;
    line-height: 1.1;
}
.greeting h1 span {
    background: linear-gradient(90deg,#ff6b6b,#ffd43b,#69db7c,#4dabf7,#da77f2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.greeting .count-line {
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    color: #5a5050;
    letter-spacing: 2px;
    margin-top: 12px;
}
.greeting .count-line strong {
    color: #8a7f7f;
}

.index-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    width: 100%;
    max-width: 520px;
}

.index-btn {
    position: relative;
    z-index: 0;
    width: 100%;
    height: 90px;
    background: #111;
    color: #e8e0d8;
    border: none;
    border-radius: 14px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    cursor: pointer;
    text-decoration: none;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 12px;
    transition: color .2s;
}
.index-btn .icon { font-size: 26px; }

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
    transition: opacity .35s;
    border-radius: 14px;
}
.index-btn::after {
    content: '';
    z-index: -1;
    position: absolute;
    width: 100%; height: 100%;
    background: #111;
    left: 0; top: 0;
    border-radius: 14px;
}
.index-btn:hover::before { opacity: 1; }
.index-btn:hover { color: #fff; }
.index-btn:active { color: #000; }
.index-btn:active::after { background: transparent; }
"""

# ── Sidebar ───────────────────────────────────────────────
NAV_LINKS = [
    ("index.html",     "🏠", "Home"),
    ("franquias.html", "🎮", "Franquias"),
    ("paises.html",    "🌍", "Países"),
    ("consoles.html",  "🕹️",  "Consoles"),
    ("nei.html",       "📊", "Experiência"),
]

SIDEBAR_JS = """
<script>
(function(){
    var sb = document.getElementById('sidebar');
    var toggle = document.getElementById('sb-toggle');
    toggle.addEventListener('click', function(e){
        e.stopPropagation();
        sb.classList.toggle('open');
    });
    document.addEventListener('click', function(e){
        if (!sb.contains(e.target)) sb.classList.remove('open');
    });
})();
</script>
"""

def build_sidebar(active_href):
    links_html = ""
    for href, icon, label in NAV_LINKS:
        cls = "glow-btn active" if href == active_href else "glow-btn"
        links_html += f'<a href="{href}" class="{cls}">{icon}<span class="btn-label">{label}</span></a>\n'
    return f"""
<nav class="sidebar" id="sidebar">
  <button class="sidebar-toggle" id="sb-toggle" title="Menu">&#9776;</button>
  <span class="sidebar-brand">// GAME.DB</span>
  <div class="sidebar-divider"></div>
  {links_html}
</nav>
{SIDEBAR_JS}
"""

# ── Página de gráfico ─────────────────────────────────────
def build_chart_page(title, subtitle, counts_dict, active_href, show_center=True):
    agora  = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    labels = list(counts_dict.keys())
    counts = list(counts_dict.values())
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]
    total  = sum(counts)
    unique = len(labels)

    labels_json = json.dumps(labels, ensure_ascii=False)
    counts_json = json.dumps(counts)
    colors_json = json.dumps(colors)

    sidebar = build_sidebar(active_href)

    center_html = ""
    if show_center:
        center_html = f"""
      <div class="chart-center-label">
        <div class="total">{unique}</div>
        <div class="total-label">tipos</div>
      </div>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Game.DB</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
{SHARED_CSS}
</style>
</head>
<body>

{sidebar}

<div class="main">

  <div class="page-header">
    <h1>{title}</h1>
    <p class="sub">{subtitle}</p>
  </div>

  <div class="chart-outer">
    <div class="card">

      <div class="chart-col">
        <canvas id="myChart"></canvas>
        {center_html}
      </div>

      <div class="legend-col" id="legend"></div>

    </div>
    <p class="timestamp">ATUALIZADO EM {agora}</p>
  </div>

</div>

<script>
const LABELS = {labels_json};
const COUNTS = {counts_json};
const COLORS = {colors_json};
const TOTAL  = {total};

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
    const item = document.createElement('div');
    item.className = 'legend-item' + (hidden.has(i) ? ' hidden' : '');
    item.innerHTML = `
      <div class="legend-swatch" style="background:${{COLORS[i]}}"></div>
      <span class="legend-name">${{label}}</span>
      <span class="legend-pct">${{pct}}%</span>
      <span class="legend-count">${{COUNTS[i]}}</span>`;
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


# ── Index ─────────────────────────────────────────────────
def gerar_index(total_jogos):
    hora = datetime.datetime.now().hour
    if hora < 12:
        saudacao = "Bom dia"
    elif hora < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    sidebar = build_sidebar("index.html")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Game.DB</title>
<style>
{SHARED_CSS}
</style>
</head>
<body>

{sidebar}

<div class="main">
  <div class="index-wrap">

    <div class="greeting">
      <p class="time-msg">// game.db</p>
      <h1>{saudacao}, <span>Eduardo!</span></h1>
      <p class="count-line">você já finalizou um total de <strong>{total_jogos} jogos</strong></p>
    </div>

    <div class="index-grid">
      <a href="franquias.html" class="index-btn"><span class="icon">🎮</span> Franquias</a>
      <a href="paises.html"    class="index-btn"><span class="icon">🌍</span> Países</a>
      <a href="consoles.html"  class="index-btn"><span class="icon">🕹️</span>  Consoles</a>
      <a href="nei.html"       class="index-btn"><span class="icon">📊</span> Experiência</a>
    </div>

  </div>
</div>

</body>
</html>""")


# ── Helpers Notion ────────────────────────────────────────
def get_value(props, nome):
    for key in props:
        key_norm  = key.lower().replace("í","i").replace("é","e")
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
    has_more    = True
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
        has_more    = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    if not all_results:
        return None, None, "Base vazia"

    jogos    = []
    consoles = []

    for item in all_results:
        if item.get("archived", False):
            continue
        props = item.get("properties", {})
        jogos.append({
            "Franquia": get_value(props, "Franquia"),
            "Pais":     get_value(props, "Países"),
            "NEI":      get_value(props, "NEI"),
        })
        try:
            for c in props["Console"]["multi_select"]:
                consoles.append(c["name"])
        except:
            pass

    return pd.DataFrame(jogos), pd.DataFrame(consoles, columns=["Console"]), None


# ── Execução ──────────────────────────────────────────────
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
    total     = len(df_jogos)

    with open("franquias.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Franquias", f"{total} jogos no acervo",
            franquias, "franquias.html", show_center=True
        ))

    with open("paises.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Países", "origem dos jogos",
            paises, "paises.html", show_center=True
        ))

    with open("consoles.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Consoles", "plataformas do acervo",
            consoles, "consoles.html", show_center=True
        ))

    with open("nei.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Experiência", "nível de interesse (NEI)",
            nei, "nei.html", show_center=False
        ))

    gerar_index(total)
    print("Páginas geradas com sucesso.")
