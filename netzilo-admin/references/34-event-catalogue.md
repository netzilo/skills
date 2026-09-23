---
id: '34'
title: Event catalogue — what each activity is called
requires: []
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 8294
sections:
- id: administration
  title: Administration
  chars: 5065
- id: access-control
  title: Access Control
  chars: 454
- id: policy-violation
  title: Policy Violation
  chars: 689
- id: data-exfiltration
  title: Data Exfiltration
  chars: 496
- id: suspicious
  title: Suspicious
  chars: 454
- id: investigation
  title: Investigation
  chars: 79
- id: ai-edge
  title: AI Edge
  chars: 335
---
# Event catalogue — what each activity is called

Generated from Netzilo Server's activity table on 2026-09-23 by
`scripts/gen-event-codes.py`. 137 activities.

Every event the API returns carries all three columns: `activity` (the display
name), `activity_code` (the stable identifier) and `activity_category`. **Say the
display name.** The code is a filter value and a machine identifier — put it in a
`GET /api/events/paginated?code=…` call, not in a sentence to an admin, unless they
asked for it or you are telling them what to search for themselves.

Codes are also the vocabulary of `references/32-detection-rule-authoring.md` and the
Activity page filters in `references/30-activity-reports-and-integrations.md`.

## Administration

| Say this | Code |
|---|---|
| Account created | `account.create` |
| Account peer inactivity expiration disabled | `account.peer.inactivity.expiration.disable` |
| Account peer inactivity expiration enabled | `account.peer.inactivity.expiration.enable` |
| Account peer inactivity expiration duration updated | `account.peer.inactivity.expiration.update` |
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
| Group created | `group.add` |
| Group deleted | `group.delete` |
| Group issuer changed | `group.issuer.update` |
| Group updated | `group.update` |
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
| Activity report created | `report.activity.created` |
| Activity report deleted | `report.activity.deleted` |
| Authentication report created | `report.authentication.created` |
| Authentication report deleted | `report.authentication.deleted` |
| Route created | `route.add` |
| Route deleted | `route.delete` |
| Route updated | `route.update` |
| Rule added | `rule.add` |
| Rule deleted | `rule.delete` |
| Rule updated | `rule.update` |
| Scanner created | `scanner.created` |
| Scanner deleted | `scanner.deleted` |
| Scanner updated | `scanner.updated` |
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
| Tool created | `tool.created` |
| Tool deleted | `tool.deleted` |
| Tool updated | `tool.updated` |
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
| Peer access blocked | `peer.access.blocked` |
| Peer access granted | `peer.access.granted` |
| Target access granted | `peer.access.target` |
| Target access blocked | `peer.access.target.blocked` |
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
| Posture check failed | `workspace.posture.check` |

## Data Exfiltration

| Say this | Code |
|---|---|
| Classified data found | `browser.data.classified` |
| Copy/Paste blocked | `browser.data.clipboard.blocked` |
| Upload source code | `browser.data.code.upload.blocked` |
| Printing blocked | `browser.data.print.blocked` |
| Sensitive data redacted | `browser.data.redacted` |
| Screeshot blocked | `browser.data.screenshot.blocked` |
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
| AI behavior graph updated | `aidr.graph` |
| Semantic event | `semantic.event` |
| Tool allowed | `tool.allowed` |
| Tool blocked | `tool.blocked` |
| Tool detected | `tool.detected` |
| Discovered tool blocked | `tool.explicitly_blocked` |
| Discovered tool approved | `tool.sanctioned` |

