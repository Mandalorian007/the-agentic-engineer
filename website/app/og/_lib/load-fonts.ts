import fs from "node:fs/promises";
import path from "node:path";

const FONT_DIR = path.join(process.cwd(), "app/og/_fonts");

type Weight = 400 | 700 | 800;

type FontSpec = {
  name: "Inter";
  data: ArrayBuffer;
  weight: Weight;
  style: "normal";
};

const FILES: Record<Weight, string> = {
  400: "Inter-Regular.woff",
  700: "Inter-Bold.woff",
  800: "Inter-ExtraBold.woff",
};

async function readFont(weight: Weight): Promise<FontSpec> {
  const buf = await fs.readFile(path.join(FONT_DIR, FILES[weight]));
  return {
    name: "Inter",
    data: buf.buffer.slice(
      buf.byteOffset,
      buf.byteOffset + buf.byteLength,
    ) as ArrayBuffer,
    weight,
    style: "normal",
  };
}

export async function loadInter(weights: Weight[] = [400, 700, 800]) {
  return Promise.all(weights.map(readFont));
}
