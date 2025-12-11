// src/config/api.ts

const LOCAL_URL = "http://localhost:8000";
const PROD_URL = "https://solidguard.onrender.com";

const isLocal =
  typeof window !== "undefined" &&
  (window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1");

export const API_BASE_URL = isLocal ? LOCAL_URL : PROD_URL;
