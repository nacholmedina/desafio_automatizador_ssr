#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import platform
import re
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pyautogui

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("calc-automation")

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 1.5

VALID_TOKENS_RE = re.compile(r"^[0-9+\-*/.= ]+$")
WIN_TITLES = ["Calculadora", "Calculator"]
REQ_KEYS = list("0123456789") + ["+", "-", "*", "/", "=", ".", "C"]
MAPPING_FILE = "calc_mapping.json"

def normalize_ops(expr: str) -> str:
    return expr.replace("×", "*").replace("x", "*").replace("X", "*").replace("÷", "/")

def validate_expr(expr: str) -> str:
    expr = normalize_ops(expr).strip()
    if not expr:
        raise ValueError("Expresión vacía")
    if not VALID_TOKENS_RE.match(expr):
        raise ValueError("Caracteres no permitidos")
    if re.search(r"[+\-*/.]{2,}", expr.replace("..", ".")):
        raise ValueError("Secuencia inválida")
    if re.match(r"^[+*/]", expr):
        raise ValueError("No puede iniciar con + * /")
    return expr

def launch_calculator(timeout: float = 20.0):
    system = platform.system().lower()
    try:
        if system == "windows":
            subprocess.Popen(["calc.exe"], shell=False)
        elif system == "darwin":
            subprocess.Popen(["open", "-a", "Calculator"])
        else:
            from shutil import which
            for exe in ("gnome-calculator", "kcalc", "xcalc"):
                if which(exe):
                    subprocess.Popen([exe])
                    break
            else:
                raise RuntimeError("Calculadora no encontrada")
    except Exception as e:
        raise RuntimeError(f"Error al lanzar calculadora: {e}")
    time.sleep(0.4)
    t0 = time.time()
    while time.time() - t0 < timeout:
        return
    raise TimeoutError("Timeout de apertura")

def find_calc_window_rect(timeout: float = 8.0):
    import pygetwindow as gw
    import time

    t0 = time.time()
    while time.time() - t0 < timeout:
        wins = []
        for t in WIN_TITLES:
            try:
                wins.extend(gw.getWindowsWithTitle(t) or [])
            except Exception:
                pass

        # Filtramos: con título y no minimizada (isMinimized sí existe)
        wins = [w for w in wins if getattr(w, "title", "") and not getattr(w, "isMinimized", False)]

        if wins:
            w = wins[0]
            try:
                # Aseguramos que esté en pantalla y activa
                if getattr(w, "isMinimized", False):
                    w.restore()
                else:
                    try:
                        w.activate()
                    except Exception:
                        pass
            except Exception:
                pass

            # Devolvemos rect absoluto de la ventana
            return (int(w.left), int(w.top), int(w.width), int(w.height))

        time.sleep(0.2)

    # Fallback final: ventana activa
    try:
        w = gw.getActiveWindow()
        if w and getattr(w, "title", ""):
            return (int(w.left), int(w.top), int(w.width), int(w.height))
    except Exception:
        pass

    raise RuntimeError("No se encontró la ventana de Calculadora")

def maximize_calculator():
    system = platform.system().lower()
    try:
        if system == "windows":
            pyautogui.hotkey("alt", "space"); time.sleep(0.12); pyautogui.press("x")
        elif system == "darwin":
            pyautogui.hotkey("command", "control", "f")
        else:
            pyautogui.hotkey("alt", "f10")
    except Exception as e:
        log.error(f"Error al maximizar: {e}")

def load_mapping(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f) or {}
        return data
    except FileNotFoundError:
        return None
    except Exception as e:
        log.error(f"No se pudo leer {path}: {e}")
        return None

def save_mapping(path: str, mapping: dict):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        log.info(f"Mapa guardado en {path}")
    except Exception as e:
        log.error(f"No se pudo guardar {path}: {e}")

def trainer_build_mapping(win_rect: tuple, click_delay: float, countdown: float = 2.0):
    left, top, _, _ = win_rect
    mapping = {}
    pyautogui.alert("Modo TRAINER: la calculadora debe estar visible. Vas a posicionar el mouse sobre cada botón que se te pida. Apretá OK para empezar.")
    for key in REQ_KEYS:
        pyautogui.alert(f"Dejá el mouse sobre el botón '{key}' y apretá OK.\nSe capturará en {countdown:.1f}s.")
        t0 = time.time()
        while time.time() - t0 < countdown:
            time.sleep(0.05)
        x, y = pyautogui.position()
        rx, ry = x - left, y - top
        mapping[key] = {"rx": rx, "ry": ry}
        log.info(f"Capturado '{key}' → abs=({x},{y}) rel=({rx},{ry})")
        pyautogui.click(x, y); time.sleep(click_delay)
    return mapping

def click_key(win_rect: tuple, mapping: dict, key: str, click_delay: float):
    left, top, _, _ = win_rect
    data = mapping.get(key)
    if not data:
        raise KeyError(f"Sin coordenadas para '{key}'")
    x, y = left + int(data["rx"]), top + int(data["ry"])
    log.info(f"Click '{key}' → ({x},{y}) rel=({data['rx']},{data['ry']})")
    pyautogui.click(x, y)
    if click_delay > 0:
        time.sleep(click_delay)

def exec_with_pyautogui(expr: str, win_rect: tuple, mapping: dict, click_delay: float):
    for ch in expr:
        if ch == " ":
            continue
        if ch in mapping:
            click_key(win_rect, mapping, ch, click_delay)
        else:
            log.warning(f"Fallback tipeo '{ch}'")
            pyautogui.typewrite(ch, interval=max(0.02, click_delay))

def take_screenshot(path: str | None = None) -> str:
    if not path:
        Path("outputs").mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = f"outputs/result-{ts}.png"
    shot = pyautogui.screenshot()
    shot.save(path)
    return path

def close_calculator():
    system = platform.system().lower()
    try:
        if system == "darwin":
            pyautogui.hotkey("command", "q")
        else:
            pyautogui.hotkey("alt", "f4")
    except Exception as e:
        log.error(f"Error cerrando: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expr", default="123+456=", help="Expresión base")
    parser.add_argument("--append", default="", help="Expresión a anexar")
    parser.add_argument("--delay", type=float, default=0.8)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--screenshot", default=None)
    parser.add_argument("--mapping", default=MAPPING_FILE)
    parser.add_argument("--click-delay", type=float, default=0.4)
    args = parser.parse_args()
    try:
        base = validate_expr(args.expr)
        add = args.append.strip()
        if add:
            add = validate_expr(add)
        final_expr = normalize_ops((base + " " + add).strip())
        if not final_expr.endswith("="):
            final_expr += "="
    except Exception as e:
        log.error(f"Expresión inválida: {e}")
        sys.exit(1)
    try:
        launch_calculator(timeout=args.timeout)
        time.sleep(0.5)
        maximize_calculator()
        time.sleep(args.delay)
        win_rect = find_calc_window_rect(timeout=8.0)
        mapping = load_mapping(args.mapping)
        if mapping is None or any(k not in mapping for k in REQ_KEYS):
            log.info("No hay mapeo o está incompleto. Iniciando trainer.")
            mapping = trainer_build_mapping(win_rect, args.click_delay, countdown=2.0)
            save_mapping(args.mapping, mapping)
        if "C" in mapping:
            try:
                click_key(win_rect, mapping, "C", args.click_delay)
            except Exception as e:
                log.warning(f"No se pudo presionar 'C': {e}")
        exec_with_pyautogui(final_expr, win_rect, mapping, args.click_delay)
        time.sleep(0.5)
        out = take_screenshot(args.screenshot)
        log.info(f"OK → Expresión ejecutada: {final_expr} | Captura: {out}")
    except Exception as e:
        log.error(f"Fallo general: {e}")
        sys.exit(1)
    finally:
        time.sleep(0.4)
        close_calculator()

if __name__ == "__main__":
    main()
