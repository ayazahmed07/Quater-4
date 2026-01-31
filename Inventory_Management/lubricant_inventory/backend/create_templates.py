"""
Create Excel Import Templates
================================
Create blank templates for items, purchases, and sales import.
"""

import pandas as pd

# 1. Items Import Template
items_data = pd.DataFrame({
    'Item Name': ['Example Item 1', 'Example Item 2'],
    'Grade': ['SG 15W40', 'MGD 10W30'],
    'Pack Size': [1.0, 0.5],
    'Purchase Price': [1500, 800],
    'Sale Price': [1800, 950],
    'Opening Stock': [10, 20]
})

items_data.to_excel('items_import_template.xlsx', index=False)
print("Created: items_import_template.xlsx")

# 2. Purchases Import Template
purchases_data = pd.DataFrame({
    'Date': ['2026-01-30', '2026-01-30'],
    'Invoice No': ['INV-001', 'INV-002'],
    'Item Name': ['Example Item 1', 'Example Item 2'],
    'Quantity': [5, 10],
    'Rate': [1500, 800]
})

purchases_data.to_excel('purchases_import_template.xlsx', index=False)
print("Created: purchases_import_template.xlsx")

# 3. Sales Import Template
sales_data = pd.DataFrame({
    'Date': ['2026-01-30', '2026-01-30'],
    'Cashier': ['Yasir', 'Alam Zaib'],
    'Item Name': ['Example Item 1', 'Example Item 2'],
    'Quantity': [2, 3]
})

sales_data.to_excel('sales_import_template.xlsx', index=False)
print("Created: sales_import_template.xlsx")

print("\nAll templates created successfully!")
print("\nInstructions:")
print("1. Open the template file in Excel")
print("2. Replace the example data with your actual data")
print("3. Keep the same column names (first row)")
print("4. Save the file")
print("5. Use the Import button in the application to upload")
