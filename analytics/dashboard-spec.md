# Measurement dashboard specification

The dashboard consumes only validated `event-v1` records from
`analytics/event-contract.json`. It does not read Laminar, MLflow, gateway,
game-mod, provider, host, subscription address, or private run telemetry.

Events carry a public content ID, a day or minute timestamp, an event name,
surface, optional campaign tag, and optional consented coarse cohort. A cohort
value is an aggregate bucket, not an identity. No email address, private run
ID, prompt, action payload, save, token, full referrer, IP address, user agent,
or device fingerprint may enter the event envelope.

Each panel reports the numerator, denominator, exclusion rules, time window,
and bot/test filtering from the contract. A panel with no eligible observations
shows `No observations`; it never displays a fabricated zero. A measured zero
is valid only when a non-empty denominator exists and no numerator events were
observed.

Audience panels cover eligible run-page views, meaningful reading or watching,
decision presentation and interaction, evidence inspection, and a consented
cohort repeat-engagement proxy. Developer panels cover setup starts,
server-confirmed quickstart completion, documentation errors, and contributor
workflow observations. Subscription panels consume only server-confirmed
success events and never expose or hash an address.

Game outcomes and infrastructure failures have separate dimensions. A game
defeat is not a publication failure, and a setup or host failure is not a game
defeat. Comparative run outcomes remain in the run publication records and are
not used as audience conversion events.

The default retention window is 90 days. Delete or aggregate records when the
window expires. Corrections append a replacement event or correction record in
the measurement store; they do not rewrite a public run manifest. Bot and test
traffic must be filtered using an explicit server-side rule before a metric is
shown. Client button clicks cannot create `quickstart_success`,
`subscribe_confirmed`, or `unsubscribe_completed`; those require a
server-confirmed observation.

The offline implementation in `publisher.events` validates events and returns
metric values as `None` with state `no_observations` when the denominator is
absent. Its fixture lane is synthetic and must never be treated as audience
data.


Production panels require the operator-enrolled upstream receipt described in `docs/MEASUREMENT.md`. The offline aggregator enforces that receipt's weekly/monthly UTC windows, observation cutoff, public-content eligibility, and explicit bot/test/infrastructure exclusions before calculating values. Panels must display the returned scope and mark incomplete windows as partial. Synthetic output has scope `local_unscoped_test` and is excluded from production panels. No deployed collector, enrolled production receipt, or observed traffic is asserted by this specification.
