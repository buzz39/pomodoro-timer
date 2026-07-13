import json
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


class FoundationFixesTest(unittest.TestCase):
    def test_vercel_no_clean_urls_or_privacy_rewrite(self):
        config = json.loads(read("vercel.json"))
        self.assertNotIn("cleanUrls", config)
        self.assertNotIn("rewrites", config)

    def test_sitemap_lists_live_pages_without_fabricated_lastmod(self):
        xml = read("sitemap.xml")
        root = ET.fromstring(xml)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text for el in root.findall("sm:url/sm:loc", ns)]
        expected = {
            "https://pomodorotimer.one/",
            "https://pomodorotimer.one/pomodoro-technique.html",
            "https://pomodorotimer.one/25-minute-timer.html",
            "https://pomodorotimer.one/50-10-timer.html",
            "https://pomodorotimer.one/study-timer.html",
            "https://pomodorotimer.one/coding-timer.html",
            "https://pomodorotimer.one/pomodoro-timer-with-music.html",
            "https://pomodorotimer.one/blog-pomodoro-technique-guide.html",
            "https://pomodorotimer.one/blog-focus-tips-for-developers.html",
            "https://pomodorotimer.one/blog-best-study-methods.html",
            "https://pomodorotimer.one/blog.html",
            "https://pomodorotimer.one/privacy.html",
        }
        self.assertEqual(set(locs), expected)
        self.assertNotIn("<lastmod>", xml)

    def test_homepage_links_to_timer_and_blog_spokes(self):
        html = read("index.html")
        for href in [
            "/25-minute-timer.html",
            "/50-10-timer.html",
            "/study-timer.html",
            "/coding-timer.html",
            "/pomodoro-timer-with-music.html",
            "/pomodoro-technique.html",
            "/blog-pomodoro-technique-guide.html",
            "/blog-focus-tips-for-developers.html",
            "/blog-best-study-methods.html",
        ]:
            self.assertIn(f'href="{href}"', html)

    def test_homepage_removes_affiliate_placeholders_and_duplicate_ga4(self):
        html = read("index.html")
        self.assertNotIn("Recommended Productivity Tools", html)
        self.assertNotIn("Replace href with your affiliate link", html)
        self.assertNotIn("G-XXXXXXXXXX", html)
        self.assertEqual(html.count("G-HFT9D6TFKV"), 2)  # script URL + config call

    def test_study_timer_has_working_embedded_timer(self):
        html = read("study-timer.html")
        self.assertIn('id="timer-study-display"', html)
        self.assertIn('id="start-study-timer"', html)
        self.assertIn("let timeLeftStudy = 25 * 60", html)
        self.assertIn("setInterval", html)
        self.assertIn("AudioContext", html)

    def test_coding_timer_has_working_50_minute_embedded_timer(self):
        html = read("coding-timer.html")
        self.assertIn('id="timer-coding-display"', html)
        self.assertIn('id="start-coding-timer"', html)
        self.assertIn("let timeLeftCoding = 50 * 60", html)
        self.assertIn("setInterval", html)
        self.assertIn("AudioContext", html)


if __name__ == "__main__":
    unittest.main()
