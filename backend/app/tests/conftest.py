import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Automated tests must be deterministic and must never spend external API quota.
os.environ["AI_PROVIDER"] = "mock"
# 同理：测试不下载 BGE 模型，统一走伪向量，保证确定性
os.environ["RAG_EMBEDDER"] = "fake"
