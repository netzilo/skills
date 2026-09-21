---
id: '33'
title: API request schemas
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 61196
sections:
- id: get-api-accounts
  title: '`GET /api/accounts`'
  chars: 233
- id: put-api-accounts-accountid
  title: '`PUT /api/accounts/{accountId}`'
  chars: 1879
- id: delete-api-accounts-accountid
  title: '`DELETE /api/accounts/{accountId}`'
  chars: 331
- id: post-api-ai-scanprompt
  title: '`POST /api/ai/scanprompt`'
  chars: 412
- id: post-api-auth-tokens
  title: '`POST /api/auth/tokens`'
  chars: 515
- id: get-api-auth-tokens-sessionid
  title: '`GET /api/auth/tokens/{sessionId}`'
  chars: 222
- id: get-api-dns-nameservers
  title: '`GET /api/dns/nameservers`'
  chars: 258
- id: post-api-dns-nameservers
  title: '`POST /api/dns/nameservers`'
  chars: 1367
- id: get-api-dns-nameservers-nsgroupi
  title: '`GET /api/dns/nameservers/{nsgroupId}`'
  chars: 352
- id: put-api-dns-nameservers-nsgroupi
  title: '`PUT /api/dns/nameservers/{nsgroupId}`'
  chars: 1466
- id: delete-api-dns-nameservers-nsgro
  title: '`DELETE /api/dns/nameservers/{nsgroupId}`'
  chars: 346
- id: get-api-dns-settings
  title: '`GET /api/dns/settings`'
  chars: 245
- id: put-api-dns-settings
  title: '`PUT /api/dns/settings`'
  chars: 369
- id: get-api-edge-discovered-tools
  title: '`GET /api/edge/discovered-tools`'
  chars: 239
- id: delete-api-edge-discovered-tools
  title: '`DELETE /api/edge/discovered-tools/{discoveredToolId}`'
  chars: 293
- id: post-api-edge-discovered-tools-d
  title: '`POST /api/edge/discovered-tools/{discoveredToolId}/analyze`'
  chars: 312
- id: post-api-edge-discovered-tools-d
  title: '`POST /api/edge/discovered-tools/{discoveredToolId}/block`'
  chars: 293
- id: post-api-edge-discovered-tools-d
  title: '`POST /api/edge/discovered-tools/{discoveredToolId}/sanction`'
  chars: 434
- id: post-api-edge-events
  title: '`POST /api/edge/events`'
  chars: 501
- id: get-api-edge-filters
  title: '`GET /api/edge/filters`'
  chars: 348
- id: post-api-edge-filters
  title: '`POST /api/edge/filters`'
  chars: 891
- id: get-api-edge-filters-filterid
  title: '`GET /api/edge/filters/{filterId}`'
  chars: 263
- id: put-api-edge-filters-filterid
  title: '`PUT /api/edge/filters/{filterId}`'
  chars: 944
- id: delete-api-edge-filters-filterid
  title: '`DELETE /api/edge/filters/{filterId}`'
  chars: 267
- id: get-api-edge-scanners
  title: '`GET /api/edge/scanners`'
  chars: 219
- id: post-api-edge-scanners
  title: '`POST /api/edge/scanners`'
  chars: 615
- id: get-api-edge-scanners-catalog
  title: '`GET /api/edge/scanners/catalog`'
  chars: 241
- id: get-api-edge-scanners-generate
  title: '`GET /api/edge/scanners/generate`'
  chars: 282
- id: post-api-edge-scanners-generate
  title: '`POST /api/edge/scanners/generate`'
  chars: 397
- id: get-api-edge-scanners-scannerid
  title: '`GET /api/edge/scanners/{scannerId}`'
  chars: 268
- id: put-api-edge-scanners-scannerid
  title: '`PUT /api/edge/scanners/{scannerId}`'
  chars: 670
- id: delete-api-edge-scanners-scanner
  title: '`DELETE /api/edge/scanners/{scannerId}`'
  chars: 271
- id: get-api-edge-tools
  title: '`GET /api/edge/tools`'
  chars: 210
- id: post-api-edge-tools
  title: '`POST /api/edge/tools`'
  chars: 686
- id: get-api-edge-tools-catalog
  title: '`GET /api/edge/tools/catalog`'
  chars: 235
- id: get-api-edge-tools-toolid
  title: '`GET /api/edge/tools/{toolId}`'
  chars: 253
- id: put-api-edge-tools-toolid
  title: '`PUT /api/edge/tools/{toolId}`'
  chars: 735
- id: delete-api-edge-tools-toolid
  title: '`DELETE /api/edge/tools/{toolId}`'
  chars: 259
- id: get-api-event-streaming
  title: '`GET /api/event-streaming`'
  chars: 247
- id: post-api-event-streaming
  title: '`POST /api/event-streaming`'
  chars: 371
- id: get-api-event-streaming-getlogvi
  title: '`GET /api/event-streaming/getLogVideos`'
  chars: 306
- id: post-api-event-streaming-sign-ur
  title: '`POST /api/event-streaming/sign-urls`'
  chars: 313
- id: delete-api-event-streaming-strea
  title: '`DELETE /api/event-streaming/{streamingId}`'
  chars: 288
- id: get-api-events
  title: '`GET /api/events`'
  chars: 227
- id: post-api-events
  title: '`POST /api/events`'
  chars: 345
- id: get-api-events-paginated
  title: '`GET /api/events/paginated`'
  chars: 593
- id: get-api-getclient
  title: '`GET /api/getclient`'
  chars: 266
- id: get-api-getsecdata
  title: '`GET /api/getsecdata`'
  chars: 231
- id: get-api-groups
  title: '`GET /api/groups`'
  chars: 227
- id: post-api-groups
  title: '`POST /api/groups`'
  chars: 367
- id: get-api-groups-groupid
  title: '`GET /api/groups/{groupId}`'
  chars: 306
- id: put-api-groups-groupid
  title: '`PUT /api/groups/{groupId}`'
  chars: 452
- id: delete-api-groups-groupid
  title: '`DELETE /api/groups/{groupId}`'
  chars: 311
- id: get-api-integrations
  title: '`GET /api/integrations`'
  chars: 226
- id: post-api-integrations
  title: '`POST /api/integrations`'
  chars: 484
- id: put-api-integrations-integration
  title: '`PUT /api/integrations/{integrationId}`'
  chars: 547
- id: delete-api-integrations-integrat
  title: '`DELETE /api/integrations/{integrationId}`'
  chars: 278
- id: get-api-locations-countries
  title: '`GET /api/locations/countries`'
  chars: 269
- id: get-api-locations-countries-coun
  title: '`GET /api/locations/countries/{country}/cities`'
  chars: 333
- id: get-api-lookup-account
  title: '`GET /api/lookup-account`'
  chars: 204
- id: get-api-mfa
  title: '`GET /api/mfa`'
  chars: 201
- id: post-api-mfa
  title: '`POST /api/mfa`'
  chars: 312
- id: put-api-mfa
  title: '`PUT /api/mfa`'
  chars: 311
- id: get-api-peers
  title: '`GET /api/peers`'
  chars: 348
- id: get-api-peers-stream
  title: '`GET /api/peers-stream`'
  chars: 354
- id: post-api-peers-bulk-delete
  title: '`POST /api/peers/bulk-delete`'
  chars: 348
- id: post-api-peers-sync
  title: '`POST /api/peers/sync`'
  chars: 340
- id: get-api-peers-peerid
  title: '`GET /api/peers/{peerId}`'
  chars: 300
- id: put-api-peers-peerid
  title: '`PUT /api/peers/{peerId}`'
  chars: 677
- id: delete-api-peers-peerid
  title: '`DELETE /api/peers/{peerId}`'
  chars: 306
- id: get-api-peers-peerid-aidr-snapsh
  title: '`GET /api/peers/{peerId}/aidr-snapshot`'
  chars: 377
- id: get-api-peers-peerid-aidr-snapsh
  title: '`GET /api/peers/{peerId}/aidr-snapshot/events`'
  chars: 547
- id: post-api-peers-peerid-aidr-snaps
  title: '`POST /api/peers/{peerId}/aidr-snapshot/replay`'
  chars: 506
- id: get-api-peers-peerid-aidr-snapsh
  title: '`GET /api/peers/{peerId}/aidr-snapshot/search`'
  chars: 392
- id: get-api-policies
  title: '`GET /api/policies`'
  chars: 233
- id: post-api-policies
  title: '`POST /api/policies`'
  chars: 1008
- id: get-api-policies-policyid
  title: '`GET /api/policies/{policyId}`'
  chars: 313
- id: put-api-policies-policyid
  title: '`PUT /api/policies/{policyId}`'
  chars: 1096
- id: delete-api-policies-policyid
  title: '`DELETE /api/policies/{policyId}`'
  chars: 317
- id: get-api-posture-checks
  title: '`GET /api/posture-checks`'
  chars: 251
- id: post-api-posture-checks
  title: '`POST /api/posture-checks`'
  chars: 836
- id: get-api-posture-checks-posturech
  title: '`GET /api/posture-checks/{postureCheckId}`'
  chars: 352
- id: put-api-posture-checks-posturech
  title: '`PUT /api/posture-checks/{postureCheckId}`'
  chars: 943
- id: delete-api-posture-checks-postur
  title: '`DELETE /api/posture-checks/{postureCheckId}`'
  chars: 349
- id: get-api-profiles
  title: '`GET /api/profiles`'
  chars: 348
- id: post-api-profiles
  title: '`POST /api/profiles`'
  chars: 687
- id: put-api-profiles-profileid
  title: '`PUT /api/profiles/{profileId}`'
  chars: 778
- id: delete-api-profiles-profileid
  title: '`DELETE /api/profiles/{profileId}`'
  chars: 302
- id: post-api-register
  title: '`POST /api/register`'
  chars: 527
- id: get-api-reports
  title: '`GET /api/reports`'
  chars: 211
- id: post-api-reports
  title: '`POST /api/reports`'
  chars: 706
- id: get-api-reports-reportid
  title: '`GET /api/reports/{reportId}`'
  chars: 258
- id: delete-api-reports-reportid
  title: '`DELETE /api/reports/{reportId}`'
  chars: 262
- id: get-api-routes
  title: '`GET /api/routes`'
  chars: 227
- id: post-api-routes
  title: '`POST /api/routes`'
  chars: 1603
- id: get-api-routes-routeid
  title: '`GET /api/routes/{routeId}`'
  chars: 306
- id: put-api-routes-routeid
  title: '`PUT /api/routes/{routeId}`'
  chars: 1688
- id: delete-api-routes-routeid
  title: '`DELETE /api/routes/{routeId}`'
  chars: 311
- id: get-api-setup-keys
  title: '`GET /api/setup-keys`'
  chars: 239
- id: post-api-setup-keys
  title: '`POST /api/setup-keys`'
  chars: 1281
- id: get-api-setup-keys-keyid
  title: '`GET /api/setup-keys/{keyId}`'
  chars: 318
- id: put-api-setup-keys-keyid
  title: '`PUT /api/setup-keys/{keyId}`'
  chars: 1365
- id: delete-api-setup-keys-keyid
  title: '`DELETE /api/setup-keys/{keyId}`'
  chars: 295
- id: get-api-smartsearch
  title: '`GET /api/smartsearch`'
  chars: 269
- id: post-api-smartsearch
  title: '`POST /api/smartsearch`'
  chars: 468
- id: get-api-stats
  title: '`GET /api/stats`'
  chars: 209
- id: post-api-stripe
  title: '`POST /api/stripe`'
  chars: 220
- id: get-api-summary
  title: '`GET /api/summary`'
  chars: 246
- id: get-api-support-openapi-yml
  title: '`GET /api/support/openapi.yml`'
  chars: 233
- id: get-api-support-sessions
  title: '`GET /api/support/sessions`'
  chars: 324
- id: post-api-support-sessions
  title: '`POST /api/support/sessions`'
  chars: 225
- id: get-api-support-sessions-session
  title: '`GET /api/support/sessions/{sessionId}`'
  chars: 295
- id: delete-api-support-sessions-sess
  title: '`DELETE /api/support/sessions/{sessionId}`'
  chars: 282
- id: post-api-support-sessions-sessio
  title: '`POST /api/support/sessions/{sessionId}/messages`'
  chars: 452
- id: get-api-templates
  title: '`GET /api/templates`'
  chars: 217
- id: get-api-templates-category
  title: '`GET /api/templates/{category}`'
  chars: 326
- id: get-api-tenant
  title: '`GET /api/tenant`'
  chars: 205
- id: put-api-tenant
  title: '`PUT /api/tenant`'
  chars: 435
- id: get-api-tenant-logo
  title: '`GET /api/tenant/logo`'
  chars: 215
- id: post-api-tenant-logo
  title: '`POST /api/tenant/logo`'
  chars: 232
- id: delete-api-tenant-logo
  title: '`DELETE /api/tenant/logo`'
  chars: 215
- id: get-api-tenant-logo-info
  title: '`GET /api/tenant/logo/info`'
  chars: 224
- id: post-api-tenant-subscription
  title: '`POST /api/tenant/subscription`'
  chars: 472
- id: post-api-tenant-subscription-con
  title: '`POST /api/tenant/subscription/confirm`'
  chars: 510
- id: post-api-tokens-revoke
  title: '`POST /api/tokens/revoke`'
  chars: 311
- id: get-api-users
  title: '`GET /api/users`'
  chars: 337
- id: post-api-users
  title: '`POST /api/users`'
  chars: 899
- id: get-api-users-userid
  title: '`GET /api/users/{userId}`'
  chars: 281
- id: put-api-users-userid
  title: '`PUT /api/users/{userId}`'
  chars: 713
- id: delete-api-users-userid
  title: '`DELETE /api/users/{userId}`'
  chars: 306
- id: get-api-users-userid-auth-factor
  title: '`GET /api/users/{userId}/auth-factors`'
  chars: 293
- id: delete-api-users-userid-auth-fac
  title: '`DELETE /api/users/{userId}/auth-factors`'
  chars: 280
- id: post-api-users-userid-invite
  title: '`POST /api/users/{userId}/invite`'
  chars: 320
- id: put-api-users-userid-name
  title: '`PUT /api/users/{userId}/name`'
  chars: 336
- id: put-api-users-userid-password
  title: '`PUT /api/users/{userId}/password`'
  chars: 348
- id: get-api-users-userid-tokens
  title: '`GET /api/users/{userId}/tokens`'
  chars: 330
- id: post-api-users-userid-tokens
  title: '`POST /api/users/{userId}/tokens`'
  chars: 485
- id: get-api-users-userid-tokens-toke
  title: '`GET /api/users/{userId}/tokens/{tokenId}`'
  chars: 397
- id: delete-api-users-userid-tokens-t
  title: '`DELETE /api/users/{userId}/tokens/{tokenId}`'
  chars: 387
- id: post-api-verify-recaptcha
  title: '`POST /api/verify-recaptcha`'
  chars: 261
---
# API request schemas

Generated from Netzilo Server's OpenAPI description on 2026-09-21 by `scripts/gen-api-schemas.py`.

**Read the schema before any write.** Every `POST`/`PUT`/`PATCH`/`DELETE` below lists the
required fields; a body missing one is rejected with 422. The live, version-exact copy is
served to admins at `GET /api/support/openapi.yml`; the Netzilo dashboard's AI assistant
reads it with its `netzilo_api_schema` tool before proposing a change. Use this file when
you have no server to ask.

Base URL: `https://<server>/api`; every path below is relative to `https://<server>`.

## `GET /api/accounts`

List all Accounts

Responses: `200` A JSON array of accounts, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/accounts/{accountId}`

Update an Account

Parameters:
- `accountId` (path, required): The unique identifier of an account

Request body (JSON):
- `settings` (object, **required**)
  - `peer_login_expiration_enabled` (boolean, **required**): Enables or disables peer login expiration globally. After peer's login has expired the user has to log in (authenticate). Applies only to peers that were added by a user (interactive SSO login). — e.g. `True`
  - `peer_login_expiration` (integer, **required**): Period of time after which peer login expires (seconds). — e.g. `43200`
  - `peer_inactivity_expiration_enabled` (boolean, **required**): Enables or disables peer inactivity expiration globally. After peer's session has expired the user has to log in (authenticate). Applies only to peers that were added by a user (interactive SSO login). — e.g. `True`
  - `peer_inactivity_expiration` (integer, **required**): Period of time of inactivity after which peer session expires (seconds). — e.g. `43200`
  - `regular_users_view_blocked` (boolean, **required**): Allows blocking regular users from viewing parts of the system. — e.g. `True`
  - `groups_propagation_enabled` (boolean, optional): Allows propagate the new user auto groups to peers that belongs to the user — e.g. `True`
  - `jwt_groups_enabled` (boolean, optional): Allows extract groups from JWT claim and add it to account groups. — e.g. `True`
  - `jwt_groups_claim_name` (string, optional): Name of the claim from which we extract groups names to add it to account groups. — e.g. `roles`
  - `jwt_allow_groups` (array of string, optional): List of groups to which users are allowed access
  - `extra` (?, optional)

Responses: `200` An Account object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/accounts/{accountId}`

Delete an Account

Parameters:
- `accountId` (path, required): The unique identifier of an account

Responses: `200` Delete account status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/ai/scanprompt`

Scan a prompt

Request body (JSON):
- `prompt` (string, **required**)
- `instruction` (string, optional): Optional AI rule instruction; empty means built-in jailbreak detection

Responses: `200` Scan result, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `412` Precondition failed, `422` Validation failed, `500` Internal Server Error

## `POST /api/auth/tokens`

Store PKCE tokens for a client session

Request body (JSON):
- `session_id` (string, **required**)
- `access_token` (string, **required**)
- `refresh_token` (string, optional)
- `id_token` (string, optional)
- `token_type` (string, optional)
- `expires_in` (integer, optional)
- `use_id_token` (boolean, optional)

Responses: `200` Stored, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/auth/tokens/{sessionId}`

Poll for stored PKCE tokens

Parameters:
- `sessionId` (path, required)

Responses: `200` Poll result, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/dns/nameservers`

List all Nameserver Groups

Responses: `200` A JSON Array of Nameserver Groups, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/dns/nameservers`

Create a Nameserver Group

Request body (JSON):
- `name` (string, **required**): Name of nameserver group name — e.g. `Google DNS`
- `description` (string, **required**): Description of the nameserver group — e.g. `Google DNS servers`
- `nameservers` (array of object, **required**): Nameserver list
  - `ip` (string, **required**): Nameserver IP — e.g. `8.8.8.8`
  - `ns_type` (string (udp), **required**): Nameserver Type — e.g. `udp`
  - `port` (integer, **required**): Nameserver Port — e.g. `53`
- `enabled` (boolean, **required**): Nameserver group status — e.g. `True`
- `groups` (array of string, **required**): Distribution group IDs that defines group of peers that will use this nameserver group
- `primary` (boolean, **required**): Defines if a nameserver group is primary that resolves all domains. It should be true only if domains list is empty. — e.g. `True`
- `domains` (array of string, **required**): Match domain list. It should be empty only if primary is true.
- `search_domains_enabled` (boolean, **required**): Search domain status for match domains. It should be true only if domains list is not empty. — e.g. `True`

Responses: `200` A Nameserver Groups Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/dns/nameservers/{nsgroupId}`

Retrieve a Nameserver Group

Parameters:
- `nsgroupId` (path, required): The unique identifier of a Nameserver Group

Responses: `200` A Nameserver Group object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/dns/nameservers/{nsgroupId}`

Update a Nameserver Group

Parameters:
- `nsgroupId` (path, required): The unique identifier of a Nameserver Group

Request body (JSON):
- `name` (string, **required**): Name of nameserver group name — e.g. `Google DNS`
- `description` (string, **required**): Description of the nameserver group — e.g. `Google DNS servers`
- `nameservers` (array of object, **required**): Nameserver list
  - `ip` (string, **required**): Nameserver IP — e.g. `8.8.8.8`
  - `ns_type` (string (udp), **required**): Nameserver Type — e.g. `udp`
  - `port` (integer, **required**): Nameserver Port — e.g. `53`
- `enabled` (boolean, **required**): Nameserver group status — e.g. `True`
- `groups` (array of string, **required**): Distribution group IDs that defines group of peers that will use this nameserver group
- `primary` (boolean, **required**): Defines if a nameserver group is primary that resolves all domains. It should be true only if domains list is empty. — e.g. `True`
- `domains` (array of string, **required**): Match domain list. It should be empty only if primary is true.
- `search_domains_enabled` (boolean, **required**): Search domain status for match domains. It should be true only if domains list is not empty. — e.g. `True`

Responses: `200` A Nameserver Group object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/dns/nameservers/{nsgroupId}`

Delete a Nameserver Group

Parameters:
- `nsgroupId` (path, required): The unique identifier of a Nameserver Group

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/dns/settings`

Retrieve DNS settings

Responses: `200` A JSON Object of DNS Setting, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/dns/settings`

Update DNS Settings

Request body (JSON):
- `disabled_management_groups` (array of string, **required**): Groups whose DNS management is disabled

Responses: `200` A JSON Object of DNS Setting, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/discovered-tools`

List discovered Tools

Responses: `200` A JSON array of discovered tools, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/edge/discovered-tools/{discoveredToolId}`

Dismiss a discovered Tool

Parameters:
- `discoveredToolId` (path, required)

Responses: `200` Dismissed, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/edge/discovered-tools/{discoveredToolId}/analyze`

Re-run AI analysis of a discovered Tool

Parameters:
- `discoveredToolId` (path, required)

Responses: `200` Analyzed, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/edge/discovered-tools/{discoveredToolId}/block`

Block a discovered Tool

Parameters:
- `discoveredToolId` (path, required)

Responses: `200` Blocked, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/edge/discovered-tools/{discoveredToolId}/sanction`

Sanction a discovered Tool

Parameters:
- `discoveredToolId` (path, required)

Request body (JSON):
- `tool_id` (string, **required**): ID of an existing tool to link to the discovered entry

Responses: `200` Sanctioned, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/edge/events`

Push client events

Request body (JSON):
- `events` (array of object, **required**): At most 100 events per request
  - `timestamp` (string, optional): RFC3339; defaults to now
  - `activity` (integer, optional): Numeric activity code
  - `json_meta` (string, optional): JSON-encoded metadata object

Responses: `200` Stored, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/filters`

List all Filters

Parameters:
- `os` (query, optional): Client OS; switches the response to expanded filters for the caller

Responses: `200` A JSON array of Filter or ExpandedFilter objects, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/edge/filters`

Create a Filter

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `os` (array of string, **required**): Must contain at least one OS
- `groups` (array of string, **required**): Must contain at least one group ID
- `posture_checks` (array of string, optional)
- `tools` (array of string, **required**): Must contain at least one tool ID
- `scanners` (array of string, **required**): Must contain at least one scanner ID
- `agents` (array of string, optional): Process path patterns (wildcards and env vars) proxied through the network when the filter is active
- `any_check_must_pass` (boolean, optional)

Responses: `200` The created Filter, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/filters/{filterId}`

Retrieve a Filter

Parameters:
- `filterId` (path, required)

Responses: `200` A Filter object, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/edge/filters/{filterId}`

Update a Filter

Parameters:
- `filterId` (path, required)

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `os` (array of string, **required**): Must contain at least one OS
- `groups` (array of string, **required**): Must contain at least one group ID
- `posture_checks` (array of string, optional)
- `tools` (array of string, **required**): Must contain at least one tool ID
- `scanners` (array of string, **required**): Must contain at least one scanner ID
- `agents` (array of string, optional): Process path patterns (wildcards and env vars) proxied through the network when the filter is active
- `any_check_must_pass` (boolean, optional)

Responses: `200` The updated Filter, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/edge/filters/{filterId}`

Delete a Filter

Parameters:
- `filterId` (path, required)

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/scanners`

List all Scanners

Responses: `200` A JSON array of Scanners, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/edge/scanners`

Create a Scanner

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `severity` (string (low | medium | high | critical), **required**): Case-insensitive; stored lower-case
- `context` (array of string, **required**): Must contain at least one value; the first one is stored as context_type
- `rule_yaml` (string, **required**)
- `enabled` (boolean, optional)

Responses: `200` The created Scanner, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/scanners/catalog`

List the Scanner catalog

Responses: `200` A JSON array of catalog entries, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/scanners/generate`

Check AI rule generation availability

Responses: `200` Generation is available, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `428` Generation is not available, `500` Internal Server Error

## `POST /api/edge/scanners/generate`

Generate a scanner rule with AI

Request body (JSON):
- `prompt` (string, **required**)
- `current_yaml` (string, optional)

Responses: `200` text/event-stream of generation frames, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `428` Precondition required, `500` Internal Server Error

## `GET /api/edge/scanners/{scannerId}`

Retrieve a Scanner

Parameters:
- `scannerId` (path, required)

Responses: `200` A Scanner object, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/edge/scanners/{scannerId}`

Update a Scanner

Parameters:
- `scannerId` (path, required)

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `severity` (string (low | medium | high | critical), **required**): Case-insensitive; stored lower-case
- `context` (array of string, **required**): Must contain at least one value; the first one is stored as context_type
- `rule_yaml` (string, **required**)
- `enabled` (boolean, optional)

Responses: `200` The updated Scanner, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/edge/scanners/{scannerId}`

Delete a Scanner

Parameters:
- `scannerId` (path, required)

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/tools`

List all Tools

Responses: `200` A JSON array of Tools, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/edge/tools`

Create a Tool

Request body (JSON):
- `name` (string, **required**)
- `transport` (string (stdio | sse | streamable_http), **required**)
- `description` (string, optional)
- `url` (string, optional)
- `command` (string, optional)
- `args` (array of string, optional)
- `env` (object, optional)
- `auth_if_needed` (boolean, optional)
- `categories` (array of string, **required**): Must contain at least one category
- `icon` (string, optional)
- `enabled` (boolean, optional)

Responses: `200` The created Tool, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/tools/catalog`

List the Tool catalog

Responses: `200` A JSON array of catalog entries, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/tools/{toolId}`

Retrieve a Tool

Parameters:
- `toolId` (path, required)

Responses: `200` A Tool object, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/edge/tools/{toolId}`

Update a Tool

Parameters:
- `toolId` (path, required)

Request body (JSON):
- `name` (string, **required**)
- `transport` (string (stdio | sse | streamable_http), **required**)
- `description` (string, optional)
- `url` (string, optional)
- `command` (string, optional)
- `args` (array of string, optional)
- `env` (object, optional)
- `auth_if_needed` (boolean, optional)
- `categories` (array of string, **required**): Must contain at least one category
- `icon` (string, optional)
- `enabled` (boolean, optional)

Responses: `200` The updated Tool, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/edge/tools/{toolId}`

Delete a Tool

Parameters:
- `toolId` (path, required)

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/event-streaming`

List event streaming targets

Responses: `200` A JSON array of event streaming targets, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/event-streaming`

Create an event streaming target

Request body (JSON):
- `platform` (string, **required**)
- `config` (object, **required**)
- `enabled` (boolean, **required**)

Responses: `200` Save status, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/event-streaming/getLogVideos`

List session recording videos

Parameters:
- `prefix` (query, optional): Object key prefix to list

Responses: `200` Pre-signed URLs, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/event-streaming/sign-urls`

Sign recording URLs

Request body (JSON):
- array of string

Responses: `200` Pre-signed URLs, in the order of the request, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/event-streaming/{streamingId}`

Delete an event streaming target

Parameters:
- `streamingId` (path, required)

Responses: `200` Delete status, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/events`

List all Events

Responses: `200` A JSON Array of Events, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/events`

Create an Event

Request body (JSON):
- `activity` (integer, **required**): Numeric activity code
- `meta` (object, **required**)

Responses: `200` The JSON string "success", `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/events/paginated`

List Events with pagination and filters

Parameters:
- `limit` (query, optional)
- `offset` (query, optional)
- `order` (query, optional)
- `user` (query, optional): Filter by initiator user ID
- `code` (query, optional): Filter by activity string code; repeat the parameter for several codes
- `date_from` (query, optional)
- `date_to` (query, optional)
- `q` (query, optional): Free-text search

Responses: `200` A page of Events, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/getclient`

Download the client installer

Parameters:
- `os` (query, optional)

Responses: `301` Redirect to the installer, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/getsecdata`

Retrieve security data for the calling user

Responses: `200` Security data, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/groups`

List all Groups

Responses: `200` A JSON Array of Groups, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/groups`

Create a Group

Request body (JSON):
- `name` (string, **required**): Group name identifier — e.g. `devs`
- `peers` (array of string, optional): List of peers ids

Responses: `200` A Group Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/groups/{groupId}`

Retrieve a Group

Parameters:
- `groupId` (path, required): The unique identifier of a group

Responses: `200` A Group object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/groups/{groupId}`

Update a Group

Parameters:
- `groupId` (path, required): The unique identifier of a group

Request body (JSON):
- `name` (string, **required**): Group name identifier — e.g. `devs`
- `peers` (array of string, optional): List of peers ids

Responses: `200` A Group object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/groups/{groupId}`

Delete a Group

Parameters:
- `groupId` (path, required): The unique identifier of a group

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/integrations`

List all Integrations

Responses: `200` A JSON array of Integrations, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/integrations`

Create an Integration

Request body (JSON):
- `platform` (string, **required**): Integration platform identifier, e.g. openai, anthropic
- `enabled` (boolean, **required**)
- `config` (object, **required**): Platform-specific configuration, e.g. {"api_key": "..."}

Responses: `200` The created Integration, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/integrations/{integrationId}`

Update an Integration

Parameters:
- `integrationId` (path, required)

Request body (JSON):
- `platform` (string, **required**): Integration platform identifier, e.g. openai, anthropic
- `enabled` (boolean, **required**)
- `config` (object, **required**): Platform-specific configuration, e.g. {"api_key": "..."}

Responses: `200` The updated Integration, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/integrations/{integrationId}`

Delete an Integration

Parameters:
- `integrationId` (path, required)

Responses: `200` Delete status, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/locations/countries`

List all country codes

Responses: `200` List of countries, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `412` Precondition failed, `422` Validation failed, `500` Internal Server Error

## `GET /api/locations/countries/{country}/cities`

List all city names by country

Parameters:
- `country` (path, required)

Responses: `200` List of cities, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `412` Precondition failed, `422` Validation failed, `500` Internal Server Error

## `GET /api/lookup-account`

Look up a tenant

Parameters:
- `search` (query, required)

Responses: `200` Tenant identity, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/mfa`

Retrieve MFA settings

Responses: `200` MFA settings, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/mfa`

Create MFA settings

Request body (JSON):
- `mfa` (boolean, optional)
- `mfaRememberBrowser` (boolean, optional)

Responses: `200` MFA settings, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/mfa`

Update MFA settings

Request body (JSON):
- `mfa` (boolean, optional)
- `mfaRememberBrowser` (boolean, optional)

Responses: `200` MFA settings, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/peers`

List all Peers

Parameters:
- `has_aidr_graph` (query, optional): When true, only peers that have at least one AIDR graph run are returned

Responses: `200` A JSON Array of Peers, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/peers-stream`

Stream all Peers

Parameters:
- `has_aidr_graph` (query, optional): When true, only peers that have at least one AIDR graph run are returned

Responses: `200` text/event-stream of peer list frames, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/peers/bulk-delete`

Delete multiple Peers

Request body (JSON):
- `peer_ids` (array of string, **required**): List of peer IDs to delete (1 to 1000)

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/peers/sync`

Trigger a network map sync for Peers

Request body (JSON):
- `peer_ids` (array of string, **required**): Peer IDs; must not be empty

Responses: `200` Sync counters, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/peers/{peerId}`

Retrieve a Peer

Parameters:
- `peerId` (path, required): The unique identifier of a peer

Responses: `200` A Peer object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/peers/{peerId}`

Update a Peer

Parameters:
- `peerId` (path, required): The unique identifier of a peer

Request body (JSON):
- `name` (string, **required**) — e.g. `stage-host-1`
- `ssh_enabled` (boolean, **required**) — e.g. `True`
- `login_expiration_enabled` (boolean, **required**) — e.g. `False`
- `inactivity_expiration_enabled` (boolean, **required**) — e.g. `False`
- `approval_required` (boolean, optional): (Cloud only) Indicates whether peer needs approval — e.g. `True`

Responses: `200` A Peer object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/peers/{peerId}`

Delete a Peer

Parameters:
- `peerId` (path, required): The unique identifier of a peer

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/peers/{peerId}/aidr-snapshot`

Retrieve a peer's AIDR snapshot

Parameters:
- `peerId` (path, required)
- `run_id` (query, optional): Graph run ID; defaults to the latest run

Responses: `200` Snapshot metadata, runs, graph and events, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/peers/{peerId}/aidr-snapshot/events`

List a peer's AIDR events

Parameters:
- `peerId` (path, required)
- `run_id` (query, optional): Graph run ID; defaults to the latest run
- `edge_kind` (query, optional)
- `activity_code` (query, optional)
- `severity` (query, optional)
- `limit` (query, optional)
- `cursor` (query, optional): ID of the last event of the previous page

Responses: `200` Events page, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/peers/{peerId}/aidr-snapshot/replay`

Replay rules against a peer's AIDR snapshot

Parameters:
- `peerId` (path, required)

Request body (JSON):
- `run_id` (string, optional): Graph run to replay against; empty means the latest run
- `rules_yaml` (string, **required**): YAML rules to evaluate (max 512 KB body)

Responses: `200` Replay result, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/peers/{peerId}/aidr-snapshot/search`

Search a peer's AIDR events

Parameters:
- `peerId` (path, required)
- `q` (query, required)
- `run_id` (query, optional)
- `limit` (query, optional)
- `offset` (query, optional)

Responses: `200` Search results, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/policies`

List all Policies

Responses: `200` A JSON Array of Policies, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/policies`

Create a Policy

Request body (JSON):
- `id` (string, optional): Policy ID — e.g. `ch8i4ug6lnn4g9hqv7mg`
- `name` (string, **required**): Policy name identifier — e.g. `ch8i4ug6lnn4g9hqv7mg`
- `description` (string, **required**): Policy friendly description — e.g. `This is a default policy that allows connections between all the resources`
- `enabled` (boolean, **required**): Policy status — e.g. `True`
- `any_check_must_pass` (boolean, **required**): Determines posture check evaluation logic. If false (default), all posture checks must pass. If true, at least one posture check set must pass. — e.g. `False`
- `source_posture_checks` (array of string, optional): Posture checks ID's applied to policy source groups
- `rules` (array of ?, **required**): Policy rule object for policy UI editor

Responses: `200` A Policy Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/policies/{policyId}`

Retrieve a Policy

Parameters:
- `policyId` (path, required): The unique identifier of a policy

Responses: `200` A Policy object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/policies/{policyId}`

Update a Policy

Parameters:
- `policyId` (path, required): The unique identifier of a policy

Request body (JSON):
- `id` (string, optional): Policy ID — e.g. `ch8i4ug6lnn4g9hqv7mg`
- `name` (string, **required**): Policy name identifier — e.g. `ch8i4ug6lnn4g9hqv7mg`
- `description` (string, **required**): Policy friendly description — e.g. `This is a default policy that allows connections between all the resources`
- `enabled` (boolean, **required**): Policy status — e.g. `True`
- `any_check_must_pass` (boolean, **required**): Determines posture check evaluation logic. If false (default), all posture checks must pass. If true, at least one posture check set must pass. — e.g. `False`
- `source_posture_checks` (array of string, optional): Posture checks ID's applied to policy source groups
- `rules` (array of ?, **required**): Policy rule object for policy UI editor

Responses: `200` A Policy object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/policies/{policyId}`

Delete a Policy

Parameters:
- `policyId` (path, required): The unique identifier of a policy

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/posture-checks`

List all Posture Checks

Responses: `200` A JSON Array of posture checks, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/posture-checks`

Create a Posture Check

Request body (JSON):
- `name` (string, **required**): Posture check name identifier — e.g. `Default`
- `description` (string, **required**): Posture check friendly description — e.g. `This checks if the peer is running required Netzilo's version`
- `checks` (object, **required**): List of objects that perform the actual checks
  - `nb_version_check` (?, optional)
  - `os_version_check` (?, optional)
  - `geo_location_check` (?, optional)
  - `date_time_checks` (?, optional)
  - `peer_network_range_check` (?, optional)
  - `process_check` (?, optional)
  - `netzilo_check` (?, optional)

Responses: `200` A posture check Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/posture-checks/{postureCheckId}`

Retrieve a Posture Check

Parameters:
- `postureCheckId` (path, required): The unique identifier of a posture check

Responses: `200` A posture check object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/posture-checks/{postureCheckId}`

Update a Posture Check

Parameters:
- `postureCheckId` (path, required): The unique identifier of a posture check

Request body (JSON):
- `name` (string, **required**): Posture check name identifier — e.g. `Default`
- `description` (string, **required**): Posture check friendly description — e.g. `This checks if the peer is running required Netzilo's version`
- `checks` (object, **required**): List of objects that perform the actual checks
  - `nb_version_check` (?, optional)
  - `os_version_check` (?, optional)
  - `geo_location_check` (?, optional)
  - `date_time_checks` (?, optional)
  - `peer_network_range_check` (?, optional)
  - `process_check` (?, optional)
  - `netzilo_check` (?, optional)

Responses: `200` A posture check object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/posture-checks/{postureCheckId}`

Delete a Posture Check

Parameters:
- `postureCheckId` (path, required): The unique identifier of a posture check

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/profiles`

List all Profiles

Parameters:
- `expand` (query, optional): When true, returns the caller's own profiles with variables substituted

Responses: `200` A JSON array of Profiles, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/profiles`

Create a Profile

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `os` (array of string, **required**)
- `enabled` (boolean, **required**)
- `groups` (array of string, **required**)
- `components` (object, **required**)
  - `netzilo_workspace` (?, optional)
  - `disposable_browser` (string, optional)
  - `browser_extension` (array of ?, optional)
  - `extension_bookmarks` (array of ?, optional)
  - `enterprise_browser` (?, optional)

Responses: `200` A Profile Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/profiles/{profileId}`

Update a Profile

Parameters:
- `profileId` (path, required): The unique identifier of a profile

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `os` (array of string, **required**)
- `enabled` (boolean, **required**)
- `groups` (array of string, **required**)
- `components` (object, **required**)
  - `netzilo_workspace` (?, optional)
  - `disposable_browser` (string, optional)
  - `browser_extension` (array of ?, optional)
  - `extension_bookmarks` (array of ?, optional)
  - `enterprise_browser` (?, optional)

Responses: `200` A Profile object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/profiles/{profileId}`

Delete a Profile

Parameters:
- `profileId` (path, required): The unique identifier of a profile

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/register`

Register a new tenant

Request body (JSON):
- `company_name` (string, **required**)
- `subdomain` (string, **required**)
- `first_name` (string, **required**)
- `last_name` (string, **required**)
- `email` (string, **required**)
- `password` (string, **required**)
- `accept_terms_of_service` (boolean, **required**)
- `recaptcha_token` (string, **required**)

Responses: `200` The new organization ID, `400` Bad Request, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/reports`

List all Reports

Responses: `200` A JSON array of Reports, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/reports`

Create a Report

Request body (JSON):
- `from` (string, **required**): Start of the reporting window, YYYY-MM-DD — e.g. `2026-09-01`
- `to` (string, **required**): End of the reporting window (inclusive), YYYY-MM-DD, not before from — e.g. `2026-09-21`
- `groups` (array of string, optional): Restrict the report to these group IDs (empty = whole account)
- `report_type` (string (user_activity | authentication | ai_activity), optional): user_activity (default), authentication, or ai_activity

Responses: `200` The generated Report, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/reports/{reportId}`

Retrieve a Report

Parameters:
- `reportId` (path, required)

Responses: `200` A Report object, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/reports/{reportId}`

Delete a Report

Parameters:
- `reportId` (path, required)

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/routes`

List all Routes

Responses: `200` A JSON Array of Routes, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/routes`

Create a Route

Request body (JSON):
- `description` (string, **required**): Route description — e.g. `My first route`
- `network_id` (string, **required**): Route network identifier, to group HA routes — e.g. `Route 1`
- `enabled` (boolean, **required**): Route status — e.g. `True`
- `peer` (string, optional): Peer Identifier associated with route. This property can not be set together with `peer_groups` — e.g. `chacbco6lnnbn6cg5s91`
- `peer_groups` (array of string, optional): Peers Group Identifier associated with route. This property can not be set together with `peer`
- `network` (string, optional): Network range in CIDR format, Conflicts with domains — e.g. `10.64.0.0/24`
- `domains` (array of string, optional): Domain list to be dynamically resolved. Max of 32 domains can be added per route configuration. Conflicts with network
- `metric` (integer, **required**): Route metric number. Lowest number has higher priority — e.g. `9999`
- `masquerade` (boolean, **required**): Indicate if peer should masquerade traffic to this route's prefix — e.g. `True`
- `groups` (array of string, **required**): Group IDs containing routing peers
- `keep_route` (boolean, **required**): Indicate if the route should be kept after a domain doesn't resolve that IP anymore — e.g. `True`
- `access_control_groups` (array of string, optional): Access control group identifier associated with route.

Responses: `200` A Route Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/routes/{routeId}`

Retrieve a Route

Parameters:
- `routeId` (path, required): The unique identifier of a route

Responses: `200` A Route object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/routes/{routeId}`

Update a Route

Parameters:
- `routeId` (path, required): The unique identifier of a route

Request body (JSON):
- `description` (string, **required**): Route description — e.g. `My first route`
- `network_id` (string, **required**): Route network identifier, to group HA routes — e.g. `Route 1`
- `enabled` (boolean, **required**): Route status — e.g. `True`
- `peer` (string, optional): Peer Identifier associated with route. This property can not be set together with `peer_groups` — e.g. `chacbco6lnnbn6cg5s91`
- `peer_groups` (array of string, optional): Peers Group Identifier associated with route. This property can not be set together with `peer`
- `network` (string, optional): Network range in CIDR format, Conflicts with domains — e.g. `10.64.0.0/24`
- `domains` (array of string, optional): Domain list to be dynamically resolved. Max of 32 domains can be added per route configuration. Conflicts with network
- `metric` (integer, **required**): Route metric number. Lowest number has higher priority — e.g. `9999`
- `masquerade` (boolean, **required**): Indicate if peer should masquerade traffic to this route's prefix — e.g. `True`
- `groups` (array of string, **required**): Group IDs containing routing peers
- `keep_route` (boolean, **required**): Indicate if the route should be kept after a domain doesn't resolve that IP anymore — e.g. `True`
- `access_control_groups` (array of string, optional): Access control group identifier associated with route.

Responses: `200` A Route object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/routes/{routeId}`

Delete a Route

Parameters:
- `routeId` (path, required): The unique identifier of a route

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/setup-keys`

List all Setup Keys

Responses: `200` A JSON Array of Setup keys, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/setup-keys`

Create a Setup Key

Request body (JSON):
- `name` (string, **required**): Setup Key name — e.g. `Default key`
- `type` (string (one-off | reusable), **required**): Setup key type, one-off for single time usage and reusable — e.g. `reusable`
- `expires_in` (integer, **required**): Expiration time in seconds. Must be between 1 day (86400) and 365 days when expirable is true (the default); ignored when expirable is false. Only used on create. — e.g. `86400`
- `revoked` (boolean, **required**): Setup key revocation status — e.g. `False`
- `auto_groups` (array of string, **required**): List of group IDs to auto-assign to peers registered with this key
- `usage_limit` (integer, **required**): A number of times this key can be used. The value of 0 indicates the unlimited usage. — e.g. `0`
- `ephemeral` (boolean, optional): Indicate that the peer will be ephemeral or not — e.g. `True`
- `expirable` (boolean, optional): Indicates whether the key has an expiration date. Defaults to true. When false, expires_in is ignored and the key never expires. — e.g. `True`

Responses: `200` A Setup Keys Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/setup-keys/{keyId}`

Retrieve a Setup Key

Parameters:
- `keyId` (path, required): The unique identifier of a setup key

Responses: `200` A Setup Key object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/setup-keys/{keyId}`

Update a Setup Key

Parameters:
- `keyId` (path, required): The unique identifier of a setup key

Request body (JSON):
- `name` (string, **required**): Setup Key name — e.g. `Default key`
- `type` (string (one-off | reusable), **required**): Setup key type, one-off for single time usage and reusable — e.g. `reusable`
- `expires_in` (integer, **required**): Expiration time in seconds. Must be between 1 day (86400) and 365 days when expirable is true (the default); ignored when expirable is false. Only used on create. — e.g. `86400`
- `revoked` (boolean, **required**): Setup key revocation status — e.g. `False`
- `auto_groups` (array of string, **required**): List of group IDs to auto-assign to peers registered with this key
- `usage_limit` (integer, **required**): A number of times this key can be used. The value of 0 indicates the unlimited usage. — e.g. `0`
- `ephemeral` (boolean, optional): Indicate that the peer will be ephemeral or not — e.g. `True`
- `expirable` (boolean, optional): Indicates whether the key has an expiration date. Defaults to true. When false, expires_in is ignored and the key never expires. — e.g. `True`

Responses: `200` A Setup Key object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/setup-keys/{keyId}`

Delete a Setup Key

Parameters:
- `keyId` (path, required): The unique identifier of a setup key

Responses: `200` Delete status, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/smartsearch`

Check smart search availability

Responses: `200` Smart search is available, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `428` Smart search is not available, `500` Internal Server Error

## `POST /api/smartsearch`

Run a smart search

Request body (JSON):
- `message` (string, **required**)
- `provider` (string, optional): openai or anthropic; defaults to the first configured provider
- `model` (string, optional)
- `top_k` (integer, optional)

Responses: `200` Search result, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `428` Precondition required, `500` Internal Server Error

## `GET /api/stats`

Retrieve dashboard statistics

Responses: `200` Statistics, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/stripe`

Stripe webhook

Request body (JSON):
- (object, see live spec)

Responses: `200` Event processed, `400` Bad Request, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/summary`

Retrieve activity summary

Responses: `200` Summary of top users, top groups and total events, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/support/openapi.yml`

Retrieve this API description

Responses: `200` The OpenAPI document, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/support/sessions`

List support sessions

Parameters:
- `limit` (query, optional): Maximum number of sessions; 0 or omitted means no limit

Responses: `200` A JSON array of sessions, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/support/sessions`

Create a support session

Responses: `200` The created session, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/support/sessions/{sessionId}`

Retrieve a support session with its messages

Parameters:
- `sessionId` (path, required)

Responses: `200` Session detail, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/support/sessions/{sessionId}`

Delete a support session

Parameters:
- `sessionId` (path, required)

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/support/sessions/{sessionId}/messages`

Send a message to the support agent

Parameters:
- `sessionId` (path, required)

Request body (JSON):
- `text` (string, **required**): Non-blank, at most 32000 characters

Responses: `200` text/event-stream of agent events, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `412` Precondition failed, `422` Validation failed, `500` Internal Server Error

## `GET /api/templates`

List all Templates

Responses: `200` A JSON array of Templates, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/templates/{category}`

List Templates by category

Parameters:
- `category` (path, required): The category of a template

Responses: `200` A JSON array of Templates, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/tenant`

Retrieve the Tenant

Responses: `200` A Tenant object, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/tenant`

Update the Tenant

Request body (JSON):
- `company_name` (string, **required**)
- `company_website` (string, **required**): Tenant domain name
- `company_size` (string, **required**)
- `heard_from` (string, **required**)

Responses: `200` The updated Tenant object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/tenant/logo`

Retrieve the company logo

Responses: `200` The logo image, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/tenant/logo`

Upload the company logo

Responses: `200` Upload result, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/tenant/logo`

Delete the company logo

Responses: `200` Delete status, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/tenant/logo/info`

Retrieve company logo metadata

Responses: `200` Logo metadata, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/tenant/subscription`

Change the subscription plan

Request body (JSON):
- `subscription` (string (Free | Professional | Enterprise), **required**): The subscription level of a tenant

Responses: `200` Tenant object, Stripe invoice preview, or {"URL": checkout URL} depending on the current subscription state, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/tenant/subscription/confirm`

Confirm a subscription change

Request body (JSON):
- `proration_date` (integer, **required**): Unix timestamp returned by the invoice preview
- `subscription` (string (Professional | Enterprise), **required**): The subscription level of a tenant

Responses: `200` The updated Tenant object, `400` Bad Request, `401` Requires authentication, `412` Precondition failed, `422` Validation failed, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

## `POST /api/tokens/revoke`

Revoke a JWT

Request body (JSON):
- `token` (string, **required**): JWT access or refresh token to revoke

Responses: `200` Revoked, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/users`

List all Users

Parameters:
- `service_user` (query, optional): Filters users and returns either regular users or service users

Responses: `200` A JSON array of Users, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/users`

Create a User

Request body (JSON):
- `email` (string, optional): User's Email to send invite to — e.g. `demo@netzilo.com`
- `name` (string, optional): User's full name — e.g. `Tom Schulz`
- `role` (string, **required**): User's Netzilo account role — e.g. `admin`
- `auto_groups` (array of string, **required**): Group IDs to auto-assign to peers registered by this user
- `is_service_user` (boolean, **required**): Is true if this user is a service user — e.g. `False`
- `password` (string, optional): User's password — e.g. `password`
- `password_change_required` (boolean, optional): Indicates whether the user is required to change their password on first login — e.g. `True`

Responses: `200` A User object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `409` Conflict, `422` Validation failed, `500` Internal Server Error

## `GET /api/users/{userId}`

Retrieve a User

Parameters:
- `userId` (path, required): The unique identifier of a user

Responses: `200` A User object, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/users/{userId}`

Update a User

Parameters:
- `userId` (path, required): The unique identifier of a user

Request body (JSON):
- `role` (string, **required**): User's Netzilo account role — e.g. `admin`
- `auto_groups` (array of string, **required**): Group IDs to auto-assign to peers registered by this user
- `is_blocked` (boolean, **required**): If set to true then user is blocked and can't use the system — e.g. `False`
- `update_peer_groups` (boolean, optional): Deprecated. Ignored by the server. — e.g. `False`

Responses: `200` A User object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/users/{userId}`

Delete a User

Parameters:
- `userId` (path, required): The unique identifier of a user

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/users/{userId}/auth-factors`

Check a user's auth factors

Parameters:
- `userId` (path, required)

Responses: `200` Whether the user has auth factors, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/users/{userId}/auth-factors`

Reset a user's auth factors

Parameters:
- `userId` (path, required)

Responses: `200` Reset status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/users/{userId}/invite`

Resend user invitation

Parameters:
- `userId` (path, required): The unique identifier of a user

Responses: `200` Invite status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/users/{userId}/name`

Update a user's name

Parameters:
- `userId` (path, required)

Request body (JSON):
- `name` (string, **required**)

Responses: `200` Update status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/users/{userId}/password`

Update a user's password

Parameters:
- `userId` (path, required)

Request body (JSON):
- `password` (string, **required**)

Responses: `200` Update status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/users/{userId}/tokens`

List all Tokens

Parameters:
- `userId` (path, required): The unique identifier of a user

Responses: `200` A JSON Array of PersonalAccessTokens, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/users/{userId}/tokens`

Create a Token

Parameters:
- `userId` (path, required): The unique identifier of a user

Request body (JSON):
- `name` (string, **required**): Name of the token — e.g. `My first token`
- `expires_in` (integer, **required**): Expiration in days — e.g. `30`

Responses: `200` The token in plain text, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/users/{userId}/tokens/{tokenId}`

Retrieve a Token

Parameters:
- `userId` (path, required): The unique identifier of a user
- `tokenId` (path, required): The unique identifier of a token

Responses: `200` A PersonalAccessTokens Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/users/{userId}/tokens/{tokenId}`

Delete a Token

Parameters:
- `userId` (path, required): The unique identifier of a user
- `tokenId` (path, required): The unique identifier of a token

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/verify-recaptcha`

Verify a reCAPTCHA token

Request body (JSON):
- `recaptcha_token` (string, **required**)

Responses: `200` Verification result, `400` Bad Request, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

