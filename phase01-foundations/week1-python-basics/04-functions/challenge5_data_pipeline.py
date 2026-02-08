"""
PROGRAM: Sales Data Processing Pipeline
----------------------------------------
Build a comprehensive data processing system using all function concepts.

This challenge demonstrates real-world data engineering tasks:
    - Data transformation and enrichment
    - Filtering and querying
    - Aggregations and analytics
    - Report Generation
    - Pipeline processing
"""

import time
import csv
from functools import wraps
from typing import List, Dict, Any, Tuple, Optional, Callable
from datetime import datetime, timedelta

# =================================================
# DECORATIONS (BONUS)
# =================================================

def timer(func):
    """Decorator to measure function excution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    
    return wrapper

def logger(func):
    """Decorator to log function calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} completed")
        return result
    
    return wrapper

def error_handler(func):
    """Decorator to handle errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {str(e)}")
            return None
    
    return wrapper

def memoize(func):
    """Decorator to cache function results"""
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from arguements
        key = str(args) + str(kwargs)

        if key not in cache:
            cache[key] = func(*args, **kwargs)
        else:
            print(f"Using cached result for {func.__name__}")
        
        return cache[key]
    
    return wrapper

# =================================================
# SAMPLE DATA
# =================================================
sales_data = [
    {"store": "Store A", "product": "Laptop", "quantity": 5, "price": 999, "date": "2025-01-15"},
    {"store": "Store B", "product": "Phone", "quantity": 10, "price": 699, "date": "2025-01-15"},
    {"store": "Store A", "product": "Mouse", "quantity": 25, "price": 29, "date": "2025-01-16"},
    {"store": "Store C", "product": "Laptop", "quantity": 3, "price": 999, "date": "2025-01-16"},
    {"store": "Store B", "product": "Keyboard", "quantity": 15, "price": 79, "date": "2025-01-17"},
    {"store": "Store A", "product": "Monitor", "quantity": 8, "price": 399, "date": "2025-01-17"},
    {"store": "Store C", "product": "Phone", "quantity": 12, "price": 699, "date": "2025-01-18"},
    {"store": "Store B", "product": "Laptop", "quantity": 7, "price": 999, "date": "2025-01-18"},
    {"store": "Store A", "product": "Tablet", "quantity": 20, "price": 499, "date": "2025-01-19"},
    {"store": "Store C", "product": "Monitor", "quantity": 5, "price": 399, "date": "2025-01-19"},
    {"store": "Store B", "product": "Mouse", "quantity": 30, "price": 29, "date": "2025-01-20"},
    {"store": "Store A", "product": "Keyboard", "quantity": 18, "price": 79, "date": "2025-01-20"},
]

# =================================================
# PART 1: DATA TRANSFORMATION FUNCTIONS
# =================================================

def calculate_revenue(sale: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add revenue field to a sale record.

    Args:
        sale (dict): Sale record with quantity and price

    Returns:
        dict: Sales record with added revenue field
    """
    sale_copy = sale.copy()
    sale_copy['revenue'] = sale_copy['quantity'] * sale_copy['price']
    return sale_copy


def add_category(sale: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add category based on price.

    Categories:
    - "High": price > 500
    - "Medium": 100 <= price <= 500
    - "Low": price < 100

    Args:
        sale (dict): Sale record with price field

    Returns:
        dict: Sale record with added category field
    """
    sale_copy = sale.copy()
    price = sale_copy['price']

    if price > 500:
        sale_copy['category'] = 'High'
    elif 100 <= price <= 500:
        sale_copy['category'] = 'Medium'
    else:
        sale_copy['category'] = 'Low'
    
    return sale_copy


def add_profit_margin (sale: Dict[str, Any], margin_rate: float = 0.3) -> Dict[str, Any]:
    """
    BONUS: Add profit margin calculation

    Args:
        sale: Sale record
        margin_rate: Profit marhin rate (default %30)

    Returns:
        Sale with profit field
    """
    sale_copy = sale.copy()
    if 'revenue' in sale_copy:
        sale_copy['profit'] = sale_copy['revenue'] * margin_rate
    
    return sale_copy


def enrich_data(*sales: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Apply all transformations to sales data.

    Args:
        *sales: Variable number of sale dictionaries.

    Returns:
        list: List of enriched sale records
    """
    enriched = []
    for sale in sales:
        enriched_sale = calculate_revenue(sale)
        enriched_sale = add_category(enriched_sale)
        enriched_sale = add_profit_margin(enriched_sale)
        enriched.append(enriched_sale)
    
    return enriched


# =================================================
# PART 2: FILTERING FUNCTIONS
# =================================================

def filter_by_store (sales: List[Dict], store_name: str) -> List[Dict]:
    """Filter sales by store name."""
    return [
        sale for sale in sales 
            if sale['store'] == store_name
    ]


def filter_by_date_range(sales: List[Dict], start_date: str, end_date: str) -> List[Dict]:
    """Filter sales within date range (inclusive)."""
    return [
        sale for sale in sales
        if start_date <= sale['date'] <= end_date
    ]


def filter_by_product(sales: List[Dict], product_name: str) -> List[Dict]:
    """Filter sales by product name."""
    return [
        sale for sale in sales
        if sale['product'] == product_name
    ]


def filter_by_criteria(sales: List[Dict], **criteria) -> List[Dict]:
    """
    Filter sales by an number of criteria

    Example:
        filter_by_criteria(sales, store ="Store A", category="High")
    """
    filtered = sales
    for key, value in criteria.items():
        filtered = [
            sale for sale in filtered
            if sale.get(key) == value
        ]
    
    return filtered


# =================================================
# PART 3: AGGREGATION FUNCTIONS
# =================================================

def total_revenue (sales: List[Dict]) -> float:
    """Calculate total revenue from sales."""
    return sum(sale.get('revenue', 0) for sale in sales)


def total_profit(sales: List[Dict])-> float:
    """BONUS: Calculate the total profit."""
    return sum(sale.get('profit', 0) for sale in sales)


def average_price(sales: List[Dict]) -> float:
    """Calculate average price of products."""
    if not sales:
        return 0.0
    
    return round(sum(sale['price'] for sale in sales) / len(sales), 2)


def sales_by_store(sales: List[Dict]) -> Dict[str, float]:
    """Calculate total revenue by store."""
    store_revenue = {}

    for sale in sales:
        store = sale['store']
        revenue = sale.get('revenue', 0)
        store_revenue[store] = store_revenue.get(store, 0) + revenue
    
    return store_revenue


def sales_by_product(sales: List[Dict]) -> Dict[str, int]:
    """Calculate total quantity sold by product."""
    product_quantity = {}
    
    for sale in sales:
        product = sale['product']
        quantity = sale['quantity']
        product_quantity[product] = product_quantity.get(product, 0) + quantity
    
    return product_quantity


def revenue_by_product(sales: List[Dict]) -> Dict[str, float]:
    """Calculate total revenue by product."""
    product_revenue = {}

    for sale in sales:
        product = sale['product']
        revenue = sale.get('revenue', 0)
        product_revenue[product] = product_revenue.get(product, 0) + revenue
    
    return product_revenue


def top_products(sales: List[Dict], n: int = 5) -> List[Tuple[str, float]]:
    """
    Get top N product by revenue

    Returns:
    List of tuples (product_name, total_revenue) sorted by revenue
    """
    product_revenue = revenue_by_product(sales)
    sorted_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)

    return sorted_products[:n]


# =================================================
# PART 4: ANALYSIS FUNCTIONS 
# =================================================

@memoize
def get_statistics(sales: List[Dict], *metrics: str) -> Dict[str, Any]:
    """
    Calculate requested statistics

    Available metrics:
    - total_revenue: Total revenue
    - total_profit: Total profit
    - total_quantity: Total items sold
    - avg_price: Average price
    - num_sales: Number of transcations
    - num_stores: Number of unique stores
    - num_products: Number of unique products
    """
    stats = {}

    # Convert to tuple for hashing
    sales_tuple = tuple(str(sale) for sale in sales)

    for metric in metrics:
        if metric == "total_revenue":
            stats[metric] = total_revenue(sales)
        elif metric == "total_profit":
            stats[metric] = total_profit(sales)
        elif metric == "total_quantity":
            stats[metric] = sum(sale['quantity'] for sale in sales)
        elif metric == "avg_price":
            stats[metric] = average_price(sales)
        elif metric == "num_sales":
            stats[metric] = len(sales)
        elif metric == "num_stores":
            stats[metric] = len(set(sale['store'] for sale in sales))
        elif metric == "num_products":
            stats[metric] = len(set(sale['product'] for sale in sales))

    return stats


def compare_stores(sales: List[Dict], store1: str, store2: str) -> Dict[str, Any]:
    """
    Compare performance of two stores.

    Returns:
        Comparison data for both stores
    """
    store1_sales = filter_by_store(sales, store1)
    store2_sales = filter_by_store(sales, store2)

    store1_revenue = total_revenue(store1_sales)
    store2_revenue = total_revenue(store2_sales)

    comparison = {
        store1: {
            "revenue": store1_revenue,
            "transactions": len(store1_sales),
            "avg_sale": store1_revenue / len(store1_sales) if store1_sales else 0,
            "profit": total_profit(store1_sales)
        },
        store2: {
            "revenue": store2_revenue,
            "transactions": len(store2_sales),
            "avg_sale": store2_revenue / len(store2_sales) if store2_sales else 0,
            "profit": total_profit(store2_sales)
        },
        "winner": store1 if store1_revenue > store2_revenue else store2
    }

    return comparison


def daily_summary(sales: List[Dict]) -> Dict[str, Dict[str, Any]]:
    """
    Create daily sale summary.

    Returns:
        Dictionary with dates as keys, daily stats as values
    """
    daily = {}

    for sale in sales:
        date = sale['date']
        if date not in daily:
            daily[date] = {
                "revenue": 0,
                "profit": 0,
                "transactions": 0,
                "quantity": 0
            }
        
        daily[date]["revenue"] += sale.get('revenue', 0)
        daily[date]["profit"] += sale.get('profit', 0)
        daily[date]["transactions"] += 1
        daily[date]["quantity"] += sale['quantity']
    
    return daily


def calculate_growth_rate(sales: List[Dict], period: str = "daily") -> Dict[str, float]:
    """
    BONUS: Calculate growth rates.

    Args:
        sales: Sales data
        period: "daily" or "weekly"

    Returns:
        Dictionary with dates and growth rates 
    """
    daily = daily_summary(sales)
    sorted_dates = sorted(daily.keys())

    growth_rates = {}
    for i in range(1, len(sorted_dates)):
        prev_date = sorted_dates[i-1]
        curr_date = sorted_dates[i]

        prev_revenue = daily[prev_date]['revenue']
        curr_revenue = daily[curr_date]['revenue']

        if prev_revenue > 0:
            growth = ((curr_revenue - prev_revenue) / prev_revenue) * 100
            growth_rates[curr_date] = round(growth, 2)
    
    return growth_rates


# =================================================
# PART 5: REPORTING FUNCTIONS 
# =================================================

def format_currency(amount:float) -> str:
    """Format number as currency"""
    return f"${amount:,.2f}"


def create_bar_chart(data: Dict[str, float], max_width: int = 40) -> str:
    """
    BONUS: Create ASCII bar chart.

    Args:
        data: Dictionary with labels and values
        max_width: maximum width of bars

    Returns:
        Formatted bar chart as string
    """
    if not data:
        return ""
    
    max_value = max(data.values())
    chart = []

    for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
        bar = "█" * bar_length
        chart.append(f"{label:15s} {bar} {format_currency(value)}")
    
    return "\n".join(chart)


def generate_report(sales: List[Dict], **options) -> str:
    """
    Generate formatted sales report.

    Options:
        - group_by: "store", "product", or"date"
        - sort_by: "revenue", "quantity", "name"
        - top_n: Show only top N items
        - include_totals: Include total row
        - include_chart: Include ASCII bar chart
    """
    group_by = options.get('group_by', 'store')
    sort_by = options.get('sort_by', 'revenue')
    top_n = options.get('top_n', None)
    include_totals = options.get('include_totals', True)
    include_chart = options.get('include_chart', False)

    report = []
    report.append("=" * 70)
    report.append("SALES REPORT".center(70))
    report.append("=" * 70)
    report.append(f"Group By: {group_by.title()} | Sort By: {sort_by.title()}")
    report.append("")

    # Group data
    if group_by == "store":
        grouped = {}
        for sale in sales:
            key = sale['store']
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(sale)
    elif group_by == "product":
        grouped = {}
        for sale in sales:
            key = sale['product']
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(sale)
    elif group_by == "date":
        grouped = {}
        for sale in sales:
            key = sale['date']
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(sale)
    else:
        grouped = {"All Sales": sales}

    # Calculate metrics for each group
    group_metrics = {}
    for key, group_sales in grouped.items():
        revenue = total_revenue(group_sales)
        quantity = sum(sale['quantity'] for sale in group_sales)
        transactions = len(group_sales)

        group_metrics[key] = {
            "revenue": revenue,
            "quantity": quantity,
            "transactions": transactions
        }
    
    # Sort
    if sort_by == "revenue":
        sorted_groups = sorted(group_metrics.items(), key=lambda x: x[1]['revenue'], reverse=True)
    elif sort_by == "quantity":
        sorted_groups == sorted(group_metrics.items(), key=lambda x: x[1]['quantity'], reverse=True)
    else:
        sorted_groups = sorted(group_metrics.items())
    
    # Apply top_n filter
    if top_n:
        sorted_groups = sorted_groups[:top_n]
    
    # Format output
    for key, metrics in sorted_groups:
        revenue_str = format_currency(metrics['revenue'])
        transactions = metrics['transactions']
        report.append(f"{key:20s} {revenue_str:>15s} ({transactions} transactions)")
    
    # Totals
    if include_totals:
        report.append("-" * 70)
        total_rev = sum(m['revenue'] for _, m in sorted_groups)
        total_trans = sum(m['transactions'] for _, m in sorted_groups)
        report.append(f"{'TOTAL':20s} {format_currency(total_rev):>15s} ({total_trans} transactions)")
    
    # Chart
    if include_chart:
        report.append("")
        report.append("Revenue Chart:")
        report.append("-" * 70)
        chart_data = {key: metrics['revenue'] for key, metrics in sorted_groups}
        report.append(create_bar_chart(chart_data))
    
    report.append("=" * 70)

    return "\n".join(report)


# =================================================
# PART 6: PIPELINE FUNCTIONS 
# =================================================

@timer
def process_pipeline(data: Any, *operations: Callable) -> Any:
    """
    Apply multiple operations in sequence.
    Args: 
        data: Initial data
        *operations: Functions to apply in order

    Returns:
        Result after all operations applied
    """
    result = data
    for operation in operations:
        result = operation(result)
    return result


# =================================================
# PART 7: UTILITY FUNCTIONS 
# =================================================

def validate_sale(sale: Dict) -> bool:
    """
    Validate that sale has all required fields.

    Required fields: store, product, quantity, price, date
    """
    required_fields = ['store', 'product', 'quantity', 'price', 'date']

    # Check all fields exist
    for field in required_fields:
        if field not in sale:
            return False
    
    # Check data types
    try:
        if not isinstance(sale['store'], str):
            return False
        if not isinstance(sale['product'], str):
            return False
        if not isinstance(sale['quantity'], (int, float)) or sale['quantity'] <= 0:
            return False
        if not isinstance(sale['price'], (int, float)) or sale['price'] <= 0:
            return False
        if not isinstance(sale['date'], str):
            return False
    except:
        return False
    
    return True


@error_handler
def clean_data(sales: List[Dict]) -> List[Dict]:
    """
    Remove invalid sales and fix data types.

    Args:
        sales: List of sale records (many contain invalid data)

    Returns:
        Cleaned data records
    """
    cleaned = []

    for sale in sales:
        if validate_sale(sale):
            cleaned_sale = sale.copy()

            # Ensure correct data types
            cleaned_sale['quantity'] = int(cleaned_sale['quantity'])
            cleaned_sale['price'] = float(cleaned_sale['price'])

            cleaned.append(cleaned_sale)
    
    return cleaned


@error_handler
def export_to_csv(sales: List[Dict], filename = "sales_export.csv") -> bool:
    """
    Export sales to CSV file.
    
    Args:
        sales:  List of sale records
        filename: Output filename

    Returns:
        True if successful, False otherwise
    """
    if not sales:
        print("No data to export")
        return False
    
    # Get all possible fields
    all_fields = set()
    for sale in sales:
        all_fields.update(sale.keys())

    fieldnames = sorted(all_fields)

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sales)

    print(f"Exported {len(sales)} records to {filename}")
    return True


# =================================================
# BONUS: ADVANCED FUNCTIONS 
# =================================================

def find_trends(sales: List[Dict], metric: str = "revenue") -> Dict[str, Any]:
    """
    BONUS: Find trends in sales data over time.

    Args:
        sales: List of sale records
        metric Metric to analyze ("revenue", "quantity", etc.)

    Returns:
        Tend analysis with growth rates
    """
    daily = daily_summary(sales)
    sorted_dates = sorted(daily.keys())

    if len(sorted_dates) < 2:
        return {"trend": "insufficient _data"}
    
    # Calculate trend
    values = [daily[date][metric] for date in sorted_dates]

    # Simpler linear trend (increasing/decreasing/stable)
    increases = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
    decreases = sum(1 for i in range(1,len(values)) if values[i] < values[i-1])

    if increases > decreases:
        trend = "increasaing"
    elif decreases > increases:
        trend = "decreasing"
    else:
        trend = "stable"\
    
    # Calculate average growth rate
    growth_rates = []
    for i in range(1, len(values)):
        if values[i-1] > 0:
            growth = ((values[i] - values[i-1]) / values[i-1]) * 100
            growth_rates.append(growth)

    avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0

    return {
        "trend": trend,
        "avg_growth_rate": round(avg_growth, 2),
        "start_value": values[0],
        "end_value": values[-1],
        "total_change": values[-1] - values[0],
        "percent_change": round(((values[-1] - values[0]) / values[0] * 100), 2) if values[0] > 0 else 0
    }


def predict_next_day(sales: List[Dict], method: str = "average") -> float:
    """
    BONUS: Predict next day's revenue.

    Args:
        sales: List of sale records
        method: "average" (use last 3 days avg) or "trend" (linear projection)

    Returns:
        Predicted revenue for next day
    """
    daily = daily_summary(sales)
    sorted_dates = sorted(daily.keys())

    if not sorted_dates:
        return 0.0
    
    if method == "average":
        # Use average of last 3 days
        last_n = min(3, len(sorted_dates))
        recent_revenues = [daily[date]['revenue'] for date in sorted_dates[-last_n:]]
        return sum(recent_revenues) / len(recent_revenues)
    
    elif method == "trend":
        # Simple linear trend
        if len(sorted_dates) < 2:
            return daily[sorted_dates[-1]]['revenue']
        
        # Calculate average daily change
        changes = []
        for i in range(1, len(sorted_dates)):
            prev = daily[sorted_dates[i-1]]['revenue']
            curr = daily[sorted_dates[i]]['revenue']
            changes.append(curr - prev)

        avg_change = sum(changes) / len(changes)
        last_day_revenue = daily[sorted_dates[i-1]]['revenue']

        return max(0, last_day_revenue + avg_change)
    
    return 0.0


def find_anomalies(sales: List[Dict], threshold: float = 2.0) -> List[Dict]:
    """
    BONUS: Find anomalous sales (unusually high or low)

    Args:
        sales: List of sale records
        threshold: Number of standard deviations to consider anomaly

    Returns:
        List of anomalous sales
    """
    if not sales:
        return []
    
    revenues = [sale.get('revenue', 0) for sale in sales]

    # Calculate mean and standard deviation
    mean = sum(revenues) / len(revenues)
    variance = sum((x - mean) ** 2 for x in revenues) / len(revenues)
    std_dev = variance ** 0.5

    # Final anomalies
    anomalies = []
    for sale in sales:
        revenue = sale.get('revenue', 0)
        z_score = abs((revenue - mean) / std_dev) if std_dev > 0 else 0

        if z_score > threshold:
            sale_copy = sale.copy()
            sale_copy['z_score'] = round(z_score, 2)
            sale_copy['anomaly_type'] = 'high' if revenue > mean else 'low'
            anomalies.append(sale_copy)
    
    return anomalies


def calculate_return_on_investment(sales: List[Dict], investment: float = 10000) -> Dict[str, float]:
    """
    BONUS: Calculate Return on Investment.

    Args:
        sales: Sales data
        investment: Initial investment amount

    Returns:
    Return on Investment metrics
    """
    total_rev = total_revenue(sales)
    total_prof = total_profit(sales)

    roi_percentage = (total_prof / investment * 100) if investment > 0 else 0

    return {
        "investment": investment,
        "total_revenue": total_rev,
        "total_profit": total_prof,
        "roi_percentage": round(roi_percentage, 2),
        "profit_margin": round((total_prof / total_rev * 100), 2) if total_rev > 0 else 0
    }


# =================================================
# MAIN PROGRAM
# =================================================

def print_section_header(title: str):
    """Helper to print section headers."""
    print("\n" + "=" * 70)
    print(f"   {title}")
    print("=" * 70)


@timer
def main():
    """Main function demonstrating all functionality"""
    print("=" * 70)
    print("SALES DATA PROCESSING PIPELINE".center(70))
    print("=" * 70)
    print(f"With Bonus Features: Decorators, Caching, Visualization, Analytics")
    print("=" * 70)

    # Step 1: Clean and enrich data
    print_section_header("1. DATA CLEANING & ENRICHMENT")
    cleaned_sales = clean_data(sales_data)
    print(f"    Cleaned: {len(cleaned_sales)} / {len(sales_data)} valid records")

    enriched_sales = enrich_data(*cleaned_sales)
    print(f"    Enriched: Added revenue, category, and profit fields")
    print(f"    Sample record:")
    print(f"    {enriched_sales[0]}")

    # Step 2: Basic filtering
    print_section_header("FILTERING EXAMPLES")
    store_a = filter_by_store(enriched_sales, "Store A")
    print(f"    Store A sales: {len(store_a)} transactions")

    high_value = filter_by_criteria(enriched_sales, category="High")
    print(f"    High-valuue sales: {len(high_value)} transactions")

    date_filtered = filter_by_date_range(enriched_sales, "2025-01-15", "2025-01-18")
    print(f"    Sales from Jan 15-18: {len(date_filtered)} transactions")

    # Step 3: Aggregations
    print_section_header("3. REVENUE & PROFIT ANALYSIS")
    total_rev = total_revenue(enriched_sales)
    total_prof = total_profit(enriched_sales)
    avg_price_val = average_price(enriched_sales)

    print(f"    Total Revenue:      {format_currency(total_rev)}")
    print(f"    Total Profit:       {format_currency(total_prof)}")
    print(f"    Average Price:      {format_currency(avg_price_val)}")
    print(f"    Profit Margin:      {(total_prof / total_rev * 100):.2f}%")

    # Step 4: Sales store with chart
    print_section_header("4. SALES BY STORE")
    store_sales = sales_by_store(enriched_sales)
    print(create_bar_chart(store_sales))

    # Step 5. Top products
    print_section_header("5. TOP PRODUCT BY REVENUE")
    top_prods = top_products(enriched_sales, 5)
    for i, (product, revenue) in enumerate(top_prods, 1):
        print(f"    {i}. {product:15s} {format_currency(revenue)}")

    # Step 6: Statistics (wich caching)
    print_section_header("6. COMPREHENSIVE STATISTICS")
    stats = get_statistics(
        enriched_sales,
        "total_revenue", "total_profit", "total_quantity", 
        "avg_price", "num_sales", "num_stores", "num_products"
    )

    for metric, value in stats.items():
        if "revenue" in metric or "price" in metric or "profit" in metric:
            print(f"    {metric:20s}: {format_currency(value)}")
        else:
            print(f"    {metric:20s}: {value}")
    
    # Call again to show caching
    print("\n   Calling statistics again (show use cache):")
    stats2 = get_statistics(enriched_sales, "total_revenue", "num_sales")

    # Step 7: Store comparison
    print_section_header("7. STORE COMPARISON")
    comparison = compare_stores(enriched_sales, "Store A", "Store B")
    print(f"    Winner: {comparison['winner']}")
    print()
    for store in ["Store A", "Store B"]:
        print(f"    {store}:")
        print(f"    Revenue:        {format_currency(comparison[store]['revenue'])}")
        print(f"    Profit:         {format_currency(comparison[store]['profit'])}")
        print(f"    Transactions:   {comparison[store]['transactions']}")
        print(f"    Average Sale:   {format_currency(comparison[store]['avg_sale'])}")
        print()

    # Step 8: Daily summary
    print_section_header("8. DAILY SALES SUMMARY")
    daily = daily_summary(enriched_sales)
    for date in sorted(daily.keys())[:5]:
        day_data = daily[date]
        print(f"    {date}: {format_currency(day_data['revenue']):>12s} "
            f"(Profit: {format_currency(day_data['profit']):>10s}, "
            f"{day_data['transactions']} trans)")
        
    if len(daily) > 5:
        print(f"    ... and {len(daily) - 5} more days")

    # Step 9: Trend analysis
    print_section_header("9. TREND ANALYSIS")
    revenue_trend = find_trends(enriched_sales, 'revenue')
    print(f"    Trend:              {revenue_trend['trend'].upper()}")
    print(f"    Avg Growth Rate:    {revenue_trend['avg_growth_rate']}%")
    print(f"    Start Revenue:      {format_currency(revenue_trend['start_value'])}")
    print(f"    End Revenue:        {format_currency(revenue_trend['end_value'])}")
    print(f"    Total Change:       {format_currency(revenue_trend['total_change'])}")
    print(f"    Percent Change:     {revenue_trend['percent_change']}%")

    # Step 10: Growth rate calculation
    print_section_header("10. DAILY GROWTH RATES")
    growth_rates = calculate_growth_rate(enriched_sales, "daily")
    print(" Date-over-date growth:")
    for date, rate in sorted(growth_rates.items())[:5]:
        arrow = "📈" if rate > 0 else "📉" if rate < 0 else "➡️"
        print(f"    {date}: {rate:>6.2f}% {arrow}")

    # Step 11: Revenue predictions
    print_section_header("11. REVENUE PREDICTION")
    pred_avg = predict_next_day(enriched_sales, "average")
    pred_trend = predict_next_day(enriched_sales, "trend")
    last_day_rev = list(daily_summary(enriched_sales).values())[-1]['revenue']

    print(f"    Last Day Revenue:             {format_currency(last_day_rev)}")
    print(f"    Prediction (Average method):  {format_currency(pred_avg)}")
    print(f"    Prediction (Trend method):    {format_currency(pred_trend)}")

    avg_diff = pred_avg - last_day_rev
    trend_diff = pred_trend - last_day_rev
    print(f"\n    Expected change (Average):    {format_currency(avg_diff)} " 
          f"({(avg_diff / last_day_rev * 100):.1f}%)")
    print(f"    Expected change (Trend):      {format_currency(trend_diff)} " 
          f"({(trend_diff / last_day_rev * 100):.1f}%)")

    # Step 12: Anomaly detection
    print_section_header("12. ANOMALY DETECTION")
    anomalies = find_anomalies(enriched_sales, threshold=1.5)

    if anomalies:
        print(f"    Found {len(anomalies)} anomalous sales (threshold: 1.5 std devs):")
        print()
        for anomaly in sorted(anomalies, key=lambda x: x['z_score'], reverse=True)[:5]:
            anomaly_icon = "⬆️" if anomaly['anomaly_type'] == 'high' else "⬇️"
            print(f"    {anomaly_icon} {anomaly['date']} | {anomaly['store']:10s} | "
                f"{anomaly['product']:10s} | {format_currency(anomaly['revenue']):>12s} | "
                f"z_score: {anomaly['z_score']}")
    else:
        print(f"    No significant anomalies detected")

    # 13. ROI (Return on Invesment) calculation
    print_section_header("13. RETURN ON INVESTMENT (ROI)")
    initial_investment = 20000
    roi = calculate_return_on_investment(enriched_sales, investment=initial_investment)

    print(f"    Initial Investment:  {format_currency(roi['investment'])}")
    print(f"    Total Revenue:       {format_currency(roi['total_revenue'])}")
    print(f"    Total Profit:        {format_currency(roi['total_profit'])}")
    print(f"    ROI:                 {roi['roi_percentage']}%")
    print(f"    Profit Margin:       {roi['profit_margin']}%")
    print()

    if roi['roi_percentage'] > 50:
        print(f"    Excellent ROI! Investment performing very well.")
    elif roi['roi_percentage'] > 20:
        print(f"    Good ROI. Healthy return on investment.")
    elif roi['roi_percentage'] > 0:
        print(f"    Positive ROI but room for improvement.")
    else:
        print(f"    Negative ROI. Review business strategy.")

    # Step 14: Product analysis
    print_section_header("14. PRODUCT PERFORMANCE ANALYSIS")
    product_rev = revenue_by_product(enriched_sales)
    product_qty = sales_by_product(enriched_sales)

    print(f"    Top Products by Revenue:")
    print(create_bar_chart(product_rev, max_width=30))

    print(f"\n  Product Metrics:")
    for product in sorted(product_rev.keys(), key=lambda x: product_rev[x], reverse=True)[:5]:
        revenue = product_rev[product]
        quantity = product_qty[product]
        avg_price = revenue / quantity if quantity > 0 else 0
        print(f"    {product:15s} | Rev: {format_currency(revenue):>12s} | "
            f"Qty: {quantity:3d} | Avg: {format_currency(avg_price):>10s}")
        
    # 15. Store performance report
    print_section_header("15. DETAILED STORE REPORT")
    report_store = generate_report (
        enriched_sales,
        group_by ="store",
        sort_by="revenue",
        include_totals=True,
        include_chart=True
    )
    print(report_store)

    # 16. Product report
    print_section_header("16. PRODUCT SALES REPORT")
    report_product = generate_report(
        enriched_sales,
        group_by="product",
        sort_by="revenue",
        top_n=5,
        include_totals=True
    )
    print(report_product)

    # Complex pipeline
    pipeline_result = process_pipeline(
        sales_data,
        clean_data,                                                    # Stage 1: Clean
        lambda x: enrich_data(*x),                                     # Stage 2: Enrich
        lambda x: filter_by_criteria(x, category="High"),              # Stage 3: Filter
        lambda x: sorted(x, key=lambda s: s['revenue'], reverse=True)  # Stage 4: Sort
    )
    
    print(f"    Pipeline processed {len(pipeline_result)} high-value sales")
    print(f"\n  Top 3 High-Value Sales:")
    for i, sale in enumerate(pipeline_result[:3], 1):
        print(f"    {i}. {sale['store']:10s} | {sale['product']:10s} | "
            f"{format_currency(sale['revenue']):>12s} | {sale['date']}")
    
    # Step 18: Custom analysis with lambda
    print_section_header("18. CUSTOM ANALYSIS (USING LAMBDAS)")

    # Filter using lambda
    weekend_sales = list(filter(
        lambda s: s['date'] in ["2025-01-18", "2025-01-19"], # Weekend dates
        enriched_sales
    ))
    print(f"    Weekend Sales:   {len(weekend_sales)} transactions")
    print(f"    Weekend Revenue: {format_currency(total_revenue(weekend_sales))}")

    # Map product names to uppercase
    product_names_upper = list(map(lambda s: s['product'].upper(), enriched_sales))
    unique_products = set(product_names_upper)
    print(f"\n  Products sold (uppercase): {', '.join(sorted(unique_products))}")

    # Reduce-like operation: find max revenue sale
    max_sale = max(enriched_sales, key=lambda s: s['revenue'])
    print(f"\n  Highest Revenue Sale:")
    print(f"    {max_sale['store']} | {max_sale['product']} | "
        f"{format_currency(max_sale['revenue'])} | {max_sale['date']}")
    
    # Step 19: Data quality report
    print_section_header("19. QUALITY REPORT")

    total_records = len(sales_data)
    valid_records = len(cleaned_sales)
    invalid_records = total_records - valid_records

    print(f"    Total Records:      {total_records}")
    print(f"    Valid Records:      {valid_records} ({valid_records / total_records * 100:.1f}%)")
    print(f"    Invalid Records:    {invalid_records} ({invalid_records / total_records * 100:.1f})")

    # Check for missing fields in enriched data
    all_fields = ['store', 'product', 'quantity', 'price', 'date', 'revenue', 'category', 'profit']
    field_completeness = {}

    for field in all_fields:
        complete = sum(1 for sale in enriched_sales if field in sale and sale[field] is not None)
        field_completeness[field] = (complete / len(enriched_sales)) * 100

    print("\n   Field Completeness:")
    for field, percentage in field_completeness.items():
        bar = "█" * int(percentage / 5)
        print(f"    {field:12s} [{bar:20s}] {percentage:.1f}%")
    
    # Step 20: Export data
    print_section_header("20. DATA EXPORT")

    # Export enriched data
    export_success = export_to_csv(enriched_sales, "sales_export_enriched.csv")

    # Export top products
    top_products_data = [
        {"product": prod, "revenue": rev}
        for prod, rev in top_products(enriched_sales, n=10)
    ]
    export_to_csv(top_products_data, "top_products.csv")

    # Export daily summary
    daily_data = [
        {"date": date, **metrics}
        for date, metrics in sorted(daily_summary(enriched_sales).items())
    ]
    export_to_csv(daily_data, "daily_summary.csv")

    print(f"    Exported 3 files:")
    print(f"    - sales_export_enriched.csv ({len(enriched_sales)} records)")
    print(f"    - top_products.csv ({len(top_products_data)} products)")
    print(f"    - daily_summary.csv ({len(daily_data)} days)")

    # Final summary
    print("\n" + "=" * 70)
    print("COMPREHENSIVE PIPELINE ANALYSIS COMPLETE".center(70))
    print("=" * 70)
    print()
    print("SUMMARY STATISTICS:")
    print(f"    Total Records Processed:    {len(enriched_sales)}")
    print(f"    Date Range:                 {min(s['date'] for s in enriched_sales)} to "
        f"{max(s['date'] for s in enriched_sales)}")
    print(f"    Total Revenue:              {format_currency(total_rev)}")
    print(F"    Total Profit:               {format_currency(total_prof)}")
    print(f"    Profit Margin:              {(total_prof / total_rev * 100):.2f}%")
    print(f"    Stores Analyzed:            {len(set(s['store'] for s in enriched_sales))}")
    print(f"    Products Tracked:           {len(set(s['product'] for s in enriched_sales))}")
    print(f"    Avg Daily Revenue:          {format_currency(total_rev / len(daily))}")
    print(f"    Trend:                      {revenue_trend['trend'].upper()}")
    print(f"    ROI:                        {roi['roi_percentage']}%")
    print()
    print(f"    FILES EXPORTED::")
    print(f"    - sales_export_enriched.csv")
    print(f"    - top_products.csv")
    print(f"    - daily_summary.csv")
    print()
    print("=" * 70)
    print("Thank for using the Sales Data Processing Pipeline!".center(70))
    print("=" * 70)


if __name__ == "__main__":
    print("\nStarting Sales Data Processing Pipeline...\n")
    main()
    print("\nPipeline execution completed sucessfully!\n")