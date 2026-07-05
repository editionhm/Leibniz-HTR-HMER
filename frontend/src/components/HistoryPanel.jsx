import React from 'react';
import { History, Clock } from 'lucide-react';

export default function HistoryPanel({ history, onLoadHistoryItem }) {
  if (!history || history.length === 0) {
    return null;
  }

  return (
    <div className="history-section panel-card">
      <h2 className="panel-title" style={{ fontSize: '1.4rem', borderBottom: '1px solid var(--border-light)', paddingBottom: '0.5rem', marginBottom: '0.25rem' }}>
        <History size={20} style={{ color: 'var(--accent-gold)' }} />
        Session History
      </h2>
      <div className="history-grid">
        {history.map((item, index) => {
          // Create object URL for history thumbnail
          const thumbUrl = item.image ? URL.createObjectURL(item.image) : '';
          
          return (
            <div 
              key={item.id || index}
              className="history-card"
              onClick={() => onLoadHistoryItem(item)}
              title="Click to restore this inference result"
            >
              {thumbUrl && (
                <img 
                  src={thumbUrl} 
                  alt="history thumbnail" 
                  className="history-thumb"
                />
              )}
              <div className="history-info">
                <div className="history-info-meta">
                  <span className="history-task-tag">{item.task}</span>
                  {item.mode && (
                    <span className="history-mode-tag">{item.mode.toUpperCase()}</span>
                  )}
                  <span style={{ display: 'flex', alignItems: 'center', gap: '2px', color: 'var(--text-light)' }}>
                    <Clock size={10} />
                    {item.latency}s
                  </span>
                </div>
                <div className="history-result-preview">
                  {item.result}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
