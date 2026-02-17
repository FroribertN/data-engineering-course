from functools import wraps
import time
import random
import logging

logging.basicConfig(level=logging.INFO)

# ===========================================
#           ETL Pipeline Decorator
# ===========================================

# ----------- Decorator 1: Timing -----------
def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logging.info(f"{func.__name__} took {elapsed:.2f} seconds")
        return result
    return wrapper

# ----------- Decorator 2: Retry  with exponential backoff -----------
def retry(max_attempts=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            wait_time = delay
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"{func.__name__} failed after {max_attempts} attempts.")
                    raise logging.warning(
                        f"{func.__name__} attempt {attempt + 1} failed: {e}. "
                        f"retrying in {wait_time}s..."
                    )
                time.sleep(wait_time)
                wait_time *= backoff # exponential backoff

        return wrapper
    return decorator

# ----------- Decorator 3: Logging -----------
def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Starting {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"Completed {func.__name__}")
        return result
    return wrapper

# ----------- Decorator 4: Validate Result -----------
def validate_result(check_func):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if not check_func(result):
                raise ValueError(
                    f"{func.__name__} returned invalid result: {result}"
                )
            return result
        return wrapper
    return decorator

# ----------- Build ETL pipeline with stacked decorators -----------
@timer
@log_execution
@retry(max_attempts=3, delay=1, backoff=2)
@validate_result(lambda x: isinstance(x, list) and len(x) > 0)
def extract_data(source):
    """Extract data from a source (simulated with random failure)"""
    if random.random() < 0.3: # 30% failure rate
        raise ConnectionError(f"Failed to connect to {source}")
    time.sleep(0.5) # Simulate delay
    return [{"id": 1, "value": 100}, {"id": 2, "value": 200}]

@timer
@log_execution
@validate_result(lambda x: isinstance(x, list))
def transform_data(data):
    """Transform the data"""
    time.sleep(0.3) # Simulate delay
    return [
        {**record, "value": record["value"] * 2}
        for record in data
    ]

@timer
@log_execution
def load_data(data, destination):
    """Load the data to destination"""
    time.sleep(0.4) # Simulate delay
    logging.info(f"Loaded {len(data)} record to {destination}")
    return f"Success: {len(data)} records"


# Run the ETL pipeline
if __name__ == "__main__":
    print("\n" + "=" * 40)
    print("STARTING ETL PIPELINE".center(40))
    print("=" * 40 + "\n")

    raw_data = extract_data("API")
    transformed = transform_data(raw_data)
    load_result = load_data(transformed, "Database")

    print(f"\nPIPELINE COMPLETED: {load_result}\n")