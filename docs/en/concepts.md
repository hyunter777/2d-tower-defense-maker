# Concepts

This page explains the rules the simulation follows. Field-level details are in [Authoring Reference](authoring.md); code-level extension is in [Extending the Framework](extending.md).

## Simulation vs. view

```
ScriptableObjects (TDMaker.Unity.Authoring)
      │  LevelAsset.Bake()  →  TemplateRegistry + LevelDef  (immutable definitions)
      ▼
Simulation (TDMaker.Core)          fixed ticks · entities + components + systems
      │  reads: sim.State, sim.Entities, sim.Spells      writes: sim.Enqueue(command)
      │  outputs: sim.Events (SimEvent list)
      ▼
View (TDMaker.Unity.View / .Hud)  SimulationRunner, EntityViewRegistry, LevelView, GameHud, …
```

- **`TDMaker.Core`** is plain C#. It does not reference `UnityEngine`, uses its own `Vec2` and its own seeded random stream (`SimRandom`, xorshift32). Gameplay outcomes (damage, gold, lives, spawns, builds) are decided here only.
- **`TDMaker.Unity`** bakes authoring assets into core definitions, advances the simulation every frame, and draws it. The view only *reads* state and *sends commands*; it never changes simulation state directly.

## Fixed tick

- The simulation advances in fixed steps: `Simulation.Step()`; `SimConfig.TickRate` defaults to **30 ticks per second** (`Simulation.DeltaTime = 1/30 s`). All durations in assets are in game seconds.
- `SimulationRunner` advances the core `SimulationClock`: it accumulates `Time.deltaTime × TimeScale` and runs as many steps as fit, up to `Catch Up Ticks Per Speed × speed` (default `8 × speed`) per rendered frame; excess backlog is dropped so a slow frame cannot snowball. `TimeScale` 0 pauses; the HUD offers 1×, 2×, 3×.
- Speeding up changes only how many ticks run per frame, not the tick length, so the outcome at 3× is the same as at 1× for the same inputs.
- Views interpolate between `Entity.PreviousPosition` and `Entity.Position` using `SimulationRunner.InterpolationAlpha`.
- `SimulationClock` is engine-independent, so custom hosts use the same catch-up rule (see [Extending the Framework](extending.md#hosting-the-simulation-without-simulationrunner)).

### System order within one tick

| # | `SimStage` | Work |
|---|---|---|
| 1 | `Commands` | Apply queued player commands |
| 2 | `Waves` | Unit expiry, scheduled summons, barracks respawn, wave start and spawning |
| 3 | `Effects` | Status effects, areas, recovery |
| 4 | `Motion` | Path following and friendly movement |
| 5 | `Blocking` | Pair soldiers/heroes with enemies |
| 6 | `Melee` | Melee attack cycles |
| 7 | `Ranged` | Target selection, ranged attacks, ability actions |
| 8 | `Projectiles` | Projectile flight and impact |
| 9 | `Damage` | Apply all queued damage in FIFO order |
| 10 | `Death` | Resolve kills, pay bounties, death summons |
| 11 | `Exits` | Resolve leaks, remove lives |
| 12 | `HeroesAndSpells` | Hero progression, spell readiness |
| 13 | `Flow` | Victory/defeat |
| 14 | `Flush` | Commit spawns and removals |

Entities created during a tick are committed at `Flush` and act **from the next tick**. Entities marked for removal are ignored by the rest of the tick.

## Campaign and release mechanics

Campaign progress and shop purchases live outside the battle. At battle start the core applies a fixed upgrade snapshot to copied definitions; the snapshot is included in replay validation and state hashes. See [Campaigns, Progress and Saves](campaign.md).

Mine fields reserve lane sites and capacity before flight and arming. Companion slots follow their owner and refill after a child falls. Reviving enemies are not final kills until their return budget ends; pending returns and raised successors keep victory waiting. Bodies are neutral records consumed by raising actions, not extra enemy kills. See [Mechanic Library](mechanics.md).

## Templates, components and systems

- An **`EntityTemplate`** is an immutable definition with optional slots: `Health`, `Armor`, `Motion`, `PathFollow`, `Bounty`, `Melee`, `Ranged`, `Tower`, `Barracks`, `Soldier`, `Hero`, `Projectile`, `Aura`, `StatusImmunity`, `Flying`, `Render`, plus `Rules` (recovery, evasion, death summon, always-on behaviors, traits) and `CustomData`.
- Templates may inherit from another template through `BaseId`; empty (null) slots inherit the parent's slot. Inheritance is resolved once when the `TemplateRegistry` is built.
- A runtime **`Entity`** carries one runtime component per filled slot (`entity.Health.Current`, `entity.PathFollow.RemainingDistance`, `entity.Tower.Priority`, …). Entities come from a fixed, prewarmed pool (`SimConfig.EntityCapacity`, default 1024). Ids only increase and are never reused.
- **Systems** implement `ISimSystem.Tick(Simulation sim, float dt)` and run in the fixed order above. You can insert your own; see [Extending the Framework](extending.md).
- Authoring assets bake into templates: `EnemyAsset`, `TowerAsset`, `SoldierAsset`, `HeroAsset` each produce one template. Each tower tier is its own template.

## Determinism

- Same templates + same level + same seed + same commands at the same ticks ⇒ same result, at any game speed.
- The core uses only its own random stream, iterates in entity-Id order, and breaks ties by the smaller Id.
- `ComputeStateHash()` hashes the full authoritative state for comparison. Command recording and replay: [Determinism and Replay](determinism-and-replay.md).

## Commands and events

**Input** – the view queues immutable commands with `Simulation.Enqueue(command)` (or `SimulationRunner.Enqueue`). They are applied at the start of the next tick.

| Command | Effect |
|---|---|
| `BuildTower(slotIndex, templateId)` | Build an available base tower on an empty slot |
| `UpgradeTower(entityId, toTemplateId)` | Upgrade into one of the tower's listed next tiers |
| `SellTower(entityId)` | Sell (see *Economy*) |
| `BuyAbility(entityId, abilityIndex)` | Buy the next rank of a tower ability |
| `SetTargetPriority(entityId, priority)` | Change a tower's priority without resetting its cooldown |
| `SetRallyPoint(entityId, position)` | Move a barracks rally point (must be inside the rally ellipse; projected onto the nearest lane) |
| `CallNextWave()` | Start the next wave now |
| `MoveHero(entityId, position)` | Order a hero to a validated point |
| `CastSpell(spellIndex, position)` | Cast a ready spell at a validated point |
| `SpendHeroPoint(entityId, skillIndex)` | Buy a hero skill rank (`SpendPoints` mode) |

A failed command produces a `CommandRejected` event with a `CommandFailure` reason (`InsufficientGold`, `SlotOccupied`, `InvalidRallyPoint`, `WaveUnavailable`, `SpellUnavailable`, …) and the command name in `Key`.

**Output** – each tick appends `SimEvent`s (`Kind`, `EntityId`, `OtherId`, `Value`, `IntValue`, `Position`, `Failure`, `Key`) to `Simulation.Events`. Examples: `Spawned`, `Removed`, `Damaged`, `Died`, `AttackStarted`, `ProjectileFired`, `ProjectileHit`, `GoldChanged`, `LivesChanged`, `WaveStarted`, `WaveCallable`, `TowerBuilt/Upgraded/Sold`, `EffectAttached/Removed`, `AbilityPurchased`, `HeroLevelChanged`, `SpellCast`, `Victory`, `Defeat`, plus the mechanic events (`ChainLinked`, `AreaPulsed`, `Healed`, `ShieldChanged`, `Displaced`, … – see [Mechanic Library](mechanics.md)). The reader calls `ClearEvents()` afterwards; `SimulationRunner` does this for you after raising `EventRaised`.

**State** – `Simulation.State` exposes `Gold`, `Lives`, `WaveNumber`, `CanCallNextWave`, `NextWaveRemaining`, `NextWaveWaitDuration` (the authored auto delay of the pending wave – the countdown's denominator; 0 while a wave is emitting or after the last one), `VictoryStars`, `Phase` and `Tick`.

**Event values worth knowing** – `ProjectileHit.Value` is the damage radius of instant (hitscan) and scheduled strikes (0 = single target; flight projectiles report 0, their radius is on the projectile). `WaveStarted.Value` is the early-call time credit in seconds and `IntValue` the one-based wave number; an early-call reward arrives as the `GoldChanged` event emitted just before it. `Victory.IntValue` is the star rating.

**Previews (never duplicate a rule in the view)** – read-only functions that use exactly the code the commands use. They do not change the world or emit events.

| Function | Use |
|---|---|
| `PreviewEarlyCallReward()` → `EarlyCallRewardPreview` | `CanCall`, `WaveNumber`, `GoldReward` (authored award), `GoldGain` (after the wallet limit), `TimeCredit`, `SpellCooldownCut`, `SpellCooldownsAffected` of calling the next wave now. |
| `PreviewEarlyCallSpellCooldownCut(spellIndex)` | Seconds that spell's remaining cooldown would lose if the next wave were called now. |
| `PreviewSellRefund(towerId)` | The refund `SellTower` would report (`TowerSold.Value`). |
| `TryResolveRallyPoint(towerId, desired, out resolved)` | Whether `SetRallyPoint` would accept the point, and the lane-projected point the soldiers would use. |
| `TryValidateSpellPoint` / `TryResolvePoint` | Spell targets and hero destinations (see [Authoring Reference](authoring.md)). |

The bundled HUDs (`GameHud`, `TDHud`) use only these functions for their sell price, call-wave bonus, spell-cut tooltip and rally preview.

**Commands after the end** – once the game is won or lost, every queued command is rejected with `GameEnded` (a `CommandRejected` event). `SimulationClock` stops stepping a finished world, so `SimulationRunner` runs one terminal step on the next frame when commands were queued after the end; the step only processes commands (the tick counter does not advance).

## Coordinate system and the range ellipse

- Simulation space is the Unity XY plane in world units (scene components convert their transforms to world XY when baking). Y is "up the screen".
- To suggest an oblique top-down view, every range is an **ellipse**: horizontal semi-axis `r`, vertical semi-axis `k·r`, where `k` is the **range Y scale**.
- A point is in range when

  ```
  dx² / r²  +  dy² / (k·r)²  ≤  1        (boundary included)
  ```

- `k` comes from the level (`LevelAsset.overrideRangeYScale` / `rangeYScale`) or else from the runner (`SimulationRunner` "Range Y Scale", default `0.8`). `k < 1` flattens ranges vertically.
- **One formula for checks and display.** The simulation uses `Simulation.RangeDistanceSquared` for tower ranges, melee contact, area damage, rally limits, spell scatter and aura radii. Everything drawn in the view, gizmos and editor previews uses `RangeShape` (Unity layer), which implements the same ellipse. What you see is exactly what is hit.
- Authored "range" or "radius" values are the horizontal semi-axis `r`.

## Target priorities

Ranged attacks choose among eligible enemies inside the ellipse (and outside `Minimum Range`), respecting flying/ground filters. Ties always go to the lower entity Id.

| Priority | Picks |
|---|---|
| **First** (default) | Shortest **remaining real path length** to the exit (sum of actual segment lengths, including connected paths), not "closest to the exit point" |
| Last | Longest remaining path length |
| Strongest | Highest current health |
| Weakest | Lowest current health |
| Closest | Smallest elliptical distance to the attacker |

A tower's default comes from `TowerAsset.targetPriority`; the player can change it at runtime (`SetTargetPriority`) and the choice survives upgrades. Enemies attacking friendly units use Closest. Soldiers and heroes choose melee opponents through their own blocking rules.

## Damage pipeline

1. **Roll.** Single-target hits roll `ceil(lerp(min, max, random))`, then multiply by the attacker's output scale (rounded up). Projectile hits deal at least 1.
2. **Area.** If the damage has a `Radius`, every eligible unit inside the ellipse is hit. With `q = distance / radius` (elliptical) and `edge = Edge Multiplier`, the amount is `ceil(base × (1 − (1 − edge)·q) × outputScale)` where `base` depends on `Falloff`:
   - `DistanceEndpoints`: `floor(max − (max − min)·q)`
   - `RolledLinear`: one roll per impact
   - `ConstantMaximum`: `max`
3. **Hooks.** Registered `IDamageHook.BeforeDamage` may change or cancel the raw amount.
4. **Queue.** Requests are applied in the `Damage` stage in request order (stage order × entity Id), so results do not depend on frame timing.
5. **Mitigation** (per request):
   - Immune channel (`TargetTraitsDef.Immunities`) or `IgnoreDamage` → 0.
   - Reduction `R`, clamped to `[0, 1]`:

     | Kind | R |
     |---|---|
     | Physical | armor + armor shifts − physical pierce |
     | Magical | magic resist + shifts − magical pierce |
     | Explosion, Electric | ½ × (armor + armor shifts − physical pierce) |
     | Poison | poison resist + shifts |
     | True | 0 |

   - Incoming multipliers (rounded half away from zero): magical damage first × `MagicalIncomingMultiplier` × status magical input scale, then all damage × `IncomingMultiplier` × status input scale.
   - Enemies lose `floor(value × (1 − R))`. Friendly units (soldiers, heroes) lose `round(value − floor(value × R))`.
   - Shields from status effects absorb the mitigated amount of matching channels, in attachment order ([Mechanic Library](mechanics.md#shields)).
   - Flags: `Execute` removes all remaining health; `NonLethal` leaves `SurvivalHealth`; `Despawn` removes without reward; armor-reduction flags change defense instead of health.

6. **After.** `Damaged` event, on-hit status effects, the damage's impact payload (secondary blast, residual region, knockback), hero experience, then `IDamageHook.AfterDamage`.

Armor and magic resist are fractions: `0.3` armor removes 30% of physical damage. `1.0` makes a unit immune to that kind.

## Resolution: kill vs. leak in the same tick

Every enemy is resolved exactly once as `Killed`, `Leaked` or `Despawned`. Because `Damage → Death → Exits` run in that order, an enemy that takes lethal damage in the same tick it reaches the exit counts as **Killed**: the bounty is paid and no life is lost.

- **Killed**: `+Bounty.Gold`.
- **Leaked**: `−LifeCost` lives and `+round(Gold × LeakBountyShare)` (level rule, default 0).
- **Defeat** when lives reach 0. **Victory** when every wave has finished emitting, nothing is pending (spawns, scheduled summons) and no enemy remains. If both happen in the same tick, defeat wins. Once decided, the outcome never changes and further commands are rejected with `GameEnded`.
- **Star rating**: on victory the core rates the result from the share of starting lives left (`remaining / starting`, capped at 1) against the level's `Victory Rating` bands (inclusive): three stars at or above the three-star share, two at or above the two-star share, otherwise one. The result is `State.VictoryStars` and the `Victory` event's `IntValue`; defeat leaves it at 0. Product default: two stars at half the lives, three at all of them.

## Economy

- **Build**: pay the tower tier's `Cost`.
- **Upgrade**: pay the *target* tier's `Cost` (each tier's cost is incremental).
- **Ability rank**: pay that rank's cost.
- **Total investment** = build + upgrades + ability ranks bought on that tower.
- **Sell**:
  - before the first wave has started (`WaveNumber == 0`): **full refund** of the investment;
  - afterwards: `round(investment × RefundShare)`, `RefundShare` from the level rules (default `0.6`). Rounding is half away from zero.
- The per-tower `Refund Ratio` field is a hidden legacy value and does not affect the simulation; editor previews also use the level's `Refund Share`.
- During play, `Simulation.PreviewSellRefund(towerId)` returns exactly the amount a sale would pay.
- There is no interest.

## Waves and early calls

- A wave contains groups; each group belongs to one path and has a start delay; each group runs its spawn entries one after another. The first unit of an entry appears one `Interval` after the entry starts; an interval of 0 spawns one unit per tick.
- After a wave **finishes emitting**, the next wave's timers start:
  - `Call Delay`: from then on the player may call it early (`CanCallNextWave`, `WaveCallable` event);
  - `Auto Delay`: it starts automatically.
- The first wave waits for the player unless `Auto Start First` is set.
- **Early call reward**: calling wave *n > 1* early pays `ceil(round(remaining seconds) × rate)` gold, where `remaining = Auto Delay − time already waited`, rounded half away from zero, and `rate` is the wave's `Early Gold Per Second` (or the level's override). Calling the first wave gives no reward.
- If the level rule `Early Call Spell Cooldown Cut` is on and the rounded remaining time exceeds `Early Call Cut Threshold`, cooling, unlocked spells are shortened by that many seconds.
- `Simulation.PreviewEarlyCallReward()` and `PreviewEarlyCallSpellCooldownCut(spellIndex)` return both effects for the current tick; the countdown ring is `NextWaveRemaining / NextWaveWaitDuration`.

## Barracks, soldiers and heroes

- A barracks tower keeps `Soldier Count` soldiers alive and replaces a fallen one after `Respawn Time`. Soldiers stand in a formation around the **rally point**, which is always projected onto the nearest lane inside the tower's rally ellipse.
- Soldiers engage enemies inside their `Intercept Radius` around the rally point. An engaged enemy stops walking while blocked and waits for its blocker to reach its place: beside the enemy on the side it walks toward, at the summed `Engagement` contact bias of the enemy and the blocker (2nd and 3rd blockers take rows above and below, by the enemy's `Row Spacing`). Blockers attack only once they stand in place; both face each other. `Blocker Capacity` on the enemy limits how many friendly units can hold it; flying or non-blockable enemies cannot be blocked.
- Heroes are friendly units that block and fight like soldiers, gain experience from damage, level up through growth rows, unlock skills, die and return after `Respawn Delay`, and move by command.

## View layer

- `SimulationRunner` bakes the level (applying template decorators), creates the `Simulation`, spawns heroes, advances it with `SimulationClock`, and raises `EventRaised` for each event once per frame (then clears them).
- `EntityViewRegistry` creates pooled `EntityView`s on `Spawned`, removes them on `Removed`, and reacts to damage, death, effects, upgrades, projectile and mechanic events (chain arcs, pulse rings, shield bubbles, …). A prefab is taken from the asset's `View` settings (or the registry's overrides by view key); otherwise a primitive sprite is generated.
- `LevelView` draws a generated placeholder ground, path ribbons and slot pads.
- `GameHud` is the production uGUI HUD (themeable with `HudTheme`); `DamageNumbers`, `VfxPool`, `AudioCuePlayer`, `TDCameraController` and `TDGameSettings` complete the presentation. See [Presentation](presentation.md). `TDHud` is a minimal IMGUI reference HUD. Any of them can be replaced by your own UI that reads `Simulation.State` and sends commands.
