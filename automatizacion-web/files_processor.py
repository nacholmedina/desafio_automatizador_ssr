from __future__ import annotations
import re
from pathlib import Path
from datetime import datetime
import pandas as pd

DOWNLOAD_DIR = Path(__file__).parent / "downloads"

def _normalize_price_series(s: pd.Series) -> pd.Series:
    def _one(x):
        if pd.isna(x):
            return pd.NA
        x = str(x).strip()
        x = re.sub(r"[^\d,.\-]", "", x)
        if x.count(",") > 0 and x.count(".") > 0:
            if x.rfind(",") > x.rfind("."):
                x = x.replace(".", "")
                x = x.replace(",", ".")
            else:
                x = x.replace(",", "")
        elif x.count(",") > 0 and x.count(".") == 0:
            x = x.replace(",", ".")
        try:
            return float(x)
        except:
            return pd.NA
    out = s.map(_one)
    return pd.to_numeric(out, errors="coerce")

def _truncate_100(s: pd.Series) -> pd.Series:
    return s.fillna("").astype(str).str.strip().str.replace(r"\s+", " ", regex=True).str.slice(0, 100)

def _today_tag() -> str:
    return datetime.now().strftime("%Y%m%d")

def _save_xlsx(df: pd.DataFrame, proveedor: str, out_dir: str | Path | None = None) -> Path:
    out_dir = Path(out_dir) if out_dir else Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{proveedor}_{_today_tag()}.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        df.to_excel(xw, index=False)
    return path

def process_autorepuestos(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    try:
        df = pd.read_csv(p, sep=";", engine="python")
    except Exception:
        df = pd.read_csv(p, sep=",", engine="python")
    cols = {c.lower(): c for c in df.columns}
    codigo_col = cols.get("cod. articulo") or cols.get("cod. artículo") or cols.get("cod articulo") or cols.get("cod artículo") or cols.get("cod_articulo")
    if not codigo_col:
        codigo_col = cols.get("cod. fabrica") or cols.get("cod. fábrica") or cols.get("cod fabrica") or cols.get("cod fábrica")
    marca_col = cols.get("marca")
    descr_col = cols.get("descripcion") or cols.get("descripción")
    precio_col = cols.get("importe") or cols.get("precio")
    df_std = pd.DataFrame({
        "CODIGO": df[codigo_col] if codigo_col else pd.NA,
        "DESCRIPCION": df[descr_col] if descr_col else pd.NA,
        "MARCA": df[marca_col] if marca_col else pd.NA,
        "PRECIO": df[precio_col] if precio_col else pd.NA,
    })
    df_std["DESCRIPCION"] = _truncate_100(df_std["DESCRIPCION"])
    df_std["PRECIO"] = _normalize_price_series(df_std["PRECIO"])
    df_std = df_std.dropna(subset=["CODIGO", "PRECIO"]).reset_index(drop=True)
    return df_std

def process_mundo_repcar(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    df = pd.read_excel(p, header=10)
    df = df.rename(columns={c: c.strip().upper() for c in df.columns})
    df = df[["CODIGO PROVEEDOR", "DESCRIPCION", "RUBRO", "MARCA", "PRECIO DE LISTA"]].copy()
    df = df.dropna(subset=["CODIGO PROVEEDOR"])
    descr = (df["DESCRIPCION"].fillna("").astype(str).str.strip() + " - " + df["RUBRO"].fillna("").astype(str).str.strip()).str.strip(" -")
    df_std = pd.DataFrame({
        "CODIGO": df["CODIGO PROVEEDOR"],
        "DESCRIPCION": _truncate_100(descr),
        "MARCA": df["MARCA"],
        "PRECIO": _normalize_price_series(df["PRECIO DE LISTA"]),
    })
    df_std = df_std.dropna(subset=["CODIGO", "PRECIO"]).reset_index(drop=True)
    return df_std

def _extract_brand_from_filename(p: Path) -> str | None:
    m = re.search(r"_(.+?)_(\d{8}-\d{6})$", p.stem)
    if not m:
        return None
    brand = m.group(1).replace("_", " ").strip()
    return brand or None

def process_autofix(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    xls = pd.ExcelFile(p)
    frames = []
    for sheet in xls.sheet_names:
        tmp = pd.read_excel(xls, sheet_name=sheet)
        tmp = tmp.rename(columns={c: c.strip().upper() for c in tmp.columns})
        codigo_col = "CODIGO" if "CODIGO" in tmp.columns else None
        descr_col = "DESCR" if "DESCR" in tmp.columns else ("DESCRIPCION" if "DESCRIPCION" in tmp.columns else None)
        precio_col = "PRECIO" if "PRECIO" in tmp.columns else None
        if not (codigo_col and descr_col and precio_col):
            continue
        t = pd.DataFrame({
            "CODIGO": tmp[codigo_col],
            "DESCRIPCION": tmp[descr_col],
            "MARCA": sheet,
            "PRECIO": tmp[precio_col],
        })
        frames.append(t)
    if not frames:
        return pd.DataFrame(columns=["CODIGO", "DESCRIPCION", "MARCA", "PRECIO"])
    df = pd.concat(frames, ignore_index=True)
    df["DESCRIPCION"] = _truncate_100(df["DESCRIPCION"])
    df["PRECIO"] = _normalize_price_series(df["PRECIO"])
    df = df.dropna(subset=["CODIGO", "PRECIO"]).reset_index(drop=True)
    return df

def process_autofix_file_to_df(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    brand = _extract_brand_from_filename(p)
    xls = pd.ExcelFile(p)
    frames = []
    for sheet in xls.sheet_names:
        tmp = pd.read_excel(xls, sheet_name=sheet)
        tmp = tmp.rename(columns={c: c.strip().upper() for c in tmp.columns})
        codigo_col = "CODIGO" if "CODIGO" in tmp.columns else None
        descr_col = "DESCR" if "DESCR" in tmp.columns else ("DESCRIPCION" if "DESCRIPCION" in tmp.columns else None)
        precio_col = "PRECIO" if "PRECIO" in tmp.columns else None
        if not (codigo_col and descr_col and precio_col):
            continue
        t = pd.DataFrame({
            "CODIGO": tmp[codigo_col],
            "DESCRIPCION": tmp[descr_col],
            "MARCA": brand if brand else sheet,
            "PRECIO": tmp[precio_col],
        })
        frames.append(t)
    if not frames:
        return pd.DataFrame(columns=["CODIGO", "DESCRIPCION", "MARCA", "PRECIO"])
    df = pd.concat(frames, ignore_index=True)
    df["DESCRIPCION"] = _truncate_100(df["DESCRIPCION"])
    df["PRECIO"] = _normalize_price_series(df["PRECIO"])
    df = df.dropna(subset=["CODIGO", "PRECIO"]).reset_index(drop=True)
    return df

def process_file(path: str | Path, out_dir: str | Path | None = None) -> Path:
    p = Path(path)
    stem = p.stem.lower()
    if "autorepuestos" in stem:
        df = process_autorepuestos(p)
        return _save_xlsx(df, "AutoRepuestos Express", out_dir)
    if "mundo repcar" in stem:
        df = process_mundo_repcar(p)
        return _save_xlsx(df, "Mundo RepCar", out_dir)
    if "autofix" in stem or "autofix repuestos" in stem or "autofix" in p.name.lower():
        df = process_autofix(p)
        return _save_xlsx(df, "Autofix", out_dir)
    raise ValueError(f"No se pudo identificar proveedor para: {p.name}")

def process_all_in_downloads(download_dir):
    d = Path(download_dir)
    exts = {".csv", ".xls", ".xlsx"}
    files = [p for p in d.iterdir() if p.is_file() and p.suffix.lower() in exts]

    today = datetime.now().strftime("%Y%m%d")
    out_re = re.compile(rf'^(AutoRepuestos Express|Mundo RepCar|Autofix)_{today}$', re.IGNORECASE)
    inputs = [p for p in files if not out_re.match(p.stem)]

    autofix_inputs = [p for p in inputs if "autofix" in p.stem.lower() or "autofix" in p.name.lower()]
    other_inputs = [p for p in inputs if p not in autofix_inputs]

    outputs, errors = [], []

    for p in sorted(other_inputs):
        try:
            out = process_file(p, out_dir=d)
            outputs.append(out)
        except Exception as e:
            errors.append((p.name, str(e)))

    if autofix_inputs:
        dfs = []
        for p in sorted(autofix_inputs):
            try:
                dfs.append(process_autofix_file_to_df(p))
            except Exception as e:
                errors.append((p.name, str(e)))
        if dfs:
            df_all = pd.concat(dfs, ignore_index=True)
            df_all = df_all.drop_duplicates(subset=["CODIGO", "MARCA", "DESCRIPCION"], keep="last")
            out = _save_xlsx(df_all, "Autofix", out_dir=d)
            outputs.append(out)

    return outputs, errors

if __name__ == "__main__":
    outs, errs = process_all_in_downloads(DOWNLOAD_DIR)

    if outs:
        print("Archivos generados:")
        for p in outs:
            print(" -", Path(p).name)
    else:
        print("No hay nuevos archivos para procesar hoy.")

    if errs:
        print("\nErrores:")
        for name, msg in errs:
            print(f" - {name}: {msg}")
