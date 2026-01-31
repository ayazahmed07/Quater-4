'use client';

import { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AppLayout } from '@/components/app-layout';
import { apiPurchases, apiItems } from '@/lib/api';

export default function PurchasesPage() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    invoice_no: '',
    item_id: 0,
    quantity: 0,
    rate: 0,
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      try {
        await apiPurchases.import(file);
        queryClient.invalidateQueries({ queryKey: ['purchases', 'dashboard-stats'] });
        alert('Purchases imported successfully!');
      } catch (err: any) {
        alert('Error importing file: ' + (err.response?.data?.detail || err.message));
      }
    }
  };

  const { data: purchases, isLoading } = useQuery({
    queryKey: ['purchases'],
    queryFn: () => apiPurchases.getAll(),
  });

  const { data: items } = useQuery({
    queryKey: ['items'],
    queryFn: apiItems.getAll,
  });

  const createMutation = useMutation({
    mutationFn: apiPurchases.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchases', 'dashboard-stats'] });
      setShowForm(false);
      resetForm();
    },
  });

  const resetForm = () => {
    setFormData({
      date: new Date().toISOString().split('T')[0],
      invoice_no: '',
      item_id: 0,
      quantity: 0,
      rate: 0,
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
            <h1 style={styles.title}>Purchases</h1>
            <p style={styles.subtitle}>Track all inventory purchases</p>
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
              {showForm ? 'Cancel' : 'Add Purchase'}
            </button>
          </div>
        </div>

        {showForm && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Record New Purchase</h2>
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
                  <label style={styles.label}>Invoice Number *</label>
                  <input
                    style={styles.input}
                    value={formData.invoice_no}
                    onChange={(e) => setFormData({ ...formData, invoice_no: e.target.value })}
                    required
                  />
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
                        {item.item_name} ({item.pack_size}L)
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
                <div style={styles.formGroup}>
                  <label style={styles.label}>Rate *</label>
                  <input
                    style={styles.input}
                    type="number"
                    step="0.01"
                    value={formData.rate}
                    onChange={(e) => setFormData({ ...formData, rate: parseFloat(e.target.value) })}
                    required
                  />
                </div>
                {formData.quantity && formData.rate && (
                  <div style={styles.totalDisplay}>
                    <div style={styles.totalLabel}>Total Value</div>
                    <div style={styles.totalValue}>Rs. {(formData.quantity * formData.rate).toFixed(2)}</div>
                  </div>
                )}
              </div>
              <div style={styles.formActions}>
                <button type="submit" style={styles.primaryButton}>Record Purchase</button>
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
          <h2 style={styles.cardTitle}>Purchase History ({purchases?.length || 0})</h2>
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
                {purchases?.map((purchase) => (
                  <tr key={purchase.purchase_id} style={styles.tableRow}>
                    <td style={styles.tableCell}>{purchase.date}</td>
                    <td style={styles.tableCell}>{purchase.invoice_no}</td>
                    <td style={styles.tableCell}>{purchase.item_name}</td>
                    <td style={styles.tableCellRight}>{purchase.quantity}</td>
                    <td style={styles.tableCellRight}>Rs. {purchase.rate}</td>
                    <td style={styles.tableCellRight}>Rs. {(purchase.quantity * purchase.rate).toFixed(2)}</td>
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
  totalDisplay: {
    padding: '16px',
    backgroundColor: '#f0f9ff',
    borderRadius: '6px',
    border: '1px solid #bae6fd',
  },
  totalLabel: {
    fontSize: '12px',
    color: '#0369a1',
    marginBottom: '4px',
  },
  totalValue: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#0c4a6e',
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
