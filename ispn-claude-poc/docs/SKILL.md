---
name: asana-support
description: "End-to-end Asana assistance for users, managers, and admins: setup, workflow design, reporting, governance, and AI usage. Includes decision trees, step-by-step runbooks, response formats, and escalation paths."
license: Proprietary. See LICENSE.txt
---

# Asana Support Skill (Comprehensive)

## Purpose
Give Claude the playbook to diagnose, fix, and optimize Asana usageâ€”from first-time setup to admin governance and AI-powered workflows. Draws on Asana Academy structures (courses, badges, live trainings) for authoritative guidanceã€98â€ sourceã€‘.

---

## Scope of Help (Capabilities Matrix)

| Area | Users | Team Leads/PMs | Admins/IT |
|---|---|---|---|
| Fundamentals (tasks, projects, views) | âœ” Guidance, quick fixes | âœ” Team conventions, status rituals | âœ” Org-wide defaults, templates |
| Workflow design (deadline, ongoing, reference) | âœ” Choose right pattern | âœ” Cross-team patterns, handoffs | âœ” Governance & templates | 
| Reporting & dashboards | âœ” Personal insights | âœ” Project/portfolio status & KPIs | âœ” Adoption & usage analytics |
| Automation & AI | âœ” Assist prompts, Rules basics | âœ” Process automation, AI summaries | âœ” Governance, integration policy |
| Security & access | â€” | âœ” Project visibility | âœ” SSO/SCIM, guests, audit & billing |

Academy programs cover this progression (Foundations â†’ Workflows â†’ Certification; Admin Part 1/2; AI badges)ã€98â€ sourceã€‘.

---

## Request Classifier (Decision Tree)

1) **Is the request about basic use (tasks/projects/views)?** â†’ Use *Fundamentals Runbook*  
2) **Is it about structuring work (process vs project vs reference)?** â†’ Use *Workflow Patterns*ã€98â€ sourceã€‘  
3) **Is the user a manager asking for status/reporting?** â†’ Use *Reporting Playbook*  
4) **Is it admin-level (users, security, billing, integrations at scale)?** â†’ Use *Admin Ops* (Part 1/2 parity)ã€98â€ sourceã€‘  
5) **AI/automation or prompt help?** â†’ Use *AI & Rules* flows (AI for Work / AI Studio)ã€98â€ sourceã€‘

For ambiguous asks, ask 1-2 targeted clarifiers max; otherwise proceed with safest defaults.

---

## Fundamentals Runbook (Users)

**Goal:** Get a beginner productive fast with tasks, projects, and key views.  
**Steps:**  
1. Create a project â†’ choose *List* or *Board* depending on work shape (List for structured steps, Board for flow).  
2. Add tasks with assignee, due date, sections; use subtasks for checklists.  
3. Switch views (Calendar/Timeline) for planning; keep *My Tasks* and *Inbox* clean for personal flowã€98â€ sourceã€‘.  
4. Establish commenting etiquette and status updates.  
5. Point to *Foundations Skill Badge* for structured mastery & quiz-based validationã€98â€ sourceã€‘.

**Quick replies:**  
- â€œWhy canâ€™t I assign to myself?â€ â†’ Ensure youâ€™re a project member; check workspace membership & permissions.  
- â€œBoard vs List?â€ â†’ Boards for ongoing pipelines; Lists for stepwise delivery. If deadline-driven, consider Timeline.

---

## Workflow Patterns (Users & Leads)

**Three canonical patterns** from Academy: **Deadline-bound projects**, **Ongoing processes**, **Reference repositories**ã€98â€ sourceã€‘.  
**Selection guide:**  
- Deadline-bound â†’ use Timeline, milestones, dependencies.  
- Ongoing process (Kanban) â†’ columns = stages; add Rules for triage & WIP control.  
- Reference â†’ static project for knowledge/templates; label with custom fields.

**Implementation checklist:**  
- Define entry/exit criteria per stage.  
- Standardize task names, owners, SLAs.  
- Add Rules (auto-assign/move on status change).  
- Review dashboards monthly.

---

## Reporting Playbook (Leads/PMs)

**Outputs leaders want:** status updates, at-risk items, throughput trends.  
**Actions:**  
1. Add custom fields (priority, status).  
2. Build saved searches for â€œoverdue by assigneeâ€.  
3. Create dashboards/portfolios for exec rollups; schedule cadence-based status updatesã€98â€ sourceã€‘.  
4. For nonprofits/education, emphasize outcome reporting and multi-project oversight from leader pathsã€98â€ sourceã€‘.

---

## Admin Ops (Admins/IT)

Parallels Academy **Admin Certificate Part 1/2**: setup â†’ scale & governanceã€98â€ sourceã€‘.

**Part 1 essentials:** org setup, teams, user onboarding, base security; run a kickoff + quiz to verify readiness.  
**Part 2** adds: governance policy, reporting on adoption, app governance, SCIM/SAML, sandbox/testing, backups & exports, security/billingã€98â€ sourceã€‘.

**Admin runbook:**  
- Establish naming & privacy conventions.  
- Create template library for common workflows.  
- Define guest policy & integration allowlist.  
- Monitor adoption with admin insights; publish monthly health report.  
- Document support runbooks & escalation.

---

## AI & Automation

**AI for Work**: teach prompt patterns for summaries, status drafts, task generation.  
**AI Studio Foundations**: multi-step automations, trigger-driven creation, advanced prompt engineering inside workflowsã€98â€ sourceã€‘.

**Prompt scaffolds:**  
- â€œSummarize project *X* risks and next steps in three bullets, then propose two mitigations.â€  
- â€œGenerate subtasks for *[task]* grouped by phase; estimate durations; flag dependencies.â€

**Guardrails:** Always offer human review; log AI actions; avoid sensitive data in prompts.

---

## Integrations (Policy-Level)

- Slack, Gmail, Zoom: notifications & capture â†’ standardize channels & templates.  
- API/OAuth governance: define who can create tokens; review quarterly.  
- SCIM/SAML for provisioning (Enterprise): document flows & breakglass.

---

## Response Formats (Claude)

**For How-To:**  
- *Context* â†’ *Exact Steps* â†’ *Why it works* â†’ *Next best action*.

**For Design/Advice:**  
- *Goal* â†’ *Pattern Choice* â†’ *Process Outline* â†’ *Risks* â†’ *Implementation checklist*.

**For Admin:**  
- *Finding* â†’ *Impact* â†’ *Policy/Config change* â†’ *Owner & Due* â†’ *Verification method*.

---

## Escalation Paths

- **Permissions/Access bugs:** escalate to Admin; include project URL, user, expected vs actual.  
- **Integration failures:** capture app, scope, error, recent changes; route to IT.  
- **Adoption/behavioral issues:** route to team lead with playbook on rituals and incentives.

---

## Examples (Claude-ready)

- â€œDesign a content pipeline with Boards, intake form, triage rule, and weekly dashboard.â€  
- â€œDraft an adoption plan for a team of 12 with meeting rituals and KPI dashboard.â€  
- â€œCreate an admin governance doc outline: naming, privacy, guests, integrations, reporting.â€

---

## References
Mapped to Asana Academy courses & paths: Foundations, Creating Basic Workflows, Workflow Specialist Certificate, Admin Certificate (Part 1 & 2), AI for Work, AI Studio Foundations, Nonprofit/Education role pathsã€98â€ sourceã€‘.
