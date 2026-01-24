import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { AuthLayout } from '../layout/Layout';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Login form submitted with email:', email);
    setError('');
    setIsLoading(true);

    try {
      console.log('Calling login API...');
      await login({ email, password });
      console.log('Login successful, navigating to:', from);
      navigate(from, { replace: true });
    } catch (err: any) {
      console.error('Login failed - Full error:', err);
      console.error('Error response:', err.response);
      console.error('Error request:', err.request);
      console.error('Error message:', err.message);
      console.error('Error code:', err.code);

      let errorMessage = 'Login failed. Please check your credentials.';
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      } else if (err.code === 'ERR_NETWORK') {
        errorMessage = 'Network error: Unable to connect to the server. Please check if the backend is running.';
      } else if (err.code === 'ECONNREFUSED') {
        errorMessage = 'Connection refused: The server is not accessible.';
      }
      console.error('Final error message:', errorMessage);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout>
      <form onSubmit={handleSubmit} className="login-form">
        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
        </div>

        <button type="submit" disabled={isLoading} className="btn-primary">
          {isLoading ? 'Signing in...' : 'Sign In'}
        </button>

        <div className="login-info">
          <p>Demo accounts:</p>
          <ul>
            <li>Admin: admin@test.com / admin123</li>
            <li>Cashier: cashier@test.com / cashier123</li>
            <li>Customer: customer@test.com / customer123</li>
          </ul>
        </div>
      </form>
    </AuthLayout>
  );
};
