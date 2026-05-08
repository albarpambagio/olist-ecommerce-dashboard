# Phase 8: Polish & Packaging Checklist

## Integration Plan Status (Completed 2026-05-08)

- [x] README rewritten with 5 sections (Background, Data Structure, Executive Summary, Insights Deep Dive, Recommendations)
- [x] CLEAN Framework formalized in `logs/phase2_cleaning_eda.log.md`
- [x] SCAN Framework + North Star added to `logs/insights.md`
- [x] DASH Framework documented in `docs/dash_framework.md` (new)
- [x] README Recommendations categorized (Market Context, Areas for Investigation, Actionable)
- [x] Framework structure integrated without explicit naming in portfolio README
- [x] North Star Metrics section added to `README.md`
- [x] Metrics by Stakeholder Team table added to `README.md`
- [x] Sales Mix concept added to `README.md` Insights Deep Dive
- [x] Sales Mix SQL added to `sql/phase4_kpis.py` (kpi_sales_mix view)
- [x] Metrics prioritization added to `logs/insights.md`
- [x] Sales Mix added to `docs/dash_framework.md`

## Dashboard Design Checklist

- [x] Consistent color palette across all pages (pick 2-3 colors max)
- [x] All axis labels are readable (font size ≥ 11pt)
- [x] No chart titles that just restate the chart type ("Bar Chart") — use business question
- [x] KPI cards show comparison context (vs. prior period or vs. target)
- [x] Slicers are clearly labeled and visible
- [x] No chart uses more than 6 colors at once
- [x] Remove all gridlines except necessary reference lines
- [x] Page navigation buttons between pages
- [x] A text box on each page with a 1-sentence "so what" of that page

## GitHub Repo Checklist

- [x] README.md structured as stakeholder report (5 sections)
- [x] `/sql/` folder with all SQL scripts (fact table, dimensions, RFM, cohort)
- [ ] `/screenshots/` folder with dashboard page images (POWER BI — BY USER)
- [ ] `.pbix` file available (POWER BI — BY USER)
- [x] Data source clearly credited (Olist via Kaggle)
- [x] Insights visible within 1 click of landing on the repo

## Portfolio Ready Checklist

- [x] SQL data pipeline automated (Python scripts)
- [x] Star schema designed and implemented
- [x] RFM segmentation working
- [x] Cohort retention analysis working
- [x] KPIs defined with formulas
- [x] DAX measures documented
- [x] README tells a story (5 sections, insights categorized)
- [ ] Dashboard screenshots added (POWER BI — BY USER)
- [ ] `.pbix` file available (POWER BI — BY USER)

---
**Status:** Integration complete. Power BI screenshots/.pbix by user to finalize.