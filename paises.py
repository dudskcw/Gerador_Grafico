"""
Dicionário unificado de países: código ISO2, nome em português e apelidos
(siglas/nomes alternativos) para lookup, além da URL da bandeira.

Por que não usar emoji de bandeira (🇧🇷)?
Emojis de bandeira dependem da fonte do sistema operacional. Windows/Chrome
no desktop, em geral, NÃO renderiza esses emojis (mostra "BR" em texto),
enquanto Android e iOS renderizam normalmente — por isso a legenda "sumia"
no computador mas aparecia no celular. A solução robusta é usar uma imagem
real da bandeira (PNG), que renderiza igual em qualquer sistema.
"""

# código ISO2 (minúsculo) -> nome de exibição em português
PAISES = {
    "br": "Brasil",
    "us": "Estados Unidos",
    "jp": "Japão",
    "gb": "Reino Unido",
    "de": "Alemanha",
    "fr": "França",
    "ca": "Canadá",
    "au": "Austrália",
    "kr": "Coreia do Sul",
    "cn": "China",
    "es": "Espanha",
    "it": "Itália",
    "se": "Suécia",
    "fi": "Finlândia",
    "nl": "Holanda",
    "pl": "Polônia",
    "ru": "Rússia",
    "ar": "Argentina",
    "mx": "México",
    "pt": "Portugal",
    "cz": "República Tcheca",
    "hu": "Hungria",
    "ua": "Ucrânia",
    "no": "Noruega",
    "dk": "Dinamarca",
    "be": "Bélgica",
    "ch": "Suíça",
    "at": "Áustria",
    "nz": "Nova Zelândia",
    "za": "África do Sul",
    "in": "Índia",
    "sg": "Singapura",
    "tw": "Taiwan",
    "il": "Israel",
    "tr": "Turquia",
    "cl": "Chile",
    "co": "Colômbia",
    "ro": "Romênia",
    "gr": "Grécia",
    "sk": "Eslováquia",
    "pe": "Peru",
}

# variações (sigla antiga, nome em inglês, sem acento, etc.) -> código ISO2
ALIASES = {
    "brasil": "br", "brazil": "br",
    "usa": "us", "eua": "us", "estados unidos": "us",
    "japao": "jp", "japão": "jp", "japan": "jp",
    "uk": "gb", "reino unido": "gb",
    "alemanha": "de", "germany": "de",
    "franca": "fr", "frança": "fr", "france": "fr",
    "canada": "ca", "canadá": "ca",
    "australia": "au", "austrália": "au",
    "coreia": "kr", "korea": "kr", "coreia do sul": "kr",
    "china": "cn",
    "espanha": "es", "spain": "es",
    "italia": "it", "itália": "it", "italy": "it",
    "suecia": "se", "suécia": "se", "sweden": "se",
    "finlandia": "fi", "finlândia": "fi", "finland": "fi",
    "holanda": "nl", "paises baixos": "nl", "países baixos": "nl", "netherlands": "nl",
    "polonia": "pl", "polônia": "pl", "poland": "pl",
    "russia": "ru", "rússia": "ru",
    "argentina": "ar",
    "mexico": "mx", "méxico": "mx",
    "portugal": "pt",
    "chequia": "cz", "republica tcheca": "cz", "república tcheca": "cz",
    "hungria": "hu", "hungary": "hu",
    "ucrania": "ua", "ucrânia": "ua", "ukraine": "ua",
    "noruega": "no", "norway": "no",
    "dinamarca": "dk", "denmark": "dk",
    "belgica": "be", "bélgica": "be", "belgium": "be",
    "suica": "ch", "suíça": "ch", "switzerland": "ch",
    "austria": "at", "áustria": "at",
    "nova zelandia": "nz", "nova zelândia": "nz", "new zealand": "nz",
    "africa do sul": "za", "áfrica do sul": "za", "south africa": "za",
    "india": "in", "índia": "in",
    "singapura": "sg", "singapore": "sg",
    "taiwan": "tw",
    "israel": "il",
    "turquia": "tr", "turkey": "tr",
    "chile": "cl",
    "colombia": "co", "colômbia": "co",
    "romenia": "ro", "romênia": "ro", "romania": "ro",
    "grecia": "gr", "grécia": "gr", "greece": "gr",
    "eslovaquia": "sk", "eslováquia": "sk", "slovakia": "sk",
    "peru": "pe",
}

FLAG_BASE_URL = "https://flagcdn.com/w40/{code}.png"


def resolver_pais(nome):
    """
    Recebe uma sigla ou nome (em qualquer variação cadastrada) e devolve
    uma tupla (nome_de_exibicao, codigo_iso2_ou_None).
    Se não reconhecer o país, devolve o texto original e None (sem bandeira).
    """
    chave = nome.strip().lower()
    iso2 = chave if chave in PAISES else ALIASES.get(chave)
    nome_exibicao = PAISES.get(iso2, nome.strip())
    return nome_exibicao, iso2


def flag_url(iso2):
    """Devolve a URL da imagem da bandeira para o código ISO2, ou None."""
    return FLAG_BASE_URL.format(code=iso2) if iso2 else None
