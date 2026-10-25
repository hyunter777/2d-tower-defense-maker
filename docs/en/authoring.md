# Authoring Reference

All gameplay content is authored as ScriptableObjects (**Create > 2D Tower Defense Maker > …**) plus a few scene components (**Add Component > 2D Tower Defense Maker > …**). At Play, `LevelAsset.Bake()` turns them into immutable core definitions.

Units: distances in world units, times in game seconds, armor/resist values as fractions (0–1).

Contents: [Common data](#common-data) · [Enemy](#enemy) · [Tower](#tower) · [Soldier](#soldier) · [Hero](#hero) · [Projectile](#projectile) · [Status Effect](#status-effect) · [Spell](#spell) · [Wave Set](#wave-set) · [Level](#level) · [Scene components](#scene-components)

The built-in mechanic blocks (chains, multi-target attacks, impact payloads and knockback, pulses, healing, shields, combat modifiers, traps, beams, reflection, life steal, path transfers, permanent auras, mine fields, companions and on-site revival) are described in [Mechanic Library](mechanics.md); HUD, feedback, camera and audio components in [Presentation](presentation.md).

---

## Common data

### Identity and view (all entity assets: Enemy, Tower, Soldier, Hero)

| Field | Meaning |
|---|---|
| `Template Id` | Unique id inside a level. Blank = asset name. Two assets with the same id in one level fail the bake. |
| `Display Name` | Name in menus. Blank = asset name. |
| `View > View Key` | Lookup key for views. Blank = template id. |
| `View > Prefab` | Optional prefab (pooled). With no prefab, a matching ArtSet entry supplies the sprite; otherwise a primitive is generated. |
| `View > Shape / Color / Size` | Placeholder sprite (Square, Circle, Diamond, Triangle, Keep, Bastion, Spire, Hall, Blob, Arrowhead, Hulk, Shield, Crest, Dart, Orb, Wing). |
| `View > Show Health Bar` | Draw a health bar. |
| `View > Shaded` | Generated sprites use the outlined, shaded style (off = flat silhouettes). |
| `View > Facing` | `None`, `FlipSprite` or `ScaleX` (for multi-sprite rigs) to face the movement direction. |
| `View > Drive Animator` | Drive an `Animator` on the prefab with the standard parameters ([Presentation](presentation.md#entity-views)). |
| `View > Hooks` | Optional VFX prefabs and audio cues for spawn, attack, hit and death ([Presentation](presentation.md#presentation-hooks-vfx-and-audio)). |
| `Extensions` | Optional `TemplateExtensionAsset`s (your subclasses) that decorate the baked template, for example with custom data ([Extending the Framework](extending.md#2-custom-data-template-definition-runtime-component)). |

> Tip: add an `EntityView` component to custom prefabs to control sorting and which renderer is tinted; it is added automatically otherwise.

### Damage

| Field | Meaning |
|---|---|
| `Kind` | `Physical`, `Magical`, `True`, `Explosion`, `Electric`, `Poison`. See [Concepts – Damage pipeline](concepts.md#damage-pipeline). |
| `Minimum` / `Maximum` | Roll range. |
| `Radius` | 0 = single target; > 0 = area damage (range ellipse). |
| `Edge Multiplier` | Damage factor at the edge of the area, interpolated from 1 at the centre. |
| `Falloff` | `DistanceEndpoints` (max at centre → min at edge), `RolledLinear` (one roll × edge factor), `ConstantMaximum`. |
| `Physical Pierce` / `Magical Pierce` | Armor / magic resist ignored by this hit (subtracted). |
| `Effects` | Status effects attached to every unit this hit damages. |
| `Experience Rate` | Hero experience per point of health removed (hero attacks). |
| `Impact` | Optional payload after each resolved hit: secondary blast, residual region, knockback and/or a path transfer ([Mechanic Library](mechanics.md#impact-payload-damage-impact)). |
| `Life Steal` | Optional healing of the attacker from the health this hit actually removes ([Mechanic Library](mechanics.md#life-steal-damage-life-steal)). |

Secondary blasts and region pulses use the same fields without `Impact` and `Life Steal` (`BasicDamageData`), so payloads cannot nest.

### Melee

| Field | Meaning |
|---|---|
| `Enabled` | Off = no melee slot. Soldiers without melee cannot block. |
| `Damage` | Damage per strike. |
| `Cooldown` | Seconds between strikes. |
| `Range` | Contact range (range ellipse). |

### Ranged attack (list; each entry is an independent channel)

| Field | Meaning |
|---|---|
| `Range` | Horizontal semi-axis `r` of the range ellipse; vertical is `r × k`. |
| `Minimum Range` | Inner exclusion radius. |
| `Cooldown` | Seconds between attacks. |
| `Damage` | Damage per hit. |
| `Projectile` | Projectile asset; empty = instant hit. |
| `Targets Flying` / `Targets Ground` | Eligible target types. |

### Recovery (enemy regeneration, hero recovery)

| Field | Meaning |
|---|---|
| `Enabled` | Turn recovery on. |
| `Amount` / `Interval` | Health per recovery tick and seconds between ticks. |
| `Damage Grace` | Seconds without taking damage before recovery starts. |
| `Idle Only` | Only while not moving or fighting. **Turn off for enemies** (they are never idle). |

### Stat modifier (status effects and ability passives)

| Field | Meaning |
|---|---|
| `Speed Scale` | Movement multiplier (0.6 = 40% slow, 0 = rooted). |
| `Output Scale` | Outgoing damage multiplier. |
| `Input Scale` / `Magical Input Scale` | Incoming damage multipliers. |
| `Physical Shift` / `Magical Shift` / `Poison Shift` | Added armor / resist (fraction, may be negative). |
| `Stun` | Stops movement and attacks while active. |
| `Combat` | `Range Scale`, `Disable Attacks`, `Ignore Blocking`, `Untargetable` ([Mechanic Library](mechanics.md#combat-modifier-modifier-combat)). |

---

## Enemy

**Create > 2D Tower Defense Maker > Enemy** (`EnemyAsset`). Required for every unit a wave spawns.

| Group | Field | Meaning |
|---|---|---|
| Vitals | `Health` | Maximum hit points. |
| | `Physical Armor` / `Magical Armor` / `Poison Armor` | Damage reductions (0–1). |
| | `Speed` | Units per second along the lane. |
| Reward | `Gold` | Bounty when killed. |
| | `Life Cost` | Lives lost when it leaks. |
| Blocking | `Blockable` | Whether soldiers/heroes can block it. |
| | `Blocker Capacity` | How many friendly units can hold it at once. |
| | `Engagement` | Where blockers stand. `Contact Bias` X is this enemy's share of the horizontal gap (usually half its drawn body width plus a small gap), Y a signed world-Y shift; `Row Spacing` is the world-Y offset of the 2nd and 3rd blocker rows (they stand half of it closer). Blockers stand on the side the enemy walks toward, independent of melee range. |
| | `Flying` | Flying units ignore blocking and can only be hit by attacks with `Targets Flying`. |
| Combat | `Melee` | Attack used against blocking units. |
| | `Ranged Attacks` | Optional attacks against friendly units (they pick the closest). |
| Abilities | `Regeneration` | Recovery (keep `Idle Only` off). |
| | `Melee Evasion` | Chance to dodge each incoming melee strike. |
| | `Status Immunities` | Effect ids or families this unit ignores (e.g. `slow`). |
| Mechanics | `Tags` | Tag bits matched by `Required/Rejected Tags` of status effects and mechanic `Targets`. |
| | `Behavior` | Always-on action channels (same fields as ability actions), for example a periodic shield cast on nearby allies. |
| | `Aura` | Area effect emitted when the unit appears. For a permanent aura enable `Until Source Lost` (and `Follow Source`): it lasts while the unit lives and is removed with it. May be pulse-only (heal or damage pulses without a status effect). |
| | `Reflection` | Thorns: returns a `Share` of the health the unit actually loses to its attacker as one hit of `Kind` ([Mechanic Library](mechanics.md#reflection-enemy-reflection)). |
| | `Death Summon` | Enemies released where it dies (split); they continue along the path. |
| | `Death Succession` | Successor rules for the released enemies: `Chain Budget`, `Rise Duration`, `Bounty Policy`, rise protection ([Mechanic Library](mechanics.md#successor-rules-enemy-death-succession)). |
| | `Revive` | Return on the spot: `Returns`, `Down Delay`, `Rise Duration`, `Return Share`, `Invulnerable / Untargetable While Rising`, `Clear Effects` ([Mechanic Library](mechanics.md#return-on-the-spot-enemy-revive)). |

Inspector extras: effective HP against each damage kind and warnings (zero speed, full immunity). The validator warns about auras without a payload and auras that do not follow their unit, returns that never happen (`Returns` 0, no health back) and successor rules with nothing to release.

---

## Tower

**Create > 2D Tower Defense Maker > Tower** (`TowerAsset`). Each tier is a separate asset; tiers link through `Upgrades`.

| Group | Field | Meaning |
|---|---|---|
| Economy | `Cost` | Gold to build this tier, or to upgrade **into** it. |
| Tree | `Upgrades` | Next tiers. One entry = linear upgrade; two or more = branch. |
| Combat | `Ranged Attacks` | Attack channels. |
| | `Target Priority` | Default priority: First, Last, Strongest, Weakest, Closest. |
| Abilities | `Abilities` | Purchasable abilities (see below), usually on final branches. |
| Barracks | `Soldier` | Assigning a Soldier asset turns this tier into a barracks. |
| | `Soldier Count` | Living soldiers maintained. |
| | `Rally Radius` | Maximum distance tower → rally point (range ellipse). |
| | `Respawn Time` | Seconds before a fallen soldier is replaced. |
| | `Formation Radius` | Spread of the idle formation around the rally point. |
| Companions | `Companions` | Owner-bound escorts or a flying follower kept beside the tower; they leave when it is sold (see Hero > Companions and [Mechanic Library](mechanics.md#companions-hero-tower-companions)). |
| Text | `Description` | Shown in menus. |

Only towers listed in the level's `Available Towers` can be built; their upgrade tiers, soldiers and projectiles are collected automatically. Sale refunds come from the level's `Refund Share`; the old per-tower `Refund Ratio` field is hidden and unused.

### Abilities (tower abilities and hero skills)

`Abilities` / `Skills` entries (`AbilityData`):

| Field | Meaning |
|---|---|
| `Id` | Ability id; blank = display name. |
| `Display Name` / `Description` | Button text and tooltip. |
| `Reset Cooldown On Purchase` | Reset this ability's timers whenever a rank is bought. |
| `Ranks` | Ranks in purchase order. Each rank **replaces** the previous rank's payload. |

Each rank (`AbilityRankData`):

| Field | Meaning |
|---|---|
| `Cost` | Gold (tower) or skill points (hero). |
| `Required Level` | Hero skills only. |
| `Passive` | Stat modifier active while this rank is owned. |
| `Soldier Replacement` | Barracks only: living and future soldiers become this Soldier asset. |
| `Actions` | Timed action channels (below). |

Each action (`AbilityActionData`) runs on its own cooldown; payloads can be combined:

| Field | Meaning |
|---|---|
| `Cooldown` | Seconds between activations. |
| `Initial Delay` | Delay before a newly bought channel can fire. |
| `Skill Experience Per Rank` | Hero only: experience per successful activation × rank (also for actions that only carry a chain, multi-target, trap, mine, beam, transfer, raise or custom payload). |
| `Use Attack` + `Attack` | Fire an extra ranged attack. |
| `Self Effect` | Status effect attached to the owner. |
| `Use Summon` + `Summon` | Create units (see Summon). |
| `Area` | Emit an area effect region at the owner (may be pulse-only). |
| `Use Chain` + `Chain` | Chained attack jumping between nearby enemies ([Mechanic Library](mechanics.md#chain-attack)). |
| `Use Multi Target` + `Multi Target` | One activation hitting several targets ([Mechanic Library](mechanics.md#multi-target-attack)). |
| `Use Trap` + `Trap` | Place a trap that arms, then triggers on nearby units ([Mechanic Library](mechanics.md#traps-action-use-trap)). |
| `Use Beam` + `Beam` | Channel a continuous beam with an exact damage budget ([Mechanic Library](mechanics.md#beams-action-use-beam)). |
| `Use Transfer` + `Transfer` | Move nearby enemies to an exact path point ([Mechanic Library](mechanics.md#path-destination-and-transfer)). |
| `Use Mines` + `Mines` | Throw a mine onto a lane node in a band around the actor; it arms after flight, landing and its arm delay ([Mechanic Library](mechanics.md#mine-fields-action-use-mines)). |
| `Use Raise` + `Raise` | Raise new units (enemy or soldier) from nearby bodies of the fallen ([Mechanic Library](mechanics.md#raising-the-fallen-action-use-raise)). |
| `Custom Action` | Your own `AbilityActionAsset` subclass ([Extending the Framework](extending.md#5-ability-action)). |

Chain, multi-target, trap, mine, beam, transfer, raise and custom payloads run together as one custom payload; the action counts as successful when any of them succeeds (for example a trap placed, a mine thrown, a body reserved or a beam started). Only successful activations restart the cooldown and award skill experience.

> Tip: the tower inspector shows DPS against several armor values, range-ellipse size, cumulative investment and the refund using the level's `Refund Share` (the first level whose tower trees contain this tier; otherwise the default 0.6).

---

## Soldier

**Create > 2D Tower Defense Maker > Soldier** (`SoldierAsset`). Produced by barracks, ability replacements and reinforcement spells.

| Field | Meaning |
|---|---|
| `Health` | Maximum hit points. |
| `Physical Armor` / `Magical Armor` | Reductions. |
| `Speed` | Movement speed. |
| `Intercept Radius` | Radius around the rally point in which it engages enemies. |
| `Engagement > Contact Bias` | Its share of the horizontal gap to the enemy it blocks (X, usually half its drawn body width plus a small gap) and a world-Y shift; added to the enemy's share. |
| `Melee` | Required to block. |
| `Ranged Attacks` | Optional. |
| `Tags` | Tag bits for effect and mechanic eligibility. |
| `Flying` | Only anti-air attacks reach it. Needed by flying follower companions; keep it off for barracks soldiers and ground escorts. |

---

## Hero

**Create > 2D Tower Defense Maker > Hero** (`HeroAsset`). Add it to the level's `Heroes`.

| Group | Field | Meaning |
|---|---|---|
| Vitals | `Health`, `Physical Armor`, `Magical Armor`, `Speed` | Level-1 base values. |
| | `Engage Radius` | Radius in which an idle hero engages enemies. |
| | `Engagement > Contact Bias` | Same as on a Soldier: the hero's share of the horizontal gap to the enemy it blocks. |
| | `Recovery` | Health recovery (usually idle only). |
| Combat | `Melee`, `Ranged Attacks` | Attacks. |
| | `Experience Per Damage` | Experience per point of health the hero's attacks remove. |
| | `Tags` | Tag bits for effect and mechanic eligibility. |
| Growth | `Skill Mode` | `AutoUnlock` (ranks unlock automatically by level) or `SpendPoints` (player spends points). |
| | `Levels` | Growth rows; row 1 is level 1 at 0 XP. Each row: `Experience` (cumulative), `Skill Points` (total budget), `Health Scale`, `Damage Scale`, `Armor Bonus`, `Magic Resist Bonus`. |
| | `Difficulty Experience Scale` | Experience multiplier. |
| | `Skills` | Abilities with point costs and required levels (see Abilities). |
| Respawn & Movement | `Respawn Delay` | Seconds dead before returning. |
| | `Return Duration` | Seconds of invulnerable return. |
| | `Use Respawn Position` / `Respawn Position` | Return at a fixed point instead of where it fell. |
| | `Move Point Rule` | Which destinations a move order accepts (see Point rule). |
| Companions | `Companions` | Owner-bound companions (`CompanionData`): `Unit` (Soldier asset), `Slots`, `Mode` (Ground Escort / Flying Follower), `Refill Delay`, `Initial Delay`, `Formation Radius`, follow distances and `Acceleration` (followers), `Wait On Owner Death`, `Remove With Owner`, `Reconnect On Return`, `Rally Radius` (towers without barracks), optional `Point Rule` ([Mechanic Library](mechanics.md#companions-hero-tower-companions)). |

Level, experience and skills are kept when the hero dies. Companion damage earns the hero experience; ground escorts take new places on every move order.

---

## Projectile

**Create > 2D Tower Defense Maker > Projectile** (`ProjectileAsset`).

| Field | Meaning |
|---|---|
| `Kind` | `Instant` (immediate hit, beam drawn), `Straight` (fixed aim point), `Ballistic` (fixed aim point, visual arc), `Homing` (follows target). |
| `Speed` | Units per second. |
| `Arc Height` | Visual arc height (ballistic). |
| `Lifetime` | Seconds before an unresolved projectile expires. |
| `Flight Time` | Fixed flight time; 0 = distance / speed. |
| `Hit Radius` | Fixed-aim single-target shots still hit if the target is this close to the aim point. |
| `View Key` | Blank = asset name. Must be unique (validator warns). |
| `Impact Area` | Optional region created once where the projectile arrives, also on empty ground (status effect and/or pulse). |
| View: `Prefab`, `Shape`, `Color`, `Size`, `Impact Fx Size`, `Beam Width`, `Shaded`, `Trail Time`, `Trail Width`, `Splash Ring` | Presentation. |
| Hooks: `Launch Vfx`, `Impact Vfx`, `Launch Cue`, `Impact Cue` | Optional pooled VFX and audio. |

Straight and ballistic shots aim at a predicted position. Area-damage shots always explode at the aim point.

---

## Status Effect

**Create > 2D Tower Defense Maker > Status Effect** (`StatusEffectAsset`). Reference it from damage `Effects`, area effects, ability `Self Effect` or spells.

| Group | Field | Meaning |
|---|---|---|
| Identity | `Effect Id` | Used for duplicate checks; blank = asset name. |
| | `Display Name` | UI name. |
| | `Family` | Group name used by immunities and suppression (e.g. `slow`, `poison`). |
| | `Rank` | Strength; a higher rank can replace a lower one. |
| | `Duration` | Lifetime in seconds. |
| Stacking | `Stack Equal Rank` | Allow separate instances at equal rank. |
| | `Replace Lower Rank` | Replace lower-ranked instances of the same id. |
| | `Refresh Equal Rank` | Re-applying at equal rank refreshes the lifetime (modifiers are not applied twice). |
| Eligibility | `Required Tags` / `Rejected Tags` | Bit masks checked against the target's tags. |
| | `Forbidden Ids` / `Forbidden Families` | Cannot attach while one of these is present. |
| | `Remove Forbidden` | Remove existing forbidden effects instead. |
| Payload | `Modifier` | Stat modifier while attached (slow, stun, armor shift, …). |
| | `Periodic` | Damage over time: `Kind`, integer `Minimum`–`Maximum` per tick, `Interval`, optional `First Damage` on attach and `Last Damage` on natural expiry (negative = off). |
| | `Healing` | Healing over time: `Healing` (amount + share of maximum health), `Interval`, `Heal On Attach`, `Heal On Expire`. |
| | `Shield` | Damage-absorbing shield per attachment: `Amount`, `Maximum Health Share`, `Channels`, `Refill On Refresh` ([Mechanic Library](mechanics.md#shields)). |
| View | `Tint`, `Tint Strength`, `Icon` | Body tint and icon above affected units (shields also use the tint for their bubble). |

Units get their tags from the `Tags` field of Enemy, Soldier and Hero assets (32 bits in the Inspector). Effects with periodic damage, healing or a shield only attach to units with health.

---

## Spell

**Create > 2D Tower Defense Maker > Spell** (`SpellAsset`). Add it to the level's `Spells` (order = button order and number keys 1–9).

| Group | Field | Meaning |
|---|---|---|
| Identity | `Spell Id`, `Display Name`, `Description`, `Color` | Id (blank = asset name), button text, tooltip, button/preview colour. |
| Rules | `Kind` | `Reinforcement` (summon friendly units), `AreaStrike` (scattered timed strikes), `AreaEffect` (region only). |
| | `Cooldown` | Seconds; consumed only by an accepted cast. |
| | `Unlock Wave` | First wave in which it can be cast (0 = before the first wave). |
| | `Point Rule` | Accepted target points (below). |
| Payload | `Support` | Summon for `Reinforcement`. |
| | `Strikes` | `Damage` (needs a radius), `Projectile`, `Count`, `Interval`, `Delay`, `Scatter Radius`, `Placement Attempts`, `Launch Offset`, `Targets Flying/Ground`. |
| | `Area` | Optional lingering region at the target point (any kind). |

### Point rule (spells and hero movement)

| Field | Meaning |
|---|---|
| `Require Path` | Point must be near a lane; accepted points are projected onto it. |
| `Path Tolerance` | Maximum distance to the nearest lane (range ellipse). |
| `Use Bounds` / `Minimum` / `Maximum` | Restrict to a rectangle. |

The same rule is used for the HUD's valid/invalid preview and by the simulation when the command arrives.

### Summon

| Field | Meaning |
|---|---|
| `Unit` | Soldier asset (friendly) or Enemy asset (hostile). |
| `Count`, `Delay`, `Interval` | Units per activation and timing. |
| `Lifetime` | Seconds; 0 = permanent. |
| `Formation Radius` | Spread of friendly units. |
| `Cancel With Source` | Cancel pending units if the source dies. |
| `Population Limit` | Max alive + pending per source; 0 = unlimited. |

### Area effect

| Field | Meaning |
|---|---|
| `Enabled`, `Effect` | Region on/off and the status effect it attaches. Leave `Effect` empty for a pulse-only region. |
| `Radius`, `Duration`, `Interval` | Range ellipse, lifetime, seconds between scans. |
| `Until Source Lost` | Permanent region: ignores `Duration`, lasts while its source lives and is removed (with the effects it attached) when the source dies or is removed. Meant for auras; needs a living source, so spells and impacts emit nothing (the validator warns). |
| `Max Targets` | Recipients per scan; 0 = unlimited. |
| `Targets Enemies` | Enemies, otherwise friendly units. |
| `Follow Source`, `Remove On End` | Move with the source; strip effects when the region ends. |
| `Targets Flying`, `Targets Ground`, `Include Towers` | Recipient filters (`Include Towers` applies to attached effects). |
| `Pulse` | Direct damage and/or healing on every occupant at each scan ([Mechanic Library](mechanics.md#region-pulses-pulse-only-regions-and-healing)). |

---

## Wave Set

**Create > 2D Tower Defense Maker > Wave Set** (`WaveSetAsset`). Best edited in **Tools > 2D Tower Defense Maker > Wave Timeline**.

**Wave**

| Field | Meaning |
|---|---|
| `Auto Delay` | Seconds after the previous wave finished emitting before this wave starts by itself. |
| `Call Delay` | Seconds after the previous wave finished emitting before the player may call it early (clamped to `Auto Delay`). |
| `Early Gold Per Second` | Reward per rounded remaining second when called early (never for wave 1). |
| `Auto Start First` | Wave 1 only: start without waiting for the player. |
| `Groups` | Groups in this wave. |

**Group**: `Path Index` (index into the level's paths), `Start Delay` (after the wave starts), `Entries` (run in order).

**Spawn entry**

| Field | Meaning |
|---|---|
| `Enemy` | Enemy asset. Entries without an enemy are skipped. |
| `Count` | Number of units. |
| `Interval` | Seconds between units (the first unit appears one interval after the entry starts). 0 = one per tick. |
| `Start Delay` | Extra delay relative to when this entry is reached. |
| `Lane Selection` | `Fixed`, `RoundRobin` (starting at `Lane Index`), `Random`. |
| `Lane Index` | Fixed lane or first round-robin lane. |
| `Following Gap` | Delay before the next entry in the group. |
| `Alternate Enemy` / `Same Kind Limit` | Alternate between two enemies every N units (0 = off), sharing `Count`. |

---

## Level

**Create > 2D Tower Defense Maker > Level** (`LevelAsset`).

| Group | Field | Meaning |
|---|---|---|
| Geometry | `Paths` | Path data (centre line, `Lane Count`, `Lane Spacing`, `Entry Node`, `Exit Node` (−1 = last), per-node lane spacing, `Air Route`). Usually written from the scene (see Level Authoring). |
| | `Build Slots` | Slot position and default rally point. |
| Content | `Waves` | Wave Set asset. |
| | `Available Towers` | Base towers buildable on empty slots. |
| | `Extra Templates` | Additional entity assets to register (e.g. units spawned only by your scripts). |
| Economy | `Starting Gold`, `Starting Lives` | Initial values. |
| Ranges | `Override Range Y Scale` / `Range Y Scale` | Range ellipse ratio `k` for this level (otherwise the runner's value). |
| Rules | `Leak Bounty Share` | Share of bounty still paid on a leak (default 0). |
| | `Refund Share` | Sale refund after the first wave has started (default 0.6). |
| | `Override Early Call Rate` / `Early Call Reward Rate` | Use one rate for all waves instead of each wave's own. |
| | `Early Call Spell Cooldown Cut` | Early calls also shorten cooling spells. |
| | `Early Call Cut Threshold` | Remaining time must exceed this for the spell cut. |
| | `Victory Rating` | `Two Star Life Ratio` (default 0.5) and `Three Star Life Ratio` (default 1): share of starting lives (0..1) still left needed for two / three stars (inclusive). Rated by the simulation (`State.VictoryStars`). |
| Player | `Spells` | Spells in button order. |
| | `Heroes` | Heroes spawned at start. |
| | `Hero Spawn` | Spawn point (additional heroes are offset sideways). |

Inspector buttons: **Validate Bake**, **Wave Timeline**, **Validate Project**.

> Upgrading from an earlier build: the old level field `Star Rating` (fractions or absolute life counts, rated by the view) is migrated into `Rules > Victory Rating` automatically when the asset loads; absolute counts become `count / Starting Lives`. Save the asset once to store the migrated values.

> Nesting depth: the deepest authoring chain (ability → rank → action → attack → damage → impact payload → region → pulse → damage) is 9 levels, inside Unity's serialization limit of 10. If you add your own nested `[Serializable]` data below that, reference a ScriptableObject instead of nesting another class.

---

## Scene components

### Level Authoring (`2D Tower Defense Maker/Level Authoring`)

| Field | Meaning |
|---|---|
| `Level` | Level asset providing waves, economy, towers, spells, heroes. |
| `Paths` | Path components in index order; empty = all child `Path Authoring` in hierarchy order. |
| `Build Slots` | Slot components in index order; empty = all child `Build Slot Authoring`. |
| `Use Scene Geometry` | Off = use the level asset's own `Paths`/`Build Slots`. |

Buttons: **Write Scene Geometry To Level Asset** (copies paths and slots into the asset), **Validate Bake**, **Open Wave Timeline**.

### Path Authoring (`2D Tower Defense Maker/Path Authoring`)

| Field | Meaning |
|---|---|
| `Points` | Centre line in local space, entry → exit. |
| `Lane Count` / `Lane Spacing` | Parallel sub-lanes generated from the centre line. Lane 0 is on the left of the travel direction. |
| `Entry Node` / `Exit Node` | Where enemies appear / leak (−1 = last point). |
| `Point Lane Spacing` | Optional per-point spacing override (0 = default). |
| `Air Route` | Presentation only: `Level View` draws the path as a dotted flight line instead of a road and leaves it out of the ground texture. Use it for routes that only flying enemies take (assign them in the wave groups); the simulation treats it like any path. |
| `Gizmo Color` | Scene gizmo colour. |

Editing shortcuts: [Editor Tools](editor-tools.md#path-and-lane-editor).

### Build Slot Authoring (`2D Tower Defense Maker/Build Slot Authoring`)

| Field | Meaning |
|---|---|
| `Rally Offset` | Default barracks rally point, relative to the slot. The simulation projects it onto the nearest lane inside the tower's rally ellipse. |
| `Preview Tower` | Editor only: draws that tower's range and rally radius. |
| `Preview Range` | Editor only: range drawn when no preview tower is set. |
| `Preview Range Y Scale` | Y scale of the always-on gizmo. |

### Simulation Runner (`2D Tower Defense Maker/Simulation Runner`)

| Field | Meaning |
|---|---|
| `Scene Level` | Level Authoring in the scene (preferred). |
| `Level` | Level asset used when no scene level is set. |
| `Tick Rate` | Ticks per second (default 30). |
| `Range Y Scale` | Default `k` (0.8) unless the level overrides it. |
| `Spawn Heroes` | Spawn the level's heroes at start. |
| `Seed` / `Randomize Seed` | Random seed; randomizing makes runs non-reproducible. |
| `Time Scale` | Game speed (0 = paused). |
| `Catch Up Ticks Per Speed` | Catch-up limit: at most this × speed ticks per rendered frame (default 8, via the core `SimulationClock`). |
| `Start On Play` | Start automatically; otherwise call `StartSimulation()`. |
| `Starting Gold Override` | Debug: replaces the level's starting gold when 0 or more. |
| Capacities | `Entity Capacity` (1024), `Event Capacity` (8192 – events of one whole frame, see [Performance](performance.md#capacity-limits)), `Command Capacity` (128), `Effect Capacity` (4096), `Area Capacity` (256), `Schedule Capacity` (1024), `Chain Capacity` (64). See [Performance](performance.md#capacity-limits). |
| Bodies | `Remains Capacity` (256; 0 keeps none) and `Remains Lifetime` (10 s): bodies of the fallen kept for raise actions (`SimConfig.WithRemains`, script: `SetRemains`). A full store keeps its old bodies. |
| Recording & Replay | `Record Commands`, `Recording Capacity`, `Recording File`, `Replay On Start`, `Replay File` ([Determinism and Replay](determinism-and-replay.md#recording-and-replaying-with-simulationrunner)). |

Scripting: see [Presentation](presentation.md#simulationrunner-scripting) (`Simulation`, `Baked`, `Enqueue`, `Advance`, `SetPaused`, `SetSpeed`, `AddTemplateDecorator`, recording, events `SimulationStarted` and `EventRaised`).

### Entity View Registry (`2D Tower Defense Maker/Entity View Registry`)

`Runner` (auto-found), `Sprite Material` (empty = unlit material created at runtime), `Overrides` (view key → prefab, overrides asset prefabs), `Vfx Pool` and `Audio Player` (auto-found), `Prewarm Primitives`, `Death Fade Time`, `Splash Rings`, fallback colours per role, the mechanic toggles `Mechanic Arcs`, `Pulse Rings`, `Heal Glows`, `Trap Markers`, `Channel Beams`, `Reaction Lines`, `Transfer Color` (path-transfer trails), and for mines, companions and revival `Mine Flights`, `Remains Markers`, `Companion Color`, `Revive Color`, `Remains Color`. Art set keys: a mine's id replaces its marker sprite, `remains` replaces the body marker.

### Level View (`2D Tower Defense Maker/Level View`)

Placeholder level drawing: a generated ground (grass colours, `Pixels Per Unit`, `Ground Margin`, `Decoration Density`, `Seed`, `Tint Camera Background`), path/border/lane/slot/entry/exit colours, `Path Padding`, `Slot Size`, `Show Lanes`. Replace or disable it when you have real level art.

### Game HUD and other presentation components

`Game HUD`, `HUD Theme`, `Damage Numbers`, `VFX Pool`, `Audio Cue Player`, `Camera Controller`, `Game Settings` and `Ellipse Renderer` are described in [Presentation](presentation.md).

### TD Hud (`2D Tower Defense Maker/TD Hud`)

Minimal IMGUI HUD kept as a code reference and, in the sample, as the **F1** debug overlay of the Game HUD (`Overlay Only`). Fields: `Runner`, `Registry`, `World Camera` (empty = `Camera.main`), pick radii for slots and heroes, `Reference Height` for UI scaling, and preview colours.
