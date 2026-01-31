'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AppLayout } from '@/components/app-layout';
import { apiReports } from '@/lib/api';
import * as XLSX from 'xlsx';

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState('stock-comparison');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const { data: stockComparison } = useQuery({
    queryKey: ['stock-comparison'],
    queryFn: apiReports.getStockComparison,
    enabled: activeTab === 'stock-comparison',
  });

  const { data: currentStock } = useQuery({
    queryKey: ['current-stock-report'],
    queryFn: apiReports.getCurrentStock,
    enabled: activeTab === 'current-stock',
  });

  const { data: salesReport } = useQuery({
    queryKey: ['sales-report', startDate, endDate],
    queryFn: () => apiReports.getSales(startDate, endDate),
    enabled: activeTab === 'sales',
  });

  const { data: purchaseReport } = useQuery({
    queryKey: ['purchase-report', startDate, endDate],
    queryFn: () => apiReports.getPurchases(startDate, endDate),
    enabled: activeTab === 'purchases',
  });

  const exportToExcel = (data: any[], filename: string) => {
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Report');
    XLSX.writeFile(wb, filename);
  };

  const getTabButtonStyle = (tab: string) => ({
    ...styles.tabButton,
    ...(activeTab === tab ? styles.tabButtonActive : {}),
  });

  return (
    <AppLayout>
      <div style={styles.container}>
        <div style={styles.header}>
          <div>
            <h1 style={styles.title}>Reports</h1>
            <p style={styles.subtitle}>View and export inventory reports</p>
          </div>
        </div>

        {/* Tabs */}
        <div style={styles.tabsContainer}>
          <button
            style={getTabButtonStyle('stock-comparison')}
            onClick={() => setActiveTab('stock-comparison')}
          >
            Stock Comparison
          </button>
          <button
            style={getTabButtonStyle('current-stock')}
            onClick={() => setActiveTab('current-stock')}
          >
            Current Stock
          </button>
          <button
            style={getTabButtonStyle('sales')}
            onClick={() => setActiveTab('sales')}
          >
            Sales Report
          </button>
          <button
            style={getTabButtonStyle('purchases')}
            onClick={() => setActiveTab('purchases')}
          >
            Purchase Report
          </button>
        </div>

        {/* Stock Comparison Report */}
        {activeTab === 'stock-comparison' && stockComparison && (
          <>
            {/* Summary Cards */}
            <div style={styles.statsGrid}>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>Total Items</div>
                <div style={styles.statValue}>{stockComparison.summary.total_items}</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>Shortage</div>
                <div style={styles.statValueDanger}>{stockComparison.summary.items_with_shortage}</div>
                <div style={styles.statSubtext}>Rs. {stockComparison.summary.total_shortage_value.toFixed(2)}</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>Excess</div>
                <div style={styles.statValueSuccess}>{stockComparison.summary.items_with_excess}</div>
                <div style={styles.statSubtext}>Rs. {stockComparison.summary.total_excess_value.toFixed(2)}</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>Matching</div>
                <div style={styles.statValue}>{stockComparison.summary.items_matching}</div>
              </div>
            </div>

            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <h2 style={styles.cardTitle}>Stock Comparison Details</h2>
                <button
                  style={styles.exportButton}
                  onClick={() => exportToExcel(stockComparison.items, `stock-comparison-${Date.now()}.xlsx`)}
                >
                  Export Excel
                </button>
              </div>
              <div style={styles.tableContainer}>
                <table style={styles.table}>
                  <thead>
                    <tr style={styles.tableHeader}>
                      <th style={styles.tableCell}>Item Name</th>
                      <th style={styles.tableCell}>System Stock</th>
                      <th style={styles.tableCell}>Physical Stock</th>
                      <th style={styles.tableCell}>Difference</th>
                      <th style={styles.tableCell}>Status</th>
                      <th style={styles.tableCellRight}>Value Impact</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stockComparison.items.map((item) => (
                      <tr key={item.item_id} style={styles.tableRow}>
                        <td style={styles.tableCell}>{item.item_name}</td>
                        <td style={styles.tableCell}>{item.system_stock.toFixed(2)}</td>
                        <td style={styles.tableCell}>{item.physical_stock ?? '-'}</td>
                        <td style={styles.tableCell}>{item.difference?.toFixed(2) ?? '-'}</td>
                        <td style={styles.tableCell}>
                          <span style={{
                            ...styles.statusBadge,
                            ...(item.status === 'SHORTAGE' ? styles.statusDanger :
                              item.status === 'EXCESS' ? styles.statusSuccess :
                              item.status === 'MATCH' ? styles.statusInfo : {})
                          }}>
                            {item.status}
                          </span>
                        </td>
                        <td style={styles.tableCellRight}>
                          {item.value_impact ? `Rs. ${item.value_impact.toFixed(2)}` : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* Current Stock Report */}
        {activeTab === 'current-stock' && currentStock && (
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <h2 style={styles.cardTitle}>Current Stock Report</h2>
              <button
                style={styles.exportButton}
                onClick={() => exportToExcel(currentStock, `current-stock-${Date.now()}.xlsx`)}
              >
                Export Excel
              </button>
            </div>
            <div style={styles.tableContainer}>
              <table style={styles.table}>
                <thead>
                  <tr style={styles.tableHeader}>
                    <th style={styles.tableCell}>Item Name</th>
                    <th style={styles.tableCell}>Grade</th>
                    <th style={styles.tableCell}>Size (L)</th>
                    <th style={styles.tableCellRight}>Stock</th>
                    <th style={styles.tableCellRight}>Purchase Price</th>
                    <th style={styles.tableCellRight}>Sale Price</th>
                    <th style={styles.tableCellRight}>Stock Value</th>
                  </tr>
                </thead>
                <tbody>
                  {currentStock.map((item, index) => (
                    <tr key={index} style={styles.tableRow}>
                      <td style={styles.tableCell}>{item.item_name}</td>
                      <td style={styles.tableCell}>{item.grade || '-'}</td>
                      <td style={styles.tableCell}>{item.pack_size}</td>
                      <td style={styles.tableCellRight}>{item.system_stock}</td>
                      <td style={styles.tableCellRight}>Rs. {item.purchase_price}</td>
                      <td style={styles.tableCellRight}>Rs. {item.sale_price}</td>
                      <td style={styles.tableCellRight}>Rs. {item.stock_value.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Sales Report */}
        {activeTab === 'sales' && (
          <>
            <div style={styles.card}>
              <h2 style={styles.cardTitle}>Filter by Date Range</h2>
              <div style={styles.filterContainer}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Start Date</label>
                  <input
                    style={styles.input}
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>End Date</label>
                  <input
                    style={styles.input}
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </div>
            </div>

            {salesReport && salesReport.length > 0 && (
              <div style={styles.card}>
                <div style={styles.cardHeader}>
                  <h2 style={styles.cardTitle}>Sales Report ({salesReport.length} records)</h2>
                  <button
                    style={styles.exportButton}
                    onClick={() => exportToExcel(salesReport, `sales-report-${Date.now()}.xlsx`)}
                  >
                    Export Excel
                  </button>
                </div>
                <div style={styles.tableContainer}>
                  <table style={styles.table}>
                    <thead>
                      <tr style={styles.tableHeader}>
                        <th style={styles.tableCell}>Date</th>
                        <th style={styles.tableCell}>Cashier</th>
                        <th style={styles.tableCell}>Shift</th>
                        <th style={styles.tableCell}>Item Name</th>
                        <th style={styles.tableCellRight}>Quantity</th>
                      </tr>
                    </thead>
                    <tbody>
                      {salesReport.map((sale, index) => (
                        <tr key={index} style={styles.tableRow}>
                          <td style={styles.tableCell}>{sale.date}</td>
                          <td style={styles.tableCell}>{sale.cashier_name}</td>
                          <td style={styles.tableCell}>{sale.shift}</td>
                          <td style={styles.tableCell}>{sale.item_name}</td>
                          <td style={styles.tableCellRight}>{sale.quantity}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}

        {/* Purchase Report */}
        {activeTab === 'purchases' && (
          <>
            <div style={styles.card}>
              <h2 style={styles.cardTitle}>Filter by Date Range</h2>
              <div style={styles.filterContainer}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Start Date</label>
                  <input
                    style={styles.input}
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>End Date</label>
                  <input
                    style={styles.input}
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </div>
            </div>

            {purchaseReport && purchaseReport.length > 0 && (
              <div style={styles.card}>
                <div style={styles.cardHeader}>
                  <h2 style={styles.cardTitle}>Purchase Report ({purchaseReport.length} records)</h2>
                  <button
                    style={styles.exportButton}
                    onClick={() => exportToExcel(purchaseReport, `purchase-report-${Date.now()}.xlsx`)}
                  >
                    Export Excel
                  </button>
                </div>
                <div style={styles.tableContainer}>
                  <table style={styles.table}>
                    <thead>
                      <tr style={styles.tableHeader}>
                        <th style={styles.tableCell}>Date</th>
                        <th style={styles.tableCell}>Invoice No</th>
                        <th style={styles.tableCell}>Item Name</th>
                        <th style={styles.tableCellRight}>Quantity</th>
                        <th style={styles.tableCellRight}>Rate</th>
                        <th style={styles.tableCellRight}>Total Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {purchaseReport.map((purchase, index) => (
                        <tr key={index} style={styles.tableRow}>
                          <td style={styles.tableCell}>{purchase.date}</td>
                          <td style={styles.tableCell}>{purchase.invoice_no}</td>
                          <td style={styles.tableCell}>{purchase.item_name}</td>
                          <td style={styles.tableCellRight}>{purchase.quantity}</td>
                          <td style={styles.tableCellRight}>Rs. {purchase.rate}</td>
                          <td style={styles.tableCellRight}>Rs. {purchase.total_value.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </AppLayout>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    padding: '0',
  },
  header: {
    marginBottom: '32px',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '14px',
    color: '#64748b',
  },
  tabsContainer: {
    display: 'flex',
    gap: '8px',
    marginBottom: '24px',
    flexWrap: 'wrap' as const,
  },
  tabButton: {
    backgroundColor: 'white',
    color: '#1e293b',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  tabButtonActive: {
    backgroundColor: '#3b82f6',
    color: 'white',
    borderColor: '#3b82f6',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px',
    marginBottom: '32px',
  },
  statCard: {
    backgroundColor: 'white',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    padding: '20px',
  },
  statLabel: {
    fontSize: '13px',
    color: '#64748b',
    marginBottom: '8px',
    fontWeight: '500',
  },
  statValue: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#1e293b',
  },
  statValueDanger: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#dc2626',
  },
  statValueSuccess: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#16a34a',
  },
  statSubtext: {
    fontSize: '12px',
    color: '#94a3b8',
    marginTop: '4px',
  },
  card: {
    backgroundColor: 'white',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
    paddingBottom: '12px',
    borderBottom: '1px solid #e2e8f0',
  },
  cardTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1e293b',
    margin: '0',
  },
  exportButton: {
    backgroundColor: '#10b981',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    padding: '8px 16px',
    fontSize: '13px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  filterContainer: {
    display: 'flex',
    gap: '16px',
    flexWrap: 'wrap' as const,
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '8px',
  },
  label: {
    fontSize: '13px',
    fontWeight: '500',
    color: '#475569',
  },
  input: {
    padding: '10px 12px',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    fontSize: '14px',
    transition: 'border-color 0.2s',
  },
  tableContainer: {
    overflowX: 'auto' as const,
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse' as const,
  },
  tableHeader: {
    backgroundColor: '#f8fafc',
    borderBottom: '2px solid #e2e8f0',
  },
  tableRow: {
    borderBottom: '1px solid #e2e8f0',
    transition: 'background-color 0.2s',
  },
  tableCell: {
    padding: '12px',
    textAlign: 'left' as const,
    fontSize: '14px',
    color: '#1e293b',
  },
  tableCellRight: {
    padding: '12px',
    textAlign: 'right' as const,
    fontSize: '14px',
    color: '#1e293b',
  },
  statusBadge: {
    padding: '4px 10px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: '500',
    display: 'inline-block',
  },
  statusDanger: {
    backgroundColor: '#fecaca',
    color: '#991b1b',
  },
  statusSuccess: {
    backgroundColor: '#bbf7d0',
    color: '#166534',
  },
  statusInfo: {
    backgroundColor: '#bfdbfe',
    color: '#1e40af',
  },
};
