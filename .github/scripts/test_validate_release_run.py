import copy
import unittest

from validate_release_run import validate


class ValidateReleaseRunTests(unittest.TestCase):
    def setUp(self):
        self.run = {
            "id": 42,
            "path": ".github/workflows/stable-release.yml",
            "event": "workflow_dispatch",
            "head_branch": "main",
            "status": "completed",
            "head_sha": "b" * 40,
            "display_title": "Nexo Desktop 0.1.8 from " + "a" * 40,
        }
        self.jobs = [{"name": name, "conclusion": "success"} for name in (
            "Validate private source", "Build Windows release", "Build universal macOS release")]
        self.artifacts = [{
            "id": index,
            "name": name,
            "expired": False,
            "size_in_bytes": 100,
            "workflow_run": {"id": 42, "head_sha": "b" * 40},
        } for index, name in enumerate(("public-win-x64", "public-osx-universal"), 1)]

    def test_selects_original_commit_version_and_both_artifact_ids(self):
        self.assertEqual(validate(self.run, self.jobs, self.artifacts), {
            "version": "0.1.8", "source_sha": "a" * 40,
            "public_sha": "b" * 40, "artifact_ids": "1,2",
        })

    def test_failed_publish_does_not_require_successful_builds_to_run_again(self):
        self.run["conclusion"] = "failure"
        self.jobs.append({"name": "Publish public release", "conclusion": "failure"})
        self.assertEqual(validate(self.run, self.jobs, self.artifacts)["version"], "0.1.8")

    def test_rejects_other_workflows_branches_events_and_running_builds(self):
        for field, value in (("path", ".github/workflows/private-source-ci.yml"),
                             ("head_branch", "feature"), ("event", "pull_request"),
                             ("status", "in_progress")):
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(dict(self.run, **{field: value}), self.jobs, self.artifacts)

    def test_rejects_moving_source_ref(self):
        self.run["display_title"] = "Nexo Desktop 0.1.8 from main"
        with self.assertRaises(ValueError):
            validate(self.run, self.jobs, self.artifacts)

    def test_rejects_failed_or_missing_platform(self):
        self.jobs[1]["conclusion"] = "failure"
        with self.assertRaises(ValueError):
            validate(self.run, self.jobs, self.artifacts)
        with self.assertRaises(ValueError):
            validate(self.run, self.jobs[:1], self.artifacts)

    def test_rejects_expired_empty_foreign_missing_and_duplicate_artifacts(self):
        for field, value in (("expired", True), ("size_in_bytes", 0),
                             ("workflow_run", {"id": 99, "head_sha": "b" * 40}),
                             ("workflow_run", {"id": 42, "head_sha": "c" * 40})):
            artifacts = copy.deepcopy(self.artifacts)
            artifacts[0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                validate(self.run, self.jobs, artifacts)
        for artifacts in (self.artifacts[:1], self.artifacts + [self.artifacts[0]]):
            with self.assertRaises(ValueError):
                validate(self.run, self.jobs, artifacts)


if __name__ == "__main__":
    unittest.main()
