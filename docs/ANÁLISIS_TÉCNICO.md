# Análisis Técnico: RedIMG v3.5.3 "Quality & Speed Pro"

Este documento detalla la arquitectura avanzada y las optimizaciones de ingeniería implementadas en la versión 3.5.0.

## 1. Arquitectura de Concurrencia (Parallel Processing)
RedIMG ha evolucionado de un modelo monohilo de procesamiento a una arquitectura de paralelismo real:

- **ThreadPoolExecutor**: Utiliza un pool de hilos para procesar hasta 4 imágenes simultáneamente. Esto aprovecha los procesadores multi-núcleo modernos, reduciendo el tiempo total de procesamiento en lotes grandes hasta en un 70%.
- **Gestión de Cola (Safe UI Thread)**: La comunicación entre los hilos de trabajo y la interfaz se realiza a través de `queue.Queue`. El hilo principal consulta esta cola cada 30ms para actualizar la barra de progreso de forma fluida.
- **Arranque Diferido**: Las animaciones y procesos secundarios se inician con un delay controlado para garantizar un arranque limpio y sin picos de CPU.

## 2. Motor de Optimización Binaria
La innovación principal de esta versión es el reemplazo del bucle lineal por un algoritmo de búsqueda binaria para la calidad:

- **Eficiencia O(log N)**: En lugar de probar calidades una a una, el motor realiza una búsqueda binaria entre los valores 10 y 90. Esto reduce drásticamente el número de operaciones de escritura en disco necesarias para encontrar la optimización ideal.
- **Target Dinámico**: El objetivo ahora es de **780 KB** con una resolución máxima de **1600px**, ajustado para ofrecer una excelente relación nitidez/peso en pantallas de alta densidad.
- **Muestreo de Color 4:2:0**: Optimiza el almacenamiento de información de color para reducir el peso sin pérdida perceptible de calidad visual.

### Manejo de Orientación y Formato
- **EXIF Tag 274**: Corrige automáticamente la rotación para que las imágenes verticales se mantengan así tras el proceso.
- **Fondo Sólido**: Al exportar a JPEG, las imágenes con transparencia se combinan automáticamente con un fondo blanco para evitar artefactos visuales o fondos negros.

## 3. Interfaz de Usuario (ttkbootstrap)
La migración a `ttkbootstrap` proporciona una base sólida para componentes modernos:

- **Botón ABOUT de Micro-Contraste**: Implementación de un `ttk.Button` con fuente de 5pt y estilo personalizado para máxima discreción y contraste seguro.
- **Arranque "Stealth" (Sin Destellos)**: Uso coordinado de `root.withdraw()` y `root.deiconify()` para asegurar que la aplicación solo sea visible una vez que el tema oscuro y los colores de sistema se han aplicado por completo.
- **Aprovisionamiento Espacial**: Ajuste del área de canvas a 129px para una barra de progreso integrada de forma más natural.
- **Polling de Alta Frecuencia**: El despachador de cola funciona a 30ms, permitiendo que la interfaz se sienta inmediata y reactiva.

## 4. Sistema de Animación y Memoria
Se han realizado mejoras críticas en la estabilidad del sistema:

- **Fix de Memory Corruption**: Corrección del error `alloc: invalid block` mediante la pre-asignación de recursos en el sistema de partículas y una gestión más estricta de los buffers de `Pillow`.
- **Pre-asignación de Partículas**: Las partículas se crean y configuran antes del primer renderizado, eliminando los lags iniciales.
- **Object Pooling**: Reutilización constante de objetos `Particle` para minimizar el impacto del recolector de basura (GC).
- **Control de FPS**: Ciclo de animación estabilizado a 80ms (~12 FPS para partículas de fondo) para mantener el uso de CPU por debajo del 1% en reposo.

---
*Documento Técnico Actualizado al 27 de febrero de 2026.*
