# Historial de Versiones - RedIMG

## v3.6.0 "Advanced Format Pro" (Abril 2026)
* **NUEVO**: Soporte para formatos WebP, AVIF y PNG con interfaz de configuración avanzada.
* **NUEVO**: Escala dinámica de redimensión (la resolución de la imagen escala proporcionalmente según el límite de 780KB, 1MB o 2MB).
* **NUEVO**: Cuantización de color para PNG, permitiendo compresión de peso dinámico de forma lossless.
* **NUEVO**: Preservación nativa de la orientación de cámara usando transposición EXIF (ImageOps).
* **NUEVO**: Indicador de tiempo estimado restante (ETA) en la barra de progreso de la interfaz.
* **NUEVO**: Engranaje de configuración dinámico en la esquina inferior derecha con alineación perfecta e integración al diseño asimétrico.
* **NUEVO**: Soporte para imágenes de iPhone (HEIC/HEIF) a través de `pillow-heif`.
* **NUEVO**: Soporte nativo para lectura de fotos RAW (.cr2, .nef, .arw, .dng) a través de `rawpy`.
* **MEJORA**: Búsqueda binaria ampliada a 6 iteraciones con "failsafe" para nunca fallar al reducir la calidad más óptima.
* **MEJORA**: Color de barra de progreso actualizado al rojo-rosado oficial del logo (`#FF1A55`).
* **MEJORA**: Rediseño visual de las ventanas "About" y "Configuración" calculando alturas y ejes XY de Windows dinámicamente para lograr una experiencia sin bordes.

## v3.5.3 "Quality & Speed Pro - Refined" (Febrero 2026)
* **FIX**: Solucionado error donde se abría el selector de archivos al terminar el proceso.
* **MEJORA**: Texto de la ventana "About" oscurecido a un gris suave para mayor legibilidad.

## v3.5.0 "Quality & Speed Pro" (Febrero 2026)
* **NUEVO**: Motor de búsqueda binaria para calidad (Optimización exacta en ms).
* **NUEVO**: Procesamiento en paralelo (Multithreading con 4 núcleos) para máxima velocidad.
* **NUEVO**: Nomenclatura automática inteligente para evitar conflictos de archivos.
* **MEJORA**: Calidad visual superior (Ajuste 4:2:0 a 780KB y 1600px).
* **MEJORA**: UI ultra-reactiva (polling de 30ms para barra de progreso).
* **FIX**: Error `alloc: invalid block` corregido (optimización crítica de memoria).
* **MEJORA**: Motor de animación de partículas.

## v3.0.0 "Modern Edition" (Enero 2026)
* **NUEVO**: Migración total a CustomTkinter / ttkbootstrap.
* **NUEVO**: Soporte Drag and Drop (Arrastrar y soltar).
* **MEJORA**: Refactorización completa orientada a objetos.

## v2.0.6 (Versión Anterior)
* Versión inicial en Tkinter estándar con motor básico JPEG.
