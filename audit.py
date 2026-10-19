#!/usr/bin/env python3
"""Asset audit tool: turns an IT asset register (CSV) into an audit report.

Flags:
  - devices not audited within the audit window (default 90 days)
  - leavers whose devices have not been returned
  - devices marked "in use" with no assigned user
  - macOS / Windows versions below a minimum supported version

Usage:
  python audit.py assets.csv --days 90 --out report.csv
"""
import argparse
import csv
from datetime import date, datetime

MIN_OS = {"macOS": (14, 0), "Windows": (11, 0)}


def parse_date(value):
    value = (value or "").strip()
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None


def parse_version(value):
    try:
        return tuple(int(p) for p in value.strip().split(".")[:2])
    except ValueError:
        return None


def check(row, today, window):
    issues = []
    last = parse_date(row.get("last_audit_date"))
    if last is None or (today - last).days > window:
        issues.append(f"Audit overdue (last: {last or 'never'})")
    leaver = parse_date(row.get("leaver_date"))
    if leaver and leaver <= today and row.get("status", "").lower() != "returned":
        issues.append(f"Leaver device not returned (left {leaver})")
    if row.get("status", "").lower() == "in use" and not row.get("assigned_to", "").strip():
        issues.append("In use but no assigned user")
    os_name = row.get("os", "").strip()
    minimum = MIN_OS.get(os_name)
    version = parse_version(row.get("os_version", ""))
    if minimum and version and version < minimum:
        issues.append(f"{os_name} {row['os_version']} below supported {'.'.join(map(str, minimum))}")
    return issues


def main():
    ap = argparse.ArgumentParser(description="Audit an IT asset register CSV.")
    ap.add_argument("register")
    ap.add_argument("--days", type=int, default=90, help="audit window in days")
    ap.add_argument("--out", default="audit_report.csv")
    args = ap.parse_args()

    today = date.today()
    flagged, total = [], 0
    with open(args.register, newline="") as f:
        for row in csv.DictReader(f):
            total += 1
            for issue in check(row, today, args.days):
                flagged.append({"asset_tag": row.get("asset_tag"),
                                "assigned_to": row.get("assigned_to") or "-",
                                "issue": issue})

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["asset_tag", "assigned_to", "issue"])
        w.writeheader()
        w.writerows(flagged)

    devices = len({r["asset_tag"] for r in flagged})
    print(f"Checked {total} devices. {devices} need attention ({len(flagged)} issues).")
    for r in flagged:
        print(f"  {r['asset_tag']:<10} {r['assigned_to']:<18} {r['issue']}")
    print(f"Report saved to {args.out}")


if __name__ == "__main__":
    main()
