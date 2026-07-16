# Mr Mathematics: £10k → £55k Membership Plan

**Goal:** £55,000 / year membership revenue (enough to treat the site as a full-time business)  
**Baseline (your figure):** ~£10,000 last year  
**Measured run-rate:** ~**£9.3k–£11.5k** TTM from the two WooCommerce sales exports below  
**Site:** [mr-mathematics.com](https://mr-mathematics.com)  
**Listed prices (annual):** Lite £19.95 · Student £29.85 · Teacher £49.95 · School £395

---

## Evidence: Sales (Jul 2023 – Jul 2026)

Two monthly WooCommerce custom reports (filenames as uploaded):

| Report | Inferred product | Unit price pattern | 3-yr items | 3-yr sales |
|--------|------------------|--------------------|----------:|----------:|
| `sales-teacher-like-monthly.csv` (report 1) | Individual memberships (mostly Teacher) | ~£30–£50; **£49.95 most common** | 524 | **£24,098** |
| `sales-119-monthly.csv` (report 2) | Fixed £119.50 SKU (likely school/department tier) | **£119.50 every sale** | 65 | **£7,768** |

**Combined totals**

| Period | Items | Revenue |
|--------|------:|--------:|
| Calendar 2023 (partial Jul–Dec) | 113 | £5,448 |
| Calendar 2024 | 219 | **£12,189** |
| Calendar 2025 | 170 | **£9,148** |
| 2026 YTD (Jan–Jul) | 87 | £5,081 |
| Academic 2023–24 (Aug–Jul) | 197 | £10,226 |
| Academic 2024–25 | 207 | **£11,117** |
| Academic 2025–26 (to Jul) | 174 | £9,715 |
| TTM to Jun 2025 | 213 | **£11,487** |
| TTM to Jun 2026 | 170 | **£9,307** |

Your “~£10k last year” matches the data. The uncomfortable part: **revenue peaked in 2024 and has softened** (~19% down TTM Jun 2025 → Jun 2026), driven mainly by fewer individual (~£50) sales (193 → 152 units TTM).

**Seasonality (combined average by month):** September dominates (~£2,260 avg; peak £2,785 in Sep 2024). November is a clear second peak. December is dead (~£280). The year is won or lost in **late August–November**.

**Product mix gap vs the live membership page:** these exports show **no £395 School lines**. Either School @ £395 is not selling / not in these reports, or departments are still buying the **£119.50** SKU. Clarify which SKU is “School” before counting on 70 × £395. At current mix, ~20 × £119.50/year ≈ £2.4k — nowhere near a full-time school channel.

**Gap to £55k from TTM £9.3k:** about **+£45.7k** (~**5.9×** current run-rate), not a small CRO tweak alone.

Rough path from *actual* baseline (illustrative):

| Lever | Stretch annual impact | Notes |
|-------|----------------------:|-------|
| Recover + grow Teacher to ~300 units @ ~£50 | ~£15k | Was ~190 at peak TTM |
| Replace/upgrade £119 SKU → true School @ £395 × 50 | ~£20k | Requires active HoD selling |
| CTR + conversion lift on existing SEO | ~£5–10k | Same traffic quality, more checkouts |
| Retention / win-back / email | ~£3–5k | Protect the base that is currently shrinking |
| **Combined stretch** | **~£45–50k uplift** | Needs all levers, especially September |

---

## Evidence: Google Search Console (last 12 months)

Source: GSC Performance export, Web search, ~4 Aug 2025 – 14 Jul 2026 (345 days).

| Metric | Total | Approx. monthly |
|--------|------:|----------------:|
| Clicks | **55,639** | **~4,900** |
| Impressions | **6,888,018** | **~608,000** |
| Average CTR | **0.81%** | — |
| Average position | **5.5** | — |

**The About page “800,000 teachers / month” claim is not supported as visits.**  
GSC shows ~5k Google clicks/month. Monthly *impressions* (~608k, peaking ~1.1–1.3M in Jan–Feb 2026) are in a similar order of magnitude to that number, but impressions are not site visits.

Other facts from the same export:

- **UK is the business:** UK 30,370 clicks (55%); US/India add impressions but tiny CTR (0.26% / 0.28%).
- **Desktop converts search better:** Desktop 39,663 clicks @ 1.08% CTR vs Mobile 14,767 @ 0.49%.
- **Traffic is concentrated:** Top 10 pages ≈ 45% of page-export clicks (pull-up nets, grade 9 vectors, indices equations, homepage, schemes of work…).
- **Huge CTR gap:** many URLs sit at position ~1–4 with 20k–190k impressions and CTR well under 1% (product pages and some lesson pages especially).
- **March 2026 cliff (explained):** Vietnam bot attacks → site crashes → Cloudflare “block all bots” → Google/Bing crawl blocked → impressions fell to ~9% of February. Rules later fixed; recovery incomplete (Jun still ~35% of Feb impressions).
- Brand queries (`mr mathematics` etc.) are strong but a minority of demand; growth is non-brand lesson queries.

Implication for £55k: the near-term SEO job is **index/crawl recovery to pre-March levels**, then CTR + conversion. You are not starting from zero — Jun already recovered clicks somewhat — but **impression share is still ~⅓ of the Feb peak**, which caps membership upside into September.

---

## March 2026 outage → index recovery playbook

### What happened (confirmed by GSC + your account)

1. Malicious bots (Vietnam) repeatedly hit the site and, with the then host/app setup, caused repeated crashes.  
2. Cloudflare was configured to stop essentially all bots.  
3. That also stopped **Googlebot / Bingbot**, so discovery and recrawl collapsed.  
4. Rules and site setup were corrected; Yoast sitemap resubmitted; high-profile URLs manually requested for indexing.  
5. **Some URLs remain unindexed or weakly recrawled** — normal after a multi-week crawl blackout, but it needs a systematic finish, not only one-off “Request indexing” clicks.

GSC monthly impressions vs Feb 2026 peak: Mar **9%** → Apr **18%** → May **36%** → Jun **35%**. Recovery stalled around one-third of peak visibility.

### Step A — Prove Google can fetch *right now* (do this before more Request indexing)

In Cloudflare, permanently:

- **Allow verified bots** (Google, Bing). Never put them behind JS challenge / Bot Fight for HTML.
- Prefer **managed allow** for verified search engine bots over country blocks that can catch crawler IPs.
- Keep blocking abusive ASN/IPs/countries for *unverified* traffic if needed.
- Check **Security → Events** filtered by UA `Googlebot` / `bingbot` for any recent Block/Challenge (should be zero).
- Confirm **“Block AI bots”** (or AI scrape controls) is not also catching multi-purpose Googlebot — Cloudflare has warned some AI-block modes can affect Googlebot depending on settings.

In Google Search Console, for 5 money URLs (homepage, schemes of work, pull-up nets, grade-9 vectors, indices):

1. **URL Inspection → Test live URL**  
2. Require: Crawl allowed = Yes, Page fetch = **Successful**, rendered HTML shows real lesson content (not a challenge/empty shell)  
3. Only then **Request indexing**

If live test fails while the page works in a browser, Cloudflare/WAF is still interfering — fix that before blaming the index.

Also check GSC **Settings → Crawl stats**: host status, crawl requests, and 4xx/5xx since the rule change. You want rising successful crawls and flat/low 403s.

Bing Webmaster Tools: same idea (URL inspection / crawl control) — you deferred Bing too.

### Step B — Index coverage triage (Pages report)

In GSC **Indexing → Pages**, export reasons. Work queues in this order:

| Bucket | Action |
|--------|--------|
| Not indexed – crawled / discovered currently not indexed | Fix internal links + sitemap inclusion; request indexing for top URLs only |
| Soft 404 / redirects / duplicates | Clean canonicals (Yoast), consolidate |
| Blocked by robots.txt / 4xx / 5xx | Fix immediately — leftover of the outage |
| Indexed | Leave alone; improve CTR/content later |

Do **not** spray “Request indexing” across hundreds of URLs. Google rate-limits it. Batch **10–20 revenue URLs/day** until the backlog of *important* URLs shows “Indexed”.

### Step C — Priority URL list (revenue + proven demand)

Recrawl/index these first (from your GSC clicks leaders + membership path):

1. `https://mr-mathematics.com/`  
2. `/mathematics-schemes-of-work/`  
3. `/mr-mathematics-membership/`  
4. `/pull-up-nets/`  
5. `/grade-9-vector-problems/`  
6. `/solving-equations-with-indices/`  
7. `/area-of-compound-shapes/`  
8. Other top-20 click URLs from the Pages export  
9. Then orphan lesson posts that **lost** index status (compare Yoast/sitemap URL count vs GSC “Indexed” count)

For each still-not-indexed URL:

- Confirm it appears in the Yoast sitemap (`sitemap_index.xml` → post/page sitemaps)  
- Confirm a visible internal link from a strong indexed page (schemes hub, related lesson, “what’s new”)  
- Fetch as Google (live test)  
- Request indexing once  
- Wait 1–2 weeks before repeating

### Step D — Help Google re-discover the long tail

After money pages are healthy:

- Keep **one clean sitemap index** submitted (Yoast). Remove any stale secondary sitemaps.  
- Publish a genuine **What’s new / site updates** post that links clusters of recovered lessons (you already do monthly updates — use the next one as an internal-link recovery hub).  
- Rebuild internal links from schemes of work → member lesson URLs that dropped out.  
- Avoid large sitewide noindex experiments while recovering.

### Step E — Guardrails so this never repeats

- Cloudflare rule note in the dashboard: **“Never challenge verified search engine bots.”**  
- Alert if GSC crawl requests or impressions drop >50% week-on-week.  
- Separate “block abusive bots” from “block all bots.”  
- After any WAF change: live-test 3 URLs in GSC the same day.

### Recovery success metrics (next 8–12 weeks)

| Signal | Target |
|--------|--------|
| Monthly impressions | Back toward **~1.0–1.3M** (Jan–Feb 2026 band) before chasing new content volume |
| Crawl stats | Stable daily Googlebot fetches; minimal 403 from CF |
| Pages report | “Not indexed” count falling; money URLs all Indexed |
| September readiness | Top 20 click URLs indexed + ranking by mid-August |

Until impressions recover, treat **index recovery as the #1 SEO project** — ahead of publishing net-new posts — because September sales depend on visibility you already earned once.

---

## The numbers (what “£55k” actually means)

From a **£9.3k TTM** base you need roughly **6×**, not a gentle uptick. Using **listed** Teacher £49.95 and School £395:

| Mix | School (£395) | Teacher (£49.95) | Approx. revenue |
|-----|---------------|------------------|-----------------|
| A – Teacher-heavy | 20 | ~940 | ~£55k |
| B – Balanced (recommended) | 70 | ~520 | ~£55k |
| C – School-led | 100 | ~310 | ~£55k |

Today you are closer to **~150 Teacher-like + ~18 × £119** per year. Hitting Mix B means roughly **3.5× Teacher volume** and replacing the quiet £119 channel with a real **£395 department** motion (or selling far more £119s — ~460/year — which is worse economics).

**Why school AOV still matters:** one £395 school sale ≈ **8 Teacher** sales ≈ **3.3 × £119** sales. But only if buyers actually pay £395 — validate that SKU in WooCommerce vs the £119.50 report line.

**Calendar checkpoints** (weighted to your real seasonality):

| Window | Cumulative target | Focus |
|--------|-------------------|--------|
| Aug–Sep | £12k+ | Must beat prior September (~£2.1–2.8k); school POs + Teacher push |
| Oct–Nov | £22k | Second peak; renewals + win-backs |
| Dec–Feb | £32k | Retention; January planning content |
| Mar–May | £45k | Budget / next-year school conversations |
| Jun–Jul | £55k | Close pipeline; prep next September |

---

## Diagnosis: recovering from a crawl blackout while sales are soft

Membership revenue slipped **~£11.5k → ~£9.3k TTM** while Google visibility is only ~**⅓ of the Feb 2026 peak** after the Cloudflare bot-block incident. Near term you need: **(1) finish index recovery**, **(2) CTR + checkout conversion**, **(3) school AOV**, **(4) reverse the Teacher unit decline before September**.

Prioritise leaks in this order:

1. **Low CTR while ranking well** (impressions → clicks) — titles/meta and weak `/product/` snippets
2. Free users never see a clear reason to pay *this week* (clicks → membership)
3. Inactive members / guest list are not systematically reactivated
4. Schools are undersold relative to individual teachers
5. Pricing is annual-only with little urgency (no trial, no term option, weak “start of term” campaigns)
6. March-style traffic collapses — monitoring / indexing resilience

Your improved SEO is an advantage **only if** high-impression pages earn stronger CTR and every high-intent page ends in a membership decision.

---

## Strategy in one sentence

**Turn SEO + free schemes/lessons into a weekly conversion machine, and turn school departments into the high-ticket growth engine.**

Four levers, in priority order:

1. **CTR / rankings harvest** (impressions you already have → more clicks)  
2. **Conversion** (those clicks → more sales)  
3. **School AOV** (same effort → larger cheques)  
4. **Retention + SEO scale** (keep buyers; grow non-brand queries)

---

## Lever 1 — CTR harvest (impressions → clicks)

You already average position **5.5** with **~6.9M** impressions. At **0.81% CTR**, most of that visibility never becomes a visit.

If overall CTR moved from 0.8% → **1.2%** on the same impressions, that is roughly **+50% clicks** (~2,500 extra Google visits/month) with little new content.

### Fix these page types first

From the GSC Pages export — high impressions, strong position, weak CTR:

| Page type | Examples | Likely fix |
|-----------|----------|------------|
| `/product/` URLs | corresponding angles, describing transformations, completing the square | Rewrite titles/meta for teachers (“lesson + worksheet”), not bare topic names; avoid thin product SERP snippets |
| High-rank lesson pages | compound shapes, cumulative frequency, plan & elevation | Benefit-led title + clearer free sample promise |
| IGCSE foundation hubs | perimeter/area/volume, Pythagoras, FDP | Match query language; add worksheet/PDF cues in title |

Also protect what already works: **pull-up nets**, **grade 9 vectors**, **indices equations**, **schemes of work**, homepage — keep rankings, improve on-page membership CTAs.

### Operational rule

Each week, take the top 10 “impressions ≥ 20k, CTR < 1%, position ≤ 8” URLs and ship title/meta + H1 clarity updates. Re-check in GSC after 2–4 weeks.

---

## Lever 2 — Conversion (clicks → membership sales)

### Fix the membership path on every high-traffic page

On blogs, schemes of work, and free lesson teasers, use one consistent CTA pattern:

1. **What they get free** (scheme / blog / sample)
2. **What members get next** (full PPT, worksheet, answers, generator)
3. **One button** → Teacher membership (not a vague “find out more”)

Priority pages to harden first:

- Schemes of work hub
- Top 20 SEO lesson/blog posts by traffic
- “What’s new” / site updates
- Any free worksheet that already ranks

### Make the offer easier to try

Add **one** low-friction entry (pick one and ship it):

- **14-day Teacher trial** at £1 or free (card captured), auto-converting to £49.95  
  *or*
- **Term membership** (~£24.95 for 4 months) for teachers who won’t commit annually in May

Annual £49.95 is cheap for the value, but “£50 now” still loses fence-sitters. A trial/term option usually lifts conversion more than another 50 free lessons.

### Prove the time-saving claim

Membership copy should lead with outcomes teachers already say in testimonials:

- “Planning done in minutes”
- “Sequenced unit ready tonight”
- “Foundation + Higher options in one place”

Use **one concrete unit** as the hero proof (you’ve already built this muscle with the Early Algebra / sequenced unit emails):  
“Skip planning tonight — full unit live.”

### Membership page clarity

Keep four tiers, but visually force a choice:

1. **Teacher** = default / most popular  
2. **School** = “buying for a department?”  
3. Lite / Student collapsed under “Also available”

Every FAQ answer should end with a CTA, not just information.

---

## Lever 3 — School membership (the £55k unlock)

Target: **~70 school memberships** in the balanced mix (~£27.7k) plus teachers for the rest.

### Who to sell

- Heads of Maths / KS3–4 coordinators  
- Schools already using free schemes of work  
- Departments where **2+ teachers** download as individuals (obvious upgrade)

### Offer that makes the PO easy

School £395 is strong value if framed as:

- Access for **every maths teacher** at the school  
- Shared schemes + consistent lesson quality  
- Less than the cost of **one cover day** / one textbook pack  

Ship a one-page PDF: “Department planning pack” — what’s included, sample unit, PO form link, academic-year pricing.

### Outreach that fits a teaching-side hustle

Weekly cadence (2–3 hours):

1. Export schools/teachers who hit schemes repeatedly (or reply to contact form / email list tags)  
2. Short personal email from you (not a blast):  
   “Your team is using the Y8/Y9 schemes — here’s school access so the whole department can download lessons.”  
3. Follow up once after 7 days with the PO form

Do **not** rely on the website alone for £395 sales. High-ticket needs human follow-up.

### Academic calendar spikes

Push school hardest in:

- **Late August – mid September** (timetables + planning)  
- **January** (second-term reset)  
- **April/May** (next-year budget conversations)

---

## Lever 4 — Retention & list conversion (money you already own)

You already run Zoho Campaigns to active + inactive members. Treat the list as a revenue product.

### Weekly member email (non-negotiable)

One email per week, same structure:

1. **Preview text that sells the outcome** (“Skip planning tonight…”)  
2. **One unit / 3–5 assets** with clear premium vs free paths  
3. **Inactive → active CTA** (membership or login)  
4. Short teaching insight (keeps opens high)

Segment:

| Segment | Goal | CTA |
|---------|------|-----|
| Paying Teacher/School | Usage + renewal | Open this week’s unit |
| Lapsed / cancelled | Win-back | “Your schemes are updated — restart for £49.95” |
| Free / guest list | Convert | Free sample → Teacher membership |
| Multi-teacher same school domain | Upgrade | School membership |

### Reactivation sequence (high ROI)

For lapsed members, 3 emails over 10 days:

1. What’s new since they left  
2. One full sequenced unit preview  
3. Deadline / academic-year reason to restart

Even a **10–15% win-back** on a modest lapsed pool can add thousands with almost no new traffic.

### Renewal reminders

Start renewal emails at **day −30, −14, −7, +3** (grace).  
Include “what you used this year” if you can (lessons downloaded / favourites).

---

## Lever 5 — SEO scale (your new skill, used commercially)

You’re better at SEO than last year. Point it at **money keywords**, not only teaching essays.

### Keyword buckets that buy memberships

| Bucket | Examples | Page job |
|--------|----------|----------|
| Planning intent | “KS3 maths scheme of work”, “GCSE maths medium term plan” | Free scheme → member lessons |
| Lesson intent | “teaching bearings GCSE”, “ratio and proportion KS3” | Free method + member full lesson |
| Problem / exam | “GCSE problem solving lessons”, topic + worksheet | Sample Q → full pack |
| Comparison / category | “maths teaching resources UK”, “secondary maths worksheets” | Membership landing support |

### Content system (sustainable full-time rhythm)

When you go deeper than evenings:

- **2 SEO articles / week** that each unlock or support a member lesson  
- **1 “what’s new” update / month** (already working — keep it)  
- Internal links: every new blog → related scheme → membership  

Rule: no orphan blog posts. If it ranks, it must sell.

### YouTube + Bluesky as SEO amplifiers

You already use both. Keep them as **distribution**, not separate businesses:

- YouTube: 1 short teaching clip → link lesson + membership in description  
- Bluesky: puzzle/hook → blog → membership soft CTA (you’ve tested puzzle threads; keep that pattern)  
- Pin membership CTA in channel/about where appropriate

Avoid spreading into new platforms until weekly email + school outreach + SEO money pages are consistent.

---

## Pricing & packaging (optional upgrades once conversion is healthy)

Do these **after** funnel fixes, not instead of them:

1. **School tier clarity** — “up to X teachers” vs whole-school (reduces friction for small departments)  
2. **Department add-on** — Teacher members at same school get a one-click upgrade credit toward £395  
3. **Slight Teacher price test** — £54.95 or £59.95 if conversion stays stable (small % lift × volume matters)  
4. Keep Lite as a downsell, not the hero — it can cannibalise Teacher if promoted too hard

---

## Full-time operating rhythm (what “next level” looks like)

When evenings become your day job, protect time for revenue work — not only resource creation.

### Suggested weekly split (~35–40 hrs)

| Block | Hours | Work |
|-------|------:|------|
| Product | 12–15 | New lessons / updates (your moat) |
| SEO & site | 6–8 | Money pages, internal links, CRO |
| Email | 3–4 | Weekly campaign + segments |
| School sales | 3–4 | Outreach, POs, follow-ups |
| Video / social | 3–4 | 1 YT + 3–5 Bluesky from existing assets |
| Admin / support | 3–4 | Access, schools, renewals |

**Rule of thumb:** if a week has only product and no email/school/CRO, you’re building a library, not a business.

---

## 90-day sprint (do this before anything fancy)

### Days 1–30 — Finish crawl recovery + stop commercial leaks

- [ ] Cloudflare: confirm zero Block/Challenge on Googlebot/Bingbot in Security Events  
- [ ] GSC live URL test on top 10 money pages; fix any fetch failures before more indexing requests  
- [ ] Pages report triage; request indexing only for important “not indexed” URLs (10–20/day)  
- [ ] Next “What’s new” post links a cluster of still-recovering lessons  
- [ ] Rewrite titles/meta for top 10 high-impression / low-CTR pages still indexed  
- [ ] Audit top 20 landing pages by clicks; add membership CTA block  
- [ ] Rewrite membership page to force Teacher vs School choice  
- [ ] Ship trial **or** term option  
- [ ] Segment Zoho: active / lapsed / free / multi-teacher domains  
- [ ] Send weekly email without fail (4 emails)

### Days 31–60 — School channel

- [ ] One-page school PDF + PO path tested end-to-end  
- [ ] 25 personal school/HoD emails  
- [ ] Win-back sequence to lapsed members  
- [ ] Publish 4 SEO posts tied to member units

### Days 61–90 — Scale what worked

- [ ] Double down on the CTA/page that converted best  
- [ ] 25 more school outreaches  
- [ ] September (or next term) campaign calendar locked  
- [ ] Review: revenue run-rate vs £14k Q1 checkpoint

---

## Metrics to watch (simple dashboard)

Track monthly in a sheet:

1. **Membership revenue** (and by tier)  
2. **New Teacher / School / Lite / Student counts**  
3. **Churn / failed renewals**  
4. **Email:** send → open → click → purchase  
5. **Top 10 pages:** sessions → add-to-cart → purchase  
6. **School pipeline:** contacted / PO sent / closed  

If traffic rises but add-to-cart doesn’t, fix CRO.  
If carts rise but revenue stalls, fix price mix (push School) or checkout friction.  
If revenue rises then falls, fix retention.

---

## What not to do

- Don’t rebuild the whole site before fixing CTAs and email  
- Don’t add lots of new free downloads without a paid next step  
- Don’t chase every social network  
- Don’t underprice school access to “be nice” — £395 is already department-friendly  
- Don’t wait for perfect analytics; ship the weekly email and school PDF this month

---

## Bottom line

£55k is **~70 schools + ~520 teachers** (or an equivalent mix)—not a mystery growth hack.

GSC shows a real niche SEO engine (~5k clicks/month, strong UK desktop demand), not 800k monthly visits. The next level is operational:

1. Harvest CTR on pages that already rank  
2. Convert those clicks into Teacher/School memberships  
3. Sell departments on purpose  
4. Email every week like it’s a product launch  

Do that consistently for a full academic year and full-time becomes a numbers problem you can manage—not a leap of faith.
