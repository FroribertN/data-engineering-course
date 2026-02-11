"""
PROGRAM: Extensible Data Pipeline Framework
--------------------------------------------

Build a complete ETL pipeline framework using advanced OOP:

Abstract Base Classes:
1. DataSource (ABC)
   - Abstract: connect(), read(), close()
   - Concrete: process() (template method)

2. DataTransformer (ABC)
   - Abstract: transform(data)
   - Concrete: validate(data)

3. DataDestination (ABC)
   - Abstract: connect(), write(data), close()

Concrete Implementations:
4. CSVSource (DataSource)
5. DatabaseSource (DataSource)
6. APISource (DataSource)

7. FilterTransformer (DataTransformer)
8. AggregateTransformer (DataTransformer)
9. CleanTransformer (DataTransformer)

10. CSVDestination (DataDestination)
11. DatabaseDestination (DataDestination)

12. Pipeline class
    - Manages source → transformers → destination
    - Methods: add_transformer(), execute()
    - Class methods: from_config(config_dict)

Features:
- Use abstract classes for interfaces
- Implement polymorphism (any source/destination works)
- Add logging mixin
- Use magic methods where appropriate
- Include proper error handling

Test with a complete pipeline!
"""

from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional
from datetime import datetime
import json
import csv


# ============================================
# 1. MIXINS
# ============================================

class LoggingMixin:
    """Mixin to add logging capability to any class"""
    
    def log(self, message: str, level: str = "INFO"):
        """
        Log a message with timestamp and level.

        Args:
            message: Message to log
            level: Log level (INFO, ERROR, WARNING, SUCCESS)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        class_name = self.__class__.__name__
        print(f"[{timestamp}] [{level:7s}] [{class_name}] {message}")
    
    def log_info(self, message: str):
        """Log an INFO message"""
        self.log(message, "INFO")

    def log_error(self, message: str):
        """Log an ERROR message"""
        self.log(message, "ERROR")

    def log_warning(self, message: str):
        """Log a WARNING message"""
        self.log(message, "WARNING")

    def log_success(self, message: str):
        """Log a SUCCESS message"""
        self.log(message, "SUCCESS")
    

class ValidationMixin:
    """Mixin to add validation capability to any class"""

    def validate_not_empty(self, data: Any, name: str = "data") -> bool:
        """
        Validate that data is not empty

        Args:
            data: Data to validate
            name: Name used in error message

        Raises:
            ValueError: If data is empty
        """
        if not data:
            raise ValueError(f"{name} cannot be empty")
        return True
    
    def validate_type(self, data: Any, expected_type: type, name: str = "data") -> bool:
        """
        Validate that data is of expected type.

        Args:
            data: Data to validate
            expected_type: Expected type
            name: Name used in error message

        Raises:
        TypeError: If data is wrong type
        """
        if not isinstance(data, expected_type):
            raise TypeError(f"{name} must be {expected_type}, got {type(data).__name__}")
        return True
    
    def validate_data_structure(self, data: List[Dict]) -> bool:
        """
        Validate that data is a list of dictionaries.
        
        Args:
            data: Data to validate

        Raises:
            TypeError: If data structure is invalid
        """
        if not isinstance(data, list):
            raise TypeError("Data must be a list")
        
        if data and not all(isinstance(item, dict) for item in data):
            raise TypeError("All items in data must be dictionaries")
        
        return True
    

# ============================================
# 2. ABSTRACT BASE CLASSES
# ============================================

class DataSource(ABC, LoggingMixin, ValidationMixin):
    """
    Abstract base class for all data sources.
    
    All data sources must implement:
        - connect(): Establish connection
        - read(): Read and return data
        - close(): Close connection

    The process() method is a template that calls these in the correct order automatically.
    """

    def __init__(self, name: str):
        """
        Initialize data source.

        Args:
            name: Name/identifier for this source
        """
        self.name = name
        self._is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the data source.

        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def read(self) -> List[Dict[str, Any]]:
        """
        Reead data from the source.

        Returns:
            List of dictionaries representing records
        """
        pass

    @abstractmethod
    def close(self) -> bool:
        """
        Close connection to the data source.

        Returns:
            bool: True if closed successfully
        """
        pass

    def process(self) -> List[Dict[str, Any]]:
        """
        Template method - orchestrates the data reading workflow.

        Automatically:
            1. Connects to the source
            2. Reads the data
            3. Closes the connection

        Returns:
            List of records read from the source
        """
        self.log_info(f"Starting data extraction from: {self.name}")

        try:
            # Stage 1: Connect
            if not self.connect():
                raise ConnectionError(f"Failed to connect to {self.name}")
            
            # Sstage 2: Read data
            data = self.read()
            self.validate_data_structure(data)

            self.log_success(f"Read {len(data)} records from {self.name}")

            return data
        
        finally:
            # Always close, even if error occurred
            self.close()

    def __enter__(self):
        """Support for 'with' statement"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when exiting 'with' block"""
        self.close()
        return False
    
    def __str__(self):
        status = "Connected" if self._is_connected else "Disconnected"
        return f"{self.__class__.__name__} ('{self.name}') [{status}]"
    
    def __repr__(self):
        return f"{self.__class__.__name__} (name='{self.name}')"
    


class DataTransformer(ABC, LoggingMixin, ValidationMixin):
    """
    Abstract base class for all data transformers.

    All transformers must implement:
        - transform(data): Apply transformation and return result
    """

    def __init__(self, name: str):
        """
        Initialize transformer.

        Args:
            name: Name/identifier for this transformer
        """
        self.name = name
    
    @abstractmethod
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply Transformation to data.

        Args:
            data: Input data as list of dictionaries

        Returns:
            Transformed data as list of dictionaries
        """
        pass

    def validate(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate data before transformation.

        Args:
            data: Data to validate

        Returns:
            bool: True if valid
        """
        return self.validate_data_structure(data)
    
    def __call__(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Allow transformer to be called as a function.

        Example:
            clean = CleanTransformer(...)
            result = clean(data)  # Calls transform()
        """
        return self.transform(data)
    
    def __str__(self):
        return f"{self.__class__.__name__} ('{self.name}')"
    
    def __repr__(self):
        return f"{self.__class__.__name__} (name='{self.name}')"
    

class DataDestination(ABC, LoggingMixin, ValidationMixin):
    """
    Abstract base class for all data destinations.
    
    All destinations must implement:
        - connection() - Establish connection
        - write(data) - Write data to destination
        - close(): Close connection

    The process() method is a template that calls these in the correct order automatically.
    """

    def __init__(self, name: str):
        """
        Initialize destination.

        Args:
            name: Name/identifier for this destination
        """
        self.name = name
        self._is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to this destination.

        Returns:
            bool: True if connection successful
        """
        pass

    @abstractmethod
    def write(self, data: List[Dict[str, Any]]) -> bool:
        """
        Write data to the destination.

        Args:
            data: Data to write
        
        Returns:
            bool: True if write successful
        """
        pass

    @abstractmethod
    def close(self) -> bool:
        """
        Close connection to the destination.

        Returns:
            bool: True if closed successfully
        """
        pass

    def process(self, data: List[Dict[str, Any]]) -> bool:
        """
        Template method - orchestrates the data writing workflow.

        Automatically:
            1. Validate the data
            2. Connects to the destination
            3. Writes the data
            4. Closes the connection

        Args:
            data: Data to write

        Returns:
            bool: True if successful
        """
        self.log_info(f"Starting load data to: {self.name}")

        try:
            # Step 1: Validate data
            self.validate_data_structure(data)

            # Step 2: Connect
            if  not self.connect():
                raise ConnectionError(f"Failed to connect to {self.name}")
            
            # Step 3: Write data
            if not self.write(data):
                raise IOError(f"Failed to write data to {self.name}")
            
            self.log_success(f"Wrote {len(data)} records to {self.name}")

            return True
        
        finally:
            # Always close, even if error occurred
            self.close()

    
    def __enter__(self):
        """Support for 'with' statement"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when exiting 'with' block"""
        self.close()
        return False
    
    def __str__(self):
        status = "Connected" if self._is_connected else "Disconnected"
        return f"{self.__class__.__name__} ('{self.name}') [{status}]"
    
    def __repr__(self):
        return f"{self.__class__.__name__} (name={self.name})"
    


# ============================================
# 3. DATA SOURCES (Concrete Implementations)
# ============================================

class CSVSource(DataSource):
    """
    Read data from CSV files.
    
    Example:
        source = CSVSource("employees.csv")
        data = source.process()
    """

    def __init__(self, filepath: str, name: Optional[str] = None):
        """
        Initialize CSV source.

        Args:
            filepath: Path to CSV file
            name: Optional display name (defaults to filepath)
        """
        super().__init__(name or filepath)
        self.filepath = filepath
        self._file_handle = None

    def connect(self) -> bool:
        """Open the CSV file for reading"""
        try:
            self.log_info(f"Opening CSV file: {self.filepath}")
            self._file_handle = open(self.filepath, "r", encoding="utf-8")
            self._is_connected = True
            return True
        except FileNotFoundError:
            self.log_error(f"File not found: {self.filepath}")
            return False
        except Exception as e:
            self.log_error(f"Error opening file: {e}")
            return False
        
    def read(self) -> List[Dict[str, Any]]:
        """Read all rows from CSV file"""
        if not self._is_connected:
            raise ConnectionError("Not connected to CSV file")
        
        reader = csv.DictReader(self._file_handle)
        data = [dict(row) for row in reader]
        self.log_info(f"Read {len(data)} rows from CSV")

        return data
    
    def close(self) -> bool:
        """Close the CSV file"""
        if self._file_handle:
            self._file_handle.close()
            self._is_connected = False
            self.log_info("CSV file closed")
        return True


class DatabaseSource(DataSource):
    """
    Read data from a database(simulated).
    
    In production, this would uuse SQLAlchemy, psycopg2, etc.

    Example:
        source = DatabaseSource("postgresql://localhost/hr", "employees")
        data = source.process()
    """
    
    def __init__(self, connection_string: str, table: str, name: Optional[str] = None):
        """
        Initialize database source.

        Args:
            connection_string: Database connection string
            table: Table name to read from
            name: Optional display name
        """
        super().__init__(name or f"DB:{table}")
        self.connection_string = connection_string
        self.table = table
        self._connection = None

    def connect(self) -> bool:
        """Establish database connection"""
        self.log_info(f"Connecting to database: {self.connection_string}")
        # Simulated connection
        self._connection = f"Connection {self.connection_string}"
        self._is_connected = True
        return True
    
    def read(self) -> List[Dict[str, Any]]:
        """Execute SELECT query and return resuults"""
        if not self._is_connected:
            raise ConnectionError("Not connected to database")
        
        self.log_info(f"Executing query: SELECT * FROM {self.table}")

        # Simulated query data
        simulated_data = {
            "employees": [
                {"id": 1, "name": "Alice", "department": "Engineering", "salary": 75000},
                {"id": 2, "name": "Bob", "department": "Sales", "salary": 65000},
                {"id": 3, "name": "Charlie", "department": "Engineering", "salary": 80000},
                {"id": 4, "name": "Diana", "department": "HR", "salary": 60000},
                {"id": 5, "name": "Eve", "department": "Sales", "salary": 70000},
            ],
            "orders": [
                {"order_id": 1, "customer": "Alice", "total": 250.00, "status": "completed"},
                {"order_id": 2, "customer": "Bob", "total": 150.00, "status": "pending"},
                {"order_id": 3, "customer": "Charlie", "total": 500.00, "status": "completed"},
            ]
        }

        # Return data for requested table, or empty list
        data = simulated_data.get(self.table, [])
        self.log_info(f"Retrieved {len(data)} records")

        return data
    
    def close(self) -> bool:
        """Close database connection"""
        if self._connection:
            self.log_info("Closing database connection")
            self.connection = None
            self._is_connected = False
        return True
    


class APISource(DataSource):
    """
    Read data from an API (simulated)

    In production, this would use the requests library.

    Example:
        source = APISource("https://api.example.com", "users")
        data = source.process()
    """

    def __init__(self, base_url: str, endpoint: str, name: Optional[str] = None):
        """
        Initialize API source.

        Args:
            base_url: Base url of the API
            endpoint: API endpoint to fetch from
            name: Optional display name
        """
        super().__init__(name or f"API:{endpoint}")
        self.base_url = base_url
        self.endpoint = endpoint
        self._session = None

    def connect(self) -> bool:
        """Create API session"""
        self.log_info(f"Connecting to API: {self.base_url}/{self.endpoint}")
        # Simulated session
        self._session = f"Session({self.base_url})"
        self._is_connected = True
        return True
    
    def read(self) -> List[Dict[str, Any]]:
        """Fetch data from API endpoint"""
        if not self._is_connected:
            raise ConnectionError("No active API session")
        
        self.log_info(f"GET {self.base_url}/{self.endpoint}")

        # Simulated API responses
        simulated_responses = {
        "users": [
                {"user_id": 101, "username": "alice_j", "email": "alice@example.com"},
                {"user_id": 102, "username": "bob_s", "email": "bob@example.com"},
                {"user_id": 103, "username": "charlie_b", "email": "charlie@example.com"},
            ],
            "events": [
                {"user_id": 101, "event": "login", "timestamp": "2025-01-20 10:00:00"},
                {"user_id": 102, "event": "purchase", "timestamp": "2025-01-20 10:15:00"},
                {"user_id": 101, "event": "logout", "timestamp": "2025-01-20 11:00:00"},
                {"user_id": 103, "event": "login", "timestamp": "2025-01-20 11:30:00"},
            ]
        }

        data = simulated_responses.get(self.endpoint, [])
        self.log_info(f"Received {len(data)} records")

        return data
    
    def close(self) -> bool:
        """Close API session"""
        if self._session:
            self.log_info("Closing API session")
            self._session = None
            self._is_connected = False
        return True



# ============================================
# 4. DATA TRANSFORMERS (Concrete Emplementations)
# ============================================

class FilterTransformer(DataTransformer):
    """
    Filter records based on a field condition.
    
    Supported operators: ==, !=, >, <, >=, <=, in, not in

    Example:
        # Keep only records where salary >= 65000
        transformer = FilterTransformer("salary", 65000, ">=")
        filtered_data = transformer.transform(data)
    """

    VALID_OPERATORS = ["==", "!=", ">", "<", ">=", "<=", "in", "not in"]

    def __init__(self, field: str, value: Any, operator: str = "==", name: Optional[str] = None):
        """
        Initialize filter transformer.
        
        Args:
            field: Field name to filter on
            value: Value to compare against
            operator: Comparison operator
            name: Optional display name
        """
        super().__init__(name or f"Filter({field} {operator} {value})")

        if operator not in self.VALID_OPERATORS:
            raise ValueError(
                f"Invalid operator '{operator}'."
                f"Valid operators: {self.VALID_OPERATORS}"
            )
        self.field = field
        self.value = value
        self.operator = operator

    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply filter to data"""
        self.validate(data)
        self.log_info(
            f"Filtering {len(data)} records: "
            f"where {self.field} {self.operator} {self.value}"
        )

        filtered = [
            record for record in data if self._matches(record.get(self.field))
        ]

        self.log_info(f"Filter result: {len(filtered)}/len{len(data)} records kept")

        return filtered
    
    def _matches(self, record_value: Any) -> bool:
        """Check if a value matches the filter condition"""
        if record_value is None:
            return False
        
        operations = {
            "==":       lambda v: v == self.value,
            "!=":       lambda v: v != self.value,
            ">":        lambda v: v > self.value,
            "<":        lambda v: v < self.value,
            ">=":       lambda v: v >= self.value,
            "<=":       lambda v: v <= self.value,
            "in":       lambda v: v in self.value,
            "not in":   lambda v: v not in self.value,
        }

        try:
            return operations[self.operator](record_value)
        except TypeError:
            return False
    


class AggregateTransformer(DataTransformer):
    """
    Aggregate data by grouping on a field.
    
    Supported operations: sum, avg, count, min, max

    Example:
        # Get average salary per department
        transformer = AggregateTransformer("department", "salary", "avg")
        aggregated = transformer.transform(data)
        # Returns [{department": Engineering", "salary_avg": 77500}, ....]
    """

    VALID_OPERATIONS = ["sum", "avg", "count", "min", "max"]

    def __init__(self, group_by: str, aggregate_field: str, operation: str = "sum", name: Optional[str] = None):
        """
        Initialize aggregate transformer.

        Args:
            group_by: Field to group records by
            aggregate_field: Field to apply aggregation on
            operation: Aggregate operation (sum, avg, count, min, max)
            name: Optional display name
        """
        super().__init__(name or f"Aggregate({operation}({aggregate_field}) by {group_by})")

        if operation not in self.VALID_OPERATIONS:
            raise ValueError(
                f"Invalid operation '{operation}'. "
                f"Valid operations: {self.VALID_OPERATIONS}"
            )
        
        self.group_by = group_by
        self.aggregate_field = aggregate_field
        self.operation = operation

    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply aggregation to data"""
        self.validate(data)
        self.log_info(
            f"Aggregating {len(data)} records: "
            f"{self.operation}({self.aggregate_field}) "
            f"grouped by {self.group_by}"
        )

        # Group records
        groups = {}
        for record in data:
            key = record.get(self.group_by, "Unknown")
            if key not in groups:
                groups[key] = []
            groups[key].append(record)
        
        # Aggregate each group
        result = []
        output_field = f"{self.aggregate_field}_{self.operation}"

        for group_value, records in sorted(groups.items()):
            aggregated = {self.group_by: group_value}
            values = [
                r.get(self.aggregate_field, 0) for r in records if r.get(self.aggregate_field) is not None
            ]

            if self.operation == "count":
                aggregated[output_field] = len(records)
            elif self.operation == "sum":
                aggregated[output_field] = sum(values)
            elif self.operation == "avg":
                aggregated[output_field] = (round(sum(values) / len(values), 2) if values else 0)
            elif self.operation == "min":
                aggregated[output_field] = min(values) if values else None
            elif self.operation == "max":
                aggregated[output_field] = max(values) if values else None
            
            result.append(aggregated)

        self.log_info(f"Aggregated into {len(result)} groups")

        return result
    


class CleanTransformer(DataTransformer):
    """
    Clean and standardize data.
    
    Supported operations:
        - remove_nulls:         Remove records with nulls/None values
        - trim_strings:         Strip whitespace from string values
        - lowercase:            Convert all strings to lowercase
        - uppercase:            Convert all strings to uppercase
        - remove_duplicates:    Remove duplicate records

    Example:
        transformer = CleanTransformer(["remove_nulls", "trim_strings"])
        cleaned_data = transformer.transform(data)
    """

    VALID_OPERATIONS = [
        "remove_nulls",
        "trim_strings",
        "lowercase",
        "uppercase",
        "remove_duplicates"
    ]

    def __init__(self, operations: List[str], name: Optional[str] = None):
        """
        Initialize clean transformer.

        Args:
            operations: List of cleaning operations to by
            name: Optional display name
        """
        super().__init__(name or f"Clean({', '.join(operations)})")

        invalid = [op for op in operations if op not in self.VALID_OPERATIONS]
        if invalid:
            raise ValueError(
                f"Invalid operations: {invalid}. "
                f"Valid operations: {self.VALID_OPERATIONS}"
            )

        self.operations = operations

    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all cleaning operations in sequence"""
        self.validate(data)
        self.log_info(
            f"Cleaning {len(data)} records with: "
            f"{', '.join(self.operations)}"
        )

        result = data.copy()

        operation_map = {
            "remove_nulls":         self._remove_nulls,
            "trim_strings":         self._trim_strings,
            "lowercase":            self._lowercase_strings,
            "uppercase":            self._uppercase_strings,
            "remove_duplicates":    self._remove_duplicates,
        }

        for operation in self.operations:
            before_count = len(result)
            result = operation_map[operation](result)
            after_count = len(result)

            if before_count != after_count:
                self.log_info(f"  {operation}: {before_count} → {after_count} records")

        self.log_info(f"Cleaning complete: {len(result)} records remaining")

        return result
    
    def _remove_nulls(self, data: List[Dict]) -> List[Dict]:
        """Remove records that have any null/None values"""
        return [
            record for record in data
            if all(v is not None and v != "" for v in record.values())
        ]
    
    def _trim_strings(self, data: List[Dict]) -> List[Dict]:
        """Strip leading/trailing whitespace from all string values"""
        return [
            {k: v.strip() if isinstance(v, str) else v for k, v in record.items()} 
            for record in data
        ]
    
    def _lowercase_strings(self, data: List[Dict]) -> List[Dict]:
        """Converts all string values to lowercase"""
        return [
            {k: v.lower() if isinstance(v, str) else v for k, v in record.items()}
            for record in data
        ]
    
    def _uppercase_strings(self, data: List[Dict]) -> List[Dict]:
        """Convert all string values to uppercase"""
        return [
            {k: v.upper() if isinstance(v, str) else v for k, v in record.items()}
            for record in data
        ]
    
    def _remove_duplicates(self, data: List[Dict]) -> List[Dict]:
        """Remove duplicate records"""
        seen = set()
        result = []

        for record in data:
            # Convert dict a hashable frozenset for deduplication
            record_key = frozenset((k, str(v)) for k, v in sorted(record.items()))
            
            if record_key not in seen:
                seen.add(record_key)
                result.append(record)

        return result
    


class SelectTransformer(DataTransformer):
    """
    Select specific fields from records.
    
    Example:
        # Keep only name and salary fields
        transformer = SelectTransformer(["name", "salary"])
        selected = transformer.transform(data)
    """

    def __init__(self, fields: List[str], name: Optional[str] = None):
        """
        Initialize select transformer.

        Args:
            fields: List of field names to keep
            name: Optional display name
        """
        super().__init__(name or f"Select({', '.join(fields)})")

        if not fields:
            raise ValueError("Fields list cannot be empty")
        
        self.fields = fields

    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Select only specified fields in each record"""
        self.validate(data)
        self.log_info(
            f"Selecting {len(self.fields)} fields from "
            f"{len(data)} records: {', '.join(self.fields)}"
        )

        result = [
            {field: record[field] for field in self.fields if field in record}
            for record in data
        ]

        return result
    


# ============================================
# 5. DATA DESTINATIONS (Concrete Emplementations)
# ============================================

class CSVDestination(DataDestination):
    """
    Write data to a CSV file.
    
    Example: 
        destination = CSVDestination("output.csv")
        destination.process()
    """

    def __init__(self, filepath: str, name: Optional[str] = None):
        """
        Initialize CSV destination.

        Args:
            filepath: Path to output CSV file
            name: Optional display name
        """
        super().__init__(name or filepath)
        self.filepath = filepath
        self._file_handle = None

    def connect(self) -> bool:
        """Open the CSV file for writing"""
        try:
            self.log_info(f"Opening CSV file for writing: {self.filepath}")
            self._file_handle = open(self.filepath, "w", newline="", encoding="utf-8")
            self._is_connected = True
            return True
        except Exception as e:
            self.log_error(f"Could not open file: {e}")
            return False
        
    def write(self, data: List[Dict[str, Any]]) -> bool:
        """Write data rows to CSV"""
        if not self._is_connected:
            raise ConnectionError("File is not open")
        
        if not data:
            self.log_warning("No data to write")
            return True
        
        # Get all unique keys for headers
        fieldnames = list(data[0].keys())

        writer = csv.DictWriter(self._file_handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

        return True
    
    def close(self) -> bool:
        """Close the CSV file"""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
            self._is_connected = False
            self.log_info("CSV file closed")
        return True
    

class DatabaseDestination(DataDestination):
    """Simulated database destination"""
    
    def __init__(self, connection_string: str, table: str, name: Optional[str] = None):
        """
        Initialize database destination.

        Args:
            connection_string: Database connection string
            table: Table name to write to
            name: Optional name
        """
        super().__init__(name or f"DB:{table}")
        self.connection_string = connection_string
        self.table = table
        self.connection = None

    def connect(self) -> bool:
        """Simulate database connection"""
        self.log_info(f"Connecting to database: {self.connection_string}")
        self.connection = f"Connection to {self.connection_string}"
        self._is_connected = True
        return True
    
    def write(self, data: List[Dict[str, Any]]) -> bool:
        """Simulate writing to database"""
        if not self._is_connected:
            raise ConnectionError("Not connected to database")
        
        self.log_info(f"Inserting {len(data)} records to {self.table}")

        # In real implementation, would execute INSERT statements
        for record in data:
            fields = ', '.join(record.keys())
            values = ', '.join(f"'{v}'" if isinstance(v, str) else str(v) for v in record.values())
            query = f"INSERT INTO {self.table} ({fields}) VALUES ({values})"
            # Would execute query here
        
        return True
    
    def close(self) -> bool:
        """Close database connection"""
        if self.connection:
            self.log_info("Closing database connection")
            self.connection = None
            self._is_connected: False
        return True
    

class JSONDestination(DataDestination):
    """Write data to JSON files"""

    def __init__(self, filepath: str, name: Optional[str] = None):
        """
        Initialize JSON destination.

        Args:
            filepath: Path to output JSON file
            name: Optional name
        """
        super().__init__(name or filepath)
        self.filepath = filepath
        self.file_handle = None

    def connect(self) -> bool:
        """Open the JSON file to writing"""
        try:
            self.log_info(f"Opening JSON file for writing: {self.filepath}")
            self.file_handle = open(self.filepath, 'w', encoding='utf-8')
            self._is_connected = True
            return True
        except Exception as e:
            self.log_error(f"Error opening file: {e}")
            return False
        
    def write(self, data: List[Dict[str, Any]]) -> bool:
        """Write data to JSON"""
        if not self._is_connected:
            raise ConnectionError("Not connected to JSON file")
        
        json.dump(data, self.file_handle, indent=2)

        return True
    
    def close(self) ->bool:
        """Close the JSON file"""
        if self.file_handle:
            self.file_handle.close()
            self._is_connected = False
            self.log_info("JSON file closed")
        return True



# ============================================
# 6. PIPELINE CLASS
# ============================================

class Pipeline(LoggingMixin):
    """Main pipeline class that orchestrates the ETL process"""

    def __init__(self, name: str):
        """
        Initialize pipeline.

        Args:
            name: Pipeline name
        """
        self.name = name
        self.source = None
        self.transformers = []
        self.destination = None
        self.execution_time = None
        self.records_processed = 0

    def set_source(self, source: DataSource):
        """Set the data source"""
        self.source = source
        self.log_info(f"Source set: {source}")
        return self  # For method chaining - assembly line
    
    def add_transformer(self, transformer: DataTransformer):
        """Add a transformer to the pipeline"""
        self.transformers.append(transformer)
        self.log_info(f"Added transformer: {transformer}")
        return self  # For method chaining
    
    def set_destination(self, destination: DataDestination):
        """Set the data destination"""
        self.destination = destination
        self.log_info(f"Destination set: {destination}")
        return self  # For method chaining
    
    def execute(self) -> bool:
        """
        Execute the pipeline.

        Returns:
            bool: True if successful
        """
        if not self.source:
            raise ValueError("No data source configured")
        
        if not self.destination:
            raise ValueError("No data destination configured")
        
        self.log_info("=" * 70)
        self.log_info(f"EXECUTING PIPELINE: {self.name}")
        self.log_info("=" * 70)

        start_time = datetime.now()

        try:
            # Extract
            self.log_info("STEP 1: EXTRACT")
            data = self.source.process()
            self.records_processed = len(data)

            # Transform
            if self.transformers:
                self.log_info(f"STEP 2: TRANSFORM ({len(self.transformers)} transformers)")
                for i, transformer in enumerate(self.transformers, 1):
                    self.log_info(f"    Transformer {i}/{len(self.transformers)}: {transformer}")
                    data = transformer.transform(data)
                    self.log_info(f"    Result: {len(data)} records")

            # Load
            self.log_info("STEP 3: LOAD")
            self.destination.process(data)

            # Success
            end_time = datetime.now()
            self.execution_time = (end_time - start_time).total_seconds()

            self.log_success("=" * 70)
            self.log_success(f"PIPELINE COMPLETED SUCCESSFULLY")
            self.log_success(f"Records Processed: {self.records_processed}")
            self.log_success(f"Final Records: {len(data)}")
            self.log_success(f"Execution Time: {self.execution_time:.2f} seconds")
            self.log_success("=" * 70)
            
            return True
        
        except Exception as e:
            self.log_error("=" * 70)
            self.log_error(f"PIPELINE FAILED: {str(e)}")
            self.log_error("=" * 70)
            raise

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'Pipeline':
        """
        Create pipeline from configuration dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            Configured Pipeline instance

        Example config:
        {
            "name": "My Pipeline",
            "source": {"type": "csv", "filepath": "input.csv"},
            "transformers": [
                {"type": "filter", "field": "age", "value": 18, "operator": ">"},
                {"type": "select", "fields": ["name", "age"]}
            ],
            "destination": {"type": "json", "filepath": "output.json"}
        }
        """
        pipeline = cls(config["name"])

        # Configure source

        # 1. Access the list
        source_list = config["source"]
        # 2. Grab the first dictionary inside the list using [0]
        source_config = source_list[0]
        # 3. Access "type"
        source_type = source_config["type"]

        if source_type == "csv":
            source = CSVSource(source_config["filepath"])
        elif source_type == "database":
            source = DatabaseSource(source_config["connection_string"], source_config["table"])
        elif source_type == "api":
            source = APISource(source_config["base_url"], source_config["endpoint"])
        else:
            raise ValueError(f"Uknown source type: {source_type}")
        
        pipeline.set_source(source)

        # Configure transformers
        for trans_config in config.get("transformers", []):
            trans_type = trans_config["type"]

            if trans_type ==  "filter":
                transformer = FilterTransformer(
                    trans_config["field"],
                    trans_config["value"],
                    trans_config.get("operator", "==")
                )
            elif trans_type == "aggregate":
                transformer = AggregateTransformer(
                    trans_config["group_by"],
                    trans_config["aggregate_field"],
                    trans_config.get("operation", "sum")
                )
            elif trans_type == "clean":
                transformer = CleanTransformer(trans_config["operations"])
            elif trans_type == "select":
                transformer = SelectTransformer(trans_config["fields"])
            else:
                raise ValueError(f"Unknown transformer type: {trans_type}")
            
            pipeline.add_transformer(transformer)
        
        # Configure destination
        dest_config = config["destination"]
        dest_type = dest_config["type"]

        if dest_type ==  "csv":
            destination = CSVDestination(dest_config["filepath"])
        elif dest_type ==  "database":
            destination = DatabaseDestination(
                dest_config["connection_string"],
                dest_config["table"]
            )
        elif dest_type == "json":
            destination = JSONDestination(dest_config["filepath"])
        else:
            raise ValueError(f"Unknown destination type: {dest_type}")
        
        pipeline.set_destination(destination)

        return pipeline
    
    def get_summary(self) -> str:
        """Get pipeline summary"""
        summary = f"""
Pipeline Summary:
-----------------
Name:           {self.name}
Source:         {self.source}
Transformers:   {len(self.transformers)}
Destination:    {self.destination}
"""
        for i, transformer in enumerate(self.transformers, 1):
            summary += f"{i}. {transformer}\n"
            if self.execution_time:
                summary += f"\nLast Execution: {self.execution_time:.2f} seconds"
                summary += f"\nRecords Processed: {self.records_processed}"
            
            return summary
        
    # Magic methods
    def __str__(self):
        return f"Pipeline('{self.name}')"
    
    def __repr__(self):
        return f"Pipeline(name='{self.name}', transformers={len(self.transformers)})"
    
    def __len__(self):
        """Number of transformers in the pipeline"""
        return len(self.transformers)
    
    def __contains__(self, transformer: DataTransformer):
        """Check if transformer is in pipeline"""
        return transformer in self.transformers
    
    def __iter__(self):
        """Iterate over transformers"""
        return iter(self.transformers)
    
    def __iadd__(self, transformer: DataTransformer):
        """Pipeline += transformer"""
        self.add_transformer(transformer)
        return self
    


# ============================================
# 7. PIPELINE FACTORY
# ============================================

class PipelineFactory(LoggingMixin):
    """Factory class for creating pre-configured pipelines"""

    @staticmethod
    def create_csv_to_json_pipeline(input_file: str, output_file: str, name: str = "CSV to JSON") -> Pipeline:
        """Create a simple CSV to JSON pipeline"""
        pipeline = Pipeline
        pipeline.set_source(CSVSource(input_file))
        pipeline.set_destination(JSONDestination(output_file))
        return pipeline
    
    @staticmethod
    def create_db_to_csv_pipeline(connection_string: str, table: str, output_file: str, name: str = "DB to CSV") -> Pipeline:
        """Create a database to CSV pipeline"""
        pipeline = Pipeline(name)
        pipeline.set_source(DatabaseSource(connection_string, table))
        pipeline.set_destination(CSVDestination(output_file))
        return pipeline
    
    @staticmethod
    def create_api_pipeline(base_url: str, endpoint: str, output_file: str, filters: Optional[List[Dict]] = None, name: str = "API Pipeline") -> Pipeline:
        """Create an API data pipeline with optional filters"""
        pipeline = Pipeline(name)
        pipeline.set_source(APISource(base_url, endpoint))

        # Add filters if provided
        if filters:
            for filter_config in filters:
                pipeline.add_transformer(FilterTransformer(**filter_config))
        
        pipeline.set_destination(JSONDestination(output_file))
        return pipeline
    


# ============================================
# 8. MAIN PROGRAM
# ============================================

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}\n")

def main():
    """Demonstrates all pipeline features"""
    print("=" * 70)
    print("DATA PIPELINE FRAMEWORK".center(70))
    print("=" * 70)
    print("Showcasing OOP: Abstract classes, Inheritance, Polymorphism")
    print("=" * 70)

# ============================================
# DEMO 1. Database to JSON Pipeline
# ============================================

    print_section("DEMO 1: Databaase → Filter → Select → JSON")

    pipeline1 = (
        Pipeline("Employee Data Pipeline")
        .set_source(DatabaseSource("postgresql://localhost?hr", "employees"))
        .add_transformer(FilterTransformer("salary", 65000, ">="))
        .add_transformer(SelectTransformer(["name", "department", "salary"]))
        .set_destination(JSONDestination("high_salary_employees.json"))
    )

    pipeline1.execute()
    print(pipeline1.get_summary())

    # ============================================
    # DEMO 2. API to CSV Pipeline
    # ============================================

    print_section("DEMO 2: API → Clean → Aggregate → CSV")

    pipeline2 = (
        Pipeline("User Events Pipeline")
        .set_source(APISource("https://api.example.com", "events"))
        .add_transformer(CleanTransformer(["remove_nulls", "trim_strings"]))
        .set_destination(CSVDestination("cleaned_events.csv"))
    )

    pipeline2.execute()
    print(pipeline2.get_summary())

    # ============================================
    # DEMO 3. Pipeline with Aggregations
    # ============================================

    print_section("DEMO 3: Database → Aggregate by Department → JSON")

    pipeline3 = (
        Pipeline("Salary Analysis Pipeline")
        .set_source(DatabaseSource("postgresql://localhost/hr", "employees"))
        .add_transformer(AggregateTransformer("department", "salary", "avg"))
        .set_destination(JSONDestination("salary_by_department.json"))
    )

    pipeline3.execute()
    print(pipeline3.get_summary())

    # ============================================
    # DEMO 4. Pipeline from Config
    # ============================================

    print_section("DEMO 4: Pipeline from Configuration Dictioonary")

    config = {
        "name": "Config-Based Pipeline",
        "source": [
            {
            "type": "database",
            "connection_string": "mysql://localhost/sales",
            "table": "orders"
            }
        ],
        "transformers": [
            {
                "type": "filter",
                "field": "salary",
                "value": 70000,
                "operator": ">"
            },
            {
                "type": "select",
                "fields": ["name", "department", "salary"]
            }
        ],
        "destination": {
            "type": "json",
            "filepath": "config_pipeline_output.json"
        }
    }

    pipeline4 = Pipeline.from_config(config)
    pipeline4.execute()
    print(pipeline4.get_summary())

    # ============================================
    # DEMO 5. Pipeline Factory
    # ============================================

    print_section("DEMO 5: Using Pipeline Factory")

    # Create pipeline using factory
    pipeline5 = PipelineFactory.create_db_to_csv_pipeline(
        connection_string="postgresql://localhost/hr",
        table="employees", output_file="all_employees.csv",
        name="DB to CSV Factory Pipeline"
        )

    pipeline5.execute()
    print(pipeline5.get_summary())

    # ============================================
    # DEMO 6. Magic Methods
    # ============================================

    print_section("DEMO 6: Pipeline Magic Methods")
    pipeline6 = Pipeline("Magic Methods Demo")
    pipeline6.set_source(DatabaseSource("localhost/db", "users"))
    pipeline6.set_destination(JSONDestination("output.json"))

    # __len__
    print(f"Number of transformers: {len(pipeline6)}")

    # __iadd__
    pipeline6 += FilterTransformer("salary", 60000, ">=")
    pipeline6 += CleanTransformer(["remove_nulls"])

    print(f"After adding transformers: {len(pipeline6)}")

    # __iter__
    print("Transformers in pipeline:")
    for transformer in pipeline6:
        print(f"    - {transformer}")

    # __contains__
    filter_t = FilterTransformer("age", 18, ">=")
    pipeline6 += filter_t
    print(f"Contains filter_t: {filter_t in pipeline6}")

    # __str__ and __repr__
    print(f"str: {str(pipeline6)}")
    print(f"repr: {repr(pipeline6)}")

    # ============================================
    # DEMO 7. Conext Manager Support
    # ============================================

    print("DEMO 7: Conext Manager Support")

    # Use data source as context manager
    db_source = DatabaseSource("localhost/db", "users")

    with db_source as source:
        data = source.read()
        print(f"Read {len(data)} records using context manager")

    print("Connection automatically closed after 'with' block")

    # ============================================
    # DEMO . Polymorphism
    # ============================================

    print_section("DEMO 8: Polymorphism - Same Interface, Different Sources")

    # Clean different sources
    sources = [
        DatabaseSource("localhost/db", "employees", "Database"),
        APISource("https://api.example.com", "users", "API"),
    ]

    # Process each source the same way
    destination = JSONDestination("polymorphism_output.json")

    for source in sources:
        print(f"\nProcessing source: {source}")
        data = source.process()
        print(f"Got {len(data)} records from {source}")

    # ============================================
    # FINAL SUMMARY
    # ============================================

    print_section("PIPELINE FRAMEWORK SUMMARY")

    print("Abstract Classes Used:")
    print(" - DataSource (ABC) → CSVSource, DatabaseSource, APISource")
    print(" - DataTransformer (ABC) → FilterTransformer, AggregateTransformer, CleanTransformer, SelectTransformer")
    print(" - DataDestination (ABC) → CSVDestination, DatabaseDestination, JSONDestination")

    print("\nOOP Concepts Demonstrated:")
    print(" - Abstract Base Classes (cannot be instantiated)")
    print(" - Inheritance (all sources inherit DataSource)")
    print(" - Method Overriding (connect, read, close)")
    print(" - Polymorphism (same interface, different behaviours)")
    print(" - Multiple Inheritance (LoggingMixin, ValidationMixin)")
    print(" - Mixins (LoggingMixin, ValidationMixin)")
    print(" - Class Methods (from_config factory method)")
    print(" - Static Method (PipelineFactory methods)")
    print(" - Magic Methods (__len__, __iter__, __contains__, __iadd__)")
    print(" - Conext Managers (__enter__, __exit__)")
    print(" - Method Chaining (.set_source().add_transformer().set_destination())")

    print("\nPipelines Demonstrates:")
    print(" 1. Database → Filter → Select → JSON")
    print(" 2. API → Clean → CSV")
    print(" 3. Database → Aggregate → JSON")
    print(" 4. Config-based pipeline creation")
    print(" 5. Factory pattern pipeline creation")
    print(" 6. Magic methods on pipeline")
    print(" 7. Context manager usage")
    print(" 8. Polymorphism with different sources")

    print("\n" + "=" * 70)
    print("FRAMEWORK DEMONSTRATION COMPLETE!".center(70))
    print("-=" * 70)


if __name__ == "__main__":
    main()