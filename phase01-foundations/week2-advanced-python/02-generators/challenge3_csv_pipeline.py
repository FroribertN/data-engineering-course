"""
PROGRAM: CSV ETL Pipeline - Memory-Efficient Data Processing
------------------------------------------------------------

Generator-based pipeline for processing CSV files of arbitrary size.
Demonstrates professional ETL patterns with proper typing and error handling.
"""
import csv
from typing import Iterator, Dict, Any, Callable, Optional
from pathlib import Path
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PipelineStats:
    """Statistics for ETL pipeline execution"""
    records_read: int = 0
    records_filtered: int = 0
    records_transformed: int = 0
    errors: int = 0


def read_csv(
        filename: str,
        encoding: str = 'utf-8',
        delimeter: str = ','
) -> Iterator[Dict[str, str]]:
    """
    Read CSV file and yield records as dictionaries.

    Generator-based approach allows processing files larger than available RAM.

    Args:
        filename: Path to CSV file
        encoding: File encoding (default: 'utf-8')
        delimeter: CSV delimeter (default: ',')

    Yields:
        Dict[str, str]: Each row as a dictionary (column_name -> value)

    Raises:
        FileNotFoundError: If file doesn't exist
        csv.Error: If CSV is malformed

    Example:
        >>> for record in read_csv('sales.csv'):
        ...     print(record['customer_id'], record['amount'])
    
    Memory: O(1) - One row at a time
    """
    filepath = Path(filename)
    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {filename}")
    
    with open(filepath, 'r', encoding=encoding, newline='') as f:
        reader = csv.DictReader(f, delimiter=delimeter)

        for row_num, row in enumerate(reader, start=2):   # Start at 2 (header is row 1)
            try:
                yield row
            except Exception as e:
                logger.error(f"Error reading row {row_num}: {e}")
                raise


def filter_threshold(
        records: Iterator[Dict[str, Any]],
        field: str,
        threshold_value: float,
        comparison: str = 'gt',
) -> Iterator[Dict[str, Any]]:
    """
    Filter records based on numeric field threshold.
    
    Part of ETL pipeline - removes records that don't meet criteria.

    Args:
        records: Input record stream
        field: Field name to check
        threshold: Threshold value
        comparison: Comparison operator ('gt', 'gte', 'lt', 'ltr', 'eq')

    Yields:
        Dict[str, Any]: Records that pass the filter

    Raises:
        ValueError: If comparison operator is invalid
        KeyError: If field doesn't exist in record
        ValueError: If field value cannot be converted to float

    Example:
        >>> records = read_csv('sales.csv')
        >>> high_value = filter_threshold(records, 'amount', 1000, 'gt')
        >>> for record in high_value:
        ...     process_high_value_sale(record)
    """
    comparison_ops = {
        'gt': lambda x, y: x > y,
        'gte': lambda x, y: x >= y,
        'lt': lambda x, y: x < y,
        'lte': lambda x, y: x <= y,
        'eq': lambda x, y: x == y,
    }

    if comparison not in comparison_ops:
        raise ValueError(
            f"Invalid comparison: {comparison}. "
            f"Must be one of {list(comparison_ops.keys())}"
        )
    
    compare_func = comparison_ops[comparison]

    for record in records:
        try:
            # Convert field to float for comparison
            value = float(record[field])

            if compare_func(value, threshold_value):
                yield record
            else:
                logger.debug(f"Filtered out record: {field}={value} (thereshold={threshold_value})")

        except KeyError:
            logger.error(f"Field '{field}' not found in record: {record.keys()}")
            raise
        except (ValueError, TypeError) as e:
            logger.warning(f"Cannot convert {field}={record.get(field)} to number: {e}")
            # Skip invalid records instead of crashing
            continue


def transform_data(
        records: Iterator[Dict[str, Any]],
        transformations: Optional[Dict[str, Callable]] = None
) -> Iterator[Dict[str, Any]]:
    """
    Apply transformations to each record in the stream.

    Flexible transformation stage that can apply different functions to different fields. 

    Args:
        records: Input record stream
        transformations: Dict mapping field names to transformation functions.
                        If None, applies default transformations.

    Yields:
        Dict[str, Any]: Transformed data
    
    Example:
        >>> transforms = {
        ...     'product': str.upper,
        ...     'amount': lambda x: float(x) * 1.1,  # 10% markup
        ...     'region': lambda x: x.strip().title()
        ... }
        >>> records = read_csv('sales.csv')
        >>> transformed = transform_data(records, transforms)
    """
    if transformations is None:
        # Default transformations
        transformations = {
            'product': lambda x: str(x).strip().upper(),
            'amount': lambda x: float(x),
            'region': lambda x: str(x).strip().upper(),
        }

    for record in records:
        transformed_record = record.copy()

        for field, transform_func in transformations.items():
            if field in transformed_record:
                try:
                    transformed_record[field] = transform_func(transformed_record[field])
                except Exception as e:
                    logger.warning(
                        f"Transformation failed for {field}={record.get(field)}: {e}"
                    )
                    # Keep original value on transformation failure
                    continue

        yield transformed_record



def count_records(records: Iterator[Dict[str, Any]]) -> int:
    """
    Count records in a stream (consume the iterator).

    Terminal operation that materializes the stream.

    Args:
        records: Input record stream
    
    Returns:
        int: Number of records 
    """
    return sum(1 for _ in records)



#  Pipeline orchestration
def run_csv_pipeline(
        input_file: str,
        output_file: Optional[str] = None,
        filter_field: Optional[str] = None,
        threshold: Optional[float] = None,
        transformations: Optional[Dict[str, Callable]] = None
) -> PipelineStats:
    """
    Execute complete CSV ETL pipeline with monitoring and error handling.

    Production-ready pipeline that:
    - Reads CSV file
    - Applies filtering
    - Transforms data
    - Writes results (optional)
    - Tracks statistics

    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV (optional)
        filter_field: Field to filter on (optional)
        filter_threshold: Threshold for filtering (optional)
        transformations: Field transformations (optional)

    Returns:
        PipelineStats: Execution Statistics

    Example:
        >>> stats = run_csv_pipeline(
        ...     input_file='sales.csv',
        ...     output_file='high_value_sales.csv',
        ...     filter_field='amount',
        ...     filter_threshold=1000.0
        ... )
        >>> print(f"Processed {stats.records_read} records")
    """
    stats = PipelineStats()

    try:
        #  Build pipeline
        logger.info(f"Starting pipeline: {input_file}")

        # 1. Extract
        records = read_csv(input_file)
        stats.records_read = 0

        # 2. Apply filtering if specified
        if filter_field and threshold is not None:
            records = filter_threshold(records, filter_field, threshold)

        # 3. Apply transformations
        if transformations:
            records = transform_data(records, transformations)

        # 4. Load - Process or write output 
        if output_file:
            with open(output_file, 'w', newline='') as f:
                writer = None

                for record in records:
                    stats.records_read += 1

                    # Initialize writer with first record's keys
                    if writer is None:
                        writer = csv.DictWriter(f, fieldnames=record.keys())
                        writer.writeheader()
                    
                    writer.writerow(record)
                    stats.records_transformed += 1

                    # Process logging
                    if stats.records_read % 1000 == 0:
                        logger.info(f"Processed {stats.records_read:,} records")
        else:
            # Just count if no output file
            for _ in records:
                stats.records_read += 1
                stats.records_transformed += 1
        
        logger.info(
            f"Pipeline completed: {stats.records_read:,} read, "
            f"{stats.records_transformed:,} transformed"
        )
    
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        stats.errors += 1
        raise

    return stats


# Test data generation
def create_test_csv(filename: str = 'test_sales.csv', num_records: int = 1000) -> None:
    """Generate test CSV file for pipeline testing"""
    import random

    products = ['Widget', 'Gadget', 'Doohickey', 'Thingmajig']
    regions = ['North', 'South', 'East', 'West']
    fieldnames = ['id', 'product', 'amount', 'region']

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, num_records + 1):
            writer.writerow({
                'id': i,
                'product': random.choice(products),
                'amount': round(random.uniform(50, 5000), 2),
                'region': random.choice(regions)
            })


if __name__ == "__main__":
    # Example Usage
    create_test_csv('sales.csv', num_records=5000)

    # Run pipeline
    pipeline_stats = run_csv_pipeline(
        input_file='sales.csv',
        output_file='high_value_sales.csv',
        filter_field='amount',
        threshold=1000.0
    )

    print(f"\nPIPELINE STATISTICS:")
    print(f"    Records Read:           {pipeline_stats.records_read:,}")
    print(f"    Records Transformed:    {pipeline_stats.records_transformed:,}")
    print(f"    Errors:                 {pipeline_stats.errors}")