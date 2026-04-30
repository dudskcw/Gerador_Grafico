import os
import requests
import pandas as pd
import plotly.express as px

# Puxa as chaves que você salvou no GitHub Secrets
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
        
        if "results" not in data:
            print("Erro na API do Notion:", data)
            break
            
        all_results.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor")

    rows_jogos = []
    rows_consoles = []
    
    for result in all_results:
        props = result["properties"]
        
        # Função para extrair texto de forma segura
        def get_select(prop_name):
            try:
                return props[prop_name]["select"]["name"]
            except:
                return "Outros"

        # Coleta dados para os 4 gráficos
        franquia = get_select("Franquia")
        pais = get_select("País")
        nei = get_select("NEI")
        
        rows_jogos.append({"Franquia": franquia, "País": pais, "NEI": nei})
        
        # O Segredo dos Consoles (Multi-select)
        if "Console" in props and props["Console"]["multi_select"]:
            for c in props["Console"]["multi_select"]:
                rows_consoles.append({"Console": c["name"]})
        else:
            rows_consoles.append({"Console": "N/A"})

    return pd.DataFrame(rows_jogos), pd.DataFrame(rows_consoles)

df_jogos, df_consoles = fetch_notion_data()

if not df_jogos.empty:
    # Criando os 4 gráficos de pizza/rosca
    fig1 = px.pie(df_jogos, names='Franquia', hole=0.4, title="Franquias")
    fig2 = px.pie(df_jogos, names='País', hole=0.4, title="Países")
    fig3 = px.pie(df_consoles, names='Console', hole=0.4, title="Consoles")
    fig4 = px.pie(df_jogos, names='NEI', hole=0.4, title="Nível de Estresse (NEI)")

    # Formatação Visual
    for fig in [fig1, fig2, fig3, fig4]:
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=False, margin=dict(t=50, b=20, l=10, r=10))

    # Gera o HTML
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<html><head><style>body{display:grid; grid-template-columns:1fr 1fr; gap:10px; background:#ffffff; font-family:sans-serif;}</style></head><body>")
        f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig3.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig4.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write("</body></html>")
else:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Erro: Verifique se a integracao foi adicionada no Notion.</h1></body></html>")
