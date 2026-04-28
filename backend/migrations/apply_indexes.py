"""
Script para aplicar migraciones de índices de nombres.
Ejecutar después de crear las tablas base.
"""

import sqlite3
from pathlib import Path


def apply_name_indexes():
    """Aplica índices para validación de unicidad de nombres"""

    # Detecta si usa SQLite (default en el proyecto)
    db_path = Path(__file__).parent.parent / "database.db"

    if not db_path.exists():
        print(f"Base de datos no encontrada en {db_path}")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Índices simples para mejorar performance en búsquedas de nombre
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_categoria_nombre ON categoria(nombre)",
            "CREATE INDEX IF NOT EXISTS idx_ingrediente_nombre ON ingrediente(nombre)",
            "CREATE INDEX IF NOT EXISTS idx_producto_nombre ON producto(nombre)",
        ]

        for index_sql in indices:
            cursor.execute(index_sql)
            print(f"✓ {index_sql}")

        conn.commit()
        conn.close()

        print("\n✓ Índices de nombres creados exitosamente")
        return True

    except sqlite3.Error as e:
        print(f"✗ Error al crear índices: {e}")
        return False


if __name__ == "__main__":
    apply_name_indexes()
