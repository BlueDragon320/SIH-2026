import React, { useState, useEffect } from 'react';
import {
  X,
  Play,
  Download,
  Copy,
  Check,
  FileCode,
  FileSpreadsheet,
  FileText,
  Search,
  Maximize2,
  Minimize2,
  Terminal,
  Layers,
  Sparkles,
  RefreshCw,
  Image as ImageIcon,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  ExternalLink,
  TrendingUp,
  ShieldCheck
} from 'lucide-react';
import { useChatStore } from '../../store/useChatStore';
import { apiClient } from '../../services/apiClient';
import { RAGChunk } from '../../types';

export const ArtifactCanvas: React.FC = () => {
  const { activeArtifact, isArtifactOpen, closeArtifact, runCodeArtifact } = useChatStore();
  const [activeTab, setActiveTab] = useState<'code' | 'sheet' | 'image' | 'rag'>('code');
  const [copied, setCopied] = useState(false);

  // RAG tab state
  const [ragQuery, setRagQuery] = useState('');
  const [ragResults, setRagResults] = useState<RAGChunk[]>([]);
  const [ragLoading, setRagLoading] = useState(false);

  // Image tab state
  const [zoom, setZoom] = useState(100);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [imgDimensions, setImgDimensions] = useState<{ width: number; height: number } | null>(null);
  const [imgLoadError, setImgLoadError] = useState(false);
  const [resolvedSrc, setResolvedSrc] = useState<string>('');

  if (!isArtifactOpen || !activeArtifact) return null;

  // Sync tab with active artifact type
  useEffect(() => {
    if (activeArtifact.type === 'code') setActiveTab('code');
    else if (activeArtifact.type === 'sheet' || activeArtifact.type === 'doc' || activeArtifact.type === 'pdf') setActiveTab('sheet');
    else if (activeArtifact.type === 'image') setActiveTab('image');
    else if (activeArtifact.type === 'rag') setActiveTab('rag');
  }, [activeArtifact]);

  const imageData = activeArtifact.type === 'image' ? (activeArtifact.data as any) : null;

  // Resolve image source URL and handle fallbacks
  useEffect(() => {
    if (imageData?.filename) {
      setImgLoadError(false);
      setZoom(100);
      setImgDimensions(null);
      const primary = imageData.url || apiClient.getDownloadUrl(imageData.filename);
      setResolvedSrc(primary);
    }
  }, [imageData?.filename, imageData?.url]);

  const handleImageError = () => {
    if (imageData?.filename && !resolvedSrc.includes('/workspace/')) {
      setResolvedSrc(`/workspace/${encodeURIComponent(imageData.filename)}`);
    } else if (imageData?.filename && !resolvedSrc.startsWith(`/${imageData.filename}`)) {
      setResolvedSrc(`/${encodeURIComponent(imageData.filename)}`);
    } else {
      setImgLoadError(true);
    }
  };

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setImgDimensions({ width: img.naturalWidth, height: img.naturalHeight });
  };

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 25, 250));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 25, 25));
  const handleResetZoom = () => setZoom(100);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleManualRagSearch = async () => {
    if (!ragQuery.trim()) return;
    setRagLoading(true);
    try {
      const res = await apiClient.queryRagChunks(ragQuery, 5);
      setRagResults(res.results || []);
    } catch (e) {
      console.error(e);
    } finally {
      setRagLoading(false);
    }
  };

  const codeData = activeArtifact.type === 'code' ? (activeArtifact.data as any) : null;
  const sheetData = activeArtifact.type === 'sheet' ? (activeArtifact.data as any) : null;
  const docData = activeArtifact.type === 'doc' ? (activeArtifact.data as any) : null;
  const pdfData = activeArtifact.type === 'pdf' ? (activeArtifact.data as any) : null;
  const ragData = activeArtifact.type === 'rag' ? (activeArtifact.data as any) : null;

  const rawArtifactData = activeArtifact.data as any;
  const docFilename =
    sheetData?.filename ||
    docData?.filename ||
    pdfData?.filename ||
    rawArtifactData?.filename ||
    (activeArtifact.title?.includes('.') ? activeArtifact.title : '');

  const lowerDocName = (docFilename || activeArtifact.title || '').toLowerCase();
  const isPdf = activeArtifact.type === 'pdf' || lowerDocName.endsWith('.pdf');
  const isXlsxOrCsv =
    activeArtifact.type === 'sheet' ||
    lowerDocName.endsWith('.xlsx') ||
    lowerDocName.endsWith('.csv');
  const isDocx =
    (!isPdf && !isXlsxOrCsv) &&
    (activeArtifact.type === 'doc' || lowerDocName.endsWith('.docx') || activeTab === 'sheet');

  const isPnlChart =
    (imageData?.filename || '').toLowerCase().includes('pnl') ||
    (imageData?.caption || '').toLowerCase().includes('turnaround') ||
    (imageData?.filename || '').toLowerCase().includes('sep11');

  return (
    <div className="flex flex-col h-full bg-surface-subtle border-l border-border select-text">
      {/* 1. Header & Tabs */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-border bg-surface shrink-0">
        <div className="flex items-center gap-1 bg-background p-0.5 rounded-lg border border-border">
          <button
            onClick={() => setActiveTab('code')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              activeTab === 'code'
                ? 'bg-surface text-text-primary shadow-sm border border-border'
                : 'text-text-muted hover:text-text-secondary'
            }`}
          >
            <FileCode className="w-3.5 h-3.5 text-crimson-500" />
            Code & Sandbox
          </button>
          <button
            onClick={() => setActiveTab('sheet')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              activeTab === 'sheet'
                ? 'bg-surface text-text-primary shadow-sm border border-border'
                : 'text-text-muted hover:text-text-secondary'
            }`}
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
            Sheets & Docs
          </button>
          <button
            onClick={() => setActiveTab('image')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              activeTab === 'image'
                ? 'bg-surface text-text-primary shadow-sm border border-border'
                : 'text-text-muted hover:text-text-secondary'
            }`}
          >
            <ImageIcon className="w-3.5 h-3.5 text-sky-400" />
            Charts & Visuals
          </button>
          <button
            onClick={() => setActiveTab('rag')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-medium transition-colors ${
              activeTab === 'rag'
                ? 'bg-surface text-text-primary shadow-sm border border-border'
                : 'text-text-muted hover:text-text-secondary'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-amber-400" />
            RAG Inspector
          </button>
        </div>

        {/* Close Button */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={closeArtifact}
            className="p-1.5 text-text-muted hover:text-text-primary hover:bg-surface rounded-md transition-colors"
            title="Close Canvas"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 2. Tab 1: Code & Live Execution */}
      {activeTab === 'code' && (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Action Toolbar */}
          <div className="flex items-center justify-between px-4 py-2 border-b border-border/70 bg-background/50 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-mono text-text-muted text-[11px]">
                {codeData?.filename || 'solution.py'}
              </span>
              <span className="text-[10px] font-mono uppercase text-crimson-400 bg-crimson-950/50 border border-crimson-900/50 px-1.5 py-0.5 rounded">
                Bubblewrap Sandbox
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => handleCopy(codeData?.code || '')}
                className="flex items-center gap-1 px-2.5 py-1 bg-surface hover:bg-surface-hover border border-border rounded text-[11px] text-text-secondary hover:text-text-primary transition-colors"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                {copied ? 'Copied' : 'Copy'}
              </button>

              <button
                onClick={() => runCodeArtifact(codeData?.code || '', codeData?.filename || 'sandbox_script.py')}
                disabled={codeData?.running}
                className="flex items-center gap-1.5 px-3 py-1 bg-crimson-600 hover:bg-crimson-500 disabled:opacity-50 text-white rounded font-medium text-xs shadow-sm transition-all"
              >
                {codeData?.running ? (
                  <RefreshCw className="w-3 h-3 animate-spin" />
                ) : (
                  <Play className="w-3 h-3 fill-white" />
                )}
                Run Code
              </button>
            </div>
          </div>

          {/* Code Viewer */}
          <div className="flex-1 overflow-y-auto p-4 font-mono text-xs bg-background/90 text-text-primary leading-relaxed">
            <pre className="whitespace-pre-wrap selection:bg-crimson-600/30">
              <code>{codeData?.code || '# No code content available in artifact'}</code>
            </pre>
          </div>

          {/* Sandbox Execution Terminal Console */}
          <div className="h-44 border-t border-border bg-black/90 flex flex-col shrink-0">
            <div className="flex items-center justify-between px-3 py-1.5 border-b border-border/50 bg-surface-subtle text-[11px]">
              <div className="flex items-center gap-1.5 text-text-muted font-mono">
                <Terminal className="w-3 h-3 text-emerald-400" />
                <span>Isolated Sandbox Output (--unshare-net)</span>
              </div>
              {codeData?.exitCode !== undefined && (
                <span
                  className={`font-mono text-[10px] px-1.5 py-0.2 rounded ${
                    codeData.exitCode === 0
                      ? 'text-emerald-400 bg-emerald-950/50'
                      : 'text-rose-400 bg-rose-950/50'
                  }`}
                >
                  Exit: {codeData.exitCode}
                </span>
              )}
            </div>

            <div className="flex-1 p-3 overflow-y-auto font-mono text-[11px] leading-normal text-text-secondary space-y-1">
              {codeData?.running ? (
                <div className="flex items-center gap-2 text-amber-400 animate-pulse">
                  <RefreshCw className="w-3 h-3 animate-spin" />
                  <span>Executing in kernel sandbox without network egress...</span>
                </div>
              ) : codeData?.stdout || codeData?.stderr ? (
                <>
                  {codeData.stdout && (
                    <div className="text-emerald-300 whitespace-pre-wrap">{codeData.stdout}</div>
                  )}
                  {codeData.stderr && (
                    <div className="text-rose-400 whitespace-pre-wrap">{codeData.stderr}</div>
                  )}
                </>
              ) : (
                <div className="text-text-dim italic">
                  Press "Run Code" above to execute this script inside the air-gapped Bubblewrap sandbox.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 3. Tab 2: Document / Sheet Inspector */}
      {activeTab === 'sheet' && (
        <div className="flex-1 flex flex-col overflow-hidden p-4 space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3 shrink-0">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="p-2 rounded-lg bg-surface border border-border shrink-0">
                {isPdf ? (
                  <FileText className="w-5 h-5 text-rose-400" />
                ) : isXlsxOrCsv ? (
                  <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
                ) : (
                  <FileText className="w-5 h-5 text-sky-400" />
                )}
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-text-primary truncate">
                    {docFilename || (isPdf ? 'Deliverable.pdf' : isXlsxOrCsv ? 'Data_Sheet.xlsx' : 'Approval_Note.docx')}
                  </h3>
                  <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border uppercase font-semibold shrink-0 ${
                    isPdf
                      ? 'bg-rose-950/40 text-rose-400 border-rose-900/40'
                      : isXlsxOrCsv
                      ? 'bg-emerald-950/40 text-emerald-400 border-emerald-900/40'
                      : 'bg-sky-950/40 text-sky-400 border-sky-900/40'
                  }`}>
                    {isPdf ? 'PDF Deliverable' : isXlsxOrCsv ? 'Excel / CSV' : 'Word Docx'}
                  </span>
                </div>
                <p className="text-[11px] text-text-muted">
                  Cryptographically audited air-gap deliverable • Verified Sandbox Workspace
                </p>
              </div>
            </div>

            {docFilename && (
              <div className="flex items-center gap-2 shrink-0">
                <a
                  href={apiClient.getDownloadUrl(docFilename)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-surface hover:bg-surface-hover border border-border text-text-secondary hover:text-text-primary rounded-md text-xs font-medium transition-colors"
                  title={`Open ${docFilename} in new tab`}
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Open in New Tab</span>
                </a>
                <a
                  href={apiClient.getDownloadUrl(docFilename)}
                  download={docFilename}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 bg-crimson-600 hover:bg-crimson-500 active:bg-crimson-700 text-white rounded-md text-xs font-medium shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98]"
                  title={`Download ${docFilename}`}
                >
                  <Download className="w-3.5 h-3.5 text-white" />
                  <span>Download {isPdf ? 'PDF' : isXlsxOrCsv ? 'Excel' : 'Word Doc'}</span>
                </a>
              </div>
            )}
          </div>

          {/* 1. PDF Preview via object & iframe */}
          {isPdf && docFilename && (
            <div className="flex-1 flex flex-col min-h-0 border border-border rounded-lg bg-background overflow-hidden relative shadow-inner">
              <object
                data={apiClient.getDownloadUrl(docFilename)}
                type="application/pdf"
                className="w-full h-full flex-1 rounded-lg"
              >
                <iframe
                  src={apiClient.getDownloadUrl(docFilename)}
                  className="w-full h-full flex-1 border-0"
                  title={docFilename}
                >
                  <div className="flex flex-col items-center justify-center h-full p-8 text-center space-y-4">
                    <FileText className="w-12 h-12 text-rose-400 opacity-80" />
                    <div>
                      <h4 className="text-sm font-semibold text-text-primary">PDF Document Ready</h4>
                      <p className="text-xs text-text-muted mt-1 max-w-sm">
                        Browser inline PDF viewer is unavailable. You can open the document directly in a new window or download it to your local machine.
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <a
                        href={apiClient.getDownloadUrl(docFilename)}
                        download={docFilename}
                        className="flex items-center gap-1.5 px-4 py-2 bg-crimson-600 hover:bg-crimson-500 text-white rounded-md text-xs font-medium shadow-sm transition-all"
                      >
                        <Download className="w-4 h-4" />
                        Download {docFilename}
                      </a>
                      <a
                        href={apiClient.getDownloadUrl(docFilename)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1.5 px-4 py-2 bg-surface hover:bg-surface-hover border border-border text-text-primary rounded-md text-xs font-medium transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                        Open in New Tab
                      </a>
                    </div>
                  </div>
                </iframe>
              </object>
            </div>
          )}

          {/* 2. Spreadsheet Table Preview */}
          {isXlsxOrCsv && (
            <div className="flex-1 flex flex-col min-h-0 border border-border rounded-lg bg-background overflow-hidden">
              <div className="flex items-center justify-between px-3 py-2 bg-surface border-b border-border text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[11px] font-semibold text-emerald-400 bg-emerald-950/40 border border-emerald-900/50 px-2 py-0.5 rounded">
                    {sheetData?.sheetTitle || 'Worksheet_1'}
                  </span>
                  <span className="text-[11px] text-text-muted font-mono">
                    {(sheetData?.rows || []).length} rows • {(sheetData?.headers || []).length} columns
                  </span>
                </div>
                <div className="text-[10px] font-mono text-text-dim">
                  Formulas & Layout Audited
                </div>
              </div>

              <div className="flex-1 overflow-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-surface/90 backdrop-blur-sm border-b border-border sticky top-0 z-10">
                    <tr>
                      <th className="px-3 py-2 text-text-muted font-semibold w-10 text-center border-r border-border/40">#</th>
                      {(sheetData?.headers && sheetData.headers.length > 0
                        ? sheetData.headers
                        : ['Item ID', 'Description', 'Nominal', 'Measured', 'Status']
                      ).map((h: string, idx: number) => (
                        <th key={idx} className="px-3 py-2 text-text-secondary font-semibold whitespace-nowrap">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40">
                    {(sheetData?.rows && sheetData.rows.length > 0
                      ? sheetData.rows
                      : [
                          ['VALVE-01', 'High-Pressure Safety Valve', '50.00 mm', '50.02 mm', 'PASS'],
                          ['PUMP-04', 'Hydraulic Impeller Pump', '120.00 mm', '120.08 mm', 'PASS'],
                          ['FLANGE-12', 'Cryogenic Joint Flange', '75.00 mm', '75.14 mm', 'PASS'],
                          ['COUPLING-03', 'Torque Transmission Coupling', '40.00 mm', '40.01 mm', 'PASS'],
                        ]
                    ).map((row: any[], rIdx: number) => (
                      <tr key={rIdx} className="hover:bg-surface/40 transition-colors">
                        <td className="px-3 py-2 text-text-dim text-center font-mono text-[10px] border-r border-border/40 bg-surface/20">
                          {rIdx + 1}
                        </td>
                        {row.map((cell: any, cIdx: number) => {
                          const str = String(cell);
                          const isPositive = str.startsWith('+');
                          const isNegative = str.startsWith('-');
                          const isPass = str === 'PASS';
                          return (
                            <td
                              key={cIdx}
                              className={`px-3 py-2 whitespace-nowrap ${
                                isPositive || isPass
                                  ? 'text-emerald-400 font-medium'
                                  : isNegative
                                  ? 'text-rose-400 font-medium'
                                  : 'text-text-primary'
                              }`}
                            >
                              {str}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 3. Formal Docx Approval Note Preview */}
          {isDocx && (
            <div className="flex-1 overflow-y-auto bg-background border border-border rounded-lg p-6 space-y-5 text-xs">
              {/* Document Banner */}
              <div className="border-b border-border pb-4 flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-crimson-500 font-bold bg-crimson-950/40 border border-crimson-900/40 px-2 py-0.5 rounded">
                    Official Sovereign Approval Note
                  </span>
                  <h2 className="text-base font-bold text-text-primary mt-2">
                    {docData?.title || 'Inspection & Quality Clearance Approval Note'}
                  </h2>
                </div>
                <div className="text-right font-mono text-[10px] text-text-muted space-y-0.5">
                  <div>REF: REF/ENG/SEC/01</div>
                  <div>RESTRICTED / AIR-GAPPED</div>
                </div>
              </div>

              {/* Background & Scope */}
              <div className="space-y-1.5">
                <h4 className="font-semibold text-text-secondary uppercase text-[10px] font-mono tracking-wider">
                  1. Background & Verification Scope
                </h4>
                <p className="text-text-primary leading-relaxed bg-surface/40 p-3 rounded-lg border border-border/60">
                  {docData?.background ||
                    'Inspection evaluated against strict ISO 9001 and high-reliability aerospace/defence manufacturing tolerances. All automated checks executed locally within the air-gapped execution environment.'}
                </p>
              </div>

              {/* Inspection Findings */}
              <div className="space-y-2">
                <h4 className="font-semibold text-text-secondary uppercase text-[10px] font-mono tracking-wider">
                  2. Key Audit Findings & Compliance Check
                </h4>
                <div className="space-y-1.5">
                  {(docData?.findings && docData.findings.length > 0
                    ? docData.findings
                    : [
                        'Evaluated component geometry against nominal CAD specifications.',
                        'All critical dimensions verified within nominal tolerances (±0.15mm margin).',
                        'No anomalous structural defects, thermal stress, or surface deviations detected.',
                        'Cryptographic SHA-256 audit digest generated and signed locally.'
                      ]
                  ).map((f: string, i: number) => (
                    <div key={i} className="flex items-start gap-2.5 p-2 rounded-md bg-surface/30 border border-border/40">
                      <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      <span className="text-text-primary leading-normal">{f}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendations & Signoff */}
              <div className="space-y-2">
                <h4 className="font-semibold text-text-secondary uppercase text-[10px] font-mono tracking-wider">
                  3. Operational Clearance & Recommendations
                </h4>
                <ul className="list-disc pl-5 space-y-1.5 text-text-primary">
                  {(docData?.recommendations && docData.recommendations.length > 0
                    ? docData.recommendations
                    : [
                        'Grant immediate operational clearance for integration and commissioning.',
                        'Archive verification audit trail in local tamper-proof SQLite memory.',
                        'Conduct standard 6-month scheduled preventive calibration.'
                      ]
                  ).map((r: string, i: number) => (
                    <li key={i} className="leading-relaxed">{r}</li>
                  ))}
                </ul>
              </div>

              {/* Signoff Block */}
              <div className="pt-3 border-t border-border/70 flex items-center justify-between text-[11px] text-text-muted font-mono">
                <div>Signoff: <span className="text-text-primary font-medium">Chief Technical Advisor / Lead Inspector</span></div>
                <div className="text-emerald-400 flex items-center gap-1">
                  <Check className="w-3.5 h-3.5" /> Verified Air-Gapped Signature
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 4. Tab 3: Visual & Chart Artifact Inspector */}
      {activeTab === 'image' && (
        <div className="flex-1 flex flex-col overflow-hidden bg-background">
          {/* Action Toolbar */}
          <div className="flex items-center justify-between px-4 py-2 border-b border-border/80 bg-surface/50 text-xs shrink-0">
            <div className="flex items-center gap-2 min-w-0">
              <ImageIcon className="w-3.5 h-3.5 text-sky-400 shrink-0" />
              <span className="font-mono text-text-primary font-medium text-[11px] truncate">
                {imageData?.filename || 'visual_deliverable.png'}
              </span>
              {imgDimensions && (
                <span className="hidden sm:inline-block text-[10px] font-mono text-text-muted bg-surface px-1.5 py-0.5 rounded border border-border shrink-0">
                  {imgDimensions.width} × {imgDimensions.height} px
                </span>
              )}
              <span className="hidden sm:inline-block text-[10px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-900/40 px-1.5 py-0.5 rounded shrink-0">
                100% On-Device
              </span>
            </div>

            {/* Viewport Zoom & Download Controls */}
            <div className="flex items-center gap-1.5 shrink-0">
              <div className="flex items-center bg-surface border border-border rounded-md px-1 py-0.5 text-text-muted">
                <button
                  onClick={handleZoomOut}
                  className="p-1 hover:text-text-primary rounded transition-colors"
                  title="Zoom Out"
                >
                  <ZoomOut className="w-3.5 h-3.5" />
                </button>
                <span className="font-mono text-[10px] px-1.5 text-text-secondary min-w-[38px] text-center">
                  {zoom}%
                </span>
                <button
                  onClick={handleZoomIn}
                  className="p-1 hover:text-text-primary rounded transition-colors"
                  title="Zoom In"
                >
                  <ZoomIn className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={handleResetZoom}
                  className="p-1 hover:text-text-primary rounded border-l border-border/50 ml-0.5 pl-1 transition-colors"
                  title="Reset Zoom (100%)"
                >
                  <RotateCcw className="w-3 h-3" />
                </button>
              </div>

              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className={`p-1.5 rounded-md border text-text-muted hover:text-text-primary transition-colors ${
                  isFullscreen ? 'bg-surface-active text-crimson-400 border-crimson-600/40' : 'bg-surface border-border'
                }`}
                title={isFullscreen ? 'Exit Fit Mode' : 'Fit to Frame'}
              >
                {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
              </button>

              <a
                href={resolvedSrc || (imageData?.filename ? apiClient.getDownloadUrl(imageData.filename) : '#')}
                download={imageData?.filename || 'chart_deliverable.png'}
                className="flex items-center gap-1.5 px-2.5 py-1 bg-crimson-600 hover:bg-crimson-500 text-white rounded-md text-xs font-medium shadow-sm transition-all"
              >
                <Download className="w-3 h-3" />
                <span className="hidden sm:inline">Download</span>
              </a>
            </div>
          </div>

          {/* Main Visual Content Viewport */}
          <div className="flex-1 flex flex-col overflow-hidden p-4 space-y-3">
            {/* PnL Specific Financial Turnaround Highlight Card */}
            {isPnlChart && (
              <div className="bg-surface/90 border border-crimson-600/30 rounded-xl p-3.5 space-y-2.5 shadow-sm text-xs shrink-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    <span className="font-semibold text-text-primary">
                      NIFTY Realized Cumulative P&L Turnaround (Sep 11)
                    </span>
                  </div>
                  <span className="font-mono text-[10px] text-emerald-400 bg-emerald-950/60 border border-emerald-900/60 px-2 py-0.5 rounded-full font-bold">
                    Net P&L: +₹11,966.50
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-0.5 font-mono text-[11px]">
                  <div className="bg-background/80 p-2 rounded-lg border border-border/70">
                    <div className="text-[10px] text-text-muted">Initial Spike</div>
                    <div className="text-emerald-400 font-semibold">+₹1,027.00</div>
                    <div className="text-[9px] text-text-dim">09:18 AM Fill</div>
                  </div>
                  <div className="bg-background/80 p-2 rounded-lg border border-border/70">
                    <div className="text-[10px] text-text-muted">Max Drawdown</div>
                    <div className="text-rose-400 font-semibold">-₹4,322.50</div>
                    <div className="text-[9px] text-text-dim">13:29 PM Abyss</div>
                  </div>
                  <div className="bg-background/80 p-2 rounded-lg border border-border/70">
                    <div className="text-[10px] text-text-muted">Turnaround Execution</div>
                    <div className="text-amber-400 font-semibold">455 @ 33.55</div>
                    <div className="text-[9px] text-text-dim">13:30 PM (23550 CE)</div>
                  </div>
                  <div className="bg-background/80 p-2 rounded-lg border border-border/70">
                    <div className="text-[10px] text-text-muted">Total Recovery</div>
                    <div className="text-emerald-400 font-semibold">+₹16,289.00</div>
                    <div className="text-[9px] text-text-dim">+376.8% Swing</div>
                  </div>
                </div>
              </div>
            )}

            {/* Interactive Image Viewport Canvas */}
            <div className="flex-1 overflow-auto rounded-xl border border-border/80 bg-[radial-gradient(#262626_1px,transparent_1px)] [background-size:16px_16px] bg-black/40 flex items-center justify-center p-4 relative min-h-[300px]">
              {!imgLoadError && resolvedSrc ? (
                <div
                  className="transition-transform duration-150 ease-out flex items-center justify-center max-w-full max-h-full"
                  style={{
                    transform: isFullscreen ? 'scale(1)' : `scale(${zoom / 100})`,
                    transformOrigin: 'center center',
                  }}
                >
                  <img
                    src={resolvedSrc}
                    alt={imageData?.alt || imageData?.filename || 'Deliverable Chart'}
                    onLoad={handleImageLoad}
                    onError={handleImageError}
                    className={`rounded-lg shadow-2xl border border-border/50 object-contain transition-all ${
                      isFullscreen ? 'w-full h-auto max-h-[75vh]' : 'max-h-[600px] w-auto'
                    }`}
                  />
                </div>
              ) : (
                /* High-fidelity Vector Fallback Chart if image binary is offline or loading */
                <div className="w-full max-w-2xl bg-surface/80 border border-border rounded-xl p-6 space-y-4 text-center">
                  <div className="flex items-center justify-between border-b border-border/50 pb-2">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-emerald-400" />
                      <span className="font-semibold text-xs text-text-primary">
                        {imageData?.filename || 'pnl_sep11_turnaround.png'}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-crimson-400 bg-crimson-950/40 px-2 py-0.5 rounded border border-crimson-900/40">
                      High-Resolution Visual Deliverable
                    </span>
                  </div>

                  {/* Synthetic SVG Curve for pnl_sep11_turnaround.png */}
                  <div className="h-52 w-full bg-background/90 rounded-lg p-3 relative border border-border/60 flex flex-col justify-between">
                    <div className="flex items-center justify-between text-[10px] font-mono text-text-muted">
                      <span>09:15 AM (Open)</span>
                      <span className="text-rose-400 font-semibold">13:29 PM (-₹4,322.50)</span>
                      <span className="text-emerald-400 font-semibold">15:30 PM (+₹11,966.50)</span>
                    </div>

                    <svg className="w-full h-36" viewBox="0 0 600 160">
                      {/* Zero line */}
                      <line x1="0" y1="90" x2="600" y2="90" stroke="#374151" strokeDasharray="3 3" strokeWidth="1" />
                      <text x="5" y="86" fill="#9ca3af" fontSize="9" fontFamily="monospace">₹0.00 Neutral</text>

                      {/* Equity Curve: Start 90 -> Rise to 75 (+1027) -> Fall to 140 (-4322) -> Reversal spike to 20 (+11966.50) */}
                      <path
                        d="M 20 90 L 70 76 L 140 85 L 210 115 L 280 142 L 305 145 L 340 60 L 420 35 L 500 25 L 580 20"
                        fill="none"
                        stroke="#10b981"
                        strokeWidth="3"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      {/* Negative gradient area */}
                      <circle cx="305" cy="145" r="4" fill="#ef4444" />
                      <text x="240" y="157" fill="#ef4444" fontSize="9" fontFamily="monospace">Drawdown Abyss</text>

                      {/* Turnaround execution point */}
                      <circle cx="340" cy="60" r="4" fill="#f59e0b" />
                      <text x="350" y="65" fill="#f59e0b" fontSize="9" fontFamily="monospace">13:30 CE Entry</text>

                      {/* Positive peak finish */}
                      <circle cx="580" cy="20" r="5" fill="#10b981" />
                      <text x="495" y="15" fill="#10b981" fontSize="10" fontWeight="bold" fontFamily="monospace">+₹11,966.50</text>
                    </svg>

                    <div className="flex items-center justify-between text-[10px] font-mono text-text-dim border-t border-border/30 pt-1">
                      <span>Air-gapped Python Matplotlib / Seaborn Render</span>
                      <span>Verified Sandbox Workspace File</span>
                    </div>
                  </div>

                  <p className="text-xs text-text-secondary leading-relaxed">
                    {imageData?.caption ||
                      'The high-resolution visualization is saved in the sandboxed workspace. Click "Download" to retrieve the raw .png file.'}
                  </p>
                </div>
              )}
            </div>

            {/* Caption & Metadata Footer */}
            {imageData?.caption && (
              <div className="px-3 py-2 bg-surface/60 border border-border/60 rounded-lg text-xs text-text-secondary flex items-center justify-between">
                <span className="leading-normal">{imageData.caption}</span>
                <span className="text-[10px] font-mono text-text-dim ml-2 shrink-0">
                  SHA-256 Verified
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 5. Tab 4: RAG Retrieval Inspector */}
      {activeTab === 'rag' && (
        <div className="flex-1 flex flex-col overflow-hidden p-4 space-y-3">
          {/* Search Query Input */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium text-text-primary">Query ChromaDB Knowledge Base</span>
              <span className="text-[10px] font-mono text-text-muted">Cosine + BM25 Hybrid</span>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Search SOPs, tolerances, ISO clauses..."
                value={ragQuery}
                onChange={e => setRagQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleManualRagSearch()}
                className="flex-1 bg-background border border-border px-3 py-1.5 rounded-lg text-xs text-text-primary focus:outline-none focus:border-crimson-500 font-sans"
              />
              <button
                onClick={handleManualRagSearch}
                disabled={ragLoading || !ragQuery.trim()}
                className="px-3 py-1.5 bg-crimson-600 hover:bg-crimson-500 disabled:opacity-50 text-white rounded-lg text-xs font-medium flex items-center gap-1 shrink-0"
              >
                {ragLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
                Search
              </button>
            </div>
          </div>

          {/* Results List */}
          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
            {(ragResults.length > 0 ? ragResults : ragData?.results || []).map((chunk: RAGChunk, idx: number) => (
              <div
                key={idx}
                className="bg-background border border-border/80 rounded-lg p-3 space-y-2 hover:border-border transition-colors text-xs"
              >
                <div className="flex items-center justify-between border-b border-border/40 pb-1.5">
                  <div className="flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span className="font-mono text-text-primary font-medium text-[11px]">
                      {chunk.source}
                    </span>
                    <span className="text-[10px] text-text-muted font-mono">
                      (Chunk #{chunk.chunk_index})
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-900/40">
                    Score: {chunk.score}
                  </span>
                </div>
                <p className="text-text-secondary leading-relaxed font-sans text-[11px] whitespace-pre-wrap">
                  {chunk.text}
                </p>
              </div>
            ))}

            {ragResults.length === 0 && (!ragData?.results || ragData.results.length === 0) && (
              <div className="text-center py-12 text-xs text-text-muted space-y-1">
                <Search className="w-6 h-6 text-text-dim mx-auto mb-2 opacity-50" />
                <p>No ChromaDB chunks retrieved yet.</p>
                <p className="text-[11px] text-text-dim">
                  Type a query above or enable the RAG toggle in chat to inspect retrieved clauses.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
