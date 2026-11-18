"""Smoke tests for routes, SEO metadata and crawler-facing files.

Run with:  python -m unittest discover tests
"""
import json
import os
import re
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, HOME_FAQS  # noqa: E402

SITE = 'https://www.datangleranking.com'
PAGES = ['/', '/practice', '/guide', '/articles', '/about', '/contact', '/privacy', '/terms',
         '/articles/comparing-close-angles', '/articles/angle-ranking-mistakes',
         '/articles/practice-progression', '/articles/why-your-eyes-misjudge-angles',
         '/articles/perceptual-ability-test-overview']


def json_ld_blocks(html):
    return [json.loads(m) for m in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


class SiteTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_pages_render_with_canonical_and_adsense(self):
        for path in PAGES:
            with self.subTest(path=path):
                resp = self.client.get(path)
                self.assertEqual(resp.status_code, 200)
                html = resp.get_data(as_text=True)
                self.assertIn(f'<link rel="canonical" href="{SITE}{path}">', html)
                self.assertIn(f'<meta property="og:url" content="{SITE}{path}">', html)
                self.assertIn('ca-pub-4473065776641796', html)
                self.assertIn('pagead2.googlesyndication.com/pagead/js/adsbygoogle.js', html)
                self.assertNotIn('noindex', html)
                for block in json_ld_blocks(html):
                    self.assertEqual(block['@context'], 'https://schema.org')

    def test_home_seo_and_structured_data(self):
        html = self.client.get('/').get_data(as_text=True)
        self.assertIn('<title>Free DAT Angle Ranking Practice | Customizable Angle Generator</title>', html)
        self.assertIn('<h1>Free DAT Angle Ranking Practice</h1>', html)
        self.assertIn('id="how-it-works"', html)
        blocks = {b['@type']: b for b in json_ld_blocks(html)}
        self.assertIn('EducationalOrganization', blocks)
        app_ld = blocks['WebApplication']
        self.assertEqual(app_ld['applicationCategory'], 'EducationalApplication')
        self.assertTrue(app_ld['isAccessibleForFree'])
        self.assertEqual(app_ld['offers']['price'], '0')
        faq = blocks['FAQPage']['mainEntity']
        self.assertEqual(len(faq), len(HOME_FAQS))
        for item in HOME_FAQS:
            # Visible FAQ must match the structured data (HTML-escaped on the page).
            self.assertIn(item['q'].replace('<', '&lt;'), html)
            self.assertIn(item['a'].replace('<', '&lt;'), html)

    def test_practice_without_session_renders(self):
        resp = self.client.get('/practice')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Rank the four angles', resp.get_data(as_text=True))

    def test_choose_difficulty_redirects_to_practice(self):
        resp = self.client.post('/', data={'variance': '10'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers['Location'].endswith('/practice'))

    def test_llms_txt(self):
        resp = self.client.get('/llms.txt')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.headers['Content-Type'].startswith('text/plain'))
        body = resp.get_data(as_text=True)
        self.assertTrue(body.startswith('# DAT Angle Ranking'))
        self.assertIn('free, customizable DAT angle ranking practice', body)

    def test_sitemap_lists_every_page_with_https_www(self):
        resp = self.client.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        locs = [e.text for e in ET.fromstring(resp.data).findall('s:url/s:loc', ns)]
        for loc in locs:
            self.assertTrue(loc.startswith(SITE + '/'), loc)
        for path in PAGES + ['/llms.txt']:
            self.assertIn(SITE + path, locs)
        for loc in locs:
            self.assertEqual(self.client.get(loc[len(SITE):]).status_code, 200, loc)

    def test_robots_and_ads_txt(self):
        robots = self.client.get('/robots.txt').get_data(as_text=True)
        self.assertNotRegex(robots, r'(?m)^Disallow: /\s*$')
        self.assertIn(f'Sitemap: {SITE}/sitemap.xml', robots)
        ads = self.client.get('/ads.txt')
        self.assertEqual(ads.status_code, 200)
        self.assertIn('pub-4473065776641796', ads.get_data(as_text=True))

    def test_og_image_exists(self):
        self.assertEqual(self.client.get('/static/example_angle.jpg').status_code, 200)


if __name__ == '__main__':
    unittest.main()
