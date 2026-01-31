'use client';

import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AppLayout } from '@/components/app-layout';
import { apiSales, apiItems } from '@/lib/api';

export default function SalesPage() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [user, setUser] = useState<any>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    cashier_name: '',
    shift: 'Yasir',  // Changed default to Yasir
    item_id: 0,
    quantity: 0,
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      try {
        await apiSales.import(file);
        queryClient.invalidateQueries({ queryKey: ['sales', 'dashboard-stats'] });
        alert('Sales imported successfully!');
      } catch (err: any) {
        alert('Error importing file: ' + (err.response?.data?.detail || err.message));
      }
    }
  };

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      setFormData(prev => ({
        ...prev,
        cashier_name: parsedUser.full_name || '',
      }));
    }
  }, []);

  const { data: sales, isLoading } = useQuery({
    queryKey: ['sales'],
    queryFn: () => apiSales.getAll(),
  });

  const { data: summary } = useQuery({
    queryKey: ['sales-summary'],
    queryFn: apiSales.getSummary,
  });

  const { data: items } = useQuery({
    queryKey: ['items'],
    queryFn: apiItems.getAll,
  });

  const createMutation = useMutation({
    mutationFn: apiSales.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales', 'dashboard-stats'] });
      setShowForm(false);
      resetForm();
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || 'Error creating sale');
    },
  });

  const resetForm = () => {
    setFormData({
      date: new Date().toISOString().split('T')[0],
      cashier_name: 'Yasir',
      shift: 'Yasir',
      item_id: 0,
      quantity: 0,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

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
        <div style={styles.header}>
          <div>
            <h1 style={styles.title}>Sales</h1>
            <p style={styles.subtitle}>Record and track all sales</p>
          </div>
          <div style={styles.buttonGroup}>
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
            <button
              style={styles.secondaryButton}
              onClick={() => fileInputRef.current?.click()}
            >
              Import Excel
            </button>
            <button
              style={styles.primaryButton}
              onClick={() => setShowForm(!showForm)}
            >
              {showForm ? 'Cancel' : 'Add Sale'}
            </button>
          </div>
        </div>

        {/* Cashier Performance Summary */}
        {summary && summary.length > 0 && (
          <div style={styles.statsGrid}>
            {summary.map((s, index) => (
              <div key={index} style={styles.statCard}>
                <div style={styles.statLabel}>{s.cashier_name}</div>
                <div style={styles.statValue}>{s.total_quantity}</div>
                <div style={styles.statSubtext}>{s.total_transactions} transactions</div>
              </div>
            ))}
          </div>
        )}

        {showForm && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Record New Sale</h2>
            <form onSubmit={handleSubmit} style={styles.form}>
              <div style={styles.formGrid}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Date *</label>
                  <input
                    style={styles.input}
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    required
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Cashier *</label>
                  <select
                    style={styles.select}
                    value={formData.shift}
                    onChange={(e) => setFormData({ ...formData, shift: e.target.value, cashier_name: e.target.value })}
                    required
                  >
                    <option value="Yasir">Yasir</option>
                    <option value="Alam Zaib">Alam Zaib</option>
                  </select>
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Item *</label>
                  <select
                    style={styles.select}
                    value={formData.item_id}
                    onChange={(e) => setFormData({ ...formData, item_id: parseInt(e.target.value) })}
                    required
                  >
                    <option value="">Select Item</option>
                    {items?.map((item) => (
                      <option key={item.item_id} value={item.item_id}>
                        {item.item_name} ({item.pack_size}L) - Rs. {item.sale_price}
                      </option>
                    ))}
                  </select>
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Quantity *</label>
                  <input
                    style={styles.input}
                    type="number"
                    step="0.01"
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
                    required
                  />
                </div>
              </div>
              <div style={styles.formActions}>
                <button type="submit" style={styles.primaryButton}>Record Sale</button>
                <button
                  type="button"
                  style={styles.secondaryButton}
                  onClick={() => { setShowForm(false); resetForm(); }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Sales History ({sales?.length || 0})</h2>
          <div style={styles.tableContainer}>
            <table style={styles.table}>
              <thead>
                <tr style={styles.tableHeader}>
                  <th style={styles.tableCell}>Date</th>
                  <th style={styles.tableCell}>Cashier</th>
                  <th style={styles.tableCell}>Item Name</th>
                  <th style={styles.tableCellRight}>Quantity</th>
                </tr>
              </thead>
              <tbody>
                {sales?.map((sale) => (
                  <tr key={sale.sale_id} style={styles.tableRow}>
                    <td style={styles.tableCell}>{sale.date}</td>
                    <td style={styles.tableCell}>{sale.cashier_name}</td>
                    <td style={styles.tableCell}>{sale.item_name}</td>
                    <td style={styles.tableCellRight}>{sale.quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
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
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '32px',
  },
  buttonGroup: {
    display: 'flex',
    gap: '12px',
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
  primaryButton: {
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  secondaryButton: {
    backgroundColor: 'white',
    color: '#1e293b',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
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
  card: {
    backgroundColor: 'white',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px',
  },
  cardTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: '16px',
    paddingBottom: '12px',
    borderBottom: '1px solid #e2e8f0',
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '20px',
  },
  formGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '16px',
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
  select: {
    padding: '10px 12px',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: 'white',
    transition: 'border-color 0.2s',
  },
  formActions: {
    display: 'flex',
    gap: '12px',
    paddingTop: '8px',
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
};
