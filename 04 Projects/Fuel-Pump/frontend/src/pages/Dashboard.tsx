import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Role } from '../types';

export const Dashboard: React.FC = () => {
  const { user, hasRole } = useAuth();

  return (
    <div className="page">
      <div className="page-header">
        <h2>Welcome, {user?.email}</h2>
      </div>

      <div className="dashboard-info">
        <p>Role: <strong>{user?.role}</strong></p>
        <p>Status: <strong>{user?.is_active ? 'Active' : 'Inactive'}</strong></p>
      </div>

      {hasRole([Role.ADMIN]) && (
        <>
          <h3>Admin Reports & Management</h3>
          <div className="dashboard-cards">
            <div className="card">
              <h3>👥 Users Management</h3>
              <p>Manage system users and their roles</p>
              <Link to="/admin/users" className="btn-card">Go to Users</Link>
            </div>

            <div className="card">
              <h3>🙋 Customers</h3>
              <p>Manage customer accounts and credit limits</p>
              <Link to="/admin/customers" className="btn-card">Go to Customers</Link>
            </div>

            <div className="card">
              <h3>⛽ Products</h3>
              <p>Manage fuel products and pricing</p>
              <Link to="/admin/products" className="btn-card">Go to Products</Link>
            </div>

            <div className="card">
              <h3>💳 Pending Transactions</h3>
              <p>Review and approve credit transactions</p>
              <Link to="/admin/transactions" className="btn-card">Go to Transactions</Link>
            </div>

            <div className="card">
              <h3>📄 Invoices & Bills</h3>
              <p>Generate and manage customer invoices</p>
              <Link to="/admin/invoices" className="btn-card">Go to Invoices</Link>
            </div>
          </div>
        </>
      )}

      {hasRole([Role.CASHIER, Role.ADMIN]) && (
        <>
          {hasRole([Role.ADMIN]) && <h3>Cashier Operations</h3>}
          <div className="dashboard-cards">
            <div className="card">
              <h3>⛽ New Transaction</h3>
              <p>Create a new fueling transaction</p>
              <Link to="/cashier/new-transaction" className="btn-card">Create Transaction</Link>
            </div>

            <div className="card">
              <h3>📊 Meter Readings</h3>
              <p>Manage pump meter readings</p>
              <Link to="/cashier/meter-readings" className="btn-card">Manage Meters</Link>
            </div>
          </div>
        </>
      )}

      {hasRole([Role.CUSTOMER]) && (
        <>
          <h3>My Account</h3>
          <div className="dashboard-cards">
            <div className="card">
              <h3>👤 My Profile</h3>
              <p>View and update your profile</p>
              <Link to="/customer/profile" className="btn-card">View Profile</Link>
            </div>

            <div className="card">
              <h3>📜 Statements</h3>
              <p>View your transaction history</p>
              <Link to="/customer/statements" className="btn-card">View Statements</Link>
            </div>

            <div className="card">
              <h3>🧾 My Invoices</h3>
              <p>View and pay your invoices</p>
              <Link to="/customer/invoices" className="btn-card">View Invoices</Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
