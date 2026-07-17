# Daily ops system — Mr Mathematics (to mid-August)

Ambitious weekday loop tied to `three-month-sales-plan.md`.

## How it works

```
Morning (automation)     →  writes daily-ops/today.md
You work the list        →  tick Done / Partial / Not done
Evening (you + agent)    →  append daily-ops/log/YYYY-MM-DD.md
                         →  update daily-ops/state.md
Next morning             →  reads state + last log → new today.md
```

## Cursor Automations to create

Go to [Cursor Automations](https://cursor.com/automations) (or Dashboard → Automations) and create **two** automations on repo `robo00123/triangle_level1`, branch `cursor/full-time-income-strategy-a2b2` (or `main` once merged).

### 1) Morning — “Mr Math Daily Plan” (weekdays 07:30 UK)

**Trigger:** Schedule — Monday–Friday 07:30 Europe/London  

**Prompt:** paste contents of `daily-ops/templates/automation-morning.md`

**Expect:** agent commits an updated `daily-ops/today.md` and a short message with today’s 6–8 tasks.

### 2) Evening — “Mr Math EOD Close” (weekdays 18:00 UK) — optional schedule

You can run this manually by opening the Cloud Agent / chat and pasting:

> Process my EOD using `daily-ops/templates/automation-eod.md`. Here is my feedback: …

Or schedule 18:00 and always reply in-thread with the filled EOD block from `today.md`.

---

## Ambition standard (Month 1: now → 15 Aug)

A full day is **~7.5–8.5 deep-work hours**, not busywork:

| Slot | Hours | Bar for “Done” |
|------|------:|----------------|
| GSC / reindex | 1.0 | 8 URLs requested + notes |
| CTR harvest | 1.5 | 8–10 titles/meta live + indexed |
| Deep refurb | 3.5–4.0 | On refurb days: **1 complete SME/TSL-quality post** shipped (guide + worksheet + CTA + Yoast) |
| Conversion prep | 1.5 | Membership/school/email asset moved forward measurably |
| Distribution / admin | 0.5 | Bluesky or YT from a shipped asset, or CF/GSC check |

**Refurb days:** Tue + Thu (sometimes Mon if ahead)  
**Title+conversion days:** Mon, Wed, Fri  
**No ROTD** until week of 11 Aug.

If a task is Partial, next day starts by finishing it before new stretch work.

## Files

| File | Role |
|------|------|
| `state.md` | Living backlog, phase, carryovers, metrics |
| `today.md` | Today’s ambitious checklist (overwrite each morning) |
| `log/YYYY-MM-DD.md` | EOD record |
| `templates/*` | Automation prompts + EOD form |

## Start tomorrow

1. Create the Morning automation with the morning template.  
2. Open `daily-ops/today.md` — Day 1 plan is already seeded.  
3. Work it; at EOD fill the feedback block and run the EOD prompt.  
4. Push/commit so the next automation sees fresh state.
