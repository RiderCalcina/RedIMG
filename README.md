# RedIMG 📸 - Optimizador de Imágenes Oficial

![Versión](https://img.shields.io/badge/Versión-3.6.1-FF1A55?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-00FF99?style=for-the-badge&logo=python)
![Plataforma](https://img.shields.io/badge/Plataforma-Windows-00CCFF?style=for-the-badge&logo=windows)

![RedIMG](RedIMG.jpg)

**RedIMG** es una herramienta de escritorio diseñada para la optimización masiva de imágenes. Enfocada en la velocidad, permite procesar cientos de fotos en segundos, ajustando su tamaño y peso para su uso en la web o para compartir rápidamente sin perder nitidez.

---

## ✨ Características Principales

- **🚀 Procesamiento Ultrarrápido**: Utiliza procesamiento paralelo (multihilo) para aprovechar al máximo todos los núcleos de tu procesador.
- **📉 Optimización Inteligente**: Algoritmo de búsqueda binaria que ajusta la calidad de la imagen hasta alcanzar el peso exacto (KB) deseado.
- **🎨 Salida Universal JPG**: Genera archivos compatibles con todos los dispositivos y plataformas.
- **📂 Soporte Multiformato**: Procesa formatos estándar (JPG, PNG, WebP) y profesionales (RAW de cámaras Canon, Nikon, Sony, además de HEIC/HEIF de iPhone).
- **🔳 Interfaz Minimalista**: Diseño ligero con soporte para arrastrar y soltar (Drag & Drop).
- **⚙️ Configuración Precisa**: Elige entre perfiles de peso preestablecidos (780KB, 1MB, 2MB) o simplemente convierte sin límite de peso.

---

## 🛠️ Instalación y Requisitos

Para ejecutar el código fuente, asegúrate de tener instalado **Python 3.8 o superior**.

### 1. Clonar el proyecto
```bash
git clone https://github.com/RiderCalcina/RedIMG.git
cd RedIMG
```

### 2. Instalar dependencias
```bash
pip install pillow ttkbootstrap pillow-heif rawpy pillow-avif-plugin windnd
```

*Nota: `rawpy` y `pillow-heif` son opcionales pero necesarios para soportar fotos de cámaras profesionales e iPhones.*

---

## 🚀 Modo de Uso

1. **Ejecutar el programa**:
   ```bash
   python RedIMG.py
   ```
2. **Arrastrar Imágenes**: Simplemente arrastra una imagen o una carpeta entera directamente a la interfaz.
3. **Configurar el peso**: Haz clic en el icono del engranaje (⚙️) para elegir el peso máximo de salida.
4. **Resultados**: El programa creará automáticamente una carpeta llamada `Nombre_RedIMG` junto a tus fotos originales con los archivos procesados.

---

## 🏎️ Optimizaciones Técnicas

RedIMG ha sido refinado para el máximo rendimiento:
- **Algoritmo de Redimensionamiento**: Implementa `BICUBIC` en lugar de Lanczos, logrando una velocidad entre 30% y 50% mayor con una diferencia visual imperceptible.
- **Búsqueda de Peso**: Reducido a 4 iteraciones de guardado para garantizar el cumplimiento del tamaño objetivo en tiempo récord.
- **Concurrencia**: Escala automáticamente hasta 20 hilos de ejecución según la potencia del equipo detectada.

---

## 📄 Licencia y Créditos

Desarrollado por **Rider Calcina**.  
Este proyecto es de código abierto y está diseñado para ser ligero, portátil.

