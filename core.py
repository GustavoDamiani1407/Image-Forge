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

def converter_imagens(pasta, log_func=lambda msg: None, progress_callback=lambda val: None,
                      formato_saida=".jpg", tr=lambda x: x):
    log_func(tr("=== Iniciando conversão para {formato} ===\n").format(formato=formato_saida))
    extensoes_convertiveis = [".jpg", ".jpeg", ".png", ".webp", ".jpg_large"]
    arquivos_alvo = []

    for raiz, _, arquivos in os.walk(pasta):
        for nome in arquivos:
            ext = os.path.splitext(nome)[1].lower()
            if ext in extensoes_convertiveis and ext != formato_saida:
                arquivos_alvo.append(os.path.join(raiz, nome))

    total = len(arquivos_alvo)
    if total == 0:
        log_func(tr("Nenhuma imagem para converter.\n"))
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
            }.get(formato_saida.lower(), formato_saida.replace(".", "").upper())

            img.save(novo_caminho, formato_pillow)
            os.remove(caminho)
            log_func(tr("{arquivo} convertido para {novo}\n").format(
                arquivo=os.path.relpath(caminho), novo=novo_nome))
        except Exception as e:
            log_func(tr("Erro ao converter {arquivo}: {erro}\n").format(
                arquivo=nome_original, erro=str(e)))

        progresso_parcial = (i / total) * 25
        progress_callback(progresso_parcial)

    METRICAS["convertidas"] += total

def extrair_numero(nome):
    numeros = re.findall(r'\d+', nome)
    return int(numeros[0]) if numeros else float('inf')

def remover_duplicatas(pasta, log_func=lambda msg: None, tr=lambda x: x):
    METRICAS["duplicatas"] = 0
    log_func(tr("=== Iniciando remoção de duplicatas ===\n"))
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
                log_func(tr("Duplicata encontrada: {dup} (original: {orig})\n").format(
                    dup=os.path.relpath(caminho), orig=original))
                os.remove(caminho)
                METRICAS["duplicatas"] += 1
            else:
                hash_dict[hashfile] = os.path.relpath(caminho)

def renomear_temp(pasta, log_func=lambda msg: None, tr=lambda x: x):
    METRICAS["temp_renomeados"] = 0
    log_func(tr("=== Realinhando arquivos TEMP ===\n"))
    for raiz, _, arquivos in os.walk(pasta):
        for nome in arquivos:
            if nome.startswith("TEMP"):
                novo_nome = nome.replace("TEMP", "")
                origem = os.path.join(raiz, nome)
                destino = os.path.join(raiz, novo_nome)
                try:
                    os.rename(origem, destino)
                    log_func(tr("Renomeado: {origem} → {destino}\n").format(
                        origem=os.path.relpath(origem), destino=os.path.relpath(destino)))
                    METRICAS["temp_renomeados"] += 1
                except Exception as e:
                    log_func(tr("Erro ao renomear {nome}: {erro}\n").format(
                        nome=nome, erro=str(e)))

def realinhar_sequencia(pasta, log_func=lambda msg: None, formato_saida=".jpg",
                       prefixo_img='i', prefixo_gif='g', unificar=False, tr=lambda x: x):
    log_func(tr("=== Realinhamento Inteligente Iniciado ===\n"))

    for raiz, _, arquivos in os.walk(pasta):
        imagens = [os.path.join(raiz, f) for f in arquivos if f.lower().endswith(formato_saida)]
        gifs = [os.path.join(raiz, f) for f in arquivos if f.lower().endswith(".gif")]

        if unificar:
            todos = imagens + gifs
            if todos:
                log_func(tr("[{dsip}/{dsgp} UNIFICADO] Subpasta: {pasta} - {qtde} arquivos\n").format(
                    dsip=tr("DSIP"), dsgp=tr("DSGP"),
                    pasta=os.path.relpath(raiz), qtde=len(todos)))
                processar_padrao(todos, raiz, prefixo_img or 'i', formato_saida, log_func, tr)
        else:
            if imagens:
                log_func(tr("[{dsip}] Subpasta: {pasta} - {qtde} arquivos\n").format(
                    dsip=tr("DSIP"), pasta=os.path.relpath(raiz), qtde=len(imagens)))
                processar_padrao(imagens, raiz, prefixo_img or 'i', formato_saida, log_func, tr)
            if gifs:
                log_func(tr("[{dsgp}] Subpasta: {pasta} - {qtde} arquivos\n").format(
                    dsgp=tr("DSGP"), pasta=os.path.relpath(raiz), qtde=len(gifs)))
                processar_padrao(gifs, raiz, prefixo_gif or 'g', '.gif', log_func, tr)

    log_func(tr("=== Realinhamento Inteligente Concluído ===\n"))

def processar_padrao(lista, raiz, prefixo, extensao, log_func, tr):
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
    gaps = []
    if indices_existentes:
        inicio = min(indices_existentes)
        fim = max(indices_existentes)
        gaps = [i for i in range(inicio, fim + 1) if i not in numerados]

    renomeios = []
    for i in gaps:
        destino = os.path.join(raiz, f"{prefixo}{i}{extensao}")
        if aleatorios:
            origem = aleatorios.pop(0)
            log_func(tr("[REALINHAMENTO] Gap {idx} preenchido com aleatório: {arquivo}\n").format(
                idx=i, arquivo=os.path.basename(origem)))
        else:
            maiores = sorted(numerados.items(), reverse=True)
            origem = None
            for idx, caminho in maiores:
                if idx not in gaps:
                    origem = numerados.pop(idx)
                    log_func(tr("[REALINHAMENTO] Gap {idx} preenchido com contra marcha: {arquivo}\n").format(
                        idx=i, arquivo=os.path.basename(origem)))
                    break
            if not origem:
                continue
        renomeios.append((origem, destino))
        METRICAS["realinhadas"] += 1
        numerados[i] = destino

    for idx, origem in numerados.items():
        destino = os.path.join(raiz, f"{prefixo}{idx}{extensao}")
        if os.path.basename(origem) != os.path.basename(destino):
            renomeios.append((origem, destino))
            log_func(tr("[RENOMEIO] Corrigido: {origem} → {destino}\n").format(
                origem=os.path.basename(origem), destino=os.path.basename(destino)))

    proximo_idx = max(numerados.keys()) + 1 if indices_existentes else 1
    for resto in aleatorios:
        while True:
            destino = os.path.join(raiz, f"{prefixo}{proximo_idx}{extensao}")
            if not os.path.exists(destino):
                renomeios.append((resto, destino))
                log_func(tr("[EXTENSÃO] Aleatório adicionado ao final: {arquivo}\n").format(
                    arquivo=os.path.basename(resto)))
                METRICAS["realinhadas"] += 1
                break
            proximo_idx += 1
        # Removido incremento extra aqui para evitar pular números
        # proximo_idx += 1

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
        log_func(tr("[PADRONIZAÇÃO] {origem} → {destino}\n").format(
            origem=os.path.basename(temp[:-5]), destino=os.path.basename(destino)))

def executar_pipeline_completo(pasta, log_func=lambda msg: None, progress_callback=lambda v: None,
                               formato_saida=".jpg", prefixo_imagem="i", prefixo_gif="g", unificar=False,
                               tr=lambda x: x):
    for k in METRICAS:
        METRICAS[k] = 0

    log_func(tr("=== Iniciando o Procedimento Image Forge ===\n"))
    converter_imagens(pasta, log_func, progress_callback, formato_saida, tr)
    progress_callback(25)
    remover_duplicatas(pasta, log_func, tr)
    progress_callback(50)
    renomear_temp(pasta, log_func, tr)
    progress_callback(75)
    realinhar_sequencia(pasta, log_func, formato_saida, prefixo_imagem, prefixo_gif, unificar, tr)
    progress_callback(100)

    log_func(tr("\n=== Procedimento Concluído ===\n"))
    log_func(tr("=== Métricas Gerais ===\n"))
    for chave, valor in METRICAS.items():
        log_func(tr("{chave}: {valor}\n").format(chave=chave.capitalize(), valor=valor))
