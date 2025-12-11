import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'card' | 'code' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  animate?: boolean;
  style?: React.CSSProperties; 
}

export function Skeleton({
  className,
  variant = 'text',
  width,
  height,
  animate = true,
}: SkeletonProps) {
  const variantClasses = {
    text: 'h-4 rounded',
    card: 'rounded-lg',
    code: 'rounded font-mono',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  };

  return (
    <div
      className={cn(
        'bg-muted/50',
        animate && 'animate-pulse relative overflow-hidden',
        variantClasses[variant],
        className
      )}
      style={{ width, height }}
    >
      {animate && (
        <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-primary/10 to-transparent" />
      )}
    </div>
  );
}

// Complex Analysis Skeleton
export function AnalysisSkeleton() {
  return (
    <div className="space-y-6 p-4">
      {/* Header Skeleton */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Skeleton variant="circular" className="h-10 w-10" />
          <div className="space-y-2">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-3 w-24 opacity-70" />
          </div>
        </div>
        <Skeleton className="h-8 w-20 rounded-full" />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-card/50 rounded-lg p-3 space-y-2">
            <Skeleton className="h-3 w-20 opacity-60" />
            <Skeleton className="h-6 w-16" />
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((j) => (
                <Skeleton key={j} className="h-2 w-2 rounded-full" />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Vulnerability Cards Skeleton */}
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-card/30 backdrop-blur rounded-lg p-4 border border-border/50">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <Skeleton variant="circular" className="h-8 w-8" />
                <div className="space-y-1">
                  <Skeleton className="h-5 w-28" />
                  <Skeleton className="h-3 w-20 opacity-60" />
                </div>
              </div>
              <Skeleton className="h-6 w-16 rounded-full" />
            </div>

            {/* Code snippet skeleton */}
            <div className="bg-background/50 rounded-md p-3 space-y-2">
              {[
                ["h-4 w-8", "h-4 w-full"],
                ["h-4 w-8", "h-4 w-3/4"],
                ["h-4 w-8", "h-4 w-5/6"]
              ].map((row, idx) => (
                <div key={idx} className="flex gap-3">
                  <Skeleton className={`${row[0]} opacity-50`} />
                  <Skeleton className={row[1]} />
                </div>
              ))}
            </div>

            {/* Action buttons skeleton */}
            <div className="flex gap-2 mt-3">
              <Skeleton className="h-8 w-24 rounded" />
              <Skeleton className="h-8 w-20 rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Code Editor Skeleton (unchanged)
export function CodeEditorSkeleton() {
  // Simulate Solidity code patterns for realistic loading state
  const codePatterns = [
    { indent: 0, width: 45, color: 'text-primary/20', comment: false }, // pragma
    { indent: 0, width: 0, color: '', comment: false }, // empty line
    { indent: 0, width: 35, color: 'text-cyan-500/20', comment: true }, // comment
    { indent: 0, width: 55, color: 'text-primary/20', comment: false }, // contract declaration
    { indent: 0, width: 0, color: '', comment: false }, // empty line
    { indent: 1, width: 40, color: 'text-cyan-500/20', comment: false }, // state variable
    { indent: 1, width: 35, color: 'text-cyan-500/20', comment: false }, // state variable
    { indent: 0, width: 0, color: '', comment: false }, // empty line
    { indent: 1, width: 50, color: 'text-yellow-500/20', comment: false }, // function signature
    { indent: 2, width: 30, color: 'text-orange-500/20', comment: false }, // require statement
    { indent: 2, width: 45, color: 'text-pink-500/20', comment: false }, // assignment
    { indent: 2, width: 35, color: 'text-indigo-500/20', comment: false }, // emit event
    { indent: 1, width: 5, color: 'text-muted-foreground/20', comment: false }, // closing brace
    { indent: 0, width: 0, color: '', comment: false }, // empty line
    { indent: 1, width: 55, color: 'text-yellow-500/20', comment: false }, // function signature
    { indent: 2, width: 40, color: 'text-red-500/20', comment: false }, // if statement
    { indent: 3, width: 35, color: 'text-green-500/20', comment: false }, // return statement
    { indent: 2, width: 5, color: 'text-muted-foreground/20', comment: false }, // closing brace
    { indent: 1, width: 5, color: 'text-muted-foreground/20', comment: false }, // closing brace
    { indent: 0, width: 5, color: 'text-muted-foreground/20', comment: false }, // closing brace
  ];

  return (
    <div className="relative h-full rounded-lg border border-border overflow-hidden bg-code-bg">
      {/* Monaco-like header bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border/50 bg-card">
        <div className="flex items-center gap-2">
          <Skeleton className="h-4 w-32 opacity-50 bg-muted" />
        </div>
        <div className="flex items-center gap-2">
          <Skeleton className="h-4 w-20 opacity-40 bg-muted" />
          <Skeleton className="h-4 w-16 opacity-40 bg-muted" />
        </div>
      </div>

      {/* Code editor content with gutter */}
      <div className="flex h-[calc(100%-40px)]">
        {/* Line numbers gutter */}
        <div className="w-12 bg-code-bg border-r border-border/30 flex flex-col py-4">
          {codePatterns.map((_, i) => (
            <div
              key={i}
              className="h-5 flex items-center justify-end pr-2 text-muted-foreground/50"
              style={{ opacity: 1 }}
            >
              <span className="text-xs font-mono animate-pulse">{i + 1}</span>
            </div>
          ))}
        </div>

        {/* Code content area */}
        <div className="flex-1 p-4 space-y-0 font-mono text-sm overflow-hidden">
          {codePatterns.map((pattern, i) => (
            <div
              key={i}
              className="h-5 flex items-center"
              style={{ opacity: 1 }}
            >
              {pattern.width > 0 && (
                <div className="relative">
                  {/* Code skeleton with syntax coloring hint */}
                  <Skeleton
                    className={cn(
                      "h-4",
                      pattern.comment && "opacity-40",
                      pattern.color
                    )}
                    style={{ width: `${pattern.width * 8}px` }}
                  />
                </div>
              )}
            </div>
          ))}

          {/* Scanning line effect */}
          <div
            className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent"
            style={{
              animation: 'scan 3s ease-in-out infinite',
              top: '0'
            }}
          />
        </div>

        {/* Minimap skeleton */}
        <div className="w-20 bg-code-bg border-l border-border/30 p-2">
          <div className="space-y-0.5 opacity-30">
            {codePatterns.map((pattern, i) => (
              <div key={i} className="h-1">
                {pattern.width > 0 && (
                  <Skeleton
                    className="h-full"
                    style={{ width: `${pattern.width}%` }}
                    animate={false}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Add animations */}
      <style>{`
        @keyframes fadeIn {
          to { opacity: 1; }
        }
        @keyframes slideIn {
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        @keyframes blink {
          50% { opacity: 0; }
        }
        @keyframes scan {
          0%, 100% {
            top: 0;
            opacity: 0;
          }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% {
            top: 100%;
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
}


// Generate Panel Skeleton
export function GenerateSkeleton() {
  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center gap-3">
        <Skeleton variant="circular" className="h-12 w-12" />
        <div className="space-y-2">
          <Skeleton className="h-5 w-36" />
          <Skeleton className="h-3 w-48 opacity-70" />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-card/30 rounded-lg p-3 flex items-center gap-3">
            <Skeleton variant="circular" className="h-8 w-8" />
            <Skeleton className="h-4 w-24" />
          </div>
        ))}
      </div>

      <Skeleton className="h-10 w-full rounded-lg" />
    </div>
  );
}

// Complex Loading State Component
export function ComplexLoader({ type = 'analysis' }: { type?: 'analysis' | 'generate' | 'code' }) {
  return (
    <div className="relative">

      {/* REMOVE GRADIENT BACKGROUND */}
      {/* <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-accent/5 to-primary/5 animate-gradient-shift rounded-lg" /> */}

      {/* Clean background */}
      <div className="absolute inset-0 bg-code-bg rounded-lg" />

      {/* Content */}
      <div className="relative z-10">
        {type === 'analysis' && <AnalysisSkeleton />}
        {type === 'generate' && <GenerateSkeleton />}
        {type === 'code' && <CodeEditorSkeleton />}
      </div>
    </div>
  );
}