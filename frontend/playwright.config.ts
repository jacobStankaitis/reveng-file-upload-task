import { defineConfig } from "@playwright/test";
import * as dotenv from "dotenv";

dotenv.config({ path: ".env" });

export default defineConfig({
  testDir: "src/e2e",
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL,
    headless: true,
    trace: "on",
  },
});
