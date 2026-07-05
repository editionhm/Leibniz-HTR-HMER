import React, { useState, useEffect } from 'react';
import { ShieldCheck, Cpu, AlertTriangle, HelpCircle } from 'lucide-react';
import UploadZone from './components/UploadZone';
import ControlPanel from './components/ControlPanel';
import ResultPanel from './components/ResultPanel';
import HistoryPanel from './components/HistoryPanel';

export default function App() {
  // State for image
  const [selectedImage, setSelectedImage] = useState(null);
  
  // State for configuration
  const [task, setTask] = useState('HTR');
  const [mode, setMode] = useState('plain');
  const [candidate, setCandidate] = useState('');
  const [taggedCandidate, setTaggedCandidate] = useState('');
  
  // Loading & Error states
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  
  // Active Output results
  const [result, setResult] = useState(null);
  const [promptUsed, setPromptUsed] = useState('');
  const [latency, setLatency] = useState(0);
  
  // History tracking
  const [history, setHistory] = useState([]);
  
  // Backend health status state
  const [health, setHealth] = useState({
    status: 'loading',
    gpu_available: false,
    gpu_name: null,
    model_loaded: false,
    mock_mode: true,
    warning: ''
  });

  // Fetch backend status on mount
  useEffect(() => {
    fetchHealthStatus();
    // Poll status every 15 seconds
    const interval = setInterval(fetchHealthStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchHealthStatus = async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setHealth({
          status: data.status,
          gpu_available: data.gpu_available,
          gpu_name: data.gpu_name,
          model_loaded: data.model_loaded,
          mock_mode: data.mock_mode,
          warning: data.config?.warning || ''
        });
      } else {
        setHealth(prev => ({ ...prev, status: 'error' }));
      }
    } catch (err) {
      console.error("Health check failed:", err);
      setHealth(prev => ({ ...prev, status: 'error' }));
    }
  };

  const handleImageSelected = (file) => {
    setSelectedImage(file);
    setErrorMsg(null);
    // Do not clear the outputs immediately, so the user can see what they had before
  };

  const handleImageClear = () => {
    setSelectedImage(null);
    setResult(null);
    setPromptUsed('');
    setLatency(0);
    setErrorMsg(null);
  };

  const handleRunInference = async () => {
    if (!selectedImage) return;

    setIsLoading(true);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append('image', selectedImage);
    formData.append('task', task);
    
    if (task === 'HMER') {
      formData.append('mode', mode);
      if (mode === 'detect_error') {
        formData.append('candidate', candidate);
      } else if (mode === 'correct_error') {
        formData.append('tagged_candidate', taggedCandidate);
      }
    }

    try {
      const response = await fetch('/api/infer', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Inference failed");
      }

      const data = await response.json();
      
      setResult(data.result);
      setPromptUsed(data.prompt);
      setLatency(data.latency_seconds);

      // Add to session history
      const newHistoryItem = {
        id: Date.now(),
        image: selectedImage,
        task: data.task,
        mode: data.mode,
        candidate: candidate,
        taggedCandidate: taggedCandidate,
        result: data.result,
        prompt: data.prompt,
        latency: data.latency_seconds
      };
      
      setHistory(prev => [newHistoryItem, ...prev]);

    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "An unexpected error occurred during inference.");
    } finally {
      setIsLoading(false);
    }
  };

  // Workflow pipelines: Piping outputs into specific inputs
  const handleUseAsCandidate = (extractedFormula) => {
    setTask('HMER');
    setMode('detect_error');
    setCandidate(extractedFormula);
    // Scroll configuration panel into view for small devices
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleUseAsTaggedCandidate = (rawOutput) => {
    setTask('HMER');
    setMode('correct_error');
    setTaggedCandidate(rawOutput);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Restore session history item
  const handleLoadHistoryItem = (item) => {
    setSelectedImage(item.image);
    setTask(item.task);
    if (item.mode) setMode(item.mode);
    if (item.candidate) setCandidate(item.candidate);
    if (item.taggedCandidate) setTaggedCandidate(item.taggedCandidate);
    setResult(item.result);
    setPromptUsed(item.prompt);
    setLatency(item.latency);
  };

  // Dynamic connection label helper
  const getStatusIndicator = () => {
    if (health.status === 'error') {
      return (
        <span style={{ display: 'flex', alignSelf: 'center', alignItems: 'center' }}>
          <span className="status-dot" style={{ backgroundColor: 'var(--error)' }} />
          Backend Connection Failed
        </span>
      );
    }
    
    if (health.status === 'loading') {
      return (
        <span style={{ display: 'flex', alignSelf: 'center', alignItems: 'center' }}>
          <span className="status-dot loading" />
          Loading model weights...
        </span>
      );
    }

    if (health.mock_mode) {
      return (
        <span style={{ display: 'flex', alignSelf: 'center', alignItems: 'center' }} title="FastAPI backend is responsive but running in simulation. Check your GPU/weights configuration.">
          <span className="status-dot online" style={{ backgroundColor: 'var(--accent-gold)' }} />
          Online (Mock Mode Active)
        </span>
      );
    }

    return (
      <span style={{ display: 'flex', alignSelf: 'center', alignItems: 'center' }} title={`Running GPU acceleration on: ${health.gpu_name || 'CUDA'}`}>
        <span className="status-dot online" />
        GPU Acceleration Active ({health.gpu_name || 'CUDA'})
      </span>
    );
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <h1>Leibniz Manuscript Recognition Demo</h1>
        <p>HTR and HMER prototype interface powered by a fine-tuned Qwen model</p>
      </header>

      {/* Warnings & Alerts */}
      {errorMsg && (
        <div className="alert-banner error">
          <AlertTriangle size={18} />
          <div>
            <strong>Inference Failed:</strong> {errorMsg}
          </div>
        </div>
      )}

      {health.warning && (
        <div className="alert-banner warning" style={{ fontSize: '0.85rem' }}>
          <AlertTriangle size={16} />
          <div>
            <strong>Adapter Notice:</strong> {health.warning}
          </div>
        </div>
      )}

      {/* Main Grid Workspace */}
      <main className="main-grid">
        {/* Left Hand side inputs configuration */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div className="panel-card">
            <h2 className="panel-title">
              <Cpu size={22} style={{ color: 'var(--accent-gold)' }} />
              Manuscript Upload
            </h2>
            <UploadZone 
              selectedImage={selectedImage}
              onImageSelected={handleImageSelected}
              onImageClear={handleImageClear}
            />
          </div>

          <ControlPanel 
            task={task}
            setTask={setTask}
            mode={mode}
            setMode={setMode}
            candidate={candidate}
            setCandidate={setCandidate}
            taggedCandidate={taggedCandidate}
            setTaggedCandidate={setTaggedCandidate}
            onRun={handleRunInference}
            isLoading={isLoading}
            hasImage={!!selectedImage}
          />
        </div>

        {/* Right Hand side outputs & KaTeX preview */}
        <ResultPanel 
          result={result}
          task={task}
          mode={mode}
          prompt={promptUsed}
          latency={latency}
          onUseAsCandidate={handleUseAsCandidate}
          onUseAsTaggedCandidate={handleUseAsTaggedCandidate}
        />

        {/* History Panel spanning across full page */}
        <HistoryPanel 
          history={history}
          onLoadHistoryItem={handleLoadHistoryItem}
        />
      </main>

      {/* Footer Status Indicators */}
      <footer className="status-footer">
        <div>
          {getStatusIndicator()}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <ShieldCheck size={14} style={{ color: 'var(--accent-gold)' }} />
          <span>Leibniz Archive Project Prototype v1.0</span>
        </div>
      </footer>
    </div>
  );
}
