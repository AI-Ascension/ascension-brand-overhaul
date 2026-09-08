# User-selected models

Ascension must let each individual choose the model and provider they want to use. Product configuration and provider integrations must preserve that choice; no particular model vendor, family, or model name is a product requirement.

Hosted and locally served models are valid integration targets. The harness provider interface owns adapter compatibility. A model needs a compatible adapter and the capabilities required by the selected workflow. Missing support should identify the adapter or capability needed, without silently substituting a different model.

User choice is the product requirement. Compatibility and tested support remain separate facts: accepting a model identifier does not prove that the provider can execute the workflow. Document the selected adapter, configuration and observed test scope for each supported path. Preserve existing model-specific run reports as dated evidence.

Publication records accept user-selected model and provider identifiers in `schemas/publication-manifest.schema.json`. Record the configuration actually used, distinguish requested configuration from observed execution, and leave unavailable identity evidence unknown. Do not infer that every model has been tested.

This product policy records the user's 2026-09-08 clarification: “Native model should be up to the user, we want to support any models that individuals want to use.” The separate build-agent orchestration and artwork-generation instructions govern production of this overhaul; they do not restrict an Ascension user's model choice.
