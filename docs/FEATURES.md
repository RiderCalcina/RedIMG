# Características de RedIMG v3.5.3 "Quality & Speed Pro"

RedIMG combina simplicidad con potencia técnica de nivel profesional. A continuación se enumeran todas las funciones clave disponibles.

## 🛠️ Capacidades de Procesamiento
- **Búsqueda Binaria de Calidad**: Motor optimizado que encuentra el punto exacto de compresión en milisegundos mediante búsqueda binaria (O(log N)).
- **Procesamiento en Paralelo (4 Núcleos)**: Utiliza multithreading real con `ThreadPoolExecutor` para procesar hasta 4 imágenes de forma simultánea.
- **Resolución Inteligente (1600px)**: Redimensiona automáticamente cualquier imagen que supere los 1600px en su lado más largo, manteniendo la proporción original para calidad retina.
- **Optimización de Peso (Target <780KB)**: Algoritmo refinado que busca el peso ideal (<780KB) con submuestreo croma 4:2:0.
- **Soporte Multiformato**: Lee JPG, JPEG, PNG, BMP, GIF, TIFF y WEBP.
- **Filtro de Transparencias**: Conversión inteligente de PNG/WEBP con transparencia a fondo blanco sólido.

## 🎨 Interfaz y Usabilidad
- **Diseño Pure Black Premium**: Estética minimalista con fondo y acento negro absoluto (#000000) basada en `ttkbootstrap`.
- **UI Ultra-Reactiva**: Interfaz con polling de 30ms para actualizaciones de estado fluidas y barra de progreso rediseñada en color celeste eléctrico.
- **Sistema de Animación de Partículas**: Fondo dinámico con partículas de colores que caen con física realista y velocidad optimizada.
- **Ventanas Simétricas**: Interfaz principal y modal About con dimensiones coherentes (300x129/140).
- **Botón ABOUT Mini**: Acceso discreto a la información mediante un micro-botón oscuro integrado.
- **Instructivo Express**: Guía de uso rápido integrada ("Arrastra o haz clic") en la sección informativa.
- **Drag & Drop de Carpetas e Imágenes**: Soporte explícito y visual para arrastrar archivos individuales o directorios completos.

## 📁 Gestión de Archivos
- **Nomenclatura Inteligente**: Renombrado secuencial (`RedIMG_001.jpg`) para lotes y sufijo `_RedIMG` para archivos individuales.
- **Selección Múltiple Individual**: Permite seleccionar y procesar varios archivos específicos sin necesidad de procesar una carpeta completa.
- **Seguridad de Archivos**: Nunca sobrescribe los archivos originales.

---
*RedIMG v3.5.3 - Rendimiento y calidad profesional al alcance de un clic.*
