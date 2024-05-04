-- Create the files table
CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,           -- UUID type for unique identifier
    file_path TEXT NOT NULL,       -- File path
    original_size INTEGER,         -- Size of the original file in bytes
    compressed_size INTEGER,       -- Size of the compressed file in bytes
    resolution TEXT                -- Resolution information
);
