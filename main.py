try:
    # Tenta importar o TkinterDnD (suporte a Drag & Drop)
    from tkinterdnd2 import TkinterDnD
    USE_DND = True
except ImportError:
    import tkinter as tk
    USE_DND = False

import ek4
from gui import iniciar_interface


def main():
    if USE_DND:
        root = TkinterDnD.Tk()
    else:
        import tkinter as tk
        root = tk.Tk()
        print("⚠️ tkinterdnd2 não instalado. Arrastar e soltar desativado.")

    # Define o título da janela usando a tradução atual
    root.title(ek4.tr("Image Forge - Gerenciador de Imagens"))

    gui = iniciar_interface(root)  # GUARDE a referência
    root.mainloop()


if __name__ == "__main__":
    main()
