try:
    # Tenta importar o TkinterDnD (suporte a Drag & Drop)
    from tkinterdnd2 import TkinterDnD
    USE_DND = True
except ImportError:
    import tkinter as tk
    USE_DND = False

from gui import iniciar_interface


def main():
    if USE_DND:
        root = TkinterDnD.Tk()
        root.title("Image Forge - com Drag & Drop")
    else:
        import tkinter as tk
        root = tk.Tk()
        root.title("Image Forge - sem Drag & Drop")
        print("⚠️ tkinterdnd2 não instalado. Arrastar e soltar desativado.")

    iniciar_interface(root)
    root.mainloop()


if __name__ == "__main__":
    main()

#V1.2.1
