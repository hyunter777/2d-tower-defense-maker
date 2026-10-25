# Performance

Measure simulation work, views, UI and rendering separately on your target devices. Content density, effect concurrency and the selected game speed all affect the work performed in a rendered frame. Warm pools and shaders before measuring steady-state behavior, and include pool growth when measuring startup and new concurrency peaks.

## Profiler markers

In the Editor and in development players the runner wraps the simulation in Unity Profiler markers, so the CPU Usage module shows where a tick goes:

- `TDMaker.Runner.Advance` → `TDMaker.Sim.Step` → one marker per stage: `TDMaker.Sim.Commands`, `Waves`, `Effects`, `Motion`, `Blocking`, `Melee`, `Ranged`, `Projectiles`, `Damage`, `Death`, `Exits`, `HeroesAndSpells`, `Flow`, `Flush`. Custom systems appear as `TDMaker.Sim.<anchor stage>#<index>`.
- `TDMaker.Runner.Dispatch` → `TDMaker.Views.OnEvent`, `TDMaker.Hud.OnEvent`, `TDMaker.DamageNumbers.OnEvent` (the event handlers of the frame).

Turn the stage markers off with `Profiler Markers` on the `Simulation Runner` (they compile away in non-development players anyway). To time stages yourself, implement `ISimProfiler` (preallocate, do not allocate in callbacks) and assign it to `SimulationRunner.Profiler`; it is chained behind the markers.

## How the core stays cheap

- **Fixed pools.** All entity bundles, components, event and damage buffers are allocated when the simulation is created (`SimConfig.EntityCapacity` default 1024, `EventCapacity` 8192, `CommandCapacity` 128; `SimConfig.WithLimits(new SimLimits(effects, areas, schedules))` for effects, areas and scheduled summons).
- **No allocation in the tick path**, no LINQ, lists are reused.
- **Spatial grid** for enemy range queries (`Simulation.ConfigureSpatialIndex(cellSize: 4)` before the first step; `enabled: false` switches to an Id-ordered linear scan with identical results).
- Per-role entity lists (`Enemies`, `Towers`, `Soldiers`, `Projectiles`, `Heroes`) avoid scanning everything.

## Capacity limits

When a pool or buffer is full, the simulation degrades instead of allocating:

| Situation | Behavior | Counter |
|---|---|---|
| No free entity (spawns, projectiles, soldiers) | Spawn waits or fails | `Simulation.CapacityFailureCount` |
| Too many damage requests in one tick (limit = `EventCapacity`) | Request dropped | `Simulation.DroppedDamageCount` |
| Event buffer full (events not cleared) | New events are dropped | `Simulation.DroppedEventCount` |
| Command queue full | Command rejected with `CapacityExceeded` | — |

Except for a full event buffer, each case also emits a `CapacityExceeded` event whose `Key` names the pool (for example `Entities`, `Damage`, `Commands`).

**Event capacity and game speed.** `SimulationRunner` delivers events once per frame, so the buffer must hold every tick a frame catches up – at most `Catch Up Ticks Per Speed × speed` ticks (24 at 3× with the default 8). The default `Event Capacity` of 8192 therefore covers about 340 events per tick at 3× in the worst catch-up frame (at a steady 60 fps a 3× frame runs only 1–2 ticks). If a denser level drops events, the runner logs one warning per run and `Simulation.DroppedEventCount` rises; raise `Event Capacity` (it also sizes the per-tick damage queue). The Dry Run report prints the peak per tick and per 24 ticks for your own levels.

If you see these counters rise, raise the capacities in the `Simulation Runner` Inspector (**Capacities**: entities, events, commands, effects, areas, schedules, chains; `SimulationRunner.CreateConfig()` builds the `SimConfig`) or reduce content density. Chains run from their own pool (`Chain Capacity`, default 64); each chain job preallocates one visited-target array of `Entity Capacity`.

## View-side tips

- Views and projectile visuals are pooled by `EntityViewRegistry` (`Prewarm Primitives`); primitive entries prepare trails, status pips and shields before the fight, so switching a former projectile view to a unit does not add those components mid-fight. Use prefabs with few renderers; avoid per-frame allocations in custom `EventRaised` handlers.
- At high speed several ticks run per frame; keep event handlers light.
- `Catch Up Ticks Per Speed` on the runner limits catch-up work after a slow frame (`value × speed` ticks per frame).
- `GameHud` (uGUI) is the production HUD. The IMGUI `TDHud` is a reference/debug overlay; keep it disabled in shipping builds.
- VFX hooks go through `VfxPool` (`Max Active` caps live instances) and mechanic feedback (arcs, rings, flashes) is pooled by `EntityViewRegistry` (`Prewarm Feedback Fx`, `Max Feedback Fx` per kind; extra effects are skipped rather than growing the pool).
- The built-in views and HUD allocate nothing per frame once their pools have grown to the level's peak. Pools still grow (and allocate once) when a new peak of simultaneous units, projectiles or traps appears; raise `Prewarm Primitives` for very dense levels.

## Measuring your own content

- Use the Unity Profiler on a development player build; the simulation runs inside `SimulationRunner.Update` (see the markers above).
- **Tools > 2D Tower Defense Maker > Dry Run Level** runs a whole level headlessly in the Editor and is a quick sanity check for content, not a benchmark.
