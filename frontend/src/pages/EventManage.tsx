import React, { useEffect, useState } from 'react';
import { Plus, Edit2, Trash2 } from 'lucide-react';
import api from '../services/api';

export default function EventManage() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editItem, setEditItem] = useState<any>(null);
  const [form, setForm] = useState({ name: '', is_required: false, allow_sports_talent: false });

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const res: any = await api.get('/api/admin/events');
      if (res.code === 200) setEvents(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (item: any = null) => {
    if (item) {
      setEditItem(item);
      setForm({
        name: item.name,
        is_required: item.is_required || false,
        allow_sports_talent: item.allow_sports_talent || false
      });
    } else {
      setEditItem(null);
      setForm({ name: '', is_required: false, allow_sports_talent: false });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editItem) {
        await api.put(`/api/admin/events/${editItem._id}`, form);
      } else {
        await api.post('/api/admin/events', form);
      }
      handleCloseModal();
      fetchEvents();
    } catch (e) {
      console.error(e);
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除这个赛事项目吗？此操作不可恢复。')) return;
    try {
      await api.delete(`/api/admin/events/${id}`);
      fetchEvents();
    } catch (e) {
      console.error(e);
      alert('删除失败');
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 className="text-2xl font-bold mb-1">赛事项目管理</h2>
          <p className="text-sm text-muted">编辑比赛项目、必考选项和特长生规则</p>
        </div>
        <button className="btn btn-primary" onClick={() => handleOpenModal()}>
          <Plus size={16} /> 新增项目
        </button>
      </div>

      <div className="glass-panel table-container">
        {loading ? (
          <div className="p-6 text-center text-muted">加载赛事项目中...</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>项目名称</th>
                <th>是否必考</th>
                <th>是否允许申报体育特长生</th>
                <th>更新时间</th>
                <th style={{ textAlign: 'right' }}>操作</th>
              </tr>
            </thead>
            <tbody>
              {events.map((item) => (
                <tr key={item._id}>
                  <td className="font-medium">{item.name}</td>
                  <td>
                    {item.is_required ? (
                      <span style={{ color: 'var(--accent)', fontWeight: 600, fontSize: '0.75rem' }}>必考科目</span>
                    ) : (
                      <span className="text-xs text-muted">选考</span>
                    )}
                  </td>
                  <td>
                    {item.allow_sports_talent ? (
                      <span style={{ color: 'var(--primary)', fontWeight: 600, fontSize: '0.75rem' }}>支持 (特)</span>
                    ) : (
                      <span className="text-xs text-muted">不支持</span>
                    )}
                  </td>
                  <td className="text-sm text-muted">
                    {new Date(item.update_time).toLocaleDateString()}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                      <button className="btn btn-secondary" onClick={() => handleOpenModal(item)}>
                        <Edit2 size={14} />
                      </button>
                      <button className="btn btn-danger" onClick={() => handleDelete(item._id)}>
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {events.length === 0 && (
                <tr><td colSpan={5} className="text-center p-6 text-muted">暂无赛事项目</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {isModalOpen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
          backgroundColor: 'rgba(15, 23, 42, 0.8)',
          backdropFilter: 'blur(4px)',
          zIndex: 50,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div className="glass-panel animate-fade-in" style={{ width: '400px', backgroundColor: 'var(--bg-secondary)', padding: '2rem' }}>
            <h3 className="text-xl font-bold mb-4">{editItem ? '编辑项目' : '新增项目'}</h3>
            <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label className="text-sm text-muted mb-2 block">项目名称</label>
                <input 
                  type="text" className="input" 
                  value={form.name} onChange={e => setForm({...form, name: e.target.value})} 
                  placeholder="如：小学组50米" required 
                />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input 
                  type="checkbox" id="req"
                  checked={form.is_required} onChange={e => setForm({...form, is_required: e.target.checked})} 
                />
                <label htmlFor="req" className="text-sm">设为必考科目 (用户必须选择才能报名)</label>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input 
                  type="checkbox" id="sports"
                  checked={form.allow_sports_talent} onChange={e => setForm({...form, allow_sports_talent: e.target.checked})} 
                />
                <label htmlFor="sports" className="text-sm">允许报考者勾选「体育特长生」</label>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={handleCloseModal}>取消</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? '保存中...' : '提交保存'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
