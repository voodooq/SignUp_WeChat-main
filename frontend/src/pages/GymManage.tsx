import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Edit2, Trash2, MapPin, Image as ImageIcon } from 'lucide-react';

interface Gym {
  id: string;
  name: string;
  name_en?: string;
  address: string;
  address_en?: string;
  lng: number;
  lat: number;
  intro?: string;
  intro_en?: string;
  images: string[];
}

export default function GymManage() {
  const [gyms, setGyms] = useState<Gym[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingGym, setEditingGym] = useState<Partial<Gym> | null>(null);

  const fetchGyms = async () => {
    try {
      const res = await axios.get('/api/gym/list');
      if (res.data.code === 200) {
        setGyms(res.data.data);
      }
    } catch (err) {
      console.error('Fetch gyms failed', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGyms();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('admin_token');
    try {
      if (editingGym?.id) {
        await axios.put(`/api/gym/admin/${editingGym.id}`, editingGym, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post('/api/gym/admin/add', editingGym, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      setShowModal(false);
      fetchGyms();
    } catch (err) {
      alert('保存失败');
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除该场馆吗？')) return;
    const token = localStorage.getItem('admin_token');
    try {
      await axios.delete(`/api/gym/admin/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchGyms();
    } catch (err) {
      alert('删除失败');
    }
  };

  const handleUploadImage = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post('/api/upload', formData);
      if (res.data.code === 200) {
        const newUrl = res.data.data.url;
        setEditingGym(prev => ({
          ...prev,
          images: [...(prev?.images || []), newUrl]
        }));
      }
    } catch (err) {
      alert('上传失败');
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">场馆及线路管理</h2>
          <p className="text-sm text-muted">管理攀岩馆信息及其关联的攀登线路</p>
        </div>
        <button
          onClick={() => {
            setEditingGym({ name: '', address: '', lng: 0, lat: 0, images: [] });
            setShowModal(true);
          }}
          className="btn btn-primary"
        >
          <Plus size={20} />
          <span>添加场馆</span>
        </button>
      </div>

      {loading ? (
        <div className="py-20 text-center text-muted">加载中...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {gyms.map((gym) => (
            <div key={gym.id} className="glass-panel group overflow-hidden border border-border hover:border-primary transition-all">
              <div className="h-44 bg-gray-100 relative">
                {gym.images?.[0] ? (
                  <img src={gym.images[0]} alt={gym.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-300">
                    <ImageIcon size={48} />
                  </div>
                )}
                <div className="absolute top-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="p-2 bg-white/90 shadow-sm rounded-lg text-primary hover:bg-primary hover:text-white" onClick={() => { setEditingGym(gym); setShowModal(true); }}>
                    <Edit2 size={16} />
                  </button>
                  <button className="p-2 bg-white/90 shadow-sm rounded-lg text-danger hover:bg-danger hover:text-white" onClick={() => handleDelete(gym.id)}>
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              <div className="p-5">
                <h3 className="font-bold text-lg mb-1">{gym.name}</h3>
                <p className="text-sm text-muted mb-4 flex items-center gap-1">
                  <MapPin size={14} /> {gym.address}
                </p>
                <div className="flex gap-2">
                  <button className="btn btn-secondary py-2 text-xs flex-1">管理线路</button>
                  <button className="btn btn-secondary py-2 text-xs px-4">详情</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && editingGym && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="glass-panel w-full max-w-2xl p-6 shadow-2xl overflow-y-auto max-h-[90vh]">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold">{editingGym.id ? '编辑场馆' : '添加新场馆'}</h3>
              <button onClick={() => setShowModal(false)} className="text-muted hover:text-gray-900">&times;</button>
            </div>
            <form onSubmit={handleSave} className="space-y-5">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-muted block mb-1">场馆名称 (中文)</label>
                  <input
                    className="input" value={editingGym.name} required
                    onChange={(e) => setEditingGym({ ...editingGym, name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-xs text-muted block mb-1">场馆名称 (英文)</label>
                  <input
                    className="input" value={editingGym.name_en || ''}
                    onChange={(e) => setEditingGym({ ...editingGym, name_en: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-muted block mb-1">详细地址</label>
                <input
                  className="input" value={editingGym.address} required
                  onChange={(e) => setEditingGym({ ...editingGym, address: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-muted block mb-1">经度 (Lng)</label>
                  <input
                    type="number" step="0.000001" className="input" value={editingGym.lng} required
                    onChange={(e) => setEditingGym({ ...editingGym, lng: parseFloat(e.target.value) })}
                  />
                </div>
                <div>
                  <label className="text-xs text-muted block mb-1">纬度 (Lat)</label>
                  <input
                    type="number" step="0.000001" className="input" value={editingGym.lat} required
                    onChange={(e) => setEditingGym({ ...editingGym, lat: parseFloat(e.target.value) })}
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-muted block mb-1">场馆简介</label>
                <textarea
                  className="input min-h-[80px] py-2" value={editingGym.intro || ''}
                  onChange={(e) => setEditingGym({ ...editingGym, intro: e.target.value })}
                />
              </div>
              <div>
                <label className="text-xs text-muted block mb-1">场馆图片 (第一张为头图)</label>
                <div className="grid grid-cols-4 gap-2 mt-2">
                  {editingGym.images?.map((url, idx) => (
                    <div key={idx} className="relative aspect-video rounded-lg overflow-hidden group">
                      <img src={url} className="w-full h-full object-cover" />
                      <button 
                        type="button"
                        className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => setEditingGym(prev => ({ ...prev, images: prev?.images?.filter((_, i) => i !== idx) }))}
                      >
                        &times;
                      </button>
                    </div>
                  ))}
                  <label className="aspect-video border-2 border-dashed border-gray-200 rounded-lg flex items-center justify-center cursor-pointer hover:bg-gray-50">
                    <Plus className="text-gray-300" />
                    <input type="file" className="hidden" accept="image/*" onChange={handleUploadImage} />
                  </label>
                </div>
              </div>
              <div className="flex gap-3 pt-6">
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary flex-1">取消</button>
                <button type="submit" className="btn btn-primary flex-1">保存场馆信息</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
