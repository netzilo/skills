---
id: '52'
title: Database encryption on a self-hosted Netzilo Server
requires:
- server-shell
executable_on:
- netzilo-harness
- human-operator
chars: 34809
sections:
- id: '1'
  title: What it protects, and what it does not
  chars: 2205
- id: '2'
  title: How it works
  chars: 1998
- id: '3'
  title: Choose a key store
  chars: 1023
- id: '4'
  title: Before you turn it on
  chars: 1275
- id: '5'
  title: Set up the key store
  chars: 8294
- id: '6'
  title: Turn it on
  chars: 7782
- id: '7'
  title: Check it
  chars: 1100
- id: '8'
  title: Day-2 operations
  chars: 4664
- id: '9'
  title: Troubleshooting
  chars: 4632
- id: '10'
  title: Security notes
  chars: 925
---
# Database encryption on a self-hosted Netzilo Server

Netzilo Server can encrypt the sensitive columns of its management database with a key
held in a key store the customer controls: HashiCorp Vault, AWS KMS, Azure Key Vault, or
a key in the configuration file. A copy of the database (a dump, a backup, a replica, a
disk snapshot) then holds ciphertext for those columns, and reading it needs the key store
as well. This file is the one place that says what it protects, how to set up each key
store, how to turn it on for every install type (on-prem one-liner, AWS image, Azure image,
Kubernetes), how to keep it on through updates, and how to operate and troubleshoot it.

It is **off unless the configuration turns it on**. Nothing turns it on by itself, and an
update never does.

Layout facts used below (`$C`, service names, restarts, the backup gate) are in
`02-server-operations.md` §1–§3 and §6.3.

## 1. What it protects, and what it does not

**Protects against:** anyone who gets the management database without the key store: a
leaked or stolen dump or backup, a database replica, a disk or volume snapshot, a
database administrator who is not a Netzilo administrator.

**Does not protect against:** someone who controls the running server (the `management`
container, or the host with `management.json` and the key store access the server has).
The server needs to read these values to work, and it does. The REST API and the dashboard
show them exactly as before (masked where they were masked).

What is encrypted:

| Data | Where it appears in the product |
|---|---|
| Setup keys, and the setup key each peer enrolled with | Endpoint → Setup Keys, peers |
| Personal access tokens and service-user tokens | Team → Users/Agents → tokens |
| AI Gateway provider credentials | Edge → Providers |
| MCP server environment, headers and OAuth settings; users' MCP sign-ins and header values | Edge → Providers → MCP Servers |
| AI provider API keys | Integrations → Artificial Intelligence |
| Event streaming and integration settings (their secrets) | Integrations |
| Profile components (Workspace and browser encryption keys, enrollment keys) | Endpoint → Profiles |
| AI chat messages and AI session event content | Edge → Sessions |
| The activity log's initiator name, initiator email and details | Activity → Events |
| AI Assistant conversations, summaries, answers and steps | the dashboard Assistant |

What stays readable in the database, by design: object names and ids, peers and their
addresses, groups, policies, routes, timestamps, the event type of each activity, and the
AI facts used for counting (agent, rule, model, server, tool, source, surface; the AI
session tables already hold these openly). Event search keeps working: keyword search uses
keyed tokens of the words (a dump shows tokens, not words), and filtering by user works.

The identity provider's database (`zitadel`) is not part of this; it is encrypted with its
own `ZITADEL_MASTERKEY` (`02-server-operations.md` §1). `DataStoreEncryptionKey` in
`management.json` is unrelated to this feature and encrypts nothing.

## 2. How it works

- **Two keys.** A random 256-bit *data key* encrypts the columns. The key store's key (the
  *key encryption key*) wraps the data key, and only the wrapped form is stored, in the
  table `encryption_keys` of the same database. The key store's key never leaves the key
  store.
- **The key store is used at start, not per request.** Management unwraps the data key once
  when it starts and keeps it in memory. A key store outage does not affect a running
  server; it stops the **next start**. Management retries an unreachable key store for
  about 30 seconds, then exits (the container restarts and tries again). A definite refusal
  (permission denied, key disabled or deleted) is not retried.
- **Two value formats.** Most columns use AES-256-GCM with a fresh nonce per value (long
  text is compressed first, so the event and chat tables usually get smaller). The few
  columns the server looks values up by (setup key, token hash, event initiator email) use
  deterministic AES-SIV: equal values give equal ciphertext, which a dump reveals, and
  nothing else. Every value is bound to its table and column, so a value copied into
  another column does not decrypt.
- **Turning it on encrypts existing data.** At the first start with encryption on,
  management encrypts the small tables (setup keys, tokens, credentials, peers, profiles)
  before it serves, in seconds, then the large ones (events, AI messages, Assistant
  history) in the background while it serves, at roughly a thousand rows a second. Readers
  accept both forms until the pass finishes. Progress is kept, so a restart continues where
  it stopped.
- **Redis.** Management's cache entries that carry stored objects are encrypted with the
  same key; a cached value it cannot read counts as a cache miss and is reloaded from the
  database. Nothing to do on the Redis side.
- **Cost.** Measured request latency and CPU with encryption on stayed within run-to-run
  noise of the same server without it.

## 3. Choose a key store

| Key store | `Provider` | Use it when | Credentials management uses |
|---|---|---|---|
| HashiCorp Vault (transit engine) | `vault` | on-prem, or any site that runs Vault | a Vault token, an AppRole, or Kubernetes auth |
| AWS KMS | `awskms` | the AWS Marketplace image, or any server with AWS access | the EC2 instance role (or IRSA, or AWS credentials in the environment) |
| Azure Key Vault | `azurekeyvault` | the Azure Marketplace image, or any server with Azure access | the VM's managed identity (or workload identity, or a service principal in the environment) |
| Local key | `local` | tests, or when nothing above is available | a base64 key in `management.json` |

`local` is the weakest: the key sits in `management.json`. It protects a database dump only
as long as that dump is never stored with `management.json`. The installer's backup
(`02-server-operations.md` §6.2) copies both into one folder, so with `local` keep the key
out of that backup and store it separately (§8.1).

## 4. Before you turn it on

1. **Pass the backup gate** (`02-server-operations.md` §6.3). Turning encryption on rewrites
   rows; a backup taken before is your way back.
2. **Check that the running management supports it:**

   ```bash
   cd "$C" && sudo docker compose exec -T management /go/bin/netzilo-mgmt encryption --help
   ```

   A list of `status`, `decrypt`, `rewrap`, `keygen` means yes. `unknown command
   "encryption"` means update management first (§6.2), then come back.
3. **Store engine.** The bundled and external PostgreSQL, SQLite and the Redis-cached
   store are supported. The legacy JSON file store is not (management refuses to start
   with `EncryptionConfig.Mode on needs the sqlite, postgres or redis store engine`).
4. **Agree the two rules with the customer:**
   - the key store must be reachable from the server **at every start**;
   - losing the key store's key (deleted, purged, or an old version disabled) makes the
     encrypted columns unreadable for good, in the database **and in every backup**.
     Turn on the key store's own deletion protection (each subsection of §5 says how).
5. **Every management instance** of the database gets the same `EncryptionConfig`
   (several instances only on Kubernetes or custom deployments).

## 5. Set up the key store

Do these steps from a workstation or the server with the key store's admin tools. The
result of each subsection is an `EncryptionConfig` block for §6.

### 5.1 HashiCorp Vault

```bash
export VAULT_ADDR=https://vault.example.com:8200
vault secrets enable transit                               # once per Vault
vault write -f transit/keys/netzilo-management             # the key; aes256-gcm96 by default

vault policy write netzilo-management - <<'EOF'
path "transit/encrypt/netzilo-management" { capabilities = ["update"] }
path "transit/decrypt/netzilo-management" { capabilities = ["update"] }
EOF
```

Then one way to authenticate:

| Method | Create it | `Vault` fields |
|---|---|---|
| Periodic token (simplest) | `vault token create -orphan -policy=netzilo-management -period=768h` | `Token` |
| AppRole | `vault auth enable approle`; `vault write auth/approle/role/netzilo-management token_policies=netzilo-management token_ttl=1h token_max_ttl=24h`; read `role-id`, write `secret-id` | `RoleID`, `SecretID` |
| Kubernetes (management on Kubernetes) | `vault write auth/kubernetes/role/netzilo-management bound_service_account_names=<sa> bound_service_account_namespaces=<ns> policies=netzilo-management ttl=1h` | `KubernetesRole` (and `KubernetesJWTPath` if the token is not at the default path) |

Management renews a configured token every 15 minutes (the token's default policy allows
it), and logs in again with AppRole or Kubernetes when a token expires.

```json
"EncryptionConfig": {
  "Mode": "on",
  "Provider": "vault",
  "Vault": {
    "Address": "https://vault.example.com:8200",
    "Token": "<token>",
    "Mount": "transit",
    "KeyName": "netzilo-management"
  }
}
```

| Field | Default | Notes |
|---|---|---|
| `Address` | — (required) | must be reachable **from the management container**; `127.0.0.1` there is the container itself, not the host |
| `Token` / `RoleID` + `SecretID` / `KubernetesRole` | — (one is required) | |
| `Mount` | `transit` | the transit engine's mount path |
| `KeyName` | `netzilo-management` | |
| `Namespace` | — | Vault Enterprise namespace |
| `CACert` | — | path **inside the container** of a PEM file to trust for `Address` (mount it, §6.1 step 4) |

Deletion protection: keep the key's `deletion_allowed` false (the default) and never lower
its `min_decryption_version` below the version that wrapped the stored key. Vault's own
data must be backed up like any Vault: losing it loses the key.

### 5.2 AWS KMS

Create a symmetric key and an alias:

```bash
aws kms create-key --description "Netzilo Server database encryption" \
  --key-usage ENCRYPT_DECRYPT --key-spec SYMMETRIC_DEFAULT --query KeyMetadata.Arn --output text
aws kms create-alias --alias-name alias/netzilo-management --target-key-id <key-arn>
aws kms enable-key-rotation --key-id <key-arn>              # optional; transparent to management
```

Allow the server's identity to use it. On the **AWS Marketplace image** that is the
instance role the stack created; add an inline policy to it:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["kms:Encrypt", "kms:Decrypt"],
    "Resource": "<key-arn>",
    "Condition": { "StringEquals": { "kms:EncryptionContext:netzilo": "netzilo-management-dek" } }
  }]
}
```

The condition is optional; management always sends that encryption context, so it limits
the role to this use of the key.

**Containers and the instance role.** Management runs in a container, one network hop
further from the instance metadata service than the host. With IMDSv2 required (the AWS
image requires it), the metadata hop limit must be at least 2 or the container gets no
credentials:

```bash
aws ec2 modify-instance-metadata-options --instance-id <instance-id> \
  --http-tokens required --http-endpoint enabled --http-put-response-hop-limit 2
```

```json
"EncryptionConfig": {
  "Mode": "on",
  "Provider": "awskms",
  "AWSKMS": { "Region": "us-east-1", "KeyID": "alias/netzilo-management" }
}
```

| Field | Notes |
|---|---|
| `Region` | set it: the AWS SDK used does not take the region from the instance |
| `KeyID` | key id, key ARN, alias name (`alias/…`) or alias ARN |
| `Endpoint` | optional: a VPC endpoint or FIPS endpoint URL |

Off AWS (on-prem host with AWS credentials), put `AWS_ACCESS_KEY_ID` and
`AWS_SECRET_ACCESS_KEY` of an IAM user limited to the policy above in the management
service's environment (§6.1 step 4). On Kubernetes use IRSA (§6.3).

Deletion protection: never schedule the key for deletion; KMS enforces a waiting period of
7–30 days during which `aws kms cancel-key-deletion` undoes it. Disabling the key stops
every start of management until it is enabled again.

### 5.3 Azure Key Vault

Create a vault with role-based access and purge protection, and an RSA key that may only
wrap and unwrap:

```bash
az keyvault create -g <resource-group> -n <vault-name> -l <region> --sku premium \
  --enable-rbac-authorization true --enable-purge-protection true --retention-days 90
az keyvault key create --vault-name <vault-name> -n netzilo-management \
  --kty RSA-HSM --size 3072 --ops wrapKey unwrapKey          # --kty RSA on the standard SKU
az lock create -n netzilo-key-no-delete --lock-type CanNotDelete \
  --resource "$(az keyvault show -g <resource-group> -n <vault-name> --query id -o tsv)"
```

Creating the key needs data-plane access to the vault from where `az` runs (the
"Key Vault Crypto Officer" role on the vault, and network access). Create the key before
you restrict the vault's network.

Allow the server's identity to use the key, and nothing else:

```bash
KEY_SCOPE="$(az keyvault show -g <resource-group> -n <vault-name> --query id -o tsv)/keys/netzilo-management"
az role assignment create --assignee-object-id <principal-id> --assignee-principal-type ServicePrincipal \
  --role "Key Vault Crypto Service Encryption User" --scope "$KEY_SCOPE"
```

| Server | `<principal-id>` |
|---|---|
| **Azure Marketplace image** | the VM's system-assigned managed identity, which the image deploys with: `az vm show -g <managed-resource-group> -n <vm-name> --query identity.principalId -o tsv` |
| Another Azure VM | enable a managed identity on it (`az vm identity assign`), then the same |
| Kubernetes on AKS | a user-assigned identity federated with management's service account (§6.3) |
| Off Azure | a service principal; its object id from `az ad sp show --id <app-id> --query id -o tsv` |

The role grants get, wrap and unwrap on that key. A new role assignment can take a few
minutes to apply; a start in that window fails with a 403 and the container retries.

**Network.** Management reaches the vault at `https://<vault-name>.vault.azure.net`. If you
close the vault's public access, give the server a path: a private endpoint in the
server's virtual network (with the `privatelink.vaultcore.azure.net` private DNS zone
linked to it), or a service endpoint on the server's subnet with that subnet allowed in
the vault's firewall.

```json
"EncryptionConfig": {
  "Mode": "on",
  "Provider": "azurekeyvault",
  "AzureKeyVault": { "KeyURL": "https://<vault-name>.vault.azure.net/keys/netzilo-management" }
}
```

Use the URL **without** a version: management then wraps with the newest key version and,
after a rotation, wraps the stored key again with the new version at its next start. A URL
with `/<version>` pins that version.

Management signs in with Azure's default credential chain: environment variables, workload
identity, then managed identity. Off Azure, put `AZURE_TENANT_ID`, `AZURE_CLIENT_ID` and
`AZURE_CLIENT_SECRET` (or `AZURE_CLIENT_CERTIFICATE_PATH`) of the service principal in the
management service's environment (§6.1 step 4).

Deletion protection: purge protection and the delete lock above. **Never disable or delete
an older key version** while a stored key or a backup may still be wrapped with it (§8.2).

### 5.4 Local key

```bash
cd "$C" && sudo docker compose exec -T management /go/bin/netzilo-mgmt encryption keygen
```

```json
"EncryptionConfig": {
  "Mode": "on",
  "Provider": "local",
  "Local": { "Key": "<output of keygen>" }
}
```

Keep a copy of the key somewhere other than the server and its backups (§8.1); without
it the encrypted columns cannot be read.

## 6. Turn it on

### 6.1 Compose installs: on-prem one-liner, AWS image, Azure image

All three run the same compose layout (`02-server-operations.md` §1); only `$C` differs.

1. Backup gate and support check (§4).
2. Set `$C` and keep a copy of the current file:

   ```bash
   if [ -f /opt/netzilo/run/docker-compose.yml ]; then C=/opt/netzilo/run; else C=/opt/netzilo; fi
   cd "$C" && sudo cp -a management.json "management.json.pre-encryption"
   ```

3. Add the block from §5 as a top-level key of `management.json`, keeping everything else:

   ```bash
   sudo python3 - <<'PY'
   import json
   path = "management.json"
   cfg = json.load(open(path))
   cfg["EncryptionConfig"] = {
       "Mode": "on",
       "Provider": "vault",
       "Vault": {"Address": "https://vault.example.com:8200", "Token": "<token>",
                 "Mount": "transit", "KeyName": "netzilo-management"},
   }
   with open(path, "r+") as f:            # same file, same owner and mode
       f.seek(0); f.write(json.dumps(cfg, indent=2) + "\n"); f.truncate()
   PY
   sudo python3 -c 'import json; print(json.load(open("management.json"))["EncryptionConfig"]["Provider"])'
   ```

4. Only if the key store needs something outside `management.json` (cloud credentials off
   their cloud, a CA file for Vault), add it to the `management` service in
   `docker-compose.yml`:

   ```yaml
     management:
       environment:
         # … the existing lines stay …
         - AZURE_TENANT_ID=<tenant-id>
         - AZURE_CLIENT_ID=<app-id>
         - AZURE_CLIENT_SECRET=<secret>
       volumes:
         # … the existing lines stay …
         - ./vault-ca.pem:/etc/netzilo/vault-ca.pem:ro    # then "CACert": "/etc/netzilo/vault-ca.pem"
   ```

   `sudo docker compose config -q` must print nothing.
5. Recreate management (the control plane is unavailable for the seconds this takes;
   connected peers keep their tunnels):

   ```bash
   sudo docker compose up -d --force-recreate management
   sudo docker compose logs -f management | grep -m 3 -i "database encryption"
   ```

   Expected, in order:

   ```text
   database encryption: created data encryption key <id>, wrapped by <provider>
   database encryption on: key <id> wrapped by <provider> (<key reference>), 0 retired key(s) readable
   database encryption: encrypting setup_keys done, <n> rows in <time>
   ```

   followed by one `encrypting <table> done` line per table; `events` and `ai_messages`
   come last and can take minutes. A start that fails shows
   `failed creating Store: … database encryption: …` and the container restarts; see §9,
   and to back out restore `management.json.pre-encryption` and recreate management again
   (nothing was encrypted if no key was created).
6. Check it (§7) and run the health gates (`02-server-operations.md` §2.1).

### 6.2 Servers installed before encryption existed, and every later update

**Update first, then turn it on.** Encryption needs a management release that has it.
Update management the usual way for the install type, with encryption still off:

| Install | Update |
|---|---|
| On-prem one-liner | `02-server-operations.md` §4.10 (`update management`, or the whole server) |
| AWS / Azure image | `02-server-operations.md` §4.5 (change the management image reference, recreate, pin) |
| Kubernetes / custom | roll out the new management image |

Confirm with the support check (§4 step 2), then follow §6.1.

**Updates keep it on.** The one-liner's upgrade and `update` commands rewrite
`management.json` by reading it and writing it back with every key, so the
`EncryptionConfig` block stays; the marketplace procedure changes only image references.
After **every** update, before calling it done:

```bash
cd "$C"
sudo python3 -c 'import json; print(json.load(open("management.json")).get("EncryptionConfig", {}).get("Mode"))'   # on
sudo docker compose config | grep -E "AZURE_|AWS_|NETZILO_ENCRYPTION_" | sed 's/=.*/=…/'   # the variables you added, if any
sudo docker compose logs --since 10m management | grep "database encryption on:"
```

Things an update must not do, and how to recover if one did:

| Event | Result | Fix |
|---|---|---|
| `management.json` replaced by one without the block | management refuses to start: `the database holds encrypted values but EncryptionConfig.Mode is off` | put the block back (`management.json.pre-encryption` or the backup), recreate |
| Management rolled back to a release without encryption | encrypted columns are unreadable to it | roll forward again; to go back for good, `decrypt` first with the newer release (§8.4) |
| The installer re-run as a fresh install | destroys the server (`02-server-operations.md` §10) | restore (§8.1) |
| Variables added in step 4 lost | start fails to reach the key store | add them again, recreate |

### 6.3 Kubernetes and other orchestrators

- **Configuration.** Mount `management.json` (from a Secret) with the block, or set the
  `NETZILO_ENCRYPTION_*` variables of §6.4 on the container. The file and the variables
  combine; a variable wins.
- **Identity without secrets.**
  - AKS: workload identity. A user-assigned managed identity with a federated credential
    for `system:serviceaccount:<namespace>:<service-account>` and the role of §5.3 on the
    key; the service account annotated `azure.workload.identity/client-id: <client-id>`;
    the pod labelled `azure.workload.identity/use: "true"` and run under that service
    account.
  - EKS: IRSA. The service account annotated with an IAM role that has the policy of §5.2.
  - Vault: `KubernetesRole` (§5.1).
- **Private networking.** If the key store is reachable only privately (a Key Vault private
  endpoint, a VPC endpoint, an internal Vault), check that the cluster's DNS resolves it to
  the private address and that no NetworkPolicy blocks the egress.
- **Readiness.** Give the management container a readiness probe on its listening port
  (a TCP check is enough). Management opens the port only after the key is unwrapped, so a
  pod that cannot reach the key store never becomes ready and a rolling update keeps the
  old pod serving. Wait for the rollout in your pipeline (`helm upgrade --wait`,
  `kubectl rollout status`) so a failure is visible.
- **Turning it on in a rolling update.** Roll out the release that supports encryption first
  with encryption still off, then turn it on in a second rollout. If several instances run,
  an instance still running with encryption off stops writing secrets as soon as another
  turns it on (it logs `another instance turned encryption on`), until it is replaced.
- **Shutdown.** Give the pod a termination grace period of at least 30 seconds.

### 6.4 Environment variables

Every field can come from the environment instead of the file; a set variable overrides the
file.

| Variable | Field |
|---|---|
| `NETZILO_ENCRYPTION_MODE` | `Mode` |
| `NETZILO_ENCRYPTION_PROVIDER` | `Provider` |
| `NETZILO_ENCRYPTION_LOCAL_KEY` | `Local.Key` |
| `NETZILO_ENCRYPTION_VAULT_ADDR` | `Vault.Address` |
| `NETZILO_ENCRYPTION_VAULT_TOKEN` | `Vault.Token` |
| `NETZILO_ENCRYPTION_VAULT_ROLE_ID` | `Vault.RoleID` |
| `NETZILO_ENCRYPTION_VAULT_SECRET_ID` | `Vault.SecretID` |
| `NETZILO_ENCRYPTION_VAULT_K8S_ROLE` | `Vault.KubernetesRole` |
| `NETZILO_ENCRYPTION_VAULT_K8S_JWT_PATH` | `Vault.KubernetesJWTPath` |
| `NETZILO_ENCRYPTION_VAULT_MOUNT` | `Vault.Mount` |
| `NETZILO_ENCRYPTION_VAULT_KEY` | `Vault.KeyName` |
| `NETZILO_ENCRYPTION_VAULT_NAMESPACE` | `Vault.Namespace` |
| `NETZILO_ENCRYPTION_VAULT_CACERT` | `Vault.CACert` |
| `NETZILO_ENCRYPTION_AWS_REGION` | `AWSKMS.Region` |
| `NETZILO_ENCRYPTION_AWS_KEY_ID` | `AWSKMS.KeyID` |
| `NETZILO_ENCRYPTION_AWS_ENDPOINT` | `AWSKMS.Endpoint` |
| `NETZILO_ENCRYPTION_AZURE_KEY_URL` | `AzureKeyVault.KeyURL` |

## 7. Check it

```bash
cd "$C" && sudo docker compose exec -T management \
  /go/bin/netzilo-mgmt encryption status --count --log-file console
```

```text
configured mode: on
stored key: 3f9c… wrapped by vault (https://vault.example.com:8200/v1/transit/keys/netzilo-management), created 2026-01-15 10:00:02
PASS                         DONE  ROWS    UPDATED
enabled                      true  0       2026-01-15 10:00:02
enc:setup_keys               true  12      2026-01-15 10:00:03
…
running instances with encryption on: 1
TABLE                    PLAINTEXT ROWS  ENCRYPTED ROWS
setup_keys               0               12
…
```

| Line | Healthy |
|---|---|
| `configured mode` | `on` |
| `stored key` | the provider and key you configured |
| every `enc:<table>` | `DONE true` once the background pass has finished |
| `running instances with encryption on` | the number of management instances you run |
| `PLAINTEXT ROWS` (with `--count`) | `0` for every table once the passes are done |

`--count` scans every table; on a large event table it takes a while. Leave it out for a
quick look.

## 8. Day-2 operations

### 8.1 Backups and restore

- **Backups need no change.** A dump holds the ciphertext and the wrapped data key; the
  backup procedure (`02-server-operations.md` §6) is the same.
- **A restore needs the key store.** Restore the whole database, the same `management.json`
  (with its `EncryptionConfig`), and make sure the restored server can reach the key store
  with an identity allowed to use the key (a new VM or cluster has a new identity: grant
  it as in §5 before the first start). The key store's key, or the key version that
  wrapped the data key at the time of the backup, must still exist and be enabled.
- **Restore the whole database, not single tables.** The data key travels in
  `encryption_keys` with the data. A database whose encrypted rows came back without that
  table makes management refuse to start (§9) instead of making a new key.
- **A copy for another environment** (a staging copy of production) reads the encrypted
  columns only with access to the same key store key.
- **Local key:** the backup script copies `management.json` with the dump, which puts the
  key next to the data. Either keep the key in an environment variable or file outside
  `$C` (§6.4), or store those backups as carefully as the key.

### 8.2 Rotating the key store's key

| Key store | Rotate | What management does |
|---|---|---|
| Vault | `vault write -f transit/keys/netzilo-management/rotate` | at its next start, wraps the data key again with the newest version |
| AWS KMS | automatic rotation (§5.2) or `aws kms rotate-key-on-demand` | nothing needed; KMS keeps the old material |
| Azure Key Vault | `az keyvault key rotate` or a rotation policy | with a versionless `KeyURL`, wraps the data key again with the newest version at its next start (`key … rewrapped from azurekeyvault key version …`) |

Keep older versions usable (Vault: do not raise `min_decryption_version` past them; Azure:
do not disable them) as long as any backup you might restore was taken before the
rotation.

Rotating the key store's key does not re-encrypt the data. To replace the data key itself,
decrypt (§8.4) and turn encryption on again; that creates a new data key.

### 8.3 Moving to another key store or key: `rewrap`

Changing `Provider`, the Vault key, the KMS key or the Key Vault key in the configuration
alone makes management refuse to start (`key provider mismatch`). Move the wrapped data
key instead; the data is not touched:

```bash
cd "$C"
sudo cp -a management.json management.old.json
# edit management.json: the new EncryptionConfig (§5); keep management.old.json as it was
sudo docker compose stop management
sudo docker compose run --rm --no-deps -T \
  -v "$PWD/management.old.json:/etc/netzilo/management.old.json:ro" \
  --entrypoint /go/bin/netzilo-mgmt management \
  encryption rewrap --old-config /etc/netzilo/management.old.json --log-file console
# expect: rewrapped the key with <new provider>
sudo docker compose up -d management
```

Both key stores must be reachable from the server during the command. Keep the old key
until backups taken before the move have expired.

### 8.4 Turning it off: `decrypt`

Setting `Mode` to `off` alone makes management refuse to start while the database holds
encrypted values. Decrypt in place first:

```bash
cd "$C"
sudo docker compose stop management
sudo docker compose run --rm --no-deps -T --entrypoint /go/bin/netzilo-mgmt management \
  encryption decrypt --log-file console
# then set "Mode": "off" in management.json (or remove the block) and:
sudo docker compose up -d management
```

- The command needs the key store (the provider block must still be there) and waits up to
  two minutes for the stopped instance's last heartbeat to age out.
- While it runs, and if it is interrupted, no instance starts with encryption on. Run it
  again to finish, or `encryption decrypt --cancel` to abandon it and keep encryption on.
- `--force` decrypts although an instance reported recently (that instance stops using the
  key within 30 seconds), and retires the key even if some values did not decrypt.
- At the end the key is retired, not deleted: it stays in `encryption_keys` as a
  read-only key. Turning encryption on again later creates a new data key.

### 8.5 What never to do

- Delete or disable the key store's key, or an older version of it still in use.
- Delete or edit rows of `encryption_keys` or `encryption_progress`.
- Change the provider or key in the configuration without `rewrap` (§8.3).
- Set `Mode` to `off` without `decrypt` (§8.4).
- Restore single tables into an encrypted database, or copy rows between databases with
  different keys.

## 9. Troubleshooting

A start failure appears in `docker compose logs management` as
`failed creating Store: <data directory>: database encryption: <reason>`. A configuration
error stops management earlier, with the field named and no store line.

| Message | Cause | Fix |
|---|---|---|
| `EncryptionConfig.Mode "…": must be on or off`, `EncryptionConfig.Provider is required when Mode is on`, `EncryptionConfig.<field> is required for the <provider> provider`, `EncryptionConfig.Vault needs Token, RoleID and SecretID, or KubernetesRole` | the block is incomplete or misspelled (field names are case-sensitive as shown in §5) | correct `management.json` (or the §6.4 variable), recreate |
| `key provider <name>: … (retrying in …)`, then the container restarts | the key store is unreachable: DNS, firewall, private endpoint, proxy | from the host, `curl -sv <address>`; from inside the network the container uses, the same; fix the path |
| `the key provider denied the key: vault encrypt: 403 permission denied` | the token or role lacks the policy of §5.1 | attach the policy |
| `the key provider denied the key: vault login: 400 …` | AppRole secret id or Kubernetes role wrong or revoked | issue a new secret id, or fix the role binding |
| `x509: certificate signed by unknown authority` (Vault) | Vault's certificate is not trusted | set `CACert` to a file mounted into the container |
| `the key provider denied the key: AWS KMS …: … is not authorized to perform: kms:Decrypt` (or `kms:Encrypt`) | the role lacks the policy, or the encryption-context condition does not match | fix the policy of §5.2 |
| `NoCredentialProviders` or `EC2RoleRequestError` (AWS) | the container gets no instance credentials | metadata hop limit 2 (§5.2); the instance has a role |
| `MissingRegion` (AWS) | `Region` not set | set `AWSKMS.Region` |
| `the key provider denied the key: Azure Key Vault …: Forbidden` | no role on the key yet, or a role assignment still propagating | assign the role of §5.3; wait a few minutes |
| `DefaultAzureCredential: failed to acquire a token` | no identity: the VM has no managed identity, the service-principal variables are missing, or workload identity is not wired | §5.3 identity table, §6.3 |
| `ForbiddenByConnection` or a connection timeout to `*.vault.azure.net` | the vault's firewall does not admit the server | private endpoint or service endpoint (§5.3 Network) |
| `the local key does not unwrap the stored key` | `Local.Key` differs from the key the data key was wrapped with | put the original key back |
| `key provider mismatch: the data encryption key is wrapped by … but the configuration names …` | provider or key changed in the configuration | put the previous block back, then `rewrap` (§8.3) |
| `the database holds encrypted values but EncryptionConfig.Mode is off` | the block was removed or set to off | put it back, or `decrypt` (§8.4) |
| `a database decryption is running or was interrupted` | `decrypt` did not finish | run `decrypt` again, or `decrypt --cancel` |
| `the store holds encrypted data but its key record is missing` | `encryption_keys` lost (partial restore, manual delete) | restore the whole database from a backup (§8.1); management will not invent a new key |
| `EncryptionConfig.Mode on needs the sqlite, postgres or redis store engine` | legacy JSON file store | migrate the store engine first (`02-server-operations.md` §17) |
| `a value of <table>.<column> does not decrypt and is returned as stored` (warning) | a value encrypted with another key, e.g. copied from another environment | find where it came from; the rest of the server works |
| `another instance turned encryption on; this instance runs with EncryptionConfig.Mode off and stops writing secrets` | several instances with different configurations | give every instance the same `EncryptionConfig` and restart it |
| `renewing the vault credentials: vault token renew: …` (warning) | the Vault token cannot be renewed, or is near its maximum TTL | use a periodic token or AppRole (§5.1) before it expires |
| `decrypt`: `<n> instance heartbeat(s) from the last 2m0s; waiting for them to age out` | an instance stopped less than two minutes ago, or still runs | wait; if it still runs, stop it (or `--force`) |
| `decrypt`: `instance … still uses the key: stop it before the key is retired` | an instance kept running | stop every management instance, run `decrypt` again |

Escalating: include the `database encryption` lines of the management log and the output
of `encryption status`. Never include `management.json`, tokens, keys or a database dump
(`12-escalation-package.md`).

## 10. Security notes

- **Audit the key store.** Each management start unwraps the data key once. Enable the key
  store's audit (Vault audit device, AWS CloudTrail for KMS `Decrypt`, Key Vault diagnostic
  logs) and alert on unwraps that do not match a management start.
- **Least privilege.** Management needs only encrypt/decrypt (Vault, KMS) or wrap/unwrap
  (Key Vault) on one key. Nobody else needs those rights for daily operation.
- **`management.json` is a secret** with a Vault token or a local key in it; it already is
  one (`02-server-operations.md` §1). Prefer identities without stored secrets: instance
  roles, managed identities, workload identity.
- **Exposure that predates encryption.** Turning encryption on protects copies made from
  then on. Dumps and backups made before stay plaintext; expire them as the retention
  policy allows, and rotate any credential that may have been in one that leaked.
