-- Migration: Add indexes for unique name validation
-- Purpose: Improve query performance for name uniqueness checks across soft-deleted records
-- Created: OpenSpec change: validate-logical-deletion-duplicates

-- Index on Categoria.nombre for uniqueness validation queries
CREATE INDEX IF NOT EXISTS idx_categoria_nombre ON categoria(nombre);

-- Index on Ingrediente.nombre for uniqueness validation queries
CREATE INDEX IF NOT EXISTS idx_ingrediente_nombre ON ingrediente(nombre);

-- Index on Producto.nombre for uniqueness validation queries
CREATE INDEX IF NOT EXISTS idx_producto_nombre ON producto(nombre);

-- Optional: Partial indexes to enforce uniqueness within active records only
-- These enforce uniqueness constraint ONLY on active records
-- This allows inactive records to have duplicate names (for soft-delete workflows)
-- Uncomment if using SQLite 3.8.0+ or PostgreSQL

-- For SQLite: Partial unique indexes
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_categoria_nombre_unique_active 
--   ON categoria(nombre) WHERE activo = 1;

-- CREATE UNIQUE INDEX IF NOT EXISTS idx_ingrediente_nombre_unique_active 
--   ON ingrediente(nombre) WHERE activo = 1;

-- CREATE UNIQUE INDEX IF NOT EXISTS idx_producto_nombre_unique_active 
--   ON producto(nombre) WHERE activo = 1;

-- For PostgreSQL: Similar approach with boolean WHERE clause
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_categoria_nombre_unique_active 
--   ON categoria(nombre) WHERE activo = true;
