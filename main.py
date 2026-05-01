import os
import requests
import pandas as pd
import plotly.express as px
import datetime

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

if not NOTION_TOKEN or not DATABASE_ID:
    raise ValueError("NOTION_TOKEN ou DATABASE_ID não configurados.")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def get_value(props, nome):
    for key in props:
        key_norm = key.lower().replace("í", "i").replace("é", "e")
        nome_norm = nome.lower().replace("í", "i").replace("é", "e")

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
            return None, f"Erro API: {response.status_code}"

        data = response.json()
        all_results.extend(data.get("results", []))

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    if not all_results:
        return None, "Base vazia"

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

    return pd.DataFrame(jogos), pd.DataFrame(consoles, columns=["Console"])


def criar_grafico(df, coluna, titulo):
    df_count = df[coluna].value_counts().reset_index()
    df_count.columns = [coluna, "count"]

    fig = px.pie(df_count, names=coluna, values="count", hole=0.4, title=titulo)

    fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout(
        autosize=True,
        height=400,
        paper_bgcolor="#1c1c1c",
        font_color="white",
        margin=dict(t=40, b=10, l=10, r=10)
    )

    return fig


def criar_grafico_console(df):
    df_count = df.value_counts().reset_index(name="count")

    fig = px.pie(df_count, names="Console", values="count", hole=0.4, title="Consoles")

    fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout(
        autosize=True,
        height=400,
        paper_bgcolor="#1c1c1c",
        font_color="white",
        margin=dict(t=40, b=10, l=10, r=10)
    )

    return fig


def gerar_pagina(fig, arquivo, titulo):
    agora = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")

    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(f"""
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        body {{
            background: #1c1c1c;
            color: white;
            font-family: sans-serif;
            margin: 0;
            padding: 20px;
        }}

        .nav a {{
            margin-right: 15px;
            color: #aaa;
            text-decoration: none;
        }}

        .card {{
            background: #252525;
            border-radius: 15px;
            padding: 10px;
            margin-top: 20px;
        }}
        </style>
        </head>

        <body>

        <div class="nav">
            <a href="index.html">Home</a>
            <a href="franquias.html">Franquias</a>
            <a href="paises.html">Países</a>
            <a href="consoles.html">Consoles</a>
            <a href="nei.html">NEI</a>
        </div>

        <div class="card">
        {fig.to_html(full_html=False, include_plotlyjs='cdn')}
        </div>

        <p style="text-align:center; color:#aaa;">
        Atualizado em {agora}
        </p>

        </body>
        </html>
        """)


def gerar_index():
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("""
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #000;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 28px;
        }

        .glow-on-hover {
            width: 200px;
            height: 70px;
            border: none;
            outline: none;
            color: #fff;
            background: #111;
            cursor: pointer;
            position: relative;
            z-index: 0;
            border-radius: 10px;
            font-size: 15px;
            font-family: sans-serif;
            letter-spacing: 0.5px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 6px;
            text-decoration: none;
        }

        .glow-on-hover .icon {
            font-size: 22px;
        }

        .glow-on-hover:before {
            content: '';
            background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
            position: absolute;
            top: -2px;
            left: -2px;
            background-size: 400%;
            z-index: -1;
            filter: blur(5px);
            width: calc(100% + 4px);
            height: calc(100% + 4px);
            animation: glowing 20s linear infinite;
            opacity: 0;
            transition: opacity .3s ease-in-out;
            border-radius: 10px;
        }

        .glow-on-hover:active {
            color: #000;
        }

        .glow-on-hover:active:after {
            background: transparent;
        }

        .glow-on-hover:hover:before {
            opacity: 1;
        }

        .glow-on-hover:after {
            z-index: -1;
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            background: #111;
            left: 0;
            top: 0;
            border-radius: 10px;
        }

        @keyframes glowing {
            0%   { background-position: 0 0; }
            50%  { background-position: 400% 0; }
            100% { background-position: 0 0; }
        }
        </style>
        </head>

        <body>

        <div class="grid">
            <a href="franquias.html" class="glow-on-hover">
                <span class="icon">🎮</span>
                Franquias
            </a>

            <a href="paises.html" class="glow-on-hover">
                <span class="icon">🌍</span>
                Países
            </a>

            <a href="consoles.html" class="glow-on-hover">
                <span class="icon">🕹️</span>
                Consoles
            </a>

            <a href="nei.html" class="glow-on-hover">
                <span class="icon">📊</span>
                Experiência
            </a>
        </div>

        </body>
        </html>
        """)

# EXECUÇÃO
df_jogos, df_consoles = carregar_dados_notion()

if df_jogos is not None:
    fig1 = criar_grafico(df_jogos, "Franquia", "Franquias")
    fig2 = criar_grafico(df_jogos, "Pais", "Países")
    fig3 = criar_grafico_console(df_consoles)
    fig4 = criar_grafico(df_jogos, "NEI", "Experiência (NEI)")

    gerar_pagina(fig1, "franquias.html", "Franquias")
    gerar_pagina(fig2, "paises.html", "Países")
    gerar_pagina(fig3, "consoles.html", "Consoles")
    gerar_pagina(fig4, "nei.html", "NEI")

    gerar_index()
