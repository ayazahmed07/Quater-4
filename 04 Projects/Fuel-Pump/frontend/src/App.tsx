import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './layout/Layout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Users } from './pages/admin/Users';
import { Customers } from './pages/admin/Customers';
import { Products } from './pages/admin/Products';
import { Transactions } from './pages/admin/Transactions';
import { Invoices } from './pages/admin/Invoices';
import { NewTransaction } from './pages/cashier/NewTransaction';
import { MeterReadings } from './pages/cashier/MeterReadings';
import { Profile } from './pages/customer/Profile';
import { Statements } from './pages/customer/Statements';
import { CustomerInvoices } from './pages/customer/CustomerInvoices';
import { Role } from './types';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />

            {/* Admin Routes */}
            <Route path="admin/users" element={<ProtectedRoute allowedRoles={[Role.ADMIN]}><Users /></ProtectedRoute>} />
            <Route path="admin/customers" element={<ProtectedRoute allowedRoles={[Role.ADMIN]}><Customers /></ProtectedRoute>} />
            <Route path="admin/products" element={<ProtectedRoute allowedRoles={[Role.ADMIN]}><Products /></ProtectedRoute>} />
            <Route path="admin/transactions" element={<ProtectedRoute allowedRoles={[Role.ADMIN]}><Transactions /></ProtectedRoute>} />
            <Route path="admin/invoices" element={<ProtectedRoute allowedRoles={[Role.ADMIN]}><Invoices /></ProtectedRoute>} />

            {/* Cashier Routes */}
            <Route path="cashier/new-transaction" element={<ProtectedRoute allowedRoles={[Role.CASHIER, Role.ADMIN]}><NewTransaction /></ProtectedRoute>} />
            <Route path="cashier/meter-readings" element={<ProtectedRoute allowedRoles={[Role.CASHIER, Role.ADMIN]}><MeterReadings /></ProtectedRoute>} />

            {/* Customer Routes */}
            <Route path="customer/profile" element={<ProtectedRoute allowedRoles={[Role.CUSTOMER]}><Profile /></ProtectedRoute>} />
            <Route path="customer/statements" element={<ProtectedRoute allowedRoles={[Role.CUSTOMER]}><Statements /></ProtectedRoute>} />
            <Route path="customer/invoices" element={<ProtectedRoute allowedRoles={[Role.CUSTOMER]}><CustomerInvoices /></ProtectedRoute>} />
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
