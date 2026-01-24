import React, { useState, useEffect } from 'react';
import { adminApi } from '../../api';
import { Customer, CustomerStatus } from '../../types';

export const Customers: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      setError(null);
      const data = await adminApi.getCustomers();
      setCustomers(data);
    } catch (error: any) {
      console.error('Failed to load customers:', error);
      setError(error.response?.data?.detail || 'Failed to load customers');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Customers Management</h2>
      </div>

      {error && <div className="error-message">{error}</div>}

      {isLoading ? (
        <div className="loading">Loading...</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Credit Limit</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {customers.map((customer) => (
              <tr key={customer.id}>
                <td>{customer.id}</td>
                <td>{customer.name}</td>
                <td>{customer.email || '-'}</td>
                <td>{customer.phone}</td>
                <td>Rs. ${Number(customer.credit_limit).toFixed(2)}</td>
                <td>{customer.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};
