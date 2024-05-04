CREATE TABLE IF NOT EXISTS files (
    id TEXT PRIMARY KEY,                       -- UUID type for unique identifier
    file_path TEXT NOT NULL,                   -- File path
    original_size INTEGER,                     -- Size of the original file in bytes
    compressed_size INTEGER,                   -- Size of the compressed file in bytes
    resolution TEXT,                           -- Resolution information
    datetime TEXT,                             -- New column for datetime
    text_in_image TEXT,                        -- New column for text_in_image
    is_camera_tilted TEXT,                     -- New column for is_camera_tilted
    is_camera_tampered TEXT,                   -- New column for is_camera_tampered
    are_there_people_in_the_image TEXT,         -- New column for are_there_people_in_the_image
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  -- Timestamp column with default value    
);
