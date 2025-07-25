# webhook/log_trace_decorator.py
import logging
logger = logging.getLogger("uvicorn")

import inspect

def log_trace(name):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"🔍 ENTER: {name}")
            result = await func(*args, **kwargs)
            logger.info(f"✅ EXIT: {name}")
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
