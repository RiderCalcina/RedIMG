# Manual de Ayuda y Funciones - RedIMG v3.6.0

Bienvenido al manual de uso de RedIMG. A continuación, se detallan todas las funciones principales de la aplicación y cómo sacarles el máximo provecho.

## Interfaz Principal (Panel de Lluvia de Píxeles)

La ventana inicial es un panel asimétrico negro, libre de botones invasivos, diseñado para la máxima fluidez y rapidez.
* **Arrastrar y Soltar**: Puede tomar una imagen individual, cientos de imágenes o carpetas enteras y soltarlas encima de este panel negro. El programa las analizará al instante e iniciará el procesamiento.
* **Clic Manual**: Si prefiere buscar los archivos tradicionalmente, simplemente haga doble clic en cualquier punto del panel para abrir el explorador de archivos.
* **Sistema de Monitoreo**: Cuando empiece un trabajo, aparecerá una barra roja de progreso. Justo debajo verá la cantidad de imágenes procesadas y el **Tiempo Estimado (ETA)** restante.
* **Cancelar Trabajo**: Una vez que un proceso ha iniciado, dar un clic detendrá inmediatamente todos los motores en segundo plano y cancelará el progreso con total seguridad.

## Ventana de Configuración (⚙)

Al hacer clic en el engranaje inferior derecho, se despliega un panel de ajustes adherido a la ventana principal. Este guarda sus preferencias incluso si cierra la aplicación.

### Target Size (Límite de Peso)
La barra deslizadora permite elegir el peso máximo del archivo de salida. Esto es posible mediante el motor de **Búsqueda Binaria** y la **Redimensión Dinámica**:
* **780KB**: Comprime la imagen y la encoge a un máximo de `1600` píxeles para asegurar un peso mínimo. Ideal para correos electrónicos o web rápida.
* **1MB**: Mantiene una resolución generosa (hasta `2048` píxeles) e intenta comprimir hasta ajustarse al Mega.
* **2MB**: Destinado a fotografía de alta resolución (hasta `3072` píxeles), aplicando una compresión muy suave.
* **Sin Límite**: Apaga por completo el motor de reducción de dimensiones (`infinito`). La imagen conservará su enorme tamaño original y únicamente pasará por el proceso de conversión de formato y optimización de metadatos.

### Convertir a (Formato de Salida)
Al hacer clic en uno de estos botones verdes de alta visibilidad, todas las imágenes entrantes serán transformadas a dicho formato automáticamente:
* **JPG**: El clásico. Se guarda utilizando un modelo progresivo y submuestreo de crominancia 4:2:0 para mantener calidad y reducir el peso hasta un 50% extra.
* **PNG**: Se guarda mediante técnicas de compresión matemática a nivel 9 (`compress_level=9`). Si la imagen supera el tamaño objetivo (como 1MB), RedIMG empleará **Cuantización Inteligente**, reduciendo drásticamente la paleta de colores para disminuir su peso manteniéndose *Lossless* (Sin ruido).
* **WebP**: El estándar de la web moderna. Si no supera el peso límite se guarda de forma pura y *Lossless* (Sin pérdida de calidad). Si se ve forzado, aplica pequeñas iteraciones de compresión inteligente para encajar en el tamaño deseado.
* **AVIF**: Formato de compresión de ultra alta eficiencia de nueva generación. Requiere una ligera carga de CPU adicional, pero logra tamaños de archivo increíbles conservando el color. (Nota: Para reproducir AVIF, Windows podría requerir una extensión o usar un navegador moderno).

## Funciones Inteligentes Ocultas (Bajo el capó)

* **Preservación EXIF Automática**: Muchas fotos, especialmente de móviles Android y iPhones, están guardadas internamente de lado y usan un archivo de datos (EXIF) para decirle a las pantallas que las giren. RedIMG transpone físicamente los píxeles de todas estas imágenes para que al procesarlas siempre permanezcan derechas para siempre en cualquier dispositivo viejo o nuevo.
* **Soporte RAW / iPhone (HEIF)**: ¿Sacó una fotografía enorme con su cámara profesional Nikon (.nef), Canon (.cr2) o Sony (.arw)? ¿O se la pasaron desde un iPhone (.heic)? RedIMG tiene decodificadores incrustados para abrirlas y convertirlas directamente en lote sin instalar códecs externos.
* **Protección Anti-Sobreescritura**: RedIMG nunca borrará su foto original ni la reemplazará. El programa creará mágicamente una carpeta llamada `RedIMG/` en el mismo lugar donde estaban sus fotos y colocará las versiones procesadas ahí adentro. Si la foto ya existía, le añadirá un número automáticamente (`_1`, `_2`).
* **Multithreading Activo**: El procesamiento se divide en todos los procesadores físicos de la computadora al mismo tiempo, lo que significa que el proceso puede ser hasta 8 veces más rápido que programas convencionales, todo mientras la barra de progreso fluye a 30 FPS en su pantalla principal.
