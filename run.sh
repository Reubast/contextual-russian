#!/usr/bin/env python3
import os
os.system("uvicorn api.main:app --host 0.0.0.0 --port " + os.getenv("PORT", "8000"))
