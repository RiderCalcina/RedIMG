from PIL import Image, ImageOps
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import webbrowser  # Importar módulo para abrir enlaces web

def corregir_orientacion(img):
    """
    Corrige la orientación de la imagen basándose en los metadatos EXIF.
    """
    try:
        # Verificar si la imagen tiene metadatos EXIF
        exif = img._getexif()
        if exif is not None:
            # Obtener el valor de orientación (etiqueta 274)
            orientacion = exif.get(274)
            if orientacion == 3:
                img = img.rotate(180, expand=True)
            elif orientacion == 6:
                img = img.rotate(270, expand=True)
            elif orientacion == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass  # Si no hay metadatos EXIF o no se puede leer, ignorar el error
    return img

def redimensionar_imagenes(carpeta, barra_progreso, ventana):
    # Verificar si la carpeta existe
    if not os.path.exists(carpeta):
        messagebox.showerror("Error", f"La carpeta '{carpeta}' no existe.")
        return

    # Crear una lista de archivos de imagen en la carpeta
    formatos_soportados = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]
    imagenes = [archivo for archivo in os.listdir(carpeta) if os.path.splitext(archivo)[1].lower() in formatos_soportados]

    if not imagenes:
        messagebox.showinfo("Información", f"No se encontraron imágenes en la carpeta '{carpeta}'.")
        return

    # Obtener el nombre de la carpeta seleccionada
    nombre_carpeta = os.path.basename(carpeta)
    if not nombre_carpeta:
        nombre_carpeta = "imagenes"  # Nombre predeterminado si no se puede obtener el nombre de la carpeta

    # Configurar la barra de progreso
    barra_progreso["maximum"] = len(imagenes)
    barra_progreso["value"] = 0
    ventana.update_idletasks()

    # Contador de errores
    errores = 0

    # Procesar cada imagen
    for i, imagen in enumerate(imagenes, start=1):
        ruta_imagen = os.path.join(carpeta, imagen)
        try:
            with Image.open(ruta_imagen) as img:
                # Corregir la orientación de la imagen
                img = corregir_orientacion(img)

                # Redimensionar manteniendo la proporción
                ancho, alto = img.size
                lado_mayor = max(ancho, alto)
                if lado_mayor > 1500:
                    escala = 1500 / lado_mayor
                    nuevo_ancho = int(ancho * escala)
                    nuevo_alto = int(alto * escala)
                    img = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)

                # Guardar la imagen en formato JPG con calidad ajustada
                nombre_salida = f"{nombre_carpeta}_{i:03d}.jpg"
                ruta_salida = os.path.join(carpeta, nombre_salida)

                # Ajustar la calidad para que el tamaño sea menor a 700 KB
                calidad = 95
                while True:
                    img.save(ruta_salida, "JPEG", quality=calidad)
                    tamaño = os.path.getsize(ruta_salida)
                    if tamaño <= 700 * 1024:  # 700 KB en bytes
                        break
                    calidad -= 5
                    if calidad < 10:
                        messagebox.showwarning("Advertencia", f"No se pudo reducir el tamaño de '{nombre_salida}' por debajo de 700 KB.")
                        break  # Salir del bucle si la calidad es demasiado baja

                # Actualizar la barra de progreso
                barra_progreso["value"] = i
                ventana.update_idletasks()

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la imagen '{imagen}': {e}")
            errores += 1

    # Mostrar mensaje de finalización
    if errores == 0:
        messagebox.showinfo("Finalizado", "Todas las imágenes han sido redimensionadas.")
    else:
        messagebox.showwarning("Finalizado con errores", f"Se redimensionaron {len(imagenes) - errores} imágenes, pero {errores} fallaron.")

def seleccionar_carpeta(barra_progreso, ventana):
    carpeta = filedialog.askdirectory(title="Seleccione la carpeta con las imágenes")
    if carpeta:
        redimensionar_imagenes(carpeta, barra_progreso, ventana)
    else:
        messagebox.showinfo("Información", "No se seleccionó ninguna carpeta.")

def centrar_ventana(ventana):
    """
    Centra la ventana en la pantalla.
    """
    ventana.update_idletasks()  # Actualiza la geometría de la ventana
    ancho_ventana = ventana.winfo_width()  # Obtiene el ancho de la ventana
    alto_ventana = ventana.winfo_height()  # Obtiene el alto de la ventana
    ancho_pantalla = ventana.winfo_screenwidth()  # Obtiene el ancho de la pantalla
    alto_pantalla = ventana.winfo_screenheight()  # Obtiene el alto de la pantalla

    # Calcula la posición x e y para centrar la ventana
    x = (ancho_pantalla // 2) - (ancho_ventana // 2)
    y = (alto_pantalla // 2) - (alto_ventana // 2)

    # Establece la geometría de la ventana
    ventana.geometry(f"+{x}+{y}")

def abrir_enlace():
    """
    Abre el enlace en el navegador predeterminado.
    """
    webbrowser.open("https://soportetecnico.rf.gd/")

def mostrar_about(ventana_principal):
    """
    Muestra la ventana "ABOUT" con la descripción y el enlace.
    """
    about_window = tk.Toplevel()
    about_window.title("About")
    about_window.geometry("300x150")
    about_window.resizable(False, False)
    about_window.configure(bg="#2E2E2E")
    about_window.overrideredirect(True)  # Eliminar bordes de la ventana

    # Posicionar la ventana "ABOUT" al lado derecho de la ventana principal, con un pequeño margen
    x = ventana_principal.winfo_x() + ventana_principal.winfo_width() + 10  # Margen de 10 píxeles
    y = ventana_principal.winfo_y()
    about_window.geometry(f"+{x}+{y}")

    # Crear un botón de cierre (x) en la esquina inferior izquierda
    boton_cerrar = tk.Button(
        about_window,
        text="x",
        command=about_window.destroy,
        bg="#FF0000",  # Color rojo llamativo
        fg="#FFFFFF",
        font=("Arial", 10, "bold"),
        bd=0,
        relief=tk.FLAT
    )
    boton_cerrar.place(relx=0.0, rely=1.0, anchor="sw", x=5, y=-5)

    # Crear un mensaje adicional en la ventana "ABOUT" (justificado)
    mensaje = tk.Label(
        about_window,
        text="\n(RedIMG Versión 1.0)\n\nEs una herramienta diseñada para redimensionar y optimizar \nimágenes por lotes de manera rápida y eficiente. \nConvierte tus imágenes a un tamaño adecuado para compartir,\nmanteniendo la calidad y reduciendo el espacio de \nalmacenamiento.",
        bg="#2E2E2E",
        fg="#FFFFFF",
        font=("Arial", 7),  # Reducir el tamaño de la fuente
        justify="left"  # Justificar el texto a la izquierda
    )
    mensaje.pack(pady=10, padx=10, anchor="w")

    # Crear un enlace "RedIMG" en la esquina inferior derecha
    enlace = tk.Label(
        about_window,
        text="RedIMG",
        bg="#2E2E2E",
        fg="#00BFFF",  # Color del enlace
        font=("Arial", 7, "underline"),
        cursor="hand2"  # Cambiar el cursor a una mano al pasar sobre el enlace
    )
    enlace.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
    enlace.bind("<Button-1>", lambda e: abrir_enlace())  # Abrir enlace al hacer clic

def main():
    # Crear la ventana principal
    ventana = tk.Tk()
    ventana.title("RedIMG")  # Título de la ventana
    ventana.geometry("300x120")  # Redimensionar la ventana principal para optimizar espacios
    ventana.resizable(False, False)  # Deshabilitar maximizar y minimizar
    ventana.configure(bg="#2E2E2E")  # Fondo oscuro

    # Centrar la ventana en la pantalla
    centrar_ventana(ventana)

    # Estilo para la barra de progreso
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("TProgressbar", background="#00BFFF", troughcolor="#4B4B4B", bordercolor="#2E2E2E", lightcolor="#00BFFF", darkcolor="#00BFFF")

    # Crear una barra de progreso
    barra_progreso = ttk.Progressbar(ventana, orient="horizontal", length=250, mode="determinate", style="TProgressbar")
    barra_progreso.pack(pady=10)

    # Crear un botón para seleccionar la carpeta
    boton_seleccionar = tk.Button(ventana, text="Seleccionar carpeta", command=lambda: seleccionar_carpeta(barra_progreso, ventana), bg="#4B4B4B", fg="#FFFFFF", font=("Arial", 10))
    boton_seleccionar.pack(pady=5)

    # Crear un botón "ABOUT" en la esquina inferior derecha
    boton_about = tk.Button(ventana, text="ABOUT", command=lambda: mostrar_about(ventana), bg="#4B4B4B", fg="#FFFFFF", font=("Arial", 8), bd=0)
    boton_about.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    # Iniciar el bucle de la interfaz gráfica
    ventana.mainloop()

if __name__ == "__main__":
    main()