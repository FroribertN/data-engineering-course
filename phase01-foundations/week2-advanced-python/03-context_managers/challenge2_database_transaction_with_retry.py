"""""
PROGRAM: Database Transaction with Automatic Retry
--------------------------------------------------

Handles transient database errors (deadlocks, connection issues) with
exponential backoff retry strategy.
"""

import time
import logging
from contextlib import contextmanager
from typing import Iterator, Optional, Type, Tuple, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeadlockError(Exception):
    """Raised when database deadlock detected"""
    pass

class TransientDatabaseError(Exception):
    """Raised for temporary network/connection issues"""
    pass


@dataclass
class RetryStats:
    """Statistics about retry attempts"""
    total_attempts: int = 0
    successful: bool = False
    final_error: Optional[Exception] = None
    total_duration: float = 0.0


@contextmanager
def transaction_with_retry(
    connection: str, 
    max_retries: int = 3, 
    initial_delay: float = 1.0, 
    backoff_multiplier: float = 2.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = (
        DeadlockError,
        TransientDatabaseError,
    )
) -> Iterator:
    """
    Database transaction that automatically retries on transient failures.

    Implements exponential backoff retry strategy for handling:
    - Database deadlocks
    - Connection timeouts
    - Temporary network issues

    Args:
        connection: Database connection object
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial retry delay in seconds (deffault: 1.0)
        backoff_multiplier: Multiply delay by this each retry (default: 2.0)
        retryable_exceptions: Tuple of exception types to retry
    
    Yields:
        cursor: Database cursor for executing queries
    
    Raises:
        Exception: Last exception if all retries exhausted
    
    Example:
        >>> conn = psycopg2.connect('postgresql://...')
        >>> with transaction_with_retry(conn, max_retries=3) as cursor:
        ...     cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        ...     cursor.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
        >>> # Automatic commit on success, rollback on error, retry on deadlock
    
    Production Pattern:
        Used in financial systems where concurrent updates may cause deadlocks:
        >>> with transaction_with_retry(conn) as cursor:
        ...     # Transfer money between accounts
        ...     cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (100, 1))
        ...     cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (100, 2))
    """
    stats = RetryStats()
    delay = initial_delay
    last_exception = None

    for attempt in range(1, max_retries + 1):
        stats.total_attempts = attempt
        start_time = time.time()

        cursor = None
        try:
            logger.info(f"Transaction attempt {attempt}/{max_retries}")

            # Get cursor
            cursor = connection.cursor()

            # Yield control to user code
            yield cursor

            # If we get here, commit transaction
            connection.commit()
            logger.info(f"Transaction committed successfully (attempt {attempt})")

            stats.successful = True
            stats.total_duration = time.time() - start_time
            return   # Success - exit
        
        except retryable_exceptions as e:
            # Retryable error - rollback and retry
            last_exception = e
            stats.final_error = e

            logger.warning(
                f"Retryable error on attempt {attempt}/{max_retries}: "
                f"{type(e).__name__}: {e}"
            )

            try:
                connection.rollback()
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")

            if attempt < max_retries:
                # Wait before retry with exponential backoff
                logger.info(f"Retrying in {delay:.2f}s...")
                time.sleep(delay)
                delay *= backoff_multiplier
            else:
                # Out of retries
                logger.error(f"Transaction failed after {max_retries} attempts: {e}")
                raise

        except Exception as e:
            # Non-retryable error - rollback and raise immediately
            logger.error(f"Non-retryable error: {type(e).__name__}: {e}")
            stats.final_error = e

            try: 
                connection.rollback()
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")

            raise

        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as e:
                    logger.warning(f"Error closing cursor: {e}")
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    

# Version with savepoints for partial rollback
@contextmanager
def transaction_with_savepoints(connection: Any, savepoint_name: str = 'sp1'):
    """
    Transaction with savepoint support for partial rollback.
    
    Allows rolling back to a savepoint instead of entire transaction.
    
    Args:
        connection: Database connection
        savepoint_name: Name for the savepoint
    
    Yields:
        tuple: (cursor, savepoint_manager)
    
    Example:
        >>> with transaction_with_savepoints(conn) as (cursor, sp):
        ...     cursor.execute("INSERT INTO users (name) VALUES ('Alice')")
        ...     sp.save()  # Create savepoint
        ...     try:
        ...         cursor.execute("INSERT INTO users (name) VALUES (NULL)")  # Fails
        ...     except:
        ...         sp.rollback()  # Rollback to savepoint, keep Alice
        ...     cursor.execute("INSERT INTO users (name) VALUES ('Bob')")
        >>> # Commit: Alice and Bob inserted, NULL attempt rolled back
    """
    class SavePointManager:
        def __init__(self, connection, name):
            self.connection = connection
            self.name = name

        def save(self):
            """Create savepoint"""
            cursor = self.connection.cursor()
            cursor.execute(f"SAVEPOINT {self.name}")
            cursor.close()
            logger.debug(f"Created savepoint: {self.name}")

        def rollback(self):
            """Rollback to savepoint"""
            cursor = self.connection.cursor()
            cursor.execute(f"ROLLBACK TO SAVEPOINT {self.name}")
            cursor.close()
            logger.debug(f"Rolled back to savepoint: {self.name}")

        def release(self):
            """Release savepoint"""
            cursor = self.connection.cursor()
            cursor.execute(f"RELEASE SAVEPOINT {self.name}")
            cursor.close()
            logger.debug(f"Released savepoint: {self.name}")

    cursor = connection.cursor()
    sp_manager = SavePointManager(connection, savepoint_name)

    try:
        yield cursor, sp_manager
        connection.commit()
        logger.info(f"Transaction with savepoints committed")
    except Exception as e:
        connection.rollback()
        logger.error(f"Transaction rolled back: {e}")
        raise
    finally:
        cursor.close()


# ================================
#            TESTING
# ================================

if __name__ == "__main__":
    print("Testing Transaction with Retry")
    print("=" * 60)

    # Mock database connection for testing
    class MockConnection:
        def __init__(self):
            self.attempt = 0
            self.committed = False
            self.rolled_back = False

        def cursor(self):
            return MockCursor(self)
        
        def commit(self):
            self.committed = True
            logger.info("COMMIT")
        
        def rollback(self):
            self.rolled_back = True
            logger.info("ROLLBACK")

    class MockCursor:
        def __init__(self, connection):
            self.connection = connection

        def execute(self, query):
            self.connection.attempt += 1
            # Simulate deadlock on first 2 attempts
            if self.connection.attempt < 3:
                raise DeadlockError("Simulated deadlock")
            logger.info(f"Executed: {query}")

        def close(self):
            pass

    
    # Test: Retry on deadlock
    print("\n1. Testing retry on deadlock:")
    conn = MockConnection()

    try:
        with transaction_with_retry(conn, max_retries=3) as cursor:
            cursor.execute("UPDATE accounts SET balance = balance - 100")
        print(f"    Success after {conn.attempt} attempt(s)")
        print(f"    Transaction committed: {conn.committed}")
    except Exception as e:
        print(f"    Failed: {e}")

    # Test: Exhaust retries
    print("\n2. Testing exhausted retries:")

    class FailingConnection(MockConnection):
        def cursor(self):
            return FailingCursor(self)
        
    class FailingCursor(MockCursor):
        def execute(self, query):
            raise DeadlockError("Persistent deadlock")
        
    conn2 = FailingConnection()
    try:
        with transaction_with_retry(conn2, max_retries=2) as cursor:
            cursor.execute("UPDATE accounts SET balance = balance - 100")
        print("     Should have failed")
    except DeadlockError:
        print(f"    Correctly failed after max retries")
        print(f"    Transaction rolled back: {conn2.rolled_back}")