# Asset Audit Tool

A small Python script that turns an IT asset register into an audit report, based on the kind of laptop and equipment register I maintain in my support role.

## What it flags
- Devices not audited within the audit window (default 90 days)
- Leavers whose devices have not been returned
- Devices marked "in use" with no assigned user
- macOS or Windows versions below a minimum supported version

## Run it
```
python audit.py sample_assets.csv --days 90 --out audit_report.csv
```
No external libraries needed, standard Python 3 only.

## Why
Manual audits miss things. This makes onboarding, offboarding and audit checks repeatable, so nothing slips through when people join or leave.
