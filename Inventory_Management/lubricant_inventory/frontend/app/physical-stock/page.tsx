'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AppLayout } from '@/components/app-layout';
import { apiPhysicalStock, apiItems } from '@/lib/api';

export default function PhysicalStockPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    item_id: 0,
    physical_quantity: 0,
  });

  const { data: entries, isLoading } = useQuery({
    queryKey: ['physical-stock'],
    queryFn: apiPhysicalStock.getAll,
  });

  const { data: items } = useQuery({
    queryKey: ['items'],
    queryFn: apiItems.getAll,
  });

  const createMutation = useMutation({
    mutationFn: apiPhysicalStock.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['physical-stock'] });
      setShowForm(false);
      resetForm();
    },
  });

  const resetForm = () => {
    setFormData({
      date: new Date().toISOString().split('T')[0],
      item_id: 0,
      physical_quantity: 0,
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
            <h1 style={styles.title}>Physical Stock</h1>
            <p style={styles.subtitle}>Record physical inventory counts</p>
          </div>
          <button
            style={styles.primaryButton}
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Cancel' : 'Add Physical Count'}
          </button>
        </div>

        {showForm && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Record Physical Count</h2>
            <form onSubmit={handleSubmit} style={styles.form}>
              <div style={styles.formGrid}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Count Date *</label>
                  <input
                    style={styles.input}
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
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
                  <label style={styles.label}>Physical Quantity Counted *</label>
                  <input
                    style={styles.input}
                    type="number"
                    step="0.01"
                    value={formData.physical_quantity}
                    onChange={(e) => setFormData({ ...formData, physical_quantity: parseFloat(e.target.value) })}
                    required
                  />
                </div>
              </div>
              <div style={styles.formActions}>
                <button type="submit" style={styles.primaryButton}>Record Physical Count</button>
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
          <h2 style={styles.cardTitle}>Physical Count History ({entries?.length || 0})</h2>
          <div style={styles.tableContainer}>
            <table style={styles.table}>
              <thead>
                <tr style={styles.tableHeader}>
                  <th style={styles.tableCell}>Date</th>
                  <th style={styles.tableCell}>Item Name</th>
                  <th style={styles.tableCellRight}>Physical Quantity</th>
                </tr>
              </thead>
              <tbody>
                {entries?.map((entry) => (
                  <tr key={entry.entry_id} style={styles.tableRow}>
                    <td style={styles.tableCell}>{entry.date}</td>
                    <td style={styles.tableCell}>{entry.item_name}</td>
                    <td style={styles.tableCellRight}>{entry.physical_quantity}</td>
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
