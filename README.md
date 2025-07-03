# 🖼️ Image Forge

![Versão](https://img.shields.io/badge/vers%C3%A3o-v1.0.0-success?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Licença](https://img.shields.io/badge/Licença-MIT-informational?style=flat-square)

**Image Forge** é uma ferramenta completa para conversão, organização e aprimoramento de imagens, criada para automatizar fluxos repetitivos com eficiência e precisão. Ideal para quem lida com grandes volumes de imagens e precisa padronizá-las com rapidez.

---

## ✨ Funcionalidades

- 🔄 **Conversão automática** de imagens `.webp`, `.png`, `.jpeg` e `.jpg_large` para `.jpg`
- ♻️ **Remoção inteligente de duplicatas** com verificação por hash
- 🧩 **Realinhamento sequencial** conforme os padrões DSIP (imagens) e DSGP (GIFs)
- 🖥️ **Interface gráfica (GUI)** com suporte a Drag & Drop (opcional)
- 📈 **Barra de progresso e log detalhado**
- 🧪 **EK1**: Aprimora qualidade de imagens e GIFs
- 📦 **EK2**: Refundição inteligente de arquivos `.zip` e subpastas

---

## 📸 Exemplo de uso

Selecione uma pasta com imagens, clique em **Iniciar Pipeline** e o Image Forge executará as seguintes etapas:

1. Converter imagens para `.jpg`
2. Eliminar duplicatas
3. Realinhar nomes sequenciais (i1.jpg, g1.gif, etc.)
4. Exibir métricas do processamento

---

## 🧪 Requisitos

- Python 3.9 ou superior  
- Bibliotecas:

```bash
pip install -r requirements.txt

