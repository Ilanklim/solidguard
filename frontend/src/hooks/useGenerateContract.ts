import { useState } from "react";
import { API_BASE_URL } from "@/config/api";

interface GeneratedContract {
  metadata: string;     // JSON string returned by backend
  malicious: string;    // Solidity code
}

export function useGenerateContract() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generated, setGenerated] = useState<GeneratedContract | null>(null);

  async function generate(attackType: string, model: string) {
    setIsGenerating(true);
    setGenerated(null);

    try {
      const res = await fetch(`${API_BASE_URL}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          attack_type: attackType,
          model,
        }),
      });

      const json = await res.json();

      if (!res.ok || !json.success) {
        console.error("Generate backend error:", json);
        throw new Error(json.detail || "Generation failed");
      }

      setGenerated({
        metadata: json.metadata,
        malicious: json.malicious,
      });
    } catch (err) {
      console.error("Generation error:", err);
    } finally {
      setIsGenerating(false);
    }
  }

  return { generate, isGenerating, generated };
}
