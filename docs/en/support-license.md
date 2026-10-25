# Support and licenses

## Getting help

Start with [Quick Start](quick-start.md) and the [FAQ](faq.md). For content problems, run **Tools > 2D Tower Defense Maker > Validate Project** and review the first relevant error. [Editor Tools](editor-tools.md#project-validator) explains how to open an issue in its authoring tool.

When contacting the publisher through the support details supplied with your Asset Store purchase, include:

- Your 2D Tower Defense Maker package version and Unity Editor version.
- The render pipeline and input backend you use.
- Clear steps to reproduce the issue, the expected result and the actual result.
- Relevant Console messages and, when useful, a small reproduction scene or screenshot.

Remove credentials and private project data from shared logs or reproduction projects.

## Package license and notices

The license supplied with your purchase governs use of **2D Tower Defense Maker**. Included third-party font software retains its own license. The package's complete third-party inventory is in `Assets/TDMaker/Documentation/ThirdPartyNotices.txt`; keep that file and the applicable font notices with redistributed font software.

The included sample gameplay content, maps and sprites are original. Sample maps and sprites use hand-authored vector artwork with procedural shape fallbacks. The font software and generated sample audio are described below.

## Inter

- **Inter 4.1**, copyright 2016 The Inter Project Authors.
- License: **SIL Open Font License 1.1**.
- Original Regular, Medium, SemiBold and Bold TTF files are included under `Assets/TDMaker/Samples/Fonts/Inter/`, alongside their generated static TextMesh Pro SDF assets.
- Full license: `Assets/TDMaker/Samples/Fonts/Inter/OFL.txt`.
- Source: [Inter 4.1 release](https://github.com/rsms/inter/releases/tag/v4.1), `Inter-4.1.zip`, `extras/ttf/Inter-Regular.ttf`, `Inter-Medium.ttf`, `Inter-SemiBold.ttf` and `Inter-Bold.ttf`, unmodified.

## Noto Sans KR

- **Noto Sans KR Regular 2.004**, copyright 2014-2021 Adobe.
- License: **SIL Open Font License 1.1**.
- Original font: `Assets/TDMaker/Samples/Fonts/NotoSansKR-Regular.otf`; the adjacent dynamic SDF asset is generated from it.
- Full license: `Assets/TDMaker/Samples/Fonts/OFL.txt`.
- Source: [Noto CJK, Sans2.004](https://github.com/notofonts/noto-cjk/tree/Sans2.004), `Sans/SubsetOTF/KR/NotoSansKR-Regular.otf`, unmodified.

The bundled OFL texts permit fonts to be bundled and embedded with software, with their copyright and license notices. The font software must not be sold by itself. Modified font software remains subject to the OFL, including any reserved-name conditions. The OFL does not require documents created with the fonts to use that license. Read the included license files for the complete terms.

If your game does not need Korean, remove the Noto Sans KR fallback entries before removing its font assets. Keep the Inter font files and their own OFL notice when continuing to use Inter.

## Sample audio

The publisher generated the sample sound effects and music with **Stable Audio 3**, a Stability AI model used under the [Stability AI Community License](https://stability.ai/community-license-agreement). The model is not included in the package.

**Powered by Stability AI**

## Unity packages and TextMesh Pro resources

The runtime depends on Unity packages distributed by Unity under their own licenses:

- Universal Render Pipeline (`com.unity.render-pipelines.universal`).
- 2D Sprite (`com.unity.2d.sprite`).
- uGUI / TextMesh Pro (`com.unity.ugui`).
- Input System (`com.unity.inputsystem`), optional; the legacy Input Manager is also supported.

Import **TMP Essential Resources** in your project through **Tools > 2D Tower Defense Maker > Import TMP Essential Resources**. These Unity resources are not redistributed with the package. The included fonts keep a reference to Unity's `TMP_SDF-Mobile` shader, which that import resolves. See [Text, fonts and languages](presentation.md#text-fonts-and-languages).
