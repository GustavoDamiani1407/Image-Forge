import os
from PIL import Image, ImageEnhance, ImageSequence

def aprimorar_jpeg(caminho, log_func):
    try:
        with Image.open(caminho) as img:
            img = img.convert("RGB")
            img = ImageEnhance.Sharpness(img).enhance(1.5)
            img = ImageEnhance.Contrast(img).enhance(1.2)
            img = ImageEnhance.Brightness(img).enhance(1.05)
            img.save(caminho)
            log_func(f"[EK1] Aprimorado: {os.path.relpath(caminho)}\n")
    except Exception as e:
        log_func(f"[EK1] Erro ao aprimorar {os.path.basename(caminho)}: {e}\n")

def aprimorar_gif(caminho, log_func):
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
            log_func(f"[EK1] GIF aprimorado: {os.path.relpath(caminho)}\n")

    except Exception as e:
        log_func(f"[EK1] Erro ao aprimorar GIF {os.path.basename(caminho)}: {e}\n")

def executar_ek1(pasta, log_func=lambda msg: None, progress_callback=lambda v: None):
    log_func("=== Executando EK1 - Aprimoramento de Imagens ===\n")

    arquivos = []
    for raiz, _, nomes in os.walk(pasta):
        for nome in nomes:
            if nome.lower().endswith((".jpg", ".jpeg", ".gif")):
                arquivos.append(os.path.join(raiz, nome))

    total = len(arquivos)
    if total == 0:
        log_func("Nenhuma imagem .jpg, .jpeg ou .gif encontrada.\n")
        progress_callback(100)
        return

    for i, caminho in enumerate(arquivos, 1):
        if caminho.lower().endswith((".jpg", ".jpeg")):
            aprimorar_jpeg(caminho, log_func)
        elif caminho.lower().endswith(".gif"):
            aprimorar_gif(caminho, log_func)

        progresso = (i / total) * 100
        progress_callback(progresso)

    log_func("=== EK1 Concluído ===\n")
    progress_callback(100)
