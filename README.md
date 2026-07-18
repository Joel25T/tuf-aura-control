# TUF Aura Control

Panel de control RGB para laptops ASUS TUF/ROG en Linux. Funciona sobre
[asusctl](https://gitlab.com/asus-linux/asusctl) como capa de control.

Desarrollado originalmente para una TUF Gaming A16 (FA607NUG) en Fedora, pero
debería funcionar en otros modelos con cambios mínimos de configuración.

## El problema

La mayoría de las tarjetas TUF solo soportan iluminación **monozona** a nivel de firmware: aceptan el modo `static` y nada más. Efectos como breathing o rainbow suelen devolver un error de `NotSupported`.

Para resolver esto:

- El único modo soportado nativamente por el hardware es el color estático.
- Los efectos animados (como el ciclo de color) se emulan por software, reaplicando `static` con distintos colores dentro de un loop continuo.

## Requisitos

- Linux con `asusctl` y `asusd` activos (se recomienda una versión reciente).
- Python 3.8 o superior.
- Tkinter (`python3-tkinter` en Fedora, `python3-tk` en Debian/Ubuntu).

Sin dependencias externas de PyPI.

## Instalación

Puedes instalarlo localmente para tu usuario:

```bash
git clone https://github.com/Joel25T/tuf-aura-control.git
cd tuf-aura-control
pip install --user .
```