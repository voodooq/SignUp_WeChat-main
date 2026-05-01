import React, { useEffect, useState } from 'react';
import { Save } from 'lucide-react';
import api from '../services/api';

export default function SettingsManage() {
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    event_title: '',
    event_location: '',
    event_date: '',
    registration_deadline: '',
    contact_name: '',
    contact_phone: ''
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const res: any = await api.get('/api/admin/settings');
      if (res.code === 200 && res.data) {
        const data = res.data;
        setForm({
          event_title: data.event_title?.value || '',
          event_location: data.event_location?.value || '',
          event_date: data.event_date?.value || '',
          registration_deadline: data.registration_deadline?.value || '',
          contact_name: data.contact_name?.value || '',
          contact_phone: data.contact_phone?.value || ''
        });
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put('/api/admin/settings', { settings: form });
      alert('系统设置已成功保存！');
    } catch (e) {
      console.error(e);
      alert('保存失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '2rem' }}>
        <h2 className="text-2xl font-bold mb-1">基本系统设置</h2>
        <p className="text-sm text-muted">管理展示在小程序端的基础赛事属性信息</p>
      </div>

      <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px' }}>
        {loading ? (
          <div className="text-muted text-center py-4">配置加载中...</div>
        ) : (
          <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label className="text-sm font-medium mb-2 block">整体赛事标题</label>
              <input 
                type="text" className="input" 
                value={form.event_title} onChange={e => setForm({...form, event_title: e.target.value})} 
                placeholder="例如：2026年XX杯少年拔河选拔赛" required 
              />
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label className="text-sm font-medium mb-2 block">比赛地点</label>
                <input 
                  type="text" className="input" 
                  value={form.event_location} onChange={e => setForm({...form, event_location: e.target.value})} 
                  placeholder="如：XX体育馆" required 
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">比赛时间（对外显示）</label>
                <input 
                  type="text" className="input" 
                  value={form.event_date} onChange={e => setForm({...form, event_date: e.target.value})} 
                  placeholder="如：4月19日 上午8:00" required 
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">报名截止时间 (倒计时使用)</label>
              <input 
                type="text" className="input" 
                value={form.registration_deadline} onChange={e => setForm({...form, registration_deadline: e.target.value})} 
                placeholder="严格格式 YYYY-MM-DD HH:mm:ss" required 
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label className="text-sm font-medium mb-2 block">对外联系人姓名</label>
                <input 
                  type="text" className="input" 
                  value={form.contact_name} onChange={e => setForm({...form, contact_name: e.target.value})} 
                  placeholder="姓名"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">联系电话</label>
                <input 
                  type="tel" className="input" 
                  value={form.contact_phone} onChange={e => setForm({...form, contact_phone: e.target.value})} 
                  placeholder="区号-电话 或 手机号"
                />
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem' }} disabled={saving}>
              <Save size={18} /> {saving ? '更新配置中...' : '保存更改'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
