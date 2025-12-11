import { useState, useEffect, useRef } from 'react';
import { useDebounce } from './useDebounce';

interface Attack {
  type: string;
  severity: "low" | "medium" | "high";
  lines: number[];
  description: string;
  refs: string[] | null;
}

interface AnalysisResult {
  mode: "raw" | "rag";
  id: string;
  solidity: string;
  attacks: Attack[] | null;
}

export function useRealtimeAnalysis(
  code: string,
  mode: "raw" | "rag",
  model: string,
  enabled: boolean = true,
  debounceMs: number = 300
) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [vulnerabilityCount, setVulnerabilityCount] = useState(0);
  const [newVulnerabilities, setNewVulnerabilities] = useState<number[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);
  const previousAttacksRef = useRef<Attack[]>([]);

  const debouncedCode = useDebounce(code, debounceMs);

  useEffect(() => {
    if (!enabled || !debouncedCode || debouncedCode.trim().length < 10) {
      setResult(null);
      setVulnerabilityCount(0);
      return;
    }

    const analyzeCode = async () => {
      // Abort previous request if still pending
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();
      setIsAnalyzing(true);

      try {
        const response = await fetch('http://127.0.0.1:8000/classify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            contract_text: debouncedCode,
            mode,
            model
          }),
          signal: abortControllerRef.current.signal
        });

        if (!response.ok) {
          throw new Error(`Analysis failed: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.success && data.result) {
          const newResult = {
            mode: data.mode,
            id: data.result.id || Date.now().toString(),
            solidity: data.result.solidity || debouncedCode,
            attacks: data.result.attacks || null
          };

          // Detect new vulnerabilities for animation
          const currentAttacks = newResult.attacks || [];
          const newLines: number[] = [];

          currentAttacks.forEach((attack: Attack) => {
            attack.lines.forEach((line: number) => {
              const wasPresent = previousAttacksRef.current.some((prevAttack: Attack) =>
                prevAttack.lines.includes(line) && prevAttack.type === attack.type
              );
              if (!wasPresent) {
                newLines.push(line);
              }
            });
          });

          setNewVulnerabilities(newLines);
          setTimeout(() => setNewVulnerabilities([]), 500); // Clear faster for snappier feel

          previousAttacksRef.current = currentAttacks;
          setResult(newResult);
          setVulnerabilityCount(currentAttacks.length);
        }
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          console.error('Real-time analysis error:', error);
        }
      } finally {
        setIsAnalyzing(false);
      }
    };

    analyzeCode();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [debouncedCode, mode, model, enabled]);

  return {
    isAnalyzing,
    result,
    vulnerabilityCount,
    newVulnerabilities,
    attacks: result?.attacks || null
  };
}