import os
import re
import hashlib
from PIL import Image

# ============================
# Variável global de métricas
# ============================
METRICAS = {
    "convertidas": 0,
    "duplicatas": 0,
    "temp_renomeados": 0,
    "realinhadas": 0
}

# ============================
# Conversor de imagens
# ============================
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
            img.save(novo_caminho, formato_saida.replace(".", "").upper())
            os.remove(caminho)
            log_func(f"{os.path.relpath(caminho)} convertido para {novo_nome}\n")
        except Exception as e:
            log_func(f"Erro ao converter {nome_original}: {e}\n")

        progresso_parcial = (i / total) * 25
        progress_callback(progresso_parcial)

    from core import METRICAS
    METRICAS["convertidas"] += total

# ============================
# Remoção de duplicatas
# ============================
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

# ============================
# Renomear arquivos TEMP
# ============================
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

# ============================
# Realinhador DSIP/DSGP
# ============================
def realinhar_sequencia(pasta, log_func=lambda msg: None, formato_saida=".jpg"):
    log_func("=== Realinhamento Inteligente Iniciado ===\n")

    for raiz, _, arquivos in os.walk(pasta):
        imagens = [os.path.join(raiz, f) for f in arquivos if f.lower().endswith(formato_saida)]
        gifs = [os.path.join(raiz, f) for f in arquivos if f.lower().endswith(".gif")]

        if imagens:
            log_func(f"[DSIP] Subpasta: {os.path.relpath(raiz)} - {len(imagens)} arquivos\n")
            processar_padrao(imagens, raiz, 'i', formato_saida, log_func)
        if gifs:
            log_func(f"[DSGP] Subpasta: {os.path.relpath(raiz)} - {len(gifs)} arquivos\n")
            processar_padrao(gifs, raiz, 'g', '.gif', log_func)

    log_func("=== Realinhamento Inteligente Concluído ===\n")

def processar_padrao(lista, raiz, prefixo, extensao, log_func):
    numerados = {}
    aleatorios = []

    for caminho in lista:
        nome = os.path.basename(caminho)
        match = re.fullmatch(fr"{prefixo}(\d+){re.escape(extensao)}", nome, re.IGNORECASE)
        if match:
            numerados[int(match.group(1))] = caminho
        else:
            aleatorios.append(caminho)

    indices_existentes = sorted(numerados.keys())
    maior_index = max(indices_existentes, default=0)
    gaps = [i for i in range(1, maior_index + 1) if i not in numerados]

    renomeios = []

    for i in gaps:
        destino = os.path.join(raiz, f"{prefixo}{i}{extensao}")
        if aleatorios:
            origem = aleatorios.pop(0)
            log_func(f"[REALINHAMENTO] Gap {i} preenchido com aleatório: {os.path.basename(origem)}\n")
        else:
            maiores = sorted(numerados.items(), reverse=True)
            origem = None
            for idx, caminho in maiores:
                if idx not in gaps:
                    origem = numerados.pop(idx)
                    log_func(f"[REALINHAMENTO] Gap {i} preenchido com contra marcha: {os.path.basename(origem)}\n")
                    break
            if not origem:
                continue

        renomeios.append((origem, destino))
        METRICAS["realinhadas"] += 1

    for idx, origem in numerados.items():
        destino = os.path.join(raiz, f"{prefixo}{idx}{extensao}")
        if os.path.basename(origem) != os.path.basename(destino):
            renomeios.append((origem, destino))
            log_func(f"[RENOMEIO] Corrigido: {os.path.basename(origem)} → {os.path.basename(destino)}\n")

    proximo_idx = maior_index + 1
    for resto in aleatorios:
        while True:
            destino = os.path.join(raiz, f"{prefixo}{proximo_idx}{extensao}")
            if not os.path.exists(destino):
                renomeios.append((resto, destino))
                log_func(f"[EXTENSÃO] Aleatório adicionado ao final: {os.path.basename(resto)}\n")
                METRICAS["realinhadas"] += 1
                break
            proximo_idx += 1
        proximo_idx += 1

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

# ============================
# Executor geral
# ============================
def executar_pipeline_completo(pasta, log_func=lambda msg: None, progress_callback=lambda v: None, formato_saida=".jpg"):
    for k in METRICAS:
        METRICAS[k] = 0

    log_func("=== Iniciando o Procedimento Image Forge ===\n")
    converter_imagens(pasta,log_func=log_func,progress_callback=progress_callback,formato_saida=formato_saida)
    progress_callback(25)
    remover_duplicatas(pasta, log_func)
    progress_callback(50)
    renomear_temp(pasta, log_func)
    progress_callback(75)
    realinhar_sequencia(pasta, log_func, formato_saida)
    progress_callback(100)

    log_func("\n=== Procedimento Concluído ===\n")
    log_func("=== Métricas Gerais ===\n")
    for chave, valor in METRICAS.items():
        log_func(f"{chave.capitalize()}: {valor}\n")
