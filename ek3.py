import os
import re

def aplicar_nomenclatura_personalizada(
    pasta,
    log_func=lambda msg: None,
    formato_imagens=".jpg",
    prefixo_img="i",
    prefixo_gif="g",
    unificar=False
):
    log_func("=== Realinhamento Inteligente Iniciado ===\n")

    imagens = []
    gifs = []

    # Coleta de arquivos
    for raiz, _, arquivos in os.walk(pasta):
        for nome in arquivos:
            caminho = os.path.join(raiz, nome)
            ext = os.path.splitext(nome)[1].lower()
            if ext == formato_imagens.lower():
                imagens.append(caminho)
            elif ext == ".gif":
                gifs.append(caminho)

    # Unificação ou não
    if unificar:
        todos = imagens + gifs
        todos.sort(key=lambda x: os.path.getmtime(x))
        aplicar_nomenclatura(todos, pasta, log_func, prefixo_img, formato_imagens, misto=True)
    else:
        imagens.sort(key=lambda x: os.path.getmtime(x))
        gifs.sort(key=lambda x: os.path.getmtime(x))
        aplicar_nomenclatura(imagens, pasta, log_func, prefixo_img, formato_imagens)
        aplicar_nomenclatura(gifs, pasta, log_func, prefixo_gif, ".gif")

    log_func("=== Realinhamento Inteligente Concluído ===\n")


def aplicar_nomenclatura(lista, raiz_base, log_func, prefixo, extensao, misto=False):
    temp_map = {}
    usados = set()
    idx = 1

    for caminho in lista:
        nome_destino = f"{prefixo}{idx}{extensao}"
        destino = os.path.join(os.path.dirname(caminho), nome_destino)

        # Garante que não sobrescreva arquivos existentes
        while os.path.exists(destino) or destino in usados:
            idx += 1
            nome_destino = f"{prefixo}{idx}{extensao}"
            destino = os.path.join(os.path.dirname(caminho), nome_destino)

        if os.path.abspath(caminho) != os.path.abspath(destino):
            temp = caminho + ".temp"
            while os.path.exists(temp):
                temp += "_"
            os.rename(caminho, temp)
            temp_map[temp] = destino
            usados.add(destino)

            if misto:
                log_func(f"[UNIFICADO] {os.path.basename(caminho)} → {nome_destino}\n")
            else:
                log_func(f"[PADRÃO] {os.path.basename(caminho)} → {nome_destino}\n")
        idx += 1

    for temp, destino in temp_map.items():
        os.rename(temp, destino)
