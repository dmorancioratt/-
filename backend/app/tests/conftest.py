import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Automated tests must be deterministic and must never spend external API quota.
os.environ["AI_PROVIDER"] = "mock"
os.environ["APP_ENV"] = "test"
