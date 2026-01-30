"""
APP.PY
=======
This is the MAIN Streamlit application file.

SIMPLE EXPLANATION:
- This file creates the user interface (what you see on screen)
- It uses Streamlit (a Python library for web apps)
- Each page is a different section of the application

HOW TO RUN:
- Open terminal/command prompt
- Navigate to the folder containing this file
- Run: streamlit run app.py
- The app will open in your web browser
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date

# Import our custom modules
from database import init_database
from crud import (
    add_item, get_all_items, get_item_by_id, update_item, import_items_from_excel,
    add_purchase, get_all_purchases,
    add_sale, get_all_sales, get_sales_by_cashier,
    add_physical_stock_entry, get_all_physical_stock, get_system_stock
)
from reports import (
    generate_stock_comparison_report, calculate_summary_totals,
    generate_current_stock_report,
    generate_sales_report, get_sales_by_cashier_summary,
    generate_purchase_report,
    export_comparison_to_excel, export_sales_to_excel,
    export_purchases_to_excel, export_current_stock_to_excel
)


# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Lubricant Inventory Management",
    page_icon="🪟",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# INITIALIZE DATABASE (Run once at startup)
# ============================================
@st.cache_resource
def init_app():
    """
    Initialize the database when the app starts.

    THINK OF IT AS:
    - Making sure the database exists and all tables are created
    - This runs only once when you start the app
    """
    init_database()


init_app()


# ============================================
# SIDEBAR NAVIGATION
# ============================================
st.sidebar.title("🪟 Lubricant Inventory Management")
st.sidebar.markdown("---")

# Create the navigation menu
page = st.sidebar.radio(
    "📋 Navigate to:",
    [
        "📦 Dashboard",
        "📝 Item Master",
        "🛒 Purchase Entry",
        "💰 Sales Entry",
        "🔢 Physical Stock Entry",
        "📊 Reports"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info("""
**System for:**
- Fuel Pump Lubricant Business

**Features:**
- Track purchases from PSO
- Record sales by 2 cashiers
- Weekly physical stock verification
- Stock comparison reports
""")


# ============================================
# PAGE 1: DASHBOARD
# ============================================
if page == "📦 Dashboard":

    st.title("📦 Dashboard")
    st.markdown("---")

    # Quick stats
    items = get_all_items()
    purchases = get_all_purchases()
    sales = get_all_sales()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Total Items", value=len(items))

    with col2:
        total_purchase_qty = sum([p['quantity'] for p in purchases])
        st.metric(label="Total Purchases", value=f"{total_purchase_qty} units")

    with col3:
        total_sales_qty = sum([s['quantity'] for s in sales])
        st.metric(label="Total Sales", value=f"{total_sales_qty} units")

    with col4:
        current_stock = sum([get_system_stock(item['item_id']) for item in items])
        st.metric(label="Current Stock", value=f"{current_stock} units")

    st.markdown("---")

    # Current stock preview
    st.subheader("📊 Current Stock Overview")
    stock_report = generate_current_stock_report()

    if not stock_report.empty:
        st.dataframe(stock_report, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ No items found. Please add items in the Item Master.")


# ============================================
# PAGE 2: ITEM MASTER
# ============================================
elif page == "📝 Item Master":

    st.title("📝 Item Master")
    st.markdown("---")

    # Tabs for different functions
    tab1, tab2, tab3 = st.tabs(["➕ Add New Item", "📥 Import from Excel", "📋 View & Edit Items"])

    # -------------------------
    # TAB 1: Add New Item
    # -------------------------
    with tab1:
        st.subheader("➕ Add New Lubricant Item")

        with st.form("add_item_form"):
            col1, col2 = st.columns(2)

            with col1:
                item_name = st.text_input("Item Name *", placeholder="e.g., HP Lubricant")
                grade = st.text_input("Grade", placeholder="e.g., SAE 10W-40")
                pack_size = st.number_input("Pack Size (Liters) *", min_value=0.1, value=1.0, step=0.5)

            with col2:
                purchase_price = st.number_input("Purchase Price *", min_value=0.0, step=0.01)
                sale_price = st.number_input("Sale Price *", min_value=0.0, step=0.01)
                opening_stock = st.number_input("Opening Stock", min_value=0.0, value=0.0)

            submitted = st.form_submit_button("✅ Add Item")

            if submitted:
                if item_name and purchase_price and sale_price:
                    item_id = add_item(
                        item_name=item_name,
                        grade=grade,
                        pack_size=pack_size,
                        purchase_price=purchase_price,
                        sale_price=sale_price,
                        opening_stock=opening_stock
                    )
                    st.success(f"✅ Item '{item_name}' added successfully! (Item ID: {item_id})")
                    st.cache_data.clear()
                else:
                    st.error("❌ Please fill in all required fields!")

    # -------------------------
    # TAB 2: Import from Excel
    # -------------------------
    with tab2:
        st.subheader("📥 Import Items from Excel")

        st.markdown("""
        **Instructions:**
        1. Create an Excel file with the following columns:
           - Item Name (required)
           - Purchase Price (required)
           - Sale Price (required)
           - Grade (optional)
           - Pack Size (optional, default 1.0)
           - Opening Stock (optional, default 0)

        2. Upload the file below
        3. Click "Import Items"
        """)

        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with item data"
        )

        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)

                st.info("📄 Preview of uploaded file:")
                st.dataframe(df, use_container_width=True)

                if st.button("📥 Import Items", type="primary"):
                    count = import_items_from_excel(df)
                    st.success(f"✅ Successfully imported {count} items!")
                    st.cache_data.clear()
            except Exception as e:
                st.error(f"❌ Error reading file: {e}")

    # -------------------------
    # TAB 3: View & Edit Items
    # -------------------------
    with tab3:
        st.subheader("📋 All Items")

        items = get_all_items()

        if items:
            # Convert to DataFrame for display
            items_df = pd.DataFrame(items)

            # Display full data
            st.dataframe(
                items_df,
                column_config={
                    "item_id": "ID",
                    "item_name": "Item Name",
                    "grade": "Grade",
                    "pack_size": "Pack Size (L)",
                    "purchase_price": "Purchase Price",
                    "sale_price": "Sale Price",
                    "opening_stock": "Opening Stock"
                },
                use_container_width=True,
                hide_index=True
            )

            # Edit section
            st.markdown("---")
            st.subheader("✏️ Edit Item")

            col1, col2 = st.columns([1, 2])

            with col1:
                # Select item to edit
                item_options = {f"{item['item_name']} (ID: {item['item_id']})": item['item_id'] for item in items}
                selected_item = st.selectbox("Select Item to Edit", options=list(item_options.keys()))

            with col2:
                if selected_item:
                    item_id = item_options[selected_item]
                    item = get_item_by_id(item_id)

                    if item:
                        with st.form("edit_item_form"):
                            col1, col2 = st.columns(2)

                            with col1:
                                new_name = st.text_input("Item Name", value=item['item_name'])
                                new_grade = st.text_input("Grade", value=item['grade'])
                                new_pack_size = st.number_input("Pack Size", value=item['pack_size'], min_value=0.1)

                            with col2:
                                new_purchase_price = st.number_input("Purchase Price", value=item['purchase_price'], min_value=0.0, step=0.01)
                                new_sale_price = st.number_input("Sale Price", value=item['sale_price'], min_value=0.0, step=0.01)

                            submitted = st.form_submit_button("💾 Update Item")

                            if submitted:
                                update_item(item_id, new_name, new_grade, new_pack_size, new_purchase_price, new_sale_price)
                                st.success(f"✅ Item '{new_name}' updated successfully!")
                                st.cache_data.clear()
                                st.rerun()
        else:
            st.warning("⚠️ No items found. Add items or import from Excel.")


# ============================================
# PAGE 3: PURCHASE ENTRY
# ============================================
elif page == "🛒 Purchase Entry":

    st.title("🛒 Purchase Entry")
    st.markdown("---")

    # Tabs
    tab1, tab2 = st.tabs(["➕ Add Purchase", "📋 Purchase History"])

    # -------------------------
    # TAB 1: Add Purchase
    # -------------------------
    with tab1:
        st.subheader("➕ Record New Purchase from PSO")

        # Get items for dropdown
        items = get_all_items()

        if not items:
            st.warning("⚠️ No items found. Please add items in the Item Master first.")
        else:
            with st.form("add_purchase_form"):
                col1, col2 = st.columns(2)

                with col1:
                    purchase_date = st.date_input("Date *", value=date.today())
                    invoice_no = st.text_input("Invoice Number *", placeholder="e.g., INV-2024-001")

                    # Item dropdown
                    item_options = {f"{item['item_name']} ({item['pack_size']}L)": item['item_id'] for item in items}
                    selected_item = st.selectbox("Select Item *", options=list(item_options.keys()))

                with col2:
                    quantity = st.number_input("Quantity Purchased *", min_value=0.01, step=1.0)
                    rate = st.number_input("Purchase Rate *", min_value=0.01, step=0.01)

                # Show total value
                if quantity and rate:
                    st.info(f"💵 Total Value: {quantity * rate:.2f}")

                submitted = st.form_submit_button("✅ Record Purchase")

                if submitted:
                    if invoice_no and selected_item and quantity and rate:
                        item_id = item_options[selected_item]
                        date_str = purchase_date.strftime("%Y-%m-%d")

                        add_purchase(date_str, invoice_no, item_id, quantity, rate)

                        st.success(f"✅ Purchase recorded successfully!")
                        st.info(f"📦 Stock for '{selected_item}' has been increased by {quantity} units")
                        st.cache_data.clear()
                    else:
                        st.error("❌ Please fill in all required fields!")

    # -------------------------
    # TAB 2: Purchase History
    # -------------------------
    with tab2:
        st.subheader("📋 All Purchases")

        purchases = get_all_purchases()

        if purchases:
            purchases_df = pd.DataFrame(purchases)

            # Remove item_id from display
            if 'item_id' in purchases_df.columns:
                purchases_df = purchases_df.drop(columns=['item_id'])

            # Reorder columns
            columns_order = ['date', 'invoice_no', 'item_name', 'quantity', 'rate']
            purchases_df = purchases_df[columns_order]

            purchases_df.columns = ['Date', 'Invoice No', 'Item Name', 'Quantity', 'Rate']

            st.dataframe(purchases_df, use_container_width=True, hide_index=True)

            # Export button
            if st.button("📥 Export to Excel"):
                export_df = generate_purchase_report()
                filename = export_purchases_to_excel(export_df)
                st.success(f"✅ Report exported: {filename}")
        else:
            st.warning("⚠️ No purchases recorded yet.")


# ============================================
# PAGE 4: SALES ENTRY
# ============================================
elif page == "💰 Sales Entry":

    st.title("💰 Sales Entry")
    st.markdown("---")

    # Tabs
    tab1, tab2 = st.tabs(["➕ Add Sale", "📋 Sales History"])

    # -------------------------
    # TAB 1: Add Sale
    # -------------------------
    with tab1:
        st.subheader("➕ Record New Sale")

        # Get items for dropdown
        items = get_all_items()

        if not items:
            st.warning("⚠️ No items found. Please add items in the Item Master first.")
        else:
            with st.form("add_sale_form"):
                col1, col2 = st.columns(2)

                with col1:
                    sale_date = st.date_input("Date *", value=date.today())

                    # Cashier selection
                    cashier_options = ["Cashier 1", "Cashier 2"]
                    cashier_name = st.selectbox("Cashier Name *", options=cashier_options)

                    # Shift selection
                    shift_options = ["Morning", "Evening"]
                    shift = st.selectbox("Shift *", options=shift_options)

                    # Item dropdown
                    item_options = {f"{item['item_name']} ({item['pack_size']}L) - Stock: {get_system_stock(item['item_id'])}":
                                    item['item_id'] for item in items}
                    selected_item = st.selectbox("Select Item *", options=list(item_options.keys()))

                    # Show current stock
                    if selected_item:
                        item_id = item_options[selected_item]
                        current_stock = get_system_stock(item_id)
                        st.info(f"📦 Current Stock: {current_stock} units")

                with col2:
                    quantity = st.number_input("Quantity Sold *", min_value=0.01, step=1.0)

                    # Show sale value
                    if selected_item and quantity:
                        item = get_item_by_id(item_id)
                        if item:
                            total_value = quantity * item['sale_price']
                            st.info(f"💵 Sale Value: {total_value:.2f}")

                submitted = st.form_submit_button("✅ Record Sale")

                if submitted:
                    if selected_item and quantity:
                        item_id = item_options[selected_item]
                        date_str = sale_date.strftime("%Y-%m-%d")

                        # Check stock and record sale
                        success = add_sale(date_str, cashier_name, shift, item_id, quantity)

                        if success:
                            st.success(f"✅ Sale recorded successfully!")
                            st.info(f"📦 Stock has been reduced by {quantity} units")
                            st.cache_data.clear()
                        else:
                            st.error(f"❌ Insufficient stock! Current stock: {current_stock}, Requested: {quantity}")
                    else:
                        st.error("❌ Please fill in all required fields!")

    # -------------------------
    # TAB 2: Sales History
    # -------------------------
    with tab2:
        st.subheader("📋 All Sales")

        sales = get_all_sales()

        if sales:
            sales_df = pd.DataFrame(sales)

            # Remove item_id from display
            if 'item_id' in sales_df.columns:
                sales_df = sales_df.drop(columns=['item_id'])

            # Reorder columns
            columns_order = ['date', 'cashier_name', 'shift', 'item_name', 'quantity']
            sales_df = sales_df[columns_order]

            sales_df.columns = ['Date', 'Cashier', 'Shift', 'Item Name', 'Quantity']

            st.dataframe(sales_df, use_container_width=True, hide_index=True)

            # Cashier-wise summary
            st.markdown("---")
            st.subheader("👥 Cashier Performance Summary")
            cashier_summary = get_sales_by_cashier_summary()

            if not cashier_summary.empty:
                st.dataframe(cashier_summary, use_container_width=True, hide_index=True)

            # Export button
            if st.button("📥 Export to Excel"):
                export_df = generate_sales_report()
                filename = export_sales_to_excel(export_df)
                st.success(f"✅ Report exported: {filename}")
        else:
            st.warning("⚠️ No sales recorded yet.")


# ============================================
# PAGE 5: PHYSICAL STOCK ENTRY
# ============================================
elif page == "🔢 Physical Stock Entry":

    st.title("🔢 Physical Stock Entry")
    st.markdown("---")

    st.info("ℹ️ This is for weekly physical stock verification. Enter the actual quantity found during physical count.")

    # Tabs
    tab1, tab2 = st.tabs(["➕ Add Physical Count", "📋 Physical Count History"])

    # -------------------------
    # TAB 1: Add Physical Count
    # -------------------------
    with tab1:
        st.subheader("➕ Record Physical Stock Count")

        # Get items for dropdown
        items = get_all_items()

        if not items:
            st.warning("⚠️ No items found. Please add items in the Item Master first.")
        else:
            with st.form("add_physical_stock_form"):
                col1, col2 = st.columns(2)

                with col1:
                    count_date = st.date_input("Count Date *", value=date.today())

                    # Item dropdown
                    item_options = {f"{item['item_name']} ({item['pack_size']}L)": item['item_id'] for item in items}
                    selected_item = st.selectbox("Select Item *", options=list(item_options.keys()))

                    # Show system stock
                    if selected_item:
                        item_id = item_options[selected_item]
                        system_stock = get_system_stock(item_id)
                        st.info(f"📊 System Stock: {system_stock} units")

                with col2:
                    physical_quantity = st.number_input("Physical Quantity Counted *", min_value=0.0, step=1.0)

                    # Show difference
                    if selected_item and physical_quantity:
                        difference = system_stock - physical_quantity
                        if difference > 0:
                            st.error(f"⚠️ SHORTAGE: {difference} units")
                        elif difference < 0:
                            st.success(f"✅ EXCESS: {abs(difference)} units")
                        else:
                            st.success("✅ MATCH: Stock matches exactly!")

                submitted = st.form_submit_button("✅ Record Physical Count")

                if submitted:
                    if selected_item and physical_quantity:
                        item_id = item_options[selected_item]
                        date_str = count_date.strftime("%Y-%m-%d")

                        add_physical_stock_entry(date_str, item_id, physical_quantity)

                        st.success(f"✅ Physical count recorded successfully!")
                        st.cache_data.clear()
                    else:
                        st.error("❌ Please fill in all required fields!")

    # -------------------------
    # TAB 2: Physical Count History
    # -------------------------
    with tab2:
        st.subheader("📋 Physical Count History")

        physical_counts = get_all_physical_stock()

        if physical_counts:
            counts_df = pd.DataFrame(physical_counts)

            # Remove entry_id from display
            if 'entry_id' in counts_df.columns:
                counts_df = counts_df.drop(columns=['entry_id'])

            # Remove item_id from display
            if 'item_id' in counts_df.columns:
                counts_df = counts_df.drop(columns=['item_id'])

            counts_df.columns = ['Date', 'Item Name', 'Physical Quantity']

            st.dataframe(counts_df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ No physical counts recorded yet.")


# ============================================
# PAGE 6: REPORTS
# ============================================
elif page == "📊 Reports":

    st.title("📊 Reports")
    st.markdown("---")

    # Report selection
    report_type = st.radio(
        "Select Report Type:",
        [
            "🔍 Stock Comparison Report (System vs Physical)",
            "📦 Current Stock Report",
            "💰 Sales Report",
            "🛒 Purchase Report"
        ]
    )

    # -------------------------
    # REPORT 1: Stock Comparison
    # -------------------------
    if report_type == "🔍 Stock Comparison Report (System vs Physical)":

        st.subheader("🔍 Stock Comparison Report")
        st.info("ℹ️ This report compares System Stock (calculated) with Physical Stock (counted)")

        # Generate report
        comparison_df = generate_stock_comparison_report()
        summary = calculate_summary_totals(comparison_df)

        if not comparison_df.empty:
            # Summary cards
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Items", summary['total_items'])

            with col2:
                st.metric("Items with Shortage", summary['items_with_shortage'],
                         f"Value: {summary['total_shortage_value']:.2f}")

            with col3:
                st.metric("Items with Excess", summary['items_with_excess'],
                         f"Value: {summary['total_excess_value']:.2f}")

            with col4:
                st.metric("Items Matching", summary['items_matching'])

            st.markdown("---")

            # Detailed comparison table
            st.subheader("📋 Detailed Comparison")

            # Color-code the status
            def color_status(val):
                if val == 'SHORTAGE':
                    return 'background-color: #ffcccc'
                elif val == 'EXCESS':
                    return 'background-color: #ccffcc'
                elif val == 'MATCH':
                    return 'background-color: #e6f3ff'
                return ''

            # Display the dataframe
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)

            # Export button
            if st.button("📥 Export Comparison Report to Excel"):
                filename = export_comparison_to_excel(comparison_df, summary)
                st.success(f"✅ Report exported: {filename}")

        else:
            st.warning("⚠️ No items found. Please add items first.")

    # -------------------------
    # REPORT 2: Current Stock
    # -------------------------
    elif report_type == "📦 Current Stock Report":

        st.subheader("📦 Current Stock Report")
        st.info("ℹ️ This shows the current system stock for all items")

        stock_df = generate_current_stock_report()

        if not stock_df.empty:
            st.dataframe(stock_df, use_container_width=True, hide_index=True)

            # Export button
            if st.button("📥 Export Stock Report to Excel"):
                filename = export_current_stock_to_excel(stock_df)
                st.success(f"✅ Report exported: {filename}")
        else:
            st.warning("⚠️ No items found.")

    # -------------------------
    # REPORT 3: Sales Report
    # -------------------------
    elif report_type == "💰 Sales Report":

        st.subheader("💰 Sales Report")

        # Date range filter (optional)
        with st.expander("🔧 Filter by Date Range (Optional)"):
            col1, col2 = st.columns(2)
            with col1:
                filter_start = st.date_input("Start Date", value=None)
            with col2:
                filter_end = st.date_input("End Date", value=None)

            apply_filter = st.button("Apply Filter")

        # Generate report
        if apply_filter and filter_start and filter_end:
            sales_df = generate_sales_report(
                start_date=filter_start.strftime("%Y-%m-%d"),
                end_date=filter_end.strftime("%Y-%m-%d")
            )
        else:
            sales_df = generate_sales_report()

        if not sales_df.empty:
            st.dataframe(sales_df, use_container_width=True, hide_index=True)

            # Cashier-wise summary
            st.markdown("---")
            st.subheader("👥 Cashier Performance")
            cashier_summary = get_sales_by_cashier_summary()
            st.dataframe(cashier_summary, use_container_width=True, hide_index=True)

            # Export button
            if st.button("📥 Export Sales Report to Excel"):
                filename = export_sales_to_excel(sales_df)
                st.success(f"✅ Report exported: {filename}")
        else:
            st.warning("⚠️ No sales records found.")

    # -------------------------
    # REPORT 4: Purchase Report
    # -------------------------
    elif report_type == "🛒 Purchase Report":

        st.subheader("🛒 Purchase Report")

        # Date range filter (optional)
        with st.expander("🔧 Filter by Date Range (Optional)"):
            col1, col2 = st.columns(2)
            with col1:
                filter_start = st.date_input("Start Date", value=None, key="purchase_start")
            with col2:
                filter_end = st.date_input("End Date", value=None, key="purchase_end")

            apply_filter = st.button("Apply Filter", key="purchase_filter")

        # Generate report
        if apply_filter and filter_start and filter_end:
            purchase_df = generate_purchase_report(
                start_date=filter_start.strftime("%Y-%m-%d"),
                end_date=filter_end.strftime("%Y-%m-%d")
            )
        else:
            purchase_df = generate_purchase_report()

        if not purchase_df.empty:
            st.dataframe(purchase_df, use_container_width=True, hide_index=True)

            # Export button
            if st.button("📥 Export Purchase Report to Excel"):
                filename = export_purchases_to_excel(purchase_df)
                st.success(f"✅ Report exported: {filename}")
        else:
            st.warning("⚠️ No purchase records found.")


# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    <p>Lubricant Inventory Management System | 100% Offline | SQLite Database</p>
    <p>Built with Streamlit, Python, and Pandas</p>
</div>
""", unsafe_allow_html=True)
