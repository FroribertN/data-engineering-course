"""
PROGRAM: Lambda Functions and Variable Arguments
--------------------------------------------------

1. create_multiplier(n)
   - Return a lambda function that multiplies by n
   - Example: times_3 = create_multiplier(3)
              times_3(5) → 15

2. sort_students(students, by="name")
   - students: list of dicts [{"name": "Alice", "age": 20, "grade": 85}, ...]
   - Sort by specified key using lambda
   - Return sorted list

3. filter_data(data, **criteria)
   - data: list of dictionaries
   - Filter based on any number of criteria
   - Example: filter_data(students, grade=85, city="Sydney")
   - Return matching items

4. calculate(*args, operation="+")
   - Accept any number of numbers
   - Apply operation: "+", "-", "*", "/"
   - Use lambda functions for operations
   - Return result

5. create_logger(prefix="LOG"):
   - Return a function that logs messages with prefix
   - Use closure
   - Example: log = create_logger("INFO")
              log("Starting process") → "[INFO] Starting process"

6. apply_functions(value, *functions)
   - Apply multiple functions in sequence
   - Example: apply_functions(5, lambda x: x*2, lambda x: x+10)
              Result: 20 (5*2=10, 10+10=20)

7. flexible_search(items, **search_params)
   - items: list of dictionaries
   - Search by any fields
   - Use lambda for filtering
   - Return all matches

8. statistics_calculator(*numbers, **options)
   - Calculate various statistics
   - numbers: any amount of numbers
   - options: include_median=True, include_mode=True, etc.
   - Return dictionary with requested stats
"""

# 1. Multiplier Factory (Closure)
def create_multiplier(n):
    """ 
    Creates a function that multiplies its input by a fixed factor n.

    Args:
        n (int/float): The multiplier factor.
    
    Returns:
        function: a lambda function that accepts 'x' and returns x * n.
    """
    return lambda x: x * n

# 2. Student Data Sorter
def sort_students(students, by="name"):
    """
    Sorts a list of student dictionaries based on a specific attribute.

    Args:
        students (list): A list of dicts (e.g., [{"name": "Alice", "age": 31}])
        by (str): The dictionary key to sort by. Default to "name".

    Returns:
        list: A new list of dictionaries sorted by the specific key.
    """
    return sorted(students, key=lambda s: s.get(by))

# 3. Exact Multi-Criteria Filter
def filter_data(data, **criteria):
   """
   Filters a list ofdictionaries based on multiple exact-match criteria.

   Args:
      data (list): List of dictionaries to filter.
      **criteria: Arbitrary keyword arguments representing key-value pairs to match.

   Returns:
      list: Dictionariees that satisfy ALL criteria provided.
   """
   return [item for item in data if all(item.get(k) == v for k, v in criteria.items())]

# 4. Functional Calculator
def calculate(*args, operation="+"):
   """
   Performs an arithmetic operation across an arbitrary number of values.

   Args:
      *args: Variable number of numeric values
      operation (str): One of "+", "-", "*", "/".

   Returns:
      float/int: The result of the reduction. Returns 0 if no args provided.
   """
   if not args:
      return 0
   
   ops = {
      "+": lambda x, y: x + y,
      "-": lambda x, y: x - y,
      "*": lambda x, y: x * y,
      "/": lambda x, y: x / y if y != 0 else 0
   }

   result = args[0]
   for value in args[1:]:
      result = ops[operation](result, value)
   return result

# 5. Logger Factory
def create_logger(prefix="LOG"):
   """
   Creates a specialized logging function with a persistent prefix

   Args:
      prefix (str): The tag to appear at the start of logs (e.g., "ERROR")

   Returns:
      function: A closure that takes a message string and returns a formatted log.
   """
   def logger(message):
      return f"[{prefix}] {message}"
   return logger

# 6. Function Pipeline Applicator
def apply_functions(value, *functions):
   """
   Passes a single value through a sequence of functions.

   Args:
      value: The starting value
      *functions: Any number of functions/lambdas to apply in order.

   Returns:
      The final value after all transformations.
   """
   for func in functions:
      value = func(value)
   
   return value

# 7. Partial-Match Flexible Search
def flexible_search(items, **search_params):
   """
   Performs a case-insensitive partial search across a list of dictionaries.

   Args:
      items (list): List of dictionaries
      **search_params: Key and partial string to search for

   Returns:
      list: Items where the search string is found within the specified fields.
   """
   return [
      items for item in items
      if all(str(v).lower() in str(item.get(k, "")).lower()
            for k, v in search_params.items())
   ]

# 8. Statistics Calculator
def statistics_calculator(*numbers, **options):
   """
   Calculates the mean and optional median/mode of numeric dataset.

   Args:
      *numbers: Variable length list of numbers
      **options: Flags such as include_median=True

   Returns:
   dict: Calculated statistics
   """
   if not numbers:
      return {}
   
   result = {}
   
   result['mean'] = sum(numbers) / len(numbers)

   if options.get('include_median'):
      sorted_nums = sorted(numbers)
      nums = len(sorted_nums)
      result['median'] = (sorted_nums[nums//2-1] + sorted_nums[nums//2] / 2 if nums % 2 == 0 else sorted_nums[nums//2])
   
   return result

# ============================
# TEST DATA
# ============================
students = [
   {"name": "Alice Smith", "age": 20, "grade": 85, "city": "Sydney"},
   {"name": "Bob Jones", "age": 22, "grade": 75, "city": "Melbourne"},
   {"name": "Charlie Brown", "age": 21, "grade": 90, "city": "Sydney"},
   {"name": "David Miller", "age": 23, "grade": 85, "city": "Perth"}
]

print("\n" + "=" * 60)
print("FUNCTIONAL TOOLKIT TEST".center(60))
print("=" * 60)

# 1. Test create_multiplier
times_3 = create_multiplier(3)
times_10 = create_multiplier(10)
print(f"1. Multiplier: 5 * 3 = {times_3(5)} | 5 * 10 = {times_10(5)}")

# 2. Test sort_students
sorted_by_grade = sort_students(students, by="grade")
print(f"2. Sort (by grade): {[s["name"] for s in sorted_by_grade]}")

# 3. Test filter_data
sydney_85s = filter_data(students, grade=85, city="Sydney")
print(f"3. Filter (Grade 85 in Sydney): {sydney_85s}")

# 4. Test calculate
add_res = calculate(10, 20, 30, operation="+")
mul_res = calculate(2, 5, 10, operation="*")
div_res = calculate(100, 2, 2, operation="/")
print(f"4. Calculate: Add={add_res}, Multiply={mul_res}, Divide={div_res}")

# 5. Test create_logger
info_log = create_logger("INFO")
error_log = create_logger("ERROR")
print(f"5. Logger: {info_log('System Online')} | {error_log('Connection Failed')}")

# 6. Test apply_functions
# Start with 10, divide 2 (5), then square it (25)
pipeline_res = apply_functions(10, lambda x: x / 2, lambda x: x ** 2)
print(f"6. Pipeline (10 -> /2 -> squared): {pipeline_res}")

# 7. Test flexible_search
# Should find "Alice Smith" and "Bob Jones" with "S" or "s" in name
name_search = flexible_search(students, name="smith")
city_search = flexible_search(students, city="ney")
print(f"7. Search: 'smith' in name -> {len(name_search)} match | 'ney' in city -> {len(city_search)} match")