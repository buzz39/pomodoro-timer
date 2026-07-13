import json
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


class FinalSeoPolishTest(unittest.TestCase):
    def test_50_10_url_replaces_50_25_everywhere_with_redirect(self):
        self.assertTrue((ROOT / "50-10-timer.html").exists())
        self.assertFalse((ROOT / "50-25-timer.html").exists())

        config = json.loads(read("vercel.json"))
        redirects = config.get("redirects", [])
        self.assertIn(
            {"source": "/50-25-timer.html", "destination": "/50-10-timer.html", "permanent": True},
            redirects,
        )

        for path in ROOT.glob("*.html"):
            html = path.read_text(encoding="utf-8")
            self.assertNotIn("50-25-timer.html", html, path.name)
            self.assertNotIn("https://pomodorotimer.one/50-25-timer.html", html, path.name)

        sitemap = read("sitemap.xml")
        self.assertIn("https://pomodorotimer.one/50-10-timer.html", sitemap)
        self.assertNotIn("50-25-timer.html", sitemap)
        self.assertIn("https://pomodorotimer.one/50-10-timer.html", read("llms.txt"))
        self.assertNotIn("50-25-timer.html", read("llms.txt"))

    def test_no_broken_root_relative_links_in_html(self):
        missing = []
        for page in ROOT.glob("*.html"):
            html = page.read_text(encoding="utf-8")
            for href in re.findall(r'href=["\']([^"\']+)["\']', html):
                if not href.startswith("/") or href.startswith("//#"):
                    continue
                target = href.split("#", 1)[0].split("?", 1)[0]
                if target in ("", "/"):
                    continue
                if not (ROOT / target.lstrip("/")).exists():
                    missing.append((page.name, href))
        self.assertEqual(missing, [])

    def test_timer_variant_pages_have_unique_content_depth_sections(self):
        expectations = {
            "25-minute-timer.html": ["Best tasks for a 25 minute timer", "When 25 minutes is too short"],
            "50-10-timer.html": ["Why 50/10 works for deep work", "Best tasks for a 50/10 timer"],
            "study-timer.html": ["Study timer workflows by subject", "Exam prep timer routine"],
            "coding-timer.html": ["Coding timer workflows by task type", "Protecting developer flow"],
            "pomodoro-timer-with-music.html": ["Music timer setup recipes", "When to use silence instead"],
        }
        for page, phrases in expectations.items():
            html = read(page)
            words = re.findall(r"[A-Za-z0-9']+", re.sub(r"<[^>]+>", " ", html))
            self.assertGreaterEqual(len(words), 700, page)
            for phrase in phrases:
                self.assertIn(phrase, html, page)

    def test_offsite_research_and_search_console_checklist_are_draft_only(self):
        offsite = read("seo-offsite-opportunities.md")
        self.assertIn("Drafts only", offsite)
        self.assertIn("Do not post automatically", offsite)
        self.assertIn("Approval required", offsite)
        self.assertIn("Reddit", offsite)
        self.assertIn("tool directories", offsite)

        checklist = read("seo-launch-checklist.md")
        self.assertIn("Google Search Console", checklist)
        self.assertIn("https://pomodorotimer.one/sitemap.xml", checklist)
        self.assertIn("URL Inspection", checklist)

    def test_sitemap_contains_all_current_html_public_pages(self):
        root = ET.fromstring(read("sitemap.xml"))
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = {el.text for el in root.findall("sm:url/sm:loc", ns)}
        public_html = {p.name for p in ROOT.glob("*.html") if p.name != "privacy.html"} | {"privacy.html"}
        expected = {"https://pomodorotimer.one/"}
        expected |= {f"https://pomodorotimer.one/{name}" for name in public_html if name != "index.html"}
        self.assertTrue(expected.issubset(locs))


if __name__ == "__main__":
    unittest.main()
