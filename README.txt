¿Cómo ejecutar el comando?

Debes abrir CMD dentro de la carpeta Conversor (la misma donde está convertir_imagen.py) y usar:

python convertir_imagen.py input/foto1.png webp output


Explicación:

input/foto1.png → ruta de entrada relativa

webp → formato de salida

output → carpeta de salida (ruta relativa)

Ejemplos completos
1. Convertir PNG → WEBP:
python convertir_imagen.py input/foto1.png webp output


Resultado:

Conversor/output/foto1.webp

2. Convertir JPG → ICO:
python convertir_imagen.py input/imagen2.jpg ico output


Resultado:

Conversor/output/imagen2.ico

3. Convertir WEBP → PNG:
python convertir_imagen.py input/logo.webp png output


Resultado:

Conversor/output/logo.png


✔️ 1. Convertir TODOS los .png a WEBP

Desde la carpeta donde está convertir_imagen.py, ejecuta:

for %i in (input\*.png) do python convertir_imagen.py "%i" webp output

✔️ 2. Convertir TODOS los .jpg a PNG
for %i in (input\*.jpg) do python convertir_imagen.py "%i" png output

✔️ 3. Convertir TODO lo que haya (cualquier extensión conocida*)

Esto sirve si tienes .jpg, .png, .webp, .jpeg, etc.:

for %i in (input\*.*) do python convertir_imagen.py "%i" webp output


Puedes cambiar webp por png, ico, jpg, etc.

✔️ 4. Convertir TODO a ICO
for %i in (input\*.*) do python convertir_imagen.py "%i" ico output

✔️ 5. Convertir todos los archivos de un tipo a otro tipo

Ejemplo: todos los .webp a .png:

for %i in (input\*.webp) do python convertir_imagen.py "%i" png output
