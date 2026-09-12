import { InferenceParams } from '../types';

export interface StreamCallbacks {
  onChunk: (content: string, thinking: string, tokensPerSec: number, totalTokens: number) => void;
  onDone: (metrics: {
    eval_count: number;
    eval_duration_ms: number;
    tokens_per_sec: number;
    thinking_duration_s: number;
  }) => void;
  onError: (err: Error) => void;
}

export async function streamOllamaChat(
  model: string,
  messages: Array<{ role: string; content: string; images?: string[] }>,
  params: InferenceParams,
  callbacks: StreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const payload: any = {
    model,
    messages,
    stream: true,
    options: {
      temperature: params.temperature,
      num_ctx: params.numCtx,
      top_p: params.topP,
      top_k: params.topK,
      repeat_penalty: params.repeatPenalty,
    },
    keep_alive: params.keepAlive,
  };

  if (params.seed !== null && params.seed !== undefined) {
    payload.options.seed = Number(params.seed);
  }

  if (params.formatJson) {
    payload.format = 'json';
  }

  if (params.systemPrompt && params.systemPrompt.trim()) {
    // Ensure system prompt is first message or system field
    payload.messages = [
      { role: 'system', content: params.systemPrompt.trim() },
      ...messages.filter(m => m.role !== 'system'),
    ];
  }

  try {
    const response = await fetch('/ollama/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal,
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`Ollama error (${response.status}): ${errText}`);
    }

    if (!response.body) {
      throw new Error('Response body is null');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');

    let accumulatedContent = '';
    let accumulatedThinking = '';
    let isInsideThink = false;
    let thinkStartTime: number | null = null;
    let thinkEndTime: number | null = null;
    let tokenCount = 0;
    const streamStartTime = performance.now();

    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.trim()) continue;

        let parsed: any;
        try {
          parsed = JSON.parse(line);
        } catch {
          continue;
        }

        const delta = parsed.message?.content || '';
        if (delta) {
          tokenCount++;

          // Parse DeepSeek-R1 / Qwen thinking tags
          let remaining = delta;
          while (remaining.length > 0) {
            if (!isInsideThink) {
              const startIdx = remaining.indexOf('<think>');
              if (startIdx !== -1) {
                accumulatedContent += remaining.slice(0, startIdx);
                isInsideThink = true;
                if (!thinkStartTime) thinkStartTime = performance.now();
                remaining = remaining.slice(startIdx + 7);
              } else {
                accumulatedContent += remaining;
                remaining = '';
              }
            } else {
              const endIdx = remaining.indexOf('</think>');
              if (endIdx !== -1) {
                accumulatedThinking += remaining.slice(0, endIdx);
                isInsideThink = false;
                thinkEndTime = performance.now();
                remaining = remaining.slice(endIdx + 8);
              } else {
                accumulatedThinking += remaining;
                remaining = '';
              }
            }
          }

          const elapsedSec = Math.max((performance.now() - streamStartTime) / 1000, 0.05);
          const liveTokensPerSec = Math.round(tokenCount / elapsedSec);

          callbacks.onChunk(accumulatedContent, accumulatedThinking, liveTokensPerSec, tokenCount);
        }

        if (parsed.done) {
          const evalCount = parsed.eval_count || tokenCount;
          const evalDurationMs = parsed.eval_duration ? parsed.eval_duration / 1e6 : (performance.now() - streamStartTime);
          const finalTps = parsed.eval_duration
            ? Math.round((parsed.eval_count / (parsed.eval_duration / 1e9)) * 10) / 10
            : Math.round(tokenCount / Math.max(evalDurationMs / 1000, 0.1));

          let thinkDurationSec = 0;
          if (thinkStartTime) {
            const end = thinkEndTime || performance.now();
            thinkDurationSec = Math.max(Math.round((end - thinkStartTime) / 1000), 1);
          }

          callbacks.onDone({
            eval_count: evalCount,
            eval_duration_ms: Math.round(evalDurationMs),
            tokens_per_sec: finalTps,
            thinking_duration_s: thinkDurationSec,
          });
        }
      }
    }
  } catch (err: any) {
    if (signal?.aborted) {
      // Stream aborted by user
      return;
    }
    callbacks.onError(err);
  }
}
