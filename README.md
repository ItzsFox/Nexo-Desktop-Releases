# Nexo Desktop Releases

This public repository hosts Nexo Desktop release assets and its cross-platform
build orchestration. Application source remains in private repositories.

## Private-source CI

`Private source CI` runs on the standard GitHub-hosted Windows and macOS runners
assigned to this public repository. It checks out an exact private source ref by
using repository-scoped, read-only deploy keys and does not upload source or CI
artifacts.

Repository administrators must configure these Actions secrets:

- `NEXO_DESKTOP_DEPLOY_KEY`: private half of a read-only deploy key registered on
  `ItzsFox/Nexo-Desktop`.
- `NEXO_WEB_DEPLOY_KEY`: private half of a read-only deploy key registered on
  `ItzsFox/Nexo`.

Run the workflow from the Actions page and provide a commit SHA, tag, or branch.
Using an immutable commit SHA is recommended.

The workflow intentionally has no `pull_request` or `push` trigger. This prevents
untrusted public contributions from receiving private-source credentials. Build
logs in this repository are public, so the workflow also avoids caches, debug
dumps, and artifact uploads.

## Stable releases

`Stable desktop release` builds the Windows and universal macOS packages from an
immutable private source commit. Publishing is a separate Boolean input and is
disabled by default, allowing the complete package gates to be tested safely.
Only release installers, update packages, manifests, checksums, and compliance
archives are transferred between jobs; retained artifacts expire after one day.

Unsigned builds need only the two deploy-key secrets above. Signed builds also
require the Windows and Apple certificate/notarization secrets named in the
workflow. The workflow is manual-only so public pull requests and pushes cannot
access any private-source or signing credential.
