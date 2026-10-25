# Campaign, Progress and Saves

A campaign strings your levels together on a world map: levels open one after another (or by your own rules), each level keeps
its best star rating, and the player's progress lives in save slots. Everything here is in `TDMaker.Unity.Campaign`
(`Runtime/Unity/Campaign`). The Demo sample (`Samples/Demo/DemoSample.unity`) uses all of it.

| Piece | What it is |
|---|---|
| `CampaignAsset` | **Create > 2D Tower Defense Maker > Campaign**. Ordered levels, their points on a world map picture, unlock rules. |
| `CampaignProgress` | The rules over one save slot: level states, best stars, star total, pending victories. |
| `ProfileData` | What a save slot stores (JSON). |
| `ISaveStore` | Where slots live: `JsonFileSaveStore` (default), `PlayerPrefsSaveStore` (PlayerPrefs-backed storage), `MemorySaveStore` (in-memory storage). |
| `CampaignSaveSlots` | Slot picker logic: summaries, open (or create), save, delete. |
| `CampaignMapScreen`, `SaveSlotScreen` | Ready-made uGUI screens (TextMesh Pro, styled by your `HudTheme`). |
| `UpgradeShopAsset`, `UpgradeShopSession`, `UpgradeShopScreen` | The permanent star-upgrade shop: tracks of ranks, the purchase rules over a slot, the ready-made screen. |

## The Campaign asset

Each entry in **Levels** has:

| Field | Meaning |
|---|---|
| Key | Stable id used by save files and text tables. **Do not rename it after release** – progress is stored by key. |
| Level | The `LevelAsset` to play. |
| Title, Summary | English texts of the map and the info panel. Translate them with the keys `campaign.level.<key>.title` / `.summary`. |
| Map Position | Point on the map picture, 0..1 from the bottom-left corner. |
| Unlock | **Previous Level** (the nearest earlier main-path level must be won; the first one is open from the start), **Required Levels** (every listed key must be won) or **Always**. |
| Min Total Stars | Optional star gate on top of the rule (earned stars, not stars left after shopping). |
| Branch | A side level. It never blocks the main path: Previous Level skips branches when looking for the previous level. A branch with Previous Level opens after the main level listed before it. |
| Counts Toward Stars | Whether its stars add to the campaign total (star gates and the upgrade shop budget). |
| Path Points | Optional bend points of the road drawn from its prerequisite. |

Also: **Map Image** (any size; the points use 0..1 coordinates), **Max Stars Per Level** (normally 3) and the **Map drawing**
group (road colours for open/locked levels, width, dash length, point size).

### Editing in the inspector

The Campaign inspector shows the map picture with every level point and the unlock roads (arrows from the prerequisite; dotted
for branches; red when something is wrong; green points open at the start).

- Click a point to select it; drag it to move it; click an empty spot to move the selected point there.
- Drop Level assets from the Project window onto the map to add them at that spot (key and title come from the asset name).
- Right-click a point: add a bend point to its road, clear its bend points, remove the level. Right-click empty map: add a bend point to the selected level's road, or add an empty level.
- The list below sets the order; the selected level's fields follow it. Every edit is undoable.

The inspector, and **Tools > 2D Tower Defense Maker > Validate Project**, report: empty or duplicate keys, entries without a Level asset, the
same Level asset twice, unknown required keys, unlock cycles, levels that can never open (also when a star gate asks for more
stars than the levels before it can give), no level open at the start, and points outside the map.

The **New Level** wizard's result page has **Add to Campaign**: pick a campaign and the new level is appended (Previous Level rule)
and the campaign is selected so you can place its point.

## Progress rules

A level is **Locked** until its save record exists, **Open** once it exists, and **Completed** after its first win. Records are
created when the unlock rule holds (`CampaignProgress.Refresh`, also on every map visit, so a level added in an update opens for
old saves too). An opened level never locks again – not when the rules change, nor when stars are spent.

Victories go through two steps, so nothing is counted twice:

1. When a battle is won, call `progress.RecordVictory(levelKey, stars)` and save. The win is stored as a **pending clear**.
   Several wins before the map is shown keep the best rating; a defeat or an immediate restart does not discard it.
2. When the map opens, call `progress.ApplyPending()` and save. It merges every pending clear once: best stars keep the maximum
   (a worse re-win changes nothing, a better one adds only the difference), the first win completes the level and raises
   `FirstCleared(key, stars)`, and the next levels open. It returns a `CampaignMapUpdate` (changes, stars gained, newly opened
   keys) for the map to highlight. Calling it again does nothing.

`EarnedStars` is the sum of best stars of the levels that count; `AvailableStars = EarnedStars − SpentStars`.
`ProjectedStars` (used by slot pickers) also counts pending wins, without counting a level twice.

```csharp
var slots = new CampaignSaveSlots(campaign, SaveStoreFactory.CreateDefault(3));
var progress = slots.Open(0);                       // loads slot 1, or starts a new profile
// ... the player wins level i with `stars`:
progress.RecordVictory(campaign.levels[i].key, stars);
slots.SaveActive();
// ... back on the map:
var update = progress.ApplyPending();
if (update.HasChanges) slots.SaveActive();
mapScreen.Show(progress, update);
```

## Save slots

`ProfileData` holds the opened levels with best stars and win counts, pending clears, **purchased permanent upgrade ranks per
track key** (`GetUpgradeRank` / `SetUpgradeRank`), **stars spent**, the earned total at the last save, and free `custom`
key/value entries for your own data (tutorial flags, selected hero, ...). App settings – volumes and language – are not in a slot;
`TDGameSettings` keeps them in PlayerPrefs (`persistVolumes`, `persistLanguage`).

Stores never throw; they return results and log warnings.

- **`JsonFileSaveStore`** (default): `persistentDataPath/TDMakerSaves/slot1.json`, `slot2.json`, ... Writes go to `slotN.json.tmp`
  and then replace the slot file, so a crash mid-write keeps the previous save (a leftover complete `.tmp` is recovered on load).
- **`PlayerPrefsSaveStore`**: one PlayerPrefs string per slot. `SaveStoreFactory.CreateDefault` chooses the platform default; you can also supply a store explicitly.
- **Unreadable data is never deleted silently.** A file that is not valid JSON, not a profile, or written by a newer version is
  renamed to `slotN.json.bak` (`.bak2`, ... if one exists; `key.bak` in PlayerPrefs), a warning is logged, and the slot starts
  empty. `SaveSlotScreen` shows a note on such a slot.
- **Versions.** Every file carries `version`. Reading an older one runs the built-in steps and then your own
  `ProfileSerializer.Migrate += (data, fromVersion) => ...` hooks, once per version step; the slot is written back in the
  current version. Fields a file lacks keep their defaults (JsonUtility), so new fields need no migration step – only changed
  meanings do.
- Deleting a slot (`CampaignSaveSlots.Delete`) removes only that slot. `SaveSlotScreen` asks first (Delete / Cancel).

## The screens

Both screens are built from code under any canvas: `CampaignMapScreen.Create(parent, theme)` and `SaveSlotScreen.Create(parent, theme)`
(`CampaignUi.Canvas` makes a canvas scaled like the HUD).

- **`CampaignMapScreen.Show(progress, update)`**: the map picture (fitted, letterboxed), dashed roads, level points (lock when
  locked, number when open, best stars under completed ones, pulsing "New!" on levels the update opened), the star total, a
  toast for first clears / stars gained / new levels, and the level info panel (title, summary, best stars, what still opens a
  locked level, **Play**). Events: `PlayRequested(levelIndex)`, `BackRequested`. Keys: 1-9 select a level, Enter plays, Esc
  closes the panel and then goes back.
- **`SaveSlotScreen.Show(slots)`**: one row per slot (stars, levels won, last played), **Continue** / **New Campaign** and
  **Delete** with confirmation. Events: `SlotChosen(slot)`, `SlotDeleted(slot)`, `BackRequested`.

Their texts are `HudTexts` keys (`campaign.map.*`, `campaign.level.*`, `campaign.slots.*`, `campaign.nav.worldMap`), translated
through your `TextTable`s like the HUD; they relabel themselves when the language changes. For the in-battle buttons, the Demo
calls `hud.SetNavigation(false, true, null, HudTexts.NavWorldMap)` so the pause menu and the result screen offer **World Map**.

## The Demo sample

`Samples/Demo/Scripts/DemoFlow.cs` is a complete flow in one scene: title → save slots → world map (`Samples/Demo/Data/SampleCampaign.asset`,
painted map picture `Samples/Demo/Art/world_map.png`; the asset is generated by **Create Sample Content**) → battle (each level on its painted map, **Level Grounds**) → result → world map.
It records each victory as a pending clear, saves immediately, and merges the result when the map opens. `UseStore(...)` lets you supply a storage implementation, and `PreviewMap()` shows a temporary in-memory profile.

The generated sample shop (`Samples/Demo/Data/SampleUpgradeShop.asset`) adds the **Upgrades** button to the map.

## The star-upgrade shop

Earned stars buy permanent upgrades between battles. An **Upgrade Shop** asset (**Create > 2D Tower Defense Maker > Upgrade Shop**, edited in
**Tools > 2D Tower Defense Maker > Upgrade Shop**) holds ordered **tracks** (shop columns); each track is a chain of **ranks** bought in order,
each rank has a star price and a list of **effects**. Assign the shop to the campaign's **Upgrade Shop** field: the world map
then shows an **Upgrades** button with the unspent stars as a badge, and every battle started while a slot of that campaign is
open applies the slot's purchased ranks.

| Track field | Meaning |
|---|---|
| Key | Stable id in save files (purchases are stored per key) and text key stem `shop.track.<key>.name` / `.summary`. **Do not rename it after release.** |
| Display Name, Description | English name and one-line summary (translated through the keys above). |
| Icon, Color | Column icon (optional) and accent colour. |
| Ranks | Price (stars), an optional English line (`shop.track.<key>.rank<N>`) and the effects. Higher ranks add their effects on top of the lower ranks. |

### Effects

Each effect maps one to one to the core `UpgradeEffectDef` (see `Runtime/Core/Upgrades.md`):

- **Target**: towers, soldiers, heroes or enemies (their template ids), spells (their spell ids), further ids, required tag bits and
  a role mask (tower, soldier, hero, spell, projectile, enemy). Filters combine with AND; the lists and the role mask are
  alternatives. Every matching value inside a selected template changes (all its attacks, ability ranks, damage payloads ...).
- **Stat**: a field (range, damage minimum / maximum, attack interval, ability cooldown, build cost, ability prices, health,
  armor, magic / poison resistance, regeneration, rally range, respawn time, spell cooldown, units called and their duration,
  effect duration, blast radius, speed, strike count and spread) and an operation: **Multiply Ceil** (multiply, then round up at
  once - use it for damage and health), **Multiply** (keeps fractions - ranges, intervals), **Add**, **Subtract**, **Set**.
  Effects apply one after another in track, rank and list order; there is no "sum everything, multiply once".
- **Add Mechanic**: adds an always-active timed action (the same action the units' and towers' behavior lists use: an extra
  attack, a self buff, a summon, an area, chain, trap, beam ...) to the selected units or towers. Give it a name for the
  tooltip (`Mechanic Name`, translated through `shop.mechanic.<Mechanic Key>`).
- **Swap Template**: replaces a unit reference (the soldier a barracks or a reinforcement spell calls, a summon) inside the
  selected templates or spells. The replacement is registered for the battle automatically.

### Rules (fixed)

- Only the next rank of a track can be bought, and only with enough stars: `Available = EarnedTotal - Spent`, where `Spent`
  is the sum of the prices of every bought rank. Spending never lowers the earned total (star gates use earned stars).
- One click on a buyable rank buys it at once - no confirmation - and the slot is saved immediately.
- **Undo Changes** returns every track to the purchases the shop **opened** with (not just the last click) and saves.
- **Reset All** clears every purchase without a confirmation, saves, and makes the empty state the new Undo baseline.
- **Done** (or Esc) closes the shop; purchases are already saved. Reopening makes the current purchases the new baseline.
- The map badge shows `min(EarnedTotal, FullShopPrice) - Spent` (never below zero): stars beyond the price of the whole shop
  are not announced. This is a display limit, not a cap on earning.

All of it comes from the core `UpgradeShopRules`; `UpgradeShopSession` applies them to a slot (`Purchase`, `Revert`, `ResetAll`,
`Available`, `GetState`) and `UpgradeShopScreen` is the ready-made screen (columns of rank nodes, tooltip with price, state
and an effect summary generated from the data - "Range +8%", "Cooldown -2s", "New: Sharpshot"). Its texts are `HudTexts`
keys (`campaign.shop.*`, field labels `campaign.shop.field.<Field>`).

### Battles

When a run starts, `SimulationRunner` builds a core `UpgradeSnapshot` from the shop and the purchased ranks and passes the level
with it (`LevelDef.WithUpgrades`); the core rewrites copies of the templates and spells before anything spawns, and includes the
snapshot in the state hash and the command log. Where the shop and ranks come from:

| Source | When |
|---|---|
| Runner **Upgrade Shop** field | Used when set. Empty: the open slot's campaign shop (`CampaignSession.Shop`). |
| `runner.UpgradeRanks` (`Func<string,int>`) | Your own rank source, such as another save system. |
| The open campaign slot | `CampaignSaveSlots.Open` sets `CampaignSession`; used unless **Use Campaign Upgrades** is off. |
| **Forced Upgrade Rank** | Every track at this rank for the run (challenge modes); purchases are unchanged. |

No shop, or nothing bought, means no snapshot: the run is exactly the run without upgrades (same hash, same log format).
`runner.Upgrades` is the snapshot of the current run, `runner.UpgradeRecord` the shop name and ranks it used.

**Replays.** A command log stores only a fingerprint of the upgrades. When the runner saves a recording it writes the ranks next
to it (`<file>.upgrades.json`), and a replay of that file reads them back (or set `runner.ReplayUpgrades`). Different ranks or a
changed shop give a different fingerprint, and the replay is refused.

### The editor

**Tools > 2D Tower Defense Maker > Upgrade Shop** shows the tracks as columns and the ranks as cells (price and effect summary):

- add, remove and move tracks; add, duplicate, remove and move ranks; every edit is undoable;
- **Price curve**: fill a track's prices from its first and last price with a back-loaded curve (prices never decrease);
- the selected rank's effects with a readable summary each (+ Stat, + Mechanic, + Swap);
- **Preview**: pick a level, a tower, unit or spell and a rank (of the selected track, or of all tracks) and compare its stats
  before and after - computed by the core rewriter, so it is what the battle uses;
- validation: no tracks, empty or duplicate keys, tracks without ranks, negative prices, effects without a filter, mechanics
  without a payload or on spells, swaps without units, Multiply Ceil on fractional fields, and effects that select nothing in
  the levels of the campaigns using the shop. **Tools > 2D Tower Defense Maker > Validate Project** runs the same checks.

The sample shop (six tracks of five ranks: archer, cannon, arcane and garrison families, Call to Arms and Starfall) is generated
by **Create Sample Content** (`SampleContentGenerator.GenerateUpgradeShopSample` writes only the shop and the text tables).
The three sample levels award at most **9 stars**. Each track costs **0, 0, 1, 2, 3 stars** (6 per track, **36** for the whole
shop). The first two ranks are free purchases, still taken in order. With all 9 stars you can buy up to **19 of 30 ranks**
(about 63%): buy the free ranks on all six tracks, rank 3 on five tracks and rank 4 on two of those tracks. Alternatively,
finish one track for 6 stars and spend the remaining 3 on other tracks. Reset All lets you try a different build.
