# Portfolio plan: turning existing projects into proof

The projects already exist. The gap is that a stranger can't verify them in five minutes. A reviewer gives a portfolio about that long. The plan below is built around that limit.

**Goal:** one public page (a simple site or a GitHub profile README) with four entries. Each entry has a one-paragraph summary, one picture or short clip, one link to evidence, and a line saying what you did and what someone else did. Being exact about the partnership on platemail.gg matters: overclaiming on a shared project is the fastest way to lose credibility in an interview.

Order of work is by payoff per hour. Stop wherever energy runs out; each step stands alone.

## 1. platemail.gg case study (highest payoff; ~4–6 hours total)

It's the only project with real outside users, so it does the most work.

- **Agree with your partner first** about what can be shown publicly (screenshots, numbers, code, their name). Get it in writing, even a text message.
- Write a 400–600 word case study: the problem, what you built, one hard decision and the trade-off, what went wrong after launch, what you'd change. Plain prose, no marketing tone.
- Add a 60–90 second screen recording of a real session.
- Include numbers only if they're real and you're allowed to share them: users, sessions, cost per session, uptime. No numbers is fine. Made-up or fuzzy numbers are not.
- **Signals for:** implementation/solutions roles, AI product support, AI ops.

## 2. A small public evaluation write-up (~6–10 hours, can be split)

Evaluation and data roles want proof that you can judge model output carefully and consistently. Your GPU measurement work is the seed.

- Pick one narrow question you've already partly answered (for example, how consistent a model is across repeated runs of the same prompt, or how often an agent's memory recall is wrong). Narrow is better.
- Publish: the question, the method, the data (or a sample), results with the uncertainty stated, and limitations. A GitHub repo with a README and a notebook is the standard format.
- Write the code in Python yourself, using AI for review and explanation rather than generation. That doubles as Python practice and gives you something you can defend line by line in a technical screen.
- **Signals for:** AI evaluation, data quality, research assistance, and some policy roles.

## 3. Multi-agent system: architecture note (~3–4 hours)

Most people can't see this project at all, so write about it rather than open-sourcing it.

- One diagram and 500–800 words: what the agents do, how memory persists, what breaks (drift, cost, context limits, conflicting writes) and how you catch it. Include a short anonymized log excerpt.
- Leave out anything personal the system holds.
- **Signals for:** AI ops, agent/automation roles, solutions engineering.

## 4. Writing samples (~2 hours if older work exists)

- Two pieces: one explanatory (for example, "how an AI dungeon master keeps track of a game," for a general reader) and one analytical (an economics or history paper you've already written, cleaned up, or the evaluation write-up).
- Technical writing roles almost always ask for samples. Have them ready as PDFs and links.
- **Signals for:** technical writing, research, policy, communications.

## 5. Client demo (optional, ~1 hour)

- Include it only if the prospective client agrees, or you strip anything identifying. One screenshot and two sentences on scoping and pricing. It shows you can turn a vague request into a quote, which is useful for implementation roles.

## Where to put it

- A GitHub profile README linking to the four entries is enough. A personal site is nice to have, not required.
- The same link goes on the resume header, LinkedIn, and every cover letter.

## Known weaknesses this does not fix

- **None of this replaces a reference.** Your business partner is the most credible person who has seen you work. Ask whether they're willing to be a reference before you list them.
- **Small-scale GPU work isn't research credentials.** Present it as careful measurement at small scale, which is true and useful. Don't present it as ML research.
- **A portfolio gets you past "can you do anything?" but not past "can he do it on a team, on a schedule?"** The steady contract work in `01-role-map.md` (evaluation platforms, temp roles) partly exists to fill that gap.
