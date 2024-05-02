-- Create the files table
CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,           -- UUID type for unique identifier
    full_file_path TEXT NOT NULL,  -- Full file path
    is_compressed INTEGER DEFAULT 0,  -- Boolean (0 for False, 1 for True)
    is_aiocr INTEGER DEFAULT 0     -- Boolean (0 for False, 1 for True)
);
