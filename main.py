import os
import requests
import pandas as pd
import plotly.express as px

# Configurações de acesso vindas do GitHub Secrets
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def carregar_dados_notion():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    
    if response.status_code != 200:
        return pd.DataFrame(), f"Erro API: {response.status_code}"
    
    data = response.json()
    results = data.get("results", [])
    
    if not results:
        return pd.DataFrame(), "Base de dados vazia ou sem permissão."

    jogos_lista = []
    consoles_lista = []

    for item in results:
        props = item["properties"]
        
        # Função interna para ler colunas do tipo 'Select' com segurança
        def extrair_select(nome_coluna):
            # Tenta variações de nome para evitar erros de digitação (ex: Pais vs Paises)
            variacoes = [nome_coluna, nome_coluna.replace("í", "i"), nome_coluna + "es"]
            for v in variacoes:
                if v in props and props[v]["select"]:
                    return props[v]["select"]["name"]
            return "Não definido"

        franquia = extrair_select("Franquia")
        pais = extrair_select("País") # O código tentará "País", "Pais" e "Paises"
        nei = extrair_select("NEI")
        
        jogos_lista.append({
            "Franquia": franquia,
            "Paises": pais,
            "NEI": nei
        })
        
        # Tratamento especial para 'Multi-select' (Console)
        if "Console" in props and props["Console"]["multi_select"]:
            for c in props["Console"]["multi_select"]:
                consoles_lista.append({"Console": c["name"]})

    return pd.DataFrame(jogos_lista), pd.DataFrame(consoles_lista)

# Execução principal
df_jogos, df_consoles = carregar_dados_notion()

if isinstance(df_jogos, pd.DataFrame) and not df_jogos.empty:
    # 1. Gráfico de Franquias
    fig1 = px.pie(df_jogos, names='Franquia', hole=0.4, title="<b>Minhas Franquias</b>")
    
    # 2. Gráfico de Países (usando o nome correto da sua coluna)
    fig2 = px.pie(df_jogos, names='Paises', hole=0.4, title="<b>Origem (Paises)</b>")
    
    # 3. Gráfico de Plataformas
    fig3 = px.pie(df_consoles, names='Console', hole=0.4, title="<b>Consoles/Plataformas</b>")
    
    # 4. Gráfico de Estresse (NEI)
    fig4 = px.pie(df_jogos, names='NEI', hole=0.4, title="<b>Nível de Estresse (NEI)</b>")

    # Estilização básica dos gráficos
    for fig in [fig1, fig2, fig3, fig4]:
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=False, margin=dict(t=40, b=10, l=10, r=10))

    # Geração do HTML
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<html><head><style>")
        f.write("body { font-family: sans-serif; background: #121212; color: white; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px; }")
        f.write(".card { background: #1e1e1e; border-radius: 15px; padding: 10px; border: 1px solid #333; }")
        f.write("</style></head><body>")
        for fig in [fig1, fig2, fig3, fig4]:
            f.write("<div class='card'>" + fig.to_html(full_html=False, include_plotlyjs='cdn') + "</div>")
        f.write("</body></html>")
else:
    # HTML de erro caso algo falhe
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"<html><body style='background:#121212; color:white; text-align:center; padding-top:100px;'>")
        f.write(f"<h1>⚠️ Status: {df_consoles}</h1>")
        f.write(f"<p>Verifique se o Token e o ID estão corretos nos Secrets do GitHub e se a conexão Link_Games foi adicionada à página.</p>")
        f.write("</body></html>")
