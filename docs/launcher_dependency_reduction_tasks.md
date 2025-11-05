# Launcher Dependency Reduction Tasks

This backlog turns the strategic recommendations around replacing Quake Live's proprietary launcher stack into actionable engineering work. Each section corresponds to a major dependency cluster identified during analysis.

## 1. Prototype service abstraction without Awesomium
- [ ] Catalogue every Awesomium entry point used by the legacy launcher (`WebCore::Initialize`, `WebView::Create`, custom `WebSession` preferences).
- [ ] Document the JavaScript bindings exposed to the launcher UI, noting the underlying native functions and data dependencies.
- [ ] Map Awesomium data source lookups (PAK/PK3 interceptors, in-memory resources) to candidate replacements within the GPL engine asset system.
- [ ] Design a bridging layer inside `src/code/ui/` that rehosts the required UI flows using the existing Quake III menu scripting system.
- [ ] Build a proof-of-concept menu that exercises the new bridging layer, validating parity for authentication prompts and core navigation.
- [ ] Record validation criteria (rendering parity, input handling, localisation) required before fully removing the Awesomium runtime.

## 2. Replace Steamworks-specific flows
- [ ] Enumerate every `steam_api` symbol referenced by the proprietary launcher and native DLLs, grouping them by feature area (auth, matchmaking, workshop, overlay, stats).
- [ ] For each feature area, identify open-source substitutes (e.g., GameNetworkingSockets, REST services) or design platform-neutral abstractions callable from both launcher and engine code.
- [ ] Define build-time toggles that allow optional integration of the proprietary Steamworks SDK without blocking open builds.
- [ ] Draft API contracts for the new service layer (authentication tokens, lobby descriptors, inventory payloads) and document expected request/response formats.
- [ ] Prototype at least one substitute flow (e.g., matchmaking) end-to-end, including mock services where necessary, and capture migration gaps.
- [ ] Outline QA criteria covering Steam-enabled builds, open-source-only builds, and mixed environments to ensure feature parity.

## 3. Rebuild media playback pipeline
- [ ] Audit existing FFmpeg usage within the launcher (video playback widgets, transcoding helpers) to understand codec requirements and performance expectations.
- [ ] Produce a minimal FFmpeg (or alternative library) build configuration that satisfies identified requirements while remaining redistributable.
- [ ] Refactor the media playback bridge so it can operate inside the GPL engine context, sharing rendering surfaces with the in-engine UI.
- [ ] Implement automated playback tests (sample trailers/tutorials) to verify decoding accuracy and resource management.
- [ ] Document deployment guidance for the rebuilt pipeline, including licensing notes and packaging steps for each supported platform.
- [ ] Track follow-up work for advanced features (streaming downloads, background playback) that may depend on additional services.
