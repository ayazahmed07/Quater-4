import React, { useState, useEffect } from 'react';
import { adminApi } from '../../api';
import { FuelingTransaction, TransactionStatus } from '../../types';

export const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<FuelingTransaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      setError(null);
      const data = await adminApi.getPendingTransactions();
      setTransactions(data);
    } catch (error: any) {
      console.error('Failed to load transactions:', error);
      setError(error.response?.data?.detail || 'Failed to load transactions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async (id: number) => {
    try {
      await adminApi.confirmTransaction(id);
      loadTransactions();
    } catch (error) {
      console.error('Failed to confirm transaction:', error);
    }
  };

  const handleReject = async (id: number) => {
    const reason = prompt('Enter rejection reason:');
    if (reason) {
      try {
        await adminApi.rejectTransaction(id, reason);
        loadTransactions();
      } catch (error) {
        console.error('Failed to reject transaction:', error);
      }
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Pending Transactions</h2>
      </div>

      {error && <div className="error-message">{error}</div>}

      {isLoading ? (
        <div className="loading">Loading...</div>
      ) : transactions.length === 0 ? (
        <div className="empty-state">No pending transactions</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Product</th>
              <th>Customer</th>
              <th>Quantity</th>
              <th>Amount</th>
              <th>Payment</th>
              <th>Created By</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((t) => (
              <tr key={t.id}>
                <td>{t.id}</td>
                <td>{t.product_name}</td>
                <td>{t.customer_name || 'Cash Customer'}</td>
                <td>{t.quantity.toFixed(2)} L</td>
                <td>${t.total_amount.toFixed(2)}</td>
                <td>{t.payment_type}</td>
                <td>{t.creator_name}</td>
                <td>{new Date(t.transaction_date).toLocaleString()}</td>
                <td>
                  <button onClick={() => handleConfirm(t.id)} className="btn-small btn-success">
                    Confirm
                  </button>
                  <button onClick={() => handleReject(t.id)} className="btn-small btn-danger">
                    Reject
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
