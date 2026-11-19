# BridgeFinder study session guide (feedback round 3)

There are two ways to run a session.

- **Self-guided (no facilitator).** Send the student `dist/bridgefinder-study.html` or its GitHub Pages link. The page walks them through consent, background, the unaided app task, a three-question check, the blinded card ratings, the System Usability Scale and the debrief. It records what they do in the app, and ends with a **Copy my answers** button. They paste the answers back to you. Collect the replies in text files and run `python prototype/study/import_answers.py replies/*.txt --out /path/to/private`, which writes `sessions.json` for the analyzer and `round3_log.csv` with one row per student. Rebuild the page with `python prototype/study/build_standalone.py`, and test it with `python prototype/tests/standalone_workflow.py`.
- **Moderated (below).** You watch, ask the check questions out loud, and take notes. It is slower but tells you more about why people get stuck.

The two modes use the same cards, rating questions and SUS, so both kinds of session go into one analysis. Each self-guided answer carries `collection_mode: self-guided-html-v1`, so the report can say how many sessions of each kind there were.

One moderated session takes about 25 minutes with one student and one facilitator. Each session gives the final report three kinds of evidence: what the student did in the app (task completion and comprehension), blinded ratings of 15 suggestion cards with the System Usability Scale (SUS), and open feedback for the next design round. The protocol and analysis are in [README.md](README.md). This guide is the script.

## Before the first session

1. On the facilitator's laptop, from the repository root:
   ```bash
   python -m pip install -r prototype/requirements.txt
   python prototype/serve.py
   ```
   Keep it running. The app is at `http://localhost:8765/web/` and the study at `http://localhost:8765/study/`.
2. Do one practice run yourself, download the file, then press **Clear this session**.
3. Do not change the app, `web/data.json` or `study/study_cards.json` until all study sessions are done. A mid-study change would mix two versions in the SUS and ratings. Collect design ideas in the log and apply them after the last session.
4. Copy `observation_log_template.csv` to a private folder outside the repository and fill in one row per session.

Sessions work best in person on the facilitator's laptop. Over Zoom, share your screen and give the student remote control, because the student cannot open your `localhost`.

## Who to recruit

Aim for 15 UIUC undergraduates or early-stage graduate students who want research experience. Avoid the ten students from rounds 1 and 2 if you can, so nobody has seen the app before. The card study has five starting researchers, so recruit across their areas rather than mostly computing:

| Starting researcher | Area |
|---|---|
| Naiman A. Khan | nutrition, gut microbiota, metabolic health |
| Stephen P. Long | crops, bioenergy, climate and agriculture |
| John A. Rogers | materials, sensors, MEMS and nanofabrication |
| Tarek Abdelzaher | computing: sensor networks, network analysis, activity recognition |
| Karen M. Tabb | maternal health, health disparities, mental health |

About three students per area would be ideal.

## 1. Recruitment message

Paste this into your participant pool's channel:

> Hi! We're Evan and Eric, and we're building **BridgeFinder** for CS 470. It's a tool that helps UIUC students find researchers outside their usual circle, and shows who might be able to introduce them. We're looking for undergrads or early grad students who are interested in getting research experience, in **any field** (nutrition, agriculture, materials, health, computing and more).
>
> It's one 25-minute session, in person or over Zoom. You'll try the app, rate some suggested researchers, and tell us what was confusing. We don't collect your name or email, and you can stop at any time.
>
> Reply or DM me with a time that works!

## 2. Session script

Text in quotation blocks is read aloud. Everything else is for the facilitator.

### Welcome and consent (2 min)

> Thanks for helping. We're testing BridgeFinder, not you, so there are no wrong answers, and confusing parts are exactly what we want to find. I'll ask you to use the app on your own and think out loud as you go. I won't help much during the task, because we want to see how it works without us. We don't record your name. We'll keep your ratings and our notes under a code like P07. You can skip anything or stop at any time. Is that OK?

Continue only on a clear yes. Write the next participant code (P01, P02 and so on) in the log.

### Background (2 min)

Ask these and record the answers in the log:

1. "Are you an undergraduate or a graduate student, and what's your major or program?"
2. "Are you looking for research experience, now or in the future?"
3. "Have you tried BridgeFinder before?"

### Step A: state an interest (1 min)

Open `http://localhost:8765/study/`.

> Please type a research topic or question you'd like to explore into the first box. A short phrase is fine. Please leave out names. Don't press Start yet.

### Step B: use the app without help (6 to 8 min)

Click the link on the study page to open the app in a new tab.

> Imagine you want to find a researcher to work with, outside your current professors' circles. Use this app to find someone who interests you, and then get to the point where you could write to them. Please think out loud as you go. Tell me when you think you're done.

While they work:
- Do not explain the interface. If they go quiet, say only "What are you thinking?" or "What would you do next?"
- If they are stuck for two minutes, give the smallest possible hint and write in the log where and what you said.
- Write down what they actually do: where they click first, which suggestion they open, whether they open the explanation or the outreach draft, what they hesitate over, and anything they say, word for word.

The task counts as **completed without help** if they choose a starting researcher, open a suggestion's card and open the outreach draft, with no hint.

When they say they are done, or after eight minutes, ask these two questions exactly and record pass or fail:

> On the card you opened, who could help introduce you to this person, and how are they connected?

Pass if they name the people on the route in order and say these are co-authors linking the two researchers.

> Back on the map, what's the difference between the solid lines and the dashed lines?

Pass if they say that solid lines are people who have published together, and dashed lines are suggestions that are not an existing connection.

Do not correct a wrong answer until the session is over.

### Step C: rate the suggestion cards (10 min)

Go back to the study tab.

> Now pick the starting researcher in this list closest to the interest you typed, and press Start rating. You'll see up to 15 suggested researchers, one at a time. Please rate each one on the three scales against your own interest. Different methods made these suggestions, and we've hidden which made which. Afterwards there are ten short questions about the app you just used.

Stay quiet during the ratings, and don't discuss the cards. At the end they press **Download responses**. Rename the file to the participant code, such as `P07.json`, and move it to your private folder. If you share the laptop, press **Clear this session** before the next student.

### Step D: debrief (4 min)

These answers decide the design changes for the next round. Record them in the student's words.

1. "What was the most confusing moment, and what did you expect to happen there?"
2. "Did any suggestion feel like someone you'd actually contact? What made it feel that way, or not?"
3. "How much did you trust the introduction route? What would make it more trustworthy?"
4. "What one thing would you change or add?"
5. "Would you use this when looking for research? Why or why not?"

### Wrap up

> That's everything, thank you! If you have any questions about the project, I'm happy to answer them now.

This is the time to explain anything they got wrong in Step B.

## After all sessions

Do not commit the participant files, because they are private study data. Share these three things with whoever runs the analysis:

1. All the `P##.json` files.
2. The filled observation log.
3. The date range of the sessions and the app commit used (`git rev-parse --short HEAD`).

Combine the files and run the analyzer:

```bash
python -c "import json,sys,glob; print(json.dumps([s for f in sorted(glob.glob(sys.argv[1]+'/P*.json')) for s in json.load(open(f))]))" /path/to/private > /path/to/private/sessions.json
python prototype/study/analyze_study.py --responses /path/to/private/sessions.json \
  --keys prototype/study/truth_keys.json --out /path/to/private/study-analysis.json
```

Then apply the design changes from the debriefs. If time allows, run a short round 4 with three to five new students on the changed app. Use Step B and the debrief only, and check whether the problems from round 3 are gone. The final report needs several rounds that show how the design changed across them.
