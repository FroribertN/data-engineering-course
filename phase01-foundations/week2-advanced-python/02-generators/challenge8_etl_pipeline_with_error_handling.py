"""
PROGRAM: Production ETL Pipeline with Comprehensive Error Handling
------------------------------------------------------------------

Enterprise-grade ETL pipeline demonstrating best practices for:
- Graceful error handling
- Dead letter queues
- Metrics and monitoring
- Data quality validation
- Retry logic
"""

import json
import logging
from typing import Iterator, Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import traceback


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Classification of error severity"""
    WARNING = "warning"         # Skippable, logged
    ERROR = "error"             # Record failed, goes to DLQ (Dead Letter Queue) - a separate storage area for "broken" data
    FATAL = "fatal"             # Pipeline stops


@dataclass
class PipelineMetrics:
    """Comprehensive pipeline execution metrics"""
    total_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    skipped_records: int = 0
    validation_errors: int = 0
    transformation_errors: int = 0
    load_errors: int = 0
    start_time: float = field(default_factory=lambda: datetime.now().timestamp())
    end_time: Optional[float] = None

    @property
    def duration(self) -> float:
        """Pipeline duration in seconds"""
        end = self.end_time or datetime.now().timestamp()
        return end - self.start_time
    
    @property
    def success_rate(self) -> float:
        """Percentage of successful records"""
        if self.total_records == 0:
            return 0.0
        return (self.successful_records / self.total_records) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            'total_records': self.total_records,
            'successful_records': self.successful_records,
            'failed_records': self.failed_records,
            'skipped_records': self.skipped_records,
            'validation_errors': self.validation_errors,
            'transformation_errors': self.transformation_errors,
            'load_errors': self.load_errors,
            'duration_seconds': self.duration,
            'success_rate_percent': round(self.success_rate, 2),
        }
    

@dataclass
class ErrorRecord:
    """Record that failed processing"""
    record: Dict[str, Any]
    stage: str
    error_type: str
    error_message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    stack_trace: Optional[str] = None


class DeadLetterQueue:
    """
    Dead Letter Queue for failed records.

    Production pattern: Instead of crashing pipeline, capture failed records for later analysis and reprocessing.
    """

    def __init__(self, dlq_path: str = "dlq.jsonl"):
        """
        Initialize DLQ.

        Args:
            dlq_path: Path to DLQ file
        """
        self.dlq_path = Path(dlq_path)
        self.errors: List[ErrorRecord] = []

    def add(self, record: Dict[str, Any], stage: str, error: Exception) -> None:
        """
        Add failed record to DLQ

        Args:
            record: Record that failed
            stage: Pipeline stage where failure occurred
            error: Exception that was raised
        """
        error_record = ErrorRecord(
            record=record,
            stage=stage,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc()
        )
        self.errors.append(error_record)

        logger.warning(
            f"Record added to DLQ: stage={stage}, "
            f"error={type(error).__name__}: {error}"
        )

    def flush(self) -> int:
        """
        Write DLQ to file.

        Returns:
            int: Number of errors written
        """
        if not self.errors:
            return 0
        
        with open(self.dlq_path, 'a') as f:
            for error in self.errors:
                json.dump({
                    'record': error.record,
                    'stage': error.stage,
                    'error_type': error.error_type,
                    'error_message': error.error_message,
                    'timestamp': error.timestamp,
                }, f)
                f.write("\n")

        count = len(self.errors)
        self.errors.clear()
        logger.info(f"Flushed {count} errors to DLQ: {self.dlq_path}")
        return count
    

def extract_jsonl(filename: str, metrics: PipelineMetrics, dlq: DeadLetterQueue) -> Iterator[Dict[str, Any]]:
    """
    Extract stage: Read JSON Lines file with error handling

    Args:
        filename: Path to JSONL file
        metrics: Pipeline metrics tracker
        dlq: Dead letter queue for failed records

    Yields:
        Dict[str, Any]: Parsed JSON records

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    filepath = Path(filename)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    
    logger.info(f"Starting extraction from: {filename}")

    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            metrics.total_records += 1

            try:
                # Parse JSON
                record = json.loads(line.strip())
                yield record
            
            except json.JSONDecodeError as e:
                # Invalid JSON - add to DLQ
                metrics.failed_records += 1
                dlq.add(
                    record={'raw_line': line.strip(), 'line_number': line_num},
                    stage='extract',
                    error=e
                )
                continue


            except Exception as e:
                #unexpected error
                logger.error(f"Unexpected error extracting line {line_num}: {e}")
                metrics.failed_records += 1
                dlq.add(
                    record={'raw_line': line.strip(), 'line_number': line_num},
                    stage='extract',
                    error=e
                )
                continue


def validate_record(records: Iterator[Dict[str, Any]], required_fields: List[str], validators: Dict[str, Callable], metrics: PipelineMetrics, dlq: DeadLetterQueue) -> Iterator[Dict[str, Any]]:
    """
    Validation stage: Ensure data quality.
    
    Args:
        records: Input record stream
        required_fields: Fields that must be present
        validators: Dict of {field: validation_function}
        metrics: Pipeline metrics
        dlq: Dead letter queue
    
    Yields:
        Dict[str, Any]: Valid records only
    
    Example:
        >>> validators = {
        ...     'amount': lambda x: x > 0,
        ...     'email': lambda x: '@' in x,
        ...     'age': lambda x: 0 <= x <= 150
        ... }
    """
    for record in records:
        try:
            # Check required fields
            missing = [f for f in required_fields if f not in record]
            if missing:
                raise ValueError(f"Missing required field(s): {missing}")
            
            # Run validators
            for field, validator_func in validators.items():
                if field in record:
                    if not validator_func(record[field]):
                        raise ValueError(f"Validation failed for {field}={record[field]}")
                    
            # Validation passed
            yield record

        except ValueError as e:
            # Validation error - add to DLQ
            metrics.validation_errors += 1
            metrics.failed_records += 1
            dlq.add(record=record, stage='validate', error=e)

        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected validation error: {e}")
            metrics.validation_errors += 1
            metrics.failed_records += 1
            dlq.add(record=record, stage='validate', error=e)


def transform_record(records: Iterator[Dict[str, Any]], transformations: Dict[str, Callable], metrics: PipelineMetrics, dlq: DeadLetterQueue, skip_on_error: bool = True) -> Iterator[Dict[str, Any]]:
    """
    Transformation stage: Apply business logic.
    
    Args:
        records: Input record stream
        transformations: Dict of {field: transformation_function}
        metrics: Pipeline metrics
        dlq: Dead letter queue
        skip_on_error: If True, skip failed records. If False, add to DLQ.
    
    Yields:
        Dict[str, Any]: Transformed records
    
    Example:
        >>> transforms = {
        ...     'name': str.upper,
        ...     'amount': lambda x: float(x) * 1.1,
        ...     'category': lambda x: x.strip().title()
        ... }
    """
    for record in records:
        transformed = record.copy()
        transformation_failed = False

        for field, transform_func in transformations.items():
            if field not in transformed:
                continue

            try:
                transformed[field] = transform_func(transformed[field])
            except Exception as e:
                logger.warning(f"Transformation failed for {field}={record.get(field)}: {e}")

                if skip_on_error:
                    # Keep original value, continue processing
                    metrics.transformation_errors += 1
                    continue
                else:
                    # Fail entire record
                    metrics.transformation_errors += 1
                    metrics.failed_records += 1
                    dlq.add(record=record, stage='transform', error=e)
                    transformation_failed = True
                    break

        if not transformation_failed:
            yield transformed 


def aggregate_results(records: Iterator[Dict[str, Any]], group_by: str, aggregations: Dict[str, Callable]) -> Iterator[Dict[ str, Any]]:
    """
    Aggregation stage: Group and aggregate data.
    
    Args:
        records: Input record stream
        group_by: Field to group by
        aggregations: Dict of {output_field: aggregation_function}
    
    Yields:
        Dict[str, Any]: Aggregated results
    
    Example:
        >>> aggregations = {
        ...     'total_amount': lambda records: sum(r['amount'] for r in records),
        ...     'count': lambda records: len(records),
        ...     'avg_amount': lambda records: sum(r['amount'] for r in records) / len(records)
        ... }
    """
    from collections import defaultdict

    # Group records
    groups = defaultdict(list)
    for record in records:
        key = record[group_by]
        groups[key].append(record)

    # Aggregate each group
    for key, group_records in groups.items():
        result = {group_by: key}

        for output_field, agg_func in aggregations.items():
            try:
                result[output_field] = agg_func(group_records)
            except Exception as e:
                logger.error(f"Aggregation errorfor {output_field}")
                result[output_field] = None

        yield result


def load_jsonl(records: Iterator[Dict[str, Any]], output_file: str, metrics: PipelineMetrics, dlq: DeadLetterQueue, batch_size: int = 1000) -> int:
    """
    Load stage: Write results to JSONL file.
    
    Args:
        records: Input record stream
        output_file: Path to output file
        metrics: Pipeline metrics
        dlq: Dead letter queue
        batch_size: Flush to disk every N records
    
    Returns:
        int: Number of records written
    
    """
    logger.info(f"Loading data to: {output_file}")

    written = 0
    batch = []

    try:
        with open(output_file, 'w') as f:
            for record in records:
                try:
                    # Convert to JSON and write
                    json_line = json.dumps(record)
                    batch.append(json_line)
                    written += 1
                    metrics.successful_records += 1

                    # Flush batch
                    if len(batch) >= batch_size:
                        f.write("\n".join(batch) + "\n")
                        f.flush()
                        batch = []

                        if written % (batch_size * 10) == 0:
                            logger.info(f"Loaded {written:,} records...")

                except Exception as e:
                    metrics.load_errors += 1
                    metrics.failed_records += 1
                    dlq.add(record=record, stage='load', error=e)

            # Write remaining batch
            if batch:
                f.write("\n".join(batch) + "\n")

    except Exception as e:
        logger.error(f"Fatal error during load: {e}")
        raise

    logger.info(f"Successfully loaded {written:,} records")
    return written



def run_etl_pipeline(input_file: str, output_file: str, config: Dict[str, Any]) -> PipelineMetrics:
    """
    Execute complete ETL pipeline with comprehensive error handling.
    
    Production-ready pipeline that never crashes due to bad data.
    
    Args:
        input_file: Path to input JSONL file
        output_file: Path to output JSONL file
        config: Pipeline configuration
    
    Returns:
        PipelineMetrics: Execution statistics
    
    Example:
        >>> config = {
        ...     'required_fields': ['id', 'amount', 'user_id'],
        ...     'validators': {
        ...         'amount': lambda x: x > 0,
        ...         'user_id': lambda x: len(str(x)) > 0
        ...     },
        ...     'transformations': {
        ...         'amount': float,
        ...         'user_id': str
        ...     }
        ... }
        >>> metrics = run_etl_pipeline('input.jsonl', 'output.jsonl', config)
    """
    metrics = PipelineMetrics()
    dlq = DeadLetterQueue(dlq_path=config.get('dlq_path', 'dlq.jsonl'))

    try:
        logger.info("=" * 60)
        logger.info("Starting ETL Pipeline")
        logger.info(f"Input:    {input_file}")
        logger.info(f"Output:   {output_file}")
        logger.info("=" * 60)

        # Build pipeline
        records = extract_jsonl(input_file, metrics, dlq)

        # Validate
        if 'required_fields' in config or 'validators' in config:
            records = validate_record(
                records,
                required_fields=config.get('required_fields', []),
                validators=config.get('validators', {}),
                metrics=metrics,
                dlq=dlq
            )

        # Transform
        if 'transformations' in config:
            records = transform_record(
                records,
                transformations=config['transformations'],
                metrics=metrics,
                dlq=dlq,
                skip_on_error=config.get('skip_transform_errors', True)
            )

        # Aggregate (optional)
        if 'group_by' in config and 'aggregations' in config:
            records = aggregate_results(
                records,
                group_by=config['group_by'],
                aggregations=config['aggregations']
            )

        # Load
        load_jsonl(
            records,
            output_file,
            metrics,
            dlq,
            batch_size=config.get('batch_size', 1000)
        )

        # Finalize
        metrics.end_time = datetime.now().timestamp()
        dlq.flush()

        # Load summary
        logger.info("=" * 60)
        logger.info("Pipeline Complete")
        logger.info(f"Duration:         {metrics.duration:.2f}s")
        logger.info(f"Total Records:    {metrics.total_records:,}")
        logger.info(f"Successful:       {metrics.successful_records:,}")
        logger.info(f"Failed:           {metrics.failed_records:,}")
        logger.info(f"Success Rate:     {metrics.success_rate:.2f}%")
        logger.info("=" * 60)

        # Write metrics
        metrics_file = config.get('metrics_file', 'pipeline_metrics.json')
        with open(metrics_file, 'w') as f:
            json.dump(metrics.to_dict(), f, indent=2)
    
    except Exception as e:
        logger.error(f"Fatal pipeline error: {e}")
        logger.error(traceback.format_exc())
        metrics.end_time = datetime.now().timestamp()
        raise

    return metrics


# ===============================================
#       TESTING WITH SAMPLE DATA
# ===============================================

if __name__ == "__main__":
    # Create test data
    test_data = [
        {'id': 1, 'user_id': 'u1', 'amount': 100.50, 'category': 'sale'},
        {'id': 2, 'user_id': 'u2', 'amount': 250.00, 'category': 'sale'},
        {'id': 3, 'user_id': 'u1', 'amount': -50.00, 'category': 'refund'},
        {'id': 4, 'user_id': 'u3', 'amount': 75.25, 'category': 'sale'},
        {'id': 5, 'amount': 120.00, 'category': 'sale'},   # Missing user_id
        'invalid json line',    # Malformed
        {'id': 6, 'user_id': 'u2', 'amount': 300.00, 'category': 'sale'},
    ]

    # Write test file
    with open('test_input.jsonl', 'w') as f:
        for record in test_data:
            if isinstance(record, dict):
                f.write(json.dumps(record) + "\n")
            else:
                f.write(record + "\n")

    # Configure pipeline
    config = {
        'required_fields': ['id', 'user_id', 'amount'],
        'validators': {
            'amount': lambda x: x > 0,
            'user_id': lambda x: len(str(x)) > 0,
        },
        'transformations': {
            'amount': float,
            'category': str.upper,
        },
        'skip_transform_errors': True,
        'batch_size': 100,
    }

    # Run pipeline
    metrics = run_etl_pipeline(
        input_file='test_input.jsonl',
        output_file='test_output.jsonl',
        config=config
    )

    print("\n" + "=" * 60)
    print(f"FINAL METRICS".center(60))
    print("=" * 60)
    for key, value in metrics.to_dict().items():
        print(f"    {key}: {value}")