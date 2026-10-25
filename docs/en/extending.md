# Extending 2D Tower Defense Maker

The simulation core (`TDMaker.Core`) exposes extension points so you can add mechanics without editing package code. Before writing code, check the built-in [mechanic library](mechanics.md) (chains, multi-target attacks, knockback, pulses, healing, shields, combat modifiers, mines, companions and on-site revival) – it covers many common needs with data only.

| Extension point | API | Use it for |
|---|---|---|
| Custom system | `ISimSystem`, `Simulation.RegisterSystem(system, SimStage, after)` | New per-tick rules (hazards, weather, objectives) |
| Custom template data | `EntityTemplate.WithCustomData<T>(value)`, `template.CustomData.Get<T>()` | Immutable per-template configuration |
| Custom runtime component | `ICustomComponent`, `Simulation.RegisterComponent<T>(factory)`, `entity.CustomData.Get<T>()` | Mutable per-entity state |
| Target selector | `ITargetSelector`, `Simulation.RegisterTargetSelector` | Custom targeting for all ranged attacks |
| Damage hook | `IDamageHook`, `Simulation.RegisterDamageHook` | Damage caps, reactions, custom absorbs |
| Ability action | `IAbilityAction`, `new AbilityActionDef(action, cooldown)`, `AbilityActionAsset` | Custom timed actions on abilities, skills and behaviors |
| Command | `ICommand`, `ICommandHandler<T>`, `Simulation.RegisterCommandHandler<T>` | New player inputs |
| Event | `Simulation.PublishEvent(SimEvent)` with kinds ≥ `SimEventKind.CustomStart` | Notify the view |
| Spatial query | `Simulation.QueryEnemies(center, range, buffer)` | Find enemies in a range ellipse |
| State hash | `IStateHashContributor` | Include your state in `ComputeStateHash()` |
| Unity: template decorator | `SimulationRunner.AddTemplateDecorator`, `TemplateExtensionAsset` | Add custom data / rules to templates baked from assets |

## The Extending sample

Every code block on this page is taken from **`Assets/TDMaker/Samples/Extending/`** (assembly `TDMaker.Samples.Extending`), which is compiled with the package:

| File | Shows |
|---|---|
| `Scripts/HazardZoneSystem.cs` | Custom system + custom event |
| `Scripts/Barrier.cs` | Custom template data (`BarrierDef`) + runtime component (`BarrierState`) |
| `Scripts/LowestBarrierSelector.cs` | Target selector |
| `Scripts/BarrierDamageHook.cs` | Damage hook |
| `Scripts/RechargeBarrier.cs`, `Scripts/RechargeBarrierAction.cs` | Ability action, and its ScriptableObject wrapper for the Inspector |
| `Scripts/BarrierData.cs` | `TemplateExtensionAsset` adding custom data from the Inspector |
| `Scripts/Stance.cs` | Command, handler, custom event and replay codec |
| `Scripts/ExtendingSample.cs` | A MonoBehaviour that registers all of the above with a `SimulationRunner` |
| `Scripts/ExtendingSnippets.cs` | The short fragments of sections 5 and "Hosting the simulation" |
| `Scripts/MechanicDefinitionsExample.cs` | The code example of [Mechanic Library](mechanics.md) |

To try it, open the Basic sample scene, add **2D Tower Defense Maker > Samples > Extending Sample** to the `2D Tower Defense Maker` object and press Play: Brutes get a 40-point barrier that recharges, towers aim at the weakest barrier, and a hazard zone burns enemies near the map centre.

> The sample uses the name *barrier* for its custom absorb so it does not clash with the built-in `ShieldDef` (shields on status effects, see [Mechanic Library](mechanics.md#shields)). Prefer the built-in shield for content; the barrier exists to demonstrate the extension points.

## Rules for extension code

- **Register before the first `Step()`.** All `Register*` calls throw once the simulation has stepped.
- **Do not allocate in `Tick`.** Allocate buffers and objects up front. Use `SpatialQueryBuffer` instances you keep.
- **Keep shared definitions immutable.** Template data, ability actions and command objects are shared; put mutable state in custom components or in your system object.
- **Stay deterministic.** Use `sim.Random`, `sim.Time` / `sim.State.Tick`, and iterate in a stable order. Never use `UnityEngine.Random`, wall clock time or unordered dictionaries in the tick path.
- **Change state through the simulation.** Health is changed through `RequestDamage`; positions through `SetEntityPosition`; effects through `sim.Effects.TryAttach` / `EmitArea`; gold, lives and builds through commands.
- **Hash your state** by implementing `IStateHashContributor` on systems, components, commands, selectors and hooks (systems, command handlers, selectors and hooks that implement it are picked up automatically; others use `RegisterStateHashContributor`).

## Registering extensions in a Unity scene

`SimulationRunner` offers two hooks:

- **`AddTemplateDecorator(decorator)`** – called for every baked template on each (re)start, *before* the simulation is created. Return a changed template (for example with `WithCustomData` or `WithRules`); the id must stay the same. Register it in `Awake`/`OnEnable`.
- **`SimulationStarted`** – raised right after the simulation is created and before its first step, also after **Restart**. Register systems, components, hooks, selectors and command handlers here. The level's heroes are already queued; components registered now are also prepared for them.

From `ExtendingSample.cs`:

```csharp
// OnEnable runs before the runner's Start(), so the decorator and the hook are in place for the first simulation.
private void OnEnable()
{
    if (runner == null) return;
    runner.AddTemplateDecorator(Decorate);
    runner.SimulationStarted += Configure;
    runner.EventRaised += OnSimEvent;
    runner.CommandCodec = new StanceCodec();
    if (runner.Simulation != null) Debug.LogWarning("[2D Tower Defense Maker] ExtendingSample was enabled after the simulation started; restart to apply it.", this);
}

private void OnDisable()
{
    if (runner == null) return;
    runner.RemoveTemplateDecorator(Decorate);
    runner.SimulationStarted -= Configure;
    runner.EventRaised -= OnSimEvent;
}

/// <summary>Template decorator: custom data plus an always-on custom ability action.</summary>
private EntityTemplate Decorate(EntityTemplate template, EntityAssetBase asset)
{
    if (!barrierTemplates.Contains(template.Id)) return template;
    var recharge = new AbilityActionDef(new RechargeBarrier(rechargeAmount), cooldown: 2f, initialDelay: 1f);
    return template.WithCustomData(new BarrierDef(barrierAmount)).WithRules(AddBehavior(template.Rules, recharge));
}

/// <summary>Runs for every new simulation (start and restart) before its first step.</summary>
private void Configure(SimulationRunner source)
{
    Simulation sim = source.Simulation;
    sim.RegisterComponent(() => new BarrierState());
    sim.RegisterComponent(() => new StanceState());
    sim.RegisterDamageHook(new BarrierDamageHook());
    sim.RegisterSystem(new HazardZoneSystem(new Vec2(hazardCenter.x, hazardCenter.y), hazardRadius), SimStage.Damage, after: false);
    if (useBarrierSelector) sim.RegisterTargetSelector(new LowestBarrierSelector());
    sim.RegisterCommandHandler(new SetStanceHandler());
}
```

`WithRules` replaces the whole rules bundle, so the sample's `AddBehavior` helper copies the template's existing recovery, evasion, death summon, traits and behavior actions before appending its own action.

**Without code:** list a `TemplateExtensionAsset` (your subclass) in any entity asset's **Extensions** field and it decorates that template during the level bake. Custom ability actions can be picked in an action's **Custom Action** field through an `AbilityActionAsset` subclass (see sections 2 and 5).

## 1. Custom system

A system receives the simulation and the fixed `dt` once per tick at its position in the stage order. Systems registered at the same anchor run in registration order; `after: false` inserts before the built-in stage.

```csharp
using TDMaker.Core;
using TDMaker.Core.Defs;
using TDMaker.Core.Systems;

namespace TDMaker.Samples.Extending
{
    /// <summary>Deals true damage every second to enemies standing in a zone, and tells the view.</summary>
    public sealed class HazardZoneSystem : ISimSystem, IStateHashContributor
    {
        /// <summary>Custom event published on every pulse; Position is the zone centre and Value its radius.</summary>
        public const SimEventKind HazardPulse = SimEventKind.CustomStart + 1;
        private static readonly DamageDef Burn = new DamageDef(DamageKind.True, 3, 3);

        private readonly SpatialQueryBuffer hits = new SpatialQueryBuffer(1024); // allocated once
        private readonly Vec2 center;
        private readonly float radius;
        private double nextPulse;

        /// <summary>Creates a zone at <paramref name="center"/> with a range-ellipse <paramref name="radius"/>.</summary>
        public HazardZoneSystem(Vec2 center, float radius) { this.center = center; this.radius = radius; }

        /// <inheritdoc />
        public void Tick(Simulation sim, float dt)
        {
            if (sim.Time < nextPulse) return;
            nextPulse = sim.Time + 1.0;
            sim.QueryEnemies(center, radius, hits);            // same range ellipse as towers; ascending Id order
            for (int i = 0; i < hits.Count; i++)
                sim.RequestDamage(new DamageContext(0, hits[i].Id, Burn.Maximum, Burn));
            sim.PublishEvent(new SimEvent(HazardPulse, position: center, value: radius));
        }

        /// <inheritdoc />
        public void AppendStateHash(ref StateHasher hash) => hash.Add(nextPulse);
    }
}
```

Registered before the built-in Damage stage, so the damage is applied in the same tick:

```csharp
sim.RegisterSystem(new HazardZoneSystem(new Vec2(hazardCenter.x, hazardCenter.y), hazardRadius), SimStage.Damage, after: false);
```

`RequestDamage` goes through the same pipeline as built-in attacks: damage hooks, the FIFO queue, armor and resist, shields, on-hit effects and experience.

## 2. Custom data: template definition + runtime component

Immutable configuration lives on the template; mutable state lives in a prewarmed component that every entity bundle owns.

```csharp
using TDMaker.Core;
using TDMaker.Core.Defs;

namespace TDMaker.Samples.Extending
{
    /// <summary>Immutable barrier configuration, shared by every entity of a template.</summary>
    public sealed class BarrierDef
    {
        /// <summary>Barrier capacity.</summary>
        public readonly float Maximum;
        /// <summary>Creates the configuration.</summary>
        public BarrierDef(float maximum) { Maximum = maximum; }
    }

    /// <summary>Mutable per-entity barrier state, prewarmed for every entity bundle.</summary>
    public sealed class BarrierState : ICustomComponent, IStateHashContributor
    {
        /// <summary>Remaining and maximum capacity.</summary>
        public float Charge, Maximum;

        /// <summary>Runs on spawn and on template change (upgrade). template == null marks an unused pool bundle. Must not allocate.</summary>
        public void Reset(EntityTemplate template)
        {
            Maximum = template?.CustomData.Get<BarrierDef>()?.Maximum ?? 0;
            Charge = Maximum;
        }

        /// <inheritdoc />
        public void AppendStateHash(ref StateHasher hash) { hash.Add(Charge); hash.Add(Maximum); }
    }
}
```

Attaching the data:

```csharp
// In code (a SimulationRunner template decorator, or templates you build yourself):
return template.WithCustomData(new BarrierDef(barrierAmount)).WithRules(AddBehavior(template.Rules, recharge));

// Runtime side (before the first Step):
sim.RegisterComponent(() => new BarrierState());   // the factory must return a new instance each call

// Anywhere in the tick:
var barrier = actor.CustomData.Get<BarrierState>(); // null if the type was not registered
```

From the Inspector, a `TemplateExtensionAsset` does the same for one asset (create it with **Create > 2D Tower Defense Maker > Samples > Barrier Data** and add it to a unit's **Extensions** list):

```csharp
using TDMaker.Core.Defs;
using TDMaker.Unity.Authoring;
using UnityEngine;

namespace TDMaker.Samples.Extending
{
    /// <summary>Lets designers add <see cref="BarrierDef"/> to a unit through its Extensions list.</summary>
    [CreateAssetMenu(menuName = "2D Tower Defense Maker/Samples/Barrier Data", fileName = "BarrierData")]
    public sealed class BarrierData : TemplateExtensionAsset
    {
        /// <summary>Barrier capacity.</summary>
        [Min(0)] public float maximum = 40;

        /// <inheritdoc />
        public override EntityTemplate Apply(EntityTemplate template) => template.WithCustomData(new BarrierDef(maximum));
    }
}
```

`CustomData` slots are inherited through `BaseId`; a child template's value of the same type replaces the parent's.

## 3. Target selector

One selector replaces the default scoring for **every** ranged attack in the world (towers, soldiers, heroes, enemies). Candidates are an ephemeral, Id-ordered buffer from the spatial index; always filter with `IsEligibleTarget`. Return `null` to skip the attack.

```csharp
using TDMaker.Core;

namespace TDMaker.Samples.Extending
{
    /// <summary>Towers prefer the target with the weakest barrier; everything else uses "lowest health".</summary>
    public sealed class LowestBarrierSelector : ITargetSelector
    {
        /// <inheritdoc />
        public Entity Select(Simulation sim, in TargetQuery query, SpatialQueryBuffer candidates)
        {
            Entity best = null;
            float bestScore = float.MaxValue;
            for (int i = 0; i < candidates.Count; i++)
            {
                Entity target = candidates[i];
                if (!sim.IsEligibleTarget(target, query)) continue;    // lifecycle, faction, flying/ground, range ellipse
                float score = query.Actor.Tower != null
                    ? target.CustomData.Get<BarrierState>()?.Charge ?? 0
                    : target.Health.Current;
                if (best == null || score < bestScore || (score == bestScore && target.Id < best.Id))
                { best = target; bestScore = score; }
            }
            return best;
        }
    }
}
```

`query.Priority` carries the tower's current priority if you want to honour it. To fall back to the built-in choice for some actors, `return sim.FindDefaultTarget(query);` – it is safe to call from a selector. Do not call `FindTarget` from inside a selector (re-entry throws).

## 4. Damage hook

`BeforeDamage` runs when a request is queued and may change `Amount` (finite, ≥ 0) or set `Cancelled`. `AfterDamage` observes every accepted request after mitigation, including those that applied zero. Hooks run in registration order and must not request damage from `BeforeDamage`.

```csharp
using TDMaker.Core;

namespace TDMaker.Samples.Extending
{
    /// <summary>Absorbs raw damage with the target's barrier before armor and resistance.</summary>
    public sealed class BarrierDamageHook : IDamageHook
    {
        /// <inheritdoc />
        public void BeforeDamage(Simulation sim, ref DamageContext hit)
        {
            var barrier = sim.Entities.Get(hit.TargetId)?.CustomData.Get<BarrierState>();
            if (barrier == null || barrier.Charge <= 0) return;
            float absorbed = System.Math.Min(hit.Amount, barrier.Charge);
            barrier.Charge -= absorbed;
            hit.Amount -= absorbed;                     // raw amount, before armor and resist
        }

        /// <inheritdoc />
        public void AfterDamage(Simulation sim, in DamageResult result)
        {
            // result.AppliedAmount is the health actually lost.
        }
    }
}
```

```csharp
sim.RegisterDamageHook(new BarrierDamageHook());
```

Built-in shields (status effect `Shield`) absorb **after** armor and resistance; a `BeforeDamage` hook sees the raw amount before both.

## 5. Ability action

An `IAbilityAction` runs on an action channel's cooldown. Returning `true` consumes the cooldown; `false` retries next tick. Keep the action object immutable and store state in a custom component.

```csharp
using TDMaker.Core;

namespace TDMaker.Samples.Extending
{
    /// <summary>Custom ability action: refills the actor's barrier.</summary>
    public sealed class RechargeBarrier : IAbilityAction
    {
        private readonly float amount;

        /// <summary>Creates the action.</summary>
        public RechargeBarrier(float amount) { this.amount = amount; }

        /// <inheritdoc />
        public bool TryExecute(Simulation sim, Entity actor, int slotIndex, int actionIndex)
        {
            var barrier = actor.CustomData.Get<BarrierState>();
            if (barrier == null || barrier.Charge >= barrier.Maximum) return false;
            barrier.Charge = System.Math.Min(barrier.Maximum, barrier.Charge + amount);
            return true;
        }
    }
}
```

Using it from code:

```csharp
var recharge = new AbilityActionDef(new RechargeBarrier(rechargeAmount), cooldown: 2f, initialDelay: 1f);

// a) Always-on behavior of a unit template (ExtendingSample appends it to the existing rules):
EntityTemplate unit = template.WithRules(new EntityRulesDef(behavior: new AbilityRankDef(new[] { recharge })));

// b) Rank 1 of a purchasable tower ability (costs must match the rank count):
var ability = new AbilityDef(new AbilityExecutionDef(new[] { new AbilityRankDef(new[] { recharge }) }), "barrier_battery", 150);

// c) Add a custom payload to an existing built-in action:
AbilityActionDef combined = existingAction.WithCustomAction(new RechargeBarrier(5));
```

Using it from the Inspector: wrap it in an `AbilityActionAsset` and pick the asset in any action's **Custom Action** field (tower abilities, hero skills, enemy behaviors). It runs together with the action's other payloads.

```csharp
using TDMaker.Core;
using TDMaker.Unity.Authoring;
using UnityEngine;

namespace TDMaker.Samples.Extending
{
    /// <summary>Lets designers pick <see cref="RechargeBarrier"/> in an ability action's Custom Action field.</summary>
    [CreateAssetMenu(menuName = "2D Tower Defense Maker/Samples/Recharge Barrier Action", fileName = "RechargeBarrierAction")]
    public sealed class RechargeBarrierAction : AbilityActionAsset
    {
        /// <summary>Barrier restored per activation.</summary>
        [Min(0)] public float amount = 5;

        /// <inheritdoc />
        public override IAbilityAction CreateAction() => new RechargeBarrier(amount);
    }
}
```

The built-in `ChainAttackDef` and `MultiTargetAttackDef` are ability actions too; when an action uses several of chain, multi-target and a custom action, they are combined with `CompositeAbilityAction`.

## 6. Command and event

```csharp
using System.IO;
using TDMaker.Core;
using TDMaker.Core.Commands;

namespace TDMaker.Samples.Extending
{
    /// <summary>A tower stance chosen by the player.</summary>
    public enum Stance
    {
        /// <summary>Default behavior.</summary>
        Normal,
        /// <summary>Alternative behavior.</summary>
        Defensive
    }

    /// <summary>Custom player command: changes a tower's stance.</summary>
    public sealed class SetStance : ICommand, IStateHashContributor   // immutable
    {
        /// <summary>Tower entity.</summary>
        public int EntityId { get; }
        /// <summary>Requested stance.</summary>
        public Stance Stance { get; }
        /// <summary>Creates the command.</summary>
        public SetStance(int entityId, Stance stance) { EntityId = entityId; Stance = stance; }
        /// <inheritdoc />
        public void AppendStateHash(ref StateHasher hash) { hash.Add(EntityId); hash.Add((int)Stance); }
    }

    /// <summary>Per-entity stance state.</summary>
    public sealed class StanceState : ICustomComponent, IStateHashContributor
    {
        /// <summary>Current stance.</summary>
        public Stance Value;
        /// <inheritdoc />
        public void Reset(TDMaker.Core.Defs.EntityTemplate template) { Value = Stance.Normal; }
        /// <inheritdoc />
        public void AppendStateHash(ref StateHasher hash) => hash.Add((int)Value);
    }

    /// <summary>Applies <see cref="SetStance"/> and publishes a custom event.</summary>
    public sealed class SetStanceHandler : ICommandHandler<SetStance>
    {
        /// <summary>Custom event; EntityId is the tower and IntValue the new stance.</summary>
        public const SimEventKind StanceChanged = SimEventKind.CustomStart + 2;

        /// <inheritdoc />
        public CommandFailure Handle(Simulation sim, SetStance command)
        {
            Entity tower = sim.Entities.Get(command.EntityId);
            var state = tower?.CustomData.Get<StanceState>();
            if (state == null || tower.Tower == null) return CommandFailure.InvalidEntity;  // emits CommandRejected
            state.Value = command.Stance;
            sim.PublishEvent(new SimEvent(StanceChanged, tower.Id, intValue: (int)command.Stance, position: tower.Position));
            return CommandFailure.None;
        }
    }

    /// <summary>Optional: persists <see cref="SetStance"/> in replays (type ids ≥ 1024 are yours).</summary>
    public sealed class StanceCodec : ICommandCodec
    {
        /// <inheritdoc />
        public int GetTypeId(ICommand command) => command is SetStance ? 1024 : 0;
        /// <inheritdoc />
        public void WritePayload(BinaryWriter writer, ICommand command)
        { var c = (SetStance)command; writer.Write(c.EntityId); writer.Write((int)c.Stance); }
        /// <inheritdoc />
        public ICommand ReadPayload(int typeId, BinaryReader reader)
            => typeId == 1024 ? new SetStance(reader.ReadInt32(), (Stance)reader.ReadInt32()) : throw new InvalidDataException();
    }
}
```

Setup (before the first Step) and use:

```csharp
sim.RegisterComponent(() => new StanceState());
sim.RegisterCommandHandler(new SetStanceHandler());
runner.CommandCodec = new StanceCodec();          // lets the runner save and load replays containing SetStance

// From UI:
public void SetTowerStance(int towerId, Stance stance) => runner.Enqueue(new SetStance(towerId, stance));
```

Built-in command types cannot be replaced. A command type without a handler is rejected with `InvalidCommand`.

## How the view consumes events

`SimulationRunner.EventRaised` delivers every event in emission order once per frame, after the frame's ticks (the runner clears them afterwards). Subscribe from any MonoBehaviour – `ExtendingSample` does:

```csharp
private void OnSimEvent(in SimEvent e)
{
    switch (e.Kind)
    {
        case HazardZoneSystem.HazardPulse:
            if (hazardVfx != null && vfxPool != null) vfxPool.Spawn(hazardVfx, new Vector3(e.Position.X, e.Position.Y, 0));
            break;
        case SetStanceHandler.StanceChanged:
            Debug.Log($"[2D Tower Defense Maker] Tower #{e.EntityId} stance: {(Stance)e.IntValue}", this);
            break;
    }
}
```

Guidelines:

- Treat events as notifications; read current values from `runner.Simulation.State` and `runner.Simulation.Entities`.
- Several ticks can run in one frame; avoid expensive work per event (pool your effects with `VfxPool`).
- Look up authoring assets for an entity with `runner.Baked.TryGetAsset(entity.Template.Id, out var asset)`, `GetTower`, `GetHero`, `GetSpell(index)`, `TryGetProjectile(viewKey, …)`, `TryGetEffect(effectId, …)` or `TryGetMechanicVisual(key, …)` (chain, multi-target and pulse looks).
- For a custom HUD, read `Simulation.State` (gold, lives, wave, `CanCallNextWave`, `NextWaveRemaining`, `NextWaveWaitDuration`, `VictoryStars`) and `Simulation.Spells`, validate targets with `TryValidateSpellPoint` / `TryResolvePoint` / `TryResolveRallyPoint`, and show prices with `PreviewSellRefund`, `PreviewEarlyCallReward` and `PreviewEarlyCallSpellCooldownCut` – the same code the commands use ([Concepts](concepts.md#commands-and-events)).

## Hosting the simulation without `SimulationRunner`

```csharp
BakedLevel baked = levelAsset.Bake();
var sim = new Simulation(baked.Templates, baked.Level, new SimConfig(tickRate: 30, rangeYScale: 0.8f), seed: 1234);
// register extensions here
var clock = new SimulationClock(sim);           // catch-up limit = 8 × speed ticks per frame
// per frame:
clock.Advance(Time.deltaTime, speed: 1f);
for (int i = 0; i < sim.Events.Count; i++) { SimEvent e = sim.Events[i]; /* … */ }
sim.ClearEvents();
// interpolate views with clock.Interpolation
```

This is what `SimulationRunner` does internally. To decorate templates in your own host, build a new `TemplateRegistry` from `baked.Templates.Templates` (changed as you like) and use `baked.WithTemplates(registry)` so the view lookups stay valid. `SimulationClock.Advance` may run several ticks per call; if you need events per tick, call `sim.Step()` yourself and drain events after each step.
