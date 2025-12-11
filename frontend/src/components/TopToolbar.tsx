import { openOnboardingModal } from "@/components/OnboardingModal";
import { ModeToggle } from "@/components/ModeToggle";
import { GeneratePanel } from "@/components/GeneratePanel";
import { useEffect } from "react";

export function TopToolbar({
  model,
  setModel,
  mode,
  setMode,
  isGenerating,
  generate,
  analyze,
  isLoading,
}) {

  return (
    <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-card">
      {/* ------------------------------------------------ */}
      {/*                     LEFT SIDE                    */}
      {/* ------------------------------------------------ */}
      <div className="flex items-center gap-6">
        {/* Branding Icon */}
        <img
          src="/contract-agreement.png"
          alt="SolidGuard"
          className="w-6 h-6 opacity-80"
        />

        {/* ---------------------------- */}
        {/*         Model Select         */}
        {/* ---------------------------- */}
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="
            px-3 py-2 rounded-lg bg-secondary border border-border 
            hover:border-primary/50 transition-colors cursor-pointer 
            focus:ring-2 focus:ring-primary/20 text-sm text-foreground
            w-[130px] truncate
          "
        >
          <option value="gpt-4.1-mini">GPT-4.1 Mini</option>
          <option value="gpt-4.1">GPT-4.1</option>
          <option value="gpt-5.1">GPT-5.1</option>
        </select>

        {/* RAW / RAG Toggle */}
        <ModeToggle mode={mode} onModeChange={setMode} />

        {/* Divider */}
        <div className="w-px h-6 bg-border/60" />

      </div>

      {/* ------------------------------------------------ */}
      {/*                    RIGHT SIDE                    */}
      {/* ------------------------------------------------ */}
      <div className="flex items-center gap-4">
        {/* Generate Contract */}
        <GeneratePanel onGenerate={generate} isLoading={isGenerating} />

        {/* Analyze Button */}
        <button
          onClick={analyze}
          disabled={isLoading}
          className="
            px-4 py-2 bg-primary text-primary-foreground rounded-lg 
            hover:opacity-90 disabled:opacity-40 transition-all
          "
        >
          {isLoading ? "Analyzing…" : "Analyze"}
        </button>

        {/* ------------------------------------------------ */}
        {/*              Help Button (?)                     */}
        {/* ------------------------------------------------ */}
        <button
          onClick={openOnboardingModal}
          className="
            w-7 h-7 flex items-center justify-center rounded-full 
            bg-secondary text-foreground/80 
            hover:bg-secondary/80 hover:text-foreground 
            transition text-sm font-semibold
          "
        >
          ?
        </button>
      </div>
    </div>
  );
}
