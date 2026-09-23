---
id: '17'
title: The End-User Guide — What to Give Employees
requires: []
executable_on:
- dashboard-assistant
- netzilo-harness
- human-operator
chars: 9057
sections:
- id: '1'
  title: Tell people before you install, not after
  chars: 845
- id: '2'
  title: The page to publish
  chars: 3412
- id: '3'
  title: Translating what the employee says
  chars: 3399
- id: '4'
  title: What to tell an employee who asks what is monitored
  chars: 808
---
# The End-User Guide — What to Give Employees

**Use this when the admin needs something to hand to their people.** Every file in this
skill set addresses the administrator. This one addresses the person whose laptop it is.
Most tickets that reach an admin are questions an employee could have answered in thirty
seconds with the right page in front of them.

Two ways to use it. Give the admin §2 to publish in their own help system, adapting the
names. Use §3 yourself when an admin relays an employee's complaint, because it maps what
the employee said to what is actually happening.

---

## 1. Tell people before you install, not after

Send this before the first device is enrolled. Silence generates more tickets than any
technical fault.

Cover four things, briefly:

1. **What it is.** A secure connection to company systems that replaces or supplements
   the old VPN.
2. **What changes for them.** Usually nothing visible. They sign in once and it runs.
3. **What is monitored.** Be honest and specific. Their ordinary web browsing and
   personal traffic are not inspected. Connections to company systems, and AI assistant
   usage where that is in scope, are recorded. If session recording is enabled anywhere,
   say so explicitly.
4. **Where to get help.** One link, one address.

Point four matters more than the other three. People who discover monitoring after the
fact escalate; people told in advance rarely do.

---

## 2. The page to publish

Adapt the product and contact names to the customer's own.

### Netzilo on your device

Netzilo connects your device securely to company systems. Once you have signed in it runs
in the background and you should not need to think about it.

**Signing in.** Open the Netzilo app and sign in with your work account. On a Mac the
first launch asks you to approve the app in System Settings. There are **three separate
approvals** and all of them are needed: a network extension, a security extension, and
Full Disk Access for the security monitor. If you approve only the first, the app appears
to work but protection is not active.

**Checking it is working.** The app shows Connected when everything is in order. If it
shows anything else, try the four steps below.

**When something does not work**

1. **Check you are online.** Open any public website first. If the internet is down,
   nothing else matters.
2. **If you are on hotel, airport or café wifi**, open a browser and complete the network's
   sign-in page first. Netzilo cannot connect through an unfinished captive portal.
3. **Check your clock.** A device with the wrong date or time cannot establish secure
   connections. Set it to update automatically.
4. **Restart the app.** Quit it fully and reopen it. If asked to sign in again, do.

If those four do not help, contact support and include: what you were trying to reach,
what the app shows, whether other websites work, and roughly when it started.

**Things that are normal and do not need a ticket**

- The app briefly disconnecting and reconnecting when you change wifi, dock, or wake the
  laptop.
- Being asked to sign in again periodically. This is a security setting, not a fault.
- A slight delay on the first connection after waking.

**Things to report straight away**

- You are asked for your password by something that does not look like the normal
  company sign-in page.
- You lose access to something you had yesterday and nothing changed on your side.
- Your device is lost or stolen. Report this immediately, not tomorrow.

**Your own portal.** You can see the applications, devices and tools available to you,
and manage your own profile, from the web portal your administrator will link. It shows
your devices and their connection quality. You can use it to check whether a device is
connected without asking anyone.

**If your company uses the Netzilo Workspace (Windows only).** Some applications may
be set up to open inside a protected workspace. You start them from the shortcuts folder
on your Desktop and in the Start menu, not from their usual icons. A few things are
normal there: the windows may carry a watermark or a coloured border; copying text out of
or pasting into them may be blocked; they may not show up in screen shares; and if the
windows go **blurry**, a security check on your device is failing (a screen lock or disk
encryption that is off, an out-of-date antivirus) — fix that and they clear on their own.
If you see "**Your workspace will be restarted in N seconds**", your administrator
changed a setting; save your work. Do not keep your own files in the shortcuts folder —
it is rebuilt whenever your settings update. The Workspace exists only on 64-bit Windows
with the standard company install; on Mac, Linux or an ARM laptop these applications
work as before or the web page is blocked, which is expected.

---

## 3. Translating what the employee says

When an admin forwards a complaint, this maps it to a cause and the file that fixes it.

| What the employee says | What is usually happening | Where to look |
|---|---|---|
| "The VPN keeps dropping" | Normal reconnect on network change. Only a fault if it fails to reconnect | `13-log-interpretation.md` §4.4 |
| "It says connected but I can't reach the server" | Policy, route or posture, not connectivity | `11-connectivity-diagnosis.md` |
| "It stopped working after I got back from the office" | Network change, captive portal, or clock drift | §2 steps 2 and 3 |
| "It asks me to log in all the time" | Login expiration setting, working as configured | `24-peers-and-setup-keys.md` |
| "It worked yesterday and now it doesn't" | A policy, group or posture check changed. Check Activity first | `20-policies-access-control.md`, `15-incident-response-and-recovery.md` §6.2 |
| "My AI assistant stopped working" | Inspection, a blocked rule, or certificate trust | `10-ai-security-aidr.md` |
| "Everything is slow since this was installed" | Relayed connection, or an inspection rule doing too much work | `11-connectivity-diagnosis.md`, `10-ai-security-aidr.md` |
| "I got a scary red button on the dashboard" | The admin's system status widget | `16-onboarding-and-rollout.md` §0 |
| "I can't see the page my colleague sees" | Role, not a fault. Most pages are admin-only | `25-users-groups-and-account-settings.md` |
| "I was told to approve something on my Mac and I clicked no" | Extension approval declined; features silently inactive | `07-client-troubleshooting.md` |
| "My work apps went blurry" | A workspace posture check is failing on the device (screen lock, disk encryption, antivirus…). The apps keep running; the blur clears when the check passes | `26-profiles-secure-workplace.md` §9 (blurred windows row), `21-posture-checks.md` |
| "It says my workspace will restart in N seconds" | The admin saved a change to the workspace profile. Expected; save work and let it restart | `26-profiles-secure-workplace.md` §2 "Changing a live workspace", §9 |
| "I can't paste into / copy out of the app" | Restrict Clipboard Access in the workspace profile (to / from / both), working as configured | `26-profiles-secure-workplace.md` §2, §9 |
| "My screen share shows nothing where the app is" | Restrict Screen Sharing in the workspace profile | `26-profiles-secure-workplace.md` §2, §9 |
| "The shortcut folder is missing" / "there's nothing in it" | No folder name in the profile, the application is not installed at the configured path, the service started before they signed in, or the workspace failed to create. Not available at all on Mac, Linux, ARM or a non-admin install | `26-profiles-secure-workplace.md` §9 (shortcuts and never-created rows) |
| "The apps in the workspace have no internet" / "it just says Initializing Netzilo" | The workspace's own network identity (its setup key) is spent, expired or revoked, or its peer has no policy to the destination — the host being online proves nothing about the workspace peer | `26-profiles-secure-workplace.md` §9 first row, `24-peers-and-setup-keys.md` |
| "The app closes as soon as I open it" (recording enabled) | Recording consent was declined or the recording storage is not configured; the workspace closes when it cannot record | `26-profiles-secure-workplace.md` §9 |

---

## 4. What to tell an employee who asks what is monitored

Answer honestly and specifically. Vague answers create escalation.

What the company can see: which devices exist and their security posture, which internal
systems were reached and when, all administrative changes, and AI assistant activity
where it is in scope, including the content that triggers a security rule.

What it cannot see: the contents of ordinary encrypted traffic between the device and
company systems, and personal browsing outside the scope of the inspection rules.

The full detail, including every device attribute collected, is in
`14-data-handling-and-privacy.md`. Give employees the summary and give their
representatives the detail if asked. Do not improvise an answer that is narrower than
what the product actually does.
