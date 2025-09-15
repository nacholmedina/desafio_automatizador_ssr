#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

APP_NAME = "ETL Boxer Parte2"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
info = logging.info
warn = logging.warning
err = logging.error

load_dotenv()


def parse_args():
    p = argparse.ArgumentParser(description="ETL Parte 2 - Boxer")
    p.add_argument("--out", required=True, help="Carpeta de salida de los CSV (se crea si no existe).")
    p.add_argument("--decimal", default=",", choices=[",", "."], help="Separador decimal (default ',').")
    p.add_argument("--sep", default=",", help="Separador de columnas del CSV (default ',').")
    p.add_argument("--ultimos-dias", type=int, default=None,
                   help="Usar N días exactos en lugar de 1 mes calendario para Autofix.")
    return p.parse_args()


def get_engine():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "repuestosDB")
    user = os.getenv("DB_USER", "scrapper")
    pwd = os.getenv("DB_PASS", "scrapper_pass")
    uri = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{name}?charset=utf8mb4"
    return create_engine(uri, pool_pre_ping=True)


def _to_numeric(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def main():
    args = parse_args()
    out_dir = Path(args.out)

    info(f"{APP_NAME} – iniciando")
    info(f"Carpeta de salida: {out_dir.resolve()}")

    if out_dir.exists() and not out_dir.is_dir():
        err(f"La ruta de salida existe pero no es carpeta: {out_dir}")
        raise SystemExit(2)
    out_dir.mkdir(parents=True, exist_ok=True)

    info("Conectando a MySQL…")
    try:
        engine = get_engine()
        with engine.connect() as _:
            pass
    except Exception as e:
        err(f"No se pudo conectar a MySQL: {e}")
        raise SystemExit(3)

    filtro_tiempo = (
        f"(CURRENT_DATE - INTERVAL {int(args.ultimos_dias)} DAY)"
        if args.ultimos_dias else
        "(CURRENT_DATE - INTERVAL 1 MONTH)"
    )

    sql_autofix_desactualizados = text(f"""
        SELECT
            r.id,
            r.codigo,
            r.descripcion,
            r.precio,
            r.marca_id,
            r.proveedor_id,
            r.ultima_actualizacion_id,
            p.nombre AS proveedor,
            a.fecha  AS fecha_actualizacion
        FROM repuesto AS r
        INNER JOIN proveedor AS p
                ON p.id = r.proveedor_id
        LEFT JOIN actualizacion AS a
               ON a.id = r.ultima_actualizacion_id
        WHERE p.nombre = 'Autofix'
          AND (a.fecha IS NULL OR a.fecha < {filtro_tiempo});
    """)

    sql_marcas_15 = text("""
        SELECT
            r.id,
            r.codigo,
            r.descripcion,
            m.nombre AS marca,
            r.precio AS precio_actual,
            ROUND(r.precio * 1.15, 2) AS precio_actualizado
        FROM repuesto AS r
        LEFT JOIN marca AS m
               ON m.id = r.marca_id
        WHERE m.nombre IN ('ELEXA','BERU','SH','MASTERFILT','RN');
    """)

    sql_prov_30 = text("""
        SELECT
            r.id,
            r.codigo,
            r.descripcion,
            p.nombre AS proveedor,
            r.precio AS precio_actual,
            ROUND(r.precio * 1.30, 2) AS precio_actualizado
        FROM repuesto AS r
        INNER JOIN proveedor AS p
                ON p.id = r.proveedor_id
        WHERE p.nombre IN ('AutoRepuestos Express', 'Automax')
          AND r.precio > 50000
          AND r.precio < 100000;
    """)

    sql_resumen = text("""
        WITH base AS (
            SELECT
                r.id,
                r.codigo,
                r.descripcion,
                r.precio,
                r.proveedor_id,
                p.nombre AS proveedor,
                r.marca_id,
                m.nombre AS marca
            FROM repuesto r
            INNER JOIN proveedor p ON p.id = r.proveedor_id
            LEFT  JOIN marca     m ON m.id = r.marca_id
        ),
        counts AS (
            SELECT
                proveedor_id,
                COUNT(*) AS total_repuestos,
                SUM(CASE
                        WHEN r.descripcion IS NULL OR TRIM(r.descripcion) = '' THEN 1
                        ELSE 0
                    END) AS sin_descripcion
            FROM repuesto r
            GROUP BY proveedor_id
        ),
        max_precio AS (
            SELECT proveedor_id, MAX(precio) AS max_precio
            FROM base
            GROUP BY proveedor_id
        ),
        maxi AS (
            SELECT b.proveedor_id,
                   b.id     AS repuesto_mas_caro_id,
                   b.codigo AS repuesto_mas_caro_codigo,
                   b.precio AS repuesto_mas_caro_precio
            FROM base b
            INNER JOIN max_precio mm
                    ON mm.proveedor_id = b.proveedor_id
                   AND mm.max_precio   = b.precio
        ),
        avg_brand AS (
            SELECT
                proveedor_id,
                COALESCE(marca, '(sin marca)') AS marca,
                AVG(precio) AS promedio_precio_marca
            FROM base
            GROUP BY proveedor_id, COALESCE(marca, '(sin marca)')
        )
        SELECT
            p.id AS proveedor_id,
            p.nombre AS proveedor,
            c.total_repuestos,
            c.sin_descripcion,
            mx.repuesto_mas_caro_id,
            mx.repuesto_mas_caro_codigo,
            mx.repuesto_mas_caro_precio,
            ab.marca,
            ROUND(ab.promedio_precio_marca, 2) AS promedio_precio_marca
        FROM proveedor p
        LEFT JOIN counts   c  ON c.proveedor_id = p.id
        LEFT JOIN maxi     mx ON mx.proveedor_id = p.id
        LEFT JOIN avg_brand ab ON ab.proveedor_id = p.id
        ORDER BY p.nombre, ab.marca;
    """)

    with engine.connect() as conn:
        df1 = pd.read_sql(sql_autofix_desactualizados, conn)
        df2 = pd.read_sql(sql_marcas_15, conn)
        df3 = pd.read_sql(sql_prov_30, conn)
        df4 = pd.read_sql(sql_resumen, conn)

    df1 = _to_numeric(df1, ["precio"])
    df2 = _to_numeric(df2, ["precio_actual", "precio_actualizado"])
    df3 = _to_numeric(df3, ["precio_actual", "precio_actualizado"])
    df4 = _to_numeric(df4, ["repuesto_mas_caro_precio", "promedio_precio_marca"])

    df1.to_csv(out_dir / "lista_a_actualizar_Autofix.csv",
               index=False, encoding="utf-8", decimal=args.decimal, sep=args.sep)
    df2.to_csv(out_dir / "aumento_15_marcas_seleccionadas.csv",
               index=False, encoding="utf-8", decimal=args.decimal, sep=args.sep)
    df3.to_csv(out_dir / "aumento_productos.csv",
               index=False, encoding="utf-8", decimal=args.decimal, sep=args.sep)

    cols_prov = [
        "proveedor_id", "proveedor", "total_repuestos", "sin_descripcion",
        "repuesto_mas_caro_id", "repuesto_mas_caro_codigo", "repuesto_mas_caro_precio"
    ]
    bloques = []
    for prov, grupo in df4.sort_values(["proveedor", "marca"]).groupby(["proveedor_id", "proveedor"], dropna=False):
        fila_resumen = grupo[cols_prov].drop_duplicates().iloc[0].to_dict()
        fila_resumen.update({"seccion": "proveedor", "marca": "", "promedio_precio_marca": ""})
        bloques.append(fila_resumen)
        for _, r in grupo[["marca", "promedio_precio_marca"]].iterrows():
            bloques.append({
                "seccion": "marca",
                "proveedor_id": "", "proveedor": "",
                "total_repuestos": "", "sin_descripcion": "",
                "repuesto_mas_caro_id": "", "repuesto_mas_caro_codigo": "", "repuesto_mas_caro_precio": "",
                "marca": r["marca"] if pd.notna(r["marca"]) else "",
                "promedio_precio_marca": r["promedio_precio_marca"]
            })
        bloques.append({
            "seccion": "", "proveedor_id": "", "proveedor": "",
            "total_repuestos": "", "sin_descripcion": "",
            "repuesto_mas_caro_id": "", "repuesto_mas_caro_codigo": "", "repuesto_mas_caro_precio": "",
            "marca": "", "promedio_precio_marca": ""
        })

    df_pretty = pd.DataFrame(bloques, columns=[
        "seccion",
        "proveedor_id", "proveedor",
        "total_repuestos", "sin_descripcion",
        "repuesto_mas_caro_id", "repuesto_mas_caro_codigo", "repuesto_mas_caro_precio",
        "marca", "promedio_precio_marca"
    ])
    df_pretty.to_csv(out_dir / "datos_individuales_proveedores.csv",
                     index=False, encoding="utf-8", decimal=args.decimal, sep=args.sep)

    info(f"CSV generados en: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
