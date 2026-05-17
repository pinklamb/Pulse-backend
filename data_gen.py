#Here I'm just generating CRM behavior for demo 

import json
import random
from datetime import date, timedelta

random.seed(42)  # reproducible demos

TODAY = date(2026, 5, 16)

STAGES = ["Discovery", "Demo", "Proposal", "Negotiation", "Closing"]
STAGE_WEIGHTS = [0.25, 0.20, 0.20, 0.25, 0.10]
STAGE_MEDIANS_DAYS = {
    "Discovery": 14, "Demo": 10, "Proposal": 21,
    "Negotiation": 18, "Closing": 7,
}

REPS = [
    "Sarah Chen", "Marcus Webb", "Priya Patel", "James O'Connor",
    "Aisha Johnson", "Diego Ramirez", "Emma Larsson", "Ryan Kim",
    "Nicole Brennan", "Tomás Silva",
]

COMPANY_PREFIXES = [
    "North", "Apex", "Blue", "Iron", "Summit", "Cascade", "Vertex", "Orbit",
    "Helix", "Pioneer", "Granite", "Meridian", "Quantum", "Beacon", "Sterling",
    "Cedar", "Lumen", "Forge", "Nimbus", "Cobalt", "Drift", "Sable", "Crest",
    "Echo", "Polar", "Onyx", "Sage", "River", "Tundra", "Vega",
]
COMPANY_SUFFIXES = [
    "Logistics", "Robotics", "Analytics", "Industries", "Systems", "Networks",
    "Dynamics", "Labs", "Health", "Capital", "Technologies", "Bioscience",
    "Manufacturing", "Solutions", "Partners", "Software", "Energy", "Group",
    "Studios", "Holdings",
]


def fake_company():
    return f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}"


def days_ago(n):
    return (TODAY - timedelta(days=n)).isoformat()


def make_emails(days_since_customer, days_since_rep, stage, account, has_proposal=False):
    """Realistic email thread, customer most-recent or rep most-recent."""
    emails = []
    if has_proposal:
        emails.append({
            "date": days_ago(days_since_customer + 21),
            "from": "rep",
            "snippet": f"Attached the proposal for {account}. Happy to walk through pricing whenever works.",
        })
    if stage in ("Negotiation", "Closing"):
        emails.append({
            "date": days_ago(days_since_customer + 10),
            "from": "customer",
            "snippet": "Need to loop in our finance team before we can move forward. Will circle back.",
        })
    emails.append({
        "date": days_ago(days_since_customer),
        "from": "customer",
        "snippet": random.choice([
            "Thanks for sending this over. Let me discuss internally and get back to you.",
            "Appreciate the follow-up. We're heads-down on Q2 planning — give us a couple weeks.",
            "Got it, will review with the team.",
            "Let me check on budget timing and revert.",
        ]),
    })
    emails.append({
        "date": days_ago(days_since_rep),
        "from": "rep",
        "snippet": random.choice([
            "Just checking in — happy to hop on a quick call if helpful.",
            "Following up on my last note. Any update on next steps?",
            "Wanted to make sure this didn't get buried. Let me know if you have questions.",
            "Circling back — should we plan a sync this week?",
        ]),
    })
    return emails[-4:]  # cap at 4 for UI


def make_deal(deal_id, profile):
    """profile in {'green','yellow','red','hero'}"""
    account = fake_company()
    owner = random.choice(REPS)
    stage = random.choices(STAGES, STAGE_WEIGHTS)[0]
    median = STAGE_MEDIANS_DAYS[stage]

    if profile == "green":
        amount = random.choice([15, 20, 25, 35, 50, 75]) * 1000
        days_in_stage = random.randint(2, int(median * 0.9))
        days_since_customer = random.randint(1, 7)
        days_since_rep = random.randint(0, 3)
        next_step_offset = random.randint(2, 10)  # future
        next_step = random.choice([
            "Schedule follow-up call", "Send pricing details",
            "Demo for technical team", "Review with procurement",
            "Finalize contract terms",
        ])
        contacts = random.randint(2, 5)
        close_offset = random.randint(15, 90)

    elif profile == "yellow":
        amount = random.choice([20, 30, 45, 60, 80]) * 1000
        days_in_stage = random.randint(int(median * 1.2), int(median * 2))
        days_since_customer = random.randint(10, 20)
        days_since_rep = random.randint(3, 8)
        next_step_offset = random.choice([random.randint(-3, -1), random.randint(1, 5)])
        next_step = random.choice([
            "Awaiting customer feedback", "Send revised proposal",
            "Follow up on pricing", "Re-engage stakeholder",
        ])
        contacts = random.randint(1, 2)
        close_offset = random.randint(-5, 30)

    elif profile == "red":
        amount = random.choice([40, 60, 80, 100]) * 1000
        days_in_stage = random.randint(int(median * 2.2), int(median * 3.5))
        days_since_customer = random.randint(25, 60)
        days_since_rep = random.randint(8, 20)
        next_step_offset = random.randint(-25, -5)
        next_step = random.choice([
            "Send revised proposal", "Schedule call with CFO",
            "Re-engage after silence", "",
        ])
        contacts = 1
        close_offset = random.randint(-20, 7)

    else:  # hero — high-stakes, very obviously slipping
        amount = random.choice([95, 120, 150]) * 1000
        stage = random.choice(["Proposal", "Negotiation"])
        median = STAGE_MEDIANS_DAYS[stage]
        days_in_stage = int(median * random.uniform(2.5, 3.2))
        days_since_customer = random.randint(28, 45)
        days_since_rep = random.randint(10, 18)
        next_step_offset = random.randint(-18, -8)
        next_step = "Send revised proposal"
        contacts = 1
        close_offset = random.randint(-10, 5)

    stage_entered = TODAY - timedelta(days=days_in_stage)
    created = stage_entered - timedelta(days=random.randint(10, 60))
    expected_close = TODAY + timedelta(days=close_offset)
    next_step_date = TODAY + timedelta(days=next_step_offset) if next_step else None

    return {
        "id": f"DEAL-{deal_id:04d}",
        "account_name": account,
        "owner": owner,
        "amount": amount,
        "stage": stage,
        "created_date": created.isoformat(),
        "expected_close_date": expected_close.isoformat(),
        "stage_entered_date": stage_entered.isoformat(),
        "last_customer_activity_date": days_ago(days_since_customer),
        "last_internal_activity_date": days_ago(days_since_rep),
        "next_step": next_step,
        "next_step_date": next_step_date.isoformat() if next_step_date else None,
        "contacts_count": contacts,
        "recent_emails": make_emails(
            days_since_customer, days_since_rep, stage, account,
            has_proposal=stage in ("Proposal", "Negotiation", "Closing"),
        ),
    
    }


def generate(n=200):
    deals = []
    # 3 hero deals first (IDs 1-3 for easy demo memory)
    for i in range(1, 4):
        deals.append(make_deal(i, "hero"))
    # Rest of the population
    counts = {"red": int(n * 0.10) - 3, "yellow": int(n * 0.20), "green": 0}
    counts["green"] = n - 3 - counts["red"] - counts["yellow"]
    next_id = 4
    for profile, count in counts.items():
        for _ in range(count):
            deals.append(make_deal(next_id, profile))
            next_id += 1
    rest = deals[3:]
    random.shuffle(rest)
    deals = deals[:3] + rest # mix non-hero deals; heroes stay near top by id
    return deals


if __name__ == "__main__":
    deals = generate(200)
    with open("deals.json", "w") as f:
        json.dump(deals, f, indent=2, default=str)
    profiles = {}
    for d in deals:
        profiles[d["_profile"]] = profiles.get(d["_profile"], 0) + 1
    total_amount = sum(d["amount"] for d in deals)
    print(f"Generated {len(deals)} deals → deals.json")
    print(f"Distribution: {profiles}")
    print(f"Total pipeline: ${total_amount:,}")
    print(f"\nHero deals (your demo stars):")
    for d in deals[:3]:
        print(f"  {d['id']}: {d['account_name']} — ${d['amount']:,} ({d['stage']}, owner: {d['owner']})")