"""Resolve a completed stable build to its immutable source and release artifacts."""

import json
import os
import re
import subprocess


def validate(run, jobs, artifacts):
    if (run.get("path") != ".github/workflows/stable-release.yml"
            or run.get("event") != "workflow_dispatch"
            or run.get("head_branch") != "main"
            or run.get("status") != "completed"):
        raise ValueError("Choose a completed stable-release.yml build from main.")

    match = re.fullmatch(
        r"Nexo Desktop ([0-9]+\.[0-9]+\.[0-9]+) from ([0-9a-f]{40})",
        run.get("display_title", ""),
    )
    if not match:
        raise ValueError("The build must use an exact desktop commit SHA, not a branch or tag.")

    for name in ("Validate private source", "Build Windows release", "Build universal macOS release"):
        matches = [job for job in jobs if job.get("name") == name]
        if len(matches) != 1 or matches[0].get("conclusion") != "success":
            raise ValueError(f"Required build job did not succeed: {name}")

    selected = []
    for name in ("public-win-x64", "public-osx-universal"):
        matches = [artifact for artifact in artifacts if artifact.get("name") == name]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one artifact named {name}.")
        artifact = matches[0]
        if artifact.get("expired") is not False or artifact.get("size_in_bytes", 0) <= 0:
            raise ValueError(f"Artifact is expired or empty: {name}")
        provenance = artifact.get("workflow_run", {})
        if provenance.get("id") != run["id"] or provenance.get("head_sha") != run["head_sha"]:
            raise ValueError(f"Artifact provenance does not match the selected build: {name}")
        selected.append(str(artifact["id"]))

    return {
        "version": match[1],
        "source_sha": match[2],
        "public_sha": run["head_sha"],
        "artifact_ids": ",".join(selected),
    }


def api(endpoint, paginated=False):
    command = ["gh", "api", endpoint]
    if paginated:
        command.extend(["--paginate", "--slurp"])
    return json.loads(subprocess.check_output(command, text=True))


def main():
    run_id = os.environ["SOURCE_RUN_ID"]
    if not re.fullmatch(r"[1-9][0-9]*", run_id):
        raise ValueError("run_id must be the numeric Actions run ID from the run URL.")
    repository = os.environ["GITHUB_REPOSITORY"]
    endpoint = f"repos/{repository}/actions/runs/{run_id}"
    run = api(endpoint)
    jobs = [job for page in api(f"{endpoint}/jobs?filter=latest&per_page=100", True)
            for job in page["jobs"]]
    artifacts = [artifact for page in api(f"{endpoint}/artifacts?per_page=100", True)
                 for artifact in page["artifacts"]]
    outputs = validate(run, jobs, artifacts)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        for name, value in outputs.items():
            output.write(f"{name}={value}\n")
    print(f"Reusing build #{run['run_number']} for Nexo Desktop {outputs['version']}")


if __name__ == "__main__":
    main()
