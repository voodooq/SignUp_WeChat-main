import React, { useState } from 'react';
import { Upload, Trash2, Download, CheckCircle, AlertTriangle } from 'lucide-react';
import api, { BASE_URL } from '../services/api';

export default function ScoreManage() {
  const [uploading, setUploading] = useState(false);
  const [clearLoading, setClearLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement> | File) => {
    const selectedFile = e instanceof File ? e : e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileChange(file);
  };

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res: any = await api.post('/api/admin/scores/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (res.code === 200) {
        alert(`导入成功！成功同步: ${res.data.success} 条，因数据格式受损跳过: ${res.data.failed} 条`);
        setFile(null);
      } else {
        alert(res.message || '导入遇到不可抗力终端');
      }
    } catch (err: any) {
      console.error(err);
      alert('无法与枢纽建立联系，请检查文件编码或网络状态');
    } finally {
      setUploading(false);
    }
  };

  const handleClearScore = async () => {
    if (!window.confirm('警告: 这个操作将物理清空全库的参赛人员成绩，只能通过重新导入恢复。是否继续？')) return;
    
    setClearLoading(true);
    try {
      await api.delete('/api/admin/scores');
      alert('肃清协议已完成：所有人员成绩状态归零。');
    } catch (e) {
      console.error(e);
      alert('肃清失败，请稍后再次调用');
    } finally {
      setClearLoading(false);
    }
  };

  const token = localStorage.getItem('admin_token') || '';

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '2rem' }}>
        <h2 className="text-2xl font-bold mb-1">大规模成绩核算中心</h2>
        <p className="text-sm text-muted">通过 Excel/CSV 表格集联处理人员分数与奖项评级</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* Import Section */}
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <div style={{ padding: '0.5rem', backgroundColor: 'rgba(59, 130, 246, 0.1)', borderRadius: '8px', color: 'var(--primary)' }}>
              <Upload size={20} />
            </div>
            <h3 className="text-lg font-bold">导入评分数据</h3>
          </div>
          
          <form onSubmit={handleImport} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div 
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={onDrop}
              style={{ 
                border: '2px dashed',
                borderColor: isDragging ? 'var(--primary)' : 'var(--border)', 
                borderRadius: 'var(--radius-md)', 
                padding: '2rem 1rem', 
                textAlign: 'center',
                backgroundColor: isDragging ? 'rgba(59, 130, 246, 0.1)' : 'rgba(15, 23, 42, 0.4)',
                transform: isDragging ? 'scale(1.02)' : 'scale(1)',
                transition: 'all var(--transition-fast)'
              }}
            >
              <input 
                type="file" id="score_file" 
                accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              <label htmlFor="score_file" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle size={32} color={file ? 'var(--accent)' : 'var(--text-muted)'} />
                <span className="font-medium">{file ? file.name : '点击调配 Excel / CSV 矩阵载体'}</span>
                {!file && <span className="text-xs text-muted">表格需含有 [准考证号, 考试成绩, 项目排名, 获奖情况] 等列以供引擎扫描匹配！</span>}
              </label>
            </div>

            <button type="submit" className="btn btn-primary" disabled={!file || uploading}>
              {uploading ? '上传并推算节点中...' : '提交集成处理'}
            </button>
          </form>
        </div>

        {/* Clear & Export Section */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <div style={{ padding: '0.5rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', color: 'var(--danger)' }}>
                <AlertTriangle size={20} />
              </div>
              <h3 className="text-lg font-bold">肃清全库成绩</h3>
            </div>
            <p className="text-sm text-muted mb-4">
              执行此操作将抹去当前宇宙线内的所有选手个人成绩及获奖数据，仅当遇到严重数据污染或新陈代谢旧赛事需要清盘时使用。
            </p>
            <button 
              className="btn btn-danger" 
              onClick={handleClearScore} 
              disabled={clearLoading}
            >
              <Trash2 size={16} /> {clearLoading ? '指令授权中...' : '物理隔离并全歼'}
            </button>
          </div>

          <div className="glass-panel" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <div style={{ padding: '0.5rem', backgroundColor: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', color: 'var(--accent)' }}>
                <Download size={20} />
              </div>
              <h3 className="text-lg font-bold">生成成绩结算报表</h3>
            </div>
            <p className="text-sm text-muted mb-4">
              向总部导出一份包含全体选手报名情况与相关成绩汇总的电子制表结构数据 (Excel格式)。
            </p>
            <a 
              className="btn btn-primary" 
              style={{ backgroundColor: 'var(--accent)', textDecoration: 'none' }}
              href={`${BASE_URL}/api/admin/registrations/export/excel?token=${token}`}
            >
              启动降维导出
            </a>
          </div>

        </div>
      </div>
    </div>
  );
}
