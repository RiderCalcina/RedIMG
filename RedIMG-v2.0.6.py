import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import webbrowser
from PIL import Image
from io import BytesIO

def corregir_orientacion(img):
    try:
        exif = img._getexif()
        if exif:
            orient = exif.get(274)
            if orient == 3:
                img = img.rotate(180, expand=True)
            elif orient == 6:
                img = img.rotate(270, expand=True)
            elif orient == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img

def convertir_a_rgb_con_fondo_blanco(img):
    if img.mode in ("RGBA", "P", "LA"):
        fondo = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        elif img.mode == "LA":
            img = img.convert("RGBA")
        fondo.paste(img, mask=img.split()[-1])
        return fondo
    elif img.mode != "RGB":
        return img.convert("RGB")
    return img

def optimizar_y_guardar(img, ruta_salida):
    buffer = BytesIO()
    calidad = 95
    while calidad >= 10:
        buffer.seek(0)
        buffer.truncate()
        img.save(
            buffer,
            "JPEG",
            quality=calidad,
            optimize=True,
            progressive=True,
            subsampling="4:2:0"
        )
        if buffer.tell() <= 700 * 1024:
            break
        calidad -= 5
    else:
        buffer.seek(0)
        buffer.truncate()
        img.save(
            buffer,
            "JPEG",
            quality=10,
            optimize=True,
            progressive=False,
            subsampling="4:2:0"
        )
    with open(ruta_salida, "wb") as f:
        f.write(buffer.getvalue())

def procesar_imagen_individual(ruta_imagen, ventana):
    try:
        nombre_original = os.path.splitext(os.path.basename(ruta_imagen))[0]
        carpeta = os.path.dirname(ruta_imagen)
        ruta_salida = os.path.join(carpeta, f"{nombre_original}_RedIMG.jpg")

        with Image.open(ruta_imagen) as img_original:
            img = corregir_orientacion(img_original)
            ancho, alto = img.size
            if max(ancho, alto) > 1500:
                escala = 1500 / max(ancho, alto)
                nuevo_tam = (int(ancho * escala), int(alto * escala))
                img = img.resize(nuevo_tam, Image.Resampling.LANCZOS)
            img_rgb = convertir_a_rgb_con_fondo_blanco(img)
            optimizar_y_guardar(img_rgb, ruta_salida)

        messagebox.showinfo("Éxito", f"Imagen redimensionada como:\n{ruta_salida}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo redimensionar la imagen:\n{str(e)}")

def redimensionar_imagenes(carpeta, barra_progreso, ventana):
    if not os.path.exists(carpeta):
        messagebox.showerror("Error", "La carpeta no existe.")
        return

    formatos = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}
    archivos = [
        f for f in os.listdir(carpeta)
        if os.path.splitext(f)[1].lower() in formatos
    ]
    if not archivos:
        messagebox.showinfo("Información", "No hay imágenes compatibles en la carpeta.")
        return

    nombre_base = os.path.basename(carpeta) or "redimg"
    total = len(archivos)
    barra_progreso["maximum"] = total
    barra_progreso["value"] = 0
    errores = 0

    for i, archivo in enumerate(archivos, 1):
        ruta = os.path.join(carpeta, archivo)
        try:
            with Image.open(ruta) as img_original:
                img = corregir_orientacion(img_original)
                ancho, alto = img.size
                if max(ancho, alto) > 1500:
                    escala = 1500 / max(ancho, alto)
                    nuevo_tam = (int(ancho * escala), int(alto * escala))
                    img = img.resize(nuevo_tam, Image.Resampling.LANCZOS)
                img_rgb = convertir_a_rgb_con_fondo_blanco(img)
                salida = os.path.join(carpeta, f"{nombre_base}_{i:03d}.jpg")
                optimizar_y_guardar(img_rgb, salida)
            barra_progreso["value"] = i
            ventana.update_idletasks()
        except Exception as e:
            errores += 1
            messagebox.showerror("Error", f"Fallo al procesar {archivo}:\n{str(e)}")

    if errores == 0:
        messagebox.showinfo("Listo", f"Todas las {total} imágenes fueron redimensionas.")
    else:
        messagebox.showwarning("Completado", f"{total - errores} imágenes procesadas. {errores} fallaron.")

def seleccionar_carpeta(barra_progreso, ventana):
    carpeta = filedialog.askdirectory(title="Seleccionar carpeta con imágenes")
    if carpeta:
        redimensionar_imagenes(carpeta, barra_progreso, ventana)

def seleccionar_archivo(ventana):
    archivo = filedialog.askopenfilename(
        title="Seleccionar una imagen",
        filetypes=[
            ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
            ("Todos los archivos", "*.*")
        ]
    )
    if archivo:
        procesar_imagen_individual(archivo, ventana)

def centrar_ventana(ventana):
    ventana.update_idletasks()
    ancho = ventana.winfo_width()
    alto = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana.winfo_screenheight() // 2) - (alto // 2)
    ventana.geometry(f"+{x}+{y}")

def abrir_enlace():
    webbrowser.open("https://qwertyaserty.com/")

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
        font=("Arial", 8, "bold"),
        bd=0,
        relief=tk.FLAT
    )
    boton_cerrar.place(relx=0.0, rely=1.0, anchor="sw", x=5, y=-5)

    mensaje = tk.Label(
        about_window,
        text="RedIMG Versión 2.0.6\n\nEs una herramienta eficiente para redimensionar y optimizar \nimágenes de forma individual o por lotes. \n\nConvierte tus imágenes a un tamaño ideal para compartir,\nmanteniendo la calidad y reduciendo el espacio de \nalmacenamiento.",
        bg="#2E2E2E",
        fg="#FFFFFF",
        font=("Arial", 7),
        justify="left"
    )
    mensaje.pack(pady=10, padx=10, anchor="w")

    enlace = tk.Label(
        about_window,
        text="www.qwertyaserty.com",
        bg="#2E2E2E",
        fg="#00BFFF",
        font=("Arial", 8, "underline"),
        cursor="hand2"
    )
    enlace.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
    enlace.bind("<Button-1>", lambda e: abrir_enlace())

def main():
    ventana = tk.Tk()
    ventana.title("RedIMG")
    ventana.geometry("300x150")
    ventana.resizable(False, False)
    ventana.configure(bg="#2E2E2E")

    # Cargar icono
    try:
        ventana.iconbitmap("RedIMG.ico")
    except Exception:
        pass

    centrar_ventana(ventana)

    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("TProgressbar", background="#00BFFF", troughcolor="#4B4B4B", bordercolor="#2E2E2E", lightcolor="#00BFFF", darkcolor="#00BFFF")

    barra_progreso = ttk.Progressbar(ventana, orient="horizontal", length=250, mode="determinate", style="TProgressbar")
    barra_progreso.pack(pady=10)

    boton_carpeta = tk.Button(
        ventana,
        text="Redimensionar carpeta",
        command=lambda: seleccionar_carpeta(barra_progreso, ventana),
        bg="#4B4B4B",
        fg="#FFFFFF",
        font=("Arial", 10),
        width=20
    )
    boton_carpeta.pack(pady=(5, 2))

    boton_archivo = tk.Button(
        ventana,
        text="Redimensionar archivo",
        command=lambda: seleccionar_archivo(ventana),
        bg="#4B4B4B",
        fg="#FFFFFF",
        font=("Arial", 10),
        width=20
    )
    boton_archivo.pack(pady=(2, 5))

    texto_about = tk.Label(
        ventana,
        text="ABOUT",
        fg="#15FF00",
        font=("Arial", 5),
        cursor="hand2",
        bg="#2E2E2E"
    )
    texto_about.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
    texto_about.bind("<Button-1>", lambda e: mostrar_about(ventana))

    ventana.mainloop()

if __name__ == "__main__":
    main()