# Presentation: HUD, Feedback, Camera and Audio

Everything on this page lives in the Unity layer (`TDMaker.Unity.View`, `TDMaker.Unity.Hud`). It only **reads** simulation state and events and **sends commands**; you can replace any piece without touching the core. The Basic sample scene wires all of them on the `2D Tower Defense Maker` object (see `SampleContentGenerator`).

| Component (Add Component > 2D Tower Defense Maker > …) | Class | Role |
|---|---|---|
| Simulation Runner | `SimulationRunner` | Owns and advances the simulation; event source for everything below |
| Entity View Registry | `EntityViewRegistry` | Pooled unit, tower and projectile views; built-in hit, death, spell and mechanic feedback |
| Level View | `LevelView` | Generated placeholder ground with decorations, path ribbons and slot pads |
| Game HUD | `GameHud` | Production uGUI HUD for mouse and keyboard, styled by a `HudTheme` |
| Damage Numbers | `DamageNumbers` | Pooled floating damage and heal numbers |
| VFX Pool | `VfxPool` | Pools VFX prefabs from presentation hooks |
| Audio Cue Player | `AudioCuePlayer` | Pools AudioSources; plays global, mechanic and per-template cues |
| Music Player | `MusicPlayer` | Menu / battle / intense loops with crossfade, victory and defeat stingers |
| Camera Controller | `TDCameraController` | Frames the level (whole map by default; optional scrolling framings with pan and zoom) |
| Game Settings | `TDGameSettings` | Player-facing toggles read by the camera, HUD and feedback |
| Ellipse Renderer | `EllipseRenderer` | Draws a range ellipse (fill + outline) with the simulation's shape |
| TD Hud | `TDHud` | Minimal IMGUI HUD, used by the sample as an **F1** debug overlay |

## SimulationRunner (scripting)

| Member | Meaning |
|---|---|
| `Simulation`, `Baked` | The running world and its baked level (authoring lookups: `TryGetAsset`, `GetTower`, `GetHero`, `GetSpell`, `TryGetProjectile`, `TryGetEffect`, `TryGetMechanicVisual`). |
| `StartSimulation()` / `Restart()` | Bake and create a fresh world. |
| `Enqueue(command)` | Queue a player command (ignored while replaying). After victory/defeat the command is rejected with `GameEnded` on the next frame. |
| `Advance(realDeltaTime)` | Advance the clock and dispatch events. Called from `Update`; tools may call it directly (edit-mode captures, replays). Uses the core `SimulationClock`: at most `Catch Up Ticks Per Speed × speed` ticks per call. |
| `TimeScale`, `SetPaused(bool)`, `IsPaused`, `SetSpeed(scale)`, `ResumeScale` | Game speed; pause remembers the last non-zero speed. |
| `InterpolationAlpha` | Fraction of a tick for render interpolation. |
| `RangeYScale`, `DefaultRangeYScale` | Effective `k` of the running level, and the runner's own setting. |
| `StartingGoldOverride` | Debug: replaces the level's starting gold (≥ 0) on the next start. |
| `CreateConfig()` | The `SimConfig` built from the Inspector (tick rate, `k`, capacities). |
| `AddTemplateDecorator` / `RemoveTemplateDecorator` | Change baked templates before each start ([Extending the Framework](extending.md#registering-extensions-in-a-unity-scene)). |
| `RecordCommands`, `RecordingFile`, `ReplayOnStart`, `ReplayFile`, `CommandLog`, `IsReplaying`, `CommandCodec`, `SaveRecording()` | Built-in recording and replay ([Determinism and Replay](determinism-and-replay.md)). |
| `SimulationStarted`, `EventRaised` | Events: new world created (register extensions); every simulation event, once per frame in emission order (the frame's events must fit `Event Capacity`; a warning is logged once per run if any are dropped). |

## GameHud

**Add Component > 2D Tower Defense Maker > Game HUD** (`TDMaker.Unity.Hud.GameHud`). Built in uGUI from code at runtime – no prefabs to maintain – and styled by a `HudTheme` asset.

Contents: top bar (gold, lives, wave, pause, 1×/2×/3×), wave-call indicators at path entrances (countdown ring, early-call bonus), radial build menu, tower panel (upgrade/branch choices, ability ranks, target priority, rally, sell), hero portraits with health/experience and skill buttons, spell bar with cooldowns and hotkeys, unit info, pause and victory/defeat screens with star rating, tooltips, toasts for rejected commands, and world feedback (range ellipses, slot highlight, placement ghost, rally/move markers, spell aim valid/invalid).

### Controls (PC mouse and keyboard)

One thing is selected or aimed at a time. A battlefield left click acts where the button is **released** (press and release must both be on the battlefield, not on HUD panels or buttons).

| Situation | Input | Result |
|---|---|---|
| Nothing selected, or a menu/info is open | Left click an empty build slot / a tower | Opens its build menu / tower panel (clicking the same one again keeps it open) |
| | Left click a soldier or an enemy | Shows its info panel (not an attack order) |
| | Left click a hero, its portrait, or **H** | Selects the hero for moving |
| | Left click empty ground or road | Clears the selection |
| Build menu / tower panel | One click on a build, upgrade or branch item | Buys it and closes the menu (hovering previews range, ghost and price; there is no second confirmation click) |
| | One click on an ability | Buys one rank; the panel stays open |
| | One click on **Sell** | Sells immediately (no confirmation by default) |
| | Click on **Set Rally** | Hides the panel and starts rally aiming |
| Hero selected | Left click anywhere on the battlefield (ground, road, slot, tower, unit, the hero itself) | Moves the hero to that point; a valid point ends the selection, an invalid one shows a marker and keeps the hero selected |
| | The same portrait again or **H** (after the last hero) | Deselects |
| | Another hero's portrait | Selects that hero |
| Rally aiming | Left click anywhere on the battlefield | Sets the rally point when it is inside the ring and on an allowed lane spot (then back to browsing); otherwise a marker and aiming continues |
| Spell aiming (spell button or **1–9**) | Left click anywhere on the battlefield, including empty ground | Casts at that point when it is valid for the spell (then back to browsing and the cooldown starts); otherwise a marker and aiming continues, no cooldown is used |
| | The same spell button or key again | Cancels aiming |
| | A locked or recharging spell button or key | Nothing is selected |
| Any selection or aim | **Right click** (anywhere) or **Esc** | Cancels everything and returns to browsing; never moves a hero; a cancelled rally keeps the old rally point |
| Nothing selected | **Right click** | Nothing (it never pauses) |
| | **Esc** | Opens the pause menu |
| Pause menu | **Esc** or **Resume** | Closes it; the battle continues with nothing selected |
| Result screen | **Esc** | Leaves the battle like the Quit button (when a Quit listener exists) |
| Wave call | One click on an entrance's call button, or **N** | Calls the whole next wave at once (every entrance); hovering shows what comes through that entrance |

Keys: **Esc** cancel / pause, **Space** or **P** pause, **1–9** spells, **H** hero, **N** next wave, **F1** debug overlay. Product additions that a buyer can turn off: the **1× / 2× / 3×** speed buttons (`TDGameSettings.speedControls`), the early-call gold preview on wave buttons and tooltips (`showEarlyCallBonus`, off by default), the tower panel's target-priority buttons and close button, and an optional sell confirmation (`confirmSell`, off). Camera pan and zoom exist only in levels whose Camera Framing scrolls; with left-drag pan on (`leftDragPan`, off by default) a press that turns into a drag pans the camera and is not also a click.

Click targets are world rectangles around each unit (the border itself is outside): heroes are roughly square, soldiers and enemies taller than wide, towers slightly wider than tall and empty build slots clearly wider than tall. Where rectangles overlap, a hero wins; otherwise the target whose position is lower on the map wins. Per content, `View > Click Area` on an entity asset replaces the rectangle (`Custom Area`, `Size`, `Offset`) and raises or lowers its priority (`Priority Bonus`).

The same entry points are public for tutorials, tests and other input devices: `BattlefieldClick(worldPoint)`, `SecondaryClick()`, `PressEscape()`, `PressSpellKey(index)`, `PressHeroKey()`, `ClickHeroPortrait(heroId)`, `CancelAll()`.

| Field | Meaning |
|---|---|
| `Runner`, `Registry`, `World Camera` | Dependencies (empty camera = `Camera.main`). |
| `Theme` | `HudTheme` asset (empty = built-in defaults). |
| `Debug Hud` | Optional `TDHud` toggled with **F1**. |
| `Audio Player` | Optional; plays the interface cues (click, build menu open/close, rally set, wave called). |
| `Pause Volume Sliders` | Master / Music / Effects / Interface sliders in the pause menu (on). |
| `Hero / Unit / Tower / Slot Click Size`, `… Click Offset` | Default click rectangles in world units (size, centre offset from the position). |
| `On Continue`, `On Quit` | UnityEvents for the result screen buttons and the pause menu's Quit (hidden when nothing is assigned in the Inspector; see `SetNavigation` for listeners added from code). |

Text: `Texts` (the scene's `TDGameSettings.Texts`), static `Describe(texts, failure)` (the text of a rejected command).

Scripting: `Configure(runner, registry, camera, theme, debugHud)`, `Connect()`, `Refresh()`, `SelectTower(entityId)`, `SelectBuildSlot(index)`, `ClearSelection()`, `CancelAll()`, `CurrentMode` (`Browsing`, `BuildMenu`, `TowerMenu`, `RallyAiming`, `HeroSelected`, `UnitSelected`), `AimingSpell`, `SelectedHero`, `SelectedTower`, `SelectedUnit`, `HasSelection`, the input entry points above, `Theme`, `Canvas`, `Runner`, `SetPauseMenu(open)`, `IsPauseMenuOpen`, static `EnsureEventSystem()`.

**Game flow from code.** A menu script that adds `onContinue`/`onQuit` listeners at runtime calls `SetNavigation(showContinue, showQuit, continueText, quitText)` to choose which buttons show and their labels – text keys or literal texts (for example "Next Battle" only when a next level exists, and "Main Menu"); with both shown the result screen places them side by side. `ClearNavigation()` returns to the Inspector rule. The pause button in the top bar opens the same pause menu as **Space**/**P**/**Esc**. The campaign screens (world map, save slots) are described in [Campaign](campaign.md). See the Demo sample (`Samples/Demo/Scripts/DemoFlow.cs`): one scene, one runner, levels swapped with `SimulationRunner.Configure(null, levelAsset)` + `StartSimulation()` (set `StartOnPlay` off so nothing starts behind the title screen).

Every value the HUD shows is read back from the simulation; failed or cancelled aims never send commands. Rules are never recomputed in the view: the sell price uses `Simulation.PreviewSellRefund`, the call-wave bonus and tooltip use `PreviewEarlyCallReward`, spell tooltips show `PreviewEarlyCallSpellCooldownCut`, the countdown ring is `NextWaveRemaining / NextWaveWaitDuration`, the rally cursor is drawn at the point `TryResolveRallyPoint` resolves (invalid points are refused before a command is sent), the early-call toast shows the `GoldChanged` delta that precedes `WaveStarted`, and the result screen shows the core's `Victory` star rating. Splash rings use `ProjectileHit.Value` for instant hits. Text is TextMesh Pro with the theme's font, and every string comes from the string tables ([Text, fonts and languages](#text-fonts-and-languages)).

## HudTheme

**Create > 2D Tower Defense Maker > HUD Theme** (`HudTheme`). All fields are optional; empty sprites use generated defaults (`HudSprites`).

| Group | Fields |
|---|---|
| Canvas | `Reference Resolution`, `Match Width Or Height`, `Sorting Order` |
| Text | `Font` (`TMP_FontAsset`; empty = the TMP Settings default), `Font Material` (optional preset), `Fallback Fonts` (for characters the font lacks, for example CJK), `Body Font Weight`, `Button Font Weight`, `Small Font Size`, `Font Size`, `Large Font Size`, `Title Font Size`, `Text Shadow` (underlay) |
| Sprites | `Panel`, `Button`, `Circle`, `Ring`, `Bar` (9-sliced where useful), icons for gold, lives, wave, incoming, star, pause, play, lock, damage |
| Colours | panel/button states, text, accent, gold, lives, wave, positive/negative, health, experience, cooldown shade, stars, overlay |
| Layout | `Top Bar Height`, `Padding` (spacing), `Panel Padding` (sample: 36), `Screen Padding` (24), `Button Text Padding` (18 horizontal / 10 vertical), radial menu radius and button size, spell button, portrait, wave indicator, tower panel width, button height |
| World feedback | range/preview/rally/hero/valid/invalid/slot-hover/unit-select colours, `Range Fill Alpha`, `Outline Width`, `Ghost Alpha` |
| Damage numbers | `Damage Number Color`, `Heal Number Color`, `Damage Number Size` |

`HudTheme.Default` is the in-memory default; `ResolveFont()` returns the configured font or the TMP Settings default (null when the TMP Essential Resources are missing), or a runtime copy of it when `Fallback Fonts` are set (see below).

## DamageNumbers

**Add Component > 2D Tower Defense Maker > Damage Numbers.** Pooled floating TextMesh Pro numbers (outlined) on a screen-space canvas, merged per target for a short window; digits are cached strings and the fade uses the canvas renderer alpha, so they do not allocate per frame. Fields: `Runner`, `World Camera`, `Theme`, `Merge Window`, `Lifetime`, `Rise`, `Minimum Value`, `Max Numbers`, `Show Heals`. Disabled when `TDGameSettings.damageNumbers` is off. `Configure(runner, camera, theme)`.

## Text, fonts and languages

All runtime text – `GameHud`, `DamageNumbers` and the sample menus – is **TextMesh Pro** (`TextMeshProUGUI`, built from code by `HudUi.Label`). TextMesh Pro is part of the uGUI package in Unity 6 (`com.unity.ugui` 2.0), so there is no extra dependency; the 2D Tower Defense Maker assemblies reference `Unity.TextMeshPro`.

### TMP Essential Resources

TextMesh Pro needs its **Essential Resources** (TMP Settings, the default LiberationSans SDF font asset and the SDF shaders) in the project once. 2D Tower Defense Maker does not ship them. When they are missing:

- the editor logs one message per session and offers **Import** in a dialog;
- **Tools > 2D Tower Defense Maker > Import TMP Essential Resources** (or Unity's **Window > TextMeshPro > Import TMP Essential Resources**) imports them into `Assets/TextMesh Pro`;
- **Validate** reports an error in the *Text* category;
- the HUD still builds and plays, but text stays invisible until the resources exist.

Batch: `-batchmode -executeMethod TDMaker.Editor.TextMeshProSetup.ImportEssentials` **without** `-quit` (the editor exits when the import finishes). Scripts can ask `TextMeshProSetup.EssentialsImported`.

### Fonts

**Included sample typography.** Both sample HUD themes explicitly use **Inter 4.1** from `Samples/Fonts/Inter/`. Regular (400), Medium (500), SemiBold (600) and Bold (700) have separate static SDF atlases and real weight-face links: body text uses Regular, button titles SemiBold, button prices Medium and headings Bold. Small/body sizes are 20/24 and the sample text shadow is disabled. Button titles and prices use separate padded regions; long text fits or truncates inside its region. The original four TTF files and their SIL Open Font License 1.1 are included alongside the generated assets (`ThirdPartyNotices.txt`).

The static atlases use 80 pt sampling, 8 px padding and a 2048-square texture per face. They include the shipped English table and common Latin UI characters. If you add characters outside that set, regenerate the atlas or add a licensed fallback. Re-running Create Sample Content preserves existing Inter assets and their GUIDs.

`HudTheme > Font` takes a `TMP_FontAsset`; empty uses the **default font asset of your TMP Settings**. `Font Material` is an optional material preset (outline, glow ...); empty uses the font's own material, and **Text Shadow** adds a drop shadow through a generated underlay material (`HudUi.TextMaterial`, shared and cached per font, so labels keep batching). Damage numbers add an outline the same way; `HudUi.SetOutline(label, theme, color, width)` does it for your own labels.

To make a font asset: select a `.ttf`/`.otf` and use **Assets > Create > TextMeshPro > Font Asset** (or **Window > TextMeshPro > Font Asset Creator** for a static atlas).

### Chinese, Japanese and Korean (CJK) fonts

The bundled Inter faces and the TMP default LiberationSans font do not cover CJK scripts; without a CJK font those characters render as boxes (and TMP logs which characters are missing). Add one font that covers the language, as a **dynamic** fallback so only the glyphs you use are rasterized.

**Sample Korean font.** The samples include **Noto Sans KR Regular** (`Samples/Fonts/NotoSansKR-Regular.otf`, about 4.4 MB, SIL Open Font License 1.1 – `Samples/Fonts/OFL.txt`, see `ThirdPartyNotices.txt`) and a dynamic font asset made from it by the sample generator, `Samples/Fonts/NotoSansKR-Regular SDF.asset` (48 pt sampling, 1024 atlas pages, multi atlas, dynamic data cleared on build). Both sample HUD themes list it in **`HudTheme > Fallback Fonts`**, so the Korean sample table renders out of the box (switch `TDGameSettings > Language` to `ko`, or use the language button of the Demo). The fallback is applied to a runtime copy of the HUD font, so your TMP Settings and the TMP default font asset are not changed. Keep the font and its license file together if you ship it; if Korean is not required, remove only the Noto Sans KR font and its theme fallback entries; keep the Inter folder and its license.

**Adding a font for another language** (Japanese, Chinese, another Korean typeface):

1. Import a font file you are licensed to ship (for example Noto Sans JP / SC / TC, SIL Open Font License).
2. Select it, **Assets > Create > TextMeshPro > Font Asset > SDF**. In the new asset set **Atlas Population Mode = Dynamic**, an atlas of 1024 (or 2048), *Multi Atlas Textures* on and *Clear Dynamic Data On Build* on.
3. Add it to your theme's **`HudTheme > Fallback Fonts`** (tried in order after the HUD font's own fallbacks). Alternatives: the HUD font asset's own **Fallback Font Assets** list (required when `HudTheme > Font` is itself a dynamic font – `Fallback Fonts` only applies to static fonts and logs a warning otherwise), **Project Settings > TextMesh Pro > Settings > Fallback Font Assets** (every TMP text in the project), or the font directly as `HudTheme > Font` for a single-language build.
4. Play the scene in that language once and check the console for missing-character warnings.

Keep Latin text in the primary font and CJK in the fallback: the HUD's numbers and the English fallback texts keep the primary font's metrics (CJK fonts have taller line metrics, so multi-line panels grow a little). Dynamic atlases fill while the game runs; in the editor the glyphs are written into the font asset (re-run **Create Sample Content** to reset the sample one). For a shipped static atlas, use the Font Asset Creator with your table's characters (*Characters from File*).

### String tables

Every user-visible HUD string is a key (`HudTexts` lists them, for example `hud.pause.title`, `hud.tower.sell` = `Sell  +{0}`). Texts come from **`TDGameSettings.Texts`** (a `TextResolver`):

| Order | Source |
|---|---|
| 1 | `TextResolver.Provider` – an optional `ITextProvider` set from code (an adapter to the Unity Localization package, a spreadsheet import ...) |
| 2 | `TDGameSettings > Text Tables` whose language matches `TDGameSettings > Language` (later tables override earlier ones) |
| 3 | the English tables in the same list (`en`) |
| 4 | the built-in English texts (`HudTexts.English`) |
| 5 | the caller's fallback (`Get(key, fallback)`), then the key itself |

A **Text Table** (**Create > 2D Tower Defense Maker > Text Table**, `TextTable`) has a `Language Code` (`en`, `ko`, `de`, `zh-Hans` ...; matched ignoring case, and `ko` serves `ko-KR`), a `Language Name` for menus and `key → text` entries. Empty texts count as missing, so a partly translated table works. Texts may use rich text (`<b>`, `<color=#ff7766>`) and `{0}`, `{1}` placeholders for numbers and names; preserve the placeholder indices, although translations may reorder them. A broken placeholder shows the text unformatted instead of throwing, and **Validate** reports placeholders the HUD does not fill.

The samples include `Samples/Text/Text_English.asset` and `Samples/Text/Text_Korean.asset`; the sample generator updates both. Sample scenes assign both tables and use `en` as their default language. Sample menu keys start with `demo.*`, campaign screen keys with `campaign.*`, and level titles and summaries use `campaign.level.<key>.title` and `.summary`. Content names and descriptions use the `content.*` keys below; missing translations display the asset's authored text.

**Adding a language**

1. Duplicate `Text_English` (or create a Text Table), set `Language Code` and `Language Name`, translate the texts (leave a text empty to keep English).
2. Add the table to `TDGameSettings > Text Tables` in your scenes (keep the English table in the list for keys you add yourself).
3. Make sure the HUD font or its fallbacks cover the script (see CJK above).
4. Select the language: `TDGameSettings > Language` in the Inspector, or `TDGameSettings.Current.SetLanguage("de")` from an options menu (`GetLanguages(list)` lists the codes of the assigned tables; `LanguageChanged` fires). Open HUDs and the sample menus relabel themselves on the next frame. With `Persist Language` on (default), the choice is saved in PlayerPrefs (`Language Prefs Key`, default `TDMaker.Language`) and loaded when play starts in a build (`LoadLanguage()`). In the Editor, **Ignore Saved Language In Editor** is enabled by default so the Inspector value takes precedence. Like volumes, the language is an app setting kept outside save slots.

**Scripting**: `Texts.Get(key)`, `Texts.Get(key, fallback)`, `Texts.Format(key, a[, b[, c]])`, `Texts.FormatText(text, a)`, `Texts.Has(key)`, `Texts.Version` (changes when the language, the tables or the provider change), `Texts.Invalidate()`; `TextTable.TryGetText`, `Set`, `Remove`, `Clear`, `Entries`; `CachedText` caches the formatted text of a key per number and language. HUD labels are updated only when their value changes, and the strings are cached per value (`NumberText.Get(int)` shares one string per integer; `CachedNumber` and `CachedText` keep the text of every value they have shown), so the HUD adds no per-frame allocation at any game speed – a count, timer or health value that comes back costs nothing; a language switch rebuilds the labels once. Top bar values and hero hints shrink (TMP auto size) instead of running past their panel in longer languages.

### Translating content names and descriptions

The game HUD uses `ContentTexts` to resolve names and descriptions for units, towers, heroes, spells, status effects, purchased abilities and hero skills. Keys follow `content.<category>.<id>.<field>`. Categories are `unit`, `spell`, `effect` and `ability`; fields are `name` and `description`. General units and status effects have no description field, so only their names are translated.

For example, `content.unit.garrison_1.name`, `content.unit.militia.name` and `content.ability.piercing_shot.name` translate Garrison, Militia and Piercing Shot. Both sample tables include content names and descriptions. Add keys following the same pattern for your own content. When a translation is absent, the original authored name or description is used.

Changing the display language preserves `TemplateId` and the authored `DisplayName`; it does not change core definitions, saves or command replay. Open tower panels, hero names and tooltips update when the language changes. Authoring tools such as Unit Workshop continue to show asset filenames and authored text.

## Presentation hooks, VFX and audio

Each entity asset's `View` has **`Hooks`** (`PresentationHooks`): `Spawn / Attack / Hit / Death Vfx` prefabs and `Spawn / Attack / Hit / Death Cue` audio cues. Projectiles have `Launch Vfx`, `Impact Vfx`, `Launch Cue`, `Impact Cue`; spells have `Cast Vfx` and `Cast Cue`. Every slot is optional.

**`AudioCue`**: `Clips` (one picked at random), `Volume`, `Pitch Min/Max`, `Min Interval` (prevents stacking), `Spatial Blend`. `HasClips` tells whether anything would play.

**`VfxPool`** (**2D Tower Defense Maker > VFX Pool**): `Spawn(prefab, position, lifetime = -1)` places a pooled instance; particle systems are restarted on reuse and the instance returns after its particle duration (or `Default Lifetime`). `Max Active` caps live instances. Implement `IPooledVfx.OnSpawned()` on a prefab component to reset custom state. `Clear()` returns everything.

## Audio

Three components play sound: `AudioCuePlayer` (one-shot cues), `MusicPlayer` (loops and stingers) and `TDGameSettings` (volumes and mixer routing). All of them are optional and every cue or clip slot may stay empty (silent).

### Cues (`AudioCuePlayer`)

**2D Tower Defense Maker > Audio Cue Player.** Plays cues through a pool of AudioSources.

| Field | Meaning |
|---|---|
| `Voices` | Pool size = global voice limit. When every voice is busy the oldest one is reused. |
| `Max Voices Per Cue` | Copies of one cue that may sound at once (default 3, 0 = no limit). Together with each cue's `Min Interval` this keeps dense fights from stacking. |
| `Master Volume` | Extra volume of this player (multiplied with the Game Settings volumes). |
| `Cues` | Global events: wave started, wave callable, **wave called** (button/N, played by the HUD instead of the click), tower built / upgraded / sold, ability purchased, life lost, **coin gained** (an enemy with a bounty died; throttle with `Min Interval`), command rejected, spell ready, **spell cast** (fallback for spells without their own `Cast Cue`), **hero moved** (order approved), hero level-up, **rally set**, victory, defeat, UI click, **build menu opened / closed**. |
| `Mechanic Cues` | Built-in mechanic events: chain started, trap placed, trap triggered, beam started, healed (give it a long `Min Interval`), shield applied (an effect with a shield was attached), damage reflected, knockback (displacement), path transferred. |
| `Keyed Cues` | `Key` + `Cue`: replaces the mechanic default for one mechanic id (chain, trap, beam, pulse, reflection or transfer id) or plays on attach of one status effect id. `SetKeyedCue(key, cue)` from code. |
| `Ensure Listener` | On Start, adds an `AudioListener` to the main camera when the scene has none. |

Per-template cues are on the assets (see above) and are routed by the `EntityViewRegistry`. Cues on the UI channel: UI click, build menu, command rejected; everything else is SFX.

Scripting: `Play(cue)`, `Play(cue, position)`, `Play(cue, position, AudioChannel)`, `PlayUi(cue)`, `PlayUi(preferred, fallback)`, `Keyed(key, fallback)`, `StopAll()`, `ActiveVoices`, static `EnsureListener()`.

### Music (`MusicPlayer`)

**2D Tower Defense Maker > Music Player.** Two pooled loop sources crossfade (`Crossfade`, real seconds) and a third plays stingers.

- **Level music**: `Level Asset > Audio > Music` (`LevelMusicData`): `Battle` loop, `Intense` loop, `Victory` / `Defeat` stingers, `Volume`. The intense loop is crossfaded in when a wave starts that matches a rule: `Intense On Last Wave`, `Intense On Boss Waves` (waves with `Boss Wave` ticked in the Wave Set – a presentation hint that is not baked into the core) or `Intense From Wave` (one-based, 0 = off).
- **Defaults** on the Music Player (`Menu Music`, `Battle Music`, `Intense Music`, `Victory Stinger`, `Defeat Stinger`) are used for every slot a level leaves empty.
- **Menu music**: plays while no simulation runs, or while the optional `Battle Root` object is inactive (assign the HUD a menu flow hides, as the Demo sample does). `Follow Battle Root` switches back to the battle loop when it shows again.
- **Stingers**: `Stinger Mode` `Stop Loop` (default: the loop fades out) or `Duck Loop` (lowered to `Duck Volume` while the stinger plays). `Paused Volume` lowers the loop while the game is paused.

Scripting: `PlayMenu()`, `PlayBattle(intense)`, `PlayOutcome(victory)`, `Stop()`, `CrossfadeTo(clip, volume)`, `Current` (`Silent`, `Menu`, `Battle`, `Intense`, `Outcome`), `CurrentClip`, `IsPlaying`, `IsIntenseWave(wave)`, `Configure(runner, battleRoot, menu, battle, intense, victory, defeat)`.

### Volume and mixer (`TDGameSettings`)

`Master Volume`, `Music Volume`, `Sfx Volume`, `Ui Volume` (0..1). A sound plays at cue volume × player volume × Master × its channel. With `Persist Volumes` on (default) the four values are loaded from PlayerPrefs on enable and written when they change (keys `Prefs Key Prefix` + `Master`/`Music`/`Sfx`/`Ui`; PlayerPrefs failures only log a warning).

Mixer routing is optional: assign `Music Group`, `Sfx Group`, `Ui Group` (`AudioMixerGroup`) to route each channel through your mixer for effects or snapshots. Volumes are applied on the AudioSources either way, so everything works without a mixer.

Options menu API: `GetVolume(AudioChannel)`, `SetVolume(AudioChannel, value)`, `EffectiveVolume(channel)`, `MixerGroup(channel)`, `LoadVolumes()`, `SaveVolumes()` (flushes PlayerPrefs), event `VolumeChanged`. The sample pause menu shows Master / Music / Effects / Interface sliders bound to these (`GameHud > Pause Volume Sliders`, on by default); closing the pause menu saves them.

### Sample audio

The samples use the sound effects and music in `Samples/Audio` (`Sfx/<key>.ogg`, `Music/<key>.ogg`, generated with Stable Audio, see `ThirdPartyNotices.txt`). The sample generator assigns them by key (`TDMaker.Editor.SampleAudio`): tower families get shot sounds (`tower_arrow_shot`, `tower_cannon_fire`, `tower_magic_cast`), projectiles impact sounds (`arrow_hit`, `cannon_explosion`, `magic_impact`), enemies `enemy_hit` and `enemy_death_small` / `enemy_death_big` by size, soldiers `sword_clash` / `soldier_death`, spells their cast sounds, the audio player the global and mechanic cues, levels `music_battle` / `music_battle_intense` / `music_victory` / `music_defeat`, and the Demo scene `music_menu`. A missing file leaves its cue empty, so generation works (and stays deterministic) without the folder.

### Editor preview

`TDMaker.Editor.AudioCuePreview` plays cues in the editor (edit or play mode): `Play(cue)`, `PlayClip(clip, volume, pitch)`, `Stop()`, `IsPlaying`, `FromProperty(serializedCue)`, `DrawCueRow(label, cue)` and `DrawSection(expanded, title, cues)` (an "Audio" foldout with each cue's field and Play/Stop buttons) for custom inspectors and windows.

## Art sets

An `ArtSet` (Create › 2D Tower Defense Maker › Art Set) maps template view keys to sprites so a whole look can be swapped without code. Assign it on the `EntityViewRegistry`; keys without an entry fall back to the asset's prefab or a generated primitive. All three samples use `BasicArtSet`: original vector units, towers and separate painted maps. The Hound, Revenant, Gravecaller and Husk have their own entries. Imported sprites remain available even when external authoring tools are absent.

Per entry: `View Key`, `Sprite`, optional frame loops (`Walk`, `Idle`, `Attack`, `Hurt`, `Death` frames with their frames-per-second), `Death Sprite` + `Death Hold` (e.g. a grave shown briefly), `Icon` (menus and portraits), `Scale`, health-bar height/width, `Walk Bob`, and for projectiles `Rotate To Flight`, `Impact Sprite` / `Impact Frames`, `Impact Size`. Set-wide: build-slot sprite and scale, `Draw Build Slots`, health-bar back/fill/low sprites.

**Facing direction** – draw or import unit art facing either way. Right-facing art needs nothing; for art drawn facing left, tick **`Faces Left`** on its entry. Units face their movement direction; in a melee engagement (and when an attack starts) they use the simulation's latched facing (`Entity.FacingX`), so a blocker and its enemy face each other. Left- and right-facing sheets can be mixed in one set. (Requires the template's `Facing` to be `FlipSprite` or `ScaleX`.)

## Entity views

`EntityViewRegistry` pools one `EntityView` per entity (prefab from the asset's `View`, the registry's `Overrides`, or a generated primitive). `View` settings: `Shape`/`Color`/`Size`, `Shaded` (outlined style), `Facing` (`None`, `FlipSprite`, `ScaleX`), `Show Health Bar`, `Drive Animator`, `Hooks`.

**Animator parameters** – with `Drive Animator` on, an `Animator` on the prefab receives the parameters it declares (others are skipped):

| `EntityView.AnimatorParameters` | Type | Set when |
|---|---|---|
| `Move` | Bool | The unit moved this frame |
| `Speed` | Float | Movement speed (units per second) |
| `Attack` | Trigger | An attack starts |
| `Hit` | Trigger | Positive damage is taken |
| `Die` | Trigger | Death fade begins |

Animator speed follows the game speed. Built-in feedback: hit flash, death fade, status-effect tint and icons, tower tier pips, projectile trails, impact flashes, splash rings, instant-hit beams, spell cast flash.

**Mechanic feedback** (see [Mechanic Library](mechanics.md)): jagged arcs between chain victims, beams for multi-target attacks, rings for every region pulse (including pulse-only regions) and projectile impact areas, heal glows, a shield bubble that fades with the remaining capacity, dust rings on displacement, greyed disarmed units and translucent untargetable units, trap markers (dim while arming, detection ring once armed, trigger flash), pooled continuous beam lines that follow source and target, reflection and life-steal lines, and path-transfer trails. Colours come from each mechanic's `Color` (or the effect tint; transfers use the registry's `Transfer Color`); optional `Vfx` prefabs go through `VfxPool`. Registry toggles: `Mechanic Arcs`, `Pulse Rings`, `Heal Glows`, `Trap Markers`, `Channel Beams`, `Reaction Lines`.

## Camera, settings and ellipses

**`TDCameraController`** (on the orthographic camera) frames the level on start for any aspect ratio. Its bounds are the level geometry plus `Padding` and the HUD reserve (`Hud Reserve Top/Bottom`), or a fixed rectangle (`Use Fixed Bounds`, set by the Map Editor to the painted map). How the level is framed comes from the level's **Camera Framing** (`LevelAsset.cameraFraming`, or a scene override on Level Authoring):

| Framing (`mode`) | View | Player camera |
|---|---|---|
| **Fit Whole Map** (default) | The whole map on one screen; other aspect ratios show the camera background at the sides or top/bottom | None – no pan, no zoom |
| **Fit Height Scroll Horizontally** | View height = map height | Pan left/right, zoom in |
| **Fit Width Scroll Vertically** | View width = map width | Pan up/down, zoom in |
| **Fixed View Size** | `viewHeight` world units (capped to the map) | Pan both ways, zoom in |

`startFocus` picks the first view (`Center`, `FirstEntrance`, `FirstExit` of path 0) and `introPan` (`introPanSeconds`) pans along the first path from its entrance to its exit when the level starts, then settles on the start focus; any pan or zoom input skips it. Off-screen wave-call buttons are pulled to the screen edge, so scrolling levels still show every entrance. Fields: `Padding`, `Min Zoom`, `Pan Speed`, `Edge Size`, `Zoom Step`, `Smoothing`. `FitToLevel()`, `Bounds`, `Framing`, `IntroPanActive`, `LeftDragging`, `VisibleRect()`, static `FocusPoint(level, area, focus)`.

By default the whole map is visible and the camera does not move. Scrolling is an opt-in per level for maps larger than the screen.

**`TDGameSettings`**: camera inputs – used only in levels whose framing scrolls – `cameraPan` (master), `edgePan` (off by default), `dragPan` (middle mouse), `keyboardPan` (WASD/arrows), `cameraZoom` (wheel, +/−), `leftDragPan` (left drag on the battlefield past a small threshold, not starting over UI; off by default; a press that became a drag is not also a click); `speedControls` (show the 1×/2×/3× buttons; off resets the speed to 1×); `language` and `textTables` ([string tables](#string-tables); `Texts`, `SetLanguage`, `GetLanguages`, `LanguageChanged`); `damageNumbers`, `confirmSell` (off: selling is one click), `showEarlyCallBonus` (off by default), `allowDebugOverlay`. `TDGameSettings.Current` returns the scene instance (or a hidden default). Bind these to your options menu.

**`EllipseRenderer`**: `EllipseRenderer.Create(name, parent, material, sortingOrder, width)`, then `Show(center, range, yScale, lineColor, fillAlpha)` / `Hide()` / `SetWidth(width)`. The shape comes from `RangeShape`, so what is drawn is exactly what the simulation tests.

## Sample screenshots

**Tools > 2D Tower Defense Maker > Capture Sample Screenshot** (`TDMaker.Editor.SampleScreenshot`) plays the Basic sample with a scripted run (builds on every slot, upgrades, calls waves early) and renders the camera with the HUD to a PNG. Batch: `-batchmode -executeMethod TDMaker.Editor.SampleScreenshot.Capture` **without** `-quit` and **without** `-nographics` (the editor exits by itself). Options: `-tdmSeconds N` (default 50), `-tdmWidth` / `-tdmHeight` (default 1920×1080), and `-tdmOut folder` for your chosen output folder. Script errors during capture are counted in the Console log.

## Language selection and click-area priority

The sample title screen's English and Korean buttons call `TDGameSettings.SetLanguage`. With **Persist Language** enabled, the choice is saved in PlayerPrefs. Builds load that choice when present, otherwise use the Inspector language. **Ignore Saved Language In Editor** is on by default so the current Inspector language controls that Play session; turn it off to test persisted-language loading. Turning off **Persist Language** stops saving new choices.

The default tower hit area includes its pad rectangle and the body SpriteRenderer's world bounds. Shadows, health bars and feedback decorations are excluded. When **View > Click Area > Custom Area** is enabled, only the authored rectangle is checked. Heroes keep selection priority; equal-priority overlaps prefer the lower anchor point. While aiming a move, rally point or spell, battlefield clicks remain point attempts.

Before wave 1, the entrance skull button shows the translated **Start Wave** label. Later, its ring shows the time until automatic wave start, and calling early uses the level's early-call reward rules. Twin Roads uses an early-call gold rate of 2 per second.
