"""
Comunicação com a API do Notion e extração/normalização dos dados
da base de jogos.
"""

import os
import requests
import pandas as pd

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")

if not NOTION_TOKEN or not DATABASE_ID:
    raise ValueError("NOTION_TOKEN ou DATABASE_ID não configurados.")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def get_value(props, nome):
    """Busca o valor de uma propriedade do Notion pelo nome (tolerante a acentos)."""
    for key in props:
        key_norm = key.lower().replace("í", "i").replace("é", "e")
        nome_norm = nome.lower().replace("í", "i").replace("é", "e")
        if key_norm == nome_norm:
            try:
                prop = props[key]
                if prop["type"] == "select":
                    return prop["select"]["name"] if prop["select"] else "Não definido"
                elif prop["type"] == "multi_select":
                    vals = [x["name"] for x in prop["multi_select"]]
                    return ", ".join(vals) if vals else "Não definido"
                elif prop["type"] == "title":
                    return prop["title"][0]["plain_text"] if prop["title"] else "Sem título"
                elif prop["type"] == "rich_text":
                    return prop["rich_text"][0]["plain_text"] if prop["rich_text"] else "Não definido"
            except Exception:
                return "Não definido"
    return "Não definido"


def carregar_dados_notion():
    """Pagina por toda a base do Notion e devolve (df_jogos, df_consoles, erro)."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    all_results = []
    has_more = True
    next_cursor = None

    while has_more:
        payload = {}
        if next_cursor:
            payload["start_cursor"] = next_cursor
        response = requests.post(url, headers=HEADERS, json=payload)
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
            "NEI": get_value(props, "NEI"),
        })
        try:
            for c in props["Console"]["multi_select"]:
                consoles.append(c["name"])
        except Exception:
            pass

    return pd.DataFrame(jogos), pd.DataFrame(consoles, columns=["Console"]), None


def explodir_multivalor(series, separador=", "):
    """
    Transforma 'Brasil, Japão' em duas linhas separadas.
    Funciona para países, franquias e qualquer campo que possa
    ter múltiplos valores separados por vírgula.
    """
    return series.str.split(separador).explode().str.strip()


def to_counts_exploded(series):
    """
    Explode valores multivalorados, conta ocorrências e retorna
    dict {label: count} ordenado do mais frequente para o menos frequente.
    """
    exploded = explodir_multivalor(series)
    counts = exploded.value_counts()
    return {k: int(v) for k, v in counts.items()}
