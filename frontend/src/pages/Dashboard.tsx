import { useEffect, useState } from 'react';
import { Users, CreditCard, Ticket, AlertCircle } from 'lucide-react';
import api from '../services/api';

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>({});
  const [error, setError] = useState('');
  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const res: any = await api.get('/api/admin/metrics');
      if (res.code === 200) {
        setStats(res.data);
      } else {
        setError(res.message || '加载统计数据失败');
      }
    } catch (err: any) {
      setError('网络不佳，请重试');
    } finally {
      setLoading(false);
    }
  };

  const cards = [
    { title: '总报名人数', value: stats.total || 0, icon: <Users size={24} />, color: 'var(--primary)', bg: 'rgba(59, 130, 246, 0.1)' },
    { title: '已缴费人数', value: stats.paid || 0, icon: <CreditCard size={24} />, color: 'var(--accent)', bg: 'rgba(16, 185, 129, 0.1)' },
    { title: '未缴费人数', value: stats.unpaid || 0, icon: <AlertCircle size={24} />, color: 'var(--warning)', bg: 'rgba(245, 158, 11, 0.1)' },
    { title: '管理员后台录入', value: stats.adminFree || 0, icon: <Ticket size={24} />, color: '#a855f7', bg: 'rgba(168, 85, 247, 0.1)' },
  ];

  if (loading) {
    return <div className="text-muted">加载看板数据中...</div>;
  }

  if (error) {
    return <div className="text-danger">{error}</div>;
  }

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '2rem' }}>
        <h2 className="text-2xl font-bold mb-1">数据概览看板</h2>
        <p className="text-sm text-muted">实时查看赛事报名情况统计</p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        {cards.map((card, idx) => (
          <div key={idx} className="glass-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              width: '48px', height: '48px',
              borderRadius: '12px',
              backgroundColor: card.bg,
              color: card.color,
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              {card.icon}
            </div>
            <div>
              <p className="text-sm font-medium text-muted mb-1">{card.title}</p>
              <h3 className="text-3xl font-bold" style={{ color: card.color }}>{card.value}</h3>
            </div>
          </div>
        ))}
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 className="text-lg font-bold mb-4">项目报名明细分布</h3>
        {stats.eventStats && stats.eventStats.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {stats.eventStats.map((item: any, idx: number) => {
              const maxCount = Math.max(...stats.eventStats.map((e: any) => e.count), 1);
              const percentage = (item.count / maxCount) * 100;
              return (
                <div key={idx}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                    <span className="text-sm font-medium">{item.event_name}</span>
                    <span className="text-sm" style={{ color: 'var(--primary)' }}>{item.count} 人</span>
                  </div>
                  <div style={{ width: '100%', height: '8px', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{
                      width: `${percentage}%`,
                      height: '100%',
                      backgroundColor: 'var(--primary)',
                      borderRadius: '4px',
                      transition: 'width 1s ease-out'
                    }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-sm text-muted py-4 text-center">暂无项目数据</div>
        )}
      </div>
    </div>
  );
}
