'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
  isMobileOpen: boolean;
  onMobileClose: () => void;
}

const navigation = [
  { name: 'Dashboard', href: '/' },
  { name: 'Inventory', href: '/items' },
  { name: 'Stock In', href: '/purchases' },
  { name: 'Stock Out', href: '/sales' },
  { name: 'Physical Stock', href: '/physical-stock' },
  { name: 'Reports', href: '/reports' },
];

export function Sidebar({ isCollapsed, onToggle, isMobileOpen, onMobileClose }: SidebarProps) {
  const pathname = usePathname();

  const SidebarContent = () => (
    <div style={sidebarStyles.container}>
      <div style={sidebarStyles.header}>
        {!isCollapsed && <div style={sidebarStyles.title}>Lubricant Inventory</div>}
        <button
          onClick={onToggle}
          style={sidebarStyles.toggleBtn}
          className="hidden lg:block"
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>

      <nav style={sidebarStyles.nav}>
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              onClick={onMobileClose}
              style={isActive ? sidebarStyles.linkActive : sidebarStyles.link}
            >
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div style={sidebarStyles.footer}>
        <button
          onClick={() => {
            localStorage.clear();
            window.location.href = '/login';
          }}
          style={sidebarStyles.logoutBtn}
        >
          Sign Out
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile */}
      {isMobileOpen && (
        <>
          <div
            onClick={onMobileClose}
            style={{
              position: 'fixed',
              inset: 0,
              backgroundColor: 'rgba(0,0,0,0.5)',
              zIndex: 40,
            }}
            className="lg:hidden"
          />
          <div
            style={{
              position: 'fixed',
              left: 0,
              top: 0,
              height: '100vh',
              width: '250px',
              backgroundColor: '#1e293b',
              zIndex: 50,
            }}
            className="lg:hidden"
          >
            <SidebarContent />
          </div>
        </>
      )}

      {/* Desktop */}
      <aside
        style={{
          position: 'fixed',
          left: 0,
          top: 0,
          height: '100vh',
          width: isCollapsed ? '80px' : '250px',
          backgroundColor: '#1e293b',
          zIndex: 40,
          transition: 'width 0.2s',
        }}
        className="hidden lg:flex"
      >
        <SidebarContent />
      </aside>
    </>
  );
}

const sidebarStyles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    height: '100%',
  },
  header: {
    padding: '20px',
    borderBottom: '1px solid #334155',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  title: {
    color: 'white',
    fontSize: '16px',
    fontWeight: 'bold',
  },
  toggleBtn: {
    background: 'none',
    border: 'none',
    color: '#94a3b8',
    cursor: 'pointer',
    padding: '4px 8px',
    fontSize: '18px',
  },
  nav: {
    flex: 1,
    padding: '20px 12px',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '4px',
  },
  link: {
    display: 'block',
    padding: '10px 12px',
    color: '#94a3b8',
    textDecoration: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    transition: 'background-color 0.2s',
  },
  linkActive: {
    display: 'block',
    padding: '10px 12px',
    color: 'white',
    backgroundColor: '#2563eb',
    textDecoration: 'none',
    borderRadius: '4px',
    fontSize: '14px',
  },
  footer: {
    padding: '20px',
    borderTop: '1px solid #334155',
  },
  logoutBtn: {
    width: '100%',
    padding: '10px',
    backgroundColor: '#dc2626',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
};
