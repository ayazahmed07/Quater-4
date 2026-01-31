'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';

interface NavbarProps {
  onMobileMenuToggle: () => void;
  isMobileMenuOpen: boolean;
}

export function Navbar({ onMobileMenuToggle, isMobileMenuOpen }: NavbarProps) {
  const router = useRouter();
  const [user, setUser] = useState<any>({});
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleSignOut = () => {
    localStorage.clear();
    router.push('/login');
  };

  // Don't render user-specific content until mounted on client
  if (!mounted) {
    return (
      <nav style={navbarStyles.nav}>
        <div style={navbarStyles.container}>
          <div style={navbarStyles.left}>
            <button
              onClick={onMobileMenuToggle}
              style={navbarStyles.menuBtn}
              className="lg:hidden"
            >
              {isMobileMenuOpen ? '✕' : '☰'}
            </button>
            <div style={navbarStyles.pageTitle}>
              Lubricant Inventory Management
            </div>
          </div>
          <div style={navbarStyles.right}>
            <div style={navbarStyles.userInfo}>
              <span style={navbarStyles.userName}>Loading...</span>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav style={navbarStyles.nav}>
      <div style={navbarStyles.container}>
        {/* Left section */}
        <div style={navbarStyles.left}>
          <button
            onClick={onMobileMenuToggle}
            style={navbarStyles.menuBtn}
            className="lg:hidden"
          >
            {isMobileMenuOpen ? '✕' : '☰'}
          </button>
          <div style={navbarStyles.pageTitle}>
            Lubricant Inventory Management
          </div>
        </div>

        {/* Right section */}
        <div style={navbarStyles.right}>
          <div style={navbarStyles.userInfo}>
            <span style={navbarStyles.userName}>{user.full_name || 'User'}</span>
            <span style={navbarStyles.userRole}>{user.role || 'Guest'}</span>
          </div>
          <button
            onClick={handleSignOut}
            style={navbarStyles.signOutBtn}
          >
            Sign Out
          </button>
        </div>
      </div>
    </nav>
  );
}

const navbarStyles: Record<string, React.CSSProperties> = {
  nav: {
    backgroundColor: 'white',
    borderBottom: '1px solid #e2e8f0',
    padding: '12px 20px',
    position: 'sticky',
    top: 0,
    zIndex: 30,
  },
  container: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  left: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  menuBtn: {
    background: 'none',
    border: '1px solid #e2e8f0',
    borderRadius: '4px',
    padding: '6px 10px',
    cursor: 'pointer',
    fontSize: '18px',
  },
  pageTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1e293b',
  },
  right: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  userInfo: {
    textAlign: 'right' as const,
  },
  userName: {
    display: 'block',
    fontSize: '14px',
    fontWeight: '500',
    color: '#1e293b',
  },
  userRole: {
    display: 'block',
    fontSize: '12px',
    color: '#64748b',
  },
  signOutBtn: {
    padding: '8px 16px',
    backgroundColor: '#2563eb',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
  },
};
