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
    
    if "results" not in data:
        return pd.DataFrame(), pd.DataFrame()

    rows_jogos = []
    rows_consoles = []
    
    for result in data["results"]:
        props = result["properties"]
        
        # Puxa os dados das colunas (Tratando como Select)
        def get_val(name):
            try:
                return props[name]["select"]["name"]
            except:
                return "Não definido"

        franquia = get_val("Franquia")
        pais = get_val("País")
        nei = get_val("NEI")
        
        rows_jogos.append({"Franquia": franquia, "País": pais, "NEI": nei})
        
        # Puxa Consoles (Tratando como Multi-select)
        if "Console" in props and props["Console"]["multi_select"]:
            for c in props["Console"]["multi_select"]:
                rows_consoles.append({"Console": c["name"]})

    return pd.DataFrame(rows_jogos), pd.DataFrame(rows_consoles)

df_j, df_c = fetch_notion_data()

if not df_j.empty:
    # Gráficos
    f1 = px.pie(df_j, names='Franquia', hole=0.4, title="Franquias")
    f2 = px.pie(df_j, names='País', hole=0.4, title="Origem (País)")
    f3 = px.pie(df_c, names='Console', hole=0.4, title="Plataformas")
    f4 = px.pie(df_j, names='NEI', hole=0.4, title="Nível de Estresse")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<html><head><style>body{display:grid; grid-template-columns:1fr 1fr; gap:10px; font-family:sans-serif;}</style></head><body>")
        for fig in [f1, f2, f3, f4]:
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write("</body></html>")
else:
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Erro: Verifique se a integracao 'Games' foi conectada a pagina.</h1></body></html>")
