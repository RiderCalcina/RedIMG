# Changelog - RedIMG

## v3.5.3 "Quality & Speed Pro - Refined" (2026-02-27)
### 🛠️ Correcciones y Refinamientos
- **Fix Ventana de Archivos**: Se separó la lógica de `on_select_file` para evitar que el selector de archivos se abra automáticamente al finalizar un proceso de optimización.
- **Limpieza de Código**: Se eliminó la función obsoleta `mostrar_config` que ya no tenía uso en la interfaz.
- **Barra de Progreso Celeste**: Se ajustó el estilo de la barra de progreso (`bootstyle="info"`) para forzar un color celeste eléctrico puro (`#00FFFF`), mejorando el impacto visual.
- **Legibilidad en About**: Se oscureció el texto de la ventana modal "About" de blanco puro a un gris suave (`#B0B0B0`) para reducir la fatiga visual sobre el fondo negro.

## v3.5.2 "Quality & Speed Pro - Polish" (2026-02-09)
### 🎨 Refinamientos de UI/UX Finales
- **Ajuste de Simetría**: La ventana de la interfaz principal y la ventana "About" ahora comparten las mismas dimensiones (300x125/140) para una estética coherente.
- **Botón ABOUT Micro**: Rediseño del botón a un tamaño minúsculo y color oscuro con contraste optimizado para una integración total en el canvas.
- **Instructivo de Uso**: Inclusión de una guía breve ("Arrastra o haz clic") directamente en la ventana informativa.
- **Mejora de Etiquetas**: Clarificación en la interfaz para incluir explícitamente el soporte de carpetas.
- **Optimización de Color**: Establecimiento del color de acento a negro puro (#000000) para una experiencia visual más inmersiva.

## v3.5.1 (2026-02-09)
### 🎨 Refinamientos de UI y Correcciones
- **Fix de Doble Gatillo**: Se corrigió el error donde el clic en el enlace "ABOUT" activaba simultáneamente el selector de archivos.
- **Optimización de Arranque**: Implementación de la técnica `withdraw/deiconify` para eliminar el destello claro al inicio de la aplicación.
- **Posicionamiento de Ventana**: La ventana "About" ahora se posiciona inteligentemente a la derecha de la ventana principal.
- **Velocidad de Lluvia**: Incremento en la velocidad de caída de las partículas para una atmósfera más dinámica.

## v3.5.0 "Quality & Speed Pro" (2026-02-09)
### 🚀 Optimización Extrema y Rendimiento
- **Motor de Búsqueda Binaria**: Implementación de un algoritmo de búsqueda binaria (O(log N)) para encontrar la calidad exacta que cumpla con el peso objetivo (<780KB) de forma ultra-rápida.
- **Procesamiento en Paralelo (Multithreading)**: Ahora utiliza `ThreadPoolExecutor` con 4 núcleos en paralelo para procesar múltiples imágenes simultáneamente, reduciendo el tiempo de espera drásticamente.
- **Selección Múltiple "Individual"**: Soporte para seleccionar múltiples archivos de una vez en el modo individual.
- **Nomenclatura Automática Inteligente**: Evita conflictos de nombres y mejora la organización de los archivos generados.
- **Corrección Crítica de Memoria**: Solución al error `alloc: invalid block` mediante una gestión de recursos más eficiente y limpieza de buffers.
- **UI Ultra-Reactiva**: Polling de 30ms para la barra de progreso y optimización de frames para una respuesta inmediata.
- **Estética Pure Black**: Refinamiento visual con fondo negro absoluto (#000000) y tema `ttkbootstrap` Darkly.
- **Previa de Partículas**: Mejora en la fluidez de las animaciones con pre-asignación de capas estáticas.

## v3.1.2 (2026-02-09)
### 🎨 Refinamiento Estético
- **Migración a ttkbootstrap**: Uso del framework `ttkbootstrap` para componentes UI más modernos y profesionales.
- **Fondo Negro Puro**: Cambio del tema midnight navy a negro puro (#000000) para mayor contraste.
- **Ajuste de Dimensiones**: Aumento del límite de resolución inteligente de 1500px a 1600px.
- **Calidad de Salida**: Ajuste del peso objetivo a 780KB con submuestreo 4:2:0 para una fidelidad visual superior.

## v3.1.0 (2026-01-30)
### 🎨 Mejoras Visuales y de Rendimiento
- **Sistema de Animación de Partículas**: Implementación completa de un sistema de partículas de fondo con física realista (gravedad, rebotes, viento).
- **Tema Dark Black**: Migración a una paleta de colores ultra-oscura (#050505) para una experiencia visual premium.
- **Ventana About**: Nueva ventana modal informativa accesible desde el enlace "ABOUT" con detalles del proyecto y enlace web.
- **Optimización de Rendimiento**: 
  - Object pooling para reutilización de partículas (elimina creación/destrucción constante).
  - Límite de 150 partículas máximas para mantener bajo uso de CPU.
  - Frame rate optimizado a ~30 FPS para animaciones fluidas.
- **Pausado Inteligente**: Las animaciones se pausan automáticamente durante el procesamiento de imágenes para liberar recursos.
- **Botones en Canvas**: Renderizado de botones con fondos semi-transparentes directamente en canvas para mejor integración visual.
- **Checkbox WEBP Minimalista**: Diseño compacto y refinado del selector de formato.

## v3.1.1 (2026-01-29)
### ✨ Mejoras Visuales y Funcionales
- **Botones con Iconos**: Se reemplazaron los botones de texto por botones iconográficos (`galeria.png` y `imagen.png`).
- **Diseño Horizontal**: Los botones ahora se muestran uno al lado del otro (side-by-side) con espaciado simétrico.
- **Tooltips Inteligentes**: Implementación de una clase `CTKToolTip` personalizada que muestra información descriptiva sin obstruir los botones.

## v3.1.0 (2026-01-27)
### ✨ Mejoras de Interfaz (UX)
- **Selector de Formato Simplificado**: Se reemplazó el menú desplegable por un **Checkbox** intuitivo para activar WEBP.
- **Preferencia por Defecto**: La aplicación ahora inicia configurada para JPG, permitiendo activar WEBP con un solo clic.
- **Ajustes de Diseño**: Refinamiento de espaciados y fuentes para una mejor legibilidad.

---

## v3.0.0 "Modern Edition" (2026-01-27)
### 🚀 Salto Tecnológico
- **Migración a CustomTkinter**: Rediseño total de la interfaz con el tema **Midnight Navy**.
- **Implementación de Multithreading**: Integración de `threading` y `queue` para evitar que la aplicación se congele durante el procesamiento.
- **Soporte WEBP**: Introducción de la capacidad de exportar imágenes en formato WEBP de alta eficiencia.
- **Arquitectura de Clases**: Refactorización completa del código a una estructura orientada a objetos más mantenible.
- **Barra de Progreso Animada**: Visualización en tiempo real del avance de los procesos por lotes.

---

## v2.0.6 (Versión Base)
- Versión inicial en Tkinter estándar.
- Motor de optimización PIL básico.
- Redimensionamiento hasta 1500px.
- Salida exclusiva en Formato JPEG.
