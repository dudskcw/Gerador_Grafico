import os
import requests
import pandas as pd
import plotly.express as px

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_notion_data():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    data = response.json()
    
    if "results" not in data or not data["results"]:
        return pd.DataFrame(), pd.DataFrame()

    rows_jogos = []
    rows_consoles = []
    
    for result in data["results"]:
        props = result["properties"]
        
        # Função para buscar coluna ignorando se tem acento ou não em "Pais"
        def get_val(names):
            for name in names:
                if name in props and props[name]["select"]:
                    return props[name]["select"]["name"]
            return "Não definido"

        franquia = get_val(["Franquia"])
        # Tenta buscar "Paises" ou "País" ou "Pais"
        pais = get_val(["Paises", "País", "Pais"])
        nei = get_val(["NEI"])
        
        rows_jogos.append({"Franquia": franquia, "Paises": pais, "NEI": nei})
        
        if "Console" in props and props["Console"]["multi_select"]:
            for c in props["Console"]["multi_select"]:
                rows_consoles.append({"Console": c["name"]})

    return pd.DataFrame(rows_jogos), pd.DataFrame(rows_consoles)

df_j, df_c = fetch_notion_data()

if not df_j.empty:
    # Cores personalizadas para o dashboard
    color_theme = px.colors.qualitative.Pastel
    
    f1 = px.pie(df_j, names='Franquia', hole=0.4, title="<b>Distribuição por Franquia</b>", color_discrete_sequence=color_theme)
    f2 = px.pie(df_j, names='Paises', hole=0.4, title="<b>Origem dos Jogos (Paises)</b>", color_discrete_sequence=color_theme)
    f3 = px.pie(df_c, names='Console', hole=0.4, title="<b>Plataformas Utilizadas</b>", color_discrete_sequence=color_theme)
    f4 = px.pie(df_j, names='NEI', hole=0.4, title="<b>Nível de Estresse (NEI)</b>", color_discrete_sequence=color_theme)

    for fig in [f1, f2, f3, f4]:
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(margin=dict(t=50, b=20, l=10, r=10), showlegend=False)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<html><head><title>Dashboard Games</title>")
        f.write("<style>body{display:grid; grid-template-columns:1fr 1fr; gap:20px; padding:20px; background:#f4f4f9; font-family:sans-serif;} .chart-container{background:white; border-radius:10px; padding:10px; shadow: 0 4px 6px rgba(0,0,0,0.1);}</style></head><body>")
        for fig in [f1, f2, f3, f4]:
            f.write("<div class='chart-container'>" + fig.to_html(full_html=False, include_plotlyjs='cdn') + "</div>")
        f.write("</body></html>")
else:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<html><body><h1 style='text-align:center; margin-top:50px;'>Aguardando conexão com o Notion...</h1><p style='text-align:center;'>Certifique-se de que a conexão 'Link_Games' foi adicionada à página.</p></body></html>")
