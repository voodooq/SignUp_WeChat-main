import React, { useEffect, useState } from 'react';
import { Plus, Edit2, Trash2 } from 'lucide-react';
import api from '../services/api';

export default function SchoolManage() {
  const [schools, setSchools] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editItem, setEditItem] = useState<any>(null);
  const [form, setForm] = useState({ name: '' });

  useEffect(() => {
    fetchSchools();
  }, []);

  const fetchSchools = async () => {
    setLoading(true);
    try {
      const res: any = await api.get('/api/admin/schools');
      if (res.code === 200) setSchools(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (item: any = null) => {
    if (item) {
      setEditItem(item);
      setForm({ name: item.name });
    } else {
      setEditItem(null);
      setForm({ name: '' });
    }
    setIsModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editItem) {
        await api.put(`/api/admin/schools/${editItem._id}`, form);
      } else {
        await api.post('/api/admin/schools', form);
      }
      setIsModalOpen(false);
      fetchSchools();
    } catch (e) {
      console.error(e);
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除这个学校吗？')) return;
    try {
      await api.delete(`/api/admin/schools/${id}`);
      fetchSchools();
    } catch (e) {
      console.error(e);
      alert('删除失败');
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 className="text-2xl font-bold mb-1">报名学校大全库</h2>
          <p className="text-sm text-muted">编辑小程序端报名时下拉可选择的学校或结构</p>
        </div>
        <button className="btn btn-primary" onClick={() => handleOpenModal()}>
          <Plus size={16} /> 新增学校
        </button>
      </div>

      <div className="glass-panel table-container">
        {loading ? (
          <div className="p-6 text-center text-muted">加载数据中...</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>学校 / 机构名称</th>
                <th>创建时间</th>
                <th style={{ textAlign: 'right' }}>操作</th>
              </tr>
            </thead>
            <tbody>
              {schools.map((item) => (
                <tr key={item._id}>
                  <td className="font-medium text-primary">{item.name}</td>
                  <td className="text-sm text-muted">
                    {new Date(item.create_time).toLocaleDateString()}
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
              {schools.length === 0 && (
                <tr><td colSpan={3} className="text-center p-6 text-muted">暂无学校/机构记录数据</td></tr>
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
            <h3 className="text-xl font-bold mb-4">{editItem ? '编辑名称' : '新增分支学校或机构'}</h3>
            <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label className="text-sm text-muted mb-2 block">名称主体</label>
                <input 
                  type="text" className="input" 
                  value={form.name} onChange={e => setForm({...form, name: e.target.value})} 
                  placeholder="如：第一实验小学" required 
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>取消</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? '同步中...' : '确认发布'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
