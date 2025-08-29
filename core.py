import os
import re
import hashlib
from PIL import Image

METRICAS = {
    "convertidas": 0,
    "duplicatas": 0,
    "temp_renomeados": 0,
    "realinhadas": 0
}

def converter_imagens(pasta, log_func=lambda msg: None, progress_callback=lambda val: None, formato_saida=".jpg"):
    log_func(f"Iniciando conversão para {formato_saida}\n")
    extensoes_convertiveis = [".jpg", ".jpeg", ".png", ".webp", ".jpg_large"]
    arquivos_alvo = []

    for raiz, _, arquivos in os.walk(pasta):
        for nome in arquivos:
            ext = os.path.splitext(nome)[1].lower()
            if ext in extensoes_convertiveis and ext != formato_saida:
                arquivos_alvo.append(os.path.join(raiz, nome))

    total = len(arquivos_alvo)
    if total == 0:
        log_func("Nenhuma imagem para converter.\n")
        return

    for i, caminho in enumerate(arquivos_alvo, 1):
        nome_original = os.path.basename(caminho)
        novo_nome = os.path.splitext(nome_original)[0] + formato_saida
        novo_caminho = os.path.join(os.path.dirname(caminho), novo_nome)

        try:
            img = Image.open(caminho)
            img.verify()
            img = Image.open(caminho).convert("RGB")

            formato_pillow = {
                ".jpg": "JPEG",
                ".jpeg": "JPEG",
                ".png": "PNG",
                ".webp": "WEBP"
            }.get(formato_saida.lower(), "JPEG")

            img.save(novo_caminho, formato_pillow)
            os.remove(caminho)
            log_func(f"{os.path.relpath(caminho)} convertido para {novo_nome}\n")
        except Exception as e:
            log_func(f"Erro ao converter {nome_original}: {e}\n")

        progresso_parcial = (i / total) * 25
        progress_callback(progresso_parcial)

    from core import METRICAS
    METRICAS["convertidas"] += total

def extrair_numero(nome):
    numeros = re.findall(r'\d+', nome)
    return int(numeros[0]) if numeros else float('inf')

def remover_duplicatas(pasta, log_func=lambda msg: None):
    METRICAS["duplicatas"] = 0
    log_func("Iniciando remoção de duplicatas\n")
    hash_dict = {}

    for raiz, _, arquivos in os.walk(pasta):
        arquivos_filtrados = [f for f in arquivos if f.lower().endswith((".jpg", ".gif"))]
        arquivos_filtrados.sort(key=extrair_numero)

        for nome in arquivos_filtrados:
            caminho = os.path.join(raiz, nome)
            with open(caminho, "rb") as f:
                hashfile = hashlib.md5(f.read()).hexdigest()

            if hashfile in hash_dict:
                original = hash_dict[hashfile]
                log_func(f"Duplicata encontrada: {os.path.relpath(caminho)} (original: {original})\n")
                os.remove(caminho)
                METRICAS["duplicatas"] += 1
            else:
                hash_dict[hashfile] = os.path.relpath(caminho)

def renomear_temp(pasta, log_func=lambda msg: None):
    METRICAS["temp_renomeados"] = 0
    log_func("Realinhando arquivos TEMP\n")
    for raiz, _, arquivos in os.walk(pasta):
        for nome in arquivos:
            if nome.startswith("TEMP"):
                novo_nome = nome.replace("TEMP", "")
                origem = os.path.join(raiz, nome)
                destino = os.path.join(raiz, novo_nome)
                try:
                    os.rename(origem, destino)
                    log_func(f"Renomeado: {os.path.relpath(origem)} → {os.path.relpath(destino)}\n")
                    METRICAS["temp_renomeados"] += 1
                except Exception as e:
                    log_func(f"Erro ao renomear {nome}: {e}\n")

def realinhar_sequencia(pasta, log_func=lambda msg: None, formato_saida=".jpg", prefixo_img='i', prefixo_gif='g'):
    log_func("=== Realinhamento Inteligente Iniciado ===\n")

    for raiz, _, arquivos in os.walk(pasta):
        imagens = [os.path.join(raiz, f) for f in arquivos if f.lower().endswith(formato_saida)]
        gifs = [os.path.join(raiz, f) for f in arquivos if f.lower().endswith(".gif")]

        # ADICIONADO: Ordena as listas para preservar a ordem ao trocar de prefixo
        imagens.sort(key=lambda path: extrair_numero(os.path.basename(path)))
        gifs.sort(key=lambda path: extrair_numero(os.path.basename(path)))

        if imagens:
            log_func(f"[DSIP] Subpasta: {os.path.relpath(raiz)} - {len(imagens)} arquivos\n")
            processar_padrao_ciclico(imagens, raiz, prefixo_img, formato_saida, log_func)
        if gifs:
            log_func(f"[DSGP] Subpasta: {os.path.relpath(raiz)} - {len(gifs)} arquivos\n")
            processar_padrao_ciclico(gifs, raiz, prefixo_gif, '.gif', log_func)

    log_func("=== Realinhamento Inteligente Concluído ===\n")

def processar_padrao_ciclico(lista, raiz, prefixo, extensao, log_func):
    extensao = extensao.lower()

    def separar_arquivos(arquivos):
        numerados = {}
        aleatorios = []
        for caminho in arquivos:
            nome = os.path.basename(caminho)
            nome_lower = nome.lower()
            match = re.fullmatch(fr"{re.escape(prefixo)}(\d+){re.escape(extensao)}", nome_lower)
            if match:
                numerados[int(match.group(1))] = caminho
            else:
                aleatorios.append(caminho)
        return numerados, aleatorios

    arquivos_atuais = list(lista)
    renomeios = []

    while True:
        numerados, aleatorios = separar_arquivos(arquivos_atuais)
        if not numerados:
            break

        indices = sorted(numerados.keys())
        maior_index = indices[-1]

        gap = None
        for i in range(1, maior_index):
            if i not in numerados:
                gap = i
                break

        if gap is None:
            break

        destino = os.path.join(raiz, f"{prefixo}{gap}{extensao}")
        origem = None

        if aleatorios:
            origem = aleatorios.pop(0)
            log_func(f"[REALINHAMENTO] Gap {gap} preenchido com aleatório: {os.path.basename(origem)}\n")
        else:
            maior_idx = max(numerados.keys())
            if maior_idx != gap:
                origem = numerados.pop(maior_idx)
                log_func(f"[REALINHAMENTO] Gap {gap} preenchido com contra marcha: {os.path.basename(origem)}\n")
            else:
                break

        if origem:
            renomeios.append((origem, destino))
            arquivos_atuais.remove(origem)
            arquivos_atuais.append(destino)
            METRICAS["realinhadas"] += 1

    numerados, _ = separar_arquivos(arquivos_atuais)
    for idx, origem in numerados.items():
        destino = os.path.join(raiz, f"{prefixo}{idx}{extensao}")
        if os.path.basename(origem) != os.path.basename(destino):
            renomeios.append((origem, destino))
            log_func(f"[RENOMEIO] Corrigido: {os.path.basename(origem)} → {os.path.basename(destino)}\n")

    _, aleatorios = separar_arquivos(arquivos_atuais)
    proximo_idx = max(numerados.keys()) if numerados else 0
    for resto in aleatorios:
        while True:
            proximo_idx += 1
            destino = os.path.join(raiz, f"{prefixo}{proximo_idx}{extensao}")
            if not os.path.exists(destino):
                renomeios.append((resto, destino))
                log_func(f"[EXTENSÃO] Aleatório adicionado ao final: {os.path.basename(resto)}\n")
                METRICAS["realinhadas"] += 1
                break

    temp_map = {}
    for origem, destino in renomeios:
        if origem == destino:
            continue
        temp = origem + ".temp"
        while os.path.exists(temp):
            temp += "_"
        os.rename(origem, temp)
        temp_map[temp] = destino

    for temp, destino in temp_map.items():
        os.rename(temp, destino)
        log_func(f"[PADRONIZAÇÃO] {os.path.basename(temp[:-5])} → {os.path.basename(destino)}\n")


def executar_pipeline_completo(pasta, log_func=lambda msg: None, progress_callback=lambda v: None, formato_saida=".jpg", prefixo_img='i', prefixo_gif='g'):
    for k in METRICAS:
        METRICAS[k] = 0

    log_func("=== Iniciando o Procedimento Image Forge ===\n")
    converter_imagens(pasta, log_func=log_func, progress_callback=progress_callback, formato_saida=formato_saida)
    progress_callback(25)
    remover_duplicatas(pasta, log_func)
    progress_callback(50)
    renomear_temp(pasta, log_func)
    progress_callback(75)
    realinhar_sequencia(pasta, log_func, formato_saida, prefixo_img, prefixo_gif)
    progress_callback(100)

    log_func("\n=== Procedimento Concluído ===\n")
    log_func("=== Métricas Gerais ===\n")
    for chave, valor in METRICAS.items():
        log_func(f"{chave.capitalize()}: {valor}\n")