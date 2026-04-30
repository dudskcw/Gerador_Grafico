import os
import requests
import pandas as pd
import plotly.express as px

# Configurações de acesso (O GitHub Actions preencherá isso)
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_notion_data():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    all_results = []
    has_more = True
    next_cursor = None
    
    while has_more:
        payload = {"start_cursor": next_cursor} if next_cursor else {}
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        all_results.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    rows_jogos = []
    rows_consoles = []
    
    for result in all_results:
        props = result["properties"]
        
        # 1. Extração de Dados Básicos (1 linha por jogo)
        franquia = props["Franquia"]["select"]["name"] if props.get("Franquia") and props["Franquia"]["select"] else "Outros"
        pais = props["Paises"]["select"]["name"] if props.get("País") and props["País"]["select"] else "Desconhecido"
        nei = props["NEI"]["select"]["name"] if props.get("NEI") and props["NEI"]["select"] else "N/A"
        
        rows_jogos.append({"Franquia": franquia, "País": pais, "NEI": nei})
        
        # 2. O SEGREDO: Separação de Consoles (Multi-select)
        if props.get("Console") and props["Console"]["multi_select"]:
            for c in props["Console"]["multi_select"]:
                rows_consoles.append({"Console": c["name"]})

    return pd.DataFrame(rows_jogos), pd.DataFrame(rows_consoles)

# Execução
df_jogos, df_consoles = fetch_notion_data()

# Criação dos Gráficos (Estilo Rosca/Donut para ficar moderno)
def criar_pizza(df, coluna, titulo):
    fig = px.pie(df, names=coluna, hole=0.4, title=titulo, template="plotly_white")
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False, margin=dict(t=50, b=20, l=20, r=20))
    return fig

fig1 = criar_pizza(df_jogos, 'Franquia', 'Distribuição por Franquia')
fig2 = criar_pizza(df_jogos, 'País', 'Origem dos Desenvolvedores')
fig3 = criar_pizza(df_consoles, 'Console', 'Consoles Mais Utilizados')
fig4 = criar_pizza(df_jogos, 'NEI', 'Nível de Estresse (NEI)')

# Gerar arquivo HTML final
with open("index.html", "w", encoding="utf-8") as f:
    f.write("<html><head><title>Dashboard Gamer</title>")
    f.write("<style>body{background:#f4f4f9; display:grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px; font-family: sans-serif;}</style></head><body>")
    f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write(fig3.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write(fig4.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write("</body></html>")
    