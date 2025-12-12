// src/config/api.ts

const LOCAL_URL = "http://localhost:8000";
const PROD_URL = "https://solidguard.onrender.com";

/**
 * Determine if we're running in a local browser environment.
 * Ensures "window" exists to avoid SSR / Vite build errors.
 */
const isLocal = (() => {
  if (typeof window === "undefined") return false;

  const host = window.location.hostname;

  return (
    host === "localhost" ||
    host === "127.0.0.1" ||
    host.startsWith("192.168.") ||
    host.endsWith(".local")
  );
})();

export const API_BASE_URL = isLocal ? LOCAL_URL : PROD_URL;