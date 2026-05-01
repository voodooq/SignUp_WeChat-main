import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KeyRound, User } from 'lucide-react';
import api from '../services/api';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Create FormData as FastAPI OAuth2PasswordRequestForm expects form data
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const res: any = await api.post('/api/admin/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      if (res.code === 200 && res.data && res.data.access_token) {
        localStorage.setItem('admin_token', res.data.access_token);
        navigate('/dashboard', { replace: true });
      } else {
        setError(res.message || '登录失败，账号或密码错误');
      }
    } catch (err: any) {
      setError(err.message || err.detail || '系统错误，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem',
      background: 'radial-gradient(circle at top right, var(--bg-tertiary) 0%, var(--bg-primary) 100%)'
    }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '400px', padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ 
            width: '64px', height: '64px', 
            borderRadius: '16px', 
            backgroundColor: 'rgba(59, 130, 246, 0.1)', 
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 1.5rem',
            border: '1px solid rgba(59, 130, 246, 0.2)'
          }}>
            <KeyRound size={32} color="var(--primary)" />
          </div>
          <h1 className="text-2xl font-bold mb-2">系统管理中心</h1>
          <p className="text-sm text-muted">请输入管理员账号和密码进入控制台</p>
        </div>

        {error && (
          <div className="animate-fade-in" style={{
            padding: '1rem',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--danger)',
            fontSize: '0.875rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <label className="text-sm font-medium text-muted mb-2 block">管理员账号</label>
            <div style={{ position: 'relative' }}>
              <div style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}>
                <User size={18} />
              </div>
              <input
                type="text"
                className="input"
                style={{ paddingLeft: '2.75rem' }}
                placeholder="请输入 admin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-muted mb-2 block">管理密码</label>
            <div style={{ position: 'relative' }}>
              <div style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}>
                <KeyRound size={18} />
              </div>
              <input
                type="password"
                className="input"
                style={{ paddingLeft: '2.75rem' }}
                placeholder="请输入密码"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.875rem', marginTop: '0.5rem', fontSize: '1rem' }}
            disabled={loading}
          >
            {loading ? '正在验证...' : '登 录'}
          </button>
        </form>
      </div>
    </div>
  );
}
