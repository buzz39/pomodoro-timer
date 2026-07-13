# SEO Launch Checklist — pomodorotimer.one

## Google Search Console
1. Open Google Search Console.
2. Add/verify property for `https://pomodorotimer.one` or domain property `pomodorotimer.one`.
3. Submit sitemap: `https://pomodorotimer.one/sitemap.xml`.
4. Use URL Inspection for:
   - `https://pomodorotimer.one/`
   - `https://pomodorotimer.one/25-minute-timer.html`
   - `https://pomodorotimer.one/50-10-timer.html`
   - `https://pomodorotimer.one/study-timer.html`
   - `https://pomodorotimer.one/coding-timer.html`
   - `https://pomodorotimer.one/pomodoro-technique.html`
5. Request indexing after inspection if Google has not crawled the updated version.

## Bing Webmaster Tools / IndexNow
- Confirm an IndexNow key file is live.
- Submit `https://pomodorotimer.one/sitemap.xml` in Bing Webmaster Tools.

## Post-deploy validation
- `https://www.pomodorotimer.one/` should 308 to apex.
- `https://pomodorotimer.one/llms.txt` should return 200.
- `https://pomodorotimer.one/og-image.png` should return 200.
- `https://pomodorotimer.one/50-25-timer.html` should redirect to `/50-10-timer.html`.
- Run Rich Results Test on homepage, blog, technique, study, coding, and 50/10 timer pages.
