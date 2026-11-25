// News-image entry: copies entry.png beside this file to /output/entry.png.
// Node 22, standard library only, no network, deterministic.
import { copyFileSync, existsSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const botDir = process.env.MAKEFUN_BOT_DIR ?? '.';
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const src = join(botDir, 'entry.png');

if (!existsSync(src)) {
  throw new Error('entry.png is missing next to main.ts; nothing to copy.');
}

mkdirSync(outDir, { recursive: true });
const dest = join(outDir, 'entry.png');
copyFileSync(src, dest);

const srcSize = statSync(src).size;
const destSize = statSync(dest).size;
if (destSize !== srcSize) {
  throw new Error(`entry.png write failed: wrote ${destSize} bytes, expected ${srcSize}.`);
}
