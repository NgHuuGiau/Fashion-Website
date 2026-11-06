import { config } from "dotenv";
import { resolve } from "path";

export default async function globalSetup() {
  // Load .env.test file
  const envPath = resolve(__dirname, ".env.test");
  config({ path: envPath });
  
  // Verify required env vars
  if (!process.env.BASE_URL) {
    throw new Error("BASE_URL is not set in .env.test");
  }
  
  console.log(`Global setup: BASE_URL = ${process.env.BASE_URL}`);
}