import { useEffect, useState } from 'react';
import { Search, Info, Download } from 'lucide-react';
import api from '../services/api';


export default function RegistrationManage() {
  const [list, setList] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [keyword, setKeyword] = useState('');
  const [eventItem, setEventItem] = useState('');
  const [eventOptions, setEventOptions] = useState<any[]>([]);

  useEffect(() => {
    loadEventOptions();
    fetchData();
  }, []);

  const loadEventOptions = async () => {
    try {
      const res: any = await api.get('/api/admin/events');
      if (res.code === 200) {
        setEventOptions(res.data || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const res: any = await api.get('/api/admin/registrations', {
        params: { keyword, event_item: eventItem, limit: 50 }
      });
      if (res.code === 200 && res.data) {
        setList(res.data.list || []);
        setTotal(res.data.total || 0);
      } else {
        setList([]);
        setTotal(0);
      }
    } catch (e) {
      console.error('Fetch failed', e);
      setList([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: any) => {
    e.preventDefault();
    fetchData();
  };

  const paymentText = (status: string) => {
    const map: Record<string, string> = { paid: '已缴费', unpaid: '未缴费', admin_free: '免缴费' };
    return map[status] || status;
  };

  const paymentColor = (status: string) => {
    switch (status) {
      case 'paid': return 'var(--accent)';
      case 'unpaid': return 'var(--warning)';
      case 'admin_free': return '#a855f7';
      default: return 'var(--text-muted)';
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 className="text-2xl font-bold mb-1">报名与人员管理</h2>
          <p className="text-sm text-muted">管理所有参赛选手的报名信息和缴费状态</p>
        </div>
        <button className="btn btn-primary">
          <Download size={16} /> 导出人员数据
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
            <div style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}>
              <Search size={18} />
            </div>
            <input
              type="text"
              className="input"
              style={{ paddingLeft: '2.75rem' }}
              placeholder="准考证号 / 姓名 / 手机号 / 身份证号"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
            />
          </div>
          <div style={{ width: '200px' }}>
            <select
              className="input"
              value={eventItem}
              onChange={(e) => setEventItem(e.target.value)}
            >
              <option value="">全部赛事项目</option>
              {eventOptions.map((e, idx) => (
                <option key={idx} value={e.name}>{e.name}</option>
              ))}
            </select>
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            搜 索
          </button>
        </form>
      </div>

      <div className="glass-panel table-container">
        {loading ? (
          <div className="p-6 text-center text-muted">正在检索数据...</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>人员信息</th>
                <th>报名项目</th>
                <th>准考证号</th>
                <th>联系电话</th>
                <th>学校 / 机构</th>
                <th>缴费状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {list.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center" style={{ padding: '3rem 1rem' }}>
                    <div style={{ color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
                      <Info size={32} opacity={0.5} />
                      <span>未找到任何匹配的人员数据</span>
                    </div>
                  </td>
                </tr>
              ) : (
                list.map((item) => (
                  <tr key={item._id}>
                    <td>
                      <div className="font-semibold text-primary">{item.name}</div>
                      <div className="text-xs text-muted mt-1">{item.gender === 'male' ? '男' : '女'}</div>
                    </td>
                    <td className="font-medium text-sm">{item.event_name}</td>
                    <td className="font-mono text-sm">{item.ticket_no}</td>
                    <td className="text-sm">{item.phone}</td>
                    <td className="text-sm">{item.school || '-'}</td>
                    <td>
                      <span style={{
                        display: 'inline-flex',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        backgroundColor: `${paymentColor(item.payment_status)}20`,
                        color: paymentColor(item.payment_status)
                      }}>
                        {paymentText(item.payment_status)}
                      </span>
                    </td>
                    <td>
                      <button className="btn btn-secondary" style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}>
                        详情
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
        {list.length > 0 && (
          <div style={{ padding: '1rem', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="text-sm text-muted">共 {total} 条记录，当前显示前 50 条</span>
          </div>
        )}
      </div>
    </div>
  );
}
