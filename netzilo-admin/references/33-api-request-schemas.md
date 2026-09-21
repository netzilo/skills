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

Responses: `200` A JSON array of accounts, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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

Responses: `200` An Account object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `DELETE /api/accounts/{accountId}`

Delete an Account

Parameters:
- `accountId` (path, required): The unique identifier of an account

Responses: `200` Delete account status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/dns/nameservers`

List all Nameserver Groups

Responses: `200` A JSON Array of Nameserver Groups, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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

Responses: `200` A Nameserver Groups Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/dns/nameservers/{nsgroupId}`

Retrieve a Nameserver Group

Parameters:
- `nsgroupId` (path, required): The unique identifier of a Nameserver Group

Responses: `200` A Nameserver Group object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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

Responses: `200` A Nameserver Group object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `DELETE /api/dns/nameservers/{nsgroupId}`

Delete a Nameserver Group

Parameters:
- `nsgroupId` (path, required): The unique identifier of a Nameserver Group

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/dns/settings`

Retrieve DNS settings

Responses: `200` A JSON Object of DNS Setting, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `PUT /api/dns/settings`

Update DNS Settings

Request body (JSON):
- `disabled_management_groups` (array of string, **required**): Groups whose DNS management is disabled

Responses: `200` A JSON Object of DNS Setting, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/event-streaming`

Request body (JSON):
- `platform` (string, **required**)
- `config` (object, **required**)
- `enabled` (boolean, **required**)

Responses: `200` A Profile Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/event-streaming/sign-urls`

Request body (JSON):
- array of string

Responses: `200` A Profile Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/events`

List all Events

Responses: `200` A JSON Array of Events, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/events`

Create an Event

Request body (JSON):
- `activity` (integer, optional)
- `meta` (object, optional)
- `timestamp` (string, optional)
- `target_id` (string, optional)

Responses: `200` A Event

## `POST /api/getclient`

Request body (JSON):
- `os` (string, optional)

Responses: `301` , `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/groups`

List all Groups

Responses: `200` A JSON Array of Groups, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/groups`

Create a Group

Request body (JSON):
- `name` (string, **required**): Group name identifier — e.g. `devs`
- `peers` (array of string, optional): List of peers ids

Responses: `200` A Group Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/groups/{groupId}`

Retrieve a Group

Parameters:
- `groupId` (path, required): The unique identifier of a group

Responses: `200` A Group object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `PUT /api/groups/{groupId}`

Update a Group

Parameters:
- `groupId` (path, required): The unique identifier of a group

Request body (JSON):
- `name` (string, **required**): Group name identifier — e.g. `devs`
- `peers` (array of string, optional): List of peers ids

Responses: `200` A Group object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `DELETE /api/groups/{groupId}`

Delete a Group

Parameters:
- `groupId` (path, required): The unique identifier of a group

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/integrations`

Responses: `200` , `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/locations/countries`

List all country codes

Responses: `200` List of country codes, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/locations/countries/{country}/cities`

List all city names by country

Parameters:
- `country` (path, required)

Responses: `200` List of city names, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/peers`

List all Peers

Responses: `200` A JSON Array of Peers, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/peers/{peerId}`

Retrieve a Peer

Parameters:
- `peerId` (path, required): The unique identifier of a peer

Responses: `200` A Peer object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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

Responses: `200` A Peer object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `DELETE /api/peers/{peerId}`

Delete a Peer

Parameters:
- `peerId` (path, required): The unique identifier of a peer

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/policies`

List all Policies

Responses: `200` A JSON Array of Policies, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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

Responses: `200` A Policy Object

## `GET /api/policies/{policyId}`

Retrieve a Policy

Parameters:
- `policyId` (path, required): The unique identifier of a policy

Responses: `200` A Policy object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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

Responses: `200` A Policy object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `DELETE /api/policies/{policyId}`

Delete a Policy

Parameters:
- `policyId` (path, required): The unique identifier of a policy

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/posture-checks`

List all Posture Checks

Responses: `200` A JSON Array of posture checks, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/posture-checks`

Create a Posture Check

Request body (JSON):
- `name` (string, **required**): Posture check name identifier — e.g. `Default`
- `description` (string, **required**): Posture check friendly description — e.g. `This checks if the peer is running required Netzilo's version`
- `checks` (object, optional): List of objects that perform the actual checks
  - `nb_version_check` (?, optional)
  - `os_version_check` (?, optional)
  - `geo_location_check` (?, optional)
  - `date_time_checks` (?, optional)
  - `peer_network_range_check` (?, optional)
  - `process_check` (?, optional)
  - `netzilo_check` (?, optional)

Responses: `200` A posture check Object

## `GET /api/posture-checks/{postureCheckId}`

Retrieve a Posture Check

Parameters:
- `postureCheckId` (path, required): The unique identifier of a posture check

Responses: `200` A posture check object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `PUT /api/posture-checks/{postureCheckId}`

Update a Posture Check

Parameters:
- `postureCheckId` (path, required): The unique identifier of a posture check

Request body (JSON):
- `name` (string, **required**): Posture check name identifier — e.g. `Default`
- `description` (string, **required**): Posture check friendly description — e.g. `This checks if the peer is running required Netzilo's version`
- `checks` (object, optional): List of objects that perform the actual checks
  - `nb_version_check` (?, optional)
  - `os_version_check` (?, optional)
  - `geo_location_check` (?, optional)
  - `date_time_checks` (?, optional)
  - `peer_network_range_check` (?, optional)
  - `process_check` (?, optional)
  - `netzilo_check` (?, optional)

Responses: `200` A posture check object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `DELETE /api/posture-checks/{postureCheckId}`

Delete a Posture Check

Parameters:
- `postureCheckId` (path, required): The unique identifier of a posture check

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/profiles`

List all Profiles

Responses: `200` , `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/profiles`

Create a Profile

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `os` (array of string, **required**)
- `enabled` (boolean, **required**)
- `groups` (array of string, optional)
- `components` (object, optional)
  - `netzilo_workspace` (?, optional)
  - `disposable_browser` (string, optional)
  - `browser_extension` (array of ?, optional)
  - `extension_bookmarks` (array of ?, optional)
  - `enterprise_browser` (?, optional)

Responses: `200` A Profile Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `PUT /api/profiles/{profileId}`

update a Profile

Parameters:
- `profileId` (path, required): The unique identifier of a profile

Request body (JSON):
- `name` (string, **required**)
- `description` (string, optional)
- `os` (array of string, **required**)
- `enabled` (boolean, **required**)
- `groups` (array of string, optional)
- `components` (object, optional)
  - `netzilo_workspace` (?, optional)
  - `disposable_browser` (string, optional)
  - `browser_extension` (array of ?, optional)
  - `extension_bookmarks` (array of ?, optional)
  - `enterprise_browser` (?, optional)

Responses: `200` A Profile object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/register`

Request body (JSON):
- `company_name` (string, **required**)
- `subdomain` (string, **required**)
- `first_name` (string, **required**)
- `last_name` (string, **required**)
- `email` (string, **required**)
- `password` (string, **required**)
- `accept_terms_of_service` (boolean, **required**)
- `recaptcha_token` (string, **required**)

Responses: `200` A Register Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden

## `POST /api/reports`

Request body (JSON):
- `from` (string, **required**): Start of the reporting window, YYYY-MM-DD — e.g. `2026-09-01`
- `to` (string, **required**): End of the reporting window (inclusive), YYYY-MM-DD, not before from — e.g. `2026-09-21`
- `groups` (array of string, optional): Restrict the report to these group IDs (empty = whole account)
- `report_type` (string (user_activity | authentication | ai_activity), optional): user_activity (default), authentication, or ai_activity

Responses: `200` A Report Object, `400` Bad Request, `401` Requires authentication

## `GET /api/routes`

List all Routes

Responses: `200` A JSON Array of Routes, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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

Responses: `200` A Route Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/routes/{routeId}`

Retrieve a Route

Parameters:
- `routeId` (path, required): The unique identifier of a route

Responses: `200` A Route object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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

Responses: `200` A Route object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `DELETE /api/routes/{routeId}`

Delete a Route

Parameters:
- `routeId` (path, required): The unique identifier of a route

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/setup-keys`

List all Setup Keys

Responses: `200` A JSON Array of Setup keys, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/setup-keys`

Create a Setup Key

Request body (JSON):
- `name` (string, **required**): Setup Key name — e.g. `Default key`
- `type` (string, **required**): Setup key type, one-off for single time usage and reusable — e.g. `reusable`
- `expires_in` (integer, **required**): Expiration time in seconds — e.g. `86400`
- `revoked` (boolean, **required**): Setup key revocation status — e.g. `False`
- `auto_groups` (array of string, **required**): List of group IDs to auto-assign to peers registered with this key
- `usage_limit` (integer, **required**): A number of times this key can be used. The value of 0 indicates the unlimited usage. — e.g. `0`
- `ephemeral` (boolean, optional): Indicate that the peer will be ephemeral or not — e.g. `True`

Responses: `200` A Setup Keys Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/setup-keys/{keyId}`

Retrieve a Setup Key

Parameters:
- `keyId` (path, required): The unique identifier of a setup key

Responses: `200` A Setup Key object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `PUT /api/setup-keys/{keyId}`

Update a Setup Key

Parameters:
- `keyId` (path, required): The unique identifier of a setup key

Request body (JSON):
- `name` (string, **required**): Setup Key name — e.g. `Default key`
- `type` (string, **required**): Setup key type, one-off for single time usage and reusable — e.g. `reusable`
- `expires_in` (integer, **required**): Expiration time in seconds — e.g. `86400`
- `revoked` (boolean, **required**): Setup key revocation status — e.g. `False`
- `auto_groups` (array of string, **required**): List of group IDs to auto-assign to peers registered with this key
- `usage_limit` (integer, **required**): A number of times this key can be used. The value of 0 indicates the unlimited usage. — e.g. `0`
- `ephemeral` (boolean, optional): Indicate that the peer will be ephemeral or not — e.g. `True`

Responses: `200` A Setup Key object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/stats`

Responses: `200` , `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/templates/{category}`

Parameters:
- `category` (path, required): The category of a template

Responses: `200` , `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/tenant`

Responses: `200` , `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/tenant`

Request body (JSON):
- `id` (string, optional): Tenant unique identifier
- `company_name` (string, optional)
- `company_website` (string, optional): Tenant domain name
- `company_size` (string, optional)
- `heard_from` (string, optional)
- `is_initialized` (boolean, optional)
- `subscription` (string, optional)

Responses: `200` , `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/tenant/subscription`

Request body (JSON):
- `subscription` (string (Personal | Professional | Enterprise), optional): The subscription level of a tenant

Responses: `200` , `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/tenant/subscription/confirm`

Request body (JSON):
- `proration_date` (integer, optional)
- `subscription` (string (Personal | Professional | Enterprise), optional): The subscription level of a tenant

Responses: `200` , `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/users`

List all Users

Parameters:
- `service_user` (query, optional): Filters users and returns either regular users or service users

Responses: `200` A JSON array of Users, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

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

Responses: `200` A User object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `PUT /api/users/{userId}`

Update a User

Parameters:
- `userId` (path, required): The unique identifier of a user

Request body (JSON):
- `role` (string, **required**): User's Netzilo account role — e.g. `admin`
- `auto_groups` (array of string, **required**): Group IDs to auto-assign to peers registered by this user
- `is_blocked` (boolean, **required**): If set to true then user is blocked and can't use the system — e.g. `False`
- `update_peer_groups` (boolean, **required**): If set to true then update peer groups as well as user groups — e.g. `False`

Responses: `200` A User object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `DELETE /api/users/{userId}`

Delete a User

Parameters:
- `userId` (path, required): The unique identifier of a user

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/users/{userId}/invite`

Resend user invitation

Parameters:
- `userId` (path, required): The unique identifier of a user

Responses: `200` Invite status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/users/{userId}/tokens`

List all Tokens

Parameters:
- `userId` (path, required): The unique identifier of a user

Responses: `200` A JSON Array of PersonalAccessTokens, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/users/{userId}/tokens`

Create a Token

Parameters:
- `userId` (path, required): The unique identifier of a user

Request body (JSON):
- `name` (string, **required**): Name of the token — e.g. `My first token`
- `expires_in` (integer, **required**): Expiration in days — e.g. `30`

Responses: `200` The token in plain text, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `GET /api/users/{userId}/tokens/{tokenId}`

Retrieve a Token

Parameters:
- `userId` (path, required): The unique identifier of a user
- `tokenId` (path, required): The unique identifier of a token

Responses: `200` A PersonalAccessTokens Object, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `DELETE /api/users/{userId}/tokens/{tokenId}`

Delete a Token

Parameters:
- `userId` (path, required): The unique identifier of a user
- `tokenId` (path, required): The unique identifier of a token

Responses: `200` Delete status code, `400` Bad Request, `401` Requires authentication, `403` Forbidden, `500` Internal Server Error

## `POST /api/verify-recaptcha`

Request body (JSON):
- `recaptcha_token` (string, **required**)

Responses: `200` A VerifyRecaptcha Object

