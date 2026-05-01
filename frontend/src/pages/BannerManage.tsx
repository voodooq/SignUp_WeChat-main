import React, { useEffect, useState } from 'react';
import { Plus, Trash2, Image as ImageIcon, Upload, Loader2 } from 'lucide-react';
import api from '../services/api';

export default function BannerManage() {
  const [banners, setBanners] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({ image_url: '', position: 'home', order: 0, link: '' });
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchBanners();
  }, []);

  const fetchBanners = async () => {
    setLoading(true);
    try {
      const res: any = await api.get('/api/admin/banners');
      if (res.code === 200) setBanners(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = () => {
    setForm({ image_url: '', position: 'home', order: 0, link: '' });
    setIsModalOpen(true);
  };

  const handleUpload = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件');
      return;
    }
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res: any = await api.post('/api/upload', formData);
      if (res.code === 200) {
        setForm(prev => ({ ...prev, image_url: res.data.url }));
      }
    } catch (e) {
      alert('上传失败');
    } finally {
      setUploading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleUpload(file);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post('/api/admin/banners', form);
      setIsModalOpen(false);
      fetchBanners();
    } catch (e) {
      console.error(e);
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除这幅轮播图吗？')) return;
    try {
      await api.delete(`/api/admin/banners/${id}`);
      fetchBanners();
    } catch (e) {
      console.error(e);
      alert('删除失败');
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 className="text-2xl font-bold mb-1">精选轮播图管控</h2>
          <p className="text-sm text-muted">编辑小程序端首页吸顶横幅轮播图推荐</p>
        </div>
        <button className="btn btn-primary" onClick={handleOpenModal}>
          <Plus size={16} /> 添加视图
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {loading ? (
          <div className="text-muted col-span-full">刷新轮播媒体阵列中...</div>
        ) : banners.length === 0 ? (
          <div className="text-muted col-span-full">云端没有轮播图信息。</div>
        ) : (
          banners.map((item) => (
            <div key={item._id} className="glass-panel" style={{ overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
              <div style={{ position: 'relative', height: '160px', backgroundColor: 'var(--bg-tertiary)' }}>
                {item.image_url ? (
                  <img src={item.image_url} alt="banner" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                    <ImageIcon size={32} opacity={0.5} />
                  </div>
                )}
                <div style={{ position: 'absolute', top: '0.5rem', right: '0.5rem' }}>
                  <button onClick={() => handleDelete(item._id)} style={{ backgroundColor: 'rgba(239, 68, 68, 0.9)', color: 'white', border: 'none', borderRadius: '4px', width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
              <div style={{ padding: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span className="text-xs font-medium" style={{ color: 'var(--primary)', backgroundColor: 'rgba(59, 130, 246, 0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                    排序权重: {item.order}
                  </span>
                  <span className="text-xs text-muted">位置: {item.position}</span>
                </div>
                {item.link ? (
                  <a href={item.link} target="_blank" rel="noreferrer" className="text-sm" style={{ color: 'var(--primary)', textDecoration: 'none', wordBreak: 'break-all' }}>{item.link}</a>
                ) : (
                  <span className="text-sm text-muted">无跳转链接映射</span>
                )}
              </div>
            </div>
          ))
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
          <div className="glass-panel animate-fade-in" style={{ width: '500px', backgroundColor: 'var(--bg-secondary)', padding: '2rem' }}>
            <h3 className="text-xl font-bold mb-4">加载媒体轮播帧</h3>
            <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label className="text-sm text-muted mb-2 block">图片媒体文件</label>
                <div 
                  onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={onDrop}
                  onClick={() => document.getElementById('banner-upload')?.click()}
                  className={`
                    w-full h-48 rounded-xl border-2 border-dashed transition-all flex flex-col items-center justify-center cursor-pointer overflow-hidden
                    ${isDragging ? 'border-primary bg-primary/5 scale-[1.02]' : 'border-gray-200 bg-gray-50 hover:bg-gray-100'}
                    ${form.image_url ? 'border-none' : ''}
                  `}
                >
                  {uploading ? (
                    <div className="flex flex-col items-center animate-pulse">
                      <Loader2 className="animate-spin text-primary mb-2" size={32} />
                      <span className="text-xs text-muted">正在上传至服务器...</span>
                    </div>
                  ) : form.image_url ? (
                    <img src={form.image_url} className="w-full h-full object-cover" alt="预览" />
                  ) : (
                    <>
                      <Upload className={`${isDragging ? 'text-primary animate-bounce' : 'text-gray-300'} mb-2`} size={32} />
                      <span className="text-xs text-muted">点击或拖拽图片到这里直传</span>
                    </>
                  )}
                  <input id="banner-upload" type="file" className="hidden" accept="image/*" onChange={e => {
                    const file = e.target.files?.[0];
                    if (file) handleUpload(file);
                  }} />
                </div>
              </div>
              <div>
                <label className="text-sm text-muted mb-2 block">点击关联跳转外链 (可选)</label>
                <input 
                  type="text" className="input" 
                  value={form.link} onChange={e => setForm({...form, link: e.target.value})} 
                  placeholder="用户在小程序点击时尝试打开的网页" 
                />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label className="text-sm text-muted mb-2 block">排序阶层数字</label>
                  <input 
                    type="number" className="input" 
                    value={form.order} onChange={e => setForm({...form, order: Number(e.target.value)})} 
                    required 
                  />
                  <span className="text-xs text-muted">数值越大排越前面</span>
                </div>
                <div>
                  <label className="text-sm text-muted mb-2 block">所属模块</label>
                  <select 
                    className="input" 
                    value={form.position} onChange={e => setForm({...form, position: e.target.value})} 
                  >
                    <option value="home">小程序首页顶栏</option>
                  </select>
                </div>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>放弃设置</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? '传输参数...' : '保存写入主库'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
