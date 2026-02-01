import os
import shutil

def which(binary_name):
    """Check if a binary exists in PATH (used for MassDNS auto-detect)"""
    return shutil.which(binary_name)

def ensure_dir(path):
    """Create directory if not present"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
