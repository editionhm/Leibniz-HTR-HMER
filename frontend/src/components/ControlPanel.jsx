import React from 'react';
import { Type, Binary, HelpCircle, AlertCircle } from 'lucide-react';

export default function ControlPanel({
  task,
  setTask,
  mode,
  setMode,
  candidate,
  setCandidate,
  taggedCandidate,
  setTaggedCandidate,
  onRun,
  isLoading,
  hasImage
}) {
  
  const hmerModes = [
    { id: 'plain', label: 'Plain' },
    { id: 'symbol_counting', label: 'Symbol Counting' },
    { id: 'tree_cot', label: 'Tree CoT' },
    { id: 'detect_error', label: 'Detect ERROR' },
    { id: 'correct_error', label: 'Correct ERROR' }
  ];

  // Helper to show current active prompt preview
  const getPromptPreview = () => {
    if (task === 'HTR') {
      return "I have an image of a handwritten text. Please transcribe the handwritten text as accurately as possible.";
    }
    
    switch (mode) {
      case 'plain':
        return "I have an image of a handwritten mathematical expression. Please write out the expression of the formula in the image using LaTeX format";
      case 'symbol_counting':
        return "I have an image of a handwritten mathematical expression. Please identify and count each distinct visible mathematical symbol in the image, and then provide its corresponding LaTeX format";
      case 'tree_cot':
        return "I have an image of a handwritten mathematical expression. Please generate the abstract syntax tree (AST) of the formula in the image, and then provide its corresponding LaTeX format.";
      case 'detect_error':
        return `I have an image of a handwritten mathematical expression and its OCR recognition result. Please help me to detect possible errors in the recognition result and mark the places where errors occur with <error_start> <error_end> and <deleted>.
erroneous formula: [${candidate || 'candidate'}]
Marked formula:`;
      case 'correct_error':
        return `I have an image of a handwritten mathematical expression and a predicted formula with error tags, correct the formula by modifying the parts marked with <error_start> and <error_end> and inserting content where <deleted> are present. Output the modifications as REPLACE, INSERT, or DELETE operations.
Marked formula: [${taggedCandidate || 'tagged candidate'}]
Correction log:`;
      default:
        return "";
    }
  };

  const isSubmitDisabled = () => {
    if (isLoading || !hasImage) return true;
    if (task === 'HMER') {
      if (mode === 'detect_error' && !candidate.trim()) return true;
      if (mode === 'correct_error' && !taggedCandidate.trim()) return true;
    }
    return false;
  };

  return (
    <div className="panel-card">
      <h2 className="panel-title">
        <Binary size={22} style={{ color: 'var(--accent-gold)' }} />
        Task Configuration
      </h2>

      {/* Task Selector */}
      <div className="section-group">
        <span className="section-label">Select Task</span>
        <div className="task-selector">
          <button
            type="button"
            className={`btn-tab ${task === 'HTR' ? 'active' : ''}`}
            onClick={() => setTask('HTR')}
          >
            <Type size={18} />
            HTR (Text)
          </button>
          <button
            type="button"
            className={`btn-tab ${task === 'HMER' ? 'active' : ''}`}
            onClick={() => setTask('HMER')}
          >
            <Binary size={18} />
            HMER (Math)
          </button>
        </div>
      </div>

      {/* HMER Mode Selector */}
      {task === 'HMER' && (
        <div className="section-group">
          <span className="section-label">HMER Prompt Strategy</span>
          <div className="strategy-grid">
            {hmerModes.map((m) => (
              <button
                key={m.id}
                type="button"
                className={`btn-pill ${mode === m.id ? 'active' : ''}`}
                onClick={() => setMode(m.id)}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Conditional Text Inputs */}
      {task === 'HMER' && mode === 'detect_error' && (
        <div className="section-group">
          <span className="section-label">Candidate Formula (OCR Result)</span>
          <textarea
            className="text-input"
            value={candidate}
            onChange={(e) => setCandidate(e.target.value)}
            placeholder="e.g. \int_0^\infty e^{-x} dx = \frac{\pi}{2}"
          />
        </div>
      )}

      {task === 'HMER' && mode === 'correct_error' && (
        <div className="section-group">
          <span className="section-label">Tagged Candidate Formula</span>
          <textarea
            className="text-input"
            value={taggedCandidate}
            onChange={(e) => setTaggedCandidate(e.target.value)}
            placeholder="e.g. \int_0^\infty e^{-x <error_start> <error_end> <deleted> ^2} dx = \frac{\pi}{2}"
          />
        </div>
      )}

      {/* Prompt Preview */}
      <div className="section-group">
        <span className="section-label">Prompt Preview</span>
        <div className="prompt-box">
          {getPromptPreview()}
        </div>
      </div>

      {/* Run Action */}
      <button
        type="button"
        className="btn-action"
        disabled={isSubmitDisabled()}
        onClick={onRun}
      >
        {isLoading ? (
          <>
            <div className="spinner" />
            Processing...
          </>
        ) : (
          "Run Inference"
        )}
      </button>

      {!hasImage && (
        <div className="alert-banner warning" style={{ fontSize: '0.8rem', padding: '0.5rem' }}>
          <AlertCircle size={14} />
          Please upload a manuscript image to run inference.
        </div>
      )}
    </div>
  );
}
