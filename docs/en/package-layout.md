# Maker and Samples

2D Tower Defense Maker is a reusable runtime framework and a set of authoring tools. You create and own the content of your game. The complete sample game is an optional reference implementation.

## Install the Maker

1. Import `2D-Tower-Defense-Maker-0.1.0.unitypackage` into a Unity 6 URP 2D project.
2. Import TMP Essential Resources once when prompted.
3. Open **Tools > 2D Tower Defense Maker > Welcome**, then **New Level**.
4. Keep **Fresh starter assets** selected and **Use Sample Sounds** off. Create the level in your own folder, such as `Assets/TDMakerContent/MyLevel`.
5. Edit the paths, build slots, units and waves, then play. Follow [Quick Start](quick-start.md).

The Maker package works on its own. The default New Level flow does not load the sample game's scene generator, string tables, artwork, audio, campaign or balance assets. It creates a Level, Wave Set, HUD Theme, units, material and scene inside your chosen folder. A fresh HUD uses the project's TMP default font until you assign your own font in its theme.

## Add optional examples

Import `2D-Tower-Defense-Maker-Samples-0.1.0.unitypackage` **after** the Maker package. Then open **Tools > 2D Tower Defense Maker > Samples > Browse Samples**.

| Part | Purpose | Location |
|---|---|---|
| Maker runtime | Simulation, authoring components, views, configurable HUD, campaign/save/shop systems | `Assets/TDMaker/Runtime/` |
| Maker tools | New Level, Workshop, Map Editor, Wave Timeline, Upgrade Tree, Validator and Dry Run | `Assets/TDMaker/Editor/` except `Editor/Samples/` |
| Your game | Your own scenes, units, waves, settings and chosen presentation | `Assets/TDMakerContent/` by default, or your own folder |
| Complete sample game | Example title, slots, world map, star shop and three battles | `Assets/TDMaker/Samples/Demo/` |
| Feature examples | Basic, Crossroads, Winding Pass and compiled extension examples | `Assets/TDMaker/Samples/` |
| Sample presentation | Original art, audio, Inter, Korean fallback and example text tables | `Assets/TDMaker/Samples/` |
| Sample authoring utilities | Optional generator, sample art importer and screenshot driver | `Assets/TDMaker/Editor/Samples/` |

The sample add-on uses the same Maker runtime. It does not contain a second copy of the engine. Existing sample paths, asset GUIDs and `TDMaker.*` namespaces are preserved.

**Fresh starter assets** is the default and creates independent content. **Reuse sample kit** and **Use Sample Sounds** deliberately reference the optional add-on. If you choose them, keep the referenced sample assets or replace those references with your own assets before removing the add-on. Regenerating sample content resets generated example files; it does not regenerate your own New Level folder.

## Features are choices, samples are examples

- Campaigns, saving and the permanent star shop are reusable Maker features. The sample's map, track prices, unlock sequence and title menu are example content.
- The engine supports both automatic hero skill unlocking and explicit skill-point purchases. The compact sample HUD shows portraits and health bars, so its heroes use automatic skill growth. To use `SpendPoints` in your own game, enable **Hero Skill Buttons** on Game HUD or supply a skill-allocation UI. Combat skill points are separate from the campaign's saved star-upgrade shop.
- The sample game starts in English and has no title-screen language buttons. String tables, Korean fallback fonts and the language API remain available for your own game.
- The compact sample battle HUD displays spell buttons without a large background panel. Hero portraits and health bars sit at the bottom left. You may restyle or replace the HUD through `HudTheme` and the runtime API.

Use the examples to learn the authoring model. Start production content with New Level and keep it in your own folder.
