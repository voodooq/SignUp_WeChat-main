import React, { useEffect, useState } from 'react';
import { Plus, Trash2, Image as ImageIcon, ArrowUp, ArrowDown, Upload, Loader2 } from 'lucide-react';
import api from '../services/api';

export default function NoticeImageManage() {
  const [images, setImages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({ image_url: '', order: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    setLoading(true);
    try {
      const res: any = await api.get('/api/admin/notice-images');
      if (res.code === 200) {
        setImages((res.data || []).sort((a: any, b: any) => b.order - a.order));
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = () => {
    setForm({ image_url: '', order: 0 });
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
      await api.post('/api/admin/notice-images', form);
      setIsModalOpen(false);
      fetchImages();
    } catch (e) {
      console.error(e);
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除参赛须知的这页长图吗？')) return;
    try {
      await api.delete(`/api/admin/notice-images/${id}`);
      fetchImages();
    } catch (e) {
      console.error(e);
      alert('删除失败');
    }
  };

  const handleReorder = async (id: string, direction: 'up' | 'down') => {
    const currentIndex = images.findIndex((img) => img._id === id);
    if (currentIndex === -1) return;
    if (direction === 'up' && currentIndex === 0) return;
    if (direction === 'down' && currentIndex === images.length - 1) return;

    const newImages = [...images];
    const swapIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    
    // Swap order
    const currentOrder = newImages[currentIndex].order;
    newImages[currentIndex].order = newImages[swapIndex].order;
    newImages[swapIndex].order = currentOrder;

    setImages(newImages.sort((a: any, b: any) => b.order - a.order));

    try {
      const orderedIds = newImages.map(img => img._id);
      await api.post('/api/admin/notice-images/reorder', { ordered_ids: orderedIds });
    } catch (e) {
      console.error('排序更新失败', e);
      fetchImages(); // revert on failure
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 className="text-2xl font-bold mb-1">参赛须知长图切片列表</h2>
          <p className="text-sm text-muted">用户报名前需要确认阅览的须知图文版块（支持多张组合）</p>
        </div>
        <button className="btn btn-primary" onClick={handleOpenModal}>
          <Plus size={16} /> 追加海报切片
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.5rem' }}>
        {loading ? (
          <div className="text-muted col-span-full">请求通知素材源中...</div>
        ) : images.length === 0 ? (
          <div className="text-muted col-span-full">还没有添加任何参赛须知图片。</div>
        ) : (
          images.map((item, idx) => (
            <div key={item._id} className="glass-panel" style={{ overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
              <div style={{ position: 'relative', height: '300px', backgroundColor: 'var(--bg-tertiary)' }}>
                {item.image_url ? (
                  <img src={item.image_url} alt="notice" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)' }}>
                    <ImageIcon size={32} opacity={0.5} />
                  </div>
                )}
                
                <div style={{ position: 'absolute', top: '0.5rem', right: '0.5rem', display: 'flex', gap: '0.25rem' }}>
                  <button onClick={() => handleDelete(item._id)} style={{ backgroundColor: 'rgba(239, 68, 68, 0.9)', color: 'white', border: 'none', borderRadius: '4px', width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                    <Trash2 size={14} />
                  </button>
                </div>
                
                <div style={{ position: 'absolute', bottom: '0.5rem', left: '50%', transform: 'translateX(-50%)', display: 'flex', gap: '0.5rem', backgroundColor: 'var(--bg-primary)', padding: '4px', borderRadius: '8px' }}>
                  <button onClick={() => handleReorder(item._id, 'up')} disabled={idx === 0} style={{ backgroundColor: idx === 0 ? 'transparent' : 'var(--bg-tertiary)', color: idx === 0 ? 'var(--text-muted)' : 'var(--primary)', border: 'none', borderRadius: '4px', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: idx === 0 ? 'not-allowed' : 'pointer' }}>
                    <ArrowUp size={16} />
                  </button>
                  <button onClick={() => handleReorder(item._id, 'down')} disabled={idx === images.length - 1} style={{ backgroundColor: idx === images.length - 1 ? 'transparent' : 'var(--bg-tertiary)', color: idx === images.length - 1 ? 'var(--text-muted)' : 'var(--primary)', border: 'none', borderRadius: '4px', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: idx === images.length - 1 ? 'not-allowed' : 'pointer' }}>
                    <ArrowDown size={16} />
                  </button>
                </div>
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
            <h3 className="text-xl font-bold mb-4">录入须知图片媒体</h3>
            <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label className="text-sm text-muted mb-2 block">图片媒体文件</label>
                <div 
                  onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                  onDragLeave={() => setIsDragging(false)}
                  onDrop={onDrop}
                  onClick={() => document.getElementById('notice-upload')?.click()}
                  className={`
                    w-full min-h-[300px] rounded-xl border-2 border-dashed transition-all flex flex-col items-center justify-center cursor-pointer overflow-hidden
                    ${isDragging ? 'border-primary bg-primary/5 scale-[1.02]' : 'border-gray-200 bg-gray-50 hover:bg-gray-100'}
                    ${form.image_url ? 'border-none' : ''}
                  `}
                >
                  {uploading ? (
                    <div className="flex flex-col items-center animate-pulse">
                      <Loader2 className="animate-spin text-primary mb-2" size={32} />
                      <span className="text-xs text-muted">正在上传...</span>
                    </div>
                  ) : form.image_url ? (
                    <img src={form.image_url} className="w-full h-auto object-contain" alt="预览" />
                  ) : (
                    <>
                      <Upload className={`${isDragging ? 'text-primary animate-bounce' : 'text-gray-300'} mb-2`} size={32} />
                      <span className="text-xs text-muted">支持点击或拖拽长图（须知切片）到这里</span>
                    </>
                  )}
                  <input id="notice-upload" type="file" className="hidden" accept="image/*" onChange={e => {
                    const file = e.target.files?.[0];
                    if (file) handleUpload(file);
                  }} />
                </div>
              </div>
              <div>
                <label className="text-sm text-muted mb-2 block">出场排序（默认数字越小越在上面展示）</label>
                <input 
                  type="number" className="input" 
                  value={form.order} onChange={e => setForm({...form, order: Number(e.target.value)})} 
                  required 
                />
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>脱离视界</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? '正在写入...' : '注入源泉流'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
