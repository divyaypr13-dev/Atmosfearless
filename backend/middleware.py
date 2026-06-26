from flask import request, jsonify
from functools import wraps
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        logger.info(f"📥 {request.method} {request.path}")
        response = f(*args, **kwargs)
        logger.info(f"✅ Completed in {time.time() - start_time:.3f}s")
        return response
    return decorated_function
