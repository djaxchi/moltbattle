"""Configuration for MoltBattle MCP Server"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("MOLTBATTLE_API_URL", "https://api.moltclash.com")

# Session Storage
SESSION_STORAGE_PATH = os.getenv("MCP_SESSION_PATH", os.path.expanduser("~/.moltbattle_mcp_session.json"))

# Default timeout for API requests
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
