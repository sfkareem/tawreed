"use client";

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileSpreadsheet, Play, CheckCircle, AlertCircle, Sparkles, Box, LayoutDashboard, History, Settings, Save, Clock, Info, Shield, Code, Zap, Eye, EyeOff, Loader2 } from 'lucide-react';
import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
  onClick: () => void;
}

interface SettingsConfig {
  api_key: string;
  model_id: string;
  base_url: string;
}

interface HistoryRecord {
  id: string;
  project_name: string;
  timestamp: string;
  packages_count: number;
  output_path: string;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'workspace' | 'history' | 'settings' | 'about'>('workspace');
  
  return (
    <div className="flex h-screen bg-[#030305] text-slate-50 font-sans overflow-hidden selection:bg-blue-500/30 relative">
      
      {/* GLOBAL BACKGROUND - Unifies Sidebar and Main Content */}
      <div className="fixed inset-0 pointer-events-none z-0 flex items-center justify-center overflow-hidden">
        {/* Glowing Orbs */}
        <div className="absolute top-[-20%] left-[-10%] w-[50vw] h-[50vw] max-w-[800px] max-h-[800px] bg-blue-600/15 rounded-full blur-[120px] mix-blend-screen" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[40vw] h-[40vw] max-w-[600px] max-h-[600px] bg-emerald-500/10 rounded-full blur-[120px] mix-blend-screen" />
        
        {/* Unified Grid Overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff03_1px,transparent_1px),linear-gradient(to_bottom,#ffffff03_1px,transparent_1px)] bg-[size:32px_32px]" />
      </div>

      {/* Sidebar - Now Glassmorphic to blend with background */}
      <div className="w-20 md:w-64 flex-shrink-0 bg-white/[0.02] backdrop-blur-3xl border-r border-white/5 flex flex-col p-4 md:p-6 z-50 transition-all duration-300">
        <div className="flex items-center justify-center md:justify-start gap-3 mb-10 md:mb-12 mt-2">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20 flex-shrink-0">
            <Box className="w-5 h-5 text-white" />
          </div>
          <h2 className="hidden md:block text-xl font-bold tracking-tight bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">Tawreed</h2>
        </div>
        
        <nav className="flex flex-col gap-2 flex-1">
          <NavItem icon={<LayoutDashboard />} label="Workspace" isActive={activeTab === 'workspace'} onClick={() => setActiveTab('workspace')} />
          <NavItem icon={<History />} label="History" isActive={activeTab === 'history'} onClick={() => setActiveTab('history')} />
          <NavItem icon={<Settings />} label="Settings" isActive={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
          <NavItem icon={<Info />} label="About" isActive={activeTab === 'about'} onClick={() => setActiveTab('about')} />
        </nav>
        
        <div className="hidden md:flex mt-auto pt-6 border-t border-white/5 text-xs text-slate-500 items-center justify-center">
          <span>v0.0.1</span>
        </div>
      </div>

      {/* Main Content Area - Scrollable but hides horizontal overflow */}
      <div className="flex-1 relative overflow-x-hidden overflow-y-auto custom-scrollbar z-10">
        <div className="min-h-full flex flex-col items-center justify-center p-4 sm:p-8 md:p-12">
          <AnimatePresence mode="wait">
            {activeTab === 'workspace' && <Workspace key="workspace" />}
            {activeTab === 'history' && <HistoryScreen key="history" />}
            {activeTab === 'settings' && <SettingsScreen key="settings" />}
            {activeTab === 'about' && <AboutScreen key="about" />}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

function NavItem({ icon, label, isActive, onClick }: NavItemProps) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center justify-center md:justify-start gap-3 p-3 md:px-4 md:py-3 rounded-xl transition-all duration-300 relative overflow-hidden group ${isActive ? 'text-white' : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.02]'}`}
      title={label}
    >
      {isActive && (
        <motion.div layoutId="activeNav" className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-emerald-500/10 border border-white/5 rounded-xl" transition={{ type: "spring", stiffness: 300, damping: 30 }} />
      )}
      {isActive && (
        <div className="absolute left-0 top-1/4 bottom-1/4 w-1 bg-gradient-to-b from-blue-400 to-emerald-400 rounded-r-full shadow-[0_0_10px_rgba(56,189,248,0.5)]" />
      )}
      <div className={`relative z-10 [&>svg]:w-5 [&>svg]:h-5 transition-transform duration-300 ${isActive ? 'scale-110 text-blue-400' : 'group-hover:scale-110'}`}>
        {icon}
      </div>
      <span className="hidden md:block relative z-10 font-medium">{label}</span>
    </button>
  );
}

function Workspace() {
  const [filePath, setFilePath] = useState('');
  const [status, setStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [settings, setSettings] = useState<SettingsConfig | null>(null);

  useEffect(() => {
    invoke<SettingsConfig>('get_settings')
      .then((s) => setSettings(s))
      .catch((err) => {
        console.error(err);
        setMessage(err instanceof Error ? err.message : String(err));
        setStatus('error');
      });
  }, []);

  const selectFile = async () => {
    try {
      const selected = await open({
        multiple: false,
        filters: [{ name: 'Excel', extensions: ['xlsx', 'xls'] }]
      });
      if (selected && typeof selected === 'string') {
        setFilePath(selected);
        setStatus('idle');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const processFile = async () => {
    if (!filePath || !settings) return;
    setStatus('processing');
    try {
      const res: string = await invoke('process_boq', {
        filePath,
        baseUrl: settings.base_url,
        model: settings.model_id,
        apiKey: settings.api_key
      });
      setMessage(`Successfully extracted to: ${res.replace(/\\/g, '/').split('/').pop()}`);
      setStatus('success');
    } catch (err: unknown) {
      setMessage(err instanceof Error ? err.message : String(err));
      setStatus('error');
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="w-full max-w-3xl"
    >
      <div className="relative bg-[#0d0d14]/60 backdrop-blur-xl border border-white/10 rounded-3xl sm:rounded-[2.5rem] p-6 sm:p-10 md:p-12 shadow-[0_0_80px_rgba(0,0,0,0.5)] overflow-hidden">
        
        {/* Subtle Inner Glow */}
        <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent opacity-50 pointer-events-none" />

        {/* Header */}
        <div className="relative z-20 flex flex-col items-center mb-8 sm:mb-12 text-center">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight mb-3 sm:mb-4">
            <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-emerald-400 bg-clip-text text-transparent">AI-Driven</span>
            <span className="text-white"> Work Package Extraction</span>
          </h1>
          <p className="text-slate-400 text-sm sm:text-base md:text-lg max-w-md">
            Upload your master sheet to automatically extract supplier packages.
          </p>
        </div>

        {/* Upload Zone */}
        <div className="relative z-20 mb-8">
          <motion.div 
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={selectFile}
            className="relative group cursor-pointer"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-emerald-500/20 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative border-2 border-dashed border-slate-700/60 hover:border-blue-500/50 bg-black/20 backdrop-blur-sm rounded-3xl p-8 sm:p-10 text-center transition-all duration-300">
              <AnimatePresence mode="wait">
                {filePath ? (
                  <motion.div 
                    key="file"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="flex flex-col items-center gap-3 sm:gap-4"
                  >
                    <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-blue-500/20 flex items-center justify-center border border-blue-500/30">
                      <FileSpreadsheet className="w-7 h-7 sm:w-8 sm:h-8 text-blue-400" />
                    </div>
                    <div className="flex flex-col items-center w-full">
                      <span className="text-blue-300 font-semibold text-lg sm:text-xl px-2 sm:px-4 truncate w-full max-w-[200px] sm:max-w-[320px]">
                        {filePath.replace(/\\/g, '/').split('/').pop()}
                      </span>
                      <span className="text-slate-500 text-xs sm:text-sm mt-1">Ready for processing</span>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div 
                    key="empty"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="flex flex-col items-center gap-3 sm:gap-4"
                  >
                    <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-slate-800/50 flex items-center justify-center border border-slate-700 group-hover:border-blue-500/50 group-hover:bg-blue-500/10 transition-all">
                      <Upload className="w-7 h-7 sm:w-8 sm:h-8 text-slate-400 group-hover:text-blue-400 transition-colors" />
                    </div>
                    <div className="flex flex-col items-center">
                      <span className="text-slate-300 font-medium text-lg sm:text-xl">Select BOQ Spreadsheet</span>
                      <span className="text-slate-500 text-xs sm:text-sm mt-1">Supports .xlsx and .xls formats</span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>

        {/* Action Button */}
        <div className="relative z-20">
          <motion.button
            whileHover={filePath && status !== 'processing' && settings?.api_key ? { scale: 1.01 } : {}}
            whileTap={filePath && status !== 'processing' && settings?.api_key ? { scale: 0.99 } : {}}
            onClick={processFile}
            disabled={!filePath || status === 'processing' || !settings?.api_key}
            className="relative w-full h-14 sm:h-16 rounded-2xl font-bold text-base sm:text-lg overflow-hidden group disabled:cursor-not-allowed"
          >
            {/* Disabled State Background */}
            <div className="absolute inset-0 bg-[#1a1a24] opacity-0 group-disabled:opacity-100 transition-opacity duration-300" />
            
            {/* Active State Background & Animation */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-emerald-600 to-blue-600 bg-[length:200%_100%] animate-[gradient_2s_linear_infinite] opacity-100 group-disabled:opacity-0 transition-opacity duration-300" />
            
            <div className="relative flex items-center justify-center gap-3 h-full transition-colors duration-300">
              {!settings?.api_key ? (
                <>
                  <Settings className="w-5 h-5 text-slate-500" />
                  <span className="text-slate-400 font-medium">Configure API Key in Settings</span>
                </>
              ) : status === 'processing' ? (
                <>
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                    <Sparkles className="w-5 h-5 text-white" />
                  </motion.div>
                  <span className="text-white">Extracting Packages with LLM...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 text-white fill-current" />
                  <span className="text-white">Generate Work Packages</span>
                </>
              )}
            </div>
          </motion.button>
        </div>

        {/* Status Messages */}
        <AnimatePresence>
          {status === 'success' && (
            <motion.div 
              initial={{ opacity: 0, height: 0, marginTop: 0 }} 
              animate={{ opacity: 1, height: 'auto', marginTop: 24 }} 
              exit={{ opacity: 0, height: 0, marginTop: 0 }}
              className="relative z-20 overflow-hidden"
            >
              <div className="p-4 sm:p-5 bg-emerald-500/10 border border-emerald-500/20 backdrop-blur-md rounded-2xl flex gap-3 sm:gap-4 items-start shadow-[0_0_30px_rgba(16,185,129,0.1)]">
                <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-400" />
                </div>
                <div>
                  <h4 className="text-emerald-400 font-semibold mb-1 text-sm sm:text-base">Processing Complete</h4>
                  <p className="text-emerald-400/80 text-xs sm:text-sm leading-relaxed break-all">{message}</p>
                </div>
              </div>
            </motion.div>
          )}
          
          {status === 'error' && (
            <motion.div 
              initial={{ opacity: 0, height: 0, marginTop: 0 }} 
              animate={{ opacity: 1, height: 'auto', marginTop: 24 }} 
              exit={{ opacity: 0, height: 0, marginTop: 0 }}
              className="relative z-20 overflow-hidden"
            >
              <div className="p-4 sm:p-5 bg-rose-500/10 border border-rose-500/20 backdrop-blur-md rounded-2xl flex gap-3 sm:gap-4 items-start shadow-[0_0_30px_rgba(244,63,94,0.1)]">
                <div className="w-8 h-8 rounded-full bg-rose-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 text-rose-400" />
                </div>
                <div>
                  <h4 className="text-rose-400 font-semibold mb-1 text-sm sm:text-base">Extraction Failed</h4>
                  <p className="text-rose-400/80 text-xs sm:text-sm leading-relaxed break-words">{message}</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </motion.div>
  );
}

function SettingsScreen() {
  const [apiKey, setApiKey] = useState('');
  const [modelId, setModelId] = useState('');
  const [baseUrl, setBaseUrl] = useState('');
  const [status, setStatus] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [showApiKey, setShowApiKey] = useState(false);

  useEffect(() => {
    invoke<SettingsConfig>('get_settings').then((s) => {
      setApiKey(s.api_key);
      setModelId(s.model_id);
      setBaseUrl(s.base_url);
      setIsLoading(false);
    }).catch((err) => {
      console.error(err);
      setStatus(`Error loading settings: ${err instanceof Error ? err.message : String(err)}`);
      setIsLoading(false);
    });
  }, []);

  const saveSettings = async () => {
    try {
      await invoke('save_settings', { apiKey, modelId, baseUrl });
      setStatus('Settings saved securely.');
      setTimeout(() => setStatus(''), 3000);
    } catch (err: unknown) {
      setStatus(`Error saving: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="w-full max-w-2xl"
    >
      <div className="bg-[#0d0d14]/60 backdrop-blur-xl border border-white/10 rounded-3xl p-6 sm:p-10 shadow-2xl relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent opacity-50 pointer-events-none" />
        
        <div className="relative z-10">
          <h2 className="text-2xl sm:text-3xl font-bold mb-2 flex items-center gap-3">
            <Settings className="text-blue-400 w-6 h-6 sm:w-8 sm:h-8" /> Configuration
          </h2>
          <p className="text-slate-400 text-sm sm:text-base mb-8">Configure your LLM provider for work package extraction.</p>
          
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <Loader2 className="w-8 h-8 animate-spin mb-4 text-blue-500" />
              <p>Loading settings...</p>
            </div>
          ) : (
            <div className="space-y-5 sm:space-y-6">
              <div>
                <label className="block text-xs sm:text-sm font-medium text-slate-300 mb-2">Base URL</label>
                <input 
                  className="w-full bg-black/40 border border-white/10 focus:border-blue-500 rounded-xl p-3 sm:p-4 text-white placeholder-slate-600 transition-colors outline-none text-sm sm:text-base"
                  placeholder="e.g. https://api.openai.com/v1" 
                  value={baseUrl} 
                  onChange={(e) => setBaseUrl(e.target.value)} 
                />
              </div>
              <div>
                <label className="block text-xs sm:text-sm font-medium text-slate-300 mb-2">Model ID</label>
                <input 
                  className="w-full bg-black/40 border border-white/10 focus:border-blue-500 rounded-xl p-3 sm:p-4 text-white placeholder-slate-600 transition-colors outline-none text-sm sm:text-base"
                  placeholder="e.g. gpt-4o-mini or MiniMax-M3" 
                  value={modelId} 
                  onChange={(e) => setModelId(e.target.value)} 
                />
              </div>
              <div>
                <label className="block text-xs sm:text-sm font-medium text-slate-300 mb-2">API Key</label>
                <div className="relative">
                  <input 
                    className="w-full bg-black/40 border border-white/10 focus:border-blue-500 rounded-xl p-3 sm:p-4 pr-12 text-white placeholder-slate-600 transition-colors outline-none text-sm sm:text-base"
                    type={showApiKey ? "text" : "password"} 
                    placeholder="sk-..." 
                    value={apiKey} 
                    onChange={(e) => setApiKey(e.target.value)} 
                  />
                  <button 
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                  >
                    {showApiKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                <p className="text-xs text-slate-500 mt-2">Stored securely in your local SQLite database.</p>
              </div>
              
              <button 
                onClick={saveSettings}
                className="w-full mt-4 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-white font-medium py-3 sm:py-4 rounded-xl transition-all duration-300 flex items-center justify-center gap-2"
              >
                <Save className="w-5 h-5" /> Save Configuration
              </button>

              <AnimatePresence>
                {status && (
                  <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className={`text-sm text-center font-medium mt-4 ${status.includes('Error') ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {status}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

function HistoryScreen() {
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    invoke<HistoryRecord[]>('get_history')
      .then((res) => {
        setHistory(res);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError(err instanceof Error ? err.message : String(err));
        setIsLoading(false);
      });
  }, []);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="w-full max-w-4xl"
    >
      <div className="bg-[#0d0d14]/60 backdrop-blur-xl border border-white/10 rounded-3xl p-6 sm:p-10 shadow-2xl relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent opacity-50 pointer-events-none" />
        
        <div className="relative z-10">
          <h2 className="text-2xl sm:text-3xl font-bold mb-2 flex items-center gap-3">
            <Clock className="text-emerald-400 w-6 h-6 sm:w-8 sm:h-8" /> Processing History
          </h2>
          <p className="text-slate-400 text-sm sm:text-base mb-8">Review previously generated work packages.</p>

          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 sm:py-16 border-2 border-dashed border-white/5 rounded-2xl bg-black/20 text-slate-400">
              <Loader2 className="w-10 h-10 animate-spin mb-4 text-blue-500" />
              <p>Loading history...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12 sm:py-16 border-2 border-dashed border-rose-500/20 rounded-2xl bg-rose-500/5">
              <AlertCircle className="w-10 h-10 sm:w-12 sm:h-12 text-rose-400 mx-auto mb-4" />
              <p className="text-rose-400 text-sm sm:text-base">Error loading history: {error}</p>
            </div>
          ) : history.length === 0 ? (
            <div className="text-center py-12 sm:py-16 border-2 border-dashed border-white/5 rounded-2xl bg-black/20">
              <History className="w-10 h-10 sm:w-12 sm:h-12 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400 text-sm sm:text-base">No processing history found.</p>
            </div>
          ) : (
            <div className="space-y-3 sm:space-y-4 max-h-[400px] sm:max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
              {history.map((record) => (
                <div key={record.id} className="bg-black/40 border border-white/5 rounded-xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-white/10 transition-colors">
                  <div>
                    <h4 className="font-semibold text-white mb-1 text-sm sm:text-base">{record.project_name}</h4>
                    <p className="text-xs text-slate-500">{record.timestamp}</p>
                  </div>
                  <div className="flex items-center gap-4 sm:gap-6 border-t border-white/5 sm:border-none pt-3 sm:pt-0">
                    <div className="text-left sm:text-right">
                      <p className="text-[10px] sm:text-xs text-slate-500 mb-1">Generated</p>
                      <p className="font-medium text-emerald-400 text-xs sm:text-sm">{record.packages_count} Packages</p>
                    </div>
                    <div className="text-left sm:text-right max-w-[150px] sm:max-w-[200px]">
                      <p className="text-[10px] sm:text-xs text-slate-500 mb-1">Output</p>
                      <p className="text-xs text-blue-300 truncate" title={record.output_path}>{record.output_path}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

function AboutScreen() {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="w-full max-w-4xl"
    >
      <div className="bg-[#0d0d14]/60 backdrop-blur-xl border border-white/10 rounded-3xl p-6 sm:p-10 shadow-2xl relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-white/5 to-transparent opacity-50 pointer-events-none" />
        
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-8">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-emerald-500 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Box className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">Tawreed Workspace</h2>
              <p className="text-slate-400 text-sm">Version 0.0.1</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* How it Works */}
            <div className="bg-black/30 border border-white/5 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-blue-400" /> How it Works
              </h3>
              <ol className="list-decimal list-inside text-sm text-slate-400 space-y-3">
                <li>Configure your LLM <span className="text-blue-300 font-medium">API Key</span> in Settings.</li>
                <li>Upload an Excel/CSV <span className="text-blue-300 font-medium">BOQ Master file</span>.</li>
                <li>Click <span className="text-blue-300 font-medium">Generate</span> to initiate AI extraction.</li>
                <li>The AI automatically breaks the Master BOQ into tailored work packages.</li>
                <li>Review the output files from your <span className="text-blue-300 font-medium">History</span> tab.</li>
              </ol>
            </div>

            {/* Developer Info */}
            <div className="bg-black/30 border border-white/5 rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Code className="w-5 h-5 text-emerald-400" /> Developer
              </h3>
              <div className="space-y-4">
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Created By</p>
                  <p className="text-sm text-slate-300">Kareem Safwat</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Website</p>
                  <a href="https://kareemsafwat.com" target="_blank" rel="noopener noreferrer" className="text-sm text-blue-400 hover:text-blue-300 transition-colors">kareemsafwat.com</a>
                </div>
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mb-1">Designed For</p>
                  <p className="text-sm text-slate-300">Procurement & Tendering Professionals</p>
                </div>
              </div>
            </div>

            {/* Legal */}
            <div className="bg-black/30 border border-white/5 rounded-2xl p-6 md:col-span-2">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Shield className="w-5 h-5 text-slate-400" /> License & Legal
              </h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Tawreed Workspace is an open-source tool designed to streamline work package extraction. This software is provided "as is", without warranty of any kind. The AI models utilized are third-party services and are subject to their respective provider's terms of service and privacy policies.
              </p>
            </div>
          </div>
          
        </div>
      </div>
    </motion.div>
  );
}
