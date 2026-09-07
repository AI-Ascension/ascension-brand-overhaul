# Included local helpers

All helpers use Python 3.10+ standard library only. They do not call models, generate images, connect to accounts, or mutate remote systems.

`validate_package.py` verifies this kit's required files, role ancestry, dependency graph, art/surface references, planned state, path safety, and existing manifest hashes. It parses JSON but is not a general-purpose JSON Schema implementation.

`agent_ledger.py PATH` validates recorded native thread relationships, required requested model/effort, model-verification evidence fields, parent lifetimes, and global open-count intervals. The helper does not observe native threads itself and is not an enforcement hook. The root must compare the ledger with trustworthy runtime metadata and use available native limits.

`validate_assets.py --manifest PATH --root OUTPUT_ROOT --ledger NATIVE_LEDGER.json` checks future artwork against the generation-only registry, actual prompt/output hashes, declared Astra identity, role-specific native ledger, requested/observed gpt-image-2 model, permitted export operations, required outputs, source/review/rights fields, and PNG header dimensions. Legacy SVG security parsing is a separate utility, not permission to deliver newly drawn SVG art. It does not replace full schema validation, decoder checks for every media format, visual inspection, malware scanning, or legal review. Blocked assets deliberately prevent a full success result.

`build_delivery.py SOURCE DESTINATION.zip` builds a local deterministic archive, excluding font binaries and common private/dependency directories. The destination must be outside the source directory. Filename exclusions are not a privacy/security audit. No upload occurs.

Run `python -m unittest discover -s tests -v` for positive and negative tests of these helpers. The synthetic runtime and publication examples are only helper-test data; they do not prove the requested agents actually ran or a product was deployed.

`art_policy.py` supplies the role-specific model resolver and generation-record consistency checks. JSON declarations do not prove native execution; inspect trustworthy runtime/image-call records and decoded images separately. Missing required generation evidence fails acceptance.
