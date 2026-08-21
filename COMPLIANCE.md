# API & Distribution Compliance Notes

_Last reviewed against public YouTube API documentation: August 20, 2026_

Video Destim Terminal's public release tries to make responsible personal self-hosting the default, but this document is **not legal advice, not a YouTube API compliance certification, and not evidence of YouTube approval**.

YouTube's API terms, Developer Policies, Required Minimum Functionality, and branding rules can change independently of this project. The operator of each self-hosted instance uses their own API credentials and is responsible for current compliance.

Authoritative starting points:

- YouTube API Services Terms: https://developers.google.com/youtube/terms/api-services-terms-of-service
- Developer Policies: https://developers.google.com/youtube/terms/developer-policies
- Developer Policies guide: https://developers.google.com/youtube/terms/developer-policies-guide
- Required Minimum Functionality: https://developers.google.com/youtube/terms/required-minimum-functionality
- Branding Guidelines: https://developers.google.com/youtube/terms/branding-guidelines
- Revision History: https://developers.google.com/youtube/terms/revision-history

The revision history should be checked before each public release. In 2026, YouTube added/updated additional policies concerning derived metrics and data storage, so old API-policy summaries should not be treated as permanent.

## Public-release safeguards / design choices

The v1.30 release:

- Uses the application name **Video Destim Terminal**, not a product name containing `YouTube` or `YT`.
- Shows `Developed with YouTube API` on the `about` screen.
- Includes a first-run privacy/terms acknowledgement and always-available `LEGAL` access.
- Links to YouTube Terms of Service and Google Privacy Policy.
- Provides local `export-data` and confirmed `delete-data` mechanisms.
- Keeps the YouTube API key server-side and excludes it from normal browser state/export output.
- Binds the Docker service to localhost by default so operators can put HTTPS/private-network access in front of it.
- Uses a best-effort housekeeping pass to refresh stored public API resource metadata before 30 days and remove/replace stale metadata for unavailable resources where practical.
- Does not embed, alter, proxy, or download the YouTube audiovisual stream; a confirmed request opens a normal YouTube watch URL.
- Does not bundle ReVanced, browser extensions, third-party APKs, or alternate playback clients.

## Known policy-review areas

These are intentionally documented rather than presented as solved/certified.

### 1. Branding / attribution placement

Current YouTube Developer Policies/Branding Guidelines say pages/features displaying YouTube content should make YouTube's source clear using applicable YouTube Brand Features, and the branding guidance discusses a `Developed with YouTube` logo for clients that are heavily dependent on YouTube content.

VDT v1.30 instead uses text-only `Developed with YouTube API` attribution on the `about` screen because that is the project's chosen interface treatment. **This document does not claim that the current placement/text satisfies YouTube's current branding requirements.** Re-review before broader/public/commercial deployment.

### 2. Optional title normalization

`NORMALIZE VIDEO TITLE CAPS?` is disabled by default. When enabled, VDT changes the capitalization of some title words in its displayed/recorded text.

Current YouTube developer-policy guidance states that video metadata such as titles should remain visible and unmodified. Therefore, enabling title normalization is a known compliance risk. Operators prioritizing strict policy adherence should leave it disabled unless they have obtained appropriate guidance/approval.

The emoji terminal treatment is display styling only: creator-provided emoji characters remain present in the title text.

### 3. Credits, cooldowns, eligibility filtering, and intentional selection

VDT deliberately uses self-imposed watch credits, cooldowns, creator curation, and eligibility filtering as independent product behavior.

It does not gate/modify an embedded YouTube player; VDT's control layer ends by opening a normal YouTube watch URL. However, current Developer Policies contain user-experience and playback-integrity requirements for API clients and YouTube-resource actions.

The maintainer/operator should independently review whether VDT's intentional selection controls fit YouTube's current interpretation. If uncertain, use YouTube's API compliance/audit process rather than assuming the handoff design alone resolves the question.

### 4. Local Stats / derived activity metrics

VDT calculates local statistics about **VDT request behavior**, such as credits spent, request count, requested-video time, rewatch count, average gap between requests, and creator request counts.

Some of those calculations use API-sourced resource metadata (for example duration/creator name) alongside locally created request events. YouTube's 2026 policy updates added additional rules around derived metrics/statistical data for audited/approved use cases.

VDT does not claim these stats are YouTube Analytics metrics, but that label alone does not determine policy compliance. Re-review this feature against the current Developer Policies before broader distribution/use cases, especially if adding analytics, scoring, comparisons, or long-term statistical storage.

## Stored API metadata

The application uses a 29-day threshold and periodic best-effort refresh so resource metadata is refreshed before 30 days where the instance is running and the API request succeeds.

No self-hosted process can guarantee a refresh while the host is powered off, disconnected, out of quota, or unable to reach the API. Operators remain responsible for data-storage policy obligations.

## Third-party playback documentation

`docs/PLAYBACK-OPTIONS.md` describes independent playback environments that may complement VDT's low-stimulation goal.

VDT does not distribute modified YouTube applications, browser extensions, ad blockers, SponsorBlock, NewPipe/PipePipe, or third-party APKs. It simply opens a URL.

Those third-party tools have their own terms/policies and can change independently of VDT. Operators are responsible for whichever playback environment they choose.

## When to seek an audit/review

Before large-scale, commercial, promoted, multi-user, or otherwise expanded deployment, review the current authoritative documents above. If the policy fit is uncertain, use YouTube's available API compliance/audit channels rather than relying on this repository's interpretation.
