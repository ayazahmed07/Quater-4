'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiAuth, type LoginRequest } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data: LoginRequest = { username, password };
      const response = await apiAuth.login(data);

      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      router.push('/');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail ||
                          err.response?.data?.message ||
                          err.message ||
                          'Login failed. Please check your credentials.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Lubricant Inventory</h1>
        <p style={styles.subtitle}>Fuel Pump Management System</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.field}>
            <label style={styles.label}>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
              style={styles.input}
              placeholder="Enter your username"
            />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={styles.input}
              placeholder="Enter your password"
            />
          </div>

          {error && (
            <div style={styles.error}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={loading ? styles.buttonDisabled : styles.button}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={styles.footer}>
          <p style={styles.footerText}>Default Accounts:</p>
          <div style={styles.accountList}>
            <div style={styles.account}>admin / admin123</div>
            
          </div>
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
    padding: '20px',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    padding: '40px',
    width: '100%',
    maxWidth: '400px',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '8px',
    textAlign: 'center' as const,
  },
  subtitle: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '32px',
    textAlign: 'center' as const,
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
  },
  field: {
    marginBottom: '16px',
  },
  label: {
    display: 'block',
    fontSize: '14px',
    fontWeight: '500',
    color: '#333',
    marginBottom: '6px',
  },
  input: {
    width: '100%',
    padding: '10px 12px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    boxSizing: 'border-box' as const,
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  error: {
    backgroundColor: '#fee',
    color: '#c33',
    padding: '10px 12px',
    borderRadius: '4px',
    fontSize: '13px',
    marginBottom: '16px',
    border: '1px solid #fcc',
  },
  button: {
    width: '100%',
    padding: '12px',
    fontSize: '14px',
    fontWeight: '500',
    color: 'white',
    backgroundColor: '#2563eb',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    marginTop: '8px',
    transition: 'background-color 0.2s',
  },
  buttonDisabled: {
    width: '100%',
    padding: '12px',
    fontSize: '14px',
    fontWeight: '500',
    color: 'white',
    backgroundColor: '#93c5fd',
    border: 'none',
    borderRadius: '4px',
    cursor: 'not-allowed',
    marginTop: '8px',
  },
  footer: {
    marginTop: '24px',
    paddingTop: '20px',
    borderTop: '1px solid #e5e5e5',
  },
  footerText: {
    fontSize: '12px',
    fontWeight: '500',
    color: '#666',
    marginBottom: '8px',
  },
  accountList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '4px',
  },
  account: {
    fontSize: '12px',
    color: '#666',
    backgroundColor: '#f9f9f9',
    padding: '6px 10px',
    borderRadius: '4px',
  },
};
