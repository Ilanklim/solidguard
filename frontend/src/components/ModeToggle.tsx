import { cn } from "@/lib/utils";
import { Info } from "lucide-react";

interface ModeToggleProps {
  mode: "raw" | "rag";
  onModeChange: (mode: "raw" | "rag") => void;
}

export function ModeToggle({ mode, onModeChange }: ModeToggleProps) {
  return (
    <div className="inline-flex items-center rounded-lg bg-secondary p-1 gap-1">
      <button
        onClick={() => onModeChange("raw")}
        className={cn(
          "px-4 py-2 rounded-md text-sm font-medium transition-all relative group",
          mode === "raw"
            ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
            : "text-muted-foreground hover:text-foreground"
        )}
        title="RAW: Direct AI analysis without additional context"
      >
        RAW
      </button>
      <button
        onClick={() => onModeChange("rag")}
        className={cn(
          "px-4 py-2 rounded-md text-sm font-medium transition-all relative group",
          mode === "rag"
            ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
            : "text-muted-foreground hover:text-foreground"
        )}
        title="RAG: AI analysis enhanced with vulnerability database"
      >
        RAG
      </button>
    </div>
  );
}
