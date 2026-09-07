# Included local helpers

Python helpers use Python 3.10+ standard library; schema tests additionally use the pinned development requirement. The JavaScript browser runner uses the pinned Playwright and axe development dependencies. These helpers do not call models, generate artwork, or mutate remote systems. Runtime observation reads local client metadata; browser review connects only to the supplied loopback site and blocks external requests.

`validate_package.py` verifies this kit's required files, role ancestry, dependency graph, art/surface references, planned state, path safety, and existing manifest hashes. It parses JSON but is not a general-purpose JSON Schema implementation.

`agent_ledger.py PATH` validates recorded native thread relationships, required requested model/effort, model-verification evidence fields, parent lifetimes, and global open-count intervals. The helper does not observe native threads itself and is not an enforcement hook. The root must compare the ledger with trustworthy runtime metadata and use available native limits.

`validate_assets.py --manifest PATH --root OUTPUT_ROOT --ledger NATIVE_LEDGER.json` checks future artwork against the generation-only registry, actual prompt/output hashes, declared Astra identity, role-specific native ledger, requested/observed gpt-image-2 model, permitted export operations, required outputs, source/review/rights fields, and PNG header dimensions. Legacy SVG security parsing is a separate utility, not permission to deliver newly drawn SVG art. It does not replace full schema validation, decoder checks for every media format, visual inspection, malware scanning, or legal review. Blocked assets deliberately prevent a full success result.

`build_delivery.py SOURCE DESTINATION.zip` builds a local deterministic archive, excluding font binaries and common private/dependency directories. The destination must be outside the source directory. Filename exclusions are not a privacy/security audit. No upload occurs.

Run `python -m unittest discover -s tests -v` for positive and negative tests of these helpers. The synthetic runtime and publication examples are only helper-test data; they do not prove the requested agents actually ran or a product was deployed.

`art_policy.py` supplies the role-specific model resolver and generation-record consistency checks. JSON declarations do not prove native execution; inspect trustworthy runtime/image-call records and decoded images separately. Missing required generation evidence fails acceptance.

`runtime_snapshot.py --database PATH --root-id ID` reads only the installed client metadata needed to observe native ancestry and model settings. Store its output privately. Thread existence is not current liveness, native closure or independent provider attestation.

`sync_content.py --source-repo PATH --consumer-root PATH --plan PATH` previews canonical functional content exports from a full Git commit. `--apply` changes local managed copies and their receipt only after digest checks. It rejects unrelated edits, path collisions, symlinks and plans omitting previously managed files. Artwork has a separate approval gate.

`node scripts/browser_review.mjs --base-url URL --routes FILE --output NEW_DIRECTORY` captures actual local website states at five widths and two themes, with reduced motion and automated accessibility checks. The route manifest supplies `id`, `path`, and expected `status` (200 or 404). Open the captured images and separately test keyboard interaction, forms, ordinary motion and zoom. Captures are test evidence, not new brand art or proof of a production deployment.

`render_handoff.py --output NEW_FILE` renders the curated requirement, art and operation ledgers. It refuses missing inventory entries, changed binding requirements and unsupported verified states. It is deterministic for unchanged inputs and refuses overwriting its output. A rendered ledger remains a report, not independent acceptance; final evidence and companion revisions must be reconciled before delivery.

The handoff release ledger has an exact schema marker/field set, nonempty summary and dimensions, and bounded nonempty string arrays. Duplicate JSON keys and non-regular paths fail. Legacy reports may omit the ledger; `FINAL_REPORT.md` and `--require-release` require it. Source-snapshot and complete-tree inventory hashes are included when present.
