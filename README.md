# Nexo Desktop Releases

Windows and macOS builds for Nexo.

To publish an existing stable build without compiling again, open Actions →
**Publish existing build** → **Run workflow** and enter the numeric run ID from
the completed stable build's Actions URL. This publishes directly after checking
the original source commit, both platform jobs, retained artifacts, release files,
manifests and checksums. The build must have used an exact desktop commit SHA.
Download or publish before its artifacts expire (currently one day after upload).
An existing release tag is left untouched; this workflow creates a new release.
