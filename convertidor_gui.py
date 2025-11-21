import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image

# ------------------ LÓGICA DE CONVERSIÓN ------------------ #

def convert_image_file(
    input_path: Path,
    output_format: str,
    output_dir: Path,
    ico_sizes: list[tuple[int, int]] | None = None
) -> tuple[bool, str]:
    if not input_path.is_file():
        return False, f"Archivo no encontrado: {input_path}"

    output_format = output_format.lower().strip().lstrip(".")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{input_path.stem}.{output_format}"

    try:
        with Image.open(input_path) as img:
            # Corregir transparencia si se pasa a JPG
            if output_format in ("jpg", "jpeg") and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            if output_format == "ico":
                # Tamaños para ICO: los que vengan del usuario, o por defecto
                sizes = ico_sizes or [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                img.save(output_file, format="ICO", sizes=sizes)
            else:
                img.save(output_file, format=output_format.upper())

        return True, f"OK: {input_path.name} -> {output_file.name}"
    except Exception as e:
        return False, f"ERROR en {input_path.name}: {e}"


def convert_folder(
    input_dir: Path,
    output_format: str,
    output_dir: Path,
    ico_sizes: list[tuple[int, int]] | None = None
) -> tuple[int, int, list[str]]:
    allowed_ext = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".ico")
    ok_count = 0
    error_count = 0
    messages: list[str] = []

    if not input_dir.is_dir():
        return 0, 0, [f"La carpeta de entrada no existe: {input_dir}"]

    output_dir.mkdir(parents=True, exist_ok=True)

    for file in input_dir.iterdir():
        if file.is_file() and file.suffix.lower() in allowed_ext:
            ok, msg = convert_image_file(file, output_format, output_dir, ico_sizes=ico_sizes)
            messages.append(msg)
            if ok:
                ok_count += 1
            else:
                error_count += 1

    if ok_count + error_count == 0:
        messages.append("No se encontraron imágenes en la carpeta.")

    return ok_count, error_count, messages

# ------------------ INTERFAZ GRÁFICA ------------------ #

class ImageConverterGUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Conversor de Imágenes")
        self.root.geometry("700x450")
        self.root.minsize(650, 400)
        self.root.resizable(True, True)

        self.mode = tk.StringVar(value="file")   # "file" o "folder"
        self.input_folder = tk.StringVar()
        self.input_file = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.output_format = tk.StringVar(value="webp")
        self.ico_sizes_str = tk.StringVar(value="16,32,48,64,128,256")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        # --- MODO --- #
        mode_frame = ttk.LabelFrame(main_frame, text="Modo de conversión", padding=10)
        mode_frame.pack(fill="x", pady=(0, 10))

        ttk.Radiobutton(
            mode_frame,
            text="Archivo único",
            variable=self.mode,
            value="file",
            command=self.update_mode
        ).grid(row=0, column=0, padx=5, pady=2, sticky="w")

        ttk.Radiobutton(
            mode_frame,
            text="Carpeta completa",
            variable=self.mode,
            value="folder",
            command=self.update_mode
        ).grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # --- Archivo (arriba en el flujo para modo Archivo único) --- #
        file_frame = ttk.LabelFrame(main_frame, text="Archivo de entrada", padding=10)
        self.file_frame = file_frame

        ttk.Label(file_frame, text="Archivo:").grid(row=0, column=0, sticky="w")
        ttk.Entry(file_frame, textvariable=self.input_file, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Buscar archivo...", command=self.browse_file).grid(row=0, column=2, padx=5)

        # --- Carpeta de entrada (solo modo carpeta) --- #
        folder_in_frame = ttk.LabelFrame(main_frame, text="Carpeta de entrada", padding=10)
        self.folder_in_frame = folder_in_frame

        ttk.Label(folder_in_frame, text="Carpeta:").grid(row=0, column=0, sticky="w")
        ttk.Entry(folder_in_frame, textvariable=self.input_folder, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(folder_in_frame, text="Buscar carpeta...", command=self.browse_input_folder).grid(row=0, column=2, padx=5)

        # --- Carpeta salida --- #
        folder_out_frame = ttk.LabelFrame(main_frame, text="Carpeta de salida", padding=10)
        folder_out_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(folder_out_frame, text="Carpeta:").grid(row=0, column=0, sticky="w")
        ttk.Entry(folder_out_frame, textvariable=self.output_folder, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(folder_out_frame, text="Buscar carpeta...", command=self.browse_output_folder).grid(row=0, column=2, padx=5)

        # --- Formato salida + tamaños ICO --- #
        format_frame = ttk.LabelFrame(main_frame, text="Formato de salida", padding=10)
        format_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(format_frame, text="Formato:").grid(row=0, column=0, sticky="w")
        formatos = ["webp", "png", "jpg", "jpeg", "ico", "bmp", "tiff"]
        combo = ttk.Combobox(
            format_frame,
            textvariable=self.output_format,
            values=formatos,
            state="readonly",
            width=15
        )
        combo.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        combo.current(0)
        combo.bind("<<ComboboxSelected>>", self.on_format_change)

        # Frame para tamaños ICO (solo visible cuando formato = ico)
        ico_frame = ttk.Frame(format_frame)
        self.ico_frame = ico_frame

        ttk.Label(ico_frame, text="Tamaños ICO (px, separados por comas):").grid(row=0, column=0, sticky="w")
        ttk.Entry(ico_frame, textvariable=self.ico_sizes_str, width=30).grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # --- Botón convertir --- #
        ttk.Button(main_frame, text="Convertir", command=self.run_conversion).pack(pady=10)

        # Estado inicial
        self.update_mode()
        self.on_format_change()  # para mostrar/ocultar tamaños ICO

    # ------------------ Callbacks GUI ------------------ #

    def update_mode(self):
        """
        Reorganiza el flujo:
        - Modo archivo: solo se muestra seleccionar archivo (arriba).
        - Modo carpeta: solo se muestra seleccionar carpeta de entrada.
        """
        # Primero, quitar ambos si están visibles
        self.file_frame.pack_forget()
        self.folder_in_frame.pack_forget()

        if self.mode.get() == "file":
            # Archivo único → arriba del flujo
            self.file_frame.pack(fill="x", pady=(0, 10))
        else:
            # Carpeta completa → mostrar solo carpeta de entrada
            self.folder_in_frame.pack(fill="x", pady=(0, 10))

    def on_format_change(self, event=None):
        """Muestra u oculta el campo de tamaños ICO según el formato."""
        if self.output_format.get().lower() == "ico":
            if not self.ico_frame.winfo_ismapped():
                self.ico_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="w")
        else:
            if self.ico_frame.winfo_ismapped():
                self.ico_frame.grid_forget()

    def browse_input_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de entrada")
        if folder:
            self.input_folder.set(folder)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de imagen",
            filetypes=[
                ("Imágenes", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.tif;*.tiff;*.ico"),
                ("Todos los archivos", "*.*"),
            ]
        )
        if file_path:
            self.input_file.set(file_path)

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder:
            self.output_folder.set(folder)

    def parse_ico_sizes(self) -> list[tuple[int, int]] | None:
        """
        Convierte el texto de tamaños (ej: '16,32,64') en [(16,16), (32,32), (64,64)].
        Si hay error, devuelve None.
        """
        text = self.ico_sizes_str.get().strip()
        if not text:
            return None

        sizes: list[tuple[int, int]] = []
        try:
            parts = text.split(",")
            for p in parts:
                p = p.strip()
                if not p:
                    continue
                n = int(p)
                if n <= 0:
                    raise ValueError("Tamaño no positivo")
                sizes.append((n, n))
            if not sizes:
                return None
            return sizes
        except Exception:
            return None

    def run_conversion(self):
        fmt = self.output_format.get().strip().lower()
        if not fmt:
            messagebox.showerror("Error", "Selecciona un formato de salida.")
            return

        output_folder_str = self.output_folder.get().strip()
        if not output_folder_str:
            messagebox.showerror("Error", "Selecciona la carpeta de salida.")
            return

        output_folder = Path(output_folder_str)
        if not output_folder.exists():
            messagebox.showerror("Error", "La carpeta de salida no existe.")
            return

        # Tamaños ICO (si aplica)
        ico_sizes = None
        if fmt == "ico":
            ico_sizes = self.parse_ico_sizes()
            if ico_sizes is None:
                messagebox.showerror(
                    "Error en tamaños ICO",
                    "Formato de tamaños no válido.\n\nEjemplo: 16,32,64,128"
                )
                return

        if self.mode.get() == "file":
            # Modo archivo único
            file_path_str = self.input_file.get().strip()
            if not file_path_str:
                messagebox.showerror("Error", "Selecciona un archivo de entrada.")
                return

            input_path = Path(file_path_str)

            # Llamamos a la conversión
            ok, msg = convert_image_file(input_path, fmt, output_folder, ico_sizes=ico_sizes)

            # Mensaje de éxito / error detallado
            output_path = output_folder / f"{input_path.stem}.{fmt}"
            if ok:
                messagebox.showinfo(
                    "Conversión completada",
                    f"Archivo convertido correctamente.\n\n"
                    f"Entrada:\n{input_path}\n\n"
                    f"Salida:\n{output_path}"
                )
            else:
                messagebox.showerror("Error en la conversión", msg)

        else:
            # Modo carpeta completa
            input_folder_str = self.input_folder.get().strip()
            if not input_folder_str:
                messagebox.showerror("Error", "Selecciona la carpeta de entrada.")
                return

            input_folder = Path(input_folder_str)

            ok_count, err_count, messages = convert_folder(input_folder, fmt, output_folder, ico_sizes=ico_sizes)

            resumen = "\n".join(messages[-15:])
            resumen += f"\n\nArchivos convertidos correctamente: {ok_count}\nErrores: {err_count}"

            if err_count == 0 and ok_count > 0:
                messagebox.showinfo("Conversión completada", resumen)
            elif ok_count > 0:
                messagebox.showwarning("Conversión con errores", resumen)
            else:
                messagebox.showerror("Sin conversiones exitosas", resumen)


# ------------------ MAIN ------------------ #

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterGUI(root)
    root.mainloop()
