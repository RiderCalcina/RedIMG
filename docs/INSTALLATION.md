# Guía de Instalación - RedIMG v3.5.3

Esta guía describe los pasos necesarios para configurar el entorno de ejecución de RedIMG desde el código fuente.

## 📋 Requisitos Previos
- **Python 3.8 o superior** (Recomendado: Python 3.12).
- **Entorno Windows** (Para compatibilidad con `iconbitmap`).

## ⚙️ Dependencias
RedIMG utiliza tres librerías externas clave. Puedes instalarlas ejecutando:

```python
pip install Pillow customtkinter
```

### Detalles de las Librerías:
- **Pillow**: El motor de procesamiento de imágenes.
- **CustomTkinter**: Para la interfaz gráfica moderna.
- **Tkinter**: (Viene incluido por defecto con Python en la mayoría de las instalaciones).

## 🚀 Cómo Ejecutar
1.  Asegúrate de tener el archivo `RedIMG-v3.0.py` y `RedIMG.ico` en la misma carpeta.
2.  Abre una terminal en ese directorio.
3.  Ejecuta el comando:
    ```bash
    python RedIMG-v3.0.py
    ```

## 🛠️ Solución de Problemas
- **Falta el Icono**: Si la app no inicia, verifica que `RedIMG.ico` esté presente. He incluido un bloque `try-except` para que la app cargue sin icono si es necesario.
- **Error de Librerías**: Asegúrate de que `pip` esté actualizado (`python -m pip install --upgrade pip`) antes de instalar las dependencias.

---
Para usuarios que prefieran el ejecutable directo, consulte la **Guía de Compilación**.
