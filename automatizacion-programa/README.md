# Automatización de la Calculadora (Challenge AIT)

Este proyecto automatiza la aplicación de **Calculadora** usando **PyAutoGUI**.  
El script abre la calculadora, la maximiza, mapea los botones con PyAutoGUI la primera vez y luego ejecuta cálculos haciendo clicks reales.  
Si no hay teclas mapeadas, escribe con el teclado como fallback para asegurar la ejecución.

---

## ¿Qué hace?

1. Abre y maximiza la Calculadora.  
2. Valida la expresión a calcular (solo dígitos y `+ - * / . =`).  
3. Usa `calc_mapping.json` si existe para clickear los botones con PyAutoGUI.  
4. Si no existe o faltan teclas, entra en **modo trainer**: te pide posicionar el mouse sobre cada tecla (`0–9`, `+`, `-`, `*`, `/`, `.`, `=`, `C`) y guarda las coordenadas en el JSON.  
5. Ejecuta el cálculo y cierra la calculadora.  
6. Si alguna tecla no está mapeada, la escribe por teclado y deja un log `[FALLBACK]`.

---

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

`requirements.txt` incluye:

```
pyautogui==0.9.54
pillow>=10.0.0
pygetwindow>=0.0.9
```

---

## Uso

Ejemplo básico:

```bash
python main.py --expr "123+456="
```

Con delay entre clicks (para la demo):

```bash
python main.py --expr "789*456" --click-delay 0.6
```

Anexando otra operación:

```bash
python main.py --expr "100/4" --append "+5="
```

Parámetros principales:
- `--expr`: cálculo base (ej. `"123+456="`).  
- `--append`: operación extra (ej. `"+5="`).  
- `--click-delay`: segundos entre clicks (ej. `0.6`).  
- `--mapping`: ruta al JSON de mapeo (`calc_mapping.json` por defecto).

---

## Si no hay teclas mapeadas

- Primera ejecución sin JSON → entra en modo trainer.  
- Vas posicionando el mouse sobre cada tecla cuando el programa lo pida.  
- Se guardan las posiciones relativas en `calc_mapping.json`.  
- Desde la segunda vez ya no hay que remapear.  
- Si falta alguna tecla, se usa fallback con `pyautogui.typewrite`.

---

## Video de demostración

En el video de entrega se ve:  
1. El mapeo de la última tecla en modo trainer.  
2. La ejecución final del cálculo con clicks visibles (`--click-delay`).  


---

## Archivos

- `main.py`: script principal.  
- `requirements.txt`: dependencias.  
- `calc_mapping.json`: archivo con coordenadas mapeadas.  
