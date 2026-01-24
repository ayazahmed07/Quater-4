import React, { useState, useEffect } from 'react';
import { adminApi } from '../../api';
import { Invoice, InvoiceStatus } from '../../types';

export const Invoices: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      setError(null);
      const data = await adminApi.getInvoices();
      setInvoices(data);
    } catch (error: any) {
      console.error('Failed to load invoices:', error);
      setError(error.response?.data?.detail || 'Failed to load invoices');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (confirm('Generate invoices for all customers?')) {
      try {
        await adminApi.generateInvoices();
        alert('Invoices generated successfully');
        loadInvoices();
      } catch (error) {
        console.error('Failed to generate invoices:', error);
        alert('Failed to generate invoices');
      }
    }
  };

  const getStatusColor = (status: InvoiceStatus) => {
    switch (status) {
      case InvoiceStatus.PAID: return 'green';
      case InvoiceStatus.OVERDUE: return 'red';
      case InvoiceStatus.PARTIAL_PAID: return 'orange';
      default: return 'blue';
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Invoices Management</h2>
        <button onClick={handleGenerate} className="btn-primary">
          Generate Invoices
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {isLoading ? (
        <div className="loading">Loading...</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Invoice #</th>
              <th>Customer</th>
              <th>Period</th>
              <th>Total</th>
              <th>Paid</th>
              <th>Balance</th>
              <th>Status</th>
              <th>Due Date</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((invoice) => (
              <tr key={invoice.id}>
                <td>{invoice.invoice_number}</td>
                <td>{invoice.customer_name}</td>
                <td>
                  {new Date(invoice.billing_period_start).toLocaleDateString()} - {new Date(invoice.billing_period_end).toLocaleDateString()}
                </td>
                <td>${invoice.total_amount.toFixed(2)}</td>
                <td>${invoice.paid_amount.toFixed(2)}</td>
                <td>${invoice.balance_due.toFixed(2)}</td>
                <td>
                  <span style={{ color: getStatusColor(invoice.status), fontWeight: 'bold' }}>
                    {invoice.status}
                  </span>
                </td>
                <td>{new Date(invoice.due_date).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
