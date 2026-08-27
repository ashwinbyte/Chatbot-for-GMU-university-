import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API calls to FastAPI during development
      // So React on 5173 can call FastAPI on 8000 without CORS issues in dev
      "/chat":  "http://localhost:8000",
      "/stats": "http://localhost:8000",
    },
  },
});
