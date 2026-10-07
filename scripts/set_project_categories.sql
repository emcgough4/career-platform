-- Group portfolio work by topic for the Work page sections (2026-10-07).
-- Requires migration 0002_project_category (alembic upgrade head).
PRAGMA foreign_keys = ON;
BEGIN;
UPDATE projects SET category = 'video' WHERE id IN (1, 2, 3, 4, 5, 6, 7);
UPDATE projects SET category = 'web design' WHERE id IN (11, 12, 13);
UPDATE projects SET category = 'content & strategy' WHERE id IN (8, 9, 10);
COMMIT;
