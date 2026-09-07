# Privacy-minimal measurement contract

W05 measurement is an event contract and a reviewable dashboard definition,
not a claim about current traffic. The source baseline and any real analytics
observations remain the responsibility of W01 and the eventual deployed
operator.

The audience funnel is eligible impression or view → meaningful episode or run
page engagement → decision presentation and interaction → evidence inspection
→ a consented coarse repeat-visit proxy. The developer funnel is docs visit →
setup start → server-confirmed useful workflow → repeat use or contribution.
Stars and followers are context only.

The capability renderer accepts either a list of records matching the existing
`schemas/capability.schema.json` or W01's
`ai-ascension.capabilities.v1` envelope. It preserves exact source IDs and
revisions, including uppercase IDs, and only sorts a copy for display. It does
not treat a source-derived record as an independent reproduction or release
support, and it does not create a current claim when W01 has not supplied a
dated source.

Every event uses `event-v1` and includes a public content ID, a coarse day or
minute timestamp, event name, surface, optional campaign tag, consent state,
optional consented cohort, server-observation state, environment, and a small
allowlist of coarse properties. The validator rejects unknown fields and
sensitive fields. A local guess is an anonymous local interaction; it is not a
community vote and produces no aggregate count in the publisher.

The contract keeps game outcomes, infrastructure failures, publication errors,
and client validation errors distinct. Server-confirmed subscription and
quickstart events cannot be inferred from a button click. If repeat identity
cannot be measured without tracking people, the dashboard shows an aggregate
cohort proxy or `No observations`.

Run `python3 -m unittest tests/test_measurement.py -v` for the synthetic local
checks. The synthetic records and their metric output are local test data and
must not be used as production observations.
