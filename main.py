import os
import requests
import pandas as pd
import datetime
import json

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID  = os.environ.get("DATABASE_ID")

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

# ── Mapa sigla/nome → emoji de bandeira ───────────────────
COUNTRY_EMOJI = {
    "BR": "🇧🇷", "BRASIL": "🇧🇷", "BRAZIL": "🇧🇷",
    "US": "🇺🇸", "USA": "🇺🇸", "EUA": "🇺🇸", "ESTADOS UNIDOS": "🇺🇸",
    "JP": "🇯🇵", "JAPÃO": "🇯🇵", "JAPAN": "🇯🇵", "JAPAO": "🇯🇵",
    "UK": "🇬🇧", "GB": "🇬🇧", "REINO UNIDO": "🇬🇧",
    "DE": "🇩🇪", "ALEMANHA": "🇩🇪", "GERMANY": "🇩🇪",
    "FR": "🇫🇷", "FRANCA": "🇫🇷", "FRANCE": "🇫🇷", "FRANCA": "🇫🇷",
    "CA": "🇨🇦", "CANADA": "🇨🇦", "CANADÁ": "🇨🇦",
    "AU": "🇦🇺", "AUSTRALIA": "🇦🇺", "AUSTRÁLIA": "🇦🇺",
    "KR": "🇰🇷", "COREIA": "🇰🇷", "KOREA": "🇰🇷", "COREIA DO SUL": "🇰🇷",
    "CN": "🇨🇳", "CHINA": "🇨🇳",
    "ES": "🇪🇸", "ESPANHA": "🇪🇸", "SPAIN": "🇪🇸",
    "IT": "🇮🇹", "ITALIA": "🇮🇹", "ITÁLIA": "🇮🇹", "ITALY": "🇮🇹",
    "SE": "🇸🇪", "SUECIA": "🇸🇪", "SUÉCIA": "🇸🇪", "SWEDEN": "🇸🇪",
    "FI": "🇫🇮", "FINLANDIA": "🇫🇮", "FINLÂNDIA": "🇫🇮", "FINLAND": "🇫🇮",
    "NL": "🇳🇱", "HOLANDA": "🇳🇱", "PAÍSES BAIXOS": "🇳🇱", "NETHERLANDS": "🇳🇱",
    "PL": "🇵🇱", "POLONIA": "🇵🇱", "POLÔNIA": "🇵🇱", "POLAND": "🇵🇱",
    "RU": "🇷🇺", "RUSSIA": "🇷🇺", "RÚSSIA": "🇷🇺",
    "AR": "🇦🇷", "ARGENTINA": "🇦🇷",
    "MX": "🇲🇽", "MEXICO": "🇲🇽", "MÉXICO": "🇲🇽",
    "PT": "🇵🇹", "PORTUGAL": "🇵🇹",
    "CZ": "🇨🇿", "CHEQUIA": "🇨🇿", "REPÚBLICA TCHECA": "🇨🇿",
    "HU": "🇭🇺", "HUNGRIA": "🇭🇺", "HUNGARY": "🇭🇺",
    "UA": "🇺🇦", "UCRANIA": "🇺🇦", "UCRÂNIA": "🇺🇦", "UKRAINE": "🇺🇦",
    "NO": "🇳🇴", "NORUEGA": "🇳🇴", "NORWAY": "🇳🇴",
    "DK": "🇩🇰", "DINAMARCA": "🇩🇰", "DENMARK": "🇩🇰",
    "BE": "🇧🇪", "BÉLGICA": "🇧🇪", "BELGICA": "🇧🇪", "BELGIUM": "🇧🇪",
    "CH": "🇨🇭", "SUÍÇA": "🇨🇭", "SUICA": "🇨🇭", "SWITZERLAND": "🇨🇭",
    "AT": "🇦🇹", "ÁUSTRIA": "🇦🇹", "AUSTRIA": "🇦🇹",
    "NZ": "🇳🇿", "NOVA ZELÂNDIA": "🇳🇿", "NEW ZEALAND": "🇳🇿",
    "ZA": "🇿🇦", "ÁFRICA DO SUL": "🇿🇦", "SOUTH AFRICA": "🇿🇦",
    "IN": "🇮🇳", "ÍNDIA": "🇮🇳", "INDIA": "🇮🇳",
    "SG": "🇸🇬", "SINGAPURA": "🇸🇬", "SINGAPORE": "🇸🇬",
    "TW": "🇹🇼", "TAIWAN": "🇹🇼",
    "IL": "🇮🇱", "ISRAEL": "🇮🇱",
    "TR": "🇹🇷", "TURQUIA": "🇹🇷", "TURKEY": "🇹🇷",
    "CL": "🇨🇱", "CHILE": "🇨🇱",
    "CO": "🇨🇴", "COLÔMBIA": "🇨🇴", "COLOMBIA": "🇨🇴",
    "RO": "🇷🇴", "ROMÊNIA": "🇷🇴", "ROMANIA": "🇷🇴",
    "GR": "🇬🇷", "GRÉCIA": "🇬🇷", "GREECE": "🇬🇷",
    "SK": "🇸🇰", "ESLOVÁQUIA": "🇸🇰", "SLOVAKIA": "🇸🇰",
}

def pais_com_emoji(nome):
    chave = nome.upper().strip()
    emoji = COUNTRY_EMOJI.get(chave, "")
    if emoji:
        return f"{emoji} {nome}"
    return nome


# ── CSS compartilhado ─────────────────────────────────────
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

/* ── HOME BUTTON (páginas de gráfico) ── */
.home-btn {
    position: fixed;
    top: 16px; left: 16px;
    z-index: 100;
    width: 40px; height: 40px;
    background: #111;
    border: none;
    border-radius: 10px;
    color: #e8e0d8;
    font-size: 18px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    text-decoration: none;
    position: fixed;
}
.home-btn::before {
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
    border-radius: 10px;
}
.home-btn::after {
    content: '';
    z-index: -1;
    position: absolute;
    width: 100%; height: 100%;
    background: #111;
    left: 0; top: 0;
    border-radius: 10px;
}
.home-btn:hover::before { opacity: 1; }

/* ── PAGE HEADER ── */
.page-header {
    text-align: center;
    padding: 52px 24px 16px;
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

/* ── CHART LAYOUT ── */
.chart-outer {
    max-width: 1000px;
    margin: 24px auto;
    padding: 0 20px 60px;
}

.card {
    background: #1a1616;
    border: 1px solid #2e2828;
    border-radius: 16px;
    padding: 32px 28px;
    position: relative;
    display: flex;
    gap: 36px;
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

/* gráfico — dobro do tamanho anterior (560px) */
.chart-col {
    flex-shrink: 0;
    width: 560px;
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
    font-size: 36px;
    font-weight: 700;
    color: #fff;
    line-height: 1;
}
.chart-center-label .total-label {
    font-size: 12px;
    color: #5a5050;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 5px;
}

/* legenda — scroll independente, altura fixa */
.legend-col {
    flex: 1;
    min-width: 0;
    max-height: 560px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 7px;
    padding-right: 4px;
    align-self: stretch;
}

.legend-col::-webkit-scrollbar { width: 4px; }
.legend-col::-webkit-scrollbar-track { background: transparent; }
.legend-col::-webkit-scrollbar-thumb { background: #2e2828; border-radius: 4px; }

.legend-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 13px;
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
    width: 11px; height: 11px;
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
    margin-bottom: 52px;
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
    font-size: clamp(28px, 5vw, 54px);
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
    margin-top: 14px;
}
.greeting .count-line strong { color: #8a7f7f; }

.index-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    width: 100%;
    max-width: 540px;
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
    font-size: 16px;
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

/* ── MOBILE ── */
@media (max-width: 700px) {
    .card {
        flex-direction: column;
        align-items: stretch;
        gap: 24px;
        padding: 20px 16px;
    }

    .chart-col {
        width: 100%;
    }

    /* legenda em baixo, altura fixa com scroll */
    .legend-col {
        max-height: 260px;
        overflow-y: auto;
    }

    .page-header h1 { font-size: 26px; }

    .index-grid { max-width: 100%; }
    .index-btn  { height: 76px; font-size: 14px; }
}
"""


# ── Botão home (para páginas de gráfico) ─────────────────
HOME_BTN = '<a href="index.html" class="home-btn" title="Home">🏠</a>'


# ── Gerar página de gráfico ───────────────────────────────
def build_chart_page(title, subtitle, counts_dict, center_label="tipos", show_center=True):
    agora  = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    labels = list(counts_dict.keys())
    counts = list(counts_dict.values())
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]
    total  = sum(counts)
    unique = len(labels)

    labels_json = json.dumps(labels, ensure_ascii=False)
    counts_json = json.dumps(counts)
    colors_json = json.dumps(colors)

    center_html = ""
    if show_center:
        center_html = f"""
      <div class="chart-center-label">
        <div class="total">{unique}</div>
        <div class="total-label">{center_label}</div>
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

{HOME_BTN}

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
      hoverOffset: 10,
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

<div class="index-wrap">

  <div class="greeting">
    <p class="time-msg">// game.db</p>
    <h1>{saudacao}, <span>Eduardo!</span></h1>
    <p class="count-line">você já finalizou um total de <strong>{total_jogos} jogos</strong></p>
  </div>

  <div class="index-grid">
    <a href="franquias.html" class="index-btn"><span class="icon">🎮</span> Franquias</a>
    <a href="paises.html"    class="index-btn"><span class="icon">🌍</span> Países</a>
    <a href="consoles.html"  class="index-btn"><span class="icon">🕹️</span> Consoles</a>
    <a href="nei.html"       class="index-btn"><span class="icon">📊</span> Experiência</a>
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
    paises_raw = to_counts(df_jogos["Pais"])
    # aplica emoji nos países
    paises = {pais_com_emoji(k): v for k, v in paises_raw.items()}
    nei      = to_counts(df_jogos["NEI"])
    consoles = to_counts(df_consoles["Console"])
    total    = len(df_jogos)

    with open("franquias.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Franquias", f"{total} jogos no acervo",
            franquias, center_label="franquias", show_center=True
        ))

    with open("paises.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Países", "origem dos jogos",
            paises, center_label="países", show_center=True
        ))

    with open("consoles.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Consoles", "plataformas do acervo",
            consoles, center_label="consoles", show_center=True
        ))

    with open("nei.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Experiência", "nível de interesse (NEI)",
            nei, show_center=False
        ))

    gerar_index(total)
    print("Páginas geradas com sucesso.")
