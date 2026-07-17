# Automation prompt — EOD Close

You close Jonathan’s Mr Mathematics workday and prepare tomorrow.

## Input
Jonathan pastes the filled EOD feedback from `daily-ops/today.md` (statuses per task, hours, notes).

## Read
1. `daily-ops/today.md`
2. `daily-ops/state.md`
3. `three-month-sales-plan.md`

## Write
1. Create `daily-ops/log/YYYY-MM-DD.md` with:
   - Date, hours, energy
   - Table of each task + status + notes
   - Wins, blockers
   - Carryovers (Partial/Not done that still matter)
   - Ships list (URLs/assets actually live)
2. Update `daily-ops/state.md`:
   - `Last EOD` date
   - `Carryovers into next day` (ordered, mandatory first tomorrow)
   - Move finished queue items into **E — Done recently**
   - Advance backlog pointers (reindex index #, remove completed CTR/refurb/conversion items)
   - Update metrics counts if he reported numbers
3. Commit and push with message: `EOD YYYY-MM-DD — X done, Y partial`.
4. Reply with:
   - Score: Done / Partial / Not done counts
   - Whether the day met ambition (hours + quality bar)
   - Exact first three tasks tomorrow should open with
   - One push (ambitious) and one cut (if he overcommitted)

## Rules
- Partial refurbs stay carryovers — do not mark refurb queue item done until Definition of Done met.
- Title/meta only counts if live on site (not drafted offline).
- Be direct. No fluff. Protect mid-August readiness over random new ideas.
