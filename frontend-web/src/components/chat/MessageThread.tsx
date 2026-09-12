import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeKatex from 'rehype-katex';
import {
  Copy,
  Check,
  RotateCcw,
  Sparkles,
  ChevronDown,
  ChevronRight,
  Play,
  FileCode,
  FileSpreadsheet,
  FileText,
  Clock,
  Zap,
  ExternalLink,
  ArrowDown,
  Image as ImageIcon,
  Download,
} from 'lucide-react';
import { Message, Artifact } from '../../types';
import { useChatStore } from '../../store/useChatStore';

interface MessageThreadProps {
  messages: Message[];
}

export const MessageThread: React.FC<MessageThreadProps> = ({ messages }) => {
  const {
    openArtifact,
    regenerateLastMessage,
    runCodeArtifact,
    isStreaming,
    activeSessionId,
  } = useChatStore();

  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const [isUserScrolledUp, setIsUserScrolledUp] = useState(false);
  const isUserScrolledUpRef = useRef(false);
  const prevMessagesCountRef = useRef(messages.length);

  // Smart check if the viewport is near bottom
  const checkIfAtBottom = useCallback(() => {
    const container = containerRef.current;
    if (!container) return true;
    const threshold = 120; // px margin of error from bottom
    const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
    return distanceFromBottom <= threshold;
  }, []);

  // Handle scroll events with smart detection of user reading history
  const handleScroll = useCallback(() => {
    const atBottom = checkIfAtBottom();
    const userScrolledUp = !atBottom;
    isUserScrolledUpRef.current = userScrolledUp;
    setIsUserScrolledUp(userScrolledUp);
  }, [checkIfAtBottom]);

  // Scroll to bottom trigger
  const scrollToBottom = useCallback((smooth = false) => {
    isUserScrolledUpRef.current = false;
    setIsUserScrolledUp(false);
    const container = containerRef.current;
    if (!container) return;

    if (smooth) {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: 'smooth',
      });
    } else {
      container.scrollTop = container.scrollHeight;
    }
  }, []);

  // When switching active session, reset scroll state and jump immediately to bottom
  useEffect(() => {
    isUserScrolledUpRef.current = false;
    setIsUserScrolledUp(false);
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [activeSessionId]);

  // When a new message is appended (e.g. user sent a prompt)
  useEffect(() => {
    if (messages.length > prevMessagesCountRef.current) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage?.role === 'user') {
        scrollToBottom(true);
      }
    }
    prevMessagesCountRef.current = messages.length;
  }, [messages.length, scrollToBottom]);

  // Track the content and reasoning of the last message for streaming auto-scroll
  const lastMessage = messages[messages.length - 1];
  const lastContent = lastMessage?.content || '';
  const lastThinking = lastMessage?.thinking || '';

  // Auto-scroll during message generation / token streaming
  useEffect(() => {
    // If the user deliberately scrolled up to review previous content, do not disrupt them
    if (isUserScrolledUpRef.current) return;

    const frameId = requestAnimationFrame(() => {
      const container = containerRef.current;
      if (!container) return;

      if (isStreaming) {
        // High-frequency token streaming: direct scrollTop pinned to bottom avoids jumpiness and animation cancellation
        container.scrollTop = container.scrollHeight;
      } else {
        // Normal completion or turn additions: smooth glide
        container.scrollTo({
          top: container.scrollHeight,
          behavior: 'smooth',
        });
      }
    });

    return () => cancelAnimationFrame(frameId);
  }, [messages.length, lastContent, lastThinking, isStreaming]);

  // ResizeObserver to track layout changes (math rendering, code blocks, accordion expansion)
  useEffect(() => {
    const container = containerRef.current;
    if (!container || typeof ResizeObserver === 'undefined') return;

    const observer = new ResizeObserver(() => {
      if (!isUserScrolledUpRef.current && container) {
        if (isStreaming) {
          container.scrollTop = container.scrollHeight;
        }
      }
    });

    observer.observe(container);
    return () => observer.disconnect();
  }, [isStreaming]);

  return (
    <div className="relative flex-1 flex flex-col min-h-0 overflow-hidden">
      {/* Scrollable Message Container */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-4 sm:px-8 py-6 space-y-6 max-w-4xl mx-auto w-full scroll-smooth"
      >
        {messages.map((msg, index) => (
          <MessageItem
            key={msg.id || index}
            message={msg}
            isLast={index === messages.length - 1}
            isGenerating={isStreaming && index === messages.length - 1}
            onRegenerate={regenerateLastMessage}
            onOpenArtifact={openArtifact}
            onRunCode={runCodeArtifact}
          />
        ))}
        {/* Anchor point at the thread bottom */}
        <div ref={bottomRef} className="h-px w-full pointer-events-none" />
      </div>

      {/* Floating Smart "Scroll to Bottom" Pill when User Scrolled Up */}
      {isUserScrolledUp && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 pointer-events-none animate-fade-in">
          <button
            type="button"
            onClick={() => scrollToBottom(true)}
            className="pointer-events-auto flex items-center gap-2 px-3.5 py-1.5 bg-surface/95 hover:bg-surface border border-crimson-600/50 hover:border-crimson-500 text-text-primary text-xs font-medium rounded-full shadow-2xl backdrop-blur-md transition-all hover:scale-105 active:scale-95 group"
          >
            <ArrowDown className="w-3.5 h-3.5 text-crimson-500 group-hover:translate-y-0.5 transition-transform" />
            <span>Scroll to latest</span>
            {isStreaming && (
              <span className="flex h-2 w-2 relative ml-0.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-crimson-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-crimson-500"></span>
              </span>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

interface MessageItemProps {
  message: Message;
  isLast: boolean;
  isGenerating?: boolean;
  onRegenerate: () => void;
  onOpenArtifact: (artifact: Artifact) => void;
  onRunCode: (code: string, filename?: string) => void;
}

const MessageItem: React.FC<MessageItemProps> = ({
  message,
  isLast,
  isGenerating,
  onRegenerate,
  onOpenArtifact,
  onRunCode,
}) => {
  const [copied, setCopied] = useState(false);
  const [showThinking, setShowThinking] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error('Failed to copy text', e);
    }
  };

  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end animate-fade-in">
        <div className="max-w-2xl bg-surface border border-border/80 text-text-primary px-4 py-3 rounded-2xl rounded-tr-sm shadow-sm space-y-2 text-xs sm:text-sm">
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>

          {/* Attachment Chips */}
          {message.attachments && message.attachments.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {message.attachments.map(att => (
                <span
                  key={att.id}
                  className="inline-flex items-center gap-1 bg-background/80 border border-border/80 px-2 py-0.5 rounded text-[11px] font-mono text-text-secondary"
                >
                  <FileText className="w-3 h-3 text-crimson-400" />
                  <span className="truncate max-w-[140px]">{att.name}</span>
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-3 animate-fade-in text-left">
      {/* Model & Meta Indicator */}
      <div className="flex items-center gap-2 text-[11px] text-text-muted">
        <span className="w-2 h-2 rounded-full bg-crimson-500"></span>
        <span className="font-semibold text-text-secondary">{message.model || 'Local Model'}</span>
        {message.tokensPerSecond && (
          <span className="font-mono text-[10px] text-text-dim">
            • {message.tokensPerSecond} t/s
          </span>
        )}
      </div>

      {/* Expandable Reasoning / Thinking Accordion (DeepSeek-R1) */}
      {message.thinking && (
        <div className="border border-border/70 rounded-lg overflow-hidden bg-surface-subtle/60 text-xs">
          <button
            type="button"
            onClick={() => setShowThinking(!showThinking)}
            className="w-full flex items-center justify-between px-3 py-2 bg-surface/50 hover:bg-surface text-text-secondary transition-colors"
          >
            <div className="flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 text-crimson-500" />
              <span className="font-medium font-mono text-[11px]">
                Thought Process {message.thinkingDurationSeconds ? `(${message.thinkingDurationSeconds}s)` : ''}
              </span>
            </div>
            {showThinking ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>

          {showThinking && (
            <div className="p-3 border-t border-border/40 font-mono text-[11px] text-text-muted leading-relaxed whitespace-pre-wrap max-h-60 overflow-y-auto bg-background/40">
              {message.thinking}
            </div>
          )}
        </div>
      )}

      {/* Main Markdown Content with Enhanced Code Block Syntax Highlighting */}
      <div className="markdown-body text-text-primary text-xs sm:text-sm leading-relaxed space-y-2">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight, rehypeKatex]}
          components={{
            code({ node, inline, className, children, ...props }: any) {
              const match = /language-(\w+)/.exec(className || '');
              const lang = match ? match[1] : '';

              // Recursively extract pure text from HAST node or React children tree
              const extractText = (item: any): string => {
                if (!item) return '';
                if (typeof item === 'string') return item;
                if (typeof item === 'number') return String(item);
                if (Array.isArray(item)) return item.map(extractText).join('');
                if (item?.type === 'text' && typeof item?.value === 'string') return item.value;
                if (item?.value && typeof item?.value === 'string') return item.value;
                if (item?.props && item?.props?.children) return extractText(item.props.children);
                if (item?.children && Array.isArray(item?.children)) return item.children.map(extractText).join('');
                return '';
              };

              const codeFromNode = node ? extractText(node) : '';
              const codeFromChildren = extractText(children);
              const rawCode = (codeFromNode && !codeFromNode.includes('[object Object]'))
                ? codeFromNode
                : codeFromChildren;
              const codeString = rawCode.replace(/\n$/, '');
              const isMultiline = codeString.includes('\n');
              const isBlockCode = !inline && (lang || isMultiline || className?.includes('hljs'));

              if (isBlockCode) {
                return (
                  <CodeBlock
                    language={lang || 'text'}
                    code={codeString}
                    className={className}
                    onRunCode={onRunCode}
                    onOpenArtifact={onOpenArtifact}
                  >
                    {children}
                  </CodeBlock>
                );
              }

              return (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
            img({ src, alt, ...props }: any) {
              const fname = (src || '').split('/').pop() || 'image.png';
              const resolvedSrc = src?.startsWith('http') || src?.startsWith('/')
                ? src
                : `/api/v1/workspace/download/${encodeURIComponent(src || '')}`;
              return (
                <div className="my-3 rounded-lg overflow-hidden border border-border bg-surface-subtle group relative max-w-lg">
                  <img
                    src={resolvedSrc}
                    alt={alt || fname}
                    className="max-h-[380px] w-auto mx-auto object-contain cursor-pointer hover:opacity-95 transition-opacity"
                    onClick={() =>
                      onOpenArtifact({
                        id: `art_img_${Date.now()}`,
                        type: 'image',
                        title: fname,
                        timestamp: new Date().toISOString(),
                        data: {
                          filename: fname,
                          url: resolvedSrc,
                          alt: alt || fname,
                          caption: alt || fname,
                        },
                      })
                    }
                    {...props}
                  />
                  <div className="flex items-center justify-between px-3 py-1.5 bg-surface/80 border-t border-border/50 text-[11px] text-text-muted">
                    <span className="font-mono truncate">{alt || fname}</span>
                    <button
                      type="button"
                      onClick={() =>
                        onOpenArtifact({
                          id: `art_img_${Date.now()}`,
                          type: 'image',
                          title: fname,
                          timestamp: new Date().toISOString(),
                          data: {
                            filename: fname,
                            url: resolvedSrc,
                            alt: alt || fname,
                            caption: alt || fname,
                          },
                        })
                      }
                      className="text-crimson-400 hover:text-crimson-300 flex items-center gap-1 font-medium"
                    >
                      <span>Open Canvas</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              );
            },
            a({ href, children, ...props }: any) {
              const isDownload = href?.includes('/workspace/download/') || href?.match(/\.(pdf|docx|xlsx|csv|png|jpg|jpeg|webp)$/i);
              return (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 font-medium text-crimson-400 hover:text-crimson-300 underline underline-offset-2 transition-colors"
                  {...props}
                >
                  {children}
                  {isDownload && <Download className="w-3 h-3 ml-0.5 inline opacity-80" />}
                </a>
              );
            },
          }}
        >
          {message.content}
        </ReactMarkdown>
      </div>

      {/* Deliverable / Artifact Quick Buttons */}
      {message.artifacts && message.artifacts.length > 0 && (
        <div className="flex flex-wrap gap-2 pt-1">
          {message.artifacts.map(art => (
            <button
              key={art.id}
              type="button"
              onClick={() => onOpenArtifact(art)}
              className="flex items-center gap-2 px-3 py-1.5 bg-surface hover:bg-surface-hover border border-crimson-600/40 rounded-lg text-xs text-text-primary shadow-sm group transition-all"
            >
              {art.type === 'code' && <FileCode className="w-3.5 h-3.5 text-crimson-500" />}
              {art.type === 'sheet' && <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />}
              {art.type === 'doc' && <FileText className="w-3.5 h-3.5 text-amber-400" />}
              {art.type === 'pdf' && <FileText className="w-3.5 h-3.5 text-rose-400" />}
              {art.type === 'image' && <ImageIcon className="w-3.5 h-3.5 text-sky-400" />}
              <span className="font-medium font-mono text-[11px]">{art.title}</span>
              <ExternalLink className="w-3 h-3 text-text-muted group-hover:text-crimson-400 transition-colors" />
            </button>
          ))}
        </div>
      )}

      {/* Action Toolbar */}
      <div className="flex items-center gap-2 pt-1 text-text-muted text-xs min-h-[28px]">
        {isGenerating ? (
          <div className="flex items-center gap-2 text-crimson-400 py-1 px-2.5 rounded-md bg-crimson-500/10 border border-crimson-500/20 text-xs font-medium animate-pulse">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-crimson-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-crimson-500"></span>
            </span>
            <span>Generating response...</span>
          </div>
        ) : (
          <>
            <button
              type="button"
              onClick={handleCopy}
              className={`flex items-center gap-1.5 py-1 px-2 rounded-md transition-colors ${
                copied
                  ? 'text-emerald-400 bg-emerald-950/40 border border-emerald-900/50'
                  : 'hover:text-text-primary hover:bg-surface'
              }`}
              title="Copy response"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              <span className="font-medium text-[11px]">{copied ? 'Copied' : 'Copy'}</span>
            </button>

            {isLast && (
              <button
                type="button"
                onClick={onRegenerate}
                className="flex items-center gap-1.5 hover:text-text-primary py-1 px-2 rounded-md hover:bg-surface transition-colors"
                title="Regenerate turn"
              >
                <RotateCcw className="w-3 h-3" />
                <span className="font-medium text-[11px]">Regenerate</span>
              </button>
            )}
          </>
        )}

        {message.totalTokens && !isGenerating && (
          <span className="font-mono text-[10px] text-text-dim ml-auto">
            {message.totalTokens} tokens {message.evalDurationMs ? `• ${(message.evalDurationMs / 1000).toFixed(1)}s` : ''}
          </span>
        )}
      </div>
    </div>
  );
};

interface CodeBlockProps {
  language: string;
  code: string;
  className?: string;
  children: React.ReactNode;
  onRunCode: (code: string, filename?: string) => void;
  onOpenArtifact: (artifact: Artifact) => void;
}

const CodeBlock: React.FC<CodeBlockProps> = ({
  language,
  code,
  className,
  children,
  onRunCode,
  onOpenArtifact,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code to clipboard', err);
    }
  };

  const getExtension = (lang: string): string => {
    const l = lang.toLowerCase();
    switch (l) {
      case 'python':
      case 'py':
        return 'py';
      case 'javascript':
      case 'js':
        return 'js';
      case 'typescript':
      case 'ts':
        return 'ts';
      case 'bash':
      case 'sh':
      case 'shell':
        return 'sh';
      case 'json':
        return 'json';
      case 'html':
        return 'html';
      case 'css':
        return 'css';
      default:
        return 'txt';
    }
  };

  const handleRun = () => {
    const ext = getExtension(language);
    const filename = `script_${Date.now().toString().slice(-4)}.${ext}`;
    onRunCode(code, filename);
    onOpenArtifact({
      id: `art_code_${Date.now()}`,
      type: 'code',
      title: `${language.toUpperCase()} Script`,
      timestamp: new Date().toISOString(),
      data: {
        code,
        language: language || 'text',
        filename,
      },
    });
  };

  return (
    <div className="my-3.5 rounded-xl overflow-hidden border border-border/80 bg-[#121217] shadow-xl font-mono text-xs">
      {/* Code Header Bar */}
      <div className="flex items-center justify-between px-3.5 py-2 bg-[#181820] border-b border-border/70 text-[11px] select-none">
        <div className="flex items-center gap-2">
          <FileCode className="w-3.5 h-3.5 text-crimson-400" />
          <span className="uppercase text-crimson-400 font-bold tracking-wider font-mono text-[10px]">
            {language || 'code'}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          {/* Run in Sandbox Button */}
          <button
            type="button"
            onClick={handleRun}
            className="flex items-center gap-1.5 px-2.5 py-1 bg-crimson-600/90 hover:bg-crimson-600 active:bg-crimson-700 text-white rounded-md text-[10px] font-semibold transition-all hover:scale-[1.02] active:scale-[0.98] shadow-sm"
            title="Execute in isolated air-gapped bubblewrap sandbox"
          >
            <Play className="w-2.5 h-2.5 fill-white" />
            <span>Run Sandbox</span>
          </button>

          {/* Crisp Copy Button with Feedback */}
          <button
            type="button"
            onClick={handleCopyCode}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-[10px] font-medium border transition-all ${
              copied
                ? 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300'
                : 'bg-surface/80 hover:bg-surface border-border/70 text-text-secondary hover:text-text-primary'
            }`}
            title="Copy code snippet to clipboard"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3 text-emerald-400 animate-scale-in" />
                <span className="font-semibold text-emerald-400">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3 text-text-muted group-hover:text-text-primary" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Code Viewer Body */}
      <div className="p-4 overflow-x-auto text-[12.5px] leading-relaxed bg-[#111115] text-[#abb2bf] selection:bg-crimson-500/30">
        <pre className="m-0 p-0 bg-transparent">
          <code className={className}>{children}</code>
        </pre>
      </div>
    </div>
  );
};
