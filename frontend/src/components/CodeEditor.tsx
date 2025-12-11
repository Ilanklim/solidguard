import { useRef, useEffect } from "react";
import Editor, { OnMount } from "@monaco-editor/react";
import type * as Monaco from "monaco-editor";
import { registerSolidityLanguage } from "@/lib/solidityLanguage";
import { CodeEditorSkeleton } from "./SkeletonLoader";
import { useToast } from "@/components/ui/use-toast";

interface Attack {
  type: string;
  severity: "low" | "medium" | "high";
  lines: number[];
  description: string;
  refs: string[] | null;
}

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  attacks?: Attack[] | null;
  reset?: boolean;
}

export function CodeEditor({
  value,
  onChange,
  attacks,
  reset,
}: CodeEditorProps) {
  const editorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<typeof Monaco | null>(null);
  const decorationsCollectionRef =
    useRef<Monaco.editor.IEditorDecorationsCollection | null>(null);

  const { toast } = useToast();

  // ---------------------------
  // EDITOR MOUNT
  // ---------------------------
  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    registerSolidityLanguage(monaco);
    monaco.editor.setTheme("solidguard-dark");

    decorationsCollectionRef.current = editor.createDecorationsCollection([]);

    if (attacks) updateDecorations(attacks);
  };

  // ---------------------------
  // MAIN VULNERABILITY DECORATIONS
  // ---------------------------
  const updateDecorations = (attacksData: Attack[] | null) => {
    if (!decorationsCollectionRef.current || !monacoRef.current) return;

    if (!attacksData || attacksData.length === 0) {
      decorationsCollectionRef.current.set([]);
      return;
    }

    const monaco = monacoRef.current;

    const newDecorations = attacksData.flatMap((att) =>
      att.lines.map((line) => ({
        range: new monaco.Range(line, 1, line, 1),
        options: {
          isWholeLine: true,
          className:
            att.severity === "high"
              ? "vulnerability-line-high"
              : att.severity === "medium"
              ? "vulnerability-line-medium"
              : "vulnerability-line-low",
          glyphMarginClassName:
            att.severity === "high"
              ? "vulnerability-glyph-high"
              : att.severity === "medium"
              ? "vulnerability-glyph-medium"
              : "vulnerability-glyph-low",
          glyphMarginHoverMessage: {
            value: `**${att.severity.toUpperCase()}**: ${att.type}\n\n${att.description}`,
          },
        },
      }))
    );

    decorationsCollectionRef.current.set(newDecorations);
  };

  useEffect(() => {
    updateDecorations(attacks ?? null);
  }, [attacks]);

  // ---------------------------
  // RESET DECORATIONS ON GENERATE
  // ---------------------------
  useEffect(() => {
    if (reset && decorationsCollectionRef.current) {
      decorationsCollectionRef.current.set([]);
    }
  }, [reset]);

  // ---------------------------
  // RENDER
  // ---------------------------
  return (
    <div className="relative h-full rounded-lg border border-border overflow-hidden">
      <Editor
        height="100%"
        defaultLanguage="solidity"
        language="solidity"
        value={value}
        onChange={(val) => {
          const text = val || "";
          const lineCount = text.split("\n").length;

          // 300-line limit enforcement
          if (lineCount > 300) {
            if (editorRef.current) {
              editorRef.current.setValue(value);
            }

            toast({
              title: "Too many lines",
              description: "Contracts must be less than 300 lines.",
              variant: "destructive",
            });

            return;
          }

          onChange(text);
        }}
        onMount={handleEditorDidMount}
        theme="solidguard-dark"
        options={{
          fontSize: 14,
          fontFamily: "'JetBrains Mono', monospace",
          lineNumbers: "on",
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          automaticLayout: true,
          padding: { top: 16, bottom: 16 },
          glyphMargin: true,
          folding: true,
          lineDecorationsWidth: 10,
          renderLineHighlight: "line",
          scrollbar: {
            verticalScrollbarSize: 8,
            horizontalScrollbarSize: 8,
          },
          overviewRulerLanes: 0,
          hideCursorInOverviewRuler: true,
          overviewRulerBorder: false,
          contextmenu: true,
          wordWrap: "off",
          tabSize: 4,
          insertSpaces: true,
          cursorBlinking: "smooth",
          cursorSmoothCaretAnimation: "on",
        }}
        loading={<CodeEditorSkeleton />}
      />

      <style>{`
        .vulnerability-line-high {
          background-color: rgba(239, 68, 68, 0.20) !important;
          border-left: 3px solid rgb(239, 68, 68) !important;
        }
        .vulnerability-line-medium {
          background-color: rgba(245, 158, 11, 0.20) !important;
          border-left: 3px solid rgb(245, 158, 11) !important;
        }
        .vulnerability-line-low {
          background-color: rgba(234, 179, 8, 0.15) !important;
          border-left: 3px solid rgb(234, 179, 8) !important;
        }

        .vulnerability-glyph-high {
          background-color: rgb(239, 68, 68);
          border-radius: 50%;
          margin-left: 4px;
        }
        .vulnerability-glyph-medium {
          background-color: rgb(245, 158, 11);
          border-radius: 50%;
          margin-left: 4px;
        }
        .vulnerability-glyph-low {
          background-color: rgb(234, 179, 8);
          border-radius: 50%;
          margin-left: 4px;
        }
      `}</style>
    </div>
  );
}
