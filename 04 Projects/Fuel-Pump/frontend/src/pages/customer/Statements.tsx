import React, { useState, useEffect } from 'react';
import { customerApi } from '../../api';
import { FuelingTransaction } from '../../types';

export const Statements: React.FC = () => {
  const [transactions, setTransactions] = useState<FuelingTransaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStatements();
  }, []);

  const loadStatements = async () => {
    try {
      const data = await customerApi.getStatements();
      setTransactions(data);
    } catch (error) {
      console.error('Failed to load statements:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>My Statements</h2>
      </div>

      {isLoading ? (
        <div className="loading">Loading...</div>
      ) : transactions.length === 0 ? (
        <div className="empty-state">No transactions found</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Product</th>
              <th>Quantity</th>
              <th>Unit Price</th>
              <th>Total</th>
              <th>Payment</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((t) => (
              <tr key={t.id}>
                <td>{new Date(t.transaction_date).toLocaleString()}</td>
                <td>{t.product_name}</td>
                <td>{Number(t.quantity).toFixed(2)} L</td>
                <td>Rs. ${Number(t.unit_price).toFixed(2)}</td>
                <td>Rs. ${Number(t.total_amount).toFixed(2)}</td>
                <td>{t.payment_type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
