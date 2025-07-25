# webhook/log_trace_decorator.py
# webhook/log_trace_decorator.py
import logging
import inspect
from functools import wraps

logger = logging.getLogger("uvicorn")

def log_trace(name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"🟡 START ➜ {name}")
            result = await func(*args, **kwargs)
            logger.info(f"🟢 END ➜ {name}")
            return result
        return wrapper
    return decorator



"""
def log_trace(tag: str):
    def decorator(fn):
        async def wrapper(*args, **kwargs):
            logger.info(f"🟡 START ➜ {tag}")
            result = await fn(*args, **kwargs)
            logger.info(f"🟢 END ➜ {tag}")
            return result
        return wrapper
    return decorator
"""
