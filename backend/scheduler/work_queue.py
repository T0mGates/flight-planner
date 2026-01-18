import asyncio
from typing import Dict

queue = asyncio.Queue()

job_status: Dict[str, dict] = {}
