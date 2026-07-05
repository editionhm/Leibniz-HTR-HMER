import React, { useEffect, useRef, useState } from 'react';
import { Copy, Download, ArrowRight, CornerDownLeft, Eye, HelpCircle, Check, ChevronDown, ChevronUp } from 'lucide-react';
import katex from 'katex';
import 'katex/dist/katex.min.css';

export default function ResultPanel({
  result,
  task,
  mode,
  prompt,
  latency,
  onUseAsCandidate,
  onUseAsTaggedCandidate
}) {
  const [copied, setCopied] = useState(false);
  const [showPrompt, setShowPrompt] = useState(false);
  const katexRef = useRef(null);

  // Helper to extract LaTeX formula from various prompt strategy outputs
  const extractLatex = (text) => {
    if (!text) return '';
    
    // Look for standard prefixes in our prompts output
    const formulaPrefixes = [
      /Formula LaTeX:\s*(.*)/i,
      /Corrected LaTeX:\s*(.*)/i,
      /Corrected formula:\s*(.*)/i,
      /Marked formula:\s*(.*)/i,
      /LaTeX:\s*(.*)/i
    ];

    for (const regex of formulaPrefixes) {
      const match = text.match(regex);
      if (match && match[1]) {
        return match[1].trim();
      }
    }

    // If it's HMER and there's no clear structure, try returning the whole string
    // but strip any trailing explanations if they look like plain English.
    // (In plain mode, the whole result is the LaTeX code).
    return text.trim();
  };

  const activeFormula = extractLatex(result);

  // Render LaTeX via KaTeX
  useEffect(() => {
    if (katexRef.current && activeFormula && task === 'HMER') {
      try {
        katex.render(activeFormula, katexRef.current, {
          displayMode: true,
          throwOnError: false,
          trust: true
        });
      } catch (err) {
        katexRef.current.innerHTML = `<span style="color:var(--error); font-size:0.9rem">KaTeX Render Error: ${err.message}</span>`;
      }
    }
  }, [activeFormula, task]);

  const handleCopy = () => {
    if (!result) return;
    navigator.clipboard.writeText(result);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!result) return;
    const element = document.createElement("a");
    const file = new Blob([result], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `leibniz_${task.toLowerCase()}_${mode || 'result'}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  if (!result) {
    return (
      <div className="panel-card">
        <h2 className="panel-title">
          <Eye size={22} style={{ color: 'var(--accent-gold)' }} />
          Recognition Output
        </h2>
        <div className="result-empty">
          <HelpCircle size={36} style={{ color: 'var(--border-medium)' }} />
          <p>Run inference on an image to view results here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="panel-card">
      <h2 className="panel-title">
        <Eye size={22} style={{ color: 'var(--accent-gold)' }} />
        Recognition Output
      </h2>

      <div className="result-output-container">
        {/* Latency / Meta */}
        <div className="result-header-meta">
          <span>Task: <strong>{task}</strong> {mode && `(${mode.toUpperCase()})`}</span>
          <span>Inference Latency: <strong>{latency}s</strong></span>
        </div>

        {/* Collapsible Prompt Used */}
        <div className="output-section">
          <button 
            type="button" 
            className="collapsible-trigger"
            onClick={() => setShowPrompt(!showPrompt)}
          >
            {showPrompt ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            {showPrompt ? "Hide prompt sent to model" : "Show prompt sent to model"}
          </button>
          {showPrompt && (
            <div className="prompt-box" style={{ marginTop: '0', fontSize: '0.8rem' }}>
              {prompt}
            </div>
          )}
        </div>

        {/* Raw Text Monospace Panel */}
        <div className="output-section">
          <span className="section-label">Raw Model Output</span>
          <pre className="raw-output">{result}</pre>
        </div>

        {/* LaTeX Math Rendering (HMER only) */}
        {task === 'HMER' && activeFormula && (
          <div className="output-section">
            <span className="section-label">KaTeX Formula Rendering</span>
            <div className="katex-rendered-card" ref={katexRef}>
              {/* Rendered by KaTeX */}
            </div>
          </div>
        )}

        {/* Helper Toolbar */}
        <div className="result-toolbar">
          <button 
            type="button" 
            className="btn-secondary"
            onClick={handleCopy}
            title="Copy output to clipboard"
          >
            {copied ? <Check size={14} style={{ color: 'var(--success)' }} /> : <Copy size={14} />}
            {copied ? "Copied!" : "Copy Raw"}
          </button>

          <button 
            type="button" 
            className="btn-secondary"
            onClick={handleDownload}
            title="Download result file"
          >
            <Download size={14} />
            Download
          </button>

          {task === 'HMER' && (
            <>
              <button 
                type="button" 
                className="btn-secondary"
                onClick={() => onUseAsCandidate(activeFormula)}
                title="Send formula to Candidate OCR input"
              >
                <ArrowRight size={14} />
                Use as candidate
              </button>

              <button 
                type="button" 
                className="btn-secondary"
                onClick={() => onUseAsTaggedCandidate(result)}
                title="Send result to Tagged candidate input"
              >
                <CornerDownLeft size={14} />
                Use as tagged candidate
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
