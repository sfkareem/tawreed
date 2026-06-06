"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileSpreadsheet, Play, CheckCircle, AlertCircle } from 'lucide-react';
import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';

export default function Workspace() {
  const [filePath, setFilePath] = useState('');
  const [status, setStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

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
    if (!filePath) return;
    setStatus('processing');
    try {
      // In reality, API keys and model would be fetched from SQLite/Settings
      const res: string = await invoke('process_boq', {
        filePath,
        baseUrl: 'https://api.minimax.io/v1',
        model: 'MiniMax-M3',
        apiKey: 'sk-cp-ucyiKsDruv0-1ruecr0A-hoHvr9kTQH9WQUTikhd5r_cuAzGnD8aSjF-L2k1rvQ5oBRdqKyfoPSywKqER6dshrlspCmusOzbNhJENwyD40KiIrNE7nWPGwA'
      });
      setMessage(`Successfully sliced to: ${res.split('\\').pop() || res.split('/').pop()}`);
      setStatus('success');
    } catch (err: any) {
      setMessage(err.toString());
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col items-center justify-center p-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl w-full bg-slate-900 border border-slate-800 rounded-3xl p-10 shadow-2xl"
      >
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent mb-4">
            Tawreed Workspace
          </h1>
          <p className="text-slate-400 text-lg">Intelligent BOQ Analysis & Slicing</p>
        </div>

        <div 
          onClick={selectFile}
          className="border-2 border-dashed border-slate-700 hover:border-blue-500 hover:bg-slate-800/50 transition-all rounded-2xl p-12 text-center cursor-pointer mb-8 group"
        >
          <motion.div whileHover={{ scale: 1.05 }} className="flex justify-center mb-4">
            <Upload className="w-12 h-12 text-slate-500 group-hover:text-blue-400 transition-colors" />
          </motion.div>
          {filePath ? (
            <div className="flex flex-col items-center justify-center gap-3 text-blue-400 font-medium">
              <FileSpreadsheet className="w-8 h-8" />
              <span className="truncate max-w-xs">{filePath.split('\\').pop() || filePath.split('/').pop()}</span>
            </div>
          ) : (
            <p className="text-slate-400 font-medium text-lg">Click to select BOQ file</p>
          )}
        </div>

        <button
          onClick={processFile}
          disabled={!filePath || status === 'processing'}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors py-4 rounded-xl font-bold text-lg flex justify-center items-center gap-3"
        >
          {status === 'processing' ? (
            <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
              <Play className="w-6 h-6" />
            </motion.div>
          ) : (
            <Play className="w-6 h-6" />
          )}
          {status === 'processing' ? 'Processing Package...' : 'Generate Packages'}
        </button>

        {status === 'success' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl flex gap-3">
            <CheckCircle className="w-6 h-6 flex-shrink-0" />
            <p>{message}</p>
          </motion.div>
        )}
        
        {status === 'error' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-6 p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl flex gap-3">
            <AlertCircle className="w-6 h-6 flex-shrink-0" />
            <p>{message}</p>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
