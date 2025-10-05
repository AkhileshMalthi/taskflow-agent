"""
Loads environment variables from a .env file into the current Python process.
Usage: python scripts/load_env.py
"""

import os
from pathlib import Path

def load_env(env_path: str = "../.env"):
    env_file = Path(env_path)
    if not env_file.exists():
        print(f".env file not found at {env_file}")
        return
    with env_file.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                name, value = line.split('=', 1)
                value = value.strip('"')
                os.environ[name] = value
    print(f"Loaded environment variables from {env_file}")

if __name__ == "__main__":
    load_env()
