import time
from functools import wraps

def rate_limit(max_calls, time_window):
    def decorator(func):
        calls = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Clean old calls
            cutoff = now - time_window
            calls[:] = [t for t in calls if t > cutoff]
            
            if len(calls) >= max_calls:
                oldest = calls[0]
                wait_time = time_window - (now - oldest)
                raise Exception(
                    f"Rate limit: max {max_calls} calls/{time_window}s. "
                    f"Wait {wait_time:.1f}s or try again at "
                    f"{time.strftime('%H:%M:%S', time.localtime(oldest + time_window))}"
                )
            
            calls.append(now)
            return func(*args, **kwargs)
        
        # Add method to check remaining calls
        def remaining():
            now = time.time()
            cutoff = now - time_window
            recent = [t for t in calls if t > cutoff]
            return max_calls - len(recent)
        
        wrapper.remaining_calls = remaining
        wrapper.reset = lambda: calls.clear()
        
        return wrapper
    return decorator


# ================================
#            TESTING
# ================================

@rate_limit(max_calls=5, time_window=60)
def api_call():
    return "success"

print(f"Remaining calls: {api_call.remaining_calls()}")