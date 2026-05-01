import { useEffect, useState } from 'react';
import { Plus, Edit2, Trash2, Calendar, MapPin, Save, X, Upload, Loader2 } from 'lucide-react';
import api from '../services/api';

interface Competition {
  _id: string;
  title: string;
  location: string;
  poster_url: string;
  start_time: string;
  reg_start_time: string;
  reg_end_time: string;
  contact_name: string;
  contact_phone: string;
  status: string;
  intro?: string;
  news?: string[];
  highlight_videos?: string[];
  live_url?: string;
  rankings?: any[];
}

export default function CompetitionManage() {
  const [list, setList] = useState<Competition[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState<Partial<Competition> | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchList();
  }, []);

  const fetchList = async () => {
    try {
      const res: any = await api.get('/api/admin/competitions');
      if (res.code === 200) {
        setList(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAdd = () => {
    setEditingItem({
      title: '',
      location: '',
      poster_url: '',
      start_time: '',
      reg_start_time: '',
      reg_end_time: '',
      contact_name: '',
      contact_phone: '',
      intro: '',
      news: [],
      highlight_videos: [],
      live_url: '',
      rankings: []
    });
    setShowModal(true);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement> | File) => {
    let file: File | undefined;
    if (e instanceof File) {
      file = e;
    } else {
      file = e.target.files?.[0];
    }
    
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res: any = await api.post('/api/upload', formData);
      if (res.code === 200) {
        setEditingItem(prev => ({ ...prev, poster_url: res.data.url }));
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

  const handleEdit = (item: Competition) => {
    const formatForInput = (s: string) => s ? s.replace(' ', 'T') : '';
    setEditingItem({
      ...item,
      start_time: formatForInput(item.start_time),
      reg_start_time: formatForInput(item.reg_start_time),
      reg_end_time: formatForInput(item.reg_end_time)
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!editingItem) return;
    const formatForSave = (s: string | undefined) => s ? s.replace('T', ' ') : '';
    const payload = {
      ...editingItem,
      start_time: formatForSave(editingItem.start_time),
      reg_start_time: formatForSave(editingItem.reg_start_time),
      reg_end_time: formatForSave(editingItem.reg_end_time)
    };
    try {
      if (payload._id) {
        await api.put(`/api/admin/competitions/${payload._id}`, payload);
      } else {
        await api.post('/api/admin/competitions', payload);
      }
      setShowModal(false);
      fetchList();
    } catch (e) {
      alert('保存失败');
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除该赛事吗？')) return;
    try {
      await api.delete(`/api/admin/competitions/${id}`);
      fetchList();
    } catch (e) {
      alert('删除失败');
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold mb-1">赛事管理</h2>
          <p className="text-sm text-muted">创建并管理多个独立的赛事活动及报名时间</p>
        </div>
        <button className="btn btn-primary" onClick={handleOpenAdd}>
          <Plus size={18} /> 创建新赛事
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full text-center py-12 text-muted">加载中...</div>
        ) : list.length === 0 ? (
          <div className="col-span-full text-center py-12 bg-white rounded-xl border-2 border-dashed">
            <Calendar className="mx-auto mb-4 text-gray-300" size={48} />
            <p className="text-muted">暂无赛事，点击右上角创建第一个</p>
          </div>
        ) : (
          list.map(item => (
            <div key={item._id} className="glass-panel relative group overflow-hidden flex flex-col">
              {item.poster_url && (
                <div className="w-full h-32 overflow-hidden">
                  <img src={item.poster_url} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" alt="封面" />
                </div>
              )}
              <div className="p-5">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-bold text-lg text-gray-900 pr-8">{item.title}</h3>
                  <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-all">
                    <button className="p-1.5 hover:bg-blue-50 text-blue-600 rounded" onClick={() => handleEdit(item)}>
                      <Edit2 size={16} />
                    </button>
                    <button className="p-1.5 hover:bg-red-50 text-red-600 rounded" onClick={() => handleDelete(item._id)}>
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex items-center gap-2"><MapPin size={14} /> {item.location}</div>
                  <div className="flex items-center gap-2"><Calendar size={14} /> 比赛：{item.start_time}</div>
                  <div className="pt-2 border-t border-gray-50">
                    <div className="text-xs text-muted mb-1">报名时间：</div>
                    <div className="text-xs font-medium">{item.reg_start_time} 至 {item.reg_end_time}</div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {showModal && editingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-lg p-6 shadow-2xl overflow-y-auto max-h-[90vh]">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold">{editingItem._id ? '编辑赛事' : '创建新赛事'}</h3>
              <button onClick={() => setShowModal(false)} className="text-muted hover:text-gray-900"><X /></button>
            </div>
            <div className="space-y-5">
              <div 
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={onDrop}
                className={`
                  w-full h-40 border-2 border-dashed rounded-xl overflow-hidden flex flex-col items-center justify-center cursor-pointer transition-all relative group
                  ${isDragging ? 'border-primary bg-primary/5 scale-[1.02]' : 'border-gray-200 bg-gray-50 hover:bg-gray-100'}
                  ${editingItem.poster_url ? 'border-none' : ''}
                `}
                onClick={() => document.getElementById('poster-upload')?.click()}
              >
                {uploading ? (
                  <div className="flex flex-col items-center animate-pulse">
                    <Loader2 className="animate-spin text-primary mb-2" size={32} />
                    <span className="text-xs text-muted">正在处理...</span>
                  </div>
                ) : editingItem.poster_url ? (
                  <img src={editingItem.poster_url} className="w-full h-full object-cover" alt="封面" />
                ) : (
                  <>
                    <Upload className={`${isDragging ? 'text-primary animate-bounce' : 'text-gray-300'} mb-2`} size={32} />
                    <span className="text-xs text-muted">点击或拖拽页面封面 (16:9)</span>
                  </>
                )}
                <input id="poster-upload" type="file" className="hidden" accept="image/*,video/*" onChange={handleUpload} />
                {editingItem.poster_url && !uploading && (
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                    <span className="text-white text-xs font-medium">更换图片/视频</span>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <input type="text" className="input" value={editingItem.title} placeholder="赛事标题" 
                  onChange={e => setEditingItem({...editingItem, title: e.target.value})} />
                <input type="text" className="input" value={editingItem.location} placeholder="地点" 
                  onChange={e => setEditingItem({...editingItem, location: e.target.value})} />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-muted block mb-1">联系人</label>
                  <input type="text" className="input" value={editingItem.contact_name} placeholder="联系人姓名" 
                    onChange={e => setEditingItem({...editingItem, contact_name: e.target.value})} />
                </div>
                <div>
                  <label className="text-xs text-muted block mb-1">联系电话</label>
                  <input type="text" className="input" value={editingItem.contact_phone} placeholder="联系电话" 
                    onChange={e => setEditingItem({...editingItem, contact_phone: e.target.value})} />
                </div>
              </div>

              <div>
                <label className="text-xs text-muted block mb-1">赛事介绍 (支持富文本/简介)</label>
                <textarea className="input min-h-[100px] py-2" value={editingItem.intro} placeholder="输入赛事详情介绍..." 
                  onChange={e => setEditingItem({...editingItem, intro: e.target.value})} />
              </div>

              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="text-xs text-muted block mb-1">相关新闻 URL (每行一个)</label>
                  <textarea className="input py-2" rows={3} value={editingItem.news?.join('\n') || ''} placeholder="输入新闻链接..." 
                    onChange={e => setEditingItem({...editingItem, news: e.target.value.split('\n').filter(s => s.trim())})} />
                </div>
                <div>
                  <label className="text-xs text-muted block mb-1">精彩视频/回顾 URL (每行一个)</label>
                  <textarea className="input py-2" rows={3} value={editingItem.highlight_videos?.join('\n') || ''} placeholder="输入视频链接..." 
                    onChange={e => setEditingItem({...editingItem, highlight_videos: e.target.value.split('\n').filter(s => s.trim())})} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs text-muted block mb-1">直播间 URL</label>
                  <input type="text" className="input" value={editingItem.live_url || ''} placeholder="https://..." 
                    onChange={e => setEditingItem({...editingItem, live_url: e.target.value})} />
                </div>
                <div>
                  <label className="text-xs text-muted block mb-1">实时名次 (JSON 格式)</label>
                  <textarea className="input py-2 text-xs font-mono" rows={2} value={JSON.stringify(editingItem.rankings || [])} placeholder='[{"rank":1,"name":"张三"}]' 
                    onChange={e => { try { setEditingItem({...editingItem, rankings: JSON.parse(e.target.value)}); } catch(e) {} }} />
                </div>
              </div>

              <div className="pt-4 border-t border-gray-100">
                <label className="text-xs font-bold text-gray-500 block mb-3 uppercase tracking-wider">时间线设置</label>
                <div className="space-y-4">
                  <div>
                    <label className="text-xs text-muted block mb-1">比赛举行时间</label>
                    <input type="datetime-local" step="1" className="input" value={editingItem.start_time} 
                      onChange={e => setEditingItem({...editingItem, start_time: e.target.value})} />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs text-muted block mb-1">报名开始时间</label>
                      <input type="datetime-local" step="1" className="input" value={editingItem.reg_start_time} 
                        onChange={e => setEditingItem({...editingItem, reg_start_time: e.target.value})} />
                    </div>
                    <div>
                      <label className="text-xs text-muted block mb-1">报名截止时间</label>
                      <input type="datetime-local" step="1" className="input" value={editingItem.reg_end_time} 
                        onChange={e => setEditingItem({...editingItem, reg_end_time: e.target.value})} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-8">
              <button className="btn btn-secondary flex-1" onClick={() => setShowModal(false)}>取消</button>
              <button className="btn btn-primary flex-1" onClick={handleSave}><Save size={18} /> 保存赛事</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
