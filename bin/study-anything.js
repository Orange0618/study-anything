#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  installSkill,
  resolveSkillsRoot,
  SUPPORTED_TARGETS,
} from "../lib/installer.js";

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const packageJson = JSON.parse(
  await readFile(path.join(packageRoot, "package.json"), "utf8"),
);

function help() {
  return `Study Anything Skill installer

Usage:
  npx --yes github:Orange0618/study-anything [options]
  # After the npm Registry release:
  npx study-anything@latest [install] [options]

Default:
  Install to ~/.agents/skills/study-anything

Options:
  --target <name>  Install for ${SUPPORTED_TARGETS.join(", ")}
  --project        Install in the current project's skills directory
  --dir <path>     Use a custom skills root; appends /study-anything
  --force          Replace a manual or locally modified install and keep a backup
  --dry-run        Show what would happen without changing files
  -h, --help       Show this help
  -v, --version    Show the package version

Examples:
  npx study-anything@latest
  npx study-anything@latest --target codex
  npx study-anything@latest --target claude --project
  npx study-anything@latest --dir ./my-skills
`;
}

function takeValue(args, index, option) {
  const current = args[index];
  const equalsIndex = current.indexOf("=");
  if (equalsIndex !== -1) {
    const value = current.slice(equalsIndex + 1);
    if (!value) throw new Error(`${option} requires a value`);
    return { value, consumed: 0 };
  }

  const value = args[index + 1];
  if (!value || value.startsWith("-")) {
    throw new Error(`${option} requires a value`);
  }
  return { value, consumed: 1 };
}

function parseArgs(argv) {
  const options = {
    target: "agents",
    project: false,
    force: false,
    dryRun: false,
  };
  let explicitTarget = false;

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === "install" && index === 0) continue;
    if (arg === "--help" || arg === "-h") return { help: true };
    if (arg === "--version" || arg === "-v") return { version: true };
    if (arg === "--project") {
      options.project = true;
      continue;
    }
    if (arg === "--force") {
      options.force = true;
      continue;
    }
    if (arg === "--dry-run") {
      options.dryRun = true;
      continue;
    }
    if (arg === "--target" || arg.startsWith("--target=")) {
      const { value, consumed } = takeValue(argv, index, "--target");
      options.target = value.toLowerCase();
      explicitTarget = true;
      index += consumed;
      continue;
    }
    if (arg === "--dir" || arg.startsWith("--dir=")) {
      const { value, consumed } = takeValue(argv, index, "--dir");
      options.dir = value;
      index += consumed;
      continue;
    }

    throw new Error(`Unknown argument: ${arg}`);
  }

  if (!SUPPORTED_TARGETS.includes(options.target)) {
    throw new Error(
      `Unsupported target: ${options.target}. Choose ${SUPPORTED_TARGETS.join(", ")}.`,
    );
  }
  if (options.dir && (options.project || explicitTarget)) {
    throw new Error("--dir cannot be combined with --project or --target");
  }

  return options;
}

async function main() {
  let parsed;
  try {
    parsed = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(`Error: ${error.message}`);
    console.error("Run with --help to see valid options.");
    process.exitCode = 2;
    return;
  }

  if (parsed.help) {
    console.log(help());
    return;
  }
  if (parsed.version) {
    console.log(packageJson.version);
    return;
  }

  const skillsRoot = resolveSkillsRoot(parsed);

  try {
    const result = await installSkill({
      packageRoot,
      packageVersion: packageJson.version,
      skillsRoot,
      force: parsed.force,
      dryRun: parsed.dryRun,
    });

    const prefix = parsed.dryRun ? "Dry run" : "Success";
    console.log(`${prefix}: Study Anything ${result.action}`);
    console.log(`Target: ${result.destination}`);
    console.log(`Validation: ${result.validation}`);
    if (result.backup) console.log(`Backup: ${result.backup}`);
    if (!parsed.dryRun) {
      console.log("Next: restart your agent, then run Study Anything: Setup <topic>");
    }
  } catch (error) {
    console.error(`Install failed: ${error.message}`);
    if (error.code === "TARGET_EXISTS" || error.code === "LOCAL_CHANGES") {
      console.error("Re-run with --force to replace it while preserving a backup.");
    }
    process.exitCode = 1;
  }
}

await main();
