"""
PROGRAM: Database Connection Pool Manager
-----------------------------------------

Manages a pool of reusable database connections for improved performance
and resource utilization.
"""

import queue
import threading
import time
import logging
from contextlib import contextmanager
from typing import Iterator, Optional, Any, Callable, Dict
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PoolStats:
    """Statistics about connection pool usage"""
    total_connections: int
    active_connections: int
    idle_connections: int
    total_acquisitions: int
    total_releases: int
    total_timeouts: int
    avg_wait_time: float


class ConnectionPool:
    """
    Thread-safe connection pool for database connections.
    
    Maintains a pool of reusable connections to avoid the overhead
    of creating/destroying connections for each query.
    
    Production Pattern:
        In high-throughput systems, connection creation is expensive.
        Connection pools:
        - Reuse connections
        - Limit concurrent connections
        - Handle connection failures gracefully
    
    Example:
        >>> pool = ConnectionPool(
        ...     connection_factory=lambda: psycopg2.connect('postgresql://...'),
        ...     pool_size=10,
        ...     max_overflow=5,
        ...     timeout=30.0
        ... )
        >>> 
        >>> # Use connection
        >>> with pool.get_connection() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM users")
        ...     results = cursor.fetchall()
        >>> 
        >>> # Connection automatically returned to pool
        >>> 
        >>> # Clenup when done
        >>> pool.close_all()
    """

    def __init__(self, connection_factory: Callable, pool_size: int = 5, max_overflow: int = 5, timeout: float = 30.0, max_connection_age: float = 3600.0):
        """
        Initialize connection pool.
        
        Args:
            connection_factory: Function that creates a new connection
            pool_size: Number of connections to maintain in pool
            max_overflow: Additional connections allowed beyond pool_size
            timeout: Seconds to wait for available connection
            max_connection_age: Max age of connection before recycling (seconds)
        
        Raises:
            ValueError: If pool_size < 1 or max_overflow < 0
        """
        if pool_size < 1:
            raise ValueError(f"pool_size must be >= 1, got {pool_size}")
        if max_overflow < 0:
            raise ValueError(f"max_overflow must be >= 0, got {max_overflow}")
        
        self.connection_factory = connection_factory
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.timeout = timeout
        self.max_connection_age = max_connection_age

        # Connection pool (queue) - FIFO (First in First Out)
        self._pool: queue.Queue = queue.Queue(maxsize=pool_size + max_overflow)

        # Tracking
        self._lock = threading.Lock()
        self._created_connections = 0
        self._active_connections = 0
        self._stats = {
            'acquisitions': 0,
            'releases': 0,
            'timeouts': 0,
            'wait_times': [],
        }

        # Create initial pool
        self._initialize_pool()

        logger.info(
            f"Connection pool initialized: size={pool_size}, "
            f"max_overflow={max_overflow}, timeout={timeout}s"
        )

    def _initialize_pool(self) -> None:
        """Create initial pool of connection"""
        for _ in range(self.pool_size):
            try:
                conn = self._create_connection()
                self._pool.put(conn, block=False)
            except Exception as e:
                logger.error(f"Error creating initial connection: {e}")

    def _create_connection(self) -> Any:
        """
        Create a new database connection with metadata

        Returns:
            Connection wrapper with metadata
        """
        try:
            conn = self.connection_factory()

            # Wrap connection with metadata
            wrapped = {
                'connection': conn,
                'created_at': time.time(),
                'last_used': time.time(),
                'use_count': 0,
            }

            with self._lock:
                self._created_connections += 1

            logger.debug(f"Created connection (total: {self._created_connections})")
            return wrapped
        
        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            raise

    def _is_connection_stale(self, wrapped_conn: Dict) -> bool:
        """
        Check if connection is too old and should be recycled.
        
        Args:
            wrapped_conn: Connection wrapper with metadata
        
        Returns:
            bool: True if connection should be recycled
        """
        age = time.time() - wrapped_conn['created_at']
        return age > self.max_connection_age
    
    @contextmanager
    def get_connection(self) -> Iterator[Any]:
        """
        Get a connection from the pool.
        
        Yields:
            Connection object
        
        Raises:
            queue.Empty: If no connection available within timeout
        
        Example:
            >>> with pool.get_connection() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("SELECT 1")
        """
        start_time = time.time()
        wrapped_conn = None
        created_new = False

        try:
            # Try to get connection from pool
            try:
                wrapped_conn = self._pool.get(timeout=self.timeout)
                logger.debug("Acquired connection from pool")
            
            except queue.Empty:
                # Pool empty - check if we can create overflow connection
                with self._lock:
                    if self._created_connections < (self.pool_size + self.max_overflow):
                        # Create a new overflow connection
                        wrapped_conn = self._create_connection()
                        created_new = True
                        logger.debug("Created oveflow connection")
                    else:
                        # No connections available
                        self._stats['timeouts'] += 1
                        raise queue.Empty(f"No connection available within {self.timeout}s timeout")
                    
            # Check if connection is stale
            if self._is_connection_stale(wrapped_conn):
                logger.info("Connection stale, creating new one")
                self._close_connection(wrapped_conn)
                wrapped_conn = self._create_connection()

            # Update metadata
            wrapped_conn['last_used'] = time.time()
            wrapped_conn['use_count'] += 1

            # Track statistics
            wait_time = time.time() - start_time
            with self._lock:
                self._stats['acquisitions'] += 1
                self._stats['wait_times'].append(wait_time)
                self._active_connections += 1

            # Yield the actual connection (unwrap)
            yield wrapped_conn['connection']

        except Exception as e:
            logger.error(f"Error using connection: {e}")
            # Don't return bad connection to pool
            if wrapped_conn and not created_new:
                self._close_connection(wrapped_conn)
                wrapped_conn = None
            raise

        finally:
            # Return connection to pool
            if wrapped_conn:
                try:
                    if created_new:
                        # Overflow connection - close it
                        self._close_connection(wrapped_conn)
                    else:
                        # Return to pool
                        self._pool.put(wrapped_conn, block=False)
                        logger.debug("Returned connection to pool")
                except queue.Full:
                    # Pool full (should not happen) - close connection
                    self._close_connection(wrapped_conn)

                with self._lock:
                    self._stats['releases'] += 1
                    self._active_connections -= 1

    def _close_connection(self, wrapped_conn: Dict) -> None:
        """Close a connection and update tracking"""
        try:
            wrapped_conn['connection'].close()
            logger.debug("Closed connection")
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")
        
        with self._lock:
            self._created_connections -= 1

    def close_all(self) -> None:
        """
        Close all connections in pool.

        Call this when shutting down the application.
        """
        logger.info("Closing all connections in pool")
        closed = 0

        while not self._pool.empty():
            try:
                wrapped_conn = self._pool.get(block=False)
                self._close_connection(wrapped_conn)
                closed += 1
            except queue.Empty:
                break

        logger.info(f"Closed {closed} connection(s)")

    def get_stats(self) -> PoolStats:
        """
        Get current pool statistics.

        Returns:
            PoolStats: Current statistics
        """
        with self._lock:
            avg_wait = (
                sum(self._stats['wait_times']) / len(self._stats['wait_times'])
                if self._stats['wait_times'] else 0.0
            )

            return PoolStats(
                total_connections=self._created_connections,
                active_connections=self._active_connections,
                idle_connections=self._pool.qsize(),
                total_acquisitions=self._stats['acquisitions'],
                total_releases=self._stats['releases'],
                total_timeouts=self._stats['timeouts'],
                avg_wait_time=avg_wait
            )
        

    def __enter__(self):
        """Support using pool as context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close all connections when exiting context"""
        self.close_all()
        return False
    


# ====================================================
#                  TESTING
# ====================================================

if __name__ == "__main__":
    print("Testing Connection Pool")
    print("=" * 60)

    # Mock connection for testing
    class MockConnection:
        _id_counter = 0

        def __init__(self):
            MockConnection._id_counter += 1
            self.id = MockConnection._id_counter
            self.closed = False
            logger.info(f"Created MockConnection #{self.id}")

        def cursor(self):
            return self
        
        def execute(self, query):
            logger.info(f"Connection #{self.id}: {query}")

        def close(self):
            self.closed = True
            logger.info(f"Closed MockConnection #{self.id}")

    
    # Test Pool
    print("\n1. Testing basic connection pool:")
    pool = ConnectionPool(
        connection_factory=MockConnection,
        pool_size=3,
        max_overflow=2,
        timeout=5.0
    )

    # Use connection
    with pool.get_connection() as conn:
        conn.execute("SELECT 1")
    print("     Connection acquired and returned")

    # Multiple connections
    print("\n2. Testing multiple concurrent connections:")
    connections = []
    for i in range(3):
        connections.append(pool.get_connection())
        conn = connections[-1].__enter__()
        conn.execute(f"SELECT {i}")

    # Return them
    for cm in connections:
        cm.__exit__(None, None, None)
    print("     Multiple connections handled")

    # Stats
    print("\n3. Pool statistics:")
    stats = pool.get_stats()
    print(f"    Total connections:      {stats.total_connections}")
    print(f"    Active:                 {stats.active_connections}")
    print(f"    Idle:                   {stats.idle_connections}")
    print(f"    Acquisitions:           {stats.total_acquisitions}")
    print(f"    Releases:               {stats.total_releases}")
    print(f"    Avg wait time:          {stats.avg_wait_time:.4f}s")

    # Cleanup
    print("\n4. Closing pool:")
    pool.close_all()
    print(f"    All connections closed")