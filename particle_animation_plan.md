# Plan de ejecución para acelerar la animación de partículas en RedIMG

## Objetivo
Mejorar la fluidez de la animación de partículas (incrementar FPS) sin impactar el procesamiento de imágenes ni la UI principal.

## Estrategia
1. **Optimizar el dibujo**
   - **Culling**: eliminar partículas que están fuera del área visible.
   - **Uso de tags y `canvas.move`**: mover partículas existentes en lugar de crear/borrar cada frame.
   - **Representación ligera**: usar círculos pequeños o puntos en vez de imágenes complejas.
2. **Controlar la frecuencia de actualización**
   - Reducir el intervalo de actualización de `30 ms` a `20 ms` (≈ 50 fps).
   - Utilizar `root.after_idle` para programar la siguiente actualización cuando el bucle de eventos esté libre.
3. **Pre‑cálculo de trayectorias**
   - Generar al iniciar una lista de posiciones (x, y, velocidad) para cada partícula.
   - En cada tick, simplemente leer la siguiente posición en la lista.
4. **Separar cálculo y renderizado**
   - Crear un hilo dedicado al cálculo de movimiento usando `threading.Thread` y `queue.Queue`.
   - El hilo principal solo consume la cola y actualiza el canvas, evitando bloqueos de la UI.
5. **Cachear recursos gráficos**
   - Cargar una única `PhotoImage` para la partícula y reutilizarla.
   - Habilitar scaling de Tkinter (`root.tk.call('tk', 'scaling', 1.0)`) para aprovechar aceleración de hardware cuando esté disponible.
6. **Perfilado y ajuste fino**
   - Medir el tiempo de cada ciclo con `time.perf_counter()`.
   - Ajustar número máximo de partículas (ej. 300) y el intervalo para mantener < 5 ms por frame.

## Pasos de implementación
| Paso | Acción | Responsable | Estimación | Comentario |
|------|--------|-------------|------------|------------|
| 1 | Implementar culling y mover partículas con tags en `Particle.update` | Dev UI | 1 día | Elimina partículas fuera de la ventana. |
| 2 | Cambiar intervalo a 20 ms y usar `after_idle` | Dev UI | 0.5 día | Mejora de fluidez. |
| 3 | Pre‑calcular trayectorias y almacenar en listas | Dev Backend | 1 día | Reduce cálculos en tiempo real. |
| 4 | Implementar hilo de cálculo con `queue.Queue` | Dev Backend | 1.5 días | Mantener UI libre. |
| 5 | Cachear `PhotoImage` y habilitar scaling | Dev UI | 0.5 día | Evita recargas de imágenes. |
| 6 | Añadir perfilado y pruebas de rendimiento | QA | 0.5 día | Verificar < 5 ms por frame. |

## Verificación
- Ejecutar la aplicación y medir FPS (≈ 50 fps) usando `time.perf_counter`.
- Confirmar que el tiempo de procesamiento de lotes de imágenes sigue < 200 ms.
- Realizar pruebas de estrés con 200‑300 partículas simultáneas.

## Riesgos y mitigaciones
- **Condiciones de carrera** al usar hilos → usar `queue.Queue` y actualizar UI solo en el hilo principal.
- **Aumento de memoria** por caché → limitar número máximo de partículas a 300.
- **Compatibilidad Windows** → probar en Windows 10/11 con diferentes DPI.

## Próximos pasos
1. Crear rama `feature/particle-performance`.
2. Implementar los cambios paso a paso.
3. Ejecutar pruebas locales y validar métricas.
4. Hacer merge a `main` tras revisión.
