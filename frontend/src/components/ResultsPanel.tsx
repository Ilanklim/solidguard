import { VulnerabilityCard } from "./VulnerabilityCard";
import { Shield, ShieldCheck, ShieldAlert } from "lucide-react";
import { ComplexLoader } from "./SkeletonLoader";

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

interface ResultsPanelProps {
  result: AnalysisResult | null;
  isLoading: boolean;
}

export function ResultsPanel({ result, isLoading }: ResultsPanelProps) {
  // Don't show loader for real-time updates - makes it feel sluggish
  if (isLoading) {
    return <ComplexLoader type="analysis" />;
  }

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-20 text-center">
        <div className="h-20 w-20 rounded-2xl bg-secondary flex items-center justify-center mb-6">
          <Shield className="h-10 w-10 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold text-foreground mb-2">
          No Analysis Yet
        </h3>
        <p className="text-sm text-muted-foreground max-w-xs">
          Paste your Solidity contract and click "Analyze" to scan for vulnerabilities
        </p>
      </div>
    );
  }

  const { attacks } = result;
  const highCount = attacks?.filter((a) => a.severity === "high").length || 0;
  const mediumCount = attacks?.filter((a) => a.severity === "medium").length || 0;
  const lowCount = attacks?.filter((a) => a.severity === "low").length || 0;

  return (
    <div className="h-full flex flex-col">
      {/* Stats Header with smooth transitions */}
      <div className="flex flex-col gap-3 border-b border-border pb-4 mb-4 transition-all duration-200">
        <div className="flex items-center gap-2">
          <div className="transition-all duration-200">
            {attacks && attacks.length > 0 ? (
              <ShieldAlert className="h-5 w-5 text-severity-high" />
            ) : (
              <ShieldCheck className="h-5 w-5 text-primary" />
            )}
          </div>
          <div className="flex-1">
            <h2 className="text-base font-semibold text-foreground transition-all duration-200">
              {attacks && attacks.length > 0
                ? `${attacks.length} ${attacks.length === 1 ? 'Vulnerability' : 'Vulnerabilities'}`
                : "Secure"}
            </h2>
            <p className="text-xs text-muted-foreground uppercase tracking-wider">
              {result.mode}
            </p>
          </div>
        </div>

        {attacks && attacks.length > 0 && (
          <div className="flex items-center gap-2">
            {highCount > 0 && (
              <div className="flex items-center gap-1 text-xs">
                <div className="h-2 w-2 rounded-full bg-severity-high" />
                <span className="text-severity-high font-medium">{highCount}</span>
              </div>
            )}
            {mediumCount > 0 && (
              <div className="flex items-center gap-1 text-xs">
                <div className="h-2 w-2 rounded-full bg-severity-medium" />
                <span className="text-severity-medium font-medium">{mediumCount}</span>
              </div>
            )}
            {lowCount > 0 && (
              <div className="flex items-center gap-1 text-xs">
                <div className="h-2 w-2 rounded-full bg-severity-low" />
                <span className="text-severity-low font-medium">{lowCount}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Vulnerabilities List with smooth transitions */}
      <div className="flex-1 overflow-y-auto space-y-4 code-scroll pr-2 transition-all duration-200">
        {attacks && attacks.length > 0 ? (
          attacks.map((attack, index) => (
            <div key={`${attack.type}-${attack.lines.join(',')}`} className="animate-in fade-in-0 slide-in-from-left-2 duration-200">
              <VulnerabilityCard attack={attack} index={index} />
            </div>
          ))
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <ShieldCheck className="h-16 w-16 text-primary mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              All Clear!
            </h3>
            <p className="text-sm text-muted-foreground max-w-xs">
              No vulnerabilities were detected in this contract
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
