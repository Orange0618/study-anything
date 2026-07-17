import assert from "node:assert/strict";
import { mkdtemp, mkdir, readFile, writeFile, rm, readdir } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { installSkill, resolveSkillsRoot } from "../lib/installer.js";

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

async function tempDirectory(t) {
  const directory = await mkdtemp(path.join(os.tmpdir(), "study-anything-test-"));
  t.after(() => rm(directory, { recursive: true, force: true }));
  return directory;
}

test("installs a validated skill into a custom skills root", async (t) => {
  const root = await tempDirectory(t);
  const result = await installSkill({
    packageRoot,
    packageVersion: "0.1.0-test",
    skillsRoot: path.join(root, "skills"),
  });

  assert.equal(result.action, "installed");
  assert.equal(result.validation, "passed");
  assert.match(await readFile(path.join(result.destination, "SKILL.md"), "utf8"), /name: study-anything/);

  const marker = JSON.parse(
    await readFile(path.join(result.destination, ".study-anything-install.json"), "utf8"),
  );
  assert.equal(marker.package, "study-anything");
  assert.ok(marker.manifest["SKILL.md"]);
});

test("updates an unchanged managed installation without leaving a backup", async (t) => {
  const root = await tempDirectory(t);
  const skillsRoot = path.join(root, "skills");
  await installSkill({ packageRoot, packageVersion: "0.1.0", skillsRoot });
  const result = await installSkill({ packageRoot, packageVersion: "0.1.1", skillsRoot });

  assert.equal(result.action, "updated");
  assert.equal(result.backup, null);
  const siblings = await readdir(skillsRoot);
  assert.deepEqual(siblings, ["study-anything"]);
});

test("refuses to overwrite local changes unless force is used", async (t) => {
  const root = await tempDirectory(t);
  const skillsRoot = path.join(root, "skills");
  const first = await installSkill({ packageRoot, packageVersion: "0.1.0", skillsRoot });
  await writeFile(path.join(first.destination, "local-note.txt"), "keep me\n", "utf8");

  await assert.rejects(
    installSkill({ packageRoot, packageVersion: "0.1.1", skillsRoot }),
    (error) => error.code === "LOCAL_CHANGES",
  );

  const forced = await installSkill({
    packageRoot,
    packageVersion: "0.1.1",
    skillsRoot,
    force: true,
  });
  assert.equal(forced.action, "replaced");
  assert.ok(forced.backup);
  assert.equal(await readFile(path.join(forced.backup, "local-note.txt"), "utf8"), "keep me\n");
});

test("refuses a manual install and preserves it as a backup with force", async (t) => {
  const root = await tempDirectory(t);
  const skillsRoot = path.join(root, "skills");
  const destination = path.join(skillsRoot, "study-anything");
  await mkdir(destination, { recursive: true });
  await writeFile(path.join(destination, "manual.txt"), "manual\n", "utf8");

  await assert.rejects(
    installSkill({ packageRoot, packageVersion: "0.1.0", skillsRoot }),
    (error) => error.code === "TARGET_EXISTS",
  );

  const forced = await installSkill({
    packageRoot,
    packageVersion: "0.1.0",
    skillsRoot,
    force: true,
  });
  assert.equal(await readFile(path.join(forced.backup, "manual.txt"), "utf8"), "manual\n");
});

test("dry run does not create the destination", async (t) => {
  const root = await tempDirectory(t);
  const skillsRoot = path.join(root, "skills");
  const result = await installSkill({
    packageRoot,
    packageVersion: "0.1.0",
    skillsRoot,
    dryRun: true,
  });

  assert.equal(result.action, "installed");
  await assert.rejects(readdir(skillsRoot), (error) => error.code === "ENOENT");
});

test("resolves universal, native, project, and custom skill roots", () => {
  const home = path.resolve("home");
  const cwd = path.resolve("project");

  assert.equal(resolveSkillsRoot({ home, cwd }), path.join(home, ".agents", "skills"));
  assert.equal(
    resolveSkillsRoot({ home, cwd, target: "codex" }),
    path.join(home, ".codex", "skills"),
  );
  assert.equal(
    resolveSkillsRoot({ home, cwd, target: "claude", project: true }),
    path.join(cwd, ".claude", "skills"),
  );
  assert.equal(
    resolveSkillsRoot({ home, cwd, dir: "custom-skills" }),
    path.join(cwd, "custom-skills"),
  );
});
