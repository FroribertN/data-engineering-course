"""
PROGRAM: Moving Average Generator - Streaming Analytics
-------------------------------------------------------

Implements moving average calculation for streaming data using generator send() method.
Production pattern for real-time analytics and monitoring systems.
"""
from typing import Generator, Optional
from collections import deque
import statistics

def moving_average(window_size: int) -> Generator[float, float, None]:
    """
    Calculate moving average over a sliding window of values.

    This generator uses send() method to recieve values and yields the current moving average. 
    Useful for:
    - Real-time metrics monitoring
    - Time-series smoothing
    - Anomaly detection preprocessing

    Args:
        window_size: Number of values in the moving window (must be >= 1)

    Yields:
        float: Current moving average

    Recieves:
        float: New value to add to the window

    Raises:
        ValueError: if window_size < 1

    Example:
        >>> avg = moving_average(window_size=3)
        >>> next(avg)  # Prime the generator
        >>> print(avg.send(10))  # 10.0
        >>> print(avg.send(20))  # 15.0
        >>> print(avg.send(30))  # 20.0
        >>> print(avg.send(40))  # 30.0 (window slides: [20, 30, 40])
    
    Time Complexity: O(1) per value (amortized)
    Space Complexity: O(window_size)
    """
    if window_size < 1:
        raise ValueError(f"window_size must be >= 1, got {window_size}")
    
    # deque is more efficient for adding/removing items from both left and right side quickly than a standard list. 
    window: deque = deque(maxlen=window_size)

    # Initial value (primer)
    value = yield 0.0

    while True:
        if value is not None:
            window.append(value)

        # Calculate and yield moving average
        current_avg = sum(window) / len(window) if window else 0.0
        value = yield current_avg


def weighted_moving_average(window_size: int) -> Generator[float, float, None]:
    """
    Calculate weighted moving average (WMA) with linear weights.

    More recent values have higher weights.
    Useful for:
    - Trend analysis
    - Responsive metrics
    - Price forecasting

    Weight formula: weight[i] = (i + 1) / sum(1 + n)
    More recent value has highest weight.

    Args:
        window_size: Number of values in the moving window

    Yields:
        float: current weighted moving average
    
    Example:
        >>> wma = weighted_moving_average(window_size=3)
        >>> next(wma)
        >>> print(wma.send(10))  # 10.0
        >>> print(wma.send(20))  # 16.67 (more weight on 20)
        >>> print(wma.send(30))  # 23.33 (most weight on 30)
    """
    if window_size <= 1:
        raise ValueError(f"window_size must be >= 1, got {window_size}")
    
    window: deque = deque(maxlen=window_size)

    # Calculate weights (1, 2, 3, ..., n)
    # Sum of weights: n(n +1) / 2
    weight_sum = window_size * (window_size + 1) / 2

    value = yield 0.0

    while True:
        if value is not None:
            window.append(value)

        if window:
            # Calculate weighted average
            weighted_sum = sum((i + 1) * val for i, val in enumerate(window))
            current_wma = weighted_sum / weight_sum
        else:
            current_wma = 0.0

        value = yield current_wma


def exponential_moving_average(alpha: float = 0.3) -> Generator[float, float, None]:
    """
    Calculate exponential moving average (EMA).

    EMA gives exponentially decreasing weights to older values.
    Formula: EMA_t = a * value_t + (1 - a) *EMA_{t-1}

    Used extensively in:
    - Financial analysis
    - Network monitoring
    - Real-time anomaly detection

    Args:
        alpha: smoothing factor (0 < aplha <= 1)
        Higher alpha = more weight on recent values
        Typical values: 0.1 to 0.3

    Yields:
        float: Current exponential moving average
    
    Example:
        >>> ema = exponential_moving_average(alpha=0.3)
        >>> next(ema)
        >>> print(ema.send(100))  # 100.0
        >>> print(ema.send(110))  # 103.0
        >>> print(ema.send(105))  # 103.6
    """
    if not 0 < alpha <= 1:
        raise ValueError(f"alpha must be in (0, 1], got {alpha}")
    
    ema: Optional[float] = None
    value = yield 0.0

    while True:
        if value is not None:
            if ema is None:
                # First value
                ema = value
            else:
                # EMA formula
                ema = alpha * value + (1 - alpha) *ema

        value = yield ema if ema is not None else 0.0


# ==========================================================
#       PRODUCTION USAGE: Real-time monitoring
# ==========================================================
class StreamingMetrics:
    """
    Real-time streaming metrics calculator using moving averages.

    Production pattern for monitoring systems and alerting.    
    """

    def __init__(self, window_size: int = 100, ema_alpha: float = 0.2):
        """
        Initialize streaming metrics.

        args:
            window_size: Window size for simple moving average
            ema_alpha: Alpha for exponential moving average       
        """
        self.sma = moving_average(window_size)
        self.ema = exponential_moving_average(ema_alpha)

        # Prime generators
        next(self.sma)
        next(self.ema)

        self.count = 0
        self.min_value = float('inf')
        self.max_value = float('-inf')

    def update(self, value: float) -> dict:
        """
        Update metrics with new value.

        Args:
            value: New metric value

        Returns:
            dict: Current metric statistics        
        """
        self.count += 1
        self.min_value = min(self.min_value, value)
        self.max_value = max(self.max_value, value)

        current_sma = self.sma.send(value)
        current_ema = self.ema.send(value)

        return {
            'count': self.count,
            'current': value,
            'sma': round(current_sma, 2),
            'ema': round(current_ema, 2),
            'min': self.min_value,
            'max': self.max_value,
        }
    

# ==========================================================
#       EXAMPLE: API response time monitoring
# ==========================================================
if __name__ == "__main__":
    import random
    import time

    # Simulate API response time monitoring
    metrics = StreamingMetrics(window_size=10, ema_alpha=0.3)

    print("API Response Time Monitor")
    print("=" * 50)

    for i in range(20):
        # Simulate response time (with occasional spikes)
        response_time = random.uniform(100, 300)
        if random.random() < 0.1:  # 10% chance of spike
            response_time += random.uniform(500, 1000)

    stats = metrics.update(response_time)

    print(
        f"Request {stats['count']:3d}: "
        f"Current={stats['current']:6.1f}ms "
        f"SMA={stats['sma']:6.1f}ms "
        f"EMA={stats['ema']:6.1f}ms"
        )
    
    # Alert if anomaly (current > EMA)  
    if stats['current'] > stats['ema'] * 2:
        print(f"    ALERT: Response time spike detected")

    time.sleep(0.1)