import { createHash, randomBytes } from "node:crypto";
import { readFile, writeFile, mkdir, cp, lstat, readdir, rename, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

export const SKILL_NAME = "study-anything";
export const SUPPORTED_TARGETS = ["agents", "codex", "claude", "cursor", "gemini"];

const TARGET_DIRECTORIES = {
  agents: ".agents",
  codex: ".codex",
  claude: ".claude",
  cursor: ".cursor",
  gemini: ".gemini",
};
const SOURCE_ITEMS = ["SKILL.md", "assets", "references", "scripts"];
const MARKER = ".study-anything-install.json";

function installerError(code, message) {
  const error = new Error(message);
  error.code = code;
  return error;
}

async function exists(filePath) {
  try {
    await lstat(filePath);
    return true;
  } catch (error) {
    if (error.code === "ENOENT") return false;
    throw error;
  }
}

function normalizeRelative(filePath) {
  return filePath.split(path.sep).join("/");
}

async function listFiles(root, relative = "") {
  const directory = path.join(root, relative);
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];

  for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
    const childRelative = path.join(relative, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await listFiles(root, childRelative)));
    } else if (entry.isFile() && entry.name !== MARKER) {
      files.push(normalizeRelative(childRelative));
    }
  }
  return files;
}

async function sha256(filePath) {
  const hash = createHash("sha256");
  hash.update(await readFile(filePath));
  return hash.digest("hex");
}

async function createManifest(root) {
  const files = await listFiles(root);
  const manifest = {};
  for (const file of files) {
    manifest[file] = await sha256(path.join(root, ...file.split("/")));
  }
  return manifest;
}

async function readMarker(destination) {
  try {
    const parsed = JSON.parse(await readFile(path.join(destination, MARKER), "utf8"));
    if (parsed.package !== SKILL_NAME || parsed.schemaVersion !== 1 || !parsed.manifest) {
      return null;
    }
    return parsed;
  } catch (error) {
    if (error.code === "ENOENT" || error instanceof SyntaxError) return null;
    throw error;
  }
}

async function isManifestCurrent(destination, expectedManifest) {
  const actual = await createManifest(destination);
  const expectedKeys = Object.keys(expectedManifest).sort();
  const actualKeys = Object.keys(actual).sort();
  if (expectedKeys.length !== actualKeys.length) return false;
  return expectedKeys.every(
    (file, index) => file === actualKeys[index] && expectedManifest[file] === actual[file],
  );
}

async function validateSkill(root) {
  const skillFile = path.join(root, "SKILL.md");
  const content = await readFile(skillFile, "utf8");
  const frontmatter = content.match(/^---\s*\r?\n([\s\S]*?)\r?\n---/);
  if (!frontmatter) {
    throw installerError("INVALID_SKILL", "SKILL.md is missing YAML frontmatter");
  }
  if (!/^name:\s*study-anything\s*$/m.test(frontmatter[1])) {
    throw installerError("INVALID_SKILL", "SKILL.md name must be study-anything");
  }
  for (const item of ["assets", "references", "scripts"]) {
    if (!(await exists(path.join(root, item)))) {
      throw installerError("INVALID_SKILL", `Skill is missing ${item}/`);
    }
  }
  return "passed";
}

function timestamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

export function resolveSkillsRoot({
  target = "agents",
  project = false,
  dir,
  cwd = process.cwd(),
  home = os.homedir(),
} = {}) {
  if (dir) return path.resolve(cwd, dir);
  if (!SUPPORTED_TARGETS.includes(target)) {
    throw installerError("UNSUPPORTED_TARGET", `Unsupported target: ${target}`);
  }
  const scopeRoot = project ? cwd : home;
  return path.join(scopeRoot, TARGET_DIRECTORIES[target], "skills");
}

export async function installSkill({
  packageRoot,
  packageVersion,
  skillsRoot,
  force = false,
  dryRun = false,
}) {
  if (!packageRoot || !packageVersion || !skillsRoot) {
    throw new TypeError("packageRoot, packageVersion, and skillsRoot are required");
  }

  await validateSkill(packageRoot);

  const destination = path.join(path.resolve(skillsRoot), SKILL_NAME);
  const destinationExists = await exists(destination);
  let action = destinationExists ? "updated" : "installed";
  let keepBackup = false;

  if (destinationExists) {
    const marker = await readMarker(destination);
    if (!marker) {
      if (!force) {
        throw installerError(
          "TARGET_EXISTS",
          `${destination} already exists and was not created by this installer`,
        );
      }
      action = "replaced";
      keepBackup = true;
    } else if (!(await isManifestCurrent(destination, marker.manifest))) {
      if (!force) {
        throw installerError(
          "LOCAL_CHANGES",
          `${destination} contains local changes`,
        );
      }
      action = "replaced";
      keepBackup = true;
    }
  }

  if (dryRun) {
    return { action, destination, validation: "source passed", backup: null };
  }

  await mkdir(path.dirname(destination), { recursive: true });
  const nonce = `${process.pid}-${randomBytes(4).toString("hex")}`;
  const staging = path.join(path.dirname(destination), `.${SKILL_NAME}.tmp-${nonce}`);
  const backup = `${destination}.backup-${timestamp()}`;
  let movedExisting = false;
  let installedNew = false;

  try {
    await mkdir(staging, { recursive: false });
    for (const item of SOURCE_ITEMS) {
      await cp(path.join(packageRoot, item), path.join(staging, item), {
        recursive: true,
        force: false,
        errorOnExist: true,
      });
    }

    await validateSkill(staging);
    const manifest = await createManifest(staging);
    await writeFile(
      path.join(staging, MARKER),
      `${JSON.stringify(
        {
          schemaVersion: 1,
          package: SKILL_NAME,
          version: packageVersion,
          installedAt: new Date().toISOString(),
          manifest,
        },
        null,
        2,
      )}\n`,
      "utf8",
    );

    if (destinationExists) {
      await rename(destination, backup);
      movedExisting = true;
    }
    await rename(staging, destination);
    installedNew = true;
    await validateSkill(destination);

    if (movedExisting && !keepBackup) {
      await rm(backup, { recursive: true, force: true });
      movedExisting = false;
    }

    return {
      action,
      destination,
      validation: "passed",
      backup: movedExisting ? backup : null,
    };
  } catch (error) {
    await rm(staging, { recursive: true, force: true }).catch(() => {});
    if (movedExisting) {
      if (installedNew && (await exists(destination))) {
        await rm(destination, { recursive: true, force: true }).catch(() => {});
      }
      if (!(await exists(destination))) {
        await rename(backup, destination).catch(() => {});
      }
    } else if (installedNew && (await exists(destination))) {
      await rm(destination, { recursive: true, force: true }).catch(() => {});
    }
    throw error;
  }
}
