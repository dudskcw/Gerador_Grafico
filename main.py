"""
Fluxo principal: busca os dados no Notion, monta os gráficos e gera
as páginas HTML estáticas do Game.DB.
"""

import datetime

try:
    from zoneinfo import ZoneInfo  # nativo do Python 3.9+, sem dependência externa
    TZ_BR = ZoneInfo("America/Sao_Paulo")
except Exception:
    TZ_BR = None  # fallback improvável, tratado em now_br()

from notion_api import carregar_dados_notion, to_counts_exploded, explodir_multivalor
from paises import resolver_pais, flag_url
from templates import build_chart_page, build_index_page

# ── Paleta genérica (franquias, países, consoles) ──────────
PALETTE = [
    "#ff6b6b", "#ffa94d", "#ffd43b", "#69db7c", "#38d9a9",
    "#4dabf7", "#748ffc", "#da77f2", "#f783ac", "#a9e34b",
    "#63e6be", "#74c0fc", "#e599f7", "#ffa8a8", "#ffe066",
]

# ── Cores fixas do NEI (ordem alfabética A → F) ────────────
NEI_ORDEM = ["A", "B", "C", "D", "F"]
NEI_CORES = {
    "A": "#ffd43b",  # Amarelo — Gratificante
    "B": "#51cf66",  # Verde — Promissor
    "C": "#4dabf7",  # Azul — Satisfeito
    "D": "#9775fa",  # Roxo — Comprometido
    "F": "#ff6b6b",  # Vermelho — Bomba
}
COR_INDEFINIDO = "#5a5050"


def now_br():
    """Horário atual no fuso de Brasília, independente do ambiente de execução."""
    if TZ_BR:
        return datetime.datetime.now(TZ_BR)
    return datetime.datetime.utcnow() - datetime.timedelta(hours=3)


def montar_generico(counts_dict):
    """labels/counts/colors na ordem de frequência (franquias, consoles)."""
    labels = list(counts_dict.keys())
    counts = list(counts_dict.values())
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]
    return labels, counts, colors


def montar_paises(series):
    """labels/counts/colors/flags para a página de Países, com bandeira real."""
    exploded = explodir_multivalor(series)
    counts_raw = exploded.value_counts()

    labels, counts, colors, flags = [], [], [], []
    for i, (nome_raw, qtd) in enumerate(counts_raw.items()):
        nome, iso2 = resolver_pais(nome_raw)
        labels.append(nome)
        counts.append(int(qtd))
        colors.append(PALETTE[i % len(PALETTE)])
        flags.append(flag_url(iso2))
    return labels, counts, colors, flags


def montar_nei(counts_dict):
    """Ordena o NEI alfabeticamente (A, B, C, D, F) e aplica as cores fixas."""
    def posicao(label):
        letra = label.strip()[0].upper() if label.strip() else "~"
        return NEI_ORDEM.index(letra) if letra in NEI_ORDEM else len(NEI_ORDEM)

    labels = sorted(counts_dict.keys(), key=posicao)
    counts = [counts_dict[l] for l in labels]
    colors = [
        NEI_CORES.get(l.strip()[0].upper(), COR_INDEFINIDO) if l.strip() else COR_INDEFINIDO
        for l in labels
    ]
    return labels, counts, colors


def indices_nao_definido(labels):
    """Índices de labels iguais a 'Não definido', para começar ocultos no gráfico."""
    return [i for i, l in enumerate(labels) if l.strip().lower() == "não definido"]


def main():
    df_jogos, df_consoles, err = carregar_dados_notion()
    if err:
        print(f"Erro: {err}")
        return

    agora = now_br().strftime("%d/%m/%Y às %H:%M")
    total = len(df_jogos)

    franquias_dict = to_counts_exploded(df_jogos["Franquia"])
    nei_dict = to_counts_exploded(df_jogos["NEI"])
    consoles_dict = {k: int(v) for k, v in df_consoles["Console"].value_counts().items()}

    fr_labels, fr_counts, fr_colors = montar_generico(franquias_dict)
    co_labels, co_counts, co_colors = montar_generico(consoles_dict)
    pa_labels, pa_counts, pa_colors, pa_flags = montar_paises(df_jogos["Pais"])
    ne_labels, ne_counts, ne_colors = montar_nei(nei_dict)

    with open("franquias.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Franquias", f"{total} jogos no acervo", fr_labels, fr_counts, fr_colors, agora,
            center_label="franquias", show_center=True,
            hidden_indices=indices_nao_definido(fr_labels),
        ))

    with open("paises.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Países", "origem dos jogos", pa_labels, pa_counts, pa_colors, agora,
            flags=pa_flags, center_label="países", show_center=True,
            hidden_indices=indices_nao_definido(pa_labels),
        ))

    with open("consoles.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Consoles", "plataformas do acervo", co_labels, co_counts, co_colors, agora,
            center_label="consoles", show_center=True,
            hidden_indices=indices_nao_definido(co_labels),
        ))

    with open("nei.html", "w", encoding="utf-8") as f:
        f.write(build_chart_page(
            "Experiência", "nível de interesse (NEI)", ne_labels, ne_counts, ne_colors, agora,
            show_center=False,
            hidden_indices=indices_nao_definido(ne_labels),
        ))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_index_page(total))

    print("Páginas geradas com sucesso.")


if __name__ == "__main__":
    main()
