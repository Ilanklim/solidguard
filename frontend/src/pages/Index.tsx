import { useState } from "react";
import { CodeEditor } from "@/components/CodeEditor";
import { ModeToggle } from "@/components/ModeToggle";
import { ResultsPanel } from "@/components/ResultsPanel";
import { Button } from "@/components/ui/button";
import { Shield, Zap, Github } from "lucide-react";
import { toast } from "sonner";

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

// Demo contract for testing
const DEMO_CONTRACT = `// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableBank {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 _amount) public {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        
        // Vulnerable to reentrancy attack
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");
        
        balances[msg.sender] -= _amount;
    }

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}`;

// Mock analysis result for demo
const mockAnalysis: AnalysisResult = {
  mode: "raw",
  id: "user_input_contract",
  solidity: "solidity",
  attacks: [
    {
      type: "reentrancy",
      severity: "high",
      lines: [14, 15, 16, 17],
      description:
        "The withdraw function sends ETH before updating the balance, allowing attackers to recursively call withdraw and drain all funds.",
      refs: null,
    },
    {
      type: "unchecked_return_value",
      severity: "medium",
      lines: [15],
      description:
        "While the return value is checked, the pattern of external call before state update creates a critical vulnerability window.",
      refs: null,
    },
  ],
};

export default function Index() {
  const [code, setCode] = useState(DEMO_CONTRACT);
  const [mode, setMode] = useState<"raw" | "rag">("raw");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const attacks = result?.attacks || null;

  const handleAnalyze = async () => {
    if (!code.trim()) {
      toast.error("Please paste a Solidity contract first");
      return;
    }

    setIsLoading(true);
    setResult(null);

    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Return mock result (in production, this would call your AI backend)
    const analysisResult = {
      ...mockAnalysis,
      mode,
      attacks: mockAnalysis.attacks?.map((attack) => ({
        ...attack,
        refs: mode === "rag" ? ["CVE-2016-1000", "SWC-107"] : null,
      })) || null,
    };

    setResult(analysisResult);
    setIsLoading(false);

    if (analysisResult.attacks && analysisResult.attacks.length > 0) {
      toast.warning(`Found ${analysisResult.attacks.length} vulnerabilities`);
    } else {
      toast.success("No vulnerabilities detected");
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center glow-effect">
              <Shield className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-foreground">SolidGuard</h1>
              <p className="text-xs text-muted-foreground">Smart Contract Analyzer</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <ModeToggle mode={mode} onModeChange={setMode} />
            <Button variant="ghost" size="icon" asChild>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub"
              >
                <Github className="h-5 w-5" />
              </a>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-[1.5fr_1fr] gap-6 h-[calc(100vh-8rem)]">
          {/* Code Editor Panel */}
          <div className="flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-sm font-semibold text-foreground">Contract Input</h2>
                <p className="text-xs text-muted-foreground">
                  Paste your Solidity code below
                </p>
              </div>
              <Button
                variant="glow"
                size="lg"
                onClick={handleAnalyze}
                disabled={isLoading}
                className="gap-2"
              >
                <Zap className="h-4 w-4" />
                {isLoading ? "Analyzing..." : "Analyze"}
              </Button>
            </div>
            <div className="flex-1 min-h-0">
              <CodeEditor
                value={code}
                onChange={setCode}
                attacks={attacks}
              />
            </div>
          </div>

          {/* Results Panel */}
          <div className="flex flex-col rounded-xl border border-border bg-card p-6 card-shadow">
            <ResultsPanel result={result} isLoading={isLoading} />
          </div>
        </div>
      </main>
    </div>
  );
}
