import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  ShieldAlert,
  RotateCcw,
  RefreshCw,
  Terminal,
  ChevronDown,
  ChevronRight,
  Copy,
  Check,
  Trash2,
  AlertTriangle,
} from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode | ((props: { error: Error; resetErrorBoundary: () => void }) => ReactNode);
  onReset?: () => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  showDetails: boolean;
  copied: boolean;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
      copied: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo });
    // Log to console for air-gapped terminal auditing
    console.error('[Air-Gap ErrorBoundary Caught Error]:', error, errorInfo);
  }

  handleReset = (): void => {
    this.props.onReset?.();
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
      copied: false,
    });
  };

  handleReload = (): void => {
    window.location.reload();
  };

  handleHardReset = (): void => {
    if (window.confirm('Clear local workbench sessions and restore default state? This will clear locally cached chats.')) {
      try {
        localStorage.removeItem('workbench_sessions_v2');
      } catch (e) {
        console.error('Failed to clear localStorage', e);
      }
      window.location.reload();
    }
  };

  handleCopyDiagnostics = async (): Promise<void> => {
    const { error, errorInfo } = this.state;
    const diagnosticReport = [
      '=== Workbench Air-Gapped Diagnostic Report ===',
      `Timestamp: ${new Date().toISOString()}`,
      `Error: ${error?.name || 'Error'}: ${error?.message || 'Unknown error'}`,
      '\n--- Error Stack ---',
      error?.stack || 'No error stack available',
      '\n--- Component Stack ---',
      errorInfo?.componentStack || 'No component stack available',
    ].join('\n');

    try {
      await navigator.clipboard.writeText(diagnosticReport);
      this.setState({ copied: true });
      setTimeout(() => {
        this.setState({ copied: false });
      }, 2000);
    } catch (err) {
      console.error('Failed to copy diagnostics', err);
    }
  };

  toggleDetails = (): void => {
    this.setState(prev => ({ showDetails: !prev.showDetails }));
  };

  render(): ReactNode {
    const { hasError, error, errorInfo, showDetails, copied } = this.state;
    const { children, fallback } = this.props;

    if (!hasError) {
      return children;
    }

    if (fallback) {
      if (typeof fallback === 'function') {
        return fallback({
          error: error || new Error('Unknown rendering error'),
          resetErrorBoundary: this.handleReset,
        });
      }
      return fallback;
    }

    return (
      <div className="min-h-screen w-screen bg-background text-text-primary flex items-center justify-center p-4 sm:p-8 select-text">
        <div className="w-full max-w-2xl bg-surface/90 border border-crimson-600/40 rounded-2xl shadow-2xl p-6 sm:p-8 backdrop-blur-xl space-y-6 relative overflow-hidden">
          {/* Subtle Ambient Crimson Glow */}
          <div className="absolute -top-24 -right-24 w-60 h-60 bg-crimson-600/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -left-24 w-60 h-60 bg-crimson-600/5 rounded-full blur-3xl pointer-events-none" />

          {/* Header Banner */}
          <div className="flex items-start gap-4">
            <div className="p-3 bg-crimson-950/60 border border-crimson-600/40 rounded-xl text-crimson-500 shadow-sm shrink-0">
              <ShieldAlert className="w-7 h-7" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono uppercase tracking-widest text-crimson-400 font-bold bg-crimson-950/80 px-2 py-0.5 rounded border border-crimson-900/50">
                  Air-Gap Safety Intercept
                </span>
                <span className="text-xs text-text-dim font-mono">• Isolated</span>
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-text-primary tracking-tight">
                System Anomaly Intercepted
              </h1>
              <p className="text-xs sm:text-sm text-text-secondary leading-relaxed">
                A runtime rendering exception was caught by the air-gapped workbench boundary. The execution context has been safely halted to prevent corruption.
              </p>
            </div>
          </div>

          {/* Error Message Box */}
          <div className="p-4 bg-background/90 border border-border/80 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-xs text-text-muted font-mono">
              <span className="flex items-center gap-1.5 text-crimson-400 font-medium">
                <AlertTriangle className="w-3.5 h-3.5" />
                {error?.name || 'Exception'}
              </span>
              <span>Local Execution</span>
            </div>
            <p className="font-mono text-xs sm:text-[13px] text-rose-300 break-words leading-relaxed">
              {error?.message || 'An unknown rendering error occurred.'}
            </p>
          </div>

          {/* Collapsible Diagnostics / Stack Trace */}
          <div className="border border-border/60 rounded-xl overflow-hidden bg-background/50 text-xs">
            <button
              onClick={this.toggleDetails}
              type="button"
              className="w-full flex items-center justify-between px-4 py-2.5 bg-surface/60 hover:bg-surface text-text-secondary transition-colors"
            >
              <div className="flex items-center gap-2 font-mono text-[11px]">
                <Terminal className="w-3.5 h-3.5 text-text-muted" />
                <span>Technical Diagnostics & Stack Trace</span>
              </div>
              {showDetails ? (
                <ChevronDown className="w-4 h-4 text-text-muted" />
              ) : (
                <ChevronRight className="w-4 h-4 text-text-muted" />
              )}
            </button>

            {showDetails && (
              <div className="p-4 border-t border-border/40 space-y-3 bg-black/60">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[11px] text-text-dim">Stack Trace (Air-Gapped Audit)</span>
                  <button
                    onClick={this.handleCopyDiagnostics}
                    type="button"
                    className="flex items-center gap-1.5 px-2.5 py-1 bg-surface hover:bg-surface-hover border border-border rounded text-[11px] font-mono text-text-secondary hover:text-text-primary transition-colors"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-400" />
                        <span className="text-emerald-400">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copy Report</span>
                      </>
                    )}
                  </button>
                </div>
                <div className="p-3 bg-black/80 rounded-lg border border-border/40 font-mono text-[11px] text-text-muted max-h-56 overflow-y-auto overflow-x-auto whitespace-pre leading-relaxed">
                  {error?.stack || 'No stack trace available.'}
                  {errorInfo?.componentStack && (
                    <>
                      {'\n\nComponent Hierarchy:'}
                      {errorInfo.componentStack}
                    </>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Recovery Actions Bar */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2">
            <button
              onClick={this.handleHardReset}
              type="button"
              className="flex items-center justify-center gap-1.5 px-3 py-2 bg-surface hover:bg-surface-hover border border-border hover:border-rose-900/40 text-text-muted hover:text-rose-400 rounded-xl text-xs transition-colors order-last sm:order-first"
              title="Clear cached session history from browser localStorage"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear Storage Cache</span>
            </button>

            <div className="flex items-center gap-2">
              <button
                onClick={this.handleReload}
                type="button"
                className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-4 py-2 bg-surface hover:bg-surface-hover border border-border text-text-primary rounded-xl text-xs font-medium transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Reload Page</span>
              </button>

              <button
                onClick={this.handleReset}
                type="button"
                className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-5 py-2 bg-crimson-600 hover:bg-crimson-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-crimson-900/30 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Recover Session</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
