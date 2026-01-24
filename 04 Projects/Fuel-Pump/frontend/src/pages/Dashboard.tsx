import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Role } from '../types';

export const Dashboard: React.FC = () => {
  const { user, hasRole } = useAuth();

  return (
    <div className="dashboard">
      <h2>Welcome, {user?.email}</h2>
      <div className="dashboard-info">
        <p>Role: <strong>{user?.role}</strong></p>
        <p>Status: <strong>{user?.is_active ? 'Active' : 'Inactive'}</strong></p>
      </div>

      {hasRole([Role.ADMIN]) && (
        <div className="dashboard-cards">
          <div className="card">
            <h3>Users Management</h3>
            <p>Manage system users and their roles</p>
            <a href="/admin/users" className="btn-card">Go to Users</a>
          </div>

          <div className="card">
            <h3>Customers</h3>
            <p>Manage customer accounts</p>
            <a href="/admin/customers" className="btn-card">Go to Customers</a>
          </div>

          <div className="card">
            <h3>Products</h3>
            <p>Manage fuel products and prices</p>
            <a href="/admin/products" className="btn-card">Go to Products</a>
          </div>

          <div className="card">
            <h3>Transactions</h3>
            <p>Review and approve transactions</p>
            <a href="/admin/transactions" className="btn-card">Go to Transactions</a>
          </div>

          <div className="card">
            <h3>Invoices</h3>
            <p>Manage customer invoices</p>
            <a href="/admin/invoices" className="btn-card">Go to Invoices</a>
          </div>
        </div>
      )}

      {hasRole([Role.CASHIER]) && (
        <div className="dashboard-cards">
          <div className="card">
            <h3>New Transaction</h3>
            <p>Create a new fueling transaction</p>
            <a href="/cashier/new-transaction" className="btn-card">Create Transaction</a>
          </div>

          <div className="card">
            <h3>Meter Readings</h3>
            <p>Manage pump meter readings</p>
            <a href="/cashier/meter-readings" className="btn-card">Manage Meters</a>
          </div>
        </div>
      )}

      {hasRole([Role.CUSTOMER]) && (
        <div className="dashboard-cards">
          <div className="card">
            <h3>My Profile</h3>
            <p>View and update your profile</p>
            <a href="/customer/profile" className="btn-card">View Profile</a>
          </div>

          <div className="card">
            <h3>Statements</h3>
            <p>View your transaction history</p>
            <a href="/customer/statements" className="btn-card">View Statements</a>
          </div>

          <div className="card">
            <h3>My Invoices</h3>
            <p>View your invoices</p>
            <a href="/customer/invoices" className="btn-card">View Invoices</a>
          </div>
        </div>
      )}
    </div>
  );
};
