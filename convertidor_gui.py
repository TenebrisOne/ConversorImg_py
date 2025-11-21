import customtkinter as ctk
from tkinter import filedialog, messagebox
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
            if output_format in ("jpg", "jpeg") and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            if output_format == "ico":
                sizes = ico_sizes or [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                img.save(output_file, format="ICO", sizes=sizes)
            else:
                img.save(output_file, format=output_format.upper())

        return True, f"OK: {input_path} -> {output_file}"
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

# ------------------ INTERFAZ MODERNA (CustomTkinter) ------------------ #

class ImageConverterApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Apariencia "tipo iOS": claro, limpio, bordes redondeados
        ctk.set_appearance_mode("light")          # "light", "dark", "system"
        ctk.set_default_color_theme("blue")       # "blue", "green", "dark-blue"

        self.title("Conversor de Imágenes")
        self.geometry("750x480")
        self.minsize(700, 430)

        # Variables de estado
        self.mode = ctk.StringVar(value="file")   # "file" o "folder"
        self.input_file = ctk.StringVar()
        self.input_folder = ctk.StringVar()
        self.output_folder = ctk.StringVar()
        self.output_format = ctk.StringVar(value="webp")
        self.ico_sizes_str = ctk.StringVar(value="16,32,48,64,128,256")

        self._build_ui()

    # ------------------ UI ------------------ #

    def _build_ui(self):
        # Contenedor principal
        main_frame = ctk.CTkFrame(self, corner_radius=24)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Conversor de Imágenes",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(15, 5))

        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Convierte imágenes a WEBP, ICO, PNG, JPG y más",
            font=ctk.CTkFont(size=13)
        )
        subtitle_label.pack(pady=(0, 15))

        # Frame superior: modo y formato
        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(5, 15))

        # Bloque izquierda: modo
        mode_frame = ctk.CTkFrame(top_frame, corner_radius=18)
        mode_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            mode_frame,
            text="Modo de conversión",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=12, pady=(8, 2))

        mode_inner = ctk.CTkFrame(mode_frame, fg_color="transparent")
        mode_inner.pack(anchor="w", padx=12, pady=(0, 8))

        ctk.CTkRadioButton(
            mode_inner,
            text="Archivo único",
            variable=self.mode,
            value="file",
            command=self._update_mode
        ).pack(side="left", padx=(0, 12))

        ctk.CTkRadioButton(
            mode_inner,
            text="Carpeta completa",
            variable=self.mode,
            value="folder",
            command=self._update_mode
        ).pack(side="left")

        # Bloque derecha: formato + tamaños ICO
        format_frame = ctk.CTkFrame(top_frame, corner_radius=18)
        format_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))

        ctk.CTkLabel(
            format_frame,
            text="Formato de salida",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=12, pady=(8, 2))

        format_inner = ctk.CTkFrame(format_frame, fg_color="transparent")
        format_inner.pack(fill="x", padx=12, pady=(0, 8))

        formatos = ["webp", "png", "jpg", "jpeg", "ico", "bmp", "tiff"]
        self.format_combo = ctk.CTkComboBox(
            format_inner,
            values=formatos,
            variable=self.output_format,
            width=120,
            command=self._on_format_change
        )
        self.format_combo.pack(side="left", padx=(0, 10))

        # Frame ICO sizes (solo visible si formato = ico)
        self.ico_frame = ctk.CTkFrame(format_inner, fg_color="transparent")
        ico_label = ctk.CTkLabel(
            self.ico_frame,
            text="Tamaños ICO:",
            font=ctk.CTkFont(size=11)
        )
        ico_label.pack(side="left")
        self.ico_entry = ctk.CTkEntry(
            self.ico_frame,
            textvariable=self.ico_sizes_str,
            placeholder_text="16,32,64,128",
            width=150
        )
        self.ico_entry.pack(side="left", padx=(5, 0))

        # Cuerpo: selección de archivo / carpeta + salida
        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # --- Frame para archivo único --- #
        self.file_frame = ctk.CTkFrame(center_frame, corner_radius=18)
        self.file_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            self.file_frame,
            text="Archivo de entrada",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 4))

        ctk.CTkEntry(
            self.file_frame,
            textvariable=self.input_file,
            placeholder_text="Selecciona un archivo de imagen",
            width=430
        ).grid(row=1, column=0, columnspan=2, padx=(12, 8), pady=(0, 12), sticky="w")

        ctk.CTkButton(
            self.file_frame,
            text="Buscar archivo",
            command=self._browse_file,
            width=120
        ).grid(row=1, column=2, padx=(0, 12), pady=(0, 12), sticky="e")

        # --- Frame para carpeta de entrada (modo carpeta) --- #
        self.folder_in_frame = ctk.CTkFrame(center_frame, corner_radius=18)

        ctk.CTkLabel(
            self.folder_in_frame,
            text="Carpeta de entrada",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 4))

        ctk.CTkEntry(
            self.folder_in_frame,
            textvariable=self.input_folder,
            placeholder_text="Selecciona la carpeta con las imágenes",
            width=430
        ).grid(row=1, column=0, columnspan=2, padx=(12, 8), pady=(0, 12), sticky="w")

        ctk.CTkButton(
            self.folder_in_frame,
            text="Buscar carpeta",
            command=self._browse_input_folder,
            width=120
        ).grid(row=1, column=2, padx=(0, 12), pady=(0, 12), sticky="e")

        # --- Carpeta de salida (común a ambos modos) --- #
        out_frame = ctk.CTkFrame(center_frame, corner_radius=18)
        out_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            out_frame,
            text="Carpeta de salida",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 4))

        ctk.CTkEntry(
            out_frame,
            textvariable=self.output_folder,
            placeholder_text="Selecciona la carpeta donde se guardarán las imágenes convertidas",
            width=430
        ).grid(row=1, column=0, columnspan=2, padx=(12, 8), pady=(0, 12), sticky="w")

        ctk.CTkButton(
            out_frame,
            text="Buscar carpeta",
            command=self._browse_output_folder,
            width=120
        ).grid(row=1, column=2, padx=(0, 12), pady=(0, 12), sticky="e")

        # Botón Convertir
        convert_button = ctk.CTkButton(
            main_frame,
            text="Convertir",
            command=self._run_conversion,
            height=40,
            corner_radius=20,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        convert_button.pack(pady=(5, 10))

        # Estado inicial
        self._update_mode()
        self._on_format_change()

    # ------------------ Helpers UI ------------------ #

    def _update_mode(self):
        # Quitar ambos
        self.file_frame.pack_forget()
        self.folder_in_frame.pack_forget()

        if self.mode.get() == "file":
            self.file_frame.pack(fill="x", pady=(0, 10))
        else:
            self.folder_in_frame.pack(fill="x", pady=(0, 10))

    def _on_format_change(self, value=None):
        if self.output_format.get().lower() == "ico":
            if not self.ico_frame.winfo_ismapped():
                self.ico_frame.pack(side="left", padx=(0, 0))
        else:
            if self.ico_frame.winfo_ismapped():
                self.ico_frame.pack_forget()

    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de imagen",
            filetypes=[
                ("Imágenes", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.tif;*.tiff;*.ico"),
                ("Todos los archivos", "*.*"),
            ]
        )
        if file_path:
            self.input_file.set(file_path)

    def _browse_input_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de entrada")
        if folder:
            self.input_folder.set(folder)

    def _browse_output_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder:
            self.output_folder.set(folder)

    def _parse_ico_sizes(self) -> list[tuple[int, int]] | None:
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

    # ------------------ Lógica de conversión (botón) ------------------ #

    def _run_conversion(self):
        fmt = self.output_format.get().strip().lower()
        if not fmt:
            messagebox.showerror("Error", "Selecciona un formato de salida.")
            return

        out_str = self.output_folder.get().strip()
        if not out_str:
            messagebox.showerror("Error", "Selecciona la carpeta de salida.")
            return

        output_dir = Path(out_str)
        if not output_dir.exists():
            messagebox.showerror("Error", "La carpeta de salida no existe.")
            return

        ico_sizes = None
        if fmt == "ico":
            ico_sizes = self._parse_ico_sizes()
            if ico_sizes is None:
                messagebox.showerror(
                    "Error en tamaños ICO",
                    "Formato de tamaños no válido.\nEjemplo: 16,32,64,128"
                )
                return

        if self.mode.get() == "file":
            # Archivo único
            file_str = self.input_file.get().strip()
            if not file_str:
                messagebox.showerror("Error", "Selecciona un archivo de entrada.")
                return

            input_path = Path(file_str)
            ok, msg = convert_image_file(input_path, fmt, output_dir, ico_sizes=ico_sizes)
            output_path = output_dir / f"{input_path.stem}.{fmt}"

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
            # Carpeta completa
            folder_str = self.input_folder.get().strip()
            if not folder_str:
                messagebox.showerror("Error", "Selecciona la carpeta de entrada.")
                return

            input_dir = Path(folder_str)
            ok_count, err_count, msgs = convert_folder(input_dir, fmt, output_dir, ico_sizes=ico_sizes)

            resumen = "\n".join(msgs[-10:])
            resumen += f"\n\nArchivos OK: {ok_count}\nErrores: {err_count}"

            if ok_count > 0 and err_count == 0:
                messagebox.showinfo("Conversión completada", resumen)
            elif ok_count > 0:
                messagebox.showwarning("Conversión con errores", resumen)
            else:
                messagebox.showerror("Sin conversiones exitosas", resumen)


# ------------------ MAIN ------------------ #

if __name__ == "__main__":
    app = ImageConverterApp()
    app.mainloop()
