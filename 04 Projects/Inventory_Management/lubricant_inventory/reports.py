"""
REPORTS.PY
==========
This file contains all the logic for generating reports.

SIMPLE EXPLANATION:
- Stock Comparison: Comparing system stock vs physical stock
- Difference: Finding shortages or excess
- Value Impact: How much money you're losing or gaining
- Export: Creating Excel files with the reports
"""

import pandas as pd
from datetime import datetime
from crud import (
    get_all_items,
    get_system_stock,
    get_all_purchases,
    get_all_sales,
    get_latest_physical_stock
)


# ============================================
# STOCK COMPARISON REPORT
# ============================================

def generate_stock_comparison_report():
    """
    Generate the main Stock Comparison Report.

    THINK OF IT AS:
    - Comparing what the computer thinks you have (system stock)
    - With what you actually counted (physical stock)
    - Finding differences (shortages or excess)

    FOR EACH ITEM:
    - System Stock = Opening Stock + Purchases - Sales
    - Physical Stock = Latest physical count
    - Difference = System Stock - Physical Stock
      - Positive difference = SHORTAGE (you have less than expected)
      - Negative difference = EXCESS (you have more than expected)
    - Value Impact = Difference × Sale Price

    RETURNS:
        DataFrame with comparison for all items
    """
    items = get_all_items()
    latest_physical = get_latest_physical_stock()

    report_data = []

    for item in items:
        item_id = item['item_id']

        # Calculate system stock
        system_stock = get_system_stock(item_id)

        # Get physical stock (if available)
        physical_stock = latest_physical.get(item_id, None)

        # Calculate difference
        if physical_stock is not None:
            difference = system_stock - physical_stock

            # Determine if it's shortage or excess
            if difference > 0:
                status = "SHORTAGE"
            elif difference < 0:
                status = "EXCESS"
            else:
                status = "MATCH"

            # Calculate value impact (using sale price)
            value_impact = abs(difference) * item['sale_price']
        else:
            difference = None
            status = "NO PHYSICAL COUNT"
            value_impact = None

        report_data.append({
            'Item ID': item_id,
            'Item Name': item['item_name'],
            'Grade': item['grade'],
            'Pack Size (L)': item['pack_size'],
            'Opening Stock': item['opening_stock'],
            'Total Purchases': _get_total_purchases(item_id),
            'Total Sales': _get_total_sales(item_id),
            'System Stock': system_stock,
            'Physical Stock': physical_stock if physical_stock is not None else '-',
            'Difference': difference if difference is not None else '-',
            'Status': status,
            'Rate (Sale Price)': item['sale_price'],
            'Value Impact': value_impact if value_impact is not None else '-'
        })

    df = pd.DataFrame(report_data)
    return df


def _get_total_purchases(item_id):
    """
    Helper function to get total purchases for an item.
    """
    from crud import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM purchases WHERE item_id = ?", (item_id,))
    result = cursor.fetchone()
    conn.close()
    return result['total'] if result else 0


def _get_total_sales(item_id):
    """
    Helper function to get total sales for an item.
    """
    from crud import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM sales WHERE item_id = ?", (item_id,))
    result = cursor.fetchone()
    conn.close()
    return result['total'] if result else 0


def calculate_summary_totals(comparison_df):
    """
    Calculate summary totals from the comparison report.

    THINK OF IT AS:
    - Adding up all shortages
    - Adding up all excess
    - Giving you the total financial impact

    PARAMETERS:
        comparison_df: DataFrame from generate_stock_comparison_report()

    RETURNS:
        Dictionary with summary totals:
        - total_shortage_value: Total value of all shortages
        - total_excess_value: Total value of all excess
        - items_with_shortage: Number of items with shortage
        - items_with_excess: Number of items with excess
        - items_matching: Number of items with matching stock
        - items_no_count: Number of items without physical count
    """
    # Handle empty DataFrame
    if comparison_df.empty or 'Physical Stock' not in comparison_df.columns:
        return {
            'total_shortage_value': 0,
            'total_excess_value': 0,
            'items_with_shortage': 0,
            'items_with_excess': 0,
            'items_matching': 0,
            'items_no_count': 0,
            'total_items': 0
        }

    # Filter rows with actual counts (not "NO PHYSICAL COUNT")
    counted_df = comparison_df[comparison_df['Physical Stock'] != '-']

    # Calculate shortage total (where Difference > 0)
    shortage_df = counted_df[counted_df['Difference'] > 0]
    total_shortage_value = shortage_df['Value Impact'].sum() if not shortage_df.empty else 0
    items_with_shortage = len(shortage_df)

    # Calculate excess total (where Difference < 0)
    excess_df = counted_df[counted_df['Difference'] < 0]
    total_excess_value = excess_df['Value Impact'].sum() if not excess_df.empty else 0
    items_with_excess = len(excess_df)

    # Count matching items
    matching_df = counted_df[counted_df['Difference'] == 0]
    items_matching = len(matching_df)

    # Count items without physical count
    items_no_count = len(comparison_df[comparison_df['Physical Stock'] == '-'])

    summary = {
        'total_shortage_value': total_shortage_value,
        'total_excess_value': total_excess_value,
        'items_with_shortage': items_with_shortage,
        'items_with_excess': items_with_excess,
        'items_matching': items_matching,
        'items_no_count': items_no_count,
        'total_items': len(comparison_df)
    }

    return summary


# ============================================
# CURRENT STOCK REPORT
# ============================================

def generate_current_stock_report():
    """
    Generate a report showing current stock for all items.

    THINK OF IT AS:
    - A quick view of what you should have in stock
    - Based purely on system calculations (opening + purchases - sales)

    RETURNS:
        DataFrame with current stock for all items
    """
    items = get_all_items()
    stock_data = []

    for item in items:
        system_stock = get_system_stock(item['item_id'])

        stock_data.append({
            'Item Name': item['item_name'],
            'Grade': item['grade'],
            'Pack Size (L)': item['pack_size'],
            'System Stock': system_stock,
            'Purchase Price': item['purchase_price'],
            'Sale Price': item['sale_price'],
            'Stock Value (at purchase price)': system_stock * item['purchase_price']
        })

    df = pd.DataFrame(stock_data)
    return df


# ============================================
# SALES REPORT
# ============================================

def generate_sales_report(start_date=None, end_date=None):
    """
    Generate a sales report.

    THINK OF IT AS:
    - A summary of all sales
    - Can filter by date range

    PARAMETERS:
        start_date: Optional start date (format: "YYYY-MM-DD")
        end_date: Optional end date (format: "YYYY-MM-DD")

    RETURNS:
        DataFrame with sales details
    """
    if start_date and end_date:
        sales = get_sales_by_date_range(start_date, end_date)
    else:
        sales = get_all_sales()

    if not sales:
        return pd.DataFrame()

    sales_data = []
    for sale in sales:
        sales_data.append({
            'Date': sale['date'],
            'Cashier': sale['cashier_name'],
            'Shift': sale['shift'],
            'Item Name': sale['item_name'],
            'Quantity': sale['quantity']
        })

    df = pd.DataFrame(sales_data)
    return df


def get_sales_by_cashier_summary():
    """
    Get a summary of sales by cashier.

    THINK OF IT AS:
    - Comparing performance of the two cashiers
    - Total quantity sold by each cashier

    RETURNS:
        DataFrame with cashier-wise sales summary
    """
    sales = get_all_sales()

    cashier_summary = {}

    for sale in sales:
        cashier = sale['cashier_name']
        quantity = sale['quantity']

        if cashier not in cashier_summary:
            cashier_summary[cashier] = {
                'total_quantity': 0,
                'total_transactions': 0
            }

        cashier_summary[cashier]['total_quantity'] += quantity
        cashier_summary[cashier]['total_transactions'] += 1

    summary_data = []
    for cashier, data in cashier_summary.items():
        summary_data.append({
            'Cashier Name': cashier,
            'Total Quantity Sold': data['total_quantity'],
            'Total Transactions': data['total_transactions']
        })

    df = pd.DataFrame(summary_data)
    return df


# ============================================
# PURCHASE REPORT
# ============================================

def generate_purchase_report(start_date=None, end_date=None):
    """
    Generate a purchase report.

    THINK OF IT AS:
    - A summary of all purchases from PSO
    - Can filter by date range

    PARAMETERS:
        start_date: Optional start date (format: "YYYY-MM-DD")
        end_date: Optional end date (format: "YYYY-MM-DD")

    RETURNS:
        DataFrame with purchase details
    """
    if start_date and end_date:
        purchases = get_purchases_by_date_range(start_date, end_date)
    else:
        purchases = get_all_purchases()

    if not purchases:
        return pd.DataFrame()

    purchase_data = []
    for purchase in purchases:
        purchase_data.append({
            'Date': purchase['date'],
            'Invoice No': purchase['invoice_no'],
            'Item Name': purchase['item_name'],
            'Quantity': purchase['quantity'],
            'Rate': purchase['rate'],
            'Total Value': purchase['quantity'] * purchase['rate']
        })

    df = pd.DataFrame(purchase_data)
    return df


# ============================================
# EXCEL EXPORT FUNCTIONS
# ============================================

def export_comparison_to_excel(df, summary):
    """
    Export the stock comparison report to Excel.

    THINK OF IT AS:
    - Creating an Excel file with:
      - Sheet 1: Detailed comparison for each item
      - Sheet 2: Summary totals

    PARAMETERS:
        df: DataFrame from generate_stock_comparison_report()
        summary: Dictionary from calculate_summary_totals()

    RETURNS:
        File path to the saved Excel file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stock_comparison_{timestamp}.xlsx"

    # Create Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: Detailed comparison
        df.to_excel(writer, sheet_name='Stock Comparison', index=False)

        # Sheet 2: Summary
        summary_df = pd.DataFrame([{
            'Total Shortage Value': summary['total_shortage_value'],
            'Total Excess Value': summary['total_excess_value'],
            'Items with Shortage': summary['items_with_shortage'],
            'Items with Excess': summary['items_with_excess'],
            'Items Matching': summary['items_matching'],
            'Items Without Physical Count': summary['items_no_count'],
            'Total Items': summary['total_items']
        }])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

    return filename


def export_sales_to_excel(df):
    """
    Export sales report to Excel.

    PARAMETERS:
        df: DataFrame from generate_sales_report()

    RETURNS:
        File path to the saved Excel file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sales_report_{timestamp}.xlsx"

    df.to_excel(filename, index=False, engine='openpyxl')

    return filename


def export_purchases_to_excel(df):
    """
    Export purchase report to Excel.

    PARAMETERS:
        df: DataFrame from generate_purchase_report()

    RETURNS:
        File path to the saved Excel file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"purchase_report_{timestamp}.xlsx"

    df.to_excel(filename, index=False, engine='openpyxl')

    return filename


def export_current_stock_to_excel(df):
    """
    Export current stock report to Excel.

    PARAMETERS:
        df: DataFrame from generate_current_stock_report()

    RETURNS:
        File path to the saved Excel file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"current_stock_{timestamp}.xlsx"

    df.to_excel(filename, index=False, engine='openpyxl')

    return filename
