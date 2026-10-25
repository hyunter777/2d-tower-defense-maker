# FAQ

**The range circle I see does not look like a circle.**
By design. Ranges are ellipses with horizontal radius `r` and vertical radius `k·r` (range Y scale `k`, default 0.8) to match an oblique top-down view. The drawn ellipse is exactly the area the simulation tests. Set the level's `Range Y Scale` to `1` for true circles.

**Which enemy does a tower shoot first?**
With the default priority **First**, the enemy with the shortest remaining *path length* to the exit – not the one nearest to the exit point. Players can switch a tower to Last, Strongest, Weakest or Closest at runtime.

**An enemy died on the exit line. Did I lose a life?**
No. Damage and death are resolved before exits in each tick, so a unit that takes lethal damage in the tick it reaches the exit counts as killed: bounty paid, no life lost.

**Why did selling refund everything?**
Before the first wave starts, selling refunds the full investment. After that the refund is `investment × Refund Share` (level rules, default 0.6). The tower asset's old `Refund Ratio` field is hidden and unused; the Upgrade Tree and Tower inspector also show the level's share.

**How much does an upgrade cost?**
The `Cost` of the tier you upgrade *into*. Each tier's cost is incremental.

**The first wave does not start.**
Wave 1 waits for the player (the HUD's **Start Wave** button or `CallNextWave`) unless `Auto Start First` is enabled on it.

**I called a wave early but got no gold.**
Calling wave 1 never pays. For later waves, the reward is based on the rounded remaining seconds of `Auto Delay`; if the wave was about to start anyway, the reward can be 0. Check `Early Gold Per Second` or the level's early-call override.

**My barracks soldiers do not block anything.**
Check that the Soldier has `Melee` enabled, the enemy is `Blockable` and not `Flying`, its `Blocker Capacity` is above 0, and the rally point can reach a lane inside the tower's `Rally Radius`. The Validator and the Build Slot inspector warn about most of these.

**Building a barracks is rejected with `InvalidRallyPoint`.**
No lane passes through the tower's rally ellipse at that slot. Move the slot closer to the path or increase `Rally Radius`.

**Enemy regeneration never triggers.**
Turn off `Idle Only` in the enemy's `Regeneration`; walking enemies are never idle.

**My new enemy is ignored by waves.**
Entries without an `Enemy` are skipped when baking. The Wave Timeline and Validator flag them.

**"Template id '…' is used by both …"**
Two assets in the same level resolve to the same id (blank ids use the asset name). Give one a unique `Template Id`.

**Does 3× speed change the outcome?**
No. Speed only changes how many fixed ticks run per frame. See [Determinism and Replay](determinism-and-replay.md).

**Can I restyle the HUD or use my own UI?**
Restyle the `Game HUD` with a `HUD Theme` asset (TextMesh Pro font, sprites, colours, sizes) and change its words with string tables. For a completely different UI, read `Simulation.State` and `Simulation.Entities`, send commands with `SimulationRunner.Enqueue`, listen to `SimulationRunner.EventRaised`, and remove the `Game HUD` (and `TD Hud`) components. See [Presentation](presentation.md) and [Extending the Framework](extending.md#how-the-view-consumes-events).

**How do I make a healer, a shielded unit or a knockback tower?**
Use the built-in mechanic blocks: pulse-only healing auras, status effects with `Shield`, and damage `Impact` payloads with displacement. See [Mechanic Library](mechanics.md); the Basic sample's Mender, Storm Spire and Cannon III use them.

**The HUD has no text, or text shows as boxes.**
No text at all: the TextMesh Pro Essential Resources are not imported – use **Tools > 2D Tower Defense Maker > Import TMP Essential Resources**. Boxes: the font has no glyphs for that language (for example Korean with the default LiberationSans); add a dynamic CJK font asset as a fallback. See [Presentation](presentation.md#text-fonts-and-languages).

**How do I translate the HUD or add a language?**
Duplicate `Samples/Text/Text_English`, set its language code, translate, add it to `TDGameSettings > Text Tables` and select the language (`TDGameSettings.Current.SetLanguage("de")`). Missing texts fall back to English. See [Presentation](presentation.md#string-tables).

**Can I use my own sprites and animations?**
Use an **ArtSet** entry keyed by the asset's `View Key` for sprites and animation frames (the Unit Workshop supports bulk frame registration), or assign a prefab in the asset's `View` section (or in the Entity View Registry's `Overrides` by view key). Add an `EntityView` component to the prefab to control the body renderer and sorting.

**Input System or legacy Input Manager?**
Both work. The HUD reads input through `PointerInput`, which uses the Input System package when it is installed and enabled, and the legacy Input Manager otherwise.

**Where do stars and permanent upgrades go?**
Win a campaign level, return to its world map and open **Upgrades**. The sample campaign awards at most nine stars; each shop track costs 0 / 0 / 1 / 2 / 3 stars, so take its free starter ranks first. Purchases are saved in the active slot and apply when the next battle starts. See [Campaigns, Progress and Saves](campaign.md).

**Mobile / touch?**
This release is **PC only (mouse and keyboard; touch UI not yet)**. The core is platform-independent; other platforms require your own input/UI and target-device testing.

**Can I add a new mechanic without editing package code?**
Yes: custom systems, per-entity data, target selectors, damage hooks, ability actions and commands. See [Extending the Framework](extending.md) and the compiled examples in `Samples/Extending`.

**Where are the logs from Dry Run and the Validator?**
The Map Editor shows **Validate**, **Dry Run** and the latest results above its scrolling content. Click the error/warning summary to open the full Validator list. The complete Dry Run report and `ValidatorWindow.RunBatch` results are also written to the Console.

**Why is the interface still English after I set the Inspector language to `ko`?**
In the Editor, enable **Ignore Saved Language In Editor** and set **Language** to `ko`. If that option is disabled, the saved PlayerPrefs language takes precedence. You can also select Korean from the sample title screen. Keep the Korean text table and the sample theme's fallback font assigned together.

**Why is there no spell button in my fresh level?**
Enable **Include Starter Spell** in the New Level wizard. For an existing level, create a Spell in Unit Workshop and add it to the Level asset's **Spells** list. Audio is a separate choice: **Use Sample Sounds** is off by default for fresh content.

**Why does clicking a tower not open its panel?**
If you are aiming a hero move, spell or rally point, right-click to cancel first. By default, both the tower body sprite and its pad are clickable. If **Custom Area** is enabled, only the authored rectangle is used.

**Which time zone do save-slot timestamps use?**
Saves record the operating system's UTC time in ISO 8601 format. The slot screen displays local time using the Gregorian `yyyy-MM-dd HH:mm` format. Existing timestamps are preserved; correcting the system clock does not rewrite older save dates.

**Does a colored Wave Set icon mean there is an error?**
2D Tower Defense Maker does not assign a special red warning icon to Wave Sets. Check the Validator's error/warning counts and Inspector messages rather than judging an asset by its icon color.
