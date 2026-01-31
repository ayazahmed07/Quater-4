'use client';

import { useQuery } from '@tanstack/react-query';
import { AppLayout } from '@/components/app-layout';
import { apiDashboard, apiReports } from '@/lib/api';

export default function DashboardPage() {
  // Fetch dashboard stats
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: apiDashboard.getStats,
  });

  // Fetch current stock
  const { data: stock } = useQuery({
    queryKey: ['current-stock'],
    queryFn: apiReports.getCurrentStock,
  });

  // Calculate low stock items and total value
  const lowStockItems = stock?.filter(item => item.system_stock < 20) || [];
  const totalStockValue = stock?.reduce((sum, item) => sum + item.stock_value, 0) || 0;

  if (isLoading) {
    return (
      <AppLayout>
        <div style={styles.loadingContainer}>
          <div style={styles.loadingText}>Loading...</div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div style={styles.container}>
        <h1 style={styles.title}>Dashboard</h1>
        <p style={styles.subtitle}>Welcome to your inventory management system</p>

        {/* Stats Grid */}
        <div style={styles.statsGrid}>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>Total Products</div>
            <div style={styles.statValue}>{stats?.total_items || 0}</div>
          </div>

          <div style={styles.statCard}>
            <div style={styles.statLabel}>Total Stock Value</div>
            <div style={styles.statValue}>
              Rs. {totalStockValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </div>
          </div>

          <div style={styles.statCard}>
            <div style={styles.statLabel}>Total Purchases</div>
            <div style={styles.statValue}>{stats?.total_purchases || 0}</div>
            <div style={styles.statSubtext}>Units purchased</div>
          </div>

          <div style={styles.statCard}>
            <div style={styles.statLabel}>Total Sales</div>
            <div style={styles.statValue}>{stats?.total_sales || 0}</div>
            <div style={styles.statSubtext}>Units sold</div>
          </div>
        </div>

        {/* Two Column Layout */}
        <div style={styles.twoColumnLayout}>
          {/* Low Stock Items */}
          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>
              Low Stock Alerts ({lowStockItems.length})
            </h2>
            <div style={styles.list}>
              {lowStockItems.length === 0 ? (
                <div style={styles.emptyState}>No low stock items</div>
              ) : (
                lowStockItems.slice(0, 10).map((item, index) => (
                  <div key={index} style={styles.listItem}>
                    <div style={styles.listItemContent}>
                      <div style={styles.itemName}>{item.item_name}</div>
                      <div style={styles.itemSubtext}>
                        Grade: {item.grade || 'N/A'} | Pack: {item.pack_size}L
                      </div>
                    </div>
                    <div style={styles.stockBadge}>{item.system_stock} units</div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Stock Summary */}
          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>Stock Summary</h2>
            <div style={styles.list}>
              {stock?.slice(0, 10).map((item, index) => (
                <div key={index} style={styles.listItem}>
                  <div style={styles.listItemContent}>
                    <div style={styles.itemName}>{item.item_name}</div>
                    <div style={styles.itemSubtext}>
                      Grade: {item.grade || 'N/A'} | Rs. {item.sale_price}/unit
                    </div>
                  </div>
                  <div style={styles.stockValue}>
                    <div style={styles.stockQty}>{item.system_stock} units</div>
                    <div style={styles.valueText}>
                      Rs. {item.stock_value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

const styles: Record<string, React.CSSProperties> = {
  loadingContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
  },
  loadingText: {
    fontSize: '18px',
    color: '#64748b',
  },
  container: {
    padding: '0',
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
    marginBottom: '32px',
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
  statSubtext: {
    fontSize: '12px',
    color: '#94a3b8',
    marginTop: '4px',
  },
  twoColumnLayout: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '20px',
  },
  section: {
    backgroundColor: 'white',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    padding: '20px',
  },
  sectionTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: '16px',
    paddingBottom: '12px',
    borderBottom: '1px solid #e2e8f0',
  },
  list: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
  },
  listItem: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px',
    backgroundColor: '#f8fafc',
    borderRadius: '6px',
    border: '1px solid #e2e8f0',
  },
  listItemContent: {
    flex: 1,
  },
  itemName: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#1e293b',
    marginBottom: '4px',
  },
  itemSubtext: {
    fontSize: '12px',
    color: '#64748b',
  },
  stockBadge: {
    backgroundColor: '#fef3c7',
    color: '#92400e',
    padding: '6px 12px',
    borderRadius: '4px',
    fontSize: '13px',
    fontWeight: '500',
  },
  stockValue: {
    textAlign: 'right' as const,
  },
  stockQty: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#1e293b',
  },
  valueText: {
    fontSize: '12px',
    color: '#64748b',
    marginTop: '2px',
  },
  emptyState: {
    textAlign: 'center' as const,
    padding: '40px 20px',
    color: '#94a3b8',
    fontSize: '14px',
  },
};
