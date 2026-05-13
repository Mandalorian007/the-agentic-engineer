import fs from "node:fs/promises";
import path from "node:path";

let cached: string | null = null;

export async function loadLogoDataUri(): Promise<string> {
  if (cached) return cached;
  const buf = await fs.readFile(
    path.join(process.cwd(), "app/og/_assets/logo.png"),
  );
  cached = `data:image/png;base64,${buf.toString("base64")}`;
  return cached;
}
