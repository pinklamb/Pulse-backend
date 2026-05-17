from datetime import date

TODAY = date(2026, 5, 16)

STAGE_MEDIANS_DAYS = {
    "Discovery": 14, "Demo": 10, "Proposal": 21,
    "Negotiation": 18, "Closing": 7,
}


def _parse(iso_str):
    if not iso_str:
        return None
    return date.fromisoformat(iso_str)


def _days_between(earlier_iso, later=TODAY):
    earlier = _parse(earlier_iso)
    if earlier is None:
        return None
    return (later - earlier).days



def rule_customer_silence(deal):
    #0-30 pts. Linear ramp: 0 days = 0pts, 30+ days = 30pts.
    days = _days_between(deal["last_customer_activity_date"])
    if days is None:
        return {"points": 30, "reason": "No record of customer activity"}
    if days <= 7:
      points = 0
    elif days <= 14:
        points = 10
    elif days <= 21:
        points = 20
    else:
        points = 30
    return {
        "points": points,
        "reason": f"Customer last replied {days} day{'s' if days != 1 else ''} ago",
    }


def rule_stage_stagnation(deal):
    #0-25 pts based on time in stage vs team median for that stage.
    days_in_stage = _days_between(deal["stage_entered_date"])
    median = STAGE_MEDIANS_DAYS.get(deal["stage"], 14)
    ratio = days_in_stage / median if median else 0

    if ratio <= 1.0:
        points = 0
    elif ratio <= 1.5:
        points = 8
    elif ratio <= 2.0:
        points = 15
    elif ratio <= 3.0:
        points = 22
    else:
        points = 25

    reason = (
        f"In {deal['stage']} for {days_in_stage} days "
        f"({ratio:.1f}x the {median}-day team median)"
    )
    return {"points": points, "reason": reason}


def rule_stale_next_step(deal):
    #0-15 pts. Missing = 10, past-due = 15, future = 0.
    next_step = deal.get("next_step")
    next_step_date = _parse(deal.get("next_step_date"))

    if not next_step or next_step.strip() == "":
        return {"points": 10, "reason": "No next step defined"}
    if next_step_date is None:
        return {"points": 10, "reason": "Next step has no due date"}

    delta = (next_step_date - TODAY).days
    if delta < 0:
        return {
            "points": 15,
            "reason": f"Next step '{next_step}' was due {abs(delta)} days ago",
        }
    return {
        "points": 0,
        "reason": f"Next step '{next_step}' on track (due in {delta} days)",
    }


def rule_single_threading(deal):
    #0-15 pts. 1 contact = 15, 2 = 8, 3+ = 0.
    contacts = deal.get("contacts_count", 0)
    if contacts <= 1:
        return {
            "points": 15,
            "reason": "Only 1 contact engaged — deal depends on a single relationship",
        }
    if contacts == 2:
        return {"points": 8, "reason": "Only 2 contacts engaged at the account"}
    return {"points": 0, "reason": f"{contacts} contacts engaged at the account"}


def rule_close_date_slipped(deal):
    #0-15 pts. Already-past close = 15, within 7 days w/ silence = 10.
    close_date = _parse(deal["expected_close_date"])
    delta = (close_date - TODAY).days
    silent_days = _days_between(deal["last_customer_activity_date"]) or 0

    if delta < 0:
        return {
            "points": 15,
            "reason": f"Expected close date passed {abs(delta)} days ago",
        }
    if delta <= 7 and silent_days >= 10:
        return {
            "points": 10,
            "reason": (
                f"Close date in {delta} days but customer silent for "
                f"{silent_days} days"
            ),
        }
    return {
        "points": 0,
        "reason": f"Close date in {delta} days, no immediate red flags",
    }


RULES = [
    ("customer_silence", rule_customer_silence),
    ("stage_stagnation", rule_stage_stagnation),
    ("stale_next_step", rule_stale_next_step),
    ("single_threading", rule_single_threading),
    ("close_date_slipped", rule_close_date_slipped),
]


def bucket(score):
    if score >= 66:
        return "red"
    if score >= 36:
        return "yellow"
    return "green"


def score_deal(deal):
    breakdown = []
    total = 0
    for name, rule_fn in RULES:
        result = rule_fn(deal)
        breakdown.append({
            "rule": name,
            "points": result["points"],
            "reason": result["reason"],
        })
        total += result["points"]
    return {
        "score": total,
        "bucket": bucket(total),
        "breakdown": breakdown,
    }



if __name__ == "__main__":
    import json
    from collections import Counter

    deals = json.load(open("deals.json"))
    profile_to_buckets = {"hero": Counter(), "red": Counter(),
                         "yellow": Counter(), "green": Counter()}

    for d in deals:
        result = score_deal(d)
        profile_to_buckets[d["_profile"]][result["bucket"]] += 1

    print("Validation: do scoring buckets match the profile labels?")
    print("(Hero deals should be red. Red profile → red. Yellow → yellow. Green → green.)\n")
    for profile in ["hero", "red", "yellow", "green"]:
        buckets = profile_to_buckets[profile]
        print(f"  {profile:7s}: {dict(buckets)}")

    print("\nTop 5 highest-risk deals:")
    scored = [(d, score_deal(d)) for d in deals]
    scored.sort(key=lambda x: x[1]["score"], reverse=True)
    for deal, result in scored[:5]:
        print(f"\n  {deal['id']}: {deal['account_name']} — ${deal['amount']:,} "
              f"({deal['_profile']} profile → score {result['score']}, "
              f"{result['bucket']})")
        for item in result["breakdown"]:
            print(f"    [{item['points']:2d}] {item['reason']}")