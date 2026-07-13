import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def extract_json_ld(html: str):
    pattern = re.compile(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        re.I | re.S,
    )
    return [json.loads(match.group(1)) for match in pattern.finditer(html)]


class RemainingFixesTest(unittest.TestCase):
    def test_llms_txt_exists_with_main_tools_and_guides(self):
        text = read("llms.txt")
        self.assertIn("# pomodorotimer.one", text)
        for url in [
            "https://pomodorotimer.one/",
            "https://pomodorotimer.one/25-minute-timer.html",
            "https://pomodorotimer.one/50-25-timer.html",
            "https://pomodorotimer.one/study-timer.html",
            "https://pomodorotimer.one/coding-timer.html",
            "https://pomodorotimer.one/pomodoro-timer-with-music.html",
            "https://pomodorotimer.one/pomodoro-technique.html",
            "https://pomodorotimer.one/blog-pomodoro-technique-guide.html",
            "https://pomodorotimer.one/blog-focus-tips-for-developers.html",
            "https://pomodorotimer.one/blog-best-study-methods.html",
        ]:
            self.assertIn(url, text)

    def test_og_image_asset_exists_for_social_and_schema_references(self):
        data = (ROOT / "og-image.png").read_bytes()
        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))

    def test_csp_header_allows_current_static_site_dependencies(self):
        config = json.loads(read("vercel.json"))
        global_headers = next(item["headers"] for item in config["headers"] if item["source"] == "/(.*)")
        headers = {item["key"].lower(): item["value"] for item in global_headers}
        self.assertIn("content-security-policy", headers)
        csp = headers["content-security-policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://pagead2.googlesyndication.com", csp)
        self.assertIn("style-src 'self' 'unsafe-inline'", csp)
        self.assertIn("img-src 'self' data:", csp)
        self.assertIn("connect-src 'self' https://www.google-analytics.com", csp)

    def test_homepage_has_citable_pomodoro_definition_and_mobile_tap_targets(self):
        html = read("index.html")
        self.assertIn("What is a Pomodoro Timer?", html)
        self.assertIn("breaks work into focused 25-minute intervals", html)
        self.assertIn("no signup required", html)
        self.assertRegex(html, r"(?s)@media \(max-width: 480px\).*\.mode-tab[^}]*min-height:\s*48px")
        self.assertRegex(html, r"(?s)@media \(max-width: 480px\).*\.btn[^}]*min-height:\s*48px")
        self.assertRegex(html, r"(?s)@media \(max-width: 480px\).*\.settings-toggle[^}]*min-height:\s*48px")

    def test_existing_article_schema_has_author_and_image(self):
        for page in [
            "pomodoro-technique.html",
            "study-timer.html",
            "coding-timer.html",
            "pomodoro-timer-with-music.html",
        ]:
            article = next(item for item in extract_json_ld(read(page)) if item.get("@type") == "Article")
            self.assertEqual(article["image"], "https://pomodorotimer.one/og-image.png")
            self.assertEqual(article["author"]["@type"], "Organization")
            self.assertEqual(article["author"]["name"], "PomodoroTimer.one")

    def test_blog_posts_have_blogposting_schema(self):
        for page in [
            "blog-pomodoro-technique-guide.html",
            "blog-focus-tips-for-developers.html",
            "blog-best-study-methods.html",
        ]:
            schemas = extract_json_ld(read(page))
            blog_post = next(item for item in schemas if item.get("@type") == "BlogPosting")
            self.assertEqual(blog_post["url"], f"https://pomodorotimer.one/{page}")
            self.assertEqual(blog_post["image"], "https://pomodorotimer.one/og-image.png")
            self.assertEqual(blog_post["author"]["name"], "PomodoroTimer.one")
            self.assertEqual(blog_post["publisher"]["logo"]["url"], "https://pomodorotimer.one/og-image.png")
            self.assertEqual(blog_post["mainEntityOfPage"]["@id"], f"https://pomodorotimer.one/{page}")

    def test_non_home_pages_have_breadcrumb_schema(self):
        pages = [
            "25-minute-timer.html",
            "50-25-timer.html",
            "study-timer.html",
            "coding-timer.html",
            "pomodoro-timer-with-music.html",
            "pomodoro-technique.html",
            "blog-pomodoro-technique-guide.html",
            "blog-focus-tips-for-developers.html",
            "blog-best-study-methods.html",
        ]
        for page in pages:
            breadcrumbs = [item for item in extract_json_ld(read(page)) if item.get("@type") == "BreadcrumbList"]
            self.assertEqual(len(breadcrumbs), 1, page)
            items = breadcrumbs[0]["itemListElement"]
            self.assertEqual(items[0]["name"], "Home")
            self.assertEqual(items[0]["item"], "https://pomodorotimer.one/")
            self.assertEqual(items[-1]["item"], f"https://pomodorotimer.one/{page}")

    def test_home_has_organization_and_blog_has_collectionpage_schema(self):
        org = next(item for item in extract_json_ld(read("index.html")) if item.get("@type") == "Organization")
        self.assertEqual(org["@id"], "https://pomodorotimer.one/#organization")
        self.assertEqual(org["logo"], "https://pomodorotimer.one/og-image.png")

        collection = next(item for item in extract_json_ld(read("blog.html")) if item.get("@type") == "CollectionPage")
        self.assertEqual(collection["url"], "https://pomodorotimer.one/blog.html")
        self.assertEqual(len(collection["hasPart"]), 3)

    def test_html_pages_parse(self):
        class Parser(HTMLParser):
            pass
        for page in ROOT.glob("*.html"):
            parser = Parser()
            parser.feed(page.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
