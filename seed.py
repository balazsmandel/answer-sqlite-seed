#!/usr/bin/env python3
"""Fills a freshly installed Apache Answer with two years' worth of made-up company Q&A content
through its own HTTP API, so the data is exactly what the application itself writes.
Deterministic (fixed random seed). Standard library only.

usage: seed.py BASE_URL ADMIN_EMAIL ADMIN_PASSWORD [OUT_JSON]
OUT_JSON receives the accounts, tokens and API keys that exist afterwards (for whoever wants to check things later).
"""
import json, random, sys, time, urllib.request, urllib.error

BASE, ADMIN_EMAIL, ADMIN_PASS = sys.argv[1].rstrip("/"), sys.argv[2], sys.argv[3]
OUT = sys.argv[4] if len(sys.argv) > 4 else "seed-accounts.json"
rnd = random.Random(20241118)

def call(method, path, body=None, token=None, ok=(200,)):
    req = urllib.request.Request(BASE + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json", **({"Authorization": token} if token else {})})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read() or b"{}").get("data")
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf8", "replace")
            if e.code == 429 or "captcha" in text.lower():
                time.sleep(2 + attempt * 3); continue
            raise SystemExit(f"{method} {path} -> {e.code}: {text[:300]}")
    raise SystemExit(f"{method} {path}: still rejected after retries")

def login(email, password):
    return call("POST", "/answer/api/v1/user/login/email", {"e_mail": email, "pass": password})["access_token"]

admin = login(ADMIN_EMAIL, ADMIN_PASS)
# site settings the owner changed over time
call("PUT", "/answer/admin/api/siteinfo/general", {"name": "Acme Engineering Q&A", "short_description": "Ask the people who run it",
     "description": "Internal questions and answers for everybody who builds and operates Acme services.",
     "site_url": BASE, "contact_email": "platform-team@acme.example"}, admin)
call("PUT", "/answer/admin/api/setting/privileges", {"level": 1}, admin)

PEOPLE = [("Priya Raman", "priya.raman"), ("Tomás Oliveira", "tomas.oliveira"), ("Ingrid Sørensen", "ingrid.sorensen"),
          ("Kwame Mensah", "kwame.mensah"), ("Li Wei", "li.wei"), ("Fatima Al-Sayed", "fatima.alsayed"), ("Jonas Becker", "jonas.becker"),
          ("Aiko Tanaka", "aiko.tanaka"), ("Mateusz Kowalski", "mateusz.kowalski"), ("Chloé Lefèvre", "chloe.lefevre"),
          ("Diego Fernández", "diego.fernandez"), ("Sara Lindqvist", "sara.lindqvist"), ("Omar Haddad", "omar.haddad"),
          ("Nina Petrova", "nina.petrova"), ("Ravi Shankar", "ravi.shankar"), ("Hannah O'Neill", "hannah.oneill"),
          ("Bao Nguyen", "bao.nguyen"), ("Elif Yıldız", "elif.yildiz")]
users = []
for i, (name, local) in enumerate(PEOPLE):
    email = f"{local}@acme.example"
    if i == 3:   # contractor mailbox routed through the staffing agency, a long but valid address
        email = f"{local}+contractor.platform-reliability.emea.rotation-2024@external-staffing-partners.infrastructure-services.acme-group.example"
    if i == 11:  # shared mailbox alias used for the on-call handover
        email = f"{local}.on-call-handover.payments-and-billing.secondary-escalation@mail-routing.shared-services.eu-central.acme-group.example"
    password = f"Seed-{local.split('.')[0].capitalize()}-2024!"
    call("POST", "/answer/admin/api/user", {"display_name": local, "email": email, "password": password}, admin)   # user name = local part
    users.append({"name": name, "email": email, "password": password, "token": login(email, password)})
    call("PUT", "/answer/api/v1/user/info", {"display_name": name[:30]}, users[-1]["token"])

sites = ["https://wiki.acme.example/display/PLAT/Runbooks?focusedCommentId=88213477&src=contextnavpagetreemode&spaceKey=PLAT&title=Incident+response+and+escalation+paths+for+the+payments+platform+including+weekend+rotations+and+vendor+contacts+for+the+card+processor+and+the+fraud+screening+provider#comment-88213477",
         "https://acme.example/people/kwame", "https://blog.example.org/~ingrid/", "https://git.acme.example/users/li.wei/projects?sort=updated&direction=desc&visibility=all&archived=false&per_page=100&utm_source=profile&utm_medium=qa&utm_campaign=internal-directory-refresh-2024-q3&ref=people-search-result-card-secondary-link-position-4-of-12-experiment-b"]
for u, site in zip(users[:4], sites):
    call("PUT", "/answer/api/v1/user/info", {"display_name": u["name"][:30], "website": site, "bio": "Platform team.", "location": "Remote"}, u["token"])

TAGS = [("Python", "python"), ("Kubernetes", "kubernetes"), ("PostgreSQL", "postgresql"), ("iOS", "ios"), ("Terraform", "terraform"),
        ("CI", "ci"), ("Go", "go"), ("Kafka", "kafka"), ("React", "react"), ("On-Call", "on-call"), ("Billing", "billing"),
        ("gRPC", "grpc"), ("Redis", "redis"), ("Helm", "helm"), ("C++", "c++"), ("Security", "security")]
TOPICS = ["Deploy fails with ImagePullBackOff on the staging cluster", "How do I rotate the Payments API signing key?",
          "PYTHON virtualenv breaks after the base image update", "python: best way to retry a flaky upstream call",
          "Terraform plan shows drift on every run for the load balancer", "Why is the nightly billing export 40 minutes late?",
          "Kafka consumer lag keeps growing on the invoices topic", "gRPC deadline exceeded only from the Frankfurt region",
          "How to run the iOS UI tests locally without the device farm", "Redis failover dropped sessions, how do we avoid it",
          "Helm upgrade hangs waiting for the pre-upgrade hook", "Which PostgreSQL isolation level does the ledger service use",
          "On-call handover checklist for the payments rotation", "Go service leaks goroutines after the client library bump",
          "React build is three times slower on the new runners", "Where do I request access to the security scanner reports",
          "C++ extension fails to link on arm64 builders", "What is the retention policy for audit logs",
          "kubernetes HPA never scales down the search workers", "CI cache is restored but dependencies are downloaded again"]
SUFFIX = ["", " (staging)", " - again", " after last week's change", " on Fridays", " for new joiners", " in eu-central", ""]
BODY = ["We see this since the last release. Steps:\n\n1. deploy\n2. wait\n3. it fails\n\n```\nerror: context deadline exceeded\n```\n\nAny idea?",
        "I checked the runbook but it only covers the old setup. What is the current way?\n\n> the wiki page is from 2022",
        "Happens roughly once a day. Logs attached below.\n\n```\nWARN retrying (attempt 3)\nERROR giving up\n```",
        "Asking for the Zürich team: is there a naïve way that works, or do we need the façade service?"]
ANSWER = ["This is caused by the registry mirror. Point the pull secret at the new mirror and redeploy.",
          "We hit the same thing. The fix was to pin the client to the previous minor version until the patch lands.",
          "Check the timeout on the sidecar first, it is 5s by default and the upstream needs 8s at peak.",
          "It is documented in the platform handbook under \"rotations\", but the short version: run the script, then restart both workers.",
          "Not a bug: the exporter waits for the ledger lock, and the lock is held by the reconciliation job on the first of the month."]
COMMENT = ["Thanks, that worked.", "Same here on the EU cluster.", "Can you add the exact command?", "This should be in the runbook.", "+1, hit this yesterday."]
LONG_SUMMARY = ("Rewrote the title and the steps after the incident review on Thursday: the original description mixed up the staging and the "
                "production cluster, the error message was from a different service, and the workaround that was accepted no longer applies since "
                "the registry mirror was moved. Also added the tags the platform team asked for, removed the screenshot with the customer name in "
                "it, and linked the follow-up ticket so people stop asking the same thing in the channel every Monday morning. Reviewed by the "
                "on-call lead; please do not revert without talking to the payments rotation first.")

questions = []
for n in range(110):
    author = users[rnd.randrange(len(users))]
    title = TOPICS[n % len(TOPICS)] + SUFFIX[(n // len(TOPICS)) % len(SUFFIX)] + ("" if n < len(TOPICS) else f" #{n}")
    tags = [{"display_name": d, "slug_name": s} for d, s in rnd.sample(TAGS, rnd.randint(1, 3))]
    q = call("POST", "/answer/api/v1/question", {"title": title[:150], "content": BODY[n % len(BODY)], "tags": tags}, author["token"])
    questions.append({"id": q["id"], "author": author, "title": title, "tags": tags, "answers": []})
for q in questions:
    for who in rnd.sample([u for u in users if u is not q["author"]], rnd.choice([0, 1, 1, 2, 2, 3])):   # one answer per person
        a = call("POST", "/answer/api/v1/answer", {"question_id": q["id"], "content": rnd.choice(ANSWER)}, who["token"])
        q["answers"].append({"id": a["info"]["id"] if isinstance(a, dict) and "info" in a else a["id"], "author": who})
for q in questions:
    for target in [q["id"]] + [a["id"] for a in q["answers"]]:
        for voter in rnd.sample(users, rnd.randint(0, 5)):
            try: call("POST", "/answer/api/v1/vote/up" if rnd.random() < 0.85 else "/answer/api/v1/vote/down", {"object_id": target}, voter["token"])
            except SystemExit: pass   # own posts cannot be voted on
        if rnd.random() < 0.35:
            call("POST", "/answer/api/v1/comment", {"object_id": target, "original_text": rnd.choice(COMMENT)}, rnd.choice(users)["token"])
    if q["answers"] and rnd.random() < 0.6:
        call("POST", "/answer/api/v1/answer/acceptance", {"question_id": q["id"], "answer_id": rnd.choice(q["answers"])["id"]}, q["author"]["token"])
    if rnd.random() < 0.3:
        call("POST", "/answer/api/v1/follow", {"object_id": q["id"]}, rnd.choice(users)["token"])
for i, q in enumerate(rnd.sample(questions, 25)):   # edits with a reason, a few of them long
    summary = LONG_SUMMARY if i < 6 else rnd.choice(["typo", "added logs", "clarified the environment", "fixed formatting"])
    call("PUT", "/answer/api/v1/question", {"id": q["id"], "title": q["title"][:150], "content": BODY[i % len(BODY)] + "\n\nEdit: see the incident notes.",
                                            "tags": q["tags"], "edit_summary": summary}, q["author"]["token"])
for q in rnd.sample(questions, 4):   # removed by a moderator
    call("DELETE", "/answer/api/v1/question", {"id": q["id"]}, admin)
keys = [call("POST", "/answer/admin/api/api-key", {"description": d, "scope": s}, admin) for d, s in
        (("status page bot", "read-only"), ("release notes poster", "global"))]
json.dump({"admin": {"email": ADMIN_EMAIL, "password": ADMIN_PASS, "token": admin},
           "users": [{k: u[k] for k in ("name", "email", "password", "token")} for u in users],
           "api_keys": keys, "questions": len(questions)}, open(OUT, "w"), indent=1, ensure_ascii=False)
print(f"seeded: {len(users)} users, {len(questions)} questions, {sum(len(q['answers']) for q in questions)} answers; accounts written to {OUT}")
