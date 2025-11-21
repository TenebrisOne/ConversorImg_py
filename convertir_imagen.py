import sys
from pathlib import Path
from PIL import Image

def convert_image(input_path: str, output_format: str, output_folder: str | None = None) -> None:
    input_file = Path(input_path)
    if not input_file.is_file():
        print(f"Archivo no encontrado: {input_file}")
        return

    output_format = output_format.lower().strip().lstrip(".")  # ej: "ico", "webp", "jpg"

    # Carpeta de salida
    output_dir = Path(output_folder) if output_folder else input_file.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{input_file.stem}.{output_format}"

    try:
        with Image.open(input_file) as img:
            # Corrección para imágenes con transparencia cuando se convierte a JPG
            if output_format in ("jpg", "jpeg") and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            # Manejo especial para ICO → requiere tamaños
            if output_format == "ico":
                # Tamaños comunes soportados por Windows
                sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                img.save(output_file, format="ICO", sizes=sizes)
            else:
                img.save(output_file, format=output_format.upper())

        print(f"Convertido: {input_file}  ->  {output_file}")

    except Exception as e:
        print(f"Error al convertir {input_file}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso:")
        print("  python convertir_imagen.py <imagen_entrada> <formato_salida> [carpeta_salida]")
        print("Ejemplos:")
        print("  python convertir_imagen.py foto.png webp")
        print("  python convertir_imagen.py logo.webp jpg salida/")
        print("  python convertir_imagen.py icono.png ico")
        sys.exit(1)

    input_path = sys.argv[1]
    output_format = sys.argv[2]
    output_folder = sys.argv[3] if len(sys.argv) >= 4 else None

    convert_image(input_path, output_format, output_folder)
