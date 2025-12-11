import { useState, useEffect } from "react";
import { Toaster } from "@/components/ui/toaster";

import { OnboardingModal } from "@/components/OnboardingModal";
import { TopToolbar } from "@/components/TopToolbar";

import { CodeEditor } from "@/components/CodeEditor";
import { ResultsPanel } from "@/components/ResultsPanel";
import { CodeEditorSkeleton } from "@/components/SkeletonLoader";

import { useAnalyzeContract } from "@/hooks/useAnalyzeContract";
import { useGenerateContract } from "@/hooks/useGenerateContract";
import { useRealtimeAnalysis } from "@/hooks/useRealtimeAnalysis";

export default function App() {
  // ============================================================================
  //                                EDITOR STATE
  // ============================================================================
  const [code, setCode] = useState<string>(
    `// Paste your Solidity contract here
    pragma solidity ^0.8.0;

    contract Example {
        uint public value;
        function setValue(uint v) public { value = v; }
    }`
  );

  const [mode, setMode] = useState<"raw" | "rag">("raw");
  const [model, setModel] = useState("gpt-4.1-mini");
  const [realtimeEnabled, setRealtimeEnabled] = useState(false);

  // ============================================================================
  //                                   API HOOKS
  // ============================================================================
  const { analyze, isLoading, result, clearResult } = useAnalyzeContract();
  const { generate, isGenerating, generated } = useGenerateContract();

  const {
    isAnalyzing: isRealtimeAnalyzing,
    result: realtimeResult,
    attacks: realtimeAttacks,
  } = useRealtimeAnalysis(code, mode, model, realtimeEnabled, 300);

  // ============================================================================
  //              UPDATE EDITOR WHEN MALICIOUS CONTRACT IS GENERATED
  // ============================================================================
  useEffect(() => {
    if (generated?.malicious) {
      clearResult();
      setCode(generated.malicious);
    }
  }, [generated, clearResult]);

  // ============================================================================
  //                              DISPLAYED RESULTS
  // ============================================================================
  const displayResult =
    realtimeEnabled && realtimeResult ? realtimeResult : result;

  const displayAttacks: any[] =
    (realtimeEnabled ? realtimeAttacks : displayResult?.attacks) || [];

  // ============================================================================
  //                                      UI
  // ============================================================================
  return (
    <div className="flex flex-col h-screen bg-background text-foreground">
      
      {/* Onboarding Popup */}
      <OnboardingModal />

      {/* Top Toolbar */}
      <TopToolbar
        model={model}
        setModel={setModel}
        mode={mode}
        setMode={setMode}
        realtimeEnabled={realtimeEnabled}
        setRealtimeEnabled={setRealtimeEnabled}
        isRealtimeAnalyzing={isRealtimeAnalyzing}
        isGenerating={isGenerating}
        generate={(attack) => generate(attack, model)}
        analyze={() => analyze(code, mode, model)}
        isLoading={isLoading}
      />

      {/* ========================================================================= */}
      {/*                                MAIN LAYOUT                                */}
      {/* ========================================================================= */}
      <div className="flex flex-1 overflow-hidden">

        {/* Code Editor */}
        <div className="w-2/3 p-4 border-r border-border overflow-auto">
          {isGenerating ? (
            <CodeEditorSkeleton />
          ) : (
            <CodeEditor
              value={code}
              onChange={setCode}
              attacks={displayAttacks}
            />
          )}
        </div>

        {/* Results Panel */}
        <div className="w-1/3 p-4 overflow-auto">
          <ResultsPanel
            isLoading={!realtimeEnabled && isLoading}
            result={displayResult}
          />
        </div>
      </div>

      {/* Toast Notifications */}
      <Toaster />
    </div>
  );
}
