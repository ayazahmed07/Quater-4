import React, { useState, useEffect } from 'react';
import { customerApi } from '../../api';
import { Invoice } from '../../types';

export const CustomerInvoices: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    try {
      const data = await customerApi.getInvoices();
      setInvoices(data);
    } catch (error) {
      console.error('Failed to load invoices:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PAID': return 'green';
      case 'OVERDUE': return 'red';
      case 'PARTIAL_PAID': return 'orange';
      default: return 'blue';
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>My Invoices</h2>
      </div>

      {isLoading ? (
        <div className="loading">Loading...</div>
      ) : invoices.length === 0 ? (
        <div className="empty-state">No invoices found</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Invoice #</th>
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
