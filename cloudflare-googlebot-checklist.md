# Cloudflare + search-bot setup checklist (Mr Mathematics)

Goal: **block abusive bots**, but **never challenge/block verified Googlebot or Bingbot**.  
Use this after the March 2026 incident.

---

## What I need from you to verify setup

Share these (screenshots or CSV exports). With them I can say “safe” or point to the exact rule to change.

### Must-have

1. **Cloudflare → Security → Events**  
   - Last **7 days**  
   - Filter / search: `Googlebot`  
   - Second filter pass: `bingbot` or `Bing`  
   - Screenshot showing whether Action is *Allow*, *Log*, *Managed Challenge*, *JS Challenge*, *Block*

2. **Cloudflare → Security → Bots** (full page screenshot)  
   - Bot Fight Mode / Super Bot Fight Mode status  
   - Verified bots handling  
   - Any “Block AI bots” / AI scrape controls

3. **Cloudflare → Security → WAF → Custom rules** (list of rules)  
   - Especially anything like: Block all bots, Block Vietnam, Block countries, Challenge all non-UK, Block ASNs  
   - For each rule: **Name, Expression (or summary), Action, Order/Priority**

4. **Google Search Console → URL Inspection** on these 5 URLs (screenshot of **Test live URL** result for each):  
   - `https://mr-mathematics.com/`  
   - `https://mr-mathematics.com/mathematics-schemes-of-work/`  
   - `https://mr-mathematics.com/pull-up-nets/`  
   - `https://mr-mathematics.com/grade-9-vector-problems/`  
   - `https://mr-mathematics.com/solving-equations-with-indices/`  
   - Need to see: **Crawl allowed**, **Page fetch**, and that HTML is real content

### Nice-to-have

5. GSC → **Settings → Crawl stats** (last 90 days)  
6. GSC → **Indexing → Pages** summary (counts by reason: Indexed / Not indexed reasons)  
7. Cloudflare → **Security → Settings** overview (Security Level, Challenge Passage)  
8. Your current **robots.txt** (`https://mr-mathematics.com/robots.txt`)

I cannot see your Cloudflare account from here. Those items are enough to audit it.

---

## Exact Cloudflare configuration (do this in order)

### 1) Bots — allow verified search engines

Go to: **Security → Bots**

Set / confirm:

| Setting | Required value |
|---------|----------------|
| Verified bots | **Allow** (do not Challenge / Block) |
| Bot Fight Mode (free) | **Off** if it has been challenging Google; prefer WAF rules for abuse instead |
| Super Bot Fight Mode (if on paid plan) | Definitely Allow verified bots; do **not** “Block definitely automated” in a way that catches search bots — verified bots must be excluded |
| Block AI Bots / AI Scrapers | **Off**, or only block *training* bots in a way that does **not** include Googlebot/Bingbot as collateral. If unsure → Off until recovery finishes |

**Rule of thumb:** if a control says “block all bots” or “challenge all automated traffic” with no verified-bot exception → turn it off or narrow it.

### 2) Add an explicit allow rule for search bots (highest priority)

Go to: **Security → WAF → Custom rules → Create rule**

**Name:** `Allow verified search engine bots`

**Expression** (Cloudflare expression language — paste carefully):

```txt
(cf.bot_management.verified_bot) or (http.user_agent contains "Googlebot") or (http.user_agent contains "Google-InspectionTool") or (http.user_agent contains "bingbot") or (http.user_agent contains "BingPreview")
```

If your plan has Bot Management fields, prefer the verified_bot version alone when available:

```txt
(cf.bot_management.verified_bot)
```

**Action:** **Skip**  
Under Skip, skip: **All remaining custom rules**, and also skip **Bot Fight Mode / Super Bot Fight Mode / WAF managed rules** if those options appear (skip as much security processing as the UI allows for this rule).

**Order:** Move this rule to the **top** (first evaluated).

> Note: UA-only allowlists can be spoofed. That is OK here because this rule is an *allow/skip*, not your only defence. Keep separate **block** rules for abusive traffic that do not apply to verified bots.

### 3) Replace “block all bots” with abuse-specific blocks

Delete or disable any rule that roughly means:

- Block all bots  
- Challenge all visitors  
- Block all automated traffic  
- Country block that was meant to stop Vietnam bots **without** excluding verified bots  

Create narrower rules instead, for example:

**Name:** `Block abusive non-verified bots (VN focus)`

**Expression (example — adjust to what you actually saw in logs):**

```txt
not cf.bot_management.verified_bot and ip.geoip.country eq "VN" and cf.client.bot
```

**Action:** **Block** (or Managed Challenge if you want to be softer)

Or IP/ASN based if you have specific attackers:

```txt
not cf.bot_management.verified_bot and ip.src in {1.2.3.4 5.6.7.8}
```

**Critical:** every Block/Challenge rule that targets bots or countries must include:

```txt
and not cf.bot_management.verified_bot
```

(or sit **below** the Allow/Skip search-bot rule so verified bots never hit them).

### 4) Security level & extras

| Place | Setting | Value |
|-------|---------|-------|
| Security → Settings | Security Level | **Essentially Off** or **Low** while recovering (avoid “I’m Under Attack” except during an active assault) |
| Security → Settings | Challenge Passage | 30 minutes is fine |
| Speed → Optimization | Rocket Loader | **Off** (can break rendering for Google) |
| Scrape Shield / Hotlink | Don’t block Google fetching images needed for understanding pages | |

### 5) robots.txt sanity

Visit `https://mr-mathematics.com/robots.txt`

Must **not** disallow `/` for Googlebot.  
Yoast sitemap line should remain, e.g. `Sitemap: https://mr-mathematics.com/sitemap_index.xml`

Optional recommended line (Cloudflare internal path):

```txt
Disallow: /cdn-cgi/
```

---

## Exact Google Search Console checks (same day as Cloudflare changes)

### A) Live fetch (proof crawlers work)

For each of the 5 URLs above:

1. GSC → **URL Inspection** → paste URL  
2. **Test live URL**  
3. Pass criteria:  
   - Crawl allowed: **Yes**  
   - Page fetch: **Successful**  
   - View tested page → HTML shows the real lesson/title (not Cloudflare challenge / blank)

If fetch fails → stop requesting indexing; fix Cloudflare first.

### B) Crawl stats

GSC → **Settings → Crawl stats**

After a successful fix you should see, over 1–2 weeks:

- Host status mostly green  
- Crawl requests returning  
- Fewer **4xx** tied to the outage period  

### C) Indexing recovery (only after live fetch passes)

GSC → **Indexing → Pages**

1. Note counts for “Not indexed” reasons  
2. Each day: pick **10–20** important not-indexed URLs  
3. Confirm in sitemap + linked internally  
4. Live test → Request indexing **once**  
5. Do not mass-request hundreds of URLs

Priority order: homepage → schemes of work → membership → top GSC click URLs → remaining lesson posts.

---

## Audit: current WAF rules (from your screenshot)

Custom rules (order matters — top first):

| # | Rule | Action | SEO verdict |
|---|------|--------|-------------|
| 1 | `Skip protection for verified bots (safe pages only)` | Skip | **OK for Google (verified).** Full expression has **no path filter** despite the name — matches `cf.client.bot` OR Google/Bing UAs; Skip custom + rate limit + managed + Super Bot Fight; Place **First**. Rename only. |
| 2 | `03 - Block high-risk countries` (RU, VN, KP, IR, BY) | Block | OK if rule 1 stays First; optional: exclude verified bots on the rule itself. |
| 3 | `04 - CN and TH - harden WordPress attack paths` | Managed Challenge | OK — already excludes Known Bots. |
| 4 | `protecting product/category pages` (`/product/` …) | Managed Challenge | **OK for Google (verified).** Expression includes `and not cf.client.bot` on GET `/product/` and `/product-category/`. |
| 5 | `Protect Search Bar` (`s=` + not Known Bot) | Managed Challenge | OK — excludes Known Bots. |
| 6 | `Block VNPT Corp` (AS45899) | Block | OK if rule 1 Skips verified bots sitewide; otherwise add bot exclusion. |
| 7 | `Allow Google & Bing but nothing else to shop` (`/shop` + not Known Bot) | Managed Challenge | OK for Google **if** Known Bots detection works; name is misleading (it challenges everyone else). |

Rate limit: `/shop` Managed Challenge — lower SEO priority than `/product/`.

**Why this matters for your GSC data:** many high-impression URLs are `/product/...` (corresponding angles, transformations, completing the square, etc.) with very low CTR. Challenging those paths for crawlers can stall re-indexing after March.

### Exact fixes (do these)

1. **Edit rule 1** — remove any URI/path condition. It must Skip for verified/Known bots on **all** URLs (including `/product/`, `/shop/`, `/wp-admin` is fine to leave challenged for humans).  
   Target expression:
   ```txt
   (cf.client.bot) or (http.user_agent contains "Googlebot") or (http.user_agent contains "Google-InspectionTool") or (http.user_agent contains "bingbot") or (http.user_agent contains "BingPreview")
   ```
   Or in the visual builder: **Known Bots equals true** OR those User-Agent contains clauses.  
   Action: **Skip** → skip remaining custom rules (and bot fight if offered).  
   Rename to: `Skip protection for verified bots (all pages)`.

2. **Edit rule 4** (`protecting product/category pages`) — add exclusion so it only challenges non-bots:
   ```txt
   ...existing product/category match... and not cf.client.bot
   ```
   In UI: add **Known Bots does not equal true** (same pattern as rules 5 and 7).

3. **Edit rule 2** (country block) — add **and Known Bots does not equal true** so a misclassified crawler never gets a hard Block.

4. Keep rule 7’s Known Bots exclusion; optional rename to `Challenge non-bots on /shop`.

5. Re-test in GSC **Test live URL**:
   - `https://mr-mathematics.com/product/corresponding-angles-parallel-lines/`
   - `https://mr-mathematics.com/pull-up-nets/`
   - Homepage  
   All three must **Page fetch: Successful**.

---

## Pass / fail definition

**Cloudflare is “set up as needed” when all of these are true:**

1. Security Events show **no Block/Challenge** for Googlebot/bingbot in the last 7 days  
2. Custom rule **Skip verified bots** exists at **top**, applies to **all pages** (not “safe pages only”), Action **Skip**  
3. `/product/` challenge rule excludes Known/Verified bots  
4. Country/ASN blocks exclude Known/Verified bots  
5. GSC **Test live URL** succeeds on homepage **and** a `/product/` URL  
6. Bot Fight / AI-block settings are not challenging search bots  

Until (2), (3), and (5) are true, treat product-page indexing as at risk.

---

## Minimal daily routine until September

| Day | Action |
|-----|--------|
| Today | Finish Cloudflare steps 1–4; send me the must-have screenshots |
| Same day | Live-test 5 money URLs in GSC |
| Daily (15 min) | 10–20 Request indexing on priority not-indexed URLs |
| Weekly | Check Crawl stats + impressions trend vs Feb peak |
| After any CF change | Re-run live URL test on homepage the same day |
