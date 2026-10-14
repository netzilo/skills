---
id: '33'
title: API request schemas
requires:
- api
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 102670
sections:
- id: get-api-accounts
  title: '`GET /api/accounts`'
  chars: 233
- id: put-api-accounts-accountid
  title: '`PUT /api/accounts/{accountId}`'
  chars: 3355
- id: delete-api-accounts-accountid
  title: '`DELETE /api/accounts/{accountId}`'
  chars: 331
- id: get-api-ai-gateway-mcp
  title: '`GET /api/ai-gateway/mcp`'
  chars: 204
- id: get-api-ai-gateway-mcp-credentials
  title: '`GET /api/ai-gateway/mcp-credentials`'
  chars: 202
- id: get-api-ai-gateway-providers
  title: '`GET /api/ai-gateway/providers`'
  chars: 194
- id: post-api-ai-gateway-usage
  title: '`POST /api/ai-gateway/usage`'
  chars: 2300
- id: get-api-ai-capabilities
  title: '`GET /api/ai/capabilities`'
  chars: 186
- id: get-api-ai-models
  title: '`GET /api/ai/models`'
  chars: 316
- id: get-api-ai-protocols
  title: '`GET /api/ai/protocols`'
  chars: 175
- id: get-api-ai-providers
  title: '`GET /api/ai/providers`'
  chars: 171
- id: post-api-ai-providers
  title: '`POST /api/ai/providers`'
  chars: 1352
- id: post-api-ai-providers-verify
  title: '`POST /api/ai/providers/verify`'
  chars: 1380
- id: put-api-ai-providers-providerid
  title: '`PUT /api/ai/providers/{providerId}`'
  chars: 1455
- id: delete-api-ai-providers-providerid
  title: '`DELETE /api/ai/providers/{providerId}`'
  chars: 261
- id: post-api-ai-providers-providerid-verify
  title: '`POST /api/ai/providers/{providerId}/verify`'
  chars: 317
- id: post-api-ai-scanprompt
  title: '`POST /api/ai/scanprompt`'
  chars: 653
- id: post-api-ai-systemone
  title: '`POST /api/ai/systemone`'
  chars: 458
- id: post-api-aidr-browser-observations
  title: '`POST /api/aidr/browser/observations`'
  chars: 1072
- id: get-api-aidr-detections
  title: '`GET /api/aidr/detections`'
  chars: 661
- id: get-api-aidr-graph
  title: '`GET /api/aidr/graph`'
  chars: 638
- id: get-api-aidr-observations
  title: '`GET /api/aidr/observations`'
  chars: 785
- id: post-api-aidr-replay
  title: '`POST /api/aidr/replay`'
  chars: 664
- id: get-api-aidr-search
  title: '`GET /api/aidr/search`'
  chars: 696
- id: get-api-aidr-session
  title: '`GET /api/aidr/session`'
  chars: 305
- id: get-api-aidr-sessions
  title: '`GET /api/aidr/sessions`'
  chars: 940
- id: get-api-aidr-sources
  title: '`GET /api/aidr/sources`'
  chars: 150
- id: post-api-aidr-sources-source-observations
  title: '`POST /api/aidr/sources/{source}/observations`'
  chars: 1077
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
- id: get-api-dns-nameservers-nsgroupid
  title: '`GET /api/dns/nameservers/{nsgroupId}`'
  chars: 352
- id: put-api-dns-nameservers-nsgroupid
  title: '`PUT /api/dns/nameservers/{nsgroupId}`'
  chars: 1466
- id: delete-api-dns-nameservers-nsgroupid
  title: '`DELETE /api/dns/nameservers/{nsgroupId}`'
  chars: 346
- id: get-api-dns-settings
  title: '`GET /api/dns/settings`'
  chars: 245
- id: put-api-dns-settings
  title: '`PUT /api/dns/settings`'
  chars: 369
- id: post-api-edge-events
  title: '`POST /api/edge/events`'
  chars: 818
- id: get-api-edge-filters
  title: '`GET /api/edge/filters`'
  chars: 485
- id: post-api-edge-filters
  title: '`POST /api/edge/filters`'
  chars: 2090
- id: get-api-edge-filters-effective
  title: '`GET /api/edge/filters/effective`'
  chars: 572
- id: get-api-edge-filters-filterid
  title: '`GET /api/edge/filters/{filterId}`'
  chars: 263
- id: put-api-edge-filters-filterid
  title: '`PUT /api/edge/filters/{filterId}`'
  chars: 2143
- id: delete-api-edge-filters-filterid
  title: '`DELETE /api/edge/filters/{filterId}`'
  chars: 267
- id: get-api-edge-filters-filterid-expanded
  title: '`GET /api/edge/filters/{filterId}/expanded`'
  chars: 281
- id: get-api-edge-guardrails
  title: '`GET /api/edge/guardrails`'
  chars: 225
- id: post-api-edge-guardrails
  title: '`POST /api/edge/guardrails`'
  chars: 621
- id: get-api-edge-guardrails-generate
  title: '`GET /api/edge/guardrails/generate`'
  chars: 284
- id: post-api-edge-guardrails-generate
  title: '`POST /api/edge/guardrails/generate`'
  chars: 401
- id: get-api-edge-guardrails-guardrailid
  title: '`GET /api/edge/guardrails/{guardrailId}`'
  chars: 278
- id: put-api-edge-guardrails-guardrailid
  title: '`PUT /api/edge/guardrails/{guardrailId}`'
  chars: 680
- id: delete-api-edge-guardrails-guardrailid
  title: '`DELETE /api/edge/guardrails/{guardrailId}`'
  chars: 279
- id: get-api-edge-limits
  title: '`GET /api/edge/limits`'
  chars: 162
- id: post-api-edge-limits
  title: '`POST /api/edge/limits`'
  chars: 805
- id: get-api-edge-limits-limitid
  title: '`GET /api/edge/limits/{limitId}`'
  chars: 247
- id: put-api-edge-limits-limitid
  title: '`PUT /api/edge/limits/{limitId}`'
  chars: 882
- id: delete-api-edge-limits-limitid
  title: '`DELETE /api/edge/limits/{limitId}`'
  chars: 272
- id: get-api-edge-mcp-catalog
  title: '`GET /api/edge/mcp-catalog`'
  chars: 132
- id: get-api-edge-mcp-servers
  title: '`GET /api/edge/mcp-servers`'
  chars: 177
- id: post-api-edge-mcp-servers
  title: '`POST /api/edge/mcp-servers`'
  chars: 1766
- id: get-api-edge-mcp-servers-serverid
  title: '`GET /api/edge/mcp-servers/{serverId}`'
  chars: 262
- id: put-api-edge-mcp-servers-serverid
  title: '`PUT /api/edge/mcp-servers/{serverId}`'
  chars: 1845
- id: delete-api-edge-mcp-servers-serverid
  title: '`DELETE /api/edge/mcp-servers/{serverId}`'
  chars: 283
- id: get-api-edge-providers
  title: '`GET /api/edge/providers`'
  chars: 171
- id: post-api-edge-providers
  title: '`POST /api/edge/providers`'
  chars: 1292
- id: post-api-edge-providers-discover
  title: '`POST /api/edge/providers/discover`'
  chars: 1126
- id: get-api-edge-providers-providerid
  title: '`GET /api/edge/providers/{providerId}`'
  chars: 262
- id: put-api-edge-providers-providerid
  title: '`PUT /api/edge/providers/{providerId}`'
  chars: 1375
- id: delete-api-edge-providers-providerid
  title: '`DELETE /api/edge/providers/{providerId}`'
  chars: 284
- id: get-api-edge-virtual-mcps
  title: '`GET /api/edge/virtual-mcps`'
  chars: 180
- id: post-api-edge-virtual-mcps
  title: '`POST /api/edge/virtual-mcps`'
  chars: 560
- id: get-api-edge-virtual-mcps-vmcpid
  title: '`GET /api/edge/virtual-mcps/{vmcpId}`'
  chars: 261
- id: put-api-edge-virtual-mcps-vmcpid
  title: '`PUT /api/edge/virtual-mcps/{vmcpId}`'
  chars: 635
- id: delete-api-edge-virtual-mcps-vmcpid
  title: '`DELETE /api/edge/virtual-mcps/{vmcpId}`'
  chars: 281
- id: get-api-event-streaming
  title: '`GET /api/event-streaming`'
  chars: 247
- id: post-api-event-streaming
  title: '`POST /api/event-streaming`'
  chars: 371
- id: get-api-event-streaming-getlogvideos
  title: '`GET /api/event-streaming/getLogVideos`'
  chars: 306
- id: post-api-event-streaming-sign-urls
  title: '`POST /api/event-streaming/sign-urls`'
  chars: 313
- id: delete-api-event-streaming-streamingid
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
- id: post-api-groups-groupid-peers-peerid
  title: '`POST /api/groups/{groupId}/peers/{peerId}`'
  chars: 398
- id: delete-api-groups-groupid-peers-peerid
  title: '`DELETE /api/groups/{groupId}/peers/{peerId}`'
  chars: 405
- id: get-api-integrations
  title: '`GET /api/integrations`'
  chars: 226
- id: post-api-integrations
  title: '`POST /api/integrations`'
  chars: 484
- id: put-api-integrations-integrationid
  title: '`PUT /api/integrations/{integrationId}`'
  chars: 547
- id: delete-api-integrations-integrationid
  title: '`DELETE /api/integrations/{integrationId}`'
  chars: 278
- id: get-api-locations-countries
  title: '`GET /api/locations/countries`'
  chars: 269
- id: get-api-locations-countries-country-cities
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
- id: get-api-posture-checks-posturecheckid
  title: '`GET /api/posture-checks/{postureCheckId}`'
  chars: 352
- id: put-api-posture-checks-posturecheckid
  title: '`PUT /api/posture-checks/{postureCheckId}`'
  chars: 943
- id: delete-api-posture-checks-posturecheckid
  title: '`DELETE /api/posture-checks/{postureCheckId}`'
  chars: 349
- id: get-api-profiles
  title: '`GET /api/profiles`'
  chars: 348
- id: post-api-profiles
  title: '`POST /api/profiles`'
  chars: 723
- id: post-api-profiles-pac
  title: '`POST /api/profiles/pac`'
  chars: 637
- id: put-api-profiles-profileid
  title: '`PUT /api/profiles/{profileId}`'
  chars: 814
- id: delete-api-profiles-profileid
  title: '`DELETE /api/profiles/{profileId}`'
  chars: 302
- id: get-api-published-apps
  title: '`GET /api/published-apps`'
  chars: 193
- id: post-api-published-apps
  title: '`POST /api/published-apps`'
  chars: 1400
- id: get-api-published-apps-check
  title: '`GET /api/published-apps/check`'
  chars: 250
- id: get-api-published-apps-domains-check
  title: '`GET /api/published-apps/domains/check`'
  chars: 277
- id: get-api-published-apps-exists
  title: '`GET /api/published-apps/exists`'
  chars: 141
- id: put-api-published-apps-appid
  title: '`PUT /api/published-apps/{appId}`'
  chars: 1481
- id: delete-api-published-apps-appid
  title: '`DELETE /api/published-apps/{appId}`'
  chars: 240
- id: post-api-register
  title: '`POST /api/register`'
  chars: 527
- id: get-api-reports
  title: '`GET /api/reports`'
  chars: 211
- id: post-api-reports
  title: '`POST /api/reports`'
  chars: 726
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
- id: get-api-support-audit-sessions-sessionid
  title: '`GET /api/support/audit/sessions/{sessionId}`'
  chars: 307
- id: get-api-support-devices-peerid
  title: '`GET /api/support/devices/{peerId}`'
  chars: 282
- id: post-api-support-devices-peerid-invoke
  title: '`POST /api/support/devices/{peerId}/invoke`'
  chars: 700
- id: get-api-support-devices-peerid-tools
  title: '`GET /api/support/devices/{peerId}/tools`'
  chars: 395
- id: get-api-support-openapi-yml
  title: '`GET /api/support/openapi.yml`'
  chars: 233
- id: get-api-support-sessions
  title: '`GET /api/support/sessions`'
  chars: 324
- id: post-api-support-sessions
  title: '`POST /api/support/sessions`'
  chars: 225
- id: get-api-support-sessions-sessionid
  title: '`GET /api/support/sessions/{sessionId}`'
  chars: 295
- id: delete-api-support-sessions-sessionid
  title: '`DELETE /api/support/sessions/{sessionId}`'
  chars: 282
- id: post-api-support-sessions-sessionid-messages
  title: '`POST /api/support/sessions/{sessionId}/messages`'
  chars: 735
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
- id: post-api-tenant-subscription-confirm
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
- id: get-api-users-current-ai-access
  title: '`GET /api/users/current/ai-access`'
  chars: 192
- id: get-api-users-current-mcp-connections
  title: '`GET /api/users/current/mcp-connections`'
  chars: 161
- id: post-api-users-current-mcp-connections-complete
  title: '`POST /api/users/current/mcp-connections/complete`'
  chars: 400
- id: delete-api-users-current-mcp-connections
  title: '`DELETE /api/users/current/mcp-connections/{serverId}`'
  chars: 234
- id: put-api-users-current-mcp-connections-serverid
  title: '`PUT /api/users/current/mcp-connections/{serverId}/headers`'
  chars: 336
- id: post-api-users-current-mcp-connections-serverid
  title: '`POST /api/users/current/mcp-connections/{serverId}/oauth`'
  chars: 322
- id: get-api-users-current-pac
  title: '`GET /api/users/current/pac`'
  chars: 418
- id: get-api-users-current-published-apps
  title: '`GET /api/users/current/published-apps`'
  chars: 179
- id: post-api-users-current-published-apps-access
  title: '`POST /api/users/current/published-apps/access`'
  chars: 2414
- id: get-api-users-current-routing
  title: '`GET /api/users/current/routing`'
  chars: 214
- id: get-api-users-userid
  title: '`GET /api/users/{userId}`'
  chars: 281
- id: put-api-users-userid
  title: '`PUT /api/users/{userId}`'
  chars: 713
- id: delete-api-users-userid
  title: '`DELETE /api/users/{userId}`'
  chars: 306
- id: get-api-users-userid-auth-factors
  title: '`GET /api/users/{userId}/auth-factors`'
  chars: 293
- id: delete-api-users-userid-auth-factors
  title: '`DELETE /api/users/{userId}/auth-factors`'
  chars: 280
- id: get-api-users-userid-gateway-sessions
  title: '`GET /api/users/{userId}/gateway-sessions`'
  chars: 302
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
  chars: 631
- id: get-api-users-userid-tokens-tokenid
  title: '`GET /api/users/{userId}/tokens/{tokenId}`'
  chars: 397
- id: delete-api-users-userid-tokens-tokenid
  title: '`DELETE /api/users/{userId}/tokens/{tokenId}`'
  chars: 387
- id: post-api-verify-recaptcha
  title: '`POST /api/verify-recaptcha`'
  chars: 261
---
# API request schemas

Generated from Netzilo Server's OpenAPI description on 2026-10-14 by `scripts/gen-api-schemas.py`.

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
  - `user_ai_assistant_enabled` (boolean, optional): Lets regular users open the AI assistant. Admins always may. A regular user also needs to belong to one of user_ai_assistant_groups. — e.g. `False`
  - `user_ai_assistant_groups` (array of string, optional): Group IDs whose members may use the AI assistant when user_ai_assistant_enabled is set. With the switch on and no groups listed, no regular user may.
  - `clientless_access_enabled` (boolean, optional): Lets users reach internal resources from a browser with only the Netzilo extension, through a Netzilo gateway (Settings → Permissions → Allow clientless access). Off, management computes no PAC for anyone; a profile's custom PAC is served regardless. — e.g. `False`
  - `clientless_proxy_address` (string, optional): The gateway proxy address (host:port) browsers are pointed at. Empty means the default, the management server's host on port 8443; reads return the effective value. — e.g. `srv.example.com:8443`
  - `published_apps_enabled` (boolean, optional): Lets administrators publish private web applications at addresses of their own, opened in any browser through a gateway's reverse-proxy mode. Off, no address of this account is published. — e.g. `False`
  - `published_app_domains` (array of ?, optional): The base domains the account publishes under, each with the reverse-proxy addresses its wildcard record points at. Used to suggest addresses and to check that an address resolves to the gateway.
  - `extra` (?, optional)

Responses: `200` An Account object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/accounts/{accountId}`

Delete an Account

Parameters:
- `accountId` (path, required): The unique identifier of an account

Responses: `200` Delete account status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/ai-gateway/mcp`

What an AI gateway pulls for MCP (credentials in clear, ETag)

Responses: `200` Servers and virtual MCPs, `304` Not modified, `401` Requires authentication, `403` Forbidden

## `GET /api/ai-gateway/mcp-credentials`

What an AI gateway pulls for per-user MCP credentials (ETag)

Responses: `200` Credentials, `304` Not modified, `401` Requires authentication, `403` Forbidden

## `GET /api/ai-gateway/providers`

Providers for an AI gateway

Responses: `200` The providers, `304` Not modified, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/ai-gateway/usage`

Ingest AI usage from a gateway

Request body (JSON):
- `gateway` (string, optional)
- `llm` (array of object, optional)
  - `request_id` (string, optional)
  - `session_id` (string, optional)
  - `at` (string (date-time), optional)
  - `gateway` (string, optional)
  - `user_id` (string, optional)
  - `user_email` (string, optional)
  - `user_name` (string, optional)
  - `peer_id` (string, optional)
  - `path` (string, optional): bearer
  - `client_app` (string, optional): The caller's User-Agent
  - `request_type` (string, optional)
  - `provider` (string, optional)
  - `model_requested` (string, optional)
  - `model` (string, optional)
  - `stream` (boolean, optional)
  - `status` (string (ok | error | blocked | limited), optional)
  - `status_code` (integer, optional)
  - `error_kind` (string, optional)
  - `prompt_tokens` (integer, optional)
  - `completion_tokens` (integer, optional)
  - `total_tokens` (integer, optional)
  - `cached_tokens` (integer, optional)
  - `reasoning_tokens` (integer, optional)
  - `cost_input` (number, optional)
  - `cost_output` (number, optional)
  - `cost_additional` (number, optional)
  - `cost_total` (number, optional): USD
  - `latency_ms` (integer, optional)
  - `upstream_latency_ms` (integer, optional)
  - `tool_calls` (integer, optional): Tool calls the answer asked for
  - `tool_names` (array of string, optional)
- `mcp` (array of object, optional)
  - `request_id` (string, optional)
  - `call_id` (string, optional)
  - `llm_request_id` (string, optional)
  - `session_id` (string, optional)
  - `at` (string (date-time), optional)
  - `gateway` (string, optional)
  - `user_id` (string, optional)
  - `user_email` (string, optional)
  - `user_name` (string, optional)
  - `peer_id` (string, optional)
  - `client_app` (string, optional)
  - `server_id` (string, optional)
  - `server_name` (string, optional)
  - `slug` (string, optional)
  - `tool` (string, optional)
  - `status` (string (ok | error | blocked | limited | redacted), optional)
  - `latency_ms` (integer, optional)
  - `arg_bytes` (integer, optional)
  - `result_bytes` (integer, optional)

Responses: `200` How many rows were new, `401` Requires authentication, `403` Forbidden, `422` Validation failed, `500` Internal Server Error

## `GET /api/ai/capabilities`

Report which AI uses this account can serve

Responses: `200` Capability map, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/ai/models`

List the models approved for a use

Parameters:
- `use` (query, required): The feature the models must be approved for.

Responses: `200` Approved models, resolution order, default marked, `401` Requires authentication, `403` Forbidden, `422` Validation failed, `500` Internal Server Error

## `GET /api/ai/protocols`

Describe the AI provider vocabulary

Responses: `200` The vocabulary, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/ai/providers`

List AI providers

Responses: `200` A JSON array of AI providers, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/ai/providers`

Create an AI provider

Request body (JSON):
- `name` (string, **required**)
- `protocol` (string (anthropic-messages | openai-completions | typesafe-systemone), **required**): The wire protocol a provider's endpoint speaks. A "typesafe-systemone" provider is called only by AIDR rules and is approved for no use.
- `base_url` (string, optional)
- `api_key` (string, optional)
- `headers` (object, optional)
- `enabled` (boolean, **required**)
- `uses` (array of string (assistant | log-analysis | threat-analysis), optional)
- `priority` (integer, optional)
- `models` (array of object, optional)
  - `id` (string, **required**): Identifier sent to the provider on the wire. — e.g. `claude-sonnet-4-5`
  - `display_name` (string, optional)
  - `context_window` (integer, optional): Total token capacity, 0 or absent when unknown.
  - `max_output_tokens` (integer, optional)
  - `uses` (array of ?, optional): Overrides the provider's approval for this model. Omit to inherit the provider; send an empty array to approve the model for nothing.
  - `default_for` (array of ?, optional): Uses this model serves by default, at most one model per use per account.

Responses: `200` The created AI provider, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `422` Validation failed, `500` Internal Server Error

## `POST /api/ai/providers/verify`

Verify a draft AI provider without storing it

Request body (JSON):
- `id` (string, optional)
- `name` (string, **required**)
- `protocol` (string (anthropic-messages | openai-completions | typesafe-systemone), **required**): The wire protocol a provider's endpoint speaks. A "typesafe-systemone" provider is called only by AIDR rules and is approved for no use.
- `base_url` (string, optional)
- `api_key` (string, optional)
- `headers` (object, optional)
- `models` (array of object, optional)
  - `id` (string, **required**): Identifier sent to the provider on the wire. — e.g. `claude-sonnet-4-5`
  - `display_name` (string, optional)
  - `context_window` (integer, optional): Total token capacity, 0 or absent when unknown.
  - `max_output_tokens` (integer, optional)
  - `uses` (array of ?, optional): Overrides the provider's approval for this model. Omit to inherit the provider; send an empty array to approve the model for nothing.
  - `default_for` (array of ?, optional): Uses this model serves by default, at most one model per use per account.
- `probe_model` (string, optional): Model the liveness probe should call; defaults to the first available.

Responses: `200` What the verification learned, including a typed failure reason, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `PUT /api/ai/providers/{providerId}`

Update an AI provider

Parameters:
- `providerId` (path, required): The AI provider ID

Request body (JSON):
- `name` (string, **required**)
- `protocol` (string (anthropic-messages | openai-completions | typesafe-systemone), **required**): The wire protocol a provider's endpoint speaks. A "typesafe-systemone" provider is called only by AIDR rules and is approved for no use.
- `base_url` (string, optional)
- `api_key` (string, optional)
- `headers` (object, optional)
- `enabled` (boolean, **required**)
- `uses` (array of string (assistant | log-analysis | threat-analysis), optional)
- `priority` (integer, optional)
- `models` (array of object, optional)
  - `id` (string, **required**): Identifier sent to the provider on the wire. — e.g. `claude-sonnet-4-5`
  - `display_name` (string, optional)
  - `context_window` (integer, optional): Total token capacity, 0 or absent when unknown.
  - `max_output_tokens` (integer, optional)
  - `uses` (array of ?, optional): Overrides the provider's approval for this model. Omit to inherit the provider; send an empty array to approve the model for nothing.
  - `default_for` (array of ?, optional): Uses this model serves by default, at most one model per use per account.

Responses: `200` The updated AI provider, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/ai/providers/{providerId}`

Delete an AI provider

Parameters:
- `providerId` (path, required): The AI provider ID

Responses: `200` Deleted, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

## `POST /api/ai/providers/{providerId}/verify`

Verify a stored AI provider and record the outcome

Parameters:
- `providerId` (path, required): The AI provider ID

Responses: `200` What the verification learned, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

## `POST /api/ai/scanprompt`

Scan a prompt

Request body (JSON):
- `prompt` (string, **required**)
- `instruction` (string, optional): Optional AI rule instruction; empty means built-in jailbreak detection
- `model` (string, optional): Optional model an AI scan asks for, as `model-id`, `provider-name/model-id` or `provider-id/model-id`; empty means the model approved for Threat Analysis. A model the account cannot use answers `label` `error`.

Responses: `200` Scan result, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `412` Precondition failed, `422` Validation failed, `500` Internal Server Error

## `POST /api/ai/systemone`

Ask System One

Request body (JSON):
- `state` (?, **required**): Any JSON value the questions are about
- `questions` (object, **required**): Typed questions, as the System One API takes them
- `model` (string, optional): Optional System One model; empty means the account's

Responses: `200` Answers, or the reason there are none, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/aidr/browser/observations`

Upload a browser's observation batch

Request body (JSON):
- `source` (object, **required**)
  - `device` (string, **required**): The browser's device id
  - `capabilities` (array of string, optional)
- `seq` (integer (uint64), optional): The last observation's seq
- `observations` (array of object, **required**): At most 5000; each needs a seq of its own, increasing per browser (the engine starts at the Unix time in nanoseconds)
  - `seq` (integer (uint64), **required**)
  - `ts` (integer (int64), **required**): Unix nanoseconds
  - `kind` (string, **required**)
  - `subject` (?, **required**)
  - `target` (object, optional)
    - `type` (string, **required**)
    - `id` (string, **required**)
    - `props` (object, optional)
  - `props` (object, optional)
  - `content_ref` (string, optional)
  - `call_id` (string, optional)
  - `report_callid` (string, optional)

Responses: `200` Batch stored, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `422` Validation failed, `500` Internal Server Error

## `GET /api/aidr/detections`

List AIDR detections

Parameters:
- `scope` (query, optional): What the read covers: `account`, `source:<peer or gateway id>`, `actor:<actor node id, e.g. user://<id>>` or `session:<session id>` (the session, its lineage and everything it spawned). Regular users must pass `source:<one of their own peers>`.
- `since` (query, optional): Start of the time window, RFC 3339 or unix nanoseconds.
- `until` (query, optional): End of the time window, RFC 3339 or unix nanoseconds.
- `limit` (query, optional)

Responses: `200` Detections, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/aidr/graph`

Export the AIDR graph of a scope

Parameters:
- `scope` (query, optional): What the read covers: `account`, `source:<peer or gateway id>`, `actor:<actor node id, e.g. user://<id>>` or `session:<session id>` (the session, its lineage and everything it spawned). Regular users must pass `source:<one of their own peers>`.
- `since` (query, optional): Start of the time window, RFC 3339 or unix nanoseconds.
- `until` (query, optional): End of the time window, RFC 3339 or unix nanoseconds.

Responses: `200` Subgraph, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/aidr/observations`

List stored AIDR observations

Parameters:
- `scope` (query, optional): What the read covers: `account`, `source:<peer or gateway id>`, `actor:<actor node id, e.g. user://<id>>` or `session:<session id>` (the session, its lineage and everything it spawned). Regular users must pass `source:<one of their own peers>`.
- `since` (query, optional): Start of the time window, RFC 3339 or unix nanoseconds.
- `until` (query, optional): End of the time window, RFC 3339 or unix nanoseconds.
- `kind` (query, optional): Observation kind, e.g. `spawn`, `connect`, `llm_request`, `tool_call`, `file_read`
- `limit` (query, optional)

Responses: `200` Observations, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/aidr/replay`

Replay rules over stored observations

Request body (JSON):
- `scope` (string, optional): `account`, `source:<id>`, `actor:<id>` or `session:<id>`; empty means the account
- `since` (string, optional): Start of the window, RFC 3339 or unix nanoseconds
- `until` (string, optional): End of the window, RFC 3339 or unix nanoseconds
- `rules_yaml` (string, **required**): The rules to evaluate, YAML documents separated by `---`
- `limit` (integer, optional): Observations replayed, newest first; 0 means 2000

Responses: `200` Replay result, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/aidr/search`

Search AIDR observations

Parameters:
- `q` (query, required)
- `scope` (query, optional): What the read covers: `account`, `source:<peer or gateway id>`, `actor:<actor node id, e.g. user://<id>>` or `session:<session id>` (the session, its lineage and everything it spawned). Regular users must pass `source:<one of their own peers>`.
- `since` (query, optional): Start of the time window, RFC 3339 or unix nanoseconds.
- `until` (query, optional): End of the time window, RFC 3339 or unix nanoseconds.
- `limit` (query, optional)

Responses: `200` Matching observations, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/aidr/session`

Retrieve an AIDR session

Parameters:
- `id` (query, required): Session id, e.g. `session://pid/811:1780936000000000000`

Responses: `200` Session detail, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

## `GET /api/aidr/sessions`

List AIDR sessions

Parameters:
- `scope` (query, optional): What the read covers: `account`, `source:<peer or gateway id>`, `actor:<actor node id, e.g. user://<id>>` or `session:<session id>` (the session, its lineage and everything it spawned). Regular users must pass `source:<one of their own peers>`.
- `since` (query, optional): Start of the time window, RFC 3339 or unix nanoseconds.
- `until` (query, optional): End of the time window, RFC 3339 or unix nanoseconds.
- `agent` (query, optional): Only agent sessions (true) or only non-agent sessions (false)
- `active` (query, optional): Only sessions not ended (true) or only ended ones (false)
- `roots` (query, optional): Only sessions that head a run (an agent session or a session nobody spawned)
- `limit` (query, optional)

Responses: `200` Sessions, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/aidr/sources`

List AIDR sources

Responses: `200` Sources, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/aidr/sources/{source}/observations`

Upload an observation batch

Parameters:
- `source` (path, required): The uploading host's id

Request body (JSON):
- `source` (object, **required**)
  - `id` (string, **required**)
  - `kind` (string, optional): `endpoint` or `gateway`; empty means gateway
  - `device` (string, optional)
  - `capabilities` (array of string, optional)
- `seq` (integer (uint64), **required**): The last observation's seq
- `observations` (array of object, **required**)
  - `seq` (integer (uint64), **required**)
  - `ts` (integer (int64), **required**): Unix nanoseconds
  - `kind` (string, **required**)
  - `subject` (?, **required**)
  - `target` (object, optional)
    - `type` (string, **required**)
    - `id` (string, **required**)
    - `props` (object, optional)
  - `props` (object, optional)
  - `content_ref` (string, optional)
  - `call_id` (string, optional)
  - `report_callid` (string, optional)

Responses: `200` Batch stored, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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

## `POST /api/edge/events`

Push client events

Request body (JSON):
- `device_id` (string, optional): The browser's device id; AI events are recorded on it
- `events` (array of object, **required**): At most 100 events per request, 4 MB in all. An element with `type` `ai` is an AIEvent; any other is a client event (timestamp, activity, json_meta).
  - `type` (string, optional): `ai` for an AIEvent; absent for a client event
  - `timestamp` (string, optional): RFC3339; defaults to now
  - `activity` (integer, optional): Numeric activity code (client events)
  - `json_meta` (string, optional): JSON-encoded metadata object (client events)

Responses: `200` Stored, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/filters`

List all Filters

Parameters:
- `os` (query, optional): Client OS; switches the response to expanded filters for the caller. `browser` returns exactly the endpoint filters whose OS list names the browser.

Responses: `304` The caller's list is the one If-None-Match names, `200` A JSON array of Filter or ExpandedFilter objects, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/edge/filters`

Create a Filter

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `os` (array of string, optional): Endpoint filters only, where at least one is required. `browser` applies the filter to the user's browser extension; desktop values (linux, darwin, windows, …) never apply to the browser, and `browser` never applies to a desktop client.
- `groups` (array of string, **required**): Must contain at least one group ID
- `type` (string (endpoint | gateway), optional): What the filter governs — an endpoint's traffic (default; the OS condition applies) or an AI gateway's (group-targeted only; endpoints skip it)
- `guardrails` (array of string, optional): Guardrail ids applied to the filter's traffic. Optional; a filter without guardrails only grants.
- `models` (array of string, optional): Gateway filters only, where at least one is required. Model ids as provider/model, or provider/* for every model of a provider.
- `limits` (array of string, optional): Gateway filters only. Limit ids; each user gets their own counters, the lowest value wins across filters.
- `mcp` (array of object, optional): Gateway filters only. MCP servers granted, each whole or by tool names
  - `server_id` (string, **required**)
  - `tools` (array of string, optional): ["*"] or empty for every tool, else tool names
- `virtual_mcps` (array of string, optional): Gateway filters only. MCP bundle ids granted
- `gateways` (array of object, optional): Gateway filters only. Where the filter's users reach gateways
  - `name` (string, optional)
  - `url` (string, **required**)
- `scanners` (array of string, optional): Older name of guardrails; read and written for compatibility
- `agents` (array of string, optional): Process path patterns (wildcards and env vars) proxied through the network when the filter is active

Responses: `200` The created Filter, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/filters/effective`

Effective filters for a user

Parameters:
- `user` (query, optional): The user's ID. The user's groups and the peer's groups combine; at least one of user and peer is required.
- `peer` (query, optional): The calling peer's ID (the tunnel path)
- `type` (query, optional): Which filters to resolve

Responses: `200` The filters that apply to the user, as references with a content version each, `304` Unchanged since the ETag given in If-None-Match, `401` Requires authentication, `403` Forbidden, `422` Missing user or unknown type

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
- `os` (array of string, optional): Endpoint filters only, where at least one is required. `browser` applies the filter to the user's browser extension; desktop values (linux, darwin, windows, …) never apply to the browser, and `browser` never applies to a desktop client.
- `groups` (array of string, **required**): Must contain at least one group ID
- `type` (string (endpoint | gateway), optional): What the filter governs — an endpoint's traffic (default; the OS condition applies) or an AI gateway's (group-targeted only; endpoints skip it)
- `guardrails` (array of string, optional): Guardrail ids applied to the filter's traffic. Optional; a filter without guardrails only grants.
- `models` (array of string, optional): Gateway filters only, where at least one is required. Model ids as provider/model, or provider/* for every model of a provider.
- `limits` (array of string, optional): Gateway filters only. Limit ids; each user gets their own counters, the lowest value wins across filters.
- `mcp` (array of object, optional): Gateway filters only. MCP servers granted, each whole or by tool names
  - `server_id` (string, **required**)
  - `tools` (array of string, optional): ["*"] or empty for every tool, else tool names
- `virtual_mcps` (array of string, optional): Gateway filters only. MCP bundle ids granted
- `gateways` (array of object, optional): Gateway filters only. Where the filter's users reach gateways
  - `name` (string, optional)
  - `url` (string, **required**)
- `scanners` (array of string, optional): Older name of guardrails; read and written for compatibility
- `agents` (array of string, optional): Process path patterns (wildcards and env vars) proxied through the network when the filter is active

Responses: `200` The updated Filter, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/edge/filters/{filterId}`

Delete a Filter

Parameters:
- `filterId` (path, required)

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/filters/{filterId}/expanded`

Get a Filter with its guardrails expanded

Parameters:
- `filterId` (path, required): The Filter ID

Responses: `200` An ExpandedFilter object with a version, `401` Requires authentication, `403` Forbidden, `404` Resource not found

## `GET /api/edge/guardrails`

List all Guardrails

Responses: `200` A JSON array of Guardrails, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/edge/guardrails`

Create a Guardrail

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `severity` (string (low | medium | high | critical), **required**): Case-insensitive; stored lower-case
- `context` (array of string, **required**): Must contain at least one value; the first one is stored as context_type
- `rule_yaml` (string, **required**)
- `enabled` (boolean, optional)

Responses: `200` The created Guardrail, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/guardrails/generate`

Check AI rule generation availability

Responses: `200` Generation is available, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `428` Generation is not available, `500` Internal Server Error

## `POST /api/edge/guardrails/generate`

Generate a guardrail rule with AI

Request body (JSON):
- `prompt` (string, **required**)
- `current_yaml` (string, optional)

Responses: `200` text/event-stream of generation frames, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `428` Precondition required, `500` Internal Server Error

## `GET /api/edge/guardrails/{guardrailId}`

Retrieve a Guardrail

Parameters:
- `guardrailId` (path, required)

Responses: `200` A Guardrail object, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `PUT /api/edge/guardrails/{guardrailId}`

Update a Guardrail

Parameters:
- `guardrailId` (path, required)

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `severity` (string (low | medium | high | critical), **required**): Case-insensitive; stored lower-case
- `context` (array of string, **required**): Must contain at least one value; the first one is stored as context_type
- `rule_yaml` (string, **required**)
- `enabled` (boolean, optional)

Responses: `200` The updated Guardrail, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/edge/guardrails/{guardrailId}`

Delete a Guardrail

Parameters:
- `guardrailId` (path, required)

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/limits`

List all Limits

Responses: `200` A JSON array of Limits, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/edge/limits`

Create a GatewayLimit

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `budget` (object, optional)
  - `max_usd` (number, **required**)
  - `reset` (string (hourly | daily | weekly | monthly | yearly), **required**)
- `tokens` (object, optional)
  - `max` (integer (int64), **required**)
  - `reset` (string (hourly | daily | weekly | monthly | yearly), **required**)
- `requests` (object, optional)
  - `max` (integer (int64), **required**)
  - `reset` (string (hourly | daily | weekly | monthly | yearly), **required**)

Responses: `200` The created GatewayLimit, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `409` Conflict, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/limits/{limitId}`

Retrieve a GatewayLimit

Parameters:
- `limitId` (path, required)

Responses: `200` A GatewayLimit object, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

## `PUT /api/edge/limits/{limitId}`

Update a GatewayLimit

Parameters:
- `limitId` (path, required)

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `budget` (object, optional)
  - `max_usd` (number, **required**)
  - `reset` (string (hourly | daily | weekly | monthly | yearly), **required**)
- `tokens` (object, optional)
  - `max` (integer (int64), **required**)
  - `reset` (string (hourly | daily | weekly | monthly | yearly), **required**)
- `requests` (object, optional)
  - `max` (integer (int64), **required**)
  - `reset` (string (hourly | daily | weekly | monthly | yearly), **required**)

Responses: `200` The updated GatewayLimit, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `409` Conflict, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/edge/limits/{limitId}`

Delete a GatewayLimit

Parameters:
- `limitId` (path, required)

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `412` Precondition failed, `500` Internal Server Error

## `GET /api/edge/mcp-catalog`

List the MCP catalog

Responses: `200` The catalog, `401` Requires authentication, `403` Forbidden

## `GET /api/edge/mcp-servers`

List all MCP Servers

Responses: `200` A JSON array of MCP Servers, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/edge/mcp-servers`

Create a GatewayMCPServer

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `slug` (string, optional): Path the server is served at (/mcp/<slug>); derived from the name when empty, immutable after creation
- `connection` (string (http | sse | stdio), **required**)
- `url` (string, optional): Required for http and sse
- `command` (string, optional): Required for stdio
- `args` (array of string, optional)
- `env` (object, optional)
- `extra_headers` (object, optional)
- `insecure_skip_verify` (boolean, optional)
- `code_mode` (boolean, optional)
- `auth_type` (string (none | headers | per_user_headers | oauth | per_user_oauth), optional)
- `headers` (object, optional): Admin-held credential headers; write-only, masked on read
- `per_user_header_keys` (array of string, optional): Header names each user supplies (per_user_headers)
- `oauth` (object, optional): An MCP server's OAuth client; empty fields are discovered and registered by management
  - `client_id` (string, optional)
  - `client_secret` (string, optional): Write-only; masked on read, empty or masked on update keeps the stored value
  - `authorize_url` (string, optional)
  - `token_url` (string, optional)
  - `registration_url` (string, optional)
  - `scopes` (array of string, optional)
  - `resource` (string, optional)
  - `redirect_uri` (string, optional): The callback registered with the authorization server; set by management
- `icon_url` (string, optional)
- `docs_url` (string, optional)

Responses: `200` The created GatewayMCPServer, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `409` Conflict, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/mcp-servers/{serverId}`

Retrieve a GatewayMCPServer

Parameters:
- `serverId` (path, required)

Responses: `200` A GatewayMCPServer object, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

## `PUT /api/edge/mcp-servers/{serverId}`

Update a GatewayMCPServer

Parameters:
- `serverId` (path, required)

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `slug` (string, optional): Path the server is served at (/mcp/<slug>); derived from the name when empty, immutable after creation
- `connection` (string (http | sse | stdio), **required**)
- `url` (string, optional): Required for http and sse
- `command` (string, optional): Required for stdio
- `args` (array of string, optional)
- `env` (object, optional)
- `extra_headers` (object, optional)
- `insecure_skip_verify` (boolean, optional)
- `code_mode` (boolean, optional)
- `auth_type` (string (none | headers | per_user_headers | oauth | per_user_oauth), optional)
- `headers` (object, optional): Admin-held credential headers; write-only, masked on read
- `per_user_header_keys` (array of string, optional): Header names each user supplies (per_user_headers)
- `oauth` (object, optional): An MCP server's OAuth client; empty fields are discovered and registered by management
  - `client_id` (string, optional)
  - `client_secret` (string, optional): Write-only; masked on read, empty or masked on update keeps the stored value
  - `authorize_url` (string, optional)
  - `token_url` (string, optional)
  - `registration_url` (string, optional)
  - `scopes` (array of string, optional)
  - `resource` (string, optional)
  - `redirect_uri` (string, optional): The callback registered with the authorization server; set by management
- `icon_url` (string, optional)
- `docs_url` (string, optional)

Responses: `200` The updated GatewayMCPServer, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `409` Conflict, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/edge/mcp-servers/{serverId}`

Delete a GatewayMCPServer

Parameters:
- `serverId` (path, required)

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `412` Precondition failed, `500` Internal Server Error

## `GET /api/edge/providers`

List all Providers

Responses: `200` A JSON array of Providers, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/edge/providers`

Create a GatewayProvider

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `type` (string, **required**): One of the AI gateway's provider types (openai, anthropic, azure, bedrock, vertex, gemini, mistral, ollama, vllm, …)
- `base_url` (string, optional): Overrides the type's default endpoint; required for ollama, vllm and sgl
- `credential` (object, optional): The credential fields of the type (api_key for most; endpoint+api_key for azure; access_key, secret_key, region for bedrock; project_id, region, auth_credentials for vertex). Write-only; on update an empty or masked field keeps the stored value
- `extra_headers` (object, optional)
- `insecure_skip_verify` (boolean, optional): Skip TLS certificate verification towards the provider, for a local or internal endpoint with its own CA. Default false
- `models` (array of object, optional)
  - `name` (string, **required**): The model identifier the provider expects
  - `display_name` (string, optional)
  - `enabled` (boolean, **required**)

Responses: `200` The created GatewayProvider, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `409` Conflict, `422` Validation failed, `500` Internal Server Error

## `POST /api/edge/providers/discover`

List the models a provider offers

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `type` (string, **required**): One of the AI gateway's provider types (openai, anthropic, azure, bedrock, vertex, gemini, mistral, ollama, vllm, …)
- `base_url` (string, optional): Overrides the type's default endpoint; required for ollama, vllm and sgl
- `credential` (object, optional): The credential fields of the type (api_key for most; endpoint+api_key for azure; access_key, secret_key, region for bedrock; project_id, region, auth_credentials for vertex). Write-only; on update an empty or masked field keeps the stored value
- `extra_headers` (object, optional)
- `insecure_skip_verify` (boolean, optional): Skip TLS certificate verification towards the provider, for a local or internal endpoint with its own CA. Default false
- `models` (array of ?, optional)
- `id` (string, optional)

Responses: `200` The models, `401` Requires authentication, `403` Forbidden, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/providers/{providerId}`

Retrieve a GatewayProvider

Parameters:
- `providerId` (path, required)

Responses: `200` A GatewayProvider object, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

## `PUT /api/edge/providers/{providerId}`

Update a GatewayProvider

Parameters:
- `providerId` (path, required)

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `type` (string, **required**): One of the AI gateway's provider types (openai, anthropic, azure, bedrock, vertex, gemini, mistral, ollama, vllm, …)
- `base_url` (string, optional): Overrides the type's default endpoint; required for ollama, vllm and sgl
- `credential` (object, optional): The credential fields of the type (api_key for most; endpoint+api_key for azure; access_key, secret_key, region for bedrock; project_id, region, auth_credentials for vertex). Write-only; on update an empty or masked field keeps the stored value
- `extra_headers` (object, optional)
- `insecure_skip_verify` (boolean, optional): Skip TLS certificate verification towards the provider, for a local or internal endpoint with its own CA. Default false
- `models` (array of object, optional)
  - `name` (string, **required**): The model identifier the provider expects
  - `display_name` (string, optional)
  - `enabled` (boolean, **required**)

Responses: `200` The updated GatewayProvider, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `409` Conflict, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/edge/providers/{providerId}`

Delete a GatewayProvider

Parameters:
- `providerId` (path, required)

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `412` Precondition failed, `500` Internal Server Error

## `GET /api/edge/virtual-mcps`

List all Virtual MCPs

Responses: `200` A JSON array of Virtual MCPs, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/edge/virtual-mcps`

Create a GatewayVirtualMCP

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `slug` (string, optional)
- `tools` (array of object, **required**)
  - `server_id` (string, **required**)
  - `tools` (array of string, **required**): ["*"] for every tool, else tool names

Responses: `200` The created GatewayVirtualMCP, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `409` Conflict, `422` Validation failed, `500` Internal Server Error

## `GET /api/edge/virtual-mcps/{vmcpId}`

Retrieve a GatewayVirtualMCP

Parameters:
- `vmcpId` (path, required)

Responses: `200` A GatewayVirtualMCP object, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

## `PUT /api/edge/virtual-mcps/{vmcpId}`

Update a GatewayVirtualMCP

Parameters:
- `vmcpId` (path, required)

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `enabled` (boolean, optional)
- `slug` (string, optional)
- `tools` (array of object, **required**)
  - `server_id` (string, **required**)
  - `tools` (array of string, **required**): ["*"] for every tool, else tool names

Responses: `200` The updated GatewayVirtualMCP, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `409` Conflict, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/edge/virtual-mcps/{vmcpId}`

Delete a GatewayVirtualMCP

Parameters:
- `vmcpId` (path, required)

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `412` Precondition failed, `500` Internal Server Error

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

## `POST /api/groups/{groupId}/peers/{peerId}`

Add a Peer to a Group

Parameters:
- `groupId` (path, required): The unique identifier of a group
- `peerId` (path, required): The unique identifier of a peer

Responses: `200` The updated Group object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/groups/{groupId}/peers/{peerId}`

Remove a Peer from a Group

Parameters:
- `groupId` (path, required): The unique identifier of a group
- `peerId` (path, required): The unique identifier of a peer

Responses: `200` The updated Group object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

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
  - `extension_proxy` (?, optional)
  - `enterprise_browser` (?, optional)

Responses: `200` A Profile Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `POST /api/profiles/pac`

Generate a PAC for groups

Request body (JSON):
- `groups` (array of string, **required**): Group IDs a member of which the PAC is computed for (every peer is in All as well).
- `os` (string, **required**): The browser's operating system as profiles name it (Windows, Darwin, Linux, Android, iOS); posture checks are evaluated for it.
- `gateway` (string, optional): The gateway proxy address the PAC points at, host:port; defaults to the account's clientless proxy address.

Responses: `200` The generated PAC, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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
  - `extension_proxy` (?, optional)
  - `enterprise_browser` (?, optional)

Responses: `200` A Profile object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/profiles/{profileId}`

Delete a Profile

Parameters:
- `profileId` (path, required): The unique identifier of a profile

Responses: `200` Delete status code, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `GET /api/published-apps`

List published applications

Responses: `200` A JSON array of published applications, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/published-apps`

Publish an application

Request body (JSON):
- `name` (string, **required**): Shown on the Workplace — e.g. `CRM`
- `description` (string, optional)
- `domain` (string, **required**): The application's address (a hostname), lowercase; one address is one application — e.g. `crm.acme.com`
- `target` (string, **required**): Where the gateway forwards to through the user's tunnel, http(s)://host[:port], no path — e.g. `http://10.1.2.3:8080`
- `groups` (array of string, **required**): Group IDs whose members may open the application. Empty means nobody.
- `enabled` (boolean, **required**)
- `preserve_host` (boolean, optional): Send the application's address as the Host header instead of the target's
- `forward_credential` (boolean, optional): Send the user's own credential to the target as an Authorization bearer, for an application that verifies users with management itself (an AI gateway)
- `posture_checks` (array of string, optional): Posture check IDs the accessing device must satisfy at the application's door
- `any_check_must_pass` (boolean, optional): Posture check evaluation logic. If false (default), all posture checks must pass. If true, at least one posture check set must pass.

Responses: `200` The published application, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `422` Validation failed, `500` Internal Server Error

## `GET /api/published-apps/check`

Whether an address can be published

Parameters:
- `domain` (query, required)
- `except` (query, optional)

Responses: `200` The answer, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/published-apps/domains/check`

Whether a base domain's wildcard points at the gateway

Parameters:
- `domain` (query, required)

Responses: `200` The resolution, `401` Requires authentication, `403` Forbidden, `422` Validation failed, `500` Internal Server Error

## `GET /api/published-apps/exists`

Whether an address is published

Parameters:
- `domain` (query, required)

Responses: `200` The answer

## `PUT /api/published-apps/{appId}`

Update a published application

Parameters:
- `appId` (path, required)

Request body (JSON):
- `name` (string, **required**): Shown on the Workplace — e.g. `CRM`
- `description` (string, optional)
- `domain` (string, **required**): The application's address (a hostname), lowercase; one address is one application — e.g. `crm.acme.com`
- `target` (string, **required**): Where the gateway forwards to through the user's tunnel, http(s)://host[:port], no path — e.g. `http://10.1.2.3:8080`
- `groups` (array of string, **required**): Group IDs whose members may open the application. Empty means nobody.
- `enabled` (boolean, **required**)
- `preserve_host` (boolean, optional): Send the application's address as the Host header instead of the target's
- `forward_credential` (boolean, optional): Send the user's own credential to the target as an Authorization bearer, for an application that verifies users with management itself (an AI gateway)
- `posture_checks` (array of string, optional): Posture check IDs the accessing device must satisfy at the application's door
- `any_check_must_pass` (boolean, optional): Posture check evaluation logic. If false (default), all posture checks must pass. If true, at least one posture check set must pass.

Responses: `200` The published application, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `422` Validation failed, `500` Internal Server Error

## `DELETE /api/published-apps/{appId}`

Unpublish an application

Parameters:
- `appId` (path, required)

Responses: `200` Unpublished, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

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
- `report_type` (string (user_activity | authentication | ai_activity | ai_usage), optional): user_activity (default), authentication, ai_activity or ai_usage

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

## `GET /api/support/audit/sessions/{sessionId}`

Read the log of any support session in the account

Parameters:
- `sessionId` (path, required)

Responses: `200` The session with its messages and owner, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

## `GET /api/support/devices/{peerId}`

Describe a peer for the support tools without contacting it

Parameters:
- `peerId` (path, required)

Responses: `200` The device summary, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

## `POST /api/support/devices/{peerId}/invoke`

Run one support tool on a peer

Parameters:
- `peerId` (path, required)

Request body (JSON):
- `name` (string, **required**): A tool name from the device's catalog
- `args` (object, optional): Arguments matching that tool's args_schema; unknown fields are rejected by the device
- `timeout_ms` (integer, optional): Per-command deadline; the device clamps it to its own ceiling (120000)

Responses: `200` The device's result, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `409` Conflict, `501` Not implemented on this device, `503` Service unavailable, `504` Gateway timeout, `500` Internal Server Error

## `GET /api/support/devices/{peerId}/tools`

List the tools a peer offers

Parameters:
- `peerId` (path, required)

Responses: `200` The device's tool catalog, as the client produced it, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `409` Conflict, `501` Not implemented on this device, `503` Service unavailable, `504` Gateway timeout, `500` Internal Server Error

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
- `model` (string, optional): The "<providerId>:<modelId>" reference chosen in the chat, from GET /api/ai/models?use=assistant. Omit to keep the session's current model, which falls back to the account default. Validated on every turn: a model that is no longer approved is refused.

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

## `GET /api/users/current/ai-access`

What the caller may use through the AI gateways

Responses: `200` Gateways, models, MCP servers and virtual MCPs granted, `401` Requires authentication

## `GET /api/users/current/mcp-connections`

The caller's state at the MCP servers granted to them

Responses: `200` Connections, `401` Requires authentication

## `POST /api/users/current/mcp-connections/complete`

Finish the caller's OAuth sign-in at an MCP server with what the provider returned

Request body (JSON):
- `state` (string, **required**): The state the provider returned with
- `code` (string, **required**): The code the provider returned

Responses: `200` Signed in, `400` Bad Request, `401` Requires authentication, `404` Resource not found

## `DELETE /api/users/current/mcp-connections/{serverId}`

Remove the caller's credential at an MCP server

Parameters:
- `serverId` (path, required)

Responses: `200` Removed, `401` Requires authentication, `404` Resource not found

## `PUT /api/users/current/mcp-connections/{serverId}/headers`

Store the caller's header values for an MCP server, after trying them

Parameters:
- `serverId` (path, required)

Request body (JSON):
- `headers` (object, **required**)

Responses: `200` Stored, `400` Bad Request, `401` Requires authentication, `404` Resource not found

## `POST /api/users/current/mcp-connections/{serverId}/oauth`

Start the caller's OAuth sign-in at an MCP server

Parameters:
- `serverId` (path, required)

Request body (JSON):
- (object, see live spec)

Responses: `200` Where the browser goes, `400` Bad Request, `401` Requires authentication, `404` Resource not found

## `GET /api/users/current/pac`

Get the caller's PAC

Parameters:
- `gateway` (query, optional): The gateway proxy address the PAC points at, host:port; defaults to the account's clientless proxy address.

Responses: `200` The PAC script, `204` No PAC for this user (mode disabled): the browser must configure no proxy., `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/users/current/published-apps`

The applications the current user may open

Responses: `200` A JSON array, `401` Requires authentication, `500` Internal Server Error

## `POST /api/users/current/published-apps/access`

Authorize the current user at a published application's door

Request body (JSON):
- `host` (string, **required**): The application's address the user is signing in at
- `browser` (object, optional): The device as the sign-in request describes it
  - `os` (string, optional)
  - `os_version` (string, optional)
  - `browser` (string, optional)
  - `browser_version` (string, optional)
  - `mobile` (boolean, optional)
- `public_ip` (string, optional): The connection's public address
- `device` (string, optional): The browser's device seed, from the Workplace, behind the session's device ID
- `extension` (boolean, optional): The Netzilo extension answered the Workplace page in this browser
- `extension_device_id` (string, optional): The extension's gateway device ID, when it has one; a live gateway session with it verifies the extension
- `enterprise_browser` (boolean, optional): The Netzilo Enterprise Browser answered the Workplace page
- `endpoint` (object, optional): A device's posture as its Netzilo client reports it
  - `goos` (string, optional)
  - `os` (string, optional)
  - `os_version` (string, optional)
  - `kernel_version` (string, optional)
  - `platform` (string, optional)
  - `client_version` (string, optional)
  - `meta` (object, optional)
    - `device_id` (string, optional)
    - `domain_name` (string, optional)
    - `is_being_debugged` (boolean, optional)
    - `is_virtual_device` (boolean, optional)
    - `is_firewall_enabled` (boolean, optional)
    - `is_disk_encryption_enabled` (boolean, optional)
    - `is_av_enabled` (boolean, optional)
    - `is_av_updated` (boolean, optional)
    - `is_screen_locked` (boolean, optional)
    - `is_os_updated` (boolean, optional)
    - `is_netzilo_container` (boolean, optional)
    - `is_netzilo_browser` (boolean, optional)
    - `is_netzilo_extension` (boolean, optional)
    - `integrity_level` (integer, optional)
  - `check_results` (array of object, optional)
    - `id` (string, optional)
    - `result` (string, optional)
- `api` (boolean, optional): A credential caller, not a browser at the Workplace
- `revalidation` (boolean, optional): A running session's evidence presented again, not a sign-in; recorded as an access event only when it no longer passes

Responses: `200` The decision, `400` Bad Request, `401` Requires authentication, `500` Internal Server Error

## `GET /api/users/current/routing`

Get the caller's browser routing

Responses: `200` The caller's browser routing, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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

## `GET /api/users/{userId}/gateway-sessions`

List a user's gateway sessions

Parameters:
- `userId` (path, required): The unique identifier of a user

Responses: `200` The user's gateway sessions, `401` Requires authentication, `403` Forbidden, `404` Resource not found, `500` Internal Server Error

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
- `scope` (string ( | mcp), optional): What the token may do. Empty is everything the user may do; "mcp" only identifies the user to AI gateways.

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

