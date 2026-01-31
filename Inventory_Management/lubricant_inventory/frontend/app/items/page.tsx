'use client';

import { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AppLayout } from '@/components/app-layout';
import { apiItems } from '@/lib/api';

export default function ItemsPage() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    item_name: '',
    grade: '',
    pack_size: 1.0,
    purchase_price: 0,
    sale_price: 0,
    opening_stock: 0,
  });

  const { data: items, isLoading } = useQuery({
    queryKey: ['items'],
    queryFn: apiItems.getAll,
  });

  // Filter items based on search term
  const filteredItems = items?.filter(item =>
    item.item_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (item.grade && item.grade.toLowerCase().includes(searchTerm.toLowerCase()))
  ) || [];

  const createMutation = useMutation({
    mutationFn: apiItems.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      setShowAddForm(false);
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => apiItems.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      setEditingItem(null);
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: apiItems.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });

  const resetForm = () => {
    setFormData({
      item_name: '',
      grade: '',
      pack_size: 1.0,
      purchase_price: 0,
      sale_price: 0,
      opening_stock: 0,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.item_id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleEdit = (item: any) => {
    setEditingItem(item);
    setFormData({
      item_name: item.item_name,
      grade: item.grade || '',
      pack_size: item.pack_size,
      purchase_price: item.purchase_price,
      sale_price: item.sale_price,
      opening_stock: item.opening_stock,
    });
    setShowAddForm(true);
  };

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this item?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      try {
        await apiItems.import(file);
        queryClient.invalidateQueries({ queryKey: ['items'] });
        alert('Items imported successfully!');
      } catch (err: any) {
        alert('Error importing file: ' + (err.response?.data?.detail || err.message));
      }
    }
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
            <h1 style={styles.title}>Items</h1>
            <p style={styles.subtitle}>Manage your inventory items</p>
          </div>
          <div style={styles.headerRight}>
            <input
              style={styles.searchInput}
              type="text"
              placeholder="Search items..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
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
                onClick={() => { setShowAddForm(true); setEditingItem(null); resetForm(); }}
              >
                Add Item
              </button>
            </div>
          </div>
        </div>

        {showAddForm && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>{editingItem ? 'Edit Item' : 'Add New Item'}</h2>
            <form onSubmit={handleSubmit} style={styles.form}>
              <div style={styles.formGrid}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Item Name *</label>
                  <input
                    style={styles.input}
                    value={formData.item_name}
                    onChange={(e) => setFormData({ ...formData, item_name: e.target.value })}
                    required
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Grade</label>
                  <input
                    style={styles.input}
                    value={formData.grade}
                    onChange={(e) => setFormData({ ...formData, grade: e.target.value })}
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Pack Size (Liters) *</label>
                  <input
                    style={styles.input}
                    type="number"
                    step="0.1"
                    value={formData.pack_size}
                    onChange={(e) => setFormData({ ...formData, pack_size: parseFloat(e.target.value) })}
                    required
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Purchase Price *</label>
                  <input
                    style={styles.input}
                    type="number"
                    step="0.01"
                    value={formData.purchase_price}
                    onChange={(e) => setFormData({ ...formData, purchase_price: parseFloat(e.target.value) })}
                    required
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Sale Price *</label>
                  <input
                    style={styles.input}
                    type="number"
                    step="0.01"
                    value={formData.sale_price}
                    onChange={(e) => setFormData({ ...formData, sale_price: parseFloat(e.target.value) })}
                    required
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>Opening Stock</label>
                  <input
                    style={styles.input}
                    type="number"
                    step="1"
                    value={formData.opening_stock}
                    onChange={(e) => setFormData({ ...formData, opening_stock: parseFloat(e.target.value) })}
                  />
                </div>
              </div>
              <div style={styles.formActions}>
                <button type="submit" style={styles.primaryButton}>
                  {editingItem ? 'Update' : 'Add'} Item
                </button>
                <button
                  type="button"
                  style={styles.secondaryButton}
                  onClick={() => { setShowAddForm(false); setEditingItem(null); resetForm(); }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div style={styles.card}>
          <h2 style={styles.cardTitle}>All Items {searchTerm && `(Filtered: ${filteredItems.length})`} ({!searchTerm && (items?.length || 0)})</h2>
          <div style={styles.tableContainer}>
            <table style={styles.table}>
              <thead>
                <tr style={styles.tableHeader}>
                  <th style={styles.tableCell}>Item Name</th>
                  <th style={styles.tableCell}>Grade</th>
                  <th style={styles.tableCell}>Size (L)</th>
                  <th style={styles.tableCellRight}>Purchase Price</th>
                  <th style={styles.tableCellRight}>Sale Price</th>
                  <th style={styles.tableCellRight}>Opening Stock</th>
                  <th style={styles.tableCellRight}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.length > 0 ? (
                  filteredItems.map((item) => (
                    <tr key={item.item_id} style={styles.tableRow}>
                      <td style={styles.tableCell}>{item.item_name}</td>
                      <td style={styles.tableCell}>{item.grade || '-'}</td>
                      <td style={styles.tableCell}>{item.pack_size}</td>
                      <td style={styles.tableCellRight}>Rs. {item.purchase_price}</td>
                      <td style={styles.tableCellRight}>Rs. {item.sale_price}</td>
                      <td style={styles.tableCellRight}>{item.opening_stock}</td>
                      <td style={styles.tableCellRight}>
                        <button
                          style={styles.iconButton}
                          onClick={() => handleEdit(item)}
                          title="Edit"
                        >
                          ✏️
                        </button>
                        <button
                          style={styles.iconButton}
                          onClick={() => handleDelete(item.item_id)}
                          title="Delete"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} style={styles.noResultsCell}>
                      {searchTerm ? 'No items found matching your search' : 'No items yet. Add your first item to get started!'}
                    </td>
                  </tr>
                )}
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
    gap: '20px',
    flexWrap: 'wrap' as const,
  },
  headerRight: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'flex-end',
    gap: '12px',
  },
  searchInput: {
    padding: '10px 16px',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    fontSize: '14px',
    minWidth: '250px',
    transition: 'border-color 0.2s',
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
  buttonGroup: {
    display: 'flex',
    gap: '12px',
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
  noResultsCell: {
    padding: '48px',
    textAlign: 'center' as const,
    fontSize: '14px',
    color: '#64748b',
    fontStyle: 'italic' as const,
  },
  iconButton: {
    backgroundColor: 'transparent',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    marginLeft: '8px',
    opacity: 0.6,
    transition: 'opacity 0.2s',
  },
};
