# Artwork access and execution status

Updated 2026-09-07T21:55:32.920715+00:00. The user authorized root generation with the available image tool; see [the recorded amendment](../art/root-generation-authorization.json).

32 actual generated masters are preserved with exact prompts, input references and SHA-256 hashes. 40 raster exports and 2 functional HTML exports exist. Asset-family states: 51 blocked, 21 verified.

The full requirement remains 72 families and 115 exports. Verified artwork means the scoped generation, source-use and export review passed; it does not authorize public distribution.

The image service rejected CAST-01, CAST-02 and CAST-03 with HTTP 429 `usage_limit_reached`. Remaining creative generation is blocked on service capacity; the recorded reset is 2026-09-14T02:55:51Z. See [failure receipt](../execution/reviews/root-image-service-limit.json).

The image backend and root author model remain unknown. The original native agent hierarchy is a separate unmet requirement. Generated artwork is not gameplay or provider evidence. The press approval registry remains empty.

| Family | Current status | Existing exports | Remaining gate |
| --- | --- | ---: | --- |
| ID-01 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| ID-02 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| ID-03 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| ID-04 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| ID-05 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| ID-06 | verified | 4 | No remaining source/export gate; public distribution approval is separate. |
| ID-07 | verified | 1 | No remaining source/export gate; public distribution approval is separate. |
| ID-08 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| BG-01 | verified | 1 | No remaining source/export gate; public distribution approval is separate. |
| BG-02 | verified | 1 | No remaining source/export gate; public distribution approval is separate. |
| BG-03 | verified | 1 | No remaining source/export gate; public distribution approval is separate. |
| BG-04 | blocked | 2 | Both tile exports exist, but the independent review found visible repeat seams. The mandatory seamless requirement needs a new generated master; image service capacity is unavailable. |
| WEB-01 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| WEB-02 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| WEB-03 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| WEB-04 | verified | 1 | No remaining source/export gate; public distribution approval is separate. |
| WEB-05 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| WEB-06 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| WEB-07 | verified | 1 | No remaining source/export gate; public distribution approval is separate. |
| WEB-08 | verified | 2 | No remaining source/export gate; public distribution approval is separate. |
| RUN-01 | blocked | 1 | The landscape export was independently reviewed. The required square export is missing and needs authored reflow after image service capacity returns. |
| RUN-02 | blocked | 2 | Landscape and vertical exports were independently reviewed. The required square export is missing and needs authored reflow after image service capacity returns. |
| RUN-03 | blocked | 0 | A source master exists, but no required 1600×500 export exists. Independent review requires a new wide creative reflow; image service capacity is unavailable. |
| RUN-04 | verified | 1 | No remaining source/export gate; public distribution approval is separate. |
| RUN-05 | verified | 1 | No remaining source/export gate; public distribution approval is separate. |
| CAST-01 | blocked | 0 | Image tool returned HTTP 429 usage_limit_reached on 2026-09-07. Required authored masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| CAST-02 | blocked | 0 | Image tool returned HTTP 429 usage_limit_reached on 2026-09-07. Required authored masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| CAST-03 | blocked | 0 | Image tool returned HTTP 429 usage_limit_reached on 2026-09-07. Required authored masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| CAST-04 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| CAST-05 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| CAST-06 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| CAST-07 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| MKT-01 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| MKT-02 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| MKT-03 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| MKT-04 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| MKT-05 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| MKT-06 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| MKT-07 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| MKT-08 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| MKT-09 | blocked | 1 | The functional press catalog exists and currently exposes zero downloads. The required generated cover is missing; image service capacity is unavailable. Public distribution approvals remain empty. |
| DOC-01 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| DOC-02 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| DOC-03 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| DOC-04 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| DOC-05 | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-01-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-01-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-02-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-02-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-03-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-03-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-04-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-04-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-05-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-05-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-06-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-06-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-07-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-07-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-08-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-08-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-09-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-09-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-10-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-10-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-11-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-11-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-12-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-12-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-13-B | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |
| GH-13-S | blocked | 0 | No image invocation was completed for this family. Creative generation is blocked by the service quota observed on CAST-01 through CAST-03; required masters and exports are missing. See execution/reviews/root-image-service-limit.json. |

Review the [asset board](../art/asset-board.html), [functional specimen](assets/identity/specimen.html), [press catalog](assets/press/index.html), [source records](provenance/root-generation-records.json), and [export receipts](provenance/root-export-receipts.json).
