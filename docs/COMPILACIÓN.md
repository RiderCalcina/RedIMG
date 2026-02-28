# Guía de Compilación - RedIMG v3.5.3

Para distribuir RedIMG como una aplicación independiente de Windows (.exe), se recomienda el uso de **Nuitka** por su eficiencia y protección de código.

## 🛠️ Preparación
Instala Nuitka mediante pip:
```bash
pip install -U nuitka
```

## 📦 Comando de Compilación Recomendado
Ejecuta el siguiente comando en la terminal desde el directorio del proyecto:

```bash
python -m nuitka --standalone --onefile --windows-disable-console --enable-plugin=tk-inter --include-data-file=RedIMG.ico=RedIMG.ico --windows-icon-from-ico=RedIMG.ico RedIMG-v3.0.py
```

### Explicación de Parámetros:
- `--standalone --onefile`: Crea un único archivo ejecutable que contiene todo lo necesario.
- `--windows-disable-console`: Evita que se abra una ventana negra de terminal al iniciar la app.
- `--enable-plugin=tk-inter`: Necesario para que CustomTkinter funcione correctamente.
- `--windows-icon-from-ico`: Incrusta el icono oficial en el archivo .exe.

## 📄 Resultado
Tras finalizar el proceso (puede tardar unos minutos), encontrarás el archivo `RedIMG-v3.0.exe` en la carpeta `dist` o en la carpeta raíz. Puedes distribuir este archivo sin necesidad de que el usuario final tenga Python o las librerías instaladas.

---
*Nota: Asegúrate de tener instalado un compilador de C++ (como Visual Studio o MinGW) para que Nuitka pueda trabajar.*
