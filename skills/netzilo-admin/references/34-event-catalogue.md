---
id: '34'
title: Event catalogue — what each activity is called
requires: []
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 12701
sections:
- id: administration
  title: Administration
  chars: 6081
- id: access-control
  title: Access Control
  chars: 816
- id: policy-violation
  title: Policy Violation
  chars: 1249
- id: data-exfiltration
  title: Data Exfiltration
  chars: 497
- id: suspicious
  title: Suspicious
  chars: 454
- id: investigation
  title: Investigation
  chars: 79
- id: ai-edge
  title: AI Edge
  chars: 2661
---
# Event catalogue — what each activity is called

Generated from Netzilo Server's activity table on 2026-10-22 by
`scripts/gen-event-codes.py`. 169 activities.

Every event the API returns carries all three columns: `activity` (the display
name), `activity_code` (the stable identifier) and `activity_category`. **Say the
display name.** The code is a filter value and a machine identifier — put it in a
`GET /api/events/paginated?code=…` call, not in a sentence to an admin, unless they
asked for it or you are telling them what to search for themselves.

Codes are also the vocabulary of `references/32-detection-rule-authoring.md` and the
Activity page filters in `references/30-activity-reports-and-integrations.md`.

Codes marked *(history only)* are no longer recorded; they stay in the table so
rows written before they were retired still show their name.

## Administration

| Say this | Code |
|---|---|
| Account created | `account.create` |
| Account peer inactivity expiration disabled | `account.peer.inactivity.expiration.disable` |
| Account peer inactivity expiration enabled | `account.peer.inactivity.expiration.enable` |
| Account peer inactivity expiration duration updated | `account.peer.inactivity.expiration.update` |
| Account clientless access disabled | `account.setting.clientless.access.disable` |
| Account clientless access enabled | `account.setting.clientless.access.enable` |
| Account clientless proxy address updated | `account.setting.clientless.proxy.address.update` |
| Account peer approval disabled | `account.setting.peer.approval.disable` |
| Account peer approval enabled | `account.setting.peer.approval.enable` |
| Account peer login expiration disabled | `account.setting.peer.login.expiration.disable` |
| Account peer login expiration enabled | `account.setting.peer.login.expiration.enable` |
| Account peer login expiration duration updated | `account.setting.peer.login.expiration.update` |
| Account AI assistant disabled for users | `account.setting.user.ai.assistant.disable` |
| Account AI assistant enabled for users | `account.setting.user.ai.assistant.enable` |
| Account AI assistant groups updated | `account.setting.user.ai.assistant.groups.update` |
| AI provider created | `ai.provider.create` |
| AI provider deleted | `ai.provider.delete` |
| AI provider updated | `ai.provider.update` |
| AI provider verified | `ai.provider.verify` |
| Dashboard login | `dashboard.login` |
| Group added to disabled management DNS setting | `dns.setting.disabled.management.group.add` |
| Group removed from disabled management DNS setting | `dns.setting.disabled.management.group.delete` |
| Filter created | `filter.created` |
| Filter deleted | `filter.deleted` |
| Filter updated | `filter.updated` |
| Limit created | `gateway_limit.created` |
| Limit deleted | `gateway_limit.deleted` |
| Limit updated | `gateway_limit.updated` |
| MCP server added | `gateway_mcp_server.created` |
| MCP server deleted | `gateway_mcp_server.deleted` |
| MCP server updated | `gateway_mcp_server.updated` |
| Provider created | `gateway_provider.created` |
| Provider deleted | `gateway_provider.deleted` |
| Provider updated | `gateway_provider.updated` |
| MCP bundle created | `gateway_virtual_mcp.created` |
| MCP bundle deleted | `gateway_virtual_mcp.deleted` |
| MCP bundle updated | `gateway_virtual_mcp.updated` |
| Group created | `group.add` |
| Group deleted | `group.delete` |
| Group issuer changed | `group.issuer.update` (*history only*) |
| Group updated | `group.update` |
| Guardrail created | `guardrail.created` |
| Guardrail deleted | `guardrail.deleted` |
| Guardrail updated | `guardrail.updated` |
| Integration created | `integration.create` |
| Integration deleted | `integration.delete` |
| Integration disabled | `integration.disabled` |
| Integration updated | `integration.update` |
| Nameserver group created | `nameserver.group.add` |
| Nameserver group deleted | `nameserver.group.delete` |
| Nameserver group updated | `nameserver.group.update` |
| Peer approval revoked | `peer.approval.revoke` |
| Peer approved | `peer.approve` |
| Group added to peer | `peer.group.add` |
| Group removed from peer | `peer.group.delete` |
| Peer inactivity expiration disabled | `peer.inactivity.expiration.disable` |
| Peer inactivity expiration enabled | `peer.inactivity.expiration.enable` |
| Peer login expiration disabled | `peer.login.expiration.disable` |
| Peer login expiration enabled | `peer.login.expiration.enable` |
| Peer login expired | `peer.login.expire` |
| Peer renamed | `peer.rename` |
| Peer SSH server disabled | `peer.ssh.disable` |
| Peer SSH server enabled | `peer.ssh.enable` |
| Personal access token created | `personal.access.token.create` |
| Personal access token deleted | `personal.access.token.delete` |
| Network Policy added | `policy.add` |
| Network Policy deleted | `policy.delete` |
| Network Policy updated | `policy.update` |
| Posture check created | `posture.check.created` |
| Posture check deleted | `posture.check.deleted` |
| Posture check updated | `posture.check.updated` |
| Profile created | `profile.created` |
| Profile removed | `profile.removed` |
| Profile updated | `profile.updated` |
| Application published | `published_app.created` |
| Application unpublished | `published_app.removed` |
| Published application updated | `published_app.updated` |
| Activity report created | `report.activity.created` |
| Activity report deleted | `report.activity.deleted` |
| Authentication report created | `report.authentication.created` |
| Authentication report deleted | `report.authentication.deleted` |
| Route created | `route.add` |
| Route deleted | `route.delete` |
| Route updated | `route.update` |
| Rule added | `rule.add` (*history only*) |
| Rule deleted | `rule.delete` (*history only*) |
| Rule updated | `rule.update` (*history only*) |
| Service user created | `service.user.create` |
| Service user deleted | `service.user.delete` |
| Setup key created | `setupkey.add` |
| Setup key deleted | `setupkey.deleted` |
| Group added to setup key | `setupkey.group.add` |
| Group removed from user setup key | `setupkey.group.delete` |
| Setup key overused | `setupkey.overuse` |
| Peer added | `setupkey.peer.add` |
| Setup key revoked | `setupkey.revoke` |
| Setup key updated | `setupkey.update` |
| Subscription updated | `subscription.updated` |
| Support session created | `support.session.create` |
| Tenant updated | `tenant.updated` |
| Transferred owner role | `transferred.owner.role` |
| User blocked | `user.block` |
| User deleted | `user.delete` |
| Group added to user | `user.group.add` |
| Group removed from user | `user.group.delete` |
| User invited | `user.invite` |
| User joined | `user.join` |
| Peer added | `user.peer.add` |
| Peer deleted | `user.peer.delete` |
| User logged in peer | `user.peer.login` |
| User role updated | `user.role.update` |
| User unblocked | `user.unblock` |

## Access Control

| Say this | Code |
|---|---|
| Accessed URL | `browser.url.access` |
| Credential refused at gateway | `gateway.credential_refused` |
| MCP server connected | `mcp.connected` |
| MCP server disconnected | `mcp.disconnected` |
| MCP server needs a new sign-in | `mcp.reauth_required` |
| Peer access blocked | `peer.access.blocked` |
| Peer access granted | `peer.access.granted` |
| Target access granted | `peer.access.target` |
| Target access blocked | `peer.access.target.blocked` |
| Application access allowed | `published_app.access_allowed` |
| Application access denied: not admitted | `published_app.access_not_admitted` |
| Session recorded | `session.recorded` |
| User logged in | `user.login` |
| User logged out | `user.logout` |
| Application started | `workspace.app.started` |

## Policy Violation

| Say this | Code |
|---|---|
| View source code | `browser.data.code.redacted` |
| Download blocked | `browser.download.file` |
| Protection paused | `browser.exception.request` |
| Enterprise workspace required | `browser.isolation.bluezone.required` |
| Local browser isolation required | `browser.isolation.local.required` |
| Disposable browser required | `browser.isolation.redzone.required` |
| Remote browser isolation required | `browser.isolation.remote.required` |
| URL posture check failed | `browser.posture.check` |
| Upload blocked | `browser.upload.file` |
| Blocked URL | `browser.url.blocked` |
| Application access denied by posture | `published_app.access_denied` |
| Posture check failed | `workspace.posture.check` |

The browser events below (`browser.download.file`, `browser.upload.file`,
`browser.url.blocked`, `browser.data.clipboard.blocked`, `browser.data.print.blocked`,
`browser.data.redacted`) come from the Netzilo browser extension and also from a published
application's restrictions. The latter carry `source: gateway`, `application`, `domain`
and `peer` = the browser as signed in (*Chrome 130 on macOS 15.1*); say *on <url> from
<browser>* for them (`44-published-applications.md` §4.2).

## Data Exfiltration

| Say this | Code |
|---|---|
| Classified data found | `browser.data.classified` |
| Copy/Paste blocked | `browser.data.clipboard.blocked` |
| Upload source code | `browser.data.code.upload.blocked` |
| Printing blocked | `browser.data.print.blocked` |
| Sensitive data redacted | `browser.data.redacted` |
| Screenshot blocked | `browser.data.screenshot.blocked` |
| Download content blocked | `browser.download.content` |
| Printing blocked | `workspace.print.blocked` |

## Suspicious

| Say this | Code |
|---|---|
| Prompt injection blocked | `browser.data.prompt.injection.blocked` |
| User failed login | `user.failedlogin` (meta `error_type` = `expired`, `revoked`, `over_used` or `key_not_found`, plus `reason`, `setup_key_name`, `usage_limit`, `used_times`; `13-log-interpretation.md` §4.8) |
| Code injection detected | `workspace.injection.detected` |
| Self-defense activated | `workspace.selfdefense.activated` |

## Investigation

| Say this | Code |
|---|---|
| AI Insight | `ai.insight` |

## AI Edge

| Say this | Code |
|---|---|
| AI allowed | `ai.allowed` (no longer recorded: allowed calls are in AI sessions; the server drops the event from older hosts, and older rows remain until they age out) |
| AI blocked | `ai.blocked` |
| AI content reported | `ai.content` (the captured messages of recorded model and tool calls on their way to the AI sessions; never shown in Activity) |
| Response action applied | `ai.control.created` (an administrator isolated or inspected AI activity; meta `effect` (`kill` = isolation, `probation` = inspection), `reason`, `scope`, `origin`, `expires_at`; `51-ai-response-actions.md` §4) |
| Response action deleted | `ai.control.deleted` (an administrator deleted a response action; it stops applying at once) |
| Response action lifted | `ai.control.lifted` (an administrator lifted a response action; meta `lift_reason` when one was given) |
| Response action applied by a guardrail | `ai.control.raised` (Netzilo isolated or inspected one AI session on its own, by the guardrail named in `origin` (`rule:<rule id>`); initiator Netzilo System; expires after 7 days unless lifted; `51-ai-response-actions.md` §2) |
| Response action updated | `ai.control.updated` (an administrator changed a response action's effect, scope, reason or expiry) |
| Response actions reported | `ai.controls.report` (a host's report of the response actions it applied; consumed by the server, never shown in Activity) |
| AI detected | `ai.detected` |
| AI redacted | `ai.redacted` |
| AI redirected | `ai.redirected` |
| AI session deleted | `ai.session.deleted` (an administrator deleted an AI session and everything it recorded; meta `session`, `agent`, `user`, `started_at`, `last_activity` and the counts removed) |
| AI usage reported | `ai.usage` (a device's or gateway's recorded model and tool calls on their way to the AI sessions; never shown in Activity) |
| AI behavior graph updated | `aidr.graph` (a device's behaviour data on its way to the graph, never stored as an entry; shown as "Session snapshot" only for a browser tab session's first behaviour (and on older device rows), with a session id that opens its graph) |
| Session trajectory available | `aidr.trajectory` (no longer created by current servers; rows an older server recorded — one per AI session, meta `session_id`, `agent_name`, `peer`, `point` — still open the session in the Agentic Activity window; `30-activity-reports-and-integrations.md` §3) |
| Semantic event | `semantic.event` (no longer recorded: behaviour observations are in the behaviour graph; the server drops the event from older hosts, and older rows remain until they age out) |

