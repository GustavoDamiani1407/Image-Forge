import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import tkinter.ttk as ttk
import os

from core import executar_pipeline_completo, METRICAS
from ek1 import executar_ek1
from ek2 import executar_ek2
import ek4  # Módulo de internacionalização

# ========== Tooltip ==========
class ToolTip:
    def __init__(self, widget, texto):
        self.widget = widget
        self.texto = texto
        self.tipwindow = None
        widget.bind("<Enter>", self.mostrar)
        widget.bind("<Leave>", self.esconder)

    def mostrar(self, event=None):
        if self.tipwindow or not self.texto:
            return
        try:
            x, y, _, _ = self.widget.bbox("insert")
        except Exception:
            x, y = 0, 0
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.texto, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=4, ipady=2)

    def esconder(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None

# ========== GUI ==========
class ImageForgeGUI:
    def __init__(self, root):
        print("Iniciando ImageForgeGUI...")
        self.root = root
        self.root.title(ek4.tr("Image Forge - Gerenciador de Imagens"))
        self.root.geometry("800x580")

        self.pasta_selecionada = ""

        self.linguas = {
            "pt_BR": "Português (Brasil)",
            "en_US": "English",
            "es_ES": "Español",
            "de_DE": "Deutsch",
            "ru_RU": "Русский",
            "ja_JP": "日本語",
            "zh_CN": "中文",
            "ko_KR": "한국어",
        }

        self.idioma_atual = ek4.get_lingua()

        # === Menu ===
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self.atualizar_menu_idioma()

        # ======= Frame: Pasta =======
        frame_caminho = tk.Frame(root)
        frame_caminho.pack(padx=10, pady=10, fill=tk.X)

        self.entry_caminho = tk.Entry(frame_caminho, font=("Arial", 12))
        self.entry_caminho.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_procurar = tk.Button(frame_caminho, text=ek4.tr("Procurar Pasta"), command=self.selecionar_pasta)
        self.btn_procurar.pack(side=tk.LEFT, padx=5)
        self.btn_procurar.tooltip = ToolTip(self.btn_procurar, ek4.tr("Seleciona a pasta contendo imagens para o pipeline"))

        # ======= Frame: Formato =======
        frame_formato = tk.Frame(root)
        frame_formato.pack(padx=10, pady=5, fill=tk.X)

        self.label_formato_saida = tk.Label(frame_formato, text=ek4.tr("Formato de saída:"))
        self.label_formato_saida.pack(side=tk.LEFT)

        self.formato_var = tk.StringVar(value=".jpg")
        self.formato_menu = ttk.Combobox(frame_formato, textvariable=self.formato_var,
                                         values=[".jpg", ".png", ".webp"], state="readonly", width=10)
        self.formato_menu.pack(side=tk.LEFT, padx=5)
        self.formato_menu.tooltip = ToolTip(self.formato_menu, ek4.tr("Define o formato final para todas as imagens (exceto GIFs)"))

        # ======= Frame: Nomenclatura (EK3) =======
        self.frame_nomes = tk.LabelFrame(root, text=ek4.tr("Personalização de Nomenclatura"))
        self.frame_nomes.pack(padx=10, pady=5, fill=tk.X)

        self.label_prefixo_imagem = tk.Label(self.frame_nomes, text=ek4.tr("Prefixo para imagens:"))
        self.label_prefixo_imagem.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.prefixo_imagem = tk.Entry(self.frame_nomes, width=8)
        self.prefixo_imagem.grid(row=0, column=1, padx=5, pady=2)
        self.prefixo_imagem.tooltip = ToolTip(self.prefixo_imagem, ek4.tr("Altere o prefixo padrão 'i' para outro ao nomear imagens (ex: 'img')"))

        self.label_prefixo_gif = tk.Label(self.frame_nomes, text=ek4.tr("Prefixo para GIFs:"))
        self.label_prefixo_gif.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.prefixo_gif = tk.Entry(self.frame_nomes, width=8)
        self.prefixo_gif.grid(row=0, column=3, padx=5, pady=2)
        self.prefixo_gif.tooltip = ToolTip(self.prefixo_gif, ek4.tr("Altere o prefixo padrão 'g' para outro ao nomear GIFs (ex: 'gif')"))

        self.unificar_var = tk.BooleanVar()
        self.check_unificar = tk.Checkbutton(self.frame_nomes, text=ek4.tr("Unificar sequência de imagens e GIFs"), variable=self.unificar_var)
        self.check_unificar.grid(row=1, column=0, columnspan=4, sticky="w", padx=5, pady=2)
        self.check_unificar.tooltip = ToolTip(self.check_unificar, ek4.tr("Ative para usar um único prefixo e sequência unificada para imagens e GIFs"))

        # ======= Frame: Botões =======
        frame_botoes = tk.Frame(root)
        frame_botoes.pack(padx=10, pady=5, fill=tk.X)

        self.btn_iniciar = tk.Button(frame_botoes, text=ek4.tr("Iniciar Pipeline"), command=self.iniciar_pipeline, state=tk.DISABLED)
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)

        self.btn_ek1 = tk.Button(frame_botoes, text=ek4.tr("Executar EK1 (Aprimorar Imagens)"), command=self.executar_ek1, state=tk.DISABLED)
        self.btn_ek1.pack(side=tk.LEFT, padx=5)

        self.btn_ek2 = tk.Button(frame_botoes, text=ek4.tr("Executar EK2 (Refundir ZIPs)"), command=self.executar_ek2, state=tk.DISABLED)
        self.btn_ek2.pack(side=tk.LEFT, padx=5)

        self.btn_salvar_log = tk.Button(frame_botoes, text=ek4.tr("Salvar Log"), command=self.salvar_log)
        self.btn_salvar_log.pack(side=tk.RIGHT, padx=5)

        # ======= Área de Log =======
        self.text_log = ScrolledText(root, height=20, font=("Consolas", 10))
        self.text_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_log.config(state=tk.DISABLED)

        # ======= Barra de Progresso =======
        self.progresso_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(root, variable=self.progresso_var, maximum=100)
        self.progressbar.pack(padx=10, pady=(0, 10), fill=tk.X)

        print("Interface criada com sucesso.")

    def atualizar_menu_idioma(self):
        self.menu_bar.delete(0)
        self.menu_idioma = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=ek4.tr("Idioma"), menu=self.menu_idioma)

        for codigo, nome in self.linguas.items():
            nome_traduzido = ek4.tr(nome)
            self.menu_idioma.add_command(label=nome_traduzido, command=lambda c=codigo: self.trocar_idioma(c))

    def trocar_idioma(self, codigo_idioma):
        if codigo_idioma != self.idioma_atual:
            ek4.set_lingua(codigo_idioma)
            self.idioma_atual = codigo_idioma
            self.log(ek4.tr("Idioma alterado para {idioma}\n").format(idioma=ek4.tr(self.linguas[codigo_idioma])))
            self.atualizar_textos()

    def atualizar_textos(self):
        self.root.title(ek4.tr("Image Forge - Gerenciador de Imagens"))
        self.atualizar_menu_idioma()

        self.btn_procurar.config(text=ek4.tr("Procurar Pasta"))
        self.label_formato_saida.config(text=ek4.tr("Formato de saída:"))

        self.frame_nomes.config(text=ek4.tr("Personalização de Nomenclatura"))
        self.label_prefixo_imagem.config(text=ek4.tr("Prefixo para imagens:"))
        self.label_prefixo_gif.config(text=ek4.tr("Prefixo para GIFs:"))
        self.check_unificar.config(text=ek4.tr("Unificar sequência de imagens e GIFs"))

        self.btn_iniciar.config(text=ek4.tr("Iniciar Pipeline"))
        self.btn_ek1.config(text=ek4.tr("Executar EK1 (Aprimorar Imagens)"))
        self.btn_ek2.config(text=ek4.tr("Executar EK2 (Refundir ZIPs)"))
        self.btn_salvar_log.config(text=ek4.tr("Salvar Log"))

    def log(self, msg):
        self.text_log.config(state=tk.NORMAL)
        self.text_log.insert(tk.END, msg)
        self.text_log.see(tk.END)
        self.text_log.config(state=tk.DISABLED)

    def atualizar_progresso(self, valor):
        self.progresso_var.set(valor)
        self.root.update_idletasks()

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_selecionada = pasta
            self.entry_caminho.delete(0, tk.END)
            self.entry_caminho.insert(0, pasta)
            self.log(ek4.tr("Pasta selecionada: {pasta}\n").format(pasta=pasta))
            self.btn_iniciar.config(state=tk.NORMAL)
            self.btn_ek1.config(state=tk.NORMAL)
            self.btn_ek2.config(state=tk.NORMAL)
            self.atualizar_progresso(0)
        else:
            self.log(ek4.tr("Nenhuma pasta selecionada.\n"))

    def iniciar_pipeline(self):
        formato = self.formato_var.get()
        prefixo_img = self.prefixo_imagem.get().strip() or None
        prefixo_gif = self.prefixo_gif.get().strip() or None
        unificar = self.unificar_var.get()

        self.log(ek4.tr("=== Iniciando Pipeline Completo ===\n"))
        try:
            executar_pipeline_completo(
                self.pasta_selecionada,
                log_func=self.log,
                progress_callback=self.atualizar_progresso,
                formato_saida=formato,
                prefixo_imagem=prefixo_img,
                prefixo_gif=prefixo_gif,
                unificar=unificar,
                tr=ek4.tr
            )
        except Exception as e:
            self.log(ek4.tr("Erro no pipeline: {erro}\n").format(erro=str(e)))

    def executar_ek1(self):
        executar_ek1(
            self.pasta_selecionada,
            log_func=self.log,
            tr=ek4.tr
        )

    def executar_ek2(self):
        executar_ek2(
            self.pasta_selecionada,
            log_func=self.log,
            tr=ek4.tr
        )

    def salvar_log(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Arquivo de Texto", "*.txt")])
        if caminho:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(self.text_log.get("1.0", tk.END))
            messagebox.showinfo(ek4.tr("Log Salvo"), ek4.tr("Log salvo em:\n{caminho}").format(caminho=caminho))

# ======= Launcher =======
def iniciar_interface(root):
    gui = ImageForgeGUI(root)
    return gui
