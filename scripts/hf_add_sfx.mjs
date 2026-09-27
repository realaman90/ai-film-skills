#!/usr/bin/env node
// Post-assembly patch for a HyperFrames index.html (idempotent — re-run after every re-assemble).
//   1. <head>: link local fonts / load classic scripts (e.g. the three.js global) after GSAP.
//   2. Mounts SFX <audio> clips on the root composition from a cue file. Scenes stay silent.
//
//   node scripts/hf_add_sfx.mjs --index <project>/index.html --cues sfx_cues.json \
//        [--head-css assets/fonts/fonts.css] [--head-js assets/vendor/three.global.js]
//
// sfx_cues.json:
//   { "kinds": { "stamp": { "src": "assets/sfx/stamp.mp3", "dur": 0.75, "track": 15, "vol": 0.8 }, ... },
//     "cues":  [ ["stamp", 27.88], ["relay", 54.02], ... ] }            // track seconds
// Put cues where the scene builders say their hits land (ask them to report SFX times), not where the
// storyboard guessed. Neighbouring clips of one kind alternate between `track` and `track + 10`, so
// overlapping hits never share a row (lint: duplicate_audio_track).
import { readFileSync, writeFileSync } from "node:fs";

const arg = (name) => {
  const i = process.argv.indexOf(`--${name}`);
  return i > 0 ? process.argv[i + 1] : undefined;
};
const file = arg("index");
if (!file) {
  console.error("usage: hf_add_sfx.mjs --index index.html [--cues cues.json] [--head-css x.css] [--head-js x.js]");
  process.exit(2);
}
let html;
try {
  html = readFileSync(file, "utf8");
} catch (err) {
  console.error(`hf_add_sfx: cannot read ${file}: ${err.message}`);
  process.exit(1);
}

const HEAD_START = "<!-- hf-add-sfx:head -->";
const HEAD_END = "<!-- /hf-add-sfx:head -->";
const headLines = [];
if (arg("head-css")) headLines.push(`    <link rel="stylesheet" href="${arg("head-css")}">`);
if (arg("head-js")) headLines.push(`    <script src="${arg("head-js")}"></script>`);
if (headLines.length) {
  const block = [HEAD_START, ...headLines, `    ${HEAD_END}`].join("\n");
  html = html.includes(HEAD_START)
    ? html.replace(new RegExp(`${HEAD_START}[\\s\\S]*?${HEAD_END}`), block.trimStart())
    : html.replace("</head>", `    ${block}\n  </head>`);
}

const cuesPath = arg("cues");
let count = 0;
if (cuesPath) {
  let spec;
  try {
    spec = JSON.parse(readFileSync(cuesPath, "utf8"));
  } catch (err) {
    console.error(`hf_add_sfx: cannot read cues ${cuesPath}: ${err.message}`);
    process.exit(1);
  }
  const seen = {};
  const lines = spec.cues.map(([kind, t], i) => {
    const k = spec.kinds[kind];
    if (!k) {
      console.error(`hf_add_sfx: cue ${i} uses unknown kind "${kind}"`);
      process.exit(1);
    }
    const n = (seen[kind] = (seen[kind] ?? -1) + 1);
    const track = k.track + (n % 2) * 10;
    return `      <audio id="sfx-${String(i).padStart(2, "0")}-${kind}" src="${k.src}" data-start="${t}" data-duration="${k.dur}" data-track-index="${track}" data-volume="${k.vol}"></audio>`;
  });
  count = lines.length;
  const S = "<!-- hf-add-sfx:cues -->";
  const E = "<!-- /hf-add-sfx:cues -->";
  const block = [S, ...lines, `      ${E}`].join("\n");
  if (html.includes(S)) {
    html = html.replace(new RegExp(`${S}[\\s\\S]*?${E}`), block.trimStart());
  } else {
    // after the music bed if there is one, else before the root composition closes
    const bgm = html.indexOf('id="el-bgm"');
    const at = bgm >= 0 ? html.indexOf("</audio>", bgm) + "</audio>".length : html.lastIndexOf("</div>");
    html = `${html.slice(0, at)}\n      ${block}${html.slice(at)}`;
  }
}

writeFileSync(file, html);
console.log(`hf_add_sfx: patched ${file} (${headLines.length} head line(s), ${count} SFX cue(s))`);
