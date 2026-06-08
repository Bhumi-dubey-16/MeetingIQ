"""
Ground truth for all 10 MeetingIQ eval transcripts.
Each case defines:
  - transcript: the raw text
  - expected_actions: list of dicts with owner + task keywords to match
  - expected_decisions: list of keyword phrases that must appear
  - expected_meeting_type: substring match on meeting_type field
"""

CASES = [
    {
        "id": "01_product_planning",
        "expected_meeting_type": "planning",
        "expected_actions": [
            {"owner_hint": "priya",   "task_hint": "endpoint specs"},
            {"owner_hint": "marcus",  "task_hint": "docs"},
            {"owner_hint": "rohan",   "task_hint": "deck"},
            {"owner_hint": "deepak",  "task_hint": "post-mortem"},
            {"owner_hint": "sarah",   "task_hint": "auth"},
        ],
        "expected_decisions": [
            "ios 15",
            "analytics",
            "qa",
        ],
        "transcript": """Sarah: Alright, let's get started. We've got a lot to cover before the sprint ends Friday.

Marcus: Quick note — I'm blocked on the API docs until design signs off on the new endpoints.

Sarah: Okay, so design needs to prioritize that. Priya, can you get me the final endpoint specs by Wednesday EOD?

Priya: Wednesday is tight but yeah, I'll make it work. I might need to cut the analytics endpoint from this sprint though.

Sarah: Let's defer analytics to sprint 14. Marcus, once you have the specs, docs by Friday?

Marcus: Friday EOD, yes.

Sarah: Good. Now the mobile team — Rohan, where are we on the iOS build?

Rohan: We're at 70%. The crash on older iOS versions is still unresolved. I think it's a threading issue but I haven't confirmed yet.

Sarah: That's a risk. Is it a launch blocker?

Rohan: If we're targeting iOS 14 and above, no. Below that, yes. We haven't decided the floor yet.

Sarah: Let's decide now. iOS 15 minimum. Document that decision.

Rohan: Noted. That actually unblocks us — I'll close that ticket.

Sarah: Great. Budget side — Deepak, we're still within the $40K sprint budget?

Deepak: At $38,200. We'll go over if we extend the vendor contract for QA support. That renewal is $3,500 and expires Thursday.

Sarah: Don't renew. We'll handle QA internally this sprint. Priya, that means you're owning QA sign-off for the analytics deferral.

Priya: Fine, I'll add it to my list.

Sarah: Open question — nobody's confirmed who's presenting at the client demo next Tuesday. That needs an owner by tomorrow.

Marcus: I can do it if someone sends me the latest deck.

Sarah: Rohan, send Marcus the deck by tonight.

Rohan: Done.

Sarah: Last thing — we need a post-mortem on the staging outage from Monday. Deepak, schedule that for next week, invite the whole team.

Deepak: Will do. Thursday works?

Sarah: Thursday's fine. Okay, I think that covers it. Anything I missed?

Marcus: The third-party auth integration — we still haven't picked a vendor.

Sarah: That's a separate meeting. I'll schedule it. This week, before Friday.

Sarah: Alright, thanks everyone.""",
    },
    {
        "id": "02_sales_call",
        "expected_meeting_type": "sales",
        "expected_actions": [
            {"owner_hint": "neha",  "task_hint": "spec sheet"},
            {"owner_hint": "neha",  "task_hint": "data residency"},
            {"owner_hint": "james", "task_hint": "manager"},
        ],
        "expected_decisions": [
            "15,500",
            "pilot",
            "okta",
        ],
        "transcript": """James: Thanks for joining, Neha. So as I mentioned, we're looking at a Q3 rollout across our Mumbai and Pune offices — about 340 seats.

Neha: Perfect. And you mentioned you're evaluating us against two other vendors?

James: Correct. You're up against Freshworks and a smaller local player. Price is a factor but it's not the only one — our CFO cares a lot about SLA guarantees.

Neha: Understood. Our enterprise tier includes a 99.9% uptime SLA with a 4-hour response window. For 340 seats you'd be looking at approximately $18,000 annually, but I can get you to $15,500 if you commit before June 30th.

James: That's closer to our range. What's the onboarding timeline?

Neha: Two weeks from contract sign. We'd assign you a dedicated success manager — that's included.

James: One issue — our IT team flagged that we need SSO via Okta. Is that supported?

Neha: Yes, Okta is on our supported identity providers list. I'll send you the technical spec sheet after this call.

James: Good. The other thing is data residency. We're in financial services, so data needs to stay in India.

Neha: Our Mumbai data center covers that. I'll confirm with our infra team but I'm 95% sure that's already live.

James: That 5% is a problem. We can't sign without confirmed data residency.

Neha: Fair. I'll get written confirmation from our infra team by Thursday. If it's confirmed, are you ready to move to a contract draft?

James: If data residency is confirmed and the price holds at $15,500 — yes, we'd be ready to sign by end of month.

Neha: I'll also include a 30-day free pilot for 20 seats so your team can validate before the full rollout.

James: That's a good offer. Let me run it by my manager and I'll get back to you by Wednesday.

Neha: Perfect. I'll send the spec sheet and data residency confirmation by Thursday. Talk soon.""",
    },
    {
        "id": "03_engineering_standup",
        "expected_meeting_type": "standup",
        "expected_actions": [
            {"owner_hint": "dev",   "task_hint": "cleanup script"},
            {"owner_hint": "mei",   "task_hint": "notification"},
            {"owner_hint": "yusuf", "task_hint": "monitoring"},
            {"owner_hint": "aisha", "task_hint": "config"},
        ],
        "expected_decisions": [
            "wednesday",
            "monitoring",
            "escalate",
        ],
        "transcript": """Dev: Quick standup. Let's go round. Aisha, you first.

Aisha: Yesterday I finished the caching layer for the search endpoint. Today I'm writing unit tests. No blockers.

Dev: Good. Yusuf?

Yusuf: I'm still on the database migration. Hit a problem — the foreign key constraint is failing on production data because there are orphaned records from the 2022 import. I need someone with DB admin access to run a cleanup script.

Dev: That's a blocker. Can you write the cleanup script today?

Yusuf: Script is ready, I just can't run it myself.

Dev: I'll run it after standup. You should be unblocked by noon. Anyone else need DB access this sprint?

Aisha: I might. The search index rebuild touches the same tables.

Dev: Let's sync after this. Okay, Mei?

Mei: I pushed the notification service to staging yesterday. There's a known issue — push notifications are delayed by up to 90 seconds on Android. I'm investigating, probably a queue throughput problem. Hoping to have a fix by EOD.

Dev: Is that a launch blocker?

Mei: If it's more than 30 seconds at launch, yes. Right now I can't guarantee it.

Dev: Flag it as high risk. If it's not resolved by Wednesday EOD, we escalate to the whole team. Okay?

Mei: Agreed.

Dev: One thing I want to raise — we have no monitoring on the new payment service. Zero alerts set up. If something breaks in prod we won't know until a user complains.

Aisha: Who owns that?

Dev: Nobody apparently, which is the problem. Yusuf, can you add monitoring setup to your list after the DB migration? This week.

Yusuf: I can do it Thursday if the migration is done by Wednesday.

Dev: That works. Everyone check the staging deploy from last night — there's a config change that affects local env setup, details in Slack. Any questions?

Mei: The config change broke my local setup. I had to revert.

Dev: That's a bug. Aisha, can you look at the config rollout? Make sure it's backwards compatible.

Aisha: I'll check it today and patch if needed.

Dev: Good. That's everything. We're done.""",
    },
    {
        "id": "04_hr_review",
        "expected_meeting_type": "review",
        "expected_actions": [
            {"owner_hint": "nisha",  "task_hint": "1-1"},
            {"owner_hint": "nisha",  "task_hint": "headcount"},
            {"owner_hint": "arjun",  "task_hint": "certification"},
        ],
        "expected_decisions": [
            "senior",
            "january",
            "24 hours",
        ],
        "transcript": """Nisha: Thanks for making time, Arjun. This is your mid-year review. I want this to be a two-way conversation, so please push back on anything.

Arjun: Of course.

Nisha: Starting with positives — your delivery on the client portal project was strong. You hit every milestone and the client specifically asked for you on the next phase. That's notable.

Arjun: I appreciate that. That project was intense.

Nisha: It was. Now, the development area — and this is consistent with what your manager Sunita flagged — there's a pattern of late communication when you're blocked. The three incidents this quarter where dependencies slipped, each time we found out late. Does that resonate?

Arjun: Honestly, yes. I tend to try to solve the problem before raising it, which I know can backfire.

Nisha: That's self-aware. The ask is to raise it earlier, even when you don't have a solution. Can you commit to flagging blockers within 24 hours of identifying them?

Arjun: Yes, that's a reasonable ask.

Nisha: Good. I'm also looking at the promotion question. You're eligible for Senior Associate from January. Sunita's recommendation is contingent on two things — leading a client-facing deliverable independently, and the communication improvement. The client portal extension would be the right vehicle.

Arjun: That's what I was hoping for. Is there a timeline for the decision?

Nisha: Formal review is in December. If the client portal phase two closes well, Sunita submits the recommendation in November.

Arjun: And the communication piece — is there formal training or is it just the behavior change?

Nisha: We can set up monthly 1-1s with Sunita specifically to track it. Would that help?

Arjun: It would.

Nisha: I'll set that up this week. One more thing — your goal from the last review was to complete the AWS Solutions Architect certification by September. Where are you?

Arjun: I'm about 60% through the coursework. September is still achievable.

Nisha: Good. Complete that and it strengthens the promotion case. I'll note it as in-progress.

Nisha: Any concerns from your side?

Arjun: The only thing I'd raise is bandwidth. I've been covering for a vacant role on the team for two months. It's affecting my bandwidth to work on the cert.

Nisha: That's fair. I'll flag the open headcount to Sunita and push for the role to be filled by August. I can't promise it but I'll escalate.

Arjun: That's all I needed.""",
    },
    {
        "id": "05_investor_update",
        "expected_meeting_type": "investor",
        "expected_actions": [
            {"owner_hint": "ananya", "task_hint": "series a"},
            {"owner_hint": "ananya", "task_hint": "sync"},
            {"owner_hint": "vikram", "task_hint": "july"},
        ],
        "expected_decisions": [
            "sso",
            "mobile",
            "runway",
        ],
        "transcript": """Ananya: Thanks everyone for joining. I'll keep this tight — 20 minutes then Q&A.

Ananya: Revenue for Q2 came in at $1.2M ARR, up from $820K at end of Q1. That's 46% quarter-over-quarter growth. We're ahead of the $1M target we set in March.

Vikram: What's driving that? New logos or expansion?

Ananya: Split — 60% new logos, 40% expansion from existing customers. Our net revenue retention is at 118%.

Vikram: That's healthy. What's the burn?

Ananya: Monthly burn is $185K. We have 14 months of runway at current burn. We're targeting 18 months, which means either we close the Series A before October or we cut burn by $25K per month.

Prerna: What does the Series A timeline look like?

Ananya: First close target is September. We're in conversations with three funds — I won't name them but two are Tier 1 India, one is a US fund that did our seed. Term sheets expected by end of July.

Vikram: What if term sheets slip?

Ananya: Then we defer two planned hires — the VP Sales and a senior engineer — from Q3 to Q4. That gets us to the 18-month runway without fundraising.

Prerna: On the product side, what's shipping this quarter?

Ananya: Three things. Enterprise SSO, which is a sales blocker for 4 deals in our pipeline. Custom reporting, which two existing customers are waiting on before expanding. And the mobile app, which is a nice-to-have.

Vikram: Can you rank those?

Ananya: SSO first, custom reporting second, mobile third. If bandwidth forces a cut, mobile gets deferred.

Prerna: Regulatory update?

Ananya: We received DPDP compliance confirmation from our legal team last week. That removes a blocker for the financial services segment. Three prospects specifically mentioned it.

Vikram: Good. My main concern is the sales hire dependency — are you comfortable running Q3 pipeline without a VP Sales?

Ananya: No, frankly. We have four qualified deals and I'm managing them directly. It's not sustainable past September. If the Series A doesn't close by then, the VP Sales hire becomes the first thing we fund, not the last.

Vikram: Noted. I'd recommend we sync on the term sheet situation in mid-July, before the board meeting.

Ananya: Agreed. I'll schedule that.""",
    },
    {
        "id": "06_vendor_negotiation",
        "expected_meeting_type": "negotiation",
        "expected_actions": [
            {"owner_hint": "shreya", "task_hint": "friday"},
            {"owner_hint": "ravi",   "task_hint": "sign"},
        ],
        "expected_decisions": [
            "4,500",
            "dedicated",
            "18 months",
        ],
        "transcript": """Ravi: Thanks for coming in, Shreya. We've been using your logistics platform for 8 months. The current contract is up August 31st and we need to decide by July 15th.

Shreya: Of course. I'm hoping we can make the renewal work.

Ravi: Honestly, we've had service issues. Three delayed shipments in Q2, one of which cost us a $12,000 penalty from our end client. That needs to be addressed before I can recommend renewal.

Shreya: I understand. Two of those were due to the port strike in May — that's force majeure. The third one was on us and I can offer a credit.

Ravi: What's the credit?

Shreya: $3,000 against the next invoice.

Ravi: That doesn't cover our exposure. We're looking for $6,000 minimum or a comparable service upgrade.

Shreya: I can go to $4,500. And I can offer dedicated account management — a named contact available 8 AM to 8 PM, not just the general support queue.

Ravi: That's valuable. Can you put that in writing with SLA terms — response within 2 hours for critical issues?

Shreya: Yes, I can include that in the contract addendum.

Ravi: Pricing. We're currently at $28,000 annually. We've benchmarked two alternatives at $23,000 and $25,000.

Shreya: Those are lower-tier providers, the SLA comparison won't hold. But I can offer you $25,500 with the dedicated account management included.

Ravi: $24,500 and we commit for 18 months instead of 12.

Shreya: That's a stretch. Let me check with my VP. I'll have an answer by Friday.

Ravi: If you can't get to $24,500, we'll need the dedicated AM and $4,500 credit at minimum to even consider renewal at current pricing.

Shreya: Understood. I'll come back Friday with a final number. If we can close by July 10th instead of July 15th, can you get signoff faster?

Ravi: If the number works and the terms are clean, yes — we can sign in 2 business days.

Shreya: I'll push internally to meet that. One more thing — are you open to adding our warehouse management module to the contract? It integrates directly and I can bundle it at no extra cost.

Ravi: We'd evaluate it but that's not a condition of renewal. Separate conversation.

Shreya: Fair. I'll come back Friday.""",
    },
    {
        "id": "07_sprint_retro",
        "expected_meeting_type": "retrospective",
        "expected_actions": [
            {"owner_hint": "kenji", "task_hint": "staging"},
            {"owner_hint": "kenji", "task_hint": "rate limit"},
            {"owner_hint": "dev",   "task_hint": "debt"},
        ],
        "expected_decisions": [
            "async",
            "scope",
            "carry-over",
        ],
        "transcript": """Dev: Okay retro time. We're doing this in three parts — what went well, what didn't, what we change. Asel, kick us off.

Asel: What went well — the async code review process. We switched to async reviews last sprint and it cut the review bottleneck significantly. I went from waiting 2 days for reviews to same-day or next morning.

Kenji: Agreed. Big improvement.

Dev: Let's keep that. What else went well?

Kenji: The daily syncs were better when we kept them to 15 minutes. The two days we ran over, people dropped off.

Dev: Good point. What didn't go well?

Asel: The staging environment was broken for two days mid-sprint. It blocked everyone from testing. We didn't escalate it fast enough.

Dev: Why didn't we escalate?

Asel: Nobody was sure whose responsibility it was.

Dev: That's an ownership gap. We need a named person responsible for staging health each sprint. We'll add that to the sprint kickoff checklist. Kenji, can you own it this sprint?

Kenji: Yes.

Dev: What else?

Kenji: Scope creep. Three tickets got added mid-sprint without going through grooming. It created confusion about priorities.

Dev: Yeah, that's a process issue. New rule — no tickets added to active sprint without both the tech lead and PM agreeing. I'll add it to our team charter document.

Asel: There's also an unresolved thing from last sprint — the API rate limiting spec. We still don't have a decision on whether we implement it client-side or server-side. It's been pending for three weeks.

Dev: Who's blocking that?

Asel: It's waiting on a call between the backend lead and the security team. That call hasn't been scheduled.

Dev: Kenji, can you schedule that call? This week?

Kenji: I'll set it up today.

Dev: What do we change going forward?

Asel: I want us to track carry-over tickets explicitly — anything that didn't finish this sprint shows up at the top of the next retro.

Dev: That's a good habit. Let's add a carry-over review as the first 5 minutes of each retro. Anyone object?

Kenji: No, that's useful.

Dev: Anything else?

Asel: I'm worried about technical debt accumulating. We've deferred three refactor tasks in a row. If we keep deferring, the codebase is going to slow us down by Q4.

Dev: I hear you. Let's reserve 10% of sprint capacity for debt from next sprint. I'll discuss it with the PM this week.

Dev: Okay. Staging owner — Kenji. Rate limiting call — Kenji by EOW. Debt allocation — I'll handle. Carry-over tracking — starts next retro. Good work, everyone.""",
    },
    {
        "id": "08_client_onboarding",
        "expected_meeting_type": "onboarding",
        "expected_actions": [
            {"owner_hint": "priya",  "task_hint": "domains"},
            {"owner_hint": "priya",  "task_hint": "admin"},
            {"owner_hint": "thomas", "task_hint": "export"},
        ],
        "expected_decisions": [
            "july",
            "sso",
            "training",
        ],
        "transcript": """Priya: Welcome, and thanks for choosing us. This call is to make sure your onboarding goes smoothly. Quick intro from your side?

Client (Thomas): Sure. I'm Thomas, Head of Operations at Meridian Logistics. My team is about 45 people across three locations — Mumbai, Delhi, Pune.

Priya: Great. Your contract starts July 1st. By end of July we want to have all 45 users active and trained. Does that timeline work?

Thomas: July is tight because we have a company offsite July 18th-20th. Training during that window won't work.

Priya: Understood. We'll schedule training sessions for July 7th-15th and resume July 21st if we need additional sessions. That keeps us on track. I'll send calendar invites this week.

Thomas: That works. One thing I need to flag early — our IT team needs to whitelist your domains. Can you send a list of required domains and ports?

Priya: I'll email that within 24 hours after this call. Also, your IT team will need to create the SSO configuration — I'll attach the setup guide. It's about 2 hours of work for them.

Thomas: Who do I contact if SSO breaks during rollout?

Priya: Your dedicated success manager is Ritu — I'll introduce you over email today. She'll be your first point of contact for anything technical during onboarding.

Thomas: Good. Data migration — we have about 3 years of historical shipment records in our old system. Can those be imported?

Priya: Yes, we support CSV import. The format spec is in the onboarding docs. Historical data import is self-serve, but Ritu can assist if you hit issues.

Thomas: What's the realistic timeline for data import?

Priya: If your IT team exports the CSV by July 5th, import can run July 7th-8th. Historical data would be live before training starts.

Thomas: Okay. I'll ask my IT team to start the export by July 3rd.

Priya: One risk I want to flag — if the SSO configuration takes longer than expected, it can delay user access. Have your IT team start the SSO setup by June 28th to give buffer.

Thomas: Noted. I'll tell them today.

Priya: Last thing — your contract includes a 90-day check-in. I'll schedule that for early October. Before then, we'll do a 30-day health check in early August. That's a 30-minute call with Ritu.

Thomas: That's all fine. The main thing for me is making sure the three location managers — Mumbai, Delhi, Pune — each have admin access. Can that be set up before training?

Priya: Yes. I'll create admin accounts for all three this week and email them credentials by Friday.

Thomas: Perfect. I think that covers it.""",
    },
    {
        "id": "09_budget_review",
        "expected_meeting_type": "budget",
        "expected_actions": [
            {"owner_hint": "karan", "task_hint": "devops"},
            {"owner_hint": "karan", "task_hint": "aws"},
            {"owner_hint": "meera", "task_hint": "salary"},
        ],
        "expected_decisions": [
            "210",
            "roas",
            "salary band",
        ],
        "transcript": """CFO (Meera): Let's go through Q2 actuals vs budget. Karan, engineering first.

Karan: Engineering came in at $420K against a $390K budget. The $30K overage was the two emergency cloud scaling events in April and May.

Meera: Were those avoidable?

Karan: The April one no — it was a traffic spike from the product launch. The May one was avoidable. We had a misconfigured autoscaling rule that nobody caught. I've fixed the config and I'm adding a monthly infrastructure audit to catch this kind of thing.

Meera: Good. Mark April as a one-time cost, May as avoidable. What's the Q3 engineering forecast?

Karan: $410K if no more incidents. I've built in a $20K buffer for unplanned cloud costs.

Meera: That's reasonable. Marketing?

Divya: Marketing came in $15K under budget at $185K vs $200K. The two campaign pauses in June saved us money but also cost us reach — we pulled back to stay within budget.

Meera: Was the underspend a good thing or did we leave growth on the table?

Divya: Honestly, we left growth on the table. The campaigns that were paused had a 3.2x ROAS. Pausing them to save $15K was the wrong trade-off.

Meera: Noted. For Q3 I want a rule — if ROAS is above 2.5, don't pause campaigns for budget reasons. Bring the request to me first.

Divya: Understood. Q3 marketing budget request is $230K — we want to test two new channels.

Meera: I'll approve $210K. The incremental $20K needs a performance gate — if the new channels don't hit 2x ROAS by August 15th, we pause and reallocate.

Divya: Fair.

Meera: Headcount — we budgeted 3 new hires in Q2, made 2. The DevOps role is still open.

Karan: We've had two candidates decline. The salary band is below market. I need either a $15K salary band increase or approval to go through a recruiter.

Meera: I'll approve the salary band increase. Get that role filled by end of July — it's a risk to have it open going into Q3.

Karan: Agreed. One more thing — the AWS enterprise discount we were expecting hasn't come through. That was a $40K annual saving assumption in the budget.

Meera: When does that expire?

Karan: The negotiation window closes August 31st. If we don't close it, we're looking at a $40K overage in Q3-Q4 projections.

Meera: Make that a priority. Get me an update by July 31st. If it's not closing, we need to adjust Q3 budget before the board meeting.

Karan: Will do.""",
    },
    {
        "id": "10_incident_response",
        "expected_meeting_type": "incident",
        "expected_actions": [
            {"owner_hint": "sneha", "task_hint": "alert"},
            {"owner_hint": "yusuf", "task_hint": "retry"},
            {"owner_hint": "arjun", "task_hint": "post-mortem"},
            {"owner_hint": "priya", "task_hint": "status"},
        ],
        "expected_decisions": [
            "connection pool",
            "30 seconds",
            "post-mortem",
        ],
        "transcript": """Incident Lead (Arjun): Okay we're in a P1. The payment service went down at 14:23. It's 14:41 now, 18 minutes downtime. What do we know?

Sneha: The payment service is returning 503s. Load balancer is healthy. The database connection pool is exhausted — we're at 100% connections, nothing available.

Arjun: Why is the pool exhausted?

Sneha: We're seeing a flood of retries from the mobile client. Looks like a loop — clients are retrying on 503, which is making the 503s worse.

Arjun: Okay. Two actions right now. Sneha, increase the DB connection pool limit. What's the max we can go to without causing DB load issues?

Sneha: We're at 100 currently, safe max is about 200.

Arjun: Double it to 200. Do that now.

Sneha: Done. Deploying.

Arjun: Yusuf, kill the retry loop on the client side. Can we push an emergency config update to throttle client retries?

Yusuf: Yes, we have a feature flag for retry behavior. I can set the retry interval to 30 seconds. Takes 2 minutes to propagate.

Arjun: Do it. Sneha, how long for the pool increase to take effect?

Sneha: 3-4 minutes.

Arjun: So we should see recovery in 5-7 minutes. Everyone stay on. Who's handling customer comms?

Priya: I can do it. Should I post a status page update?

Arjun: Yes — post now. Keep it brief: "Payment service disruption, investigating, update in 15 minutes." Don't mention root cause yet.

Priya: Posted.

Sneha: Pool increase is live. Connection count dropping — we're at 78 now, down from 100.

Arjun: Good. Yusuf, retry flag status?

Yusuf: Propagating. About 90 seconds out.

Arjun: Sneha, anything else in the logs?

Sneha: One thing — there's an alert that was supposed to fire when connection pool hit 80%. It never fired. We had no warning.

Arjun: That alert is broken. After we're stable — who owns the alerting config?

Sneha: That's me.

Arjun: After this is resolved, write up why it didn't fire and fix it today. That's a high priority action.

Sneha: Understood.

Yusuf: Retry flag is live. Client retry interval now 30 seconds.

Sneha: Payment service recovering — 503s dropping. We're at 12% error rate, down from 100%.

Arjun: Keep watching. Priya, send the 15-minute update in about 10 minutes saying we're recovering.

Priya: Will do.

Sneha: Error rate at 2%. Service is stable.

Arjun: Good. Incident resolved at approximately 14:52, 29 minutes total. Post-mortem meeting tomorrow 10 AM, mandatory for everyone on this call. I'll send the invite.

Arjun: Action items before then: Sneha fixes the alerting gap today. Yusuf documents the retry loop as a known client bug and files a ticket. I'll write the initial post-mortem draft by 9 AM tomorrow.""",
    },
]