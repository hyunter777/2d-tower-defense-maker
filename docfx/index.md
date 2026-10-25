---
title: API overview
---

# 2D Tower Defense Maker API

The reference documents the public and protected API of the three product assemblies. The `TDMaker.*` namespaces and assembly names are the identifiers used in your Unity project.

Start with the user manual for installation, editor workflows and playable samples. Select the product logo above to return to the manual. Use this reference when writing integrations, building content from code or extending the simulation.

| Assembly | Responsibility | Start here |
| --- | --- | --- |
| `TDMaker.Core` | Engine-independent simulation, immutable definitions, player commands, entities and events | [Simulation](xref:TDMaker.Core.Simulation), [definitions](xref:TDMaker.Core.Defs), [commands](xref:TDMaker.Core.Commands) |
| `TDMaker.Unity` | ScriptableObject authoring, scene integration, views, HUD, localization and campaign progress | [LevelAsset](xref:TDMaker.Unity.Authoring.LevelAsset), [SimulationRunner](xref:TDMaker.Unity.View.SimulationRunner), [authoring namespace](xref:TDMaker.Unity.Authoring) |
| `TDMaker.Editor` | Level creation, validation, authoring windows and simulation previews | [Editor namespace](xref:TDMaker.Editor), [ProjectValidator](xref:TDMaker.Editor.ProjectValidator), [LevelDryRun](xref:TDMaker.Editor.LevelDryRun) |

## Working with the simulation

Bake a `LevelAsset` into immutable definitions, create a `Simulation`, enqueue player commands and advance fixed ticks with `Step()`. Consume simulation events before clearing them. `SimulationRunner` performs this integration for a Unity scene and exposes the current simulation for custom controls.

`TDMaker.Core` has no Unity engine dependency. Keep gameplay rules in the simulation and use `TDMaker.Unity` to present state and translate user input into commands. Editor APIs belong in editor-only assemblies.

## Reference scope

This reference is generated from the product's actual C# declarations and XML documentation using DocFX 2.81.0 with local Unity 6000.4.1f1 references. It includes exported types and members, overloads, parameters, return values and available examples. Private implementation, product source files and source links are excluded from the published site.

The documentation generator runs separately from the site build. A site build reads the checked-in API metadata and does not require Unity, the product source code or the local compiled assemblies.
