# Mechanic Library

Ready-made building blocks for common tower defense mechanics. Each one is a core definition (`TDMaker.Core.Defs`) with a matching serializable authoring block (`TDMaker.Unity.Authoring`), so designers can attach it to towers, tower abilities, enemies, hero skills, spells and projectiles without code. The view draws every one of them out of the box.

| Mechanic | Core definition | Authoring block | Where you attach it |
|---|---|---|---|
| Chain attack | `ChainAttackDef` | `ChainAttackData` | Ability / skill / behavior action: `Use Chain` + `Chain` |
| Multi-target attack | `MultiTargetAttackDef` | `MultiTargetAttackData` | Action: `Use Multi Target` + `Multi Target` |
| Recipient filter | `MechanicTargetDef` | `MechanicTargetData` | `Targets` of chains, multi-target attacks, impact payloads and pulses |
| Impact payload | `ImpactPayloadDef` | `ImpactPayloadData` | Any attack damage: `Damage > Impact` |
| Path displacement (knockback / pull) | `PathDisplacementDef` | `ImpactPayloadData.useDisplacement` + `displacement` | Inside an impact payload |
| Region pulse | `AreaPulseDef` | `AreaPulseData` | Any area effect: `Area > Pulse` (an area without a status effect becomes **pulse-only**) |
| Healing | `HealingDef` | `HealingData` | Pulses and periodic healing |
| Periodic healing | `PeriodicHealingDef` | `PeriodicHealingData` | Status effect: `Healing` |
| Shield | `ShieldDef` | `ShieldData` | Status effect: `Shield` |
| Combat modifier | `CombatModifierDef` | `CombatModifierData` | Stat modifier: `Combat` (status effects, ability passives) |
| Trap (mine, snare) | `TrapDef` | `TrapData` | Action: `Use Trap` + `Trap` |
| Beam (channel) | `BeamDef` | `BeamData` | Action: `Use Beam` + `Beam` |
| Reflection (thorns) | `ReflectionDef` | `ReflectionData` | Enemy: `Reflection` |
| Life steal | `LifeStealDef` | `LifeStealData` | Any attack damage: `Damage > Life Steal` |
| Path destination | `PathDestinationDef` | `PathDestinationData` | Inside a transfer action or an impact payload |
| Path transfer | `PathTransferDef` | `PathTransferData` | Action: `Use Transfer` + `Transfer`; hits: `Impact > Use Transfer` |
| Permanent aura | `AreaEffectDef.WithOwnerLifetime` / `CreateOwned` | `AreaEffectData.untilSourceLost` | Enemy `Aura`: `Until Source Lost` |
| Mine field (automatic mine laying) | `DeploymentPlanDef` (+ `TrapDef`) | `MineFieldData` | Action: `Use Mines` + `Mines` |
| Companions (escorts, followers) | `CompanionDef` | `CompanionData` | Hero / Tower: `Companions` |
| Return on the spot | `ReviveDef` | `ReviveData` | Enemy: `Revive` |
| Successor rules | `SummonDef.WithDeathSuccession` | `DeathSuccessionData` | Enemy: `Death Succession` (with `Death Summon`) |
| Raising the fallen | `RaiseRemainsDef` | `RaiseRemainsData` | Action: `Use Raise` + `Raise` |

Projectiles can additionally leave a region where they land: `ProjectileAsset > Impact Area` (core: `ProjectileDef.WithImpactArea`).

## Chain attack

One activation hits a first target near the actor, then jumps from victim to victim. Each victim is hit at most once per chain.

| Field | Meaning |
|---|---|
| `Id` | Event key; also selects the arc colour in the view. Use one id per look. |
| `Damage` | Damage at each link (may carry status effects and an impact payload). |
| `Range` | Range of the first link from the actor (scaled by the actor's range modifier). |
| `Link Range` | Range from one victim to the next. |
| `Max Targets` | Distinct victims including the first. |
| `Link Delay` | Game seconds between links (0 still waits for the next tick). |
| `Link Scale` | Damage multiplier applied after each link (0.8 = every jump deals 20% less). |
| `Chance` | One roll per activation; a failed roll still uses the cooldown. |
| `Targets`, `Targets Flying`, `Targets Ground` | Victim eligibility. |
| `Cancel With Source` | Remaining links stop if the actor dies, disappears, is stunned, disarmed or ordered to rally. |
| `Color`, `Vfx` | Arc colour and an optional pooled VFX spawned on each victim. |

Each link picks the nearest eligible enemy (ties: lower Id). Chains run from a fixed pool (`SimConfig.ChainCapacity`, runner field `Chain Capacity`, default 64); unfinished chains count as pending work, so the level does not end while one is running.

Events: `ChainStarted` (IntValue = chain id), `ChainLinked` per victim, `ChainEnded` (Value = victims), `MechanicMissed` on a failed roll.

## Multi-target attack

One activation hits several distinct targets at once.

| Field | Meaning |
|---|---|
| `Id` | Event key and beam colour key. |
| `Damage` | Independent hit per target. |
| `Range`, `Max Targets` | Search ellipse and number of targets. |
| `Health Budget` | Optional: the chosen targets' summed current health cannot exceed this (0 = no budget). Requires single-target damage. Useful for "finish off several weak enemies". |
| `Chance`, `Targets`, `Targets Flying`, `Targets Ground` | As for chains. |
| `Color`, `Vfx` | Beam colour and optional VFX per target. |

Towers order targets by their current target priority; other actors take the nearest first. Events: `MechanicTargeted` per target, then `MechanicActivated` (IntValue = targets hit).

## Recipient filter (`Targets`)

| Field | Meaning |
|---|---|
| `Required Tags` / `Rejected Tags` | Bit masks matched against the recipient's `Tags` (Enemy, Soldier and Hero assets have a `Tags` field). |
| `Allow Heroes` | Heroes may be chosen. |
| `Maximum Health Ratio` | Only recipients at or below this share of their maximum health (1 = any). |
| `Maximum Health` | Only recipients at or below this current health (0 = off). |

Tags are your own convention: decide what each bit means (the Basic sample uses bit 0 = support, bit 1 = heavy).

## Impact payload (`Damage > Impact`)

Extra work after a resolved hit, rolled once per hit:

| Field | Meaning |
|---|---|
| `Enabled`, `Chance` | Turn on; probability per eligible hit. |
| `Trigger On Zero Damage` | Also trigger on hits that removed no health (control-only attacks). Immune targets never trigger. |
| `Targets` | Extra victim eligibility, checked before the damage is applied. |
| `Use Secondary Damage` + `Secondary Damage` | An independent extra hit centred on the victim (give it a radius for a blast). |
| `Area` | A residual region left at the impact point, even if the victim died (status effect and/or pulse). |
| `Use Displacement` + `Displacement` | Moves a **surviving** victim along its own path and lane: negative = back toward the entry (knockback), positive = toward the exit. Clamped to the path; blockers are released. |
| `Use Transfer` + `Destination` | Moves a **surviving** victim to an exact path point (after any displacement); see [Path destination and transfer](#path-destination-and-transfer). A payload with only a transfer needs no dummy damage. |

Events: `ImpactPayloadTriggered` (IntValue bits: secondary damage 1, area 2, displacement 4, path transfer 8), `Displaced`, `PathTransferred`.

## Region pulses, pulse-only regions and healing

Every area effect (`AreaEffectData`: tower/skill actions, spells, enemy auras, impact payloads, projectile impact areas) can carry a `Pulse`:

| Field | Meaning |
|---|---|
| `Enabled`, `Id` | Turn on; event key (also the ring colour key). |
| `Use Damage` + `Damage` | Single-target hit on every occupant per scan (the region is the area; the damage radius is ignored). |
| `Use Healing` + `Healing` | `Amount` + `Maximum Health Share` restored to every occupant per scan (never above maximum health; not affected by damage multipliers). |
| `Targets` | Extra occupant eligibility. |
| `Color`, `Vfx` | Ring colour and optional VFX per pulse. |

Occupants are re-scanned every `Interval`; nothing lingers after a unit leaves. **Leave `Effect` empty for a pulse-only region** – no dummy status effect is needed. `Targets Enemies` selects the enemy faction (so an enemy aura with `Targets Enemies` on heals other enemies). Event: `AreaPulsed` (Value = radius, IntValue = occupants affected, Key = pulse id).

**Periodic healing** on a status effect (`Healing`): `Healing`, `Interval`, `Heal On Attach`, `Heal On Expire` (natural expiry only). Refreshing the effect does not reset its cadence. Event: `Healed`.

## Shields

A status effect with `Shield` enabled gives each accepted attachment its own shield:

| Field | Meaning |
|---|---|
| `Amount` + `Maximum Health Share` | Capacity, snapshotted when attached. |
| `Channels` | Damage kinds absorbed (after armor and resistance). Execute and despawn hits bypass shields. |
| `Refill On Refresh` | Re-applying at equal rank refills the shield; otherwise the remaining capacity is kept. |

Several shields absorb in attachment order; removing the effect discards unused capacity. Events: `ShieldChanged` (Value = capacity, 0 when gone), `ShieldAbsorbed`. The view draws a bubble that fades with the remaining capacity.

## Combat modifier (`Modifier > Combat`)

| Field | Meaning |
|---|---|
| `Range Scale` | Multiplies attack ranges, including melee contact (area sizes are not scaled). Tower range support or "nearsighted" debuffs. |
| `Disable Attacks` | No attacks or ability actions; movement and recovery continue (for example a tower jam). |
| `Ignore Blocking` | Cannot be blocked; current blockers are released (dashes). |
| `Untargetable` | Attacks cannot select the unit (concealment); status effects keep their own rules. |

Stacked flags are reference-counted and fully reversed on removal. Events: `CombatControlChanged` (IntValue bits: attacks disabled 1, ignores blocking 2, untargetable 4), `AttackRangeChanged`. The view greys out disarmed units and draws untargetable units translucent.

## Traps (`Action > Use Trap`)

A fixed-position deployment (mine, snare, glyph). It arms after a delay, then hits the nearest eligible unit inside its detection radius until its triggers or lifetime run out.

| Field | Meaning |
|---|---|
| `Id` | Event key and marker colour key; also the population-limit key (per source). |
| `Damage` | Hit on trigger. An area packet (`Radius` > 0) is centred on the trap; a single-target packet hits the triggering unit. May carry effects, an impact payload and life steal. |
| `Trigger Radius` | Detection ellipse, independent of the damage radius. |
| `Lifetime`, `Arm Delay` | Total lifetime (including arming) and the delay before it can trigger. A trap never acts in the tick it was placed. |
| `Max Triggers`, `Trigger Cooldown` | Activations before it is used up, and the delay between them (at most one per tick). |
| `Population Limit` | Live traps with this id per source (0 = unlimited). When full, the action does not succeed and its cooldown does not restart. |
| `Area` | Optional region left at the trap on every trigger (status effect and/or pulse). |
| `Targets Enemies`, `Targets Flying`, `Targets Ground`, `Targets` | Who triggers it. Area victims use normal damage eligibility. |
| `Cancel With Source` | Off (default): the trap outlives its source with the damage multiplier and hero credit captured at placement. On: removed when the source dies. |
| `Placement`, `Placement Range`, `Offset` | `Source` (actor position), `Rally` (barracks/hero rally point, else the actor) or `Opponent` (nearest eligible unit within the range). The offset is added before validation. |
| `Use Custom Point Rule` + `Point Rule` | Placement validation; by default the point is snapped onto the nearest lane. A rejected point cancels the activation. |
| `Color`, `Vfx` | Marker colour and optional VFX per trigger. |

Traps come from a fixed pool (`SimConfig.WithAdvancedCapacity`, default 128). Remaining friendly traps do not delay victory. Code can also place one at an explicit point: `Simulation.PlaceTrap(def, point, sourceId)` / `RemoveTrap(id)`.

Events: `TrapPlaced` (IntValue = trap id, Value = lifetime), `TrapArmed` (Value = detection radius), `TrapTriggered` (OtherId = triggering unit, Value = damage radius), `TrapRemoved` (Value = `MechanicEndReason`: Completed, Expired, SourceLost, Cancelled). The view draws a dim pulsing marker while arming, a solid marker with a detection ring once armed, a flash and blast ring per trigger, and fades the marker out on removal.

Spells cannot place traps yet (a spell has no action payload); use a hero skill or a tower ability.

## Mine fields (`Action > Use Mines`)

Automatic mine laying for towers, hero skills and enemy behaviors (core: `DeploymentPlanDef` with a `TrapDef` payload). Each activation picks **one lane node** of a level path inside a distance band around the producer – a seeded, deterministic pick among the valid nodes, not the spot under an enemy – reserves it together with a trap slot, throws the mine (flight, landing, then the arming delay) and leaves a trap that bursts under the first eligible unit.

| Field | Meaning |
|---|---|
| `Id` | Event key: marker colour, keyed audio cue, mine limit key. An art set entry with this key replaces the generated marker. |
| `Damage`, `Trigger Radius`, `Max Triggers`, `Area`, `Targets …` | As for traps: an area packet re-searches its victims around the mine; a single-target packet hits the triggering unit. A detection radius of about a quarter to a third of the blast radius reads well. |
| `Lifetime` | Counted **from the throw**: flight, landing and arming use it up. An unused mine fades out without exploding. |
| `Arm Delay` | After the landing preparation. |
| `Keep When Source Lost` | On (default): mines already laid stay when the producer is sold or dies, with their damage multiplier and hero credit captured at the throw. |
| `Minimum Distance`, `Maximum Distance` | The placement band (range ellipses around the producer). Only lane **nodes** inside it are candidates; denser node runs are picked more often. |
| `Side Clearance` | Minimum horizontal offset of a site from the producer. |
| `Minimum Spacing`, `Spacing Scope` | Distance to other mines, including those still in flight; `Owner` checks this producer's mines, `Global` every deployment (spell traps too). |
| `Max Mines` | Mines of this id alive or in flight per producer. A full field **rejects** the throw (old mines are never replaced); the action then does not succeed and its cooldown does not restart. |
| `Transit Duration`, `Settle Duration` | Flight time and landing preparation (the mine cannot trigger before `transit + settle + arm delay`). |
| `Use Custom Point Rule` + `Point Rule` | Terrain check for every candidate node; a node the rule would move is skipped. |

No candidate means no throw – there is no fallback spot. A mine whose lifetime ends in the same tick an enemy reaches it **explodes** (detection wins); expiry itself never explodes. Events: `TrapPlaced` and `DeploymentReserved` (IntValue = trap id, Position = site), `DeploymentInTransit`, `DeploymentLanded`, then the trap events `TrapArmed`, `TrapTriggered`, `TrapRemoved` (Value = `MechanicEndReason`). The view throws the marker along an arc from the producer, flashes the landing spot, shows the detection ring once armed with a short fuse blink, draws the blast and lets an expired mine sink and fade slowly. The Workshop's tower **Mechanics** tab has **+ Mine-laying ability** for a ready two-rank ability.

## Companions (`Hero` / `Tower > Companions`)

Owner-bound slots (core: `CompanionDef`, template custom data). Each slot keeps one child alive; a fallen child is replaced `Refill Delay` seconds after **its** death. Child damage earns the owner experience.

| Field | Meaning |
|---|---|
| `Unit` | A Soldier asset. Ground escorts: not flying, with melee to block. Flying followers: `Flying` on (Soldier asset), usually with a ranged attack. |
| `Slots`, `Mode` | `Ground Escort` walks, blocks and fights like a soldier and takes new places around the owner on every hero move order or rally point. `Flying Follower` flies after the owner and never blocks; it attacks from where it is. |
| `Refill Delay`, `Initial Delay` | Refill after a loss; first arrival after the owner appears. |
| `Formation Radius` | Ground escorts' places around the owner's last move / rally point. |
| `Follow Start Distance`, `Follow Stop Distance`, `Acceleration` | Flying followers: start moving beyond the start distance, stop at the stop distance (start must be larger). |
| `Wait On Owner Death` | On (default): children return to the dead owner and stop fighting; they reconnect when it comes back. |
| `Remove With Owner`, `Reconnect On Return` | On (default): children leave when a tower is sold; waiting children rejoin a returning hero (off: they leave instead). `Remove With Owner` off: they stay on as independent units. |
| `Rally Radius` | Towers without barracks: how far a `SetRallyPoint` command may move the escorts (`Simulation.TryResolveRallyPoint`). The sample HUD offers the rally button on barracks only; on a barracks the escorts follow its rally point. |
| `Use Custom Point Rule` + `Point Rule` | Ground spawn / reposition points (default: on a lane). An invalid point leaves the slot empty. |

Empty friendly slots never hold victory. Events: `CompanionSpawned` (EntityId = child, OtherId = owner, IntValue = slot, Key = child template), `CompanionWaiting`, `CompanionReconnected`, `CompanionRetired`, `CompanionDetached`. The view draws a short tether and a ring where a child arrives, dims waiting children and fades retiring ones out. The Validator reports flying mismatches as errors (the level would not start).

## Return on the spot (`Enemy > Revive`)

The same unit lies down when killed, gets `Return Share` of its maximum health back after `Down Delay`, rises for `Rise Duration` and walks on with the same identity (core: `ReviveDef`). `Returns` counts over its lifetime; the death after the last one is final. While down it neither moves nor fights; while rising it may ignore damage (`Invulnerable While Rising`) and be skipped by attacks (`Untargetable While Rising`), independently. `Clear Effects` removes its status effects when it falls.

Its bounty is paid **once** (on the first death) and a split on death (`Death Summon`) happens only after the last return. Pending returns hold victory. Events: `Died`, then `UnitDowned` (IntValue = returns used), `UnitRising` (Value = rise time), `UnitRevived`. The view keeps the unit (no death fade), turns it onto its side and darkens it, hides its health bar, and tweens it upright while it rises. The Sandbox counts falls separately from kills.

## Successor rules (`Enemy > Death Succession`)

Extra rules for the enemies released by `Death Summon` (core: `SummonDef.WithDeathSuccession`): `Chain Budget` – death releases the whole lineage may make (one release can hold several siblings; 1 = successors do not release again), `Rise Duration` – successors rise before they act (optionally invulnerable / untargetable), `Bounty Policy` – `Once Per Lineage` (a lineage never pays twice) or `Suppress Successor`. A lineage leaks one life cost at most once, whichever member gets through. Successors inherit the dead unit's path position and travel direction.

## Raising the fallen (`Action > Use Raise`)

Killed units leave a **body** (a neutral record: position, path position, side, kind, tags, cause). A raise action reserves the closest eligible bodies (ties by body order), casts for `Cast Delay`, then consumes each body and creates `Unit` there (core: `RaiseRemainsDef`). An Enemy result is hostile and continues the body's path; a Soldier result fights for the player.

| Field | Meaning |
|---|---|
| `Id`, `Color`, `Vfx` | Event key, cast colour, optional VFX where a body is raised. |
| `Unit` | Created from each body; the body's own stats are not copied. |
| `Range`, `Max Count` | Body search radius around the caster and bodies per activation. |
| `Cast Delay`, `Rise Duration`, `Reservation Timeout` | Reservation to consumption; the result's rise time; the time-out (0 = cast delay + 1 s). |
| `Bodies`, `From Enemies / Soldiers / Heroes`, `Required Tags` | Whose bodies qualify. Hostile results need a body that was on a path. |
| `Skip Suppressed Deaths`, `Skip Executed`, `Minimum Age`, `Maximum Age` | Cause and age filters (maximum 0 = until the body decays). |
| `Population Limit`, `Chain Budget` | Raised units of this caster at once (reservations included); raises a lineage may make (1 = a raised unit's body cannot be raised again). |
| `Invulnerable While Rising`, `Untargetable While Rising` | Protection of the raised unit while it rises. |

A caster that moves, is stunned or dies releases its reservations; a body that decays is not extended by a reservation. The body is consumed only after the new unit is created, so a full entity pool releases the reservation instead. Raised enemies share the body's lineage, so they pay no second bounty. Bodies are kept by the **Simulation Runner** (`Remains Capacity`, default 256, 0 keeps none; `Remains Lifetime`, default 10 s; core: `SimConfig.WithRemains`); a full store does not push old bodies out. Reserved bodies hold victory; unreserved ones do not.

Events: `RemainsCreated` (EntityId = dead unit, IntValue = body id), `RemainsReserved` (EntityId = caster, Value = cast delay), `RemainsReleased`, `RemainsConsumed` (OtherId = new unit). In levels where something raises bodies the view draws a small body marker for each available body (art set key `remains` replaces it), makes a reserved body glow, draws a tether from the caster for the cast time and flashes where the unit rises (the new unit starts lying and gets up).

## Beams (`Action > Use Beam`)

A continuous single-target channel with an **exact total damage budget** split over pulses.

| Field | Meaning |
|---|---|
| `Id` | Event key; beam colour and width key. |
| `Damage` | Channel (`Kind`), pierce, on-hit effects, impact payload and life steal. `Minimum`/`Maximum` and `Radius` are ignored – the budget decides the amount. |
| `Total Damage` | Raw damage of one channel before defenses, multiplied once by the source's damage multiplier and rounded up. |
| `Pulse Count`, `Interval`, `First Delay` | The budget is split evenly; earlier pulses take the remainder (100 over 3 pulses = 34, 33, 33). |
| `Range` | Targeting range and tracking limit; the beam ends when the target leaves it. The target is never switched. |
| `Targets`, `Targets Flying`, `Targets Ground` | Rechecked on every pulse. |
| `Cancel With Source` | On (default): ends when the source dies, is stunned or disarmed, or is ordered to move. Off: continues from the source's last position. |
| `Color`, `Width`, `Vfx` | Line look and optional VFX on the target per pulse. |

The budget is counted before armor, shields and hooks: mitigated, absorbed or rejected slices are not refunded, and an interrupted beam does not deal its remainder. Unfinished beams count as pending work. Pool: `SimConfig.WithAdvancedCapacity` (default 64); code can stop one with `Simulation.CancelBeam(id)`.

Events: `BeamStarted` (IntValue = beam id, OtherId = target, Value = captured budget), `BeamPulsed` (Value = raw slice), `BeamEnded` (Value = `MechanicEndReason`: Completed, TargetLost, OutOfRange, SourceLost, Interrupted, Cancelled). The view keeps one pooled line per beam from start to end, following the source and target views, widening on every pulse and fading out at the end.

## Reflection (`Enemy > Reflection`)

Thorns: when the unit loses health, a `Share` of the **actual** loss (shield absorption and overkill excluded, rounded up) is returned to the attacker as one single-target hit of `Kind` (with optional pierce).

- Reflected hits never reflect again and never steal life, so two reflecting units cannot loop.
- Dead attackers, attackers without health (towers) and self-damage are skipped; a unit that dies from the hit still reflects it.

Event: `DamageReflected` (EntityId = reflecting unit, OtherId = attacker, Value = returned raw amount, Key = `Id`). The view draws a short line from the reflecting unit to the attacker and a flash on the attacker in the reflection `Color`.

## Life steal (`Damage > Life Steal`)

The attacker recovers `Health Share` × the health this packet actually removed, plus `Flat Healing` per qualifying hit, up to its missing health.

| Field | Meaning |
|---|---|
| `Id`, `Color` | Event key and feedback colour. |
| `Health Share`, `Flat Healing` | Healing formula. |
| `Include Periodic` | Also steal from the damage-over-time ticks of effects carried by this packet. |
| `Heal Credit Owner` | Heal the hero credited with the hit instead of the immediate source (for example a hero's trap or summon). |

Units without health (towers) cannot be healed. Events: `LifeStolen` (EntityId = healed unit, OtherId = victim, Value = restored health) and the usual `Healed` (heal numbers). The view draws a thin line from the victim to the healed unit.

## Path destination and transfer

A **path destination** (`Path Index`, `Node Index`, `Lane Index`, `Progress`, `Clear Effects`) is an exact point on a level path: the segment starting at `Node Index`, `Progress` of the way to the next node. `Lane Index` -1 keeps the unit's lane (modulo the destination's lane count). It is checked against the level when used: a path, lane or node outside the path's entry..exit range moves nothing (the validator reports it as an error for the level's towers and heroes).

A **transfer action** (`Use Transfer` + `Transfer`: `Id`, `Destination`, `Range`, `Max Targets`, `Targets`) moves up to `Max Targets` path-following enemies within `Range`, nearest first. Hits can do the same through `Impact > Use Transfer`.

A moved unit is released from blockers, its attack cycles restart, its own cancellable chains and beams end, and with `Clear Effects` its effects are removed. Event: `PathTransferred` (EntityId = unit, OtherId = source, IntValue = path index, Value = progress, Position = destination). The view snaps the unit (no sliding across the map), draws a trail from where it was and replays its appear pop; the trail colour is the registry's `Transfer Color`.

## Permanent auras (`Area > Until Source Lost`)

An area with `Until Source Lost` has no timed expiry: it lasts while its source is alive and is removed – together with the effects it attached – when the source dies or is removed. Heroes re-emit their permanent auras when they return. Attached effects still follow their own duration and refresh rules; only the region's lifetime is permanent.

Use it for enemy `Aura`s. A spell or impact area has no living source and emits nothing; on an ability action every activation would add another permanent region, so the validator warns in both cases.

## Combining in actions

An ability, hero skill or enemy behavior action can combine its built-in payloads (`Attack`, `Self Effect`, `Summon`, `Area`) with `Use Chain`, `Use Multi Target`, `Use Trap`, `Use Mines`, `Use Beam`, `Use Transfer`, `Use Raise` and a `Custom Action` asset ([Extending the Framework](extending.md#5-ability-action)). They run together on the action's cooldown. The action succeeds when any payload succeeds; only then does the cooldown restart and a hero earn `Skill Experience Per Rank` × rank (core: `new AbilityActionDef(action, cooldown, initialDelay, skillExperiencePerRank)`).

The enemy **Mechanics** fields include:

- `Tags` – their tag bits.
- `Behavior` – always-on action channels (for example "every 7 s, shield nearby allies").
- `Aura` – a region emitted when the unit appears. For a permanent aura enable `Until Source Lost` (and `Follow Source`).
- `Reflection` – thorns.
- `Death Summon` + `Death Succession` – split on death and the successor rules.
- `Revive` – return on the spot.

## Projectile accuracy

Ballistic and straight shots aim where the target will be along its actual path when the shot lands, with the same flight time used for aiming and for the flight (fixed `Flight Time`, or solved from distance and speed). Blocked, stunned or stopped targets are not led. Homing shots track; instant shots hit at once. The Dry Run reports, per source, ballistic shots fired, landed, damaging, landed after the target was already gone, and landed beside a live target (with the average miss distance).

## In the Basic sample

| Content | Mechanics used |
|---|---|
| Storm Spire › **Arc Lightning** | Chain attack (4 → 6 victims, 20% weaker per jump) |
| Volley Nest › **Split Volley** | Multi-target attack |
| Cannon III › **Concussion Shell**, Warden › **Shield Bash** | Impact payload with knockback; `Targets` rejects the *heavy* tag (Brutes) |
| Void Spire › **Null Lance** | Beam: 140 → 200 magic damage over 8 → 10 pulses |
| Void Spire › **Rift** | Path transfer: the two nearest light enemies go back to the north road's second node |
| Garrison III › **Caltrops** | Trap at the rally point: arms after 1 s, area burst plus a short chill region, up to 2 → 3 live |
| Warden › **Snare** | Trap placed under the nearest enemy; trap-only action that still awards skill experience |
| Warden blade | Life steal (25% of health removed) |
| **Brute** enemy | Reflection: 25% of the health it loses goes back to its attacker as physical damage |
| **Mender** enemy | Behavior action casting the **Ward** shield effect on nearby allies; permanent pulse-only healing aura (`Effect` empty, `Until Source Lost`) |
| **Ward** status effect | Shield with refill on refresh |

The mine field, companion and revival samples are prepared by `SampleContentGenerator.GenerateReleaseMechanicSamples` (also callable with `-executeMethod`): Volley Nest › **Barbed Mines** (mine field, venom blast, 3 → 5 mines), Warden › **Hound** (ground-escort companion, refilled 10 s after it falls), **Revenant** (returns once with half its health) and **Gravecaller** (raises up to two **Husks** from nearby enemy bodies). The full sample generator already connects Revenants and Gravecallers to later waves in all three sample levels, gives the Warden its Hound, and adds Barbed Mines to Volley Nest. The standalone method updates only those mechanic assets.

## Coding against the definitions

```csharp
using TDMaker.Core.Defs;

var arc = new ChainAttackDef("arc", new DamageDef(DamageKind.Electric, 20, 30), range: 3, linkRange: 1.6f, maxTargets: 4, linkScale: 0.8f);
var chainAction = new AbilityActionDef(arc, cooldown: 5);                     // a chain is an IAbilityAction

var knockback = new DamageDef(DamageKind.Physical, 10, 15)
    .WithImpact(new ImpactPayloadDef(displacement: new PathDisplacementDef(-1.2f)));

var heal = AreaEffectDef.CreatePulse(new AreaPulseDef("mend", healing: new HealingDef(5)), radius: 1.6f, duration: 1, interval: 1.5f,
    followSource: true).WithOwnerLifetime();                                     // permanent pulse-only region
var aura = new AuraDef(heal);

var caltrops = new TrapDef("caltrops", new DamageDef(DamageKind.Explosion, 20, 30, radius: 0.9f), triggerRadius: 0.6f, lifetime: 20,
    armDelay: 1, populationLimit: 2, placement: TrapPlacement.Rally);
var lance = new BeamDef("lance", new DamageDef(DamageKind.Magical, 1, 1), totalDamage: 140, pulseCount: 8, interval: 0.2f, range: 3.6f);
var snare = new AbilityActionDef(caltrops, cooldown: 9, initialDelay: 1, skillExperiencePerRank: 3);  // hero skill XP on a trap-only action

var drain = new DamageDef(DamageKind.Physical, 10, 16).WithLifeSteal(new LifeStealDef("drain", healthShare: 0.25f));
var thorns = new EntityRulesDef().WithReflection(new ReflectionDef("thorns", 0.25f, new DamageDef(DamageKind.Physical, 1, 1)));
var rift = new PathTransferDef("rift", new PathDestinationDef(pathIndex: 0, nodeIndex: 1), range: 3, maxTargets: 2);

var mines = new DeploymentPlanDef(new TrapDef("mines", new DamageDef(DamageKind.Explosion, 30, 45, radius: 1), triggerRadius: 0.3f, lifetime: 30, armDelay: 0.5f),
    minimumDistance: 0.6f, maximumDistance: 3, minimumSpacing: 0.6f, populationLimit: 4, transitDuration: 0.6f, settleDuration: 0.2f);
var mineAction = new AbilityActionDef(mines, cooldown: 5);                      // a deployment plan is an IAbilityAction
var withHound = heroTemplate.WithCustomData(new CompanionDef("hound", slots: 1, refillDelay: 10));
var revenant = enemyTemplate.WithCustomData(new ReviveDef(returns: 1, downDelay: 1.5f, riseDuration: 1, returnShare: 0.5f));
var raise = new RaiseRemainsDef("raise", "husk", range: 2.4f, maxCount: 2, castDelay: 1.2f, riseDuration: 1, populationLimit: 4);
var config = new SimConfig(30, 0.8f).WithRemains(capacity: 256, lifetime: 10);

var ward = new StatusEffectDef("ward", duration: 5).WithShield(new ShieldDef(amount: 30, refillOnRefresh: true));
var jam = new StatusEffectDef("jam", duration: 3, modifier: new StatModifierDef().WithCombat(new CombatModifierDef(disableAttacks: true)));
```
