import { useState, useCallback } from "react";

export function useAnalyzeContract() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  async function analyze(
    contractText: string,
    mode: "raw" | "rag",
    model: string
  ) {
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contract_text: contractText,
          mode,
          model,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        console.error("Classify backend error:", errorData);
        throw new Error(errorData.detail || "Backend error");
      }

      const data = await res.json();
      console.log("API Response:", data);

      const resultToSet = {
        mode: data.mode,
        id: "user_input",
        solidity: contractText,
        attacks: data.result.attacks || [],
      };
      console.log("Setting result:", resultToSet);
      setResult(resultToSet);
    } catch (err) {
      console.error("Analyze error caught:", err);
      console.error("Full error details:", err);
      // Don't set result to null, keep previous result
      // setResult(null);
    } finally {
      setIsLoading(false);
    }
  }

  // Function to clear results (useful when generating new contracts)
  const clearResult = useCallback(() => {
    console.log("Clearing result");
    setResult(null);
  }, []);

  return { analyze, isLoading, result, clearResult };
}
