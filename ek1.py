import os
from PIL import Image, ImageEnhance, ImageSequence

def aprimorar_jpeg(caminho, log_func, tr):
    try:
        with Image.open(caminho) as img:
            img = img.convert("RGB")
            img = ImageEnhance.Sharpness(img).enhance(1.5)
            img = ImageEnhance.Contrast(img).enhance(1.2)
            img = ImageEnhance.Brightness(img).enhance(1.05)
            img.save(caminho)
            log_func(tr("[EK1] Aprimorado: {arquivo}\n").format(arquivo=os.path.relpath(caminho)))
    except Exception as e:
        log_func(tr("[EK1] Erro ao aprimorar {arquivo}: {erro}\n").format(arquivo=os.path.basename(caminho), erro=e))

def aprimorar_gif(caminho, log_func, tr):
    try:
        with Image.open(caminho) as img:
            frames = []

            for frame in ImageSequence.Iterator(img):
                frame = frame.convert("RGB")
                frame = ImageEnhance.Sharpness(frame).enhance(1.5)
                frame = ImageEnhance.Contrast(frame).enhance(1.2)
                frame = ImageEnhance.Brightness(frame).enhance(1.05)
                frames.append(frame)

            # Salvar com loop infinito
            frames[0].save(
                caminho,
                save_all=True,
                append_images=frames[1:],
                loop=0,
                duration=img.info.get("duration", 100),
                disposal=2
            )
            log_func(tr("[EK1] GIF aprimorado: {arquivo}\n").format(arquivo=os.path.relpath(caminho)))

    except Exception as e:
        log_func(tr("[EK1] Erro ao aprimorar GIF {arquivo}: {erro}\n").format(arquivo=os.path.basename(caminho), erro=e))

def executar_ek1(pasta, log_func=lambda msg: None, progress_callback=lambda v: None, tr=lambda x: x):
    log_func(tr("=== Executando EK1 - Aprimoramento de Imagens ===\n"))

    arquivos = []
    for raiz, _, nomes in os.walk(pasta):
        for nome in nomes:
            if nome.lower().endswith((".jpg", ".jpeg", ".gif")):
                arquivos.append(os.path.join(raiz, nome))

    total = len(arquivos)
    if total == 0:
        log_func(tr("Nenhuma imagem .jpg, .jpeg ou .gif encontrada.\n"))
        progress_callback(100)
        return

    for i, caminho in enumerate(arquivos, 1):
        if caminho.lower().endswith((".jpg", ".jpeg")):
            aprimorar_jpeg(caminho, log_func, tr)
        elif caminho.lower().endswith(".gif"):
            aprimorar_gif(caminho, log_func, tr)

        progresso = (i / total) * 100
        progress_callback(progresso)

    log_func(tr("=== EK1 Concluído ===\n"))
    progress_callback(100)
