# Private website artwork candidate

The reviewed local website revision is `7e63ff4a5317de5305602f5d407a93246e66d248` on `work/root-art-integration`. Its base is `56e532b21922f39480cd15dcbb465676770408f5`, the existing public draft PR head. The new artwork candidate has not been pushed to that public PR or deployed. The bundle contains only the candidate delta and requires the base commit; its hash and all 41 changed-file hashes are in `../github/website-art-candidate.json`.

The 21 artwork images and two token sources are bound to brand source revision `b938b75799aa0525f5a47ed2ec34802653cb02c3`. Local PHP tests passed 30 tests / 114 assertions; 30 local HTTP/TLS mail-sink checks, 48 browser matrix states, six normal-motion states and nine focused fallback states passed. Synthetic signup cases were intercepted locally. Read the linked receipts for their exact scopes and limits.

To restore for local review, use a separate clean website checkout containing the prerequisite commit. Keep the bundle private:

```sh
git clone https://github.com/AI-Ascension/aiascension.tech.git website-art-review
cd website-art-review
git cat-file -e 56e532b21922f39480cd15dcbb465676770408f5^{commit}
git bundle verify /absolute/path/to/website-art-candidate.bundle
git fetch /absolute/path/to/website-art-candidate.bundle refs/heads/work/root-art-integration:refs/heads/review/root-art
git switch review/root-art
git rev-parse HEAD
```

The last command must print `7e63ff4a5317de5305602f5d407a93246e66d248`. If the base is unavailable in the default clone, fetch the existing PR branch named by `../github/website-pull-request.json`, then verify the exact base before importing the bundle. Run the website with its committed Composer lockfile and PHP 8.3; use `php vendor/bin/phpunit` for the local tests. A loopback static preview can display HTML, but must never serve PHP source or handle real forms; use a PHP-capable local server with a temporary test store and mail sink for subscription checks.

Publication, deployment, production SMTP, legal clearance and the complete 72-family artwork release remain separate gates. The bundle is part of the private audit handoff and carries no public distribution approval.
