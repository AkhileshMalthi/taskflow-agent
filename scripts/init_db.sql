-- Initialize database schema if needed
-- This script runs automatically when the PostgreSQL container starts

-- Create tables (if your application doesn't auto-create them)
-- The SQLAlchemy models should handle this, but we can add initial setup here if needed

-- Example: Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- You can add seed data here if needed
-- INSERT INTO ...

COMMIT;
