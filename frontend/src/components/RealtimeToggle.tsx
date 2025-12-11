import { Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Props {
  enabled: boolean;
  onChange: (enabled: boolean) => void;
  isAnalyzing?: boolean;
}

export function RealtimeToggle({ enabled, onChange, isAnalyzing }: Props) {
  return (
    <button
      onClick={() => onChange(!enabled)}
      className={cn(
        "flex items-center gap-2 px-3 py-1.5 rounded-md transition-all duration-200",
        "hover:bg-muted/50",
        enabled && "text-primary"
      )}
    >
      {/* Icon with quick pulse when enabled */}
      <div className="relative">
        <Zap className={cn(
          "h-3.5 w-3.5 transition-all duration-200",
          enabled ? "text-primary" : "text-muted-foreground"
        )} />
        {enabled && (
          <Zap className="h-3.5 w-3.5 absolute inset-0 text-primary animate-quick-pulse" />
        )}
      </div>

      {/* Label */}
      <span className={cn(
        "text-xs font-medium transition-colors duration-200",
        enabled ? "text-foreground" : "text-muted-foreground"
      )}>
        Real-time
      </span>

      {/* Status indicator */}
      {enabled && (
        <div className="relative flex items-center">
          <div className={cn(
            "w-1.5 h-1.5 rounded-full transition-all duration-200",
            isAnalyzing ? "bg-primary animate-pulse" : "bg-green-500"
          )} />
          {isAnalyzing && (
            <div className="w-1.5 h-1.5 rounded-full bg-primary absolute inset-0 animate-quick-pulse" />
          )}
        </div>
      )}
    </button>
  );
}