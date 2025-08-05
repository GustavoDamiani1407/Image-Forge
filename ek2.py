import os
import zipfile
import shutil

def executar_ek2(pasta, log_func=lambda msg: None, progress_callback=lambda v: None, tr=lambda x: x):
    """
    Refundição inteligente de arquivos .zip e suas subpastas.
    Extrai o conteúdo de todos os zips para uma pasta única, unificando os arquivos.
    """

    log_func(tr("=== Executando EK2 - Refundição de Zips ===\n"))

    try:
        # Encontrar todos os arquivos zip na pasta e subpastas
        arquivos_zip = []
        for raiz, _, arquivos in os.walk(pasta):
            for nome in arquivos:
                if nome.lower().endswith(".zip"):
                    arquivos_zip.append(os.path.join(raiz, nome))

        total = len(arquivos_zip)
        if total == 0:
            log_func(tr("Nenhum arquivo .zip encontrado para refundir.\n"))
            progress_callback(100)
            return

        # Pasta destino única para extrair todo conteúdo
        pasta_unificada = os.path.join(pasta, "__refundicao_unificada")
        if not os.path.exists(pasta_unificada):
            os.makedirs(pasta_unificada)

        for i, caminho_zip in enumerate(arquivos_zip, 1):
            nome_zip = os.path.basename(caminho_zip)
            log_func(tr("Processando {arquivo}...\n").format(arquivo=nome_zip))

            try:
                with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                    # Extrair para pasta temporária
                    pasta_temp = os.path.join(pasta, "__temp_ek2")
                    if os.path.exists(pasta_temp):
                        shutil.rmtree(pasta_temp)
                    os.makedirs(pasta_temp)

                    zip_ref.extractall(pasta_temp)
                    log_func(tr("Extraído {arquivo} para pasta temporária {pasta}\n").format(arquivo=nome_zip, pasta=pasta_temp))

                    # Agora mover arquivos da pasta_temp para a pasta_unificada
                    for root_temp, dirs_temp, files_temp in os.walk(pasta_temp):
                        for file_temp in files_temp:
                            caminho_arquivo = os.path.join(root_temp, file_temp)
                            # Mantém estrutura relativa para evitar conflitos
                            rel_path = os.path.relpath(caminho_arquivo, pasta_temp)
                            destino = os.path.join(pasta_unificada, rel_path)

                            # Cria pastas necessárias na unificada
                            os.makedirs(os.path.dirname(destino), exist_ok=True)

                            # Se arquivo existir, adiciona sufixo numérico para evitar sobrescrever
                            if os.path.exists(destino):
                                base, ext = os.path.splitext(destino)
                                contador = 1
                                novo_destino = f"{base}_{contador}{ext}"
                                while os.path.exists(novo_destino):
                                    contador += 1
                                    novo_destino = f"{base}_{contador}{ext}"
                                destino = novo_destino

                            shutil.move(caminho_arquivo, destino)
                    log_func(tr("Conteúdo de {arquivo} movido para {pasta}\n").format(arquivo=nome_zip, pasta=pasta_unificada))

                    # Limpa pasta temporária
                    shutil.rmtree(pasta_temp)

                # Remove o zip original
                os.remove(caminho_zip)
                log_func(tr("Removido arquivo zip original {arquivo}\n").format(arquivo=nome_zip))

            except Exception as e:
                log_func(tr("Erro ao processar {arquivo}: {erro}\n").format(arquivo=nome_zip, erro=e))

            progresso = (i / total) * 100
            progress_callback(progresso)

    except Exception as e:
        log_func(tr("Erro ao executar EK2: {erro}\n").format(erro=e))

    log_func(tr("=== EK2 Concluído ===\n"))
    progress_callback(100)
