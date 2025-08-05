import os
import shutil
from core import (
    converter_imagens,
    remover_duplicatas,
    renomear_temp,
    realinhar_sequencia,
    executar_pipeline_completo,
)

# Função de log simples para imprimir mensagens
def log_print(msg):
    print(msg, end='')  # Já tem \n nas mensagens

# Função de tradução dummy (substitua pela real, se quiser)
def tr_dummy(texto):
    # Aqui só retorna o texto original para teste, sem tradução
    return texto

# Pasta temporária de teste
pasta_teste = "teste_imagens"

# Cria a pasta e alguns arquivos simulados
if os.path.exists(pasta_teste):
    shutil.rmtree(pasta_teste)
os.makedirs(pasta_teste)

# Criando arquivos dummy
with open(os.path.join(pasta_teste, "TEMP_image1.jpg"), "wb") as f:
    f.write(b"dummydata")
with open(os.path.join(pasta_teste, "image1.png"), "wb") as f:
    f.write(b"dummydata")
with open(os.path.join(pasta_teste, "image2.jpg"), "wb") as f:
    f.write(b"dummydata")
with open(os.path.join(pasta_teste, "g1.gif"), "wb") as f:
    f.write(b"dummydata")

# Agora executa o pipeline completo (você pode executar passo a passo também)
executar_pipeline_completo(
    pasta=pasta_teste,
    log_func=log_print,
    progress_callback=lambda v: print(f"Progresso: {v:.1f}%"),
    formato_saida=".jpg",
    prefixo_imagem="i",
    prefixo_gif="g",
    unificar=False,
    tr=tr_dummy,
)

# Remova a pasta de teste, se desejar
# shutil.rmtree(pasta_teste)
