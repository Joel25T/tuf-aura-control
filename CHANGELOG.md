# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [Sin publicar]

### Agregado
- Servicio de systemd para apagar el RGB automáticamente al apagar el equipo (`packaging/`).
- El ciclo de color ahora corre como proceso independiente y sobrevive al cierre de la GUI.
- La GUI detecta ciclos de color activos provenientes de sesiones anteriores.
- Nueva rueda de color HSV, con sliders en degradado y efecto de brillo pulsante en el swatch.
- Interruptor maestro (encendido/apagado general) en el sidebar.
- Tarjetas de la interfaz con esquinas redondeadas.

### Corregido
- El estado del ciclo ahora guarda el `boot_id` para evitar confundir PIDs entre reinicios.
- Se agregó verificación de `/proc/<pid>/cmdline` antes de enviar señales a un proceso.
- Control de brillo actualizado de `asusctl -k` a `asusctl leds set`, siguiendo la sintaxis actual de `asusctl`.

## [0.1.0] - 2026-07-16

### Agregado
- Primera versión del proyecto empaquetada como paquete de Python.
- Interfaz estilo Armoury Crate, con sidebar, color estático, control de brillo y ciclo de color.
- Configuración por usuario, guardada en `~/.config/tuf-aura-control/config.json`.
- Fallback vía sysfs para el control de brillo.

### Corregido
- Comando de color actualizado de `asusctl aura static` a `asusctl aura effect static`.