# Video Destim Terminal Privacy Notice

_Last updated: August 20, 2026_

Video Destim Terminal is self-hosted software. This notice describes the behavior of the unmodified v1.30 distribution. If you modify the software, expose it to additional users, add analytics, or operate it as a service for other people, you are responsible for updating your privacy disclosures accordingly.

## YouTube API Services

VDT uses the YouTube Data API v3 to retrieve public channel and video metadata. By using VDT's YouTube-related features, you also acknowledge that Google/YouTube services are governed by their own policies, including:

- YouTube Terms of Service: https://www.youtube.com/t/terms
- Google Privacy Policy: https://policies.google.com/privacy
- YouTube API Services Terms: https://developers.google.com/youtube/terms/api-services-terms-of-service
- YouTube Developer Policies: https://developers.google.com/youtube/terms/developer-policies

## Data stored by your instance

The unmodified application stores data locally in `data/video-destim-terminal.db`, including:

- VDT settings and credit state;
- creator links and public creator metadata;
- video identifiers/public video metadata needed for local watched/request-history behavior;
- VDT watch-request timestamps and local watched/rewatch state;
- locally calculated VDT request/activity statistics;
- cooldown state and the time statistics tracking began;
- cache/metadata-refresh housekeeping state.

The project author does not receive this database from independently hosted instances.

## API key and override PIN

Your YouTube Data API key and cooldown override PIN are stored in your local `.env` file and made available to the server process.

The API key is used by server-side API requests and is not intentionally exposed to the browser or included in `export-data`.

The override PIN is not an authentication credential and must not be treated as one.

## Stored YouTube API metadata

The public distribution includes a best-effort metadata refresh routine. Saved public/non-authorized YouTube API resource metadata is checked periodically and refreshed before reaching 30 days of age. If a resource is no longer returned, stale API-derived metadata is removed/replaced from the applicable local record where the implementation can do so.

Operators remain responsible for reviewing current YouTube API policies because those policies can change.

## Browser storage

VDT uses browser local/session storage for small interface state, including:

- the per-browser first-run legal acknowledgement;
- return-screen state used when handing playback off to another app/site;
- legacy migration input if an older pre-database VDT build left compatible state in browser storage.

## Network requests made by the unmodified interface

Normal operation can involve:

- server-side requests to `www.googleapis.com` for YouTube Data API v3 metadata;
- browser requests to `fonts.googleapis.com` and `fonts.gstatic.com` for the VT323 web font;
- navigation to a standard `youtube.com/watch` URL after the user confirms a watch request;
- YouTube/Google legal-policy pages if the user chooses those links;
- `ko-fi.com/vespux` only if the user opens SUPPORT and answers Yes to the tip-jar confirmation.

Ordinary network-request information such as IP address, browser headers, or server egress IP can therefore be visible to the relevant third-party service under its own privacy practices.

## Playback handoff

When you confirm a video, VDT returns/navigates to a standard YouTube watch URL. From that point onward, the selected browser/player and its provider control playback-related data handling.

Optional playback tools described in the documentation are independent third-party projects and are not part of VDT.

## No VDT telemetry to the project author

The unmodified distribution does not contain a VDT analytics/telemetry service and does not send your local VDT database to the project author.

## Export and deletion

`export-data` downloads a JSON copy of local configuration/creator/history state. It intentionally excludes the YouTube API key and override PIN, but the export can still contain private local usage/history information and should be protected accordingly.

`delete-data` (also available from `LEGAL`) permanently resets the local VDT database after confirmation. It does **not** delete information held by YouTube/Google or any third-party playback application.

## Security and retention

You control the host and therefore control filesystem permissions, backups, network exposure, and retention of your local files.

Protect `.env`, `data/`, exports, and backups as private data. For access/security guidance, see `SECURITY.md`.
