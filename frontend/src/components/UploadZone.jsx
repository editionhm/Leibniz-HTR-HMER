import React, { useState, useRef } from 'react';
import { UploadCloud, FileImage, X } from 'lucide-react';

export default function UploadZone({ selectedImage, onImageSelected, onImageClear }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/')) {
        onImageSelected(file);
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onImageSelected(e.target.files[0]);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="section-group">
      <span className="section-label">Manuscript Image</span>
      
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        accept="image/*" 
        style={{ display: 'none' }} 
      />

      {!selectedImage ? (
        <div 
          className={`upload-zone ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={triggerFileSelect}
        >
          <UploadCloud size={40} className="text-light" style={{ color: 'var(--accent-gold)' }} />
          <div className="upload-zone-text">
            <h3>Drag & drop manuscript image</h3>
            <p>or click to browse from files (PNG, JPG, JPEG)</p>
          </div>
        </div>
      ) : (
        <div className="preview-container">
          <img 
            src={URL.createObjectURL(selectedImage)} 
            alt="Manuscript preview" 
            className="preview-image" 
          />
          <button 
            type="button" 
            className="btn-remove-image" 
            onClick={onImageClear}
            title="Remove image"
          >
            <X size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
