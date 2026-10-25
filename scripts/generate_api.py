"""Refresh public API metadata from local 2D Tower Defense Maker sources.

Only the sanitized YAML and manifest are published. Unity references, compiled
assemblies, XML documentation and all temporary projects remain under .work.
This command does not start Unity or change the imported Unity project.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from xml.sax.saxutils import escape

import yaml


SITE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT = SITE_ROOT.parents[1]
DOCFX_VERSION = "2.81.0"
ASSEMBLIES = {
    "Core": ("Runtime/Core", []),
    "Unity": ("Runtime/Unity", ["Core"]),
    "Editor": ("Editor", ["Core", "Unity"]),
}
SOURCE_FIELDS = {"source", "sourceLink", "sourceUrl", "sourceURL", "documentation", "remote", "git"}
ABSOLUTE_PATH = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]|file://|/(?:Users|home|workspace|workspace_ai|tmp|private/var)/")


class DocfxLoader(getattr(yaml, "CSafeLoader", yaml.SafeLoader)):
    """DocFX can emit unquoted '=' scalars, which PyYAML tags as YAML values."""


DocfxLoader.add_constructor("tag:yaml.org,2002:value", lambda loader, node: loader.construct_scalar(node))


def run(command: list[str | Path], cwd: Path) -> None:
    subprocess.run([str(arg) for arg in command], cwd=cwd, check=True)


def clean_metadata(value):
    if isinstance(value, dict):
        return {key: clean_metadata(item) for key, item in value.items() if key not in SOURCE_FIELDS}
    if isinstance(value, list):
        return [clean_metadata(item) for item in value]
    return value


def validate_public_metadata(value, location: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in SOURCE_FIELDS:
                raise ValueError(f"Source metadata remains in {location}: {key}")
            validate_public_metadata(item, location)
    elif isinstance(value, list):
        for item in value:
            validate_public_metadata(item, location)
    elif isinstance(value, str):
        if ABSOLUTE_PATH.search(value):
            raise ValueError(f"An absolute path remains in public metadata: {location}")
        if re.search(r"https?://[^\s]+/(?:blob|raw)/[^\s]+\.cs(?:[#?]|$)", value):
            raise ValueError(f"A source-code URL remains in public metadata: {location}")


def unity_defines(project: Path, part: str, version: str) -> list[str]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)[abfp]\d+", version)
    if not match:
        raise ValueError("Use a full Unity version such as 6000.4.1f1.")
    major, minor, patch = map(int, match.groups())
    settings = (project / "ProjectSettings/ProjectSettings.asset").read_text(encoding="utf-8-sig")
    input_match = re.search(r"^\s*activeInputHandler:\s*(\d+)", settings, re.MULTILINE)
    if not input_match:
        raise ValueError("Cannot resolve activeInputHandler from the project's Player Settings.")
    input_handler = int(input_match.group(1))
    expected_input = input_handler in (1, 2)
    expected_legacy = input_handler in (0, 2)
    # Read Unity's own compiler response file instead of inventing conditional symbols.
    # Player-build response files are excluded: the Editor assembly and editor-only API
    # are documented together using the current imported project's Editor configuration.
    responses = sorted((project / "Library/Bee/artifacts").glob(f"*/TDMaker.{part}.rsp"),
                       key=lambda path: path.stat().st_mtime, reverse=True)
    for response in responses:
        text = response.read_text(encoding="utf-8-sig")
        defines = []
        for line in text.splitlines():
            if line.startswith(("-define:", "/define:")):
                defines.extend(line.split(":", 1)[1].strip('"').split(";"))
        if ("UNITY_EDITOR" in defines and f"UNITY_{major}_{minor}_{patch}" in defines
                and ("ENABLE_INPUT_SYSTEM" in defines) == expected_input
                and ("ENABLE_LEGACY_INPUT_MANAGER" in defines) == expected_legacy):
            return list(dict.fromkeys(defines))
    raise ValueError(f"No matching Unity {version} Editor compiler symbols found for TDMaker.{part}. "
                     "Use this generator with a project already imported by that Editor version.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--unity-managed", type=Path,
                        default=Path("C:/Program Files/Unity/Hub/Editor/6000.4.1f1/Editor/Data/Managed/UnityEngine"))
    parser.add_argument("--script-assemblies", type=Path)
    parser.add_argument("--docfx", default=shutil.which("docfx") or str(Path.home() / ".dotnet/tools/docfx.exe"))
    parser.add_argument("--output", type=Path, default=SITE_ROOT / "api-metadata")
    parser.add_argument("--work", type=Path)
    args = parser.parse_args()

    project = args.project_root.resolve()
    source = project / "Assets/TDMaker"
    managed = args.unity_managed.resolve()
    imported = (args.script_assemblies or project / "Library/ScriptAssemblies").resolve()
    work = (args.work or project / ".work/qa08/api-generation").resolve()
    output = args.output.resolve()
    if not (source / "Runtime/Core/TDMaker.Core.asmdef").is_file():
        raise SystemExit("Choose an imported TD Maker project with Assets/TDMaker/Runtime/Core.")
    if work == output or output in work.parents or work in output.parents:
        raise SystemExit("Public metadata and temporary build directories must be separate.")
    version = re.search(r"^m_EditorVersion:\s*(\S+)",
                        (project / "ProjectSettings/ProjectVersion.txt").read_text(encoding="utf-8-sig"), re.MULTILINE).group(1)
    defines = {part: unity_defines(project, part, version) for part in ASSEMBLIES}
    docfx_version = subprocess.check_output([args.docfx, "--version"], text=True).strip()
    if docfx_version.split("+", 1)[0] != DOCFX_VERSION:
        raise SystemExit(f"DocFX {DOCFX_VERSION} is required; found {docfx_version}.")

    reference_paths = {path.name: path for path in managed.glob("*.dll")}
    for name in ("UnityEngine.dll", "UnityEditor.dll"):
        reference_paths.setdefault(name, managed.parent / name)
    for name in ("UnityEngine.UI.dll", "UnityEditor.UI.dll", "Unity.TextMeshPro.dll", "Unity.InputSystem.dll"):
        reference_paths[name] = imported / name
    for path in reference_paths.values():
        if not path.is_file():
            raise SystemExit(f"A required local Unity reference is missing: {path}")
    work.mkdir(parents=True, exist_ok=True)
    for part, (folder, dependencies) in ASSEMBLIES.items():
        target = work / part
        target.mkdir(exist_ok=True)
        references = "".join(f'<ProjectReference Include="../{name}/{name}.csproj" />' for name in dependencies)
        if part != "Core":
            references += "".join(f'<Reference Include="{escape(str(path))}" Private="false" />'
                                  for path in sorted(reference_paths.values()))
        project_xml = f'''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.1</TargetFramework><LangVersion>9.0</LangVersion><Nullable>disable</Nullable>
    <AssemblyName>TDMaker.{part}</AssemblyName><EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <GenerateDocumentationFile>true</GenerateDocumentationFile><DebugType>none</DebugType>
    <NoWarn>1591;0649;0169;0414</NoWarn><DefineConstants>{';'.join(defines[part])}</DefineConstants>
    <RestoreSources></RestoreSources><RestoreIgnoreFailedSources>true</RestoreIgnoreFailedSources>
  </PropertyGroup>
  <ItemGroup><Compile Include="{escape(str(source / folder))}/**/*.cs" /></ItemGroup>
  <ItemGroup>{references}</ItemGroup>
</Project>
'''
        (target / f"{part}.csproj").write_text(project_xml, encoding="utf-8")
    # All references are local SDK/Unity assemblies. No NuGet PackageReference is generated.
    run(["dotnet", "build", work / "Editor/Editor.csproj", "-c", "Release", "--nologo"], work)

    binaries = work / "binaries"
    binaries.mkdir(exist_ok=True)
    for part in ASSEMBLIES:
        for suffix in ("dll", "xml"):
            shutil.copy2(work / part / f"bin/Release/netstandard2.1/TDMaker.{part}.{suffix}", binaries)
    reference_dir = work / "references"
    reference_dir.mkdir(exist_ok=True)
    for path in reference_paths.values():
        shutil.copy2(path, reference_dir / path.name)
    raw_metadata = work / "raw-metadata"
    raw_metadata.mkdir(exist_ok=True)
    for stale in raw_metadata.glob("*.yml"):
        stale.unlink()
    config = {"metadata": [{"src": [{"src": binaries.as_posix(), "files": ["TDMaker.*.dll"]}],
                            "references": ["references/*.dll"], "dest": raw_metadata.as_posix(),
                            "disableGitFeatures": True, "includePrivateMembers": False}]}
    config_path = work / "metadata.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    run([args.docfx, "metadata", config_path, "--disableGitFeatures"], work)

    # Validate all generated documents before replacing the previous public metadata.
    sanitized = {}
    public_uids = []
    for path in sorted(raw_metadata.glob("*.yml")):
        text = path.read_text(encoding="utf-8-sig")
        marker = text.splitlines()[0] + "\n" if text.startswith("###") else ""
        data = clean_metadata(yaml.load(text, Loader=DocfxLoader))
        validate_public_metadata(data, path.name)
        if isinstance(data, dict):
            public_uids.extend(item["uid"] for item in data.get("items", []) if "uid" in item)
        sanitized[path.name] = marker + yaml.dump(data, Dumper=getattr(yaml, "CSafeDumper", yaml.SafeDumper),
                                                 sort_keys=False, allow_unicode=True, width=120)
    if not public_uids or any(not any(uid.startswith("TDMaker." + part) for uid in public_uids) for part in ASSEMBLIES):
        raise SystemExit("API extraction did not produce all Core, Unity and Editor namespaces.")
    output.mkdir(parents=True, exist_ok=True)
    for stale in output.glob("*.yml"):
        if stale.name not in sanitized:
            stale.unlink()
    for name, text in sanitized.items():
        (output / name).write_text(text, encoding="utf-8", newline="\n")
    source_hash = hashlib.sha256()
    for part, (folder, _) in ASSEMBLIES.items():
        for path in sorted((source / folder).rglob("*.cs")):
            source_hash.update(path.relative_to(source).as_posix().encode("utf-8"))
            source_hash.update(path.read_bytes())
    manifest = {"product": "2D Tower Defense Maker", "docfx_version": DOCFX_VERSION, "unity_version": version,
                "assemblies": ["TDMaker." + part for part in ASSEMBLIES],
                "visibility": "public and protected API", "source_sha256": source_hash.hexdigest(),
                "source_files_published": False, "source_links_published": False,
                "metadata_files": len(sanitized), "documented_uids": len(public_uids), "defines": defines}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
