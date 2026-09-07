# Identity and background review

The independent source review cleared 11 of 12 identity/background masters for mechanical export. It required correcting the typography specimen caption from Geist Mono to JetBrains Mono. Root generated that correction as ID-08 generation 002; the second independent review confirmed the JetBrains Mono caption and complete 1600×2000 export. See [second-batch review](../execution/reviews/W02-root-art-second-batch-review.json).

This document summarizes recorded visual findings. It does not attest an image backend, certify legal clearance, authorize publication, or complete the original native agent-tree requirement.

Source review: [W02 root-art identity review](../execution/reviews/W02-root-art-identity-review.json). Current generation route: [recorded user authorization](../art/root-generation-authorization.json).

| Family | Reviewed source generation | Source finding |
| --- | ---: | --- |
| ID-01 | 4 | ready_for_mechanical_export |
| ID-02 | 1 | ready_for_mechanical_export |
| ID-03 | 1 | ready_for_mechanical_export |
| ID-04 | 1 | ready_for_mechanical_export |
| ID-05 | 1 | ready_for_mechanical_export |
| ID-06 | 1 | ready_for_mechanical_export |
| ID-07 | 1 | ready_for_mechanical_export |
| ID-08 | 2 | Generation 001 rejected for font caption; generation 002 independently reviewed and ready |
| BG-01 | 1 | ready_for_mechanical_export |
| BG-02 | 1 | ready_for_mechanical_export |
| BG-03 | 1 | ready_for_mechanical_export |
| BG-04 | 1 | ready_for_mechanical_export; subtle repeat seams remain |

## Usage findings

- The avatar remains recognizable at 96, 48 and 24 px. The simplified favicon was inspected at 64, 32 and 16 px.
- Small evidence icons need adjacent text labels; the sheet alone does not supply accessible meaning.
- The selected mark/wordmark sources intentionally have opaque backgrounds. They are not transparent overlays.
- The route-pattern tiles have faint tonal seams in a repeated field; a strict seamless requirement remains unresolved.
- Generated type specimens illustrate font references. Functional typography and color values come from tokens.css, with system fallbacks when licensed fonts are not installed.

## Current artifacts

- [Functional specimen](assets/identity/specimen.html)
- [Raster specimen](assets/identity/specimen.png)
- [Actual source index](provenance/root-generation-index.json)
- [Mechanical export receipts](provenance/root-export-receipts.json)
- [Current asset status manifest](asset-manifest.json)

Every final export must retain its own hash and actual source-generation record. The identity/background families other than BG-04 have now passed the scoped source, export and provenance gates. BG-04 remains blocked for visible repeat seams. See the [root acceptance record](../execution/root-art-acceptance.json) and current manifest; no public distribution approval is issued.
