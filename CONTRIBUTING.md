# Contribuir

¡Gracias por tu interés en el proyecto! Cualquier aporte, por pequeño que sea, se agradece un montón.

## Soporte para tu modelo

Si tienes una ASUS TUF/ROG y notas que se comporta diferente a lo esperado, nos ayuda mucho que compartas información:

1. Ejecuta estos comandos y guarda la salida:
```bash
   asusctl --version
   asusctl aura --help
   asusctl -s
```
2. Abre un issue indicando el modelo exacto de tu equipo y pega la salida de esos comandos.
3. Si puedes ir un paso más allá, un PR agregando tu configuración a `config.example.json` ayuda a que el proyecto soporte más modelos con el tiempo.

## Guía de código

Para mantener el proyecto simple y fácil de mantener, seguimos estas reglas:

- **Sin dependencias externas.** Es una decisión intencional, no un descuido.
- **Separación de responsabilidades:** la UI nunca llama a `subprocess` directamente; toda la interacción con el sistema pasa por `backend.py`.
- **Antes de abrir un PR**, verifica que el código compile correctamente:
```bash
  python3 -m py_compile tuf_aura_control/*.py
```
- **Documentación de efectos:** si agregas un nuevo efecto de iluminación, indica si es nativo del hardware o emulado por software. Esto ayuda a quienes usan el proyecto a entender qué esperar de cada uno.

## Ideas para contribuir

Si buscas por dónde empezar, aquí hay algunas ideas pendientes:

- Regla de udev para permitir el fallback de brillo sin necesidad de root.
- Detección automática de modelo.
- Persistencia del último color seleccionado entre reinicios.
- Empaquetado para AUR / COPR / Flatpak.
- Suite de pruebas (todavía no existe ninguna, así que cualquier aporte aquí es especialmente valioso).

## Código de conducta

Este es un proyecto de hobby, mantenido en tiempo libre. No hay obligación de nadie de responder rápido, arreglar algo puntual o aceptar cada propuesta, pero sí el compromiso de tratar a todos con respeto. Pedimos lo mismo de quienes participen.