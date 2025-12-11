import { useState } from "react";

const ATTACK_OPTIONS = [
  { label: "Access Control", value: "access_control" },
  { label: "Arithmetic", value: "arithmetic" },
  { label: "Denial of Service", value: "denial_of_service" },
  { label: "Front Running", value: "front_running" },
  { label: "Initialization", value: "initialization" },
  { label: "Reentrancy", value: "reentrancy" },
  { label: "Signature Verification", value: "signature_verification" },
  { label: "Unchecked Return Value", value: "unchecked_return_value" },
  { label: "Unencrypted Private Data", value: "unencrypted_private_data" },
  { label: "Unprotected Self Destruct", value: "unprotected_self_destruct" },
];

export function GeneratePanel({
  onGenerate,
  isLoading,
}: {
  onGenerate: (attackType: string) => void;
  isLoading: boolean;
}) {
  const [attack, setAttack] = useState("reentrancy");

  return (
    <div className="flex items-center gap-2">

      <select
        value={attack}
        onChange={(e) => setAttack(e.target.value)}
        className="
          px-3 py-2 rounded-lg bg-secondary border border-border 
          hover:border-primary/50 transition-all cursor-pointer
          focus:ring-2 focus:ring-primary/20 text-sm text-foreground
          w-[180px] truncate
        "
      >
        {ATTACK_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

      <button
        onClick={() => onGenerate(attack)}
        disabled={isLoading}
        className="
          px-4 py-2 bg-primary text-primary-foreground rounded-lg
          hover:opacity-90 disabled:opacity-40 transition-all
        "
      >
        {isLoading ? "Generating…" : "Generate Contract"}
      </button>
    </div>
  );
}
