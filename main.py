import os
import requests
import pandas as pd
import plotly.express as px

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

if not NOTION_TOKEN or not DATABASE_ID:
    raise ValueError("NOTION_TOKEN ou DATABASE_ID não configurados.")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


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
            return None, f"Erro API: {response.status_code} - {response.text}"

        data = response.json()
        all_results.extend(data.get("results", []))

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    if not all_results:
        return None, "Base vazia ou sem permissão."

    jogos = []
    consoles = []

    for item in all_results:
        props = item.get("properties", {})

        def get_select(nome):
            try:
                return props[nome]["select"]["name"]
            except:
                return "Não definido"

        franquia = get_select("Franquia")
        pais = get_select("País")
        nei = get_select("NEI")

        jogos.append({
            "Franquia": franquia,
            "Pais": pais,
            "NEI": nei
        })

        # multi-select consoles
        try:
            for c in props["Console"]["multi_select"]:
                consoles.append(c["name"])
        except:
            pass

    df_jogos = pd.DataFrame(jogos)
    df_consoles = pd.DataFrame(consoles, columns=["Console"])

    return df_jogos, df_consoles


def gerar_graficos(df_jogos, df_consoles):
    # Agrupamentos corretos
    df_franquia = df_jogos["Franquia"].value_counts().reset_index()
    df_franquia.columns = ["Franquia", "count"]

    df_pais = df_jogos["Pais"].value_counts().reset_index()
    df_pais.columns = ["Pais", "count"]

    df_nei = df_jogos["NEI"].value_counts().reset_index()
    df_nei.columns = ["NEI", "count"]

    df_console = df_consoles.value_counts().reset_index(name="count")

    # Criação dos gráficos
    fig1 = px.pie(df_franquia, names="Franquia", values="count", hole=0.4, title="Franquias")
    fig2 = px.pie(df_pais, names="Pais", values="count", hole=0.4, title="Países")
    fig3 = px.pie(df_console, names="Console", values="count", hole=0.4, title="Consoles")
    fig4 = px.pie(df_nei, names="NEI", values="count", hole=0.4, title="Estresse (NEI)")

    figs = [fig1, fig2, fig3, fig4]

    for fig in figs:
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            showlegend=False,
            margin=dict(t=40, b=10, l=10, r=10),
            paper_bgcolor="#1e1e1e",
            font_color="white"
        )

    return figs


def gerar_html(figs):
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("""
        <html>
        <head>
        <meta charset="utf-8">
        <style>
        body {
            font-family: sans-serif;
            background: #121212;
            color: white;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }
        .card {
            background: #1e1e1e;
            border-radius: 15px;
            padding: 10px;
            border: 1px solid #333;
        }
        </style>
        </head>
        <body>
        """)

        # inclui plotly só uma vez
        f.write("<div class='card'>")
        f.write(figs[0].to_html(full_html=False, include_plotlyjs=True))
        f.write("</div>")

        for fig in figs[1:]:
            f.write("<div class='card'>")
            f.write(fig.to_html(full_html=False, include_plotlyjs=False))
            f.write("</div>")

        f.write("</body></html>")


def gerar_html_erro(msg):
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"""
        <html>
        <body style='background:#121212; color:white; text-align:center; padding-top:100px;'>
        <h1>Erro</h1>
        <p>{msg}</p>
        </body>
        </html>
        """)


# EXECUÇÃO
df_jogos, resultado = carregar_dados_notion()

if isinstance(resultado, str):
    gerar_html_erro(resultado)
else:
    figs = gerar_graficos(df_jogos, resultado)
    gerar_html(figs)
