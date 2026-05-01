import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, CalendarDays, Users, Settings, LogOut, MapPin, Image, FileText, Calculator } from 'lucide-react';

export default function AdminLayout() {
  const location = useLocation();

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    window.location.href = '/login';
  };

  const navItems = [
    { name: '数据看板', path: '/dashboard', icon: <LayoutDashboard size={20} /> },
    { name: '赛事中心', path: '/competitions', icon: <CalendarDays size={20} /> },
    { name: '项目/科目管理', path: '/events', icon: <FileText size={20} /> },
    { name: '学校机构库', path: '/schools', icon: <MapPin size={20} /> },
    { name: '人员报名管理', path: '/registrations', icon: <Users size={20} /> },
    { name: '批量成绩中心', path: '/scores', icon: <Calculator size={20} /> },
    { name: '轮播推荐图', path: '/banners', icon: <Image size={20} /> },
    { name: '图文须知', path: '/notices', icon: <FileText size={20} /> },
    { name: '场馆及线路', path: '/gyms', icon: <MapPin size={20} /> },
    { name: '系统高级设置', path: '/settings', icon: <Settings size={20} /> },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside
        style={{
          width: '260px',
          backgroundColor: 'var(--bg-secondary)',
          borderRight: '1px solid var(--border)',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div style={{ padding: '2rem 1.5rem', borderBottom: '1px solid var(--border)' }}>
          <h1 className="text-xl font-bold" style={{ color: 'var(--primary)' }}>
            赛事报名系统
          </h1>
          <p className="text-xs text-muted" style={{ marginTop: '0.25rem' }}>
            管理端 Dashboard
          </p>
        </div>

        <nav style={{ flex: 1, padding: '1.5rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {navItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.75rem 1rem',
                  borderRadius: 'var(--radius-md)',
                  textDecoration: 'none',
                  color: isActive ? '#ffffff' : 'var(--text-secondary)',
                  backgroundColor: isActive ? 'var(--primary)' : 'transparent',
                  transition: 'all var(--transition-fast)',
                }}
              >
                {item.icon}
                <span className="font-medium text-sm">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div style={{ padding: '1.5rem 1rem', borderTop: '1px solid var(--border)' }}>
          <button
            onClick={handleLogout}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              width: '100%',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-md)',
              border: 'none',
              backgroundColor: 'transparent',
              color: 'var(--danger)',
              cursor: 'pointer',
              transition: 'background-color var(--transition-fast)',
            }}
            onMouseOver={(e) => (e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.1)')}
            onMouseOut={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
          >
            <LogOut size={20} />
            <span className="font-medium text-sm">退出登录</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <header
          style={{
            height: '64px',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            padding: '0 2rem',
            backgroundColor: 'rgba(30, 41, 59, 0.5)',
            backdropFilter: 'blur(12px)',
          }}
        >
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span className="text-sm font-bold text-white">A</span>
            </div>
            <span className="text-sm font-medium">超级管理员</span>
          </div>
        </header>

        <div style={{ flex: 1, overflowY: 'auto', padding: '2rem' }}>
          <Outlet />
        </div>
      </main>
    </div>
  );
}
