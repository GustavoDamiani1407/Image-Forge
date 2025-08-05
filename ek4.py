import os
import json

_lingua_atual = "pt_BR"
_traducoes = {}

def _log(msg):
    # Aqui você pode substituir por logging se quiser mais tarde
    print(f"[ek4] {msg}")

def carregar_traducoes():
    global _traducoes
    lang_dir = os.path.join(os.path.dirname(__file__), "lang")
    caminho = os.path.join(lang_dir, f"{_lingua_atual}.json")

    if not os.path.isfile(caminho):
        _log(f"Arquivo de idioma '{_lingua_atual}.json' não encontrado. Tentando fallback para 'en_US.json'.")
        fallback = "en_US"
        caminho = os.path.join(lang_dir, f"{fallback}.json")
        if not os.path.isfile(caminho):
            _log(f"Arquivo fallback '{fallback}.json' também não encontrado. Usando traduções vazias.")
            _traducoes.clear()
            return

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            _traducoes.clear()
            _traducoes.update(json.load(f))
        _log(f"Traduções carregadas para '{_lingua_atual}'")
    except Exception as e:
        _log(f"Erro ao carregar arquivo de idioma '{_lingua_atual}.json': {e}")
        _traducoes.clear()

def set_lingua(codigo):
    global _lingua_atual
    if codigo != _lingua_atual:
        _lingua_atual = codigo
        carregar_traducoes()

def get_lingua():
    return _lingua_atual

def tr(chave, **kwargs):
    """
    Retorna a tradução da chave, formatando com kwargs se houver.
    Exemplo: tr("Idioma alterado para {idioma}", idioma="Português")
    Se não encontrar a chave, retorna a própria chave formatada.
    """
    texto = _traducoes.get(chave, chave)
    try:
        return texto.format(**kwargs)
    except Exception:
        # Caso haja erro na formatação, retorna o texto cru
        return texto

# Carrega traduções padrão ao iniciar o módulo
carregar_traducoes()
