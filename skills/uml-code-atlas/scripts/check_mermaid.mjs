#!/usr/bin/env node
/**
 * Parses every ```mermaid block in a Markdown file and reports which ones fail.
 *
 * Usage:  node check_mermaid.mjs <file.md> [more.md ...]
 * Setup:  cd <this script's directory> && npm i mermaid jsdom
 *
 * Exit code is the number of failing blocks, so it composes with shell logic.
 *
 * Note that parsing is necessary but not sufficient: some constructs parse here
 * and still fail to render in older or restricted Mermaid runtimes. See
 * references/mermaid-pitfalls.md for the list worth avoiding preemptively.
 */
import fs from "node:fs";

let JSDOM;
try {
  ({ JSDOM } = await import("jsdom"));
} catch {
  console.error(
    "Missing dependencies. Run this in the script's directory:\n  npm i mermaid jsdom",
  );
  process.exit(1);
}

const dom = new JSDOM("<!DOCTYPE html><body></body>", { pretendToBeVisual: true });
global.window = dom.window;
global.document = dom.window.document;
Object.defineProperty(global, "navigator", {
  value: dom.window.navigator,
  configurable: true,
});
global.Element = dom.window.Element;
global.SVGElement = dom.window.SVGElement;
global.HTMLElement = dom.window.HTMLElement;
global.Node = dom.window.Node;
global.getComputedStyle = dom.window.getComputedStyle;

let mermaid;
try {
  mermaid = (await import("mermaid")).default;
} catch {
  console.error(
    "Missing dependencies. Run this in the script's directory:\n  npm i mermaid jsdom",
  );
  process.exit(1);
}
mermaid.initialize({ startOnLoad: false, securityLevel: "loose" });

const files = process.argv.slice(2);
if (files.length === 0) {
  console.error("Usage: node check_mermaid.mjs <file.md> [more.md ...]");
  process.exit(1);
}

let failing = 0;
let total = 0;

for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  const blocks = [...text.matchAll(/```mermaid\n([\s\S]*?)```/g)];
  console.log(`\n${file} — ${blocks.length} mermaid block(s)`);
  for (const [i, match] of blocks.entries()) {
    total++;
    const code = match[1];
    const line = text.slice(0, match.index).split("\n").length;
    const first = code.trim().split("\n")[0];
    try {
      await mermaid.parse(code);
      console.log(`  OK   #${i + 1} (line ${line})  ${first}`);
    } catch (error) {
      failing++;
      console.log(`  FAIL #${i + 1} (line ${line})  ${first}`);
      const message = String(error?.message ?? error)
        .split("\n")
        .slice(0, 8)
        .map((l) => `       ${l}`)
        .join("\n");
      console.log(message);
    }
  }
}

console.log(
  failing === 0
    ? `\nALL OK — ${total} block(s) parsed`
    : `\n${failing} of ${total} block(s) failing`,
);
process.exit(failing);
