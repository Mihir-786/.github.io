"""Safety and import/export smoke tests for the public-leads Career Ops bridge."""
import csv
import tempfile
import unittest
from pathlib import Path
from career_ops_bridge import normalized_url, export_candidates, import_candidates


class CareerOpsBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.csv = self.root / "latest.csv"
        self.export = self.root / "queue.md"
        self.inbox = self.root / "data" / "pipeline.md"
        self.inbox.parent.mkdir(parents=True)
        with self.csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "company", "location",
                                                  "source", "url", "score", "remote"])
            writer.writeheader()
            writer.writerows([
                dict(title="Marketing Specialist", company="Acme Inc",
                     location="NYC", source="LinkedIn", score="30",
                     url="https://www.linkedin.com/jobs/view/123?trk=abc", remote="False"),
                dict(title="Marketing Specialist", company="Acme Inc",
                     location="NYC", source="LinkedIn", score="29",
                     url="https://www.linkedin.com/jobs/view/123?trk=other", remote="False"),
                dict(title="Content Creator", company="Example Studio",
                     location="NYC", source="LinkedIn", score="23",
                     url="https://www.linkedin.com/jobs/view/234", remote="False"),
                dict(title="Broken", company="Nothing", location="NYC", source="?",
                     score="0", url="not a url", remote="False"),
            ])
        self.inbox.write_text("# Pipeline\n\n## Pending\n\n"
                              "- [ ] https://www.linkedin.com/jobs/view/234 | Example Studio | Content Creator\n\n"
                              "## Processed\n\n- [x] https://example.com/old | Old | Role\n",
                              encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_normalized_url_preserves_meaningful_params(self):
        self.assertEqual(normalized_url("https://jobs.example.com/apply?id=123&utm_source=foo"),
                         "https://jobs.example.com/apply?id=123")
        self.assertEqual(normalized_url("javascript:alert(1)"), "")

    def test_export_deduplicates(self):
        count = export_candidates(self.csv, self.export, 15)
        text = self.export.read_text()
        self.assertEqual(count, 2)
        self.assertEqual(text.count("- [ ] "), 2)
        self.assertIn("## Pending", text)
        self.assertNotIn("mihirpatelll055", text)

    def test_preview_does_not_write(self):
        export_candidates(self.csv, self.export, 15)
        before = self.inbox.read_bytes()
        count = import_candidates(self.export, self.inbox, False)
        self.assertEqual(count, 1)
        self.assertEqual(self.inbox.read_bytes(), before)

    def test_confirm_merges_without_losing_processed(self):
        export_candidates(self.csv, self.export, 15)
        count = import_candidates(self.export, self.inbox, True)
        self.assertEqual(count, 1)
        t = self.inbox.read_text()
        self.assertEqual(t.count("https://www.linkedin.com/jobs/view/234"), 1)
        self.assertIn("https://www.linkedin.com/jobs/view/123", t)
        self.assertLess(t.index("https://www.linkedin.com/jobs/view/123"), t.index("## Processed"))
        self.assertIn("https://example.com/old", t)
        self.assertEqual(len(list(self.inbox.parent.glob("pipeline.md.*.bak"))), 1)

    def test_second_import_adds_zero(self):
        export_candidates(self.csv, self.export, 15)
        import_candidates(self.export, self.inbox, True)
        self.assertEqual(import_candidates(self.export, self.inbox, True), 0)


if __name__ == "__main__":
    unittest.main()
