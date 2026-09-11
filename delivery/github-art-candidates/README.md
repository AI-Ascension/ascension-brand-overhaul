# Private GitHub artwork candidates

The map in this directory records twelve independently reviewed candidate bundles. They preserve generated artwork privately for review; no public consumer push, merge or settings change is authorized by a bundle or review result.

For a candidate, read its repository, stable repository ID, `public_prerequisite`, bundle path and SHA-256, `head`, and copied-file hashes in `github-art-candidates-map.json`. Restore into a fresh clone, preserving existing working directories. The clone must contain the exact prerequisite commit; a newer default branch is not a substitute for that object.

For example, after setting `candidate_bundle` to the absolute path of `GH01-sts2-harness.bundle`, the GH-01 candidate can be inspected with:

```sh
sha256sum "$candidate_bundle"
git clone --no-checkout https://github.com/AI-Ascension/sts2-harness.git candidate-harness
git -C candidate-harness fetch origin d2105005ebdb6a5f7dd5e266e80b139e294cf89e
git -C candidate-harness bundle verify "$candidate_bundle"
git -C candidate-harness fetch "$candidate_bundle" HEAD
git -C candidate-harness switch --detach FETCH_HEAD
git -C candidate-harness rev-parse HEAD
git -C candidate-harness diff --stat d2105005ebdb6a5f7dd5e266e80b139e294cf89e HEAD
```

Compare the bundle digest and restored head with the map before using the candidate. The independent review verified bundle restoration and source/export byte equality. Recheck these values after transferring files. Review the README, the art-sync receipt and each PNG against the declared changed-file inventory.

GH-11 intentionally has a two-commit candidate history: its final direct-parent delta repairs the receipt, while its integration-base delta contains the complete five-file presentation change. Both bases are recorded explicitly. GH-13 is the root repository's own presentation and is excluded from these twelve bundles.

The existing website artwork candidate is separately described in `../../github/website-art-candidate.json`; GH-10 adds repository presentation on top of that local candidate. Neither establishes a deployed website. Before any authorized public push or merge, refresh the remote identity, target head, required checks, publication authority and resulting scope.
