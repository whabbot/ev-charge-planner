#!/usr/bin/env python3
"""Milestone 1: pick cheapest / lowest-carbon half-hours until departure.

Uses Octopus Agile unit rates and NESO Carbon Intensity (regional by outward postcode).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from zoneinfo import ZoneInfo

UK = ZoneInfo("Europe/London")
AGILE_PRODUCT = "AGILE-24-10-01"
# GSP letter -> Octopus tariff region suffix (common mapping)
GSP_BY_OUTWARD_PREFIX = {
    # rough defaults; override with --gsp when known
}


@dataclass(frozen=True)
class Slot:
    start: datetime
    end: datetime
    price_p_kwh: float | None
    intensity_g: float | None

    @property
    def hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600.0


def _get_json(url: str) -> dict | list:
    req = urllib.request.Request(
        url, headers={"User-Agent": "smart-ev-charge-planner/0.1"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def parse_iso(s: str) -> datetime:
    s = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def outward_code(postcode: str) -> str:
    pc = postcode.strip().upper().replace(" ", "")
    if len(pc) < 2:
        raise SystemExit("postcode too short")
    # outward is all but last 3 inward chars
    if len(pc) > 3:
        return pc[:-3]
    return pc


def resolve_gsp(gsp: str | None) -> str:
    letter = (gsp or "C").strip().upper()
    if len(letter) != 1 or not letter.isalpha():
        raise SystemExit(
            "--gsp must be a single letter (Octopus region), e.g. C for London"
        )
    return letter


def fetch_agile_rates(
    gsp: str, period_from: datetime, period_to: datetime
) -> list[Slot]:
    tariff = f"E-1R-{AGILE_PRODUCT}-{gsp}"
    base = (
        f"https://api.octopus.energy/v1/products/{AGILE_PRODUCT}/"
        f"electricity-tariffs/{tariff}/standard-unit-rates/"
    )
    params = {
        "period_from": period_from.astimezone(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "period_to": period_to.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "page_size": "1500",
    }
    url = base + "?" + urllib.parse.urlencode(params)
    try:
        data = _get_json(url)
    except urllib.error.HTTPError as e:
        raise SystemExit(
            f"Octopus Agile fetch failed ({e.code}) for tariff {tariff}: {e.reason}"
        ) from e
    slots: list[Slot] = []
    for row in data.get("results", []):
        slots.append(
            Slot(
                start=parse_iso(row["valid_from"]),
                end=parse_iso(row["valid_to"]),
                price_p_kwh=float(row["value_inc_vat"]),
                intensity_g=None,
            )
        )
    slots.sort(key=lambda s: s.start)
    return slots


def fetch_carbon_slots(outward: str, period_from: datetime) -> list[Slot]:
    # Try outward; if 400, try common longer forms is caller's job. Falls back to national.
    from_s = period_from.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    regional_url = (
        f"https://api.carbonintensity.org.uk/regional/intensity/{from_s}/fw48h/postcode/"
        f"{urllib.parse.quote(outward)}"
    )
    national_url = f"https://api.carbonintensity.org.uk/intensity/{from_s}/fw48h"
    label = outward
    try:
        data = _get_json(regional_url)
        block = data.get("data")
        if isinstance(block, dict):
            rows = block.get("data", [])
            label = block.get("shortname") or outward
        else:
            raise ValueError("unexpected regional shape")
        source = f"regional:{label}"
    except Exception:
        data = _get_json(national_url)
        rows = data.get("data", [])
        source = "national"
        label = "GB"
    slots: list[Slot] = []
    for row in rows:
        intensity = row.get("intensity") or {}
        forecast = intensity.get("forecast")
        if forecast is None:
            continue
        slots.append(
            Slot(
                start=parse_iso(
                    row["from"] if "T" in row["from"] else row["from"] + "Z"
                ),
                end=parse_iso(row["to"] if "T" in row["to"] else row["to"] + "Z"),
                price_p_kwh=None,
                intensity_g=float(forecast),
            )
        )
    slots.sort(key=lambda s: s.start)
    return slots, source, label  # type: ignore[return-value]


def merge_slots(price_slots: list[Slot], carbon_slots: list[Slot]) -> list[Slot]:
    # index carbon by start
    by_start = {s.start: s for s in carbon_slots}
    merged: list[Slot] = []
    for p in price_slots:
        c = by_start.get(p.start)
        # tolerate 1-minute drift / formatting
        if c is None:
            for cs in carbon_slots:
                if abs((cs.start - p.start).total_seconds()) < 60:
                    c = cs
                    break
        merged.append(
            Slot(
                start=p.start,
                end=p.end,
                price_p_kwh=p.price_p_kwh,
                intensity_g=c.intensity_g if c else None,
            )
        )
    return merged


def window_filter(slots: Iterable[Slot], now: datetime, depart: datetime) -> list[Slot]:
    out = []
    for s in slots:
        if s.end <= now:
            continue
        if s.start >= depart:
            continue
        if s.end > depart:
            # truncate conceptually by skipping partials for v1 (half-hour independence)
            continue
        out.append(s)
    return out


def pick_slots(slots: list[Slot], n: int, key) -> list[Slot]:
    ranked = sorted(slots, key=key)
    return sorted(ranked[:n], key=lambda s: s.start)


def fmt_slot(s: Slot) -> str:
    local_s = s.start.astimezone(UK).strftime("%a %H:%M")
    local_e = s.end.astimezone(UK).strftime("%H:%M")
    price = f"{s.price_p_kwh:6.2f}p" if s.price_p_kwh is not None else "   n/a"
    carbon = f"{s.intensity_g:5.0f}g" if s.intensity_g is not None else "  n/a"
    return f"  {local_s}-{local_e}  {price}/kWh  {carbon}CO2/kWh"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Smart EV Charge Planner — rates CLI (milestone 1)"
    )
    p.add_argument(
        "--kwh-needed", type=float, required=True, help="Energy still needed (kWh)"
    )
    p.add_argument(
        "--charge-kw",
        type=float,
        default=7.4,
        help="Fixed charge rate kW (default 7.4)",
    )
    p.add_argument(
        "--depart-at",
        required=True,
        help="Departure time ISO, e.g. 2026-10-11T08:00 or with offset",
    )
    p.add_argument(
        "--postcode", default="SW1A 1AA", help="UK postcode (outward used for carbon)"
    )
    p.add_argument(
        "--gsp",
        default="C",
        help="Octopus GSP letter for Agile tariff (default C=London)",
    )
    p.add_argument(
        "--now", default=None, help="Override now (ISO) for reproducible runs"
    )
    args = p.parse_args(argv)

    if args.kwh_needed < 0:
        raise SystemExit("kwh-needed must be >= 0")
    if args.charge_kw <= 0:
        raise SystemExit("charge-kw must be > 0")

    now = parse_iso(args.now) if args.now else datetime.now(timezone.utc)
    depart_raw = args.depart_at.strip()
    if depart_raw.endswith("Z") or "+" in depart_raw[10:] or depart_raw.count("-") > 2:
        depart = parse_iso(depart_raw)
    else:
        # interpret naive as Europe/London
        depart = (
            datetime.fromisoformat(depart_raw)
            .replace(tzinfo=UK)
            .astimezone(timezone.utc)
        )

    if depart <= now:
        raise SystemExit("depart-at must be in the future relative to now")

    hours_needed = args.kwh_needed / args.charge_kw
    slots_needed = (
        int(math.ceil(hours_needed / 0.5 - 1e-12)) if args.kwh_needed > 0 else 0
    )

    outward = outward_code(args.postcode)
    gsp = resolve_gsp(args.gsp)

    period_to = max(depart, now)
    # Agile often publishes ~next day; pull a generous window
    price_slots = fetch_agile_rates(gsp, now, depart)
    carbon_slots, carbon_source, carbon_label = fetch_carbon_slots(outward, now)  # type: ignore[misc]
    merged = merge_slots(price_slots, carbon_slots)
    available = window_filter(merged, now, depart)

    print(f"Smart EV Charge Planner — rates CLI")
    print(f"Now (UK):     {now.astimezone(UK).strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"Depart (UK):  {depart.astimezone(UK).strftime('%Y-%m-%d %H:%M %Z')}")
    print(
        f"Need:         {args.kwh_needed:.2f} kWh at {args.charge_kw:.2f} kW → {slots_needed} half-hour slot(s)"
    )
    print(
        f"Agile:        {AGILE_PRODUCT} region {gsp} ({len(price_slots)} rates fetched)"
    )
    print(f"Carbon:       {carbon_source} ({carbon_label}); postcode outward {outward}")
    print(f"Usable slots before departure: {len(available)}")

    if args.kwh_needed == 0:
        print("\nAlready full / empty need — nothing to schedule.")
        return 0

    if slots_needed > len(available):
        print(
            f"\nWarning: only {len(available)} slots before departure, "
            f"need {slots_needed}. Using all available."
        )
        n = len(available)
    else:
        n = slots_needed

    priced = [s for s in available if s.price_p_kwh is not None]
    carboned = [s for s in available if s.intensity_g is not None]

    cost_plan = pick_slots(priced, n, key=lambda s: (s.price_p_kwh, s.start))
    carbon_plan = pick_slots(carboned, n, key=lambda s: (s.intensity_g, s.start))

    def totals(plan: list[Slot], field: str) -> tuple[float, float]:
        # each slot charges charge_kw * 0.5 kWh
        kwh = args.charge_kw * 0.5 * len(plan)
        if field == "cost":
            pence = sum((s.price_p_kwh or 0.0) * args.charge_kw * 0.5 for s in plan)
            return kwh, pence / 100.0
        grams = sum((s.intensity_g or 0.0) * args.charge_kw * 0.5 for s in plan)
        return kwh, grams

    # charge-now baseline: earliest N slots
    baseline = sorted(available, key=lambda s: s.start)[:n]

    print("\n=== Cost-optimal slots ===")
    for s in cost_plan:
        print(fmt_slot(s))
    kwh_c, pounds = totals(cost_plan, "cost")
    _, grams_c = totals(cost_plan, "carbon")
    print(f"  Totals: {kwh_c:.2f} kWh, £{pounds:.2f}, {grams_c:.0f} gCO2")

    print("\n=== Carbon-optimal slots ===")
    for s in carbon_plan:
        print(fmt_slot(s))
    kwh_g, pounds_g = totals(carbon_plan, "cost")
    _, grams_g = totals(carbon_plan, "carbon")
    print(f"  Totals: {kwh_g:.2f} kWh, £{pounds_g:.2f}, {grams_g:.0f} gCO2")

    print("\n=== Charge-now baseline (earliest slots) ===")
    for s in baseline:
        print(fmt_slot(s))
    kwh_b, pounds_b = totals(baseline, "cost")
    _, grams_b = totals(baseline, "carbon")
    print(f"  Totals: {kwh_b:.2f} kWh, £{pounds_b:.2f}, {grams_b:.0f} gCO2")

    if pounds_b > 0:
        save = pounds_b - pounds
        print(
            f"\nVs charge-now: cost plan saves £{save:.2f}; carbon plan is {grams_b - grams_g:.0f} gCO2 lower."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
