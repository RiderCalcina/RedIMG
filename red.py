from PIL import Image, ImageOps
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import webbrowser

def corregir_orientacion(img):
    try:
        exif = img._getexif()
        if exif is not None:
            orientacion = exif.get(274)
            if orientacion == 3:
                img = img.rotate(180, expand=True)
            elif orientacion == 6:
                img = img.rotate(270, expand=True)
            elif orientacion == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img

def redimensionar_imagenes(carpeta, barra_progreso, ventana):
    if not os.path.exists(carpeta):
        messagebox.showerror("Error", f"La carpeta '{carpeta}' no existe.")
        return

    formatos_soportados = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]
    imagenes = [archivo for archivo in os.listdir(carpeta) if os.path.splitext(archivo)[1].lower() in formatos_soportados]

    if not imagenes:
        messagebox.showinfo("Información", f"No se encontraron imágenes en la carpeta '{carpeta}'.")
        return

    nombre_carpeta = os.path.basename(carpeta)
    if not nombre_carpeta:
        nombre_carpeta = "imagenes"

    barra_progreso["maximum"] = len(imagenes)
    barra_progreso["value"] = 0
    ventana.update_idletasks()

    errores = 0

    for i, imagen in enumerate(imagenes, start=1):
        ruta_imagen = os.path.join(carpeta, imagen)
        try:
            with Image.open(ruta_imagen) as img:
                img = corregir_orientacion(img)

                ancho, alto = img.size
                lado_mayor = max(ancho, alto)
                if lado_mayor > 1500:
                    escala = 1500 / lado_mayor
                    nuevo_ancho = int(ancho * escala)
                    nuevo_alto = int(alto * escala)
                    img = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)

                nombre_salida = f"{nombre_carpeta}_{i:03d}.jpg"
                ruta_salida = os.path.join(carpeta, nombre_salida)

                calidad = 95
                while True:
                    img.save(ruta_salida, "JPEG", quality=calidad)
                    tamaño = os.path.getsize(ruta_salida)
                    if tamaño <= 700 * 1024:
                        break
                    calidad -= 5
                    if calidad < 10:
                        messagebox.showwarning("Advertencia", f"No se pudo reducir el tamaño de '{nombre_salida}' por debajo de 700 KB.")
                        break

                barra_progreso["value"] = i
                ventana.update_idletasks()

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la imagen '{imagen}': {e}")
            errores += 1

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
    ventana.update_idletasks()
    ancho_ventana = ventana.winfo_width()
    alto_ventana = ventana.winfo_height()
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho_ventana // 2)
    y = (alto_pantalla // 2) - (alto_ventana // 2)
    ventana.geometry(f"+{x}+{y}")

def abrir_enlace():
    webbrowser.open("https://soportetecnico.rf.gd/")

def mostrar_about(ventana_principal):
    about_window = tk.Toplevel()
    about_window.title("About")
    about_window.geometry("300x150")
    about_window.resizable(False, False)
    about_window.configure(bg="#2E2E2E")
    about_window.overrideredirect(True)

    x = ventana_principal.winfo_x() + ventana_principal.winfo_width() + 10
    y = ventana_principal.winfo_y()
    about_window.geometry(f"+{x}+{y}")

    boton_cerrar = tk.Button(
        about_window,
        text="x",
        command=about_window.destroy,
        bg="#FF0000",
        fg="#FFFFFF",
        font=("Arial", 10, "bold"),
        bd=0,
        relief=tk.FLAT
    )
    boton_cerrar.place(relx=0.0, rely=1.0, anchor="sw", x=5, y=-5)

    mensaje = tk.Label(
        about_window,
        text="\n(RedIMG Versión 1.0)\n\nEs una herramienta diseñada para redimensionar y optimizar \nimágenes por lotes de manera rápida y eficiente. \nConvierte tus imágenes a un tamaño adecuado para compartir,\nmanteniendo la calidad y reduciendo el espacio de \nalmacenamiento.",
        bg="#2E2E2E",
        fg="#FFFFFF",
        font=("Arial", 7),
        justify="left"
    )
    mensaje.pack(pady=10, padx=10, anchor="w")

    enlace = tk.Label(
        about_window,
        text="RedIMG",
        bg="#2E2E2E",
        fg="#00BFFF",
        font=("Arial", 7, "underline"),
        cursor="hand2"
    )
    enlace.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
    enlace.bind("<Button-1>", lambda e: abrir_enlace())

def main():
    ventana = tk.Tk()
    ventana.title("RedIMG")
    ventana.geometry("300x120")
    ventana.resizable(False, False)
    ventana.configure(bg="#2E2E2E")

    centrar_ventana(ventana)

    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("TProgressbar", background="#00BFFF", troughcolor="#4B4B4B", bordercolor="#2E2E2E", lightcolor="#00BFFF", darkcolor="#00BFFF")

    barra_progreso = ttk.Progressbar(ventana, orient="horizontal", length=250, mode="determinate", style="TProgressbar")
    barra_progreso.pack(pady=10)

    boton_seleccionar = tk.Button(ventana, text="Seleccionar carpeta", command=lambda: seleccionar_carpeta(barra_progreso, ventana), bg="#4B4B4B", fg="#FFFFFF", font=("Arial", 10))
    boton_seleccionar.pack(pady=5)

    boton_about = tk.Button(ventana, text="ABOUT", command=lambda: mostrar_about(ventana), bg="#4B4B4B", fg="#FFFFFF", font=("Arial", 8), bd=0)
    boton_about.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    ventana.mainloop()

if __name__ == "__main__":
    main()