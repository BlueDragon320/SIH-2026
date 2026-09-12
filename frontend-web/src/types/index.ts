export type Role = 'user' | 'assistant' | 'system';

export interface Attachment {
  id: string;
  name: string;
  size: number;
  type: string;
  path?: string;
  url?: string;
}

export interface CodeArtifact {
  code: string;
  language: string;
  filename?: string;
  stdout?: string;
  stderr?: string;
  exitCode?: number;
  running?: boolean;
}

export interface SheetArtifact {
  filename: string;
  sheetTitle?: string;
  headers: string[];
  rows: (string | number)[][];
  summary?: Record<string, string>;
}

export interface DocArtifact {
  filename: string;
  title: string;
  background?: string;
  findings?: string[];
  recommendations?: string[];
  url?: string;
}

export interface PdfArtifact {
  filename: string;
  title?: string;
  url?: string;
  totalPages?: number;
}

export interface ImageArtifact {
  filename: string;
  url?: string;
  alt?: string;
  caption?: string;
  width?: number;
  height?: number;
}

export interface RAGChunk {
  source: string;
  chunk_index: number;
  text: string;
  score: number;
  metadata?: Record<string, any>;
}

export interface RAGArtifact {
  query: string;
  results: RAGChunk[];
}

export type ArtifactType = 'code' | 'sheet' | 'doc' | 'rag' | 'image' | 'pdf';

export interface Artifact {
  id: string;
  type: ArtifactType;
  title: string;
  timestamp: string;
  data: CodeArtifact | SheetArtifact | DocArtifact | RAGArtifact | ImageArtifact | PdfArtifact;
}

export interface StepRecord {
  step_number: number;
  phase: string;
  description: string;
  tool_name?: string;
  tool_input?: any;
  tool_output?: any;
  status: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED' | 'RETRY';
  timestamp: string;
}

export interface Message {
  id: string;
  role: Role;
  content: string;
  thinking?: string;
  thinkingDurationSeconds?: number;
  model?: string;
  taskType?: string;
  tokensPerSecond?: number;
  totalTokens?: number;
  evalDurationMs?: number;
  timestamp: string;
  attachments?: Attachment[];
  artifacts?: Artifact[];
  steps?: StepRecord[];
}

export interface Session {
  id: string;
  title: string;
  pinned?: boolean;
  createdAt: string;
  updatedAt: string;
  modelOverride?: string | null;
  ragEnabled?: boolean;
  messages: Message[];
}

export interface InferenceParams {
  systemPrompt: string;
  temperature: number;
  numCtx: number;
  topP: number;
  topK: number;
  repeatPenalty: number;
  seed: number | null;
  formatJson: boolean;
  keepAlive: string;
}

export interface HardwareGPU {
  available: boolean;
  name: string;
  vram_total_mb: number;
  vram_used_mb: number;
  vram_free_mb: number;
  gpu_util_percent: number;
  temperature_c: number;
}

export interface HardwareRAM {
  total_mb: number;
  used_mb: number;
  percent: number;
}

export interface HardwareStatus {
  gpu: HardwareGPU;
  cpu_percent: number;
  ram: HardwareRAM;
  loaded_models: string[];
  timestamp: string;
}

export interface NetworkStatus {
  airgap_status: string;
  external_egress_rate_bps: number;
  external_ingress_rate_bps?: number;
  verified_zero_egress: boolean;
  active_connections_count: number;
}

export interface ModelOption {
  name: string;
  ollama_tag: string;
  vram_gb: number;
  capabilities: string[];
  is_installed: boolean;
  is_resident?: boolean;
  description: string;
}
