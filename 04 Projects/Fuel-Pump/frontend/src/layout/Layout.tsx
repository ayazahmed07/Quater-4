import React, { ReactNode } from 'react';
import { Link, useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Role } from '../types';

export const Layout: React.FC = () => {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="layout">
      <header className="header">
        <div className="header-left">
          <h1>Fuel Pump Management</h1>
          <span className="user-info">{user?.email} ({user?.role})</span>
        </div>
        <div className="header-right">
          <button onClick={handleLogout} className="btn-logout">
            Logout
          </button>
        </div>
      </header>

      <div className="main-container">
        <aside className="sidebar">
          <nav className="nav">
            <Link
              to="/dashboard"
              className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
            >
              Dashboard
            </Link>

            {hasRole([Role.ADMIN]) && (
              <>
                <Link
                  to="/admin/users"
                  className={`nav-link ${isActive('/admin/users') ? 'active' : ''}`}
                >
                  Users
                </Link>
                <Link
                  to="/admin/customers"
                  className={`nav-link ${isActive('/admin/customers') ? 'active' : ''}`}
                >
                  Customers
                </Link>
                <Link
                  to="/admin/products"
                  className={`nav-link ${isActive('/admin/products') ? 'active' : ''}`}
                >
                  Products
                </Link>
                <Link
                  to="/admin/transactions"
                  className={`nav-link ${isActive('/admin/transactions') ? 'active' : ''}`}
                >
                  Transactions
                </Link>
                <Link
                  to="/admin/invoices"
                  className={`nav-link ${isActive('/admin/invoices') ? 'active' : ''}`}
                >
                  Invoices
                </Link>
              </>
            )}

            {hasRole([Role.CASHIER, Role.ADMIN]) && (
              <>
                <Link
                  to="/cashier/new-transaction"
                  className={`nav-link ${isActive('/cashier/new-transaction') ? 'active' : ''}`}
                >
                  New Transaction
                </Link>
                <Link
                  to="/cashier/meter-readings"
                  className={`nav-link ${isActive('/cashier/meter-readings') ? 'active' : ''}`}
                >
                  Meter Readings
                </Link>
              </>
            )}

            {hasRole([Role.CUSTOMER]) && (
              <>
                <Link
                  to="/customer/profile"
                  className={`nav-link ${isActive('/customer/profile') ? 'active' : ''}`}
                >
                  My Profile
                </Link>
                <Link
                  to="/customer/statements"
                  className={`nav-link ${isActive('/customer/statements') ? 'active' : ''}`}
                >
                  Statements
                </Link>
                <Link
                  to="/customer/invoices"
                  className={`nav-link ${isActive('/customer/invoices') ? 'active' : ''}`}
                >
                  My Invoices
                </Link>
              </>
            )}
          </nav>
        </aside>

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

interface AuthLayoutProps {
  children: ReactNode;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className="auth-layout">
      <div className="auth-container">
        <div className="auth-header">
          <h1>Fuel Pump Management</h1>
          <p>Sign in to your account</p>
        </div>
        {children}
      </div>
    </div>
  );
};
