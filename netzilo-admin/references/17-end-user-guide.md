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
