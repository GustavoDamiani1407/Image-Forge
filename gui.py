import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import tkinter.ttk as ttk
import os
from core import executar_pipeline_completo, METRICAS
from ek1 import executar_ek1
from ek2 import executar_ek2

try:
    from tkinterdnd2 import DND_FILES
except ImportError:
    DND_FILES = None

try:
    from tkinterdnd2 import DND_FILES
    USE_DND = True
except ImportError:
    DND_FILES = None
    USE_DND = False


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
        x, y, _, _ = self.widget.bbox("insert")
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

class ImageForgeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Forge - Gerenciador de Imagens")
        self.root.geometry("720x520")

        self.pasta_selecionada = ""

        # Frame de seleção
        frame_caminho = tk.Frame(root)
        frame_caminho.pack(padx=10, pady=10, fill=tk.X)

        self.entry_caminho = tk.Entry(frame_caminho, font=("Arial", 12))
        self.entry_caminho.pack(side=tk.LEFT, fill=tk.X, expand=True)

        if USE_DND and DND_FILES is not None:
            try:
                self.entry_caminho.drop_target_register(DND_FILES)
                self.entry_caminho.dnd_bind('<<Drop>>', self.handle_drop)
            except Exception as e:
                self.log(f"Drag & Drop não habilitado: {e}\n")

        btn_procurar = tk.Button(frame_caminho, text="Procurar Pasta", command=self.selecionar_pasta)
        btn_procurar.pack(side=tk.LEFT, padx=5)
        ToolTip(btn_procurar, "Seleciona a pasta contendo imagens")

        # Frame para menu de formato
        frame_formato = tk.Frame(root)
        frame_formato.pack(padx=10, pady=5, fill=tk.X)

        tk.Label(frame_formato, text="Formato de saída:").pack(side=tk.LEFT)

        self.formato_var = tk.StringVar(value=".jpg")
        formato_menu = ttk.Combobox(frame_formato, textvariable=self.formato_var,
                                      values=[".jpg", ".png", ".webp"],
                                      state="readonly", width=10)
        formato_menu.pack(side=tk.LEFT, padx=5)
        ToolTip(formato_menu, "Selecione o formato final das imagens convertidas")
        
        # Frame para os prefixos
        frame_prefixos = tk.Frame(root)
        frame_prefixos.pack(padx=10, pady=5, fill=tk.X)

        tk.Label(frame_prefixos, text="Prefixo Imagem:").pack(side=tk.LEFT, padx=(0, 5))
        self.prefixo_img_var = tk.StringVar(value="i")
        entry_prefixo_img = tk.Entry(frame_prefixos, textvariable=self.prefixo_img_var, width=10)
        entry_prefixo_img.pack(side=tk.LEFT)
        ToolTip(entry_prefixo_img, "Prefixo para renomear arquivos de imagem (ex: 'img-', 'foto_', etc.)")
        
        tk.Label(frame_prefixos, text="Prefixo GIF:").pack(side=tk.LEFT, padx=(10, 5))
        self.prefixo_gif_var = tk.StringVar(value="g")
        entry_prefixo_gif = tk.Entry(frame_prefixos, textvariable=self.prefixo_gif_var, width=10)
        entry_prefixo_gif.pack(side=tk.LEFT)
        ToolTip(entry_prefixo_gif, "Prefixo para renomear arquivos GIF (ex: 'gif-', 'anim_', etc.)")

        # Botões principais
        frame_botoes = tk.Frame(root)
        frame_botoes.pack(padx=10, pady=5, fill=tk.X)

        self.btn_iniciar = tk.Button(frame_botoes, text="Iniciar Pipeline", command=self.iniciar_pipeline, state=tk.DISABLED)
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        ToolTip(self.btn_iniciar, "Executa o pipeline principal")

        self.btn_ek1 = tk.Button(frame_botoes, text="Executar EK1 (Aprimorar Imagens)", command=self.executar_ek1, state=tk.DISABLED)
        self.btn_ek1.pack(side=tk.LEFT, padx=5)
        ToolTip(self.btn_ek1, "Aprimora imagens e gifs de baixa qualidade")

        self.btn_ek2 = tk.Button(frame_botoes, text="Executar EK2 (Refundir Zips)", command=self.executar_ek2, state=tk.DISABLED)
        self.btn_ek2.pack(side=tk.LEFT, padx=5)
        ToolTip(self.btn_ek2, "Refundição inteligente de arquivos zip")

        self.btn_salvar_log = tk.Button(frame_botoes, text="Salvar Log", command=self.salvar_log)
        self.btn_salvar_log.pack(side=tk.RIGHT, padx=5)
        ToolTip(self.btn_salvar_log, "Salva o log como arquivo .txt")

        # Área de log
        self.text_log = ScrolledText(root, height=20, font=("Consolas", 10))
        self.text_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_log.config(state=tk.DISABLED)

        # Barra de progresso
        self.progresso_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(root, variable=self.progresso_var, maximum=100)
        self.progressbar.pack(padx=10, pady=(0,10), fill=tk.X)

    def handle_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        if paths:
            pasta = paths[0]
            if os.path.isdir(pasta):
                self.pasta_selecionada = pasta
                self.entry_caminho.delete(0, tk.END)
                self.entry_caminho.insert(0, pasta)
                self.log(f"Pasta arrastada e selecionada: {pasta}\n")
                self.btn_iniciar.config(state=tk.NORMAL)
                self.btn_ek1.config(state=tk.NORMAL)
                self.btn_ek2.config(state=tk.NORMAL)
                self.atualizar_progresso(0)
            else:
                self.log("Arraste uma pasta válida.\n")

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
            self.log(f"Pasta selecionada: {pasta}\n")
            self.btn_iniciar.config(state=tk.NORMAL)
            self.btn_ek1.config(state=tk.NORMAL)
            self.btn_ek2.config(state=tk.NORMAL)
            self.atualizar_progresso(0)
        else:
            self.log("Nenhuma pasta selecionada.\n")

    def iniciar_pipeline(self):
        if not self.pasta_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma pasta antes de iniciar o pipeline.")
            return
        self.log("=== Iniciando Pipeline Completo ===\n")
        self.atualizar_progresso(0)
        try:
            formato = self.formato_var.get()
            
            prefixo_img = self.prefixo_img_var.get().strip() or "i"
            prefixo_gif = self.prefixo_gif_var.get().strip() or "g"

            # ADICIONE ESTA LINHA PARA DEBUG
            self.log(f"DEBUG GUI: Lendo prefixos da interface. Imagem: '{prefixo_img}', GIF: '{prefixo_gif}'\n")

            executar_pipeline_completo(
                self.pasta_selecionada,
                log_func=self.log,
                progress_callback=self.atualizar_progresso,
                formato_saida=formato,
                prefixo_img=prefixo_img,
                prefixo_gif=prefixo_gif
            )
        except Exception as e:
            self.log(f"Erro no pipeline: {e}\n")
        self.log("=== Pipeline Concluído ===\n")
        self.exibir_metricas()

    def exibir_metricas(self):
        self.log("\n=== Métricas Gerais ===\n")
        for chave, valor in METRICAS.items():
            self.log(f"{chave}: {valor}\n")

    def executar_ek1(self):
        if not self.pasta_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma pasta antes de executar EK1.")
            return
        self.log("=== Executando EK1 - Aprimoramento de Imagens ===\n")
        self.atualizar_progresso(0)
        try:
            executar_ek1(
                self.pasta_selecionada,
                log_func=self.log,
                progress_callback=self.atualizar_progresso
            )
        except Exception as e:
            self.log(f"Erro ao executar EK1: {e}\n")
        self.log("=== EK1 Concluído ===\n")

    def executar_ek2(self):
        if not self.pasta_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma pasta antes de executar EK2.")
            return
        self.log("=== Executando EK2 - Refundição de Zips ===\n")
        self.atualizar_progresso(0)
        try:
            executar_ek2(
                self.pasta_selecionada,
                log_func=self.log,
                progress_callback=self.atualizar_progresso
            )
        except Exception as e:
            self.log(f"Erro ao executar EK2: {e}\n")
        self.log("=== EK2 Concluído ===\n")

    def salvar_log(self):
        if self.text_log.get("1.0", tk.END).strip() == "":
            messagebox.showinfo("Info", "O log está vazio, nada para salvar.")
            return
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if arquivo:
            try:
                with open(arquivo, "w", encoding="utf-8") as f:
                    f.write(self.text_log.get("1.0", tk.END))
                messagebox.showinfo("Sucesso", f"Log salvo em:\n{arquivo}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar log:\n{e}")

def iniciar_interface(root):
    ImageForgeGUI(root)

#V1.2.1