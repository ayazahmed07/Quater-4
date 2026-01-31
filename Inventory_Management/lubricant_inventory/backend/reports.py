"""
REPORTS.PY - Report Generation
===============================
Stock comparison and report generation logic.
"""

from typing import List, Dict
from crud import (
    get_all_items, get_system_stock, get_all_purchases,
    get_all_sales, get_latest_physical_stock, get_all_stock_summary,
    get_cashier_summary
)


# ==================== STOCK COMPARISON REPORT ====================

def generate_stock_comparison_report() -> Dict:
    """
    Generate stock comparison report (system vs physical).

    Returns dict with 'items' and 'summary' keys.
    """
    items = get_all_items()
    latest_physical = get_latest_physical_stock()

    report_items = []
    total_shortage_value = 0
    total_excess_value = 0
    items_with_shortage = 0
    items_with_excess = 0
    items_matching = 0
    items_no_count = 0

    for item in items:
        item_id = item['item_id']
        system_stock = get_system_stock(item_id)
        physical_stock = latest_physical.get(item_id, None)

        if physical_stock is not None:
            difference = system_stock - physical_stock

            if difference > 0:
                status = "SHORTAGE"
                items_with_shortage += 1
            elif difference < 0:
                status = "EXCESS"
                items_with_excess += 1
            else:
                status = "MATCH"
                items_matching += 1

            value_impact = abs(difference) * item['sale_price']

            if status == "SHORTAGE":
                total_shortage_value += value_impact
            elif status == "EXCESS":
                total_excess_value += value_impact
        else:
            difference = None
            status = "NO PHYSICAL COUNT"
            value_impact = None
            items_no_count += 1

        report_items.append({
            'item_id': item_id,
            'item_name': item['item_name'],
            'grade': item['grade'],
            'pack_size': item['pack_size'],
            'opening_stock': item['opening_stock'],
            'total_purchases': _get_total_purchases(item_id),
            'total_sales': _get_total_sales(item_id),
            'system_stock': system_stock,
            'physical_stock': physical_stock,
            'difference': difference,
            'status': status,
            'rate': item['sale_price'],
            'value_impact': value_impact
        })

    summary = {
        'total_items': len(items),
        'items_with_shortage': items_with_shortage,
        'items_with_excess': items_with_excess,
        'items_matching': items_matching,
        'items_no_count': items_no_count,
        'total_shortage_value': total_shortage_value,
        'total_excess_value': total_excess_value
    }

    return {
        'items': report_items,
        'summary': summary
    }


def _get_total_purchases(item_id: int) -> float:
    """Helper: Get total purchases for an item."""
    from crud import _execute_query, _dict_from_row

    result = _execute_query("SELECT COALESCE(SUM(quantity), 0) as total FROM purchases WHERE item_id = ?", (item_id,), fetch='one')
    if result:
        row = _dict_from_row(result)
        return row['total'] if row else 0
    return 0


def _get_total_sales(item_id: int) -> float:
    """Helper: Get total sales for an item."""
    from crud import _execute_query, _dict_from_row

    result = _execute_query("SELECT COALESCE(SUM(quantity), 0) as total FROM sales WHERE item_id = ?", (item_id,), fetch='one')
    if result:
        row = _dict_from_row(result)
        return row['total'] if row else 0
    return 0


# ==================== CURRENT STOCK REPORT ====================

def generate_current_stock_report() -> List[Dict]:
    """Generate current stock report for all items."""
    items = get_all_items()
    stock_data = []

    for item in items:
        system_stock = get_system_stock(item['item_id'])

        stock_data.append({
            'item_name': item['item_name'],
            'grade': item['grade'],
            'pack_size': item['pack_size'],
            'system_stock': system_stock,
            'purchase_price': item['purchase_price'],
            'sale_price': item['sale_price'],
            'stock_value': system_stock * item['purchase_price']
        })

    return stock_data


# ==================== SALES REPORT ====================

def generate_sales_report(start_date: str = None, end_date: str = None) -> List[Dict]:
    """Generate sales report, optionally filtered by date range."""
    if start_date and end_date:
        from crud import get_sales_by_date_range
        sales = get_sales_by_date_range(start_date, end_date)
    else:
        sales = get_all_sales()

    if not sales:
        return []

    return [{
        'date': s['date'],
        'cashier_name': s['cashier_name'],
        'shift': s['shift'],
        'item_name': s['item_name'],
        'quantity': s['quantity']
    } for s in sales]


# ==================== PURCHASE REPORT ====================

def generate_purchase_report(start_date: str = None, end_date: str = None) -> List[Dict]:
    """Generate purchase report, optionally filtered by date range."""
    if start_date and end_date:
        from crud import get_purchases_by_date_range
        purchases = get_purchases_by_date_range(start_date, end_date)
    else:
        purchases = get_all_purchases()

    if not purchases:
        return []

    return [{
        'date': p['date'],
        'invoice_no': p['invoice_no'],
        'item_name': p['item_name'],
        'quantity': p['quantity'],
        'rate': p['rate'],
        'total_value': p['quantity'] * p['rate']
    } for p in purchases]
