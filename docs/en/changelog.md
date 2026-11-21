# Changelog

## 1.1.0 (2026-11-21)

1.1.0 is an update to the editor experience. It does not change simulation rules or the runtime API, so projects made with 1.0.0 keep working.

### Project Overview hub

- **Tools > 2D Tower Defense Maker > Project Overview** is the new hub, with a page strip for **Overview**, **Content**, **Project Check** and **Samples**. The Overview page shows one card per content kind (levels, wave sets, towers, enemies, soldiers, heroes, spells, projectiles, status effects, campaigns and upgrade shops) with the number in your project, and shortcuts to every editor, the manual and the API reference.
- The new **Content** page lists every maker asset with a kind filter and counts, a search by name or folder, an **Issues only** filter, and details with the asset's project-check problems, what uses it and what it uses; **Open**, **Select in Project** and (for levels) **▶ Play Level** act on the selected asset.
- **Tools > 2D Tower Defense Maker > Validate Project** opens the hub on **Project Check** and starts a scan; **Samples > Browse Samples** opens it on **Samples**. **Run check** re-runs the scan from the page, with **Errors** / **Warnings** / **Notes** toggles and their counts, a search over messages and categories, a severity tag on every row and keyboard navigation (↑/↓/Enter; a quick double click opens the owning editor).
- The **Samples** page lists one block per sample scene with **Open** and **Not installed** states, refreshed on focus. Sample regeneration stays in the customer **Samples** menu and the page runs it for you.
- It opens by itself the first time a project loads 2D Tower Defense Maker, and at each editor start while **Show on startup** is on (stored per project). It never opens in batch mode. Click a content card (or **Browse all content**) to open the **Content** page on that kind.
- The 1.0 **Welcome** window became this hub. The startup preference carries over, and code that calls `WelcomeWindow.Open()` still opens the hub (the type is marked obsolete).

### Editor look and docking

- The hub, the five maker editors (Map Editor, Unit Workshop, Wave Timeline, Upgrade Tree, Upgrade Shop) and the Validator share a new UI Toolkit layout with themed headings, buttons, cards and lists. The New Level wizard, the new-asset dialog, the custom inspectors and the Unit Workshop's tab pages use the same frame in 1.1.0, with the same fields and the same behaviour.
- Editor text uses the Geist typeface, loaded for editor windows only (SIL Open Font License 1.1, see `ThirdPartyNotices.txt`).
- The hub and the maker editors share one window: the first maker window you open floats, and every later maker window opens as a tab in it - normally beside the Project Overview, which opens on the first load. The New Level wizard remains a standalone dialog, and the full Validator list can still open as its own window next to the Map Editor (**Open list**).

### Menus

- The customer menu is grouped into Start, Editors, Check and play, Samples and Help bands separated by lines, in that order.
- Maker-development tools (**Capture Sample Screenshot**, **Reimport Sample Art**) moved to **Tools > 2D Tower Defense Maker (Dev)**. They are used when producing the sample content and the store screenshots, not when building a game.
- The **Welcome** entry is gone; use **Project Overview**. All other editor menu paths are unchanged.

### Play Level

- **▶ Play Level** starts a level from the Map Editor, the Wave Timeline, the Level inspector, the New Level wizard or the Project window's right-click menu: it saves the level, opens the scene that plays it (or builds a temporary scene from the level asset when no scene does), enters Play mode, and reopens the scenes that were open before when Play mode stops.

### Data formats

- Every maker asset now records the data format it was saved with. Assets saved by an older release still open (the migration runs in memory) and appear in the Validator's new **Data format** rule as warnings; assets saved by a newer package are errors and are never modified.
- **Tools > 2D Tower Defense Maker > Upgrade Asset Formats** re-saves outdated assets in the current format. It asks for confirmation and is not undoable, so commit or back up first; the Project Overview's **Project Check** summary shows the same notice with an **Upgrade…** button, and `TDMaker.Editor.AssetFormatUpgrade.RunBatch` does it headlessly for `-executeMethod`.
- `IVersionedAsset` and `AssetSchema.RegisterStep` let your own `ScriptableObject` assets - and subclasses of the maker's asset bases, through `ISubclassVersionedAsset` - carry their own version and migration steps. Steps must be idempotent and must not call Unity API; see [Extending the Framework](extending.md#versioning-your-own-assets).

### Documentation

- The manual covers the new hub pages, the Content browser, Play Level and data formats, and its editor screenshots were recaptured for the UI Toolkit windows. The API reference was regenerated from this release and still lists `WelcomeWindow` as obsolete.

## 1.0.0

The first version of **2D Tower Defense Maker** includes:

- A fixed-tick, engine-independent C# simulation with command recording, replay and state hashes.
- Multi-lane paths, waves, branching towers, purchased abilities, blocking barracks, controllable heroes and player spells.
- Damage, armor and resistance rules; status effects; chains, pulses, shields, traps, mine fields, beams, companions and on-site revival.
- The New Level wizard, Map Editor, Unit Workshop, Wave Timeline, Upgrade Tree, Project Validator and headless Dry Run.
- Campaign progression, best-star ratings, three save slots, a world map and permanent star-upgrade tracks.
- Pooled Unity views, a TextMesh Pro/uGUI HUD, VFX and audio hooks, music transitions and camera framing.
- Twin Roads, Crossroads and Winding Pass, plus a complete title-to-campaign sample flow and compiled extension examples.

### Sample presentation and onboarding

- Inter 4.1 Regular, Medium, SemiBold and Bold faces with static SDF atlases, explicit sample-theme assignments and bundled OFL notices. The optional dynamic Noto Sans KR fallback remains included.
- Separate padded title and price regions on buttons and upgrade cards, larger sample small/body text and no sample text shadow.
- English and Korean interface/content tables and live relabeling APIs. The sample title starts in English without language-selection buttons.
- A consistent **Start Wave** label, more generous starting resources and gentler pacing across the three sample levels.
- New Unit Workshop assets are selected and scrolled into view after clearing list filters. Map Editor results stay visible above its scrolling content.
- Fresh levels include an optional starter reinforcement spell; sample audio remains an explicit opt-in.
- Maker runtime/tools are independent of optional sample content. Fresh starter assets are created in the user's own game folder.
- Low hero cards show portraits, names, levels, health and experience bars, with a selected-card border. Skill-purchase controls remain an explicit option for projects using manual progression.
- Updated English guides and actual authoring screenshots cover Welcome, New Level, Unit Workshop and the Map Editor. AI-assisted development and sample audio generation are disclosed in the notices.

See [Quick Start](quick-start.md) for the first level, [Presentation](presentation.md) for typography and localization, and [Support and licenses](support-license.md) for notices.
