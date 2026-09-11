# Mandatory artwork policy — registered generation routes

**Version 2.0.0 · user revision dated September 7, 2026**

Every newly commissioned or creatively revised artwork in this overhaul must use a registered route in `generation-policy.json`. The active user-authorized route uses the available **`image_gen__imagegen`** tool under the root author; it makes no claim about the tool's image model or backend unless that is independently observed. Historical records may use the legacy route: a final prompt written by an actual **Astra agent (`gpt-6-astra`)** and an explicitly selected **`gpt-image-2`** backend with `max` reasoning effort. This supersedes the version-1 alternatives that allowed three generated illustrations alongside code-drawn vectors, deterministic graphics, and reused art.

The normative machine-readable counterpart is `generation-policy.json`. All specifications, role tasks, asset briefs, tests, and acceptance records must follow this policy. It does not expand permission to spend money, publish private inputs, or modify live systems.

## 1. Agent and tool responsibilities

The root retains its current model. Leads, coordinators, implementation agents outside the two art-author roles, and independent reviewers remain Luna/max. **W02-C1-BUILD and W02-C2-BUILD are Astra/max leaves at depth 3** for the legacy route. The complete descendant catalog remains seven leads, fourteen coordinators, and twenty-eight leaves: forty-seven Luna roles and two Astra roles. The root route is explicitly authorized by `art/root-generation-authorization.json`; it does not create a native child or attest a named model.

Use the legacy lineage when that route is selected: root → W02 lead → W02 coordinator → Astra author, with Astra invoking the image-generation tool with **`gpt-image-2`**. The authorized root route is root-authored through `image_gen__imagegen`; it has role `ROOT`, depth `0`, and no parent. Neither image tool is a fourth-level subagent. No leaf may spawn a child, launch a concealed client, or reset its ancestry. Ordinary implementation agents request artwork through the parent/root instead of launching ad hoc art agents. All waiting parents and Astra leaves count toward the 250-open-descendant project ceiling.

Luna agents may gather facts, specify exact wording, list target sizes, identify rights-reviewed references, and write acceptance criteria. These are **briefs**, not final image prompts. The selected route author must independently turn the brief into the actual image-generation prompt and author every creative revision. Merely adding an Astra approval label to another author's final prompt does not establish authorship.

## 2. Universal scope for new artwork

The rule includes marks, logos, wordmarks, avatars, icons, icon sheets, decorative patterns, textures, illustrations, webpage illustrations, empty-state artwork, GitHub banners, social previews, thumbnails, editorial posters, run cards, comparison panels, overlays, lower thirds, title scenes, sponsorship tiles, press graphics, and exported architecture/flow/map/chart presentations. Future campaign instances follow the same rule; the finite initial registry is not an exemption for later art.

In-image typography and geometric diagrams are not exceptions. Supply exact text and source facts to the selected route author; generate them through that route; inspect them at use size. Correct incorrect letters, extra symbols, inconsistent logos, misleading graph geometry, or wrong arrows through another generation/edit on the same registered route. Do not paint a correction with code and keep claiming the final artwork is entirely generated.

New-brand art cannot be supplied by hand-authored SVG paths, Canvas drawing, CSS illustration, Python drawing, stock art, stock icon packs, a different image model, manual repainting, vector tracing, or copying a legacy image as the final result. No blanket “deterministic graphics” or “precise text” escape hatch remains.

## 3. Explicitly separate non-art materials

**Evidence media:** real screenshots, gameplay video, recordings, and empirical captures are source evidence, not commissioned art. They must remain authentic. Never use image generation to invent, repair, upscale by hallucination, extend, or replace evidence. Preserve original captures and permit only disclosed non-generative redaction, encoding, or presentation crops that do not change the claimed result. Evidence exports remain separately indexed in `evidence-media-registry.json`. A generated illustration of a run is a poster, not proof that it occurred.

**Historical material:** legacy marks, proof cards, historical illustrations, token files, and notices remain in their historical/archive context, unchanged where required for rollback or evidence. They are indexed in `reference-registry.json`. They may inform a new generation when rights and inputs are verified; they cannot substitute for new-brand artwork. Do not regenerate historical evidence merely to make its provenance appear compliant with this new commissioning policy.

**Functional software and text:** HTML page structure, CSS layout and typography, buttons, keyboard/focus behavior, live factual UI values, source JSON, data tables, machine-readable Mermaid source, captions, transcripts, alt text, and a textual asset catalog remain code/content. They are not decorative image deliverables. A functional page may display approved generated art alongside real data without regenerating the art on every update. Do not use these exceptions to hand-draw logos, decorative diagrams, or new exported promotional images.

All *exported illustrative diagrams and charts* still require one of the registered generation routes. Keep the canonical graph/data separately accessible and validate the generated presentation against it. A machine-readable planning graph in this package is a specification, not a delivered visual diagram.

## 4. Prompt-to-image workflow

1. The coordinator supplies a bounded task with asset ID, source/reference digests, rights, exact copy, target placements, export requirements, permitted input disclosure, and budget. References must actually exist and be usable; do not invent opaque image IDs or imply a named image was attached.
2. Select the registered route. For the legacy route, verify the author's native identity and effective model/effort. For the root route, use the canonical user authorization record and record `ROOT`, depth `0`, no parent, and no native-agent attestation.
3. The selected author writes the final prompt and stores its exact UTF-8 bytes under `brand/prompts/astra/<asset-id>/<job-id>.md` for the legacy route or `brand/prompts/root/<asset-id>/<job-id>.txt` (or `.md`) for the root route. Both are plain UTF-8 prompt containers; the exact stored bytes and SHA-256 govern, not the extension. Record a SHA-256. The instruction package's briefs are not pre-executed author attestations.
4. Invoke the selected image-generation/edit route. The legacy route explicitly requests `gpt-image-2` and allows verification of the backend. The root route invokes `image_gen__imagegen`; leave author model, effort, image model, and backend as `unknown` or `unspecified` unless trustworthy evidence and a policy update establish them. When a wrapper automatically revises prompts, retain its actual revised prompt if exposed and require the selected author to review it. A generic image tool cannot establish a named backend by itself.
5. Record the actual request/response identifiers or trusted tool-execution trace references; omit credentials. Preserve each returned original unchanged, including its original dimensions, format, and digest.
6. The route author inspects outputs against the acceptance contract. For a revision, that author writes a new prompt with explicit changes and invariants; use the actual previous output as an edit reference and record the lineage. Do not call a failed or missing output a generated master.
7. A separate reviewer checks the art, text, source facts, source permissions, native author evidence for the legacy route or authorization/tool evidence for the root route, model evidence when available, crop safety, small-size legibility, and intended surfaces. The builder does not approve its own final output.
8. Produce permitted mechanical exports and bind every export to its original generation record. The root/integration owner updates the shared manifest, preserving exclusive write ownership.

## 5. Model selection, parameters, and fallback policy

The legacy generation request must select **`gpt-image-2`**, not `auto`, `chatgpt-image-latest`, or an earlier image model. A backend may report a documented dated snapshot; the policy currently recognizes `gpt-image-2-2026-04-21` only with trustworthy alias-resolution evidence. The root route records image model `unknown` and backend `unspecified` when the available tool does not expose those facts. Additional model identities require verified evidence and a recorded policy update; do not guess from name prefixes or tool defaults.

Astra and image generation are distinct model roles. Do not pass `gpt-image-2` as the text author's model or assume that selecting Astra determines the image backend. Do not invent unsupported CLI flags, native-agent config keys, or API parameters. A prompt requesting the correct model is not proof that the runtime selected it.

Export sizes are design targets, not blindly valid model request sizes. Verify the currently supported pixel, edge, aspect-ratio, format, and transparency constraints. Generate on a supported canvas, with intentional safe zones, then crop/resize noncreatively. Preserve actual output dimensions rather than claiming a requested output size was honored. A transparent-capable format alone is not proof of a working alpha channel. Inspect alpha and previews on contrasting backgrounds; if the current tool cannot produce the needed transparency, block the exact export or obtain an explicitly accepted opaque variant rather than changing the design silently.

No assumption of native SVG, layered design files, font binaries, video, or audio output is permitted. Retain PNG/WebP/JPEG outputs as actually supported. Raster content embedded in an SVG wrapper is not an editable vector source and does not satisfy any native-vector promise. Version-1 `.svg` art requirements have been replaced by raster exports; functional document/code requirements remain.

If the selected route, required evidence, inputs, rights, or budget is unavailable, block that exact job. Complete unrelated engineering and textual deliverables. The root authorization permits only the registered available image-tool route; it does not permit an arbitrary model, backend, or drawing method. Do not mark a brief or reference asset delivered. A model-capability blocker is not a reason to stop all website work.

## 6. Mechanical derivatives and reuse

Allowed post-processing is limited to identity/copy, resizing, intentional cropping, format encoding, lossless optimization, metadata stripping, slicing an already generated icon sheet, alpha-preserving export, and assembling unchanged generated frames. These transformations cannot create new creative shapes or labels. A light/dark redesign, new title, altered logo, different composition, new data graphic, or corrected symbol is a creative revision and requires another job through the selected registered route.

Existing *compliant* generated masters can be reused for identical visual content with their original verified prompt and generation lineage. Mechanical responsive crops do not require repeated image calls. The permission to reuse a compliant master is not permission to reuse legacy art with unknown model/authorship provenance.

Motion uses generated stills/layers or generated frames mechanically sequenced, positioned, or faded according to a recorded assembly recipe. Every visible art element must trace to its recorded generation route. Do not introduce a different video generator, procedural drawing, optical-flow invention, or unlicensed music. Retain a reduced-motion still and accessible captions/text. Real episode footage remains the separate evidence-media source.

## 7. Costs, caching, and publication

Use a default maximum of three initial concept candidates and two revision rounds per creative family; justify and authorize additional spend within the actual available budget. Record attempts, including failed ones. Reuse immutable references, prompts, approved masters, and crops by content hash. Repeated model calls are not a requirement for deterministic packaging.

Separate creative production from serving. Website build, local preview, static hosting, email assembly, and repeated viewing must not implicitly call a generation route. A new campaign graphic or source-dependent promotional card creates an explicit bounded art job and review. Ordinary HTML data updates reuse existing art without repainting it. Do not publish stale in-image statistics when the source changes; invalidate that asset's approval and regenerate through its recorded route.

Send only approved inputs to generation. Never submit private raw trajectories, hidden reasoning, secrets, subscriber records, or proprietary game files. Generated art is not automatically trademark-cleared or a publisher endorsement. Brand, rights, factual, model-provenance, and publication reviews are separate checks. Font files must not appear in delivery archives.

## 8. Required record and release gate

Each generation record must identify the route, asset/job, author role/agent/parent/depth, requested/accepted/observed author identity and effort, runtime evidence reference, exact prompt path/hash, image model request and actual model evidence, tool/endpoint, request or trace identifiers, source/reference provenance, raw output path/hash/dimensions, review reference, and any model/tool prompt transformation. Legacy records use the Astra values and native ledger. Root-route records use `ROOT`, `root`, no parent, depth `0`, `unknown` author and image-model values, `unspecified` backend, `image_gen__imagegen`, and the canonical user authorization reference and hash. Each derivative records the job it came from and the enumerated noncreative steps applied.

`validate_assets.py` checks declared provenance, file integrity, and policy consistency. `agent_ledger.py` checks recorded ancestry and role-specific model settings. These helpers do not themselves attest a real provider call or cryptographically authenticate a runtime log; reviewers must inspect the referenced actual records. A fabricated JSON record is not evidence.

Release is blocked for missing mandatory art, unverifiable authorship/model selection, prohibited post-processing, missing rights, unsupported factual text, or mismatched export hashes. Continue to report implementation, artwork completion, review, deployment, and actual campaign operation as separate states.

## Source references

Official OpenAI model documentation consulted September 7, 2026 identifies `gpt-6-astra` and its reasoning settings: https://developers.openai.com/api/docs/models/gpt-6-astra . Image model capabilities: https://developers.openai.com/api/docs/models/gpt-image-2 . Generation/edit workflows: https://developers.openai.com/api/docs/guides/image-generation . Exact current generation parameters and dated model IDs: https://developers.openai.com/api/reference/resources/images/methods/generate . Tool-based prompt transformation is described at https://developers.openai.com/api/docs/guides/tools-image-generation . Recheck installed/account capabilities during execution; documentation is not account-access verification.

## Root record layout

Root prompts use the registry prompt_directory under brand/prompts/root/. Actual successful generation records are consolidated in brand/provenance/root-generation-records.json. Per-asset selected records are in brand/asset-manifest.json, including exact reuse of a declared parent generation for mechanical derivatives such as WEB-01 from BG-01. An asset with no new generation must not receive an invented image-call record. The registry generation_record_directory and generation_record_file describe this layout; blocked future assets may have no record yet.
