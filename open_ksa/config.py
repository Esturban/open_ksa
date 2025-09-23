import os

# Default threshold in bytes to consider a file 'large' and suggest on-disk saving
ON_DISK_THRESHOLD_BYTES = int(os.environ.get("OPEN_KSA_ON_DISK_THRESHOLD", 100_000_000))
# Default directory to store large files
LARGE_FILES_DIR = os.environ.get(
    "OPEN_KSA_LARGE_FILES_DIR", os.path.join(os.getcwd(), "opendata", "large_files")
)
