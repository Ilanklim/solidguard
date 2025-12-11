import { useEffect, useState } from "react";

let externalOpenModal: (() => void) | null = null;

export function OnboardingModal() {
  const [isOpen, setIsOpen] = useState(false);

  // Allow external components to open the modal
  useEffect(() => {
    externalOpenModal = () => setIsOpen(true);
  }, []);

  // Open automatically if user hasn't seen it
  useEffect(() => {
    const hasSeen = localStorage.getItem("solidguard_onboarding_seen");
    if (!hasSeen) {
      setIsOpen(true);
    }
  }, []);

  const closeModal = () => {
    localStorage.setItem("solidguard_onboarding_seen", "true");
    setIsOpen(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fadeIn">
      <div className="bg-card border border-border rounded-xl p-8 w-full max-w-lg shadow-xl animate-scaleIn">

        <h2 className="text-2xl font-semibold mb-4">Welcome to SolidGuard 👋</h2>

        <p className="text-muted-foreground mb-4 text-sm leading-relaxed">
          SolidGuard is an AI-powered smart contract auditor.  
          Paste your Solidity code, choose RAW or RAG mode, select a model, and click <strong>Analyze</strong> to detect vulnerabilities.
        </p>

        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2">How to Use</h3>
          <ul className="list-disc list-inside text-muted-foreground text-sm space-y-1">
            <li>Paste your Solidity contract into the editor.</li>
            <li>Select <strong>RAW</strong> or <strong>RAG</strong> mode.</li>
            <li>Choose a model (GPT-4.1 Mini, GPT-4.1, GPT-5.1).</li>
            <li>Click <strong>Analyze</strong> to scan for vulnerabilities.</li>
            <li>Review color-coded results in the right panel.</li>
          </ul>
        </div>

        <button
          onClick={closeModal}
          className="w-full py-2 mt-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition"
        >
          Got it
        </button>
      </div>
    </div>
  );
}

// This allows external components to trigger the modal
export function openOnboardingModal() {
  if (externalOpenModal) externalOpenModal();
}
