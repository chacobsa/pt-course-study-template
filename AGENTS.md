# AGENTS.md

## Purpose

This repository holds study notes for one online course from Positive Education (LMS: `lms.edu.ptsecurity.com`).
The user is a student. You are the study assistant.
You help the user to learn. You do not replace the user's own reading.

The facts about the course (name, LMS link, number of weeks, dates, labs) are in [[course]] (`course.md`). Read it first.
If `course.md` still has `TODO` values, run the `/init-course` skill before anything else.

## Course profile

`course.md` has the field "Тип курса". It sets which optional parts apply:

| Profile | For | What it adds |
|---|---|---|
| `network` | network traffic and security courses | PCAP rules, Wireshark, Suricata, `detections/`, the "attack" section in notes |
| `general` | theory courses without special files | nothing extra. `attachments/` is created only if a material has a file |
| `attachments` | other courses with files (archives, binaries, datasets, VM images) | `attachments/` and the attachment rules, no network parts |

Parts marked `(network)` in this file apply only to the `network` profile. The attachment rules apply to every profile when a material has a file. The lab trainer rules apply to every course that has a trainer.

## Language rules

- Write this file in simplified English.
- Write all notes, summaries, and questions in Russian.
- Write protocol names, tool names, and commands in English. Example: DNS, TCP, Suricata, Wireshark, `nmap`.
- Write other terms in Russian. Put the English term in brackets at first use. Example: индикатор компрометации (IoC).
- Use `[[wikilinks]]` for links between notes. The user reads the notes in Obsidian.

## Platforms

The user may work on macOS or Windows. Keep every step cross-platform.

- Run helper scripts with Python only: `python -I scripts/<name>.py`. Use `python3` on macOS if `python` is missing.
- Do not write bash-only commands (`shasum`, `sed -i`, `nc`, `file`, `rm -rf`, `export`) in notes or scripts. Use Python or the dedicated tools. The scripts in `scripts/` replace them.
- Use forward slashes in paths inside files. Use `pathlib` in scripts.
- Save text files as UTF-8 with LF line endings.
- At the start of work, and after any tool error, run `python -I scripts/doctor.py`. It checks the tools and the hardware. Add `--net` to check that the course hosts answer.

## Repository layout

```
AGENTS.md                      This file.
course.md                      Facts about this course. Filled by /init-course.
README.md                      Course map, schedule, progress.
SETUP.md                       How to install the tools (macOS, Windows).
notes/<week>/                  Summaries. One file for each LMS material.
transcripts/<week>/            Text of videos and webinars. Committed.
media/<week>/                  Downloaded videos and other course files (PDF, slides). Never committed.
attachments/<week>/            Downloaded files of materials (PCAP, archives, binaries, ...). Never committed.
attachments/<week>/incoming/   Files that the user downloaded by hand. Never committed.
sources/manifest.csv           One row for each material. Tracks status.
sources/attachments.csv        One row for each attachment. Tracks status.
scripts/                       Helper scripts (Python). See "Tools and environment".
templates/                     Templates for notes.
cheatsheets/                   Short references for tools.
detections/                    Suricata rules and Wireshark filters (network profile only).
labs/                          Reports of practical tasks.
glossary.md                    Term list.
questions.md                   Weak topics and open questions.
whisper-fixes.md               Known speech-to-text errors and their corrections.
```

Week folders use this pattern: `w1`, `w2`, and so on. Notes may use a longer name, for example `w1-basics`.

Public sharing: this repository is a template. The folders `notes/`, `transcripts/`, `media/`, `attachments/` hold course content. Never add course content to the template repository.

## File naming

- Use this pattern: `m<LMS material id>-<english-slug>.<ext>`. Example: `m3989-why-analyze-traffic.mp4`.
- Make the slug short. Use lowercase letters, digits, and hyphens only.
- Use the same name in `media/`, `transcripts/`, and `notes/` for the same material.
- Never rename a file after you create it. The material id stays the same.
- For an attachment, use the same pattern with the extension of the file (`.pcap`, `.zip`, `.exe`, ...). Example: `m3905-network-vm-start.pcap`. For a PCAP, the extension follows the real format: `.pcapng` for a pcapng file (`attachment_register.py` warns about a wrong extension).
- A material with one attachment has no number in the slug.
- If one material has more than one attachment, give each file its own short slug from its original name. Add a two-digit number at the end of every slug. The number is the place of the file on the material page. Example for three files in material 4000: `m4000-scan-01.pcap`, `m4000-scan-slow-02.pcap`, `m4000-exploit-03.pcapng`.
- Keep the original file name in `sources/attachments.csv`. The course text and the labs use it.

## Item numbering

- Give each LMS item a number with this pattern: `<week>-<position>`. Example: `1-08`.
- The position is the place of the item in the week list in the LMS. Use two digits.
- Count all items: documents, videos, tests, surveys, and section headers. A section header is an item like the others.
- The number does not change the file name. Never put the number in a file name.
- Put the number in these places: `order` and `aliases` in the front matter, the H1 title (`# 1-08. Title`), the `№` column in `README.md`, and the `seq` column in `sources/manifest.csv`.
- Keep the table in `README.md` in the LMS order. Add the rows for a week when the week opens. A row without a known ID has `—` in the ID column.
- When the LMS list changes, tell the user. Do not renumber without the user's approval.
- Get IDs and positions from the course structure (see "Course structure" below).
- Do not click an item in the LMS list to find its ID. A click opens the material and can count as viewed.
- Check an ID against the number inside the material when you can. Example: the title "2.1.0" in the page is the third item of section 2.
- The ID column in `README.md` has material IDs only. Tests and polls have their own ID ranges. Their rows have `—`.
- A section can have hidden resources in `links` (for example a PDF guide). They have no place in the LMS list. Do not give them a number. Mention them in the README notes and in the note of the related material.

## Glossary

- `glossary.md` holds all abbreviations and terms. Each entry has the full name (or what it is), a plain explanation, an example, and the place in the course. The header of `glossary.md` has a sample entry.
- When you write a note, find each abbreviation and term. Link the first use in the note to its entry. Use this form: `[[glossary#GRE|GRE]]`.
- A term links to the glossary only. Do not write `[[IDS]]`: there is no note with this name. To point to a note about the topic, add a second link: `[[glossary#IDS|IDS]] ([[m4106-ids]])`.
- If a term has no entry, add one before you finish the note. Keep the entries in alphabetical order. Latin first, then Cyrillic.
- The entry heading is plain text. Do not use a slash, a bracket, or a colon in a heading. These characters break the link.
- A comma in a heading is allowed. Related terms can share one entry. Example: `Snort и Suricata`.
- Mark facts that are not from the course. Write that the definition comes from general knowledge.
- Do not edit existing lines with a script that splits and joins text. A bug can break the note.
- To add entries, use `python -I scripts/glossary_insert.py <blocks> glossary.md <out>`. It only inserts new text: `@@BEFORE <heading>` before an existing heading, `@@END` at the end of the file (for the first entry and for entries after the last one in the alphabet). It writes a new file and stops if an old line was changed or removed. Read the result. Then replace the file.
- Before you add entries, check the order of the existing entries. Move entries that are in the wrong place.
- After each change, run `python -I scripts/check_glossary.py` and `python -I scripts/check_links.py`. They check that:
  - every `[[glossary#...]]` link in the notes has an entry;
  - the entries are in the right order;
  - there are no duplicate headings;
  - no heading has a slash, a bracket, or a colon;
  - every other `[[link]]` points to an existing note.
- Check the result and repair it before you report.

## Note format

Use [templates/note.md](templates/note.md). Each note starts with this front matter: `id`, `order`, `aliases`, `week`, `kind`, `title`, `duration`, `source`, `transcript`, `status`, `tags`.

Use this structure:

1. The H1 title: `# 1-08. Title`.
2. Short summary: the first paragraph after the title. One or two sentences. No heading.
3. Content: `##` sections in the order of the source.
4. `(network)` For an attack note: what the attack does, which protocols and ports it uses, how it looks in traffic, how to detect it.
5. `## Вопросы для закрепления`. Start the section with the standard line about `[Claude]` and `[Курс]` (copy it from the template).
6. `## Заметки и пробелы`. Write open tasks as `- [ ]`. The last line is `- Связано: [[...]], [[README]]`.

Keep each note short. Do not copy long text from the course. Write summaries in your own words.

Status values:

| Place | Values |
|---|---|
| Front matter `status` | `summarized`: the note is ready. `partial`: the note uses only part of the material, for example the video is not transcribed yet. |
| Status column in `README.md` | `не начат` → `прочитан` → `конспект готов` → `вопросы заданы`. A `partial` note has `прочитан` and the reason in brackets. |
| `sources/manifest.csv` | `downloaded`, `transcribed`: `yes`, `no`, or `n/a` (no video). `summarized`: `yes`, `no`, or `partial`. |
| Attachment table in `README.md` | `не скачан` → `скачан` → `сверен` (or `сверен частично`): the frames or facts from the note are checked against the file. |

Formats in the tracking files:

- Video length: `h:mm:ss`, also under one hour. Example: `0:09:11`, `1:06:53`. Use it in `duration` in the front matter and in `sources/manifest.csv`.
- The length of a PCAP capture in the `meta` column of `sources/attachments.csv` is in seconds, as `capinfos` shows it. Example: `70.65`.
- In `sources/manifest.csv`, `video_id` is the video id of any host and `video_host` is the host (`vimeo` or `kinescope`). Both are empty for documents.
- A hidden resource (see "Item numbering") has a row in `sources/manifest.csv` with `kind` = `resource` and an empty `seq`. The video columns are empty.
- A known attachment that is not downloaded yet has a row in the attachment table in `README.md`: `—` in the ID column, the planned local name, and the status `не скачан`. It gets a row in `sources/attachments.csv` only after the download.

Content rules:

- A material can have errors. Do not fix them silently. In the gaps section, write "Расхождение в материале": what the material says, what is correct, and where your version comes from.
- Do not copy invite links (for example the Telegram chat), passwords, or demo logins into notes. Write that the link is on the material page.
- Write in the gaps section which pictures, diagrams, and leftover blocks you did not use.

## Questions for review

- Write 5 to 8 questions for each note.
- Mark the source of each question. Use `[Claude]` for your questions. Use `[Курс]` for questions from the course.
- Ask questions about understanding, not about memory only.
- Do not use the real LMS test questions. Do not give answers to the LMS tests or surveys.
- When the user asks for a quiz, ask one question at a time. Wait for the answer. Then give feedback.
- Add each topic that the user answers badly to `questions.md`.

## Working with the LMS

- Never enter a password. The user logs in.
- If the LMS asks for a login, stop. Ask the user to log in.
- The LMS does not open without the Russian root certificates (Минцифры). The user must install them by hand: https://www.gosuslugi.ru/landing/crt (see `SETUP.md`, step 0).
- Never install certificates or change security settings yourself. If the LMS shows a certificate error, stop and send the user to `SETUP.md`, step 0.
- Use a browser for LMS pages, not `curl`. `curl` and Python do not use the system certificate store in the same way, so they can fail even after the user installed the certificates.
- `curl` is fine for the material files on Yandex Cloud storage (`tb-box-…storage.yandexcloud.net`) and for Kinescope. To get the size of a file without a download, use `curl -sI <url>` and read `content-length`. On Windows, write `curl.exe`.
- The default browser is the built-in browser of the Claude desktop app. Its LMS session can break. Seen in October 2026: every page redirected to `/auth/sso/oauth/new` with error 500; later the login page of the Positive portal (`idp.myportal.ptsecurity.com`) opened instead. Claude in Chrome worked with the user's login then. If the built-in browser cannot open the LMS or asks for a login, tell the user. Ask before you switch to Chrome.
- The course team says that the LMS works best in Yandex Browser. If the LMS shows errors, tell the user about this advice.
- Opening a material in the LMS can mark it as "completed". This changes the user's progress.
- The material data has `seconds_for_complete` (20 seconds in one course). Even a short visit to the material page can count as viewed.
- Do not open a material that the user has not asked for.
- Never take a test or survey. Never send answers.

### Course structure

- The course page loads `GET /api/v2/course_sessions/<session>/take`. The session number is in `course.md`. You can read the same response with `fetch` from the course page. It does not open any material.
- The response has `data.course.sections[]`. Each section has `materials`, `quizzes`, `polls`, `tasks`, and `links`.
- Useful fields of a material: `id`, `title`, `section_position` (the place in the list), `completed`, `source` (the HTML file of the page), `seconds_for_complete`.
- Use this response for IDs, positions, and "completed" flags. Check the order against the list on the course page.

### Material files

- A document material is a Tilda page saved as an HTML file on Yandex Cloud storage. The `source` field has its URL. The LMS shows this file in a frame.
- You can read the `source` file directly when the user has asked for the material.
- Reading the `source` file does not mark the material as completed. Checked in October 2026: after 24 materials were read from their `source` files, all 24 still had `completed: false`, and the progress on the course page did not change. Tell the user that these materials still count as not done. To get progress, the user opens them in the LMS.
- Read the progress percent on the course page. The field `course_stat.progress` in the API is not the percent: it was 11 when the page showed 5%. Maybe it is the number of completed items. Not sure.

## Reading material pages

Tilda pages are hard to read as text. Follow these rules:

- `get_page_text` gives blocks in code order, not in screen order. Get the order from the block positions on the page: top first, then left.
- Responsive layouts repeat the same text. Remove the repeats.
- Collapsed blocks (accordions, "Пример »", "Узнай больше") are hidden with `display: none`. They are part of the material. Read them.
- Some pages have leftover blocks from other materials. They are inside `.t-popup` or below the end of the page (`document.documentElement.scrollHeight`). Do not use them in the note. Example: a block about another protocol below the end of the page.
- Tables with icons (✓, ✗) have no text in the cells. Check them on a screenshot.
- Many pictures and diagrams do not load (lazy loading). Write in the note which pictures you did not check.
- Tool results can cut long strings. Read long texts in parts.

## Downloads

- Ask the user before each download. Say the file name, the source, and the size. If you cannot get the size, say so.
- Links to `storage.ptsecurity.com` (for example `?dl=1` or `seafhttp/...?op=view`) can start a download at once. A visit to such a link is a download. Do not open it without the user's approval.
- A visit to a `storage.ptsecurity.com` link once froze the Chrome tab. If a tab stops responding, stop. Close your tab. Tell the user to check Chrome for an open dialog.
- After a download attempt, check the user's Downloads folder (`~/Downloads`) for files that the browser saved. Tell the user what you found.
- Download each file into a new empty folder in your scratchpad first. Check it: `python -I scripts/attachment_register.py <file> --dry-run` shows the kind, the size, and the PCAP format; use `ffprobe` for a video. Then move the file to its place.
- Save videos and other course files (PDF, slides, course map) in `media/<week>/`. Use the naming rules. Example: `m4000-course-map.pdf`.
- Save the files of materials (PCAP, archives, ...) in `attachments/<week>/`. See "Attachments".

When `storage.ptsecurity.com` does not answer:

- In October 2026 the host did not answer from one computer for a day (ports 443 and 80, also outside the sandbox). Other sites worked. Two days before, a download from it worked.
- Check the hosts once: `python -I scripts/doctor.py --net`. Do not retry in a loop.
- If the host does not answer, tell the user. Offer three ways: try later, use a VPN or another network, or the user downloads the files by hand.
- Files that the user downloads by hand go to `attachments/<week>/incoming/` with their original names. You then move each file to `attachments/<week>/` with the right name and register it (see "Attachments"). This is the first name you give the file, so the rule "never rename" does not apply yet.

## Videos and transcripts

1. Ask the user before the download. Say the name, the host, and the size (see "Video hosts").
2. Download the video with `yt-dlp` and the LMS referer (for Kinescope, see "Kinescope" below). Keep the best quality. Do not re-encode. Download into your scratchpad, check with `ffprobe`, then move the file to `media/<week>/`.
3. Run `python -I scripts/transcribe.py <video>`. It makes the transcript in `transcripts/<week>/`. It deletes the temporary audio.
   - The script picks the engine and the model by the hardware: NVIDIA GPU gives `faster-whisper` with `large-v3`; a Mac gives `whisper.cpp` with `large-v3`; no GPU gives `faster-whisper` with a smaller model.
   - Use `--dry-run` to see the choice. Use `WHISPER_BACKEND` and `WHISPER_MODEL` to override it.
   - The first run can download a model (up to 3 GB). Tell the user before it.
4. Fix the transcript (see "How to fix a transcript"). Check the end of the file for repeated lines.
5. Write the note. Mark uncertain words in the note.
6. Update the row in `sources/manifest.csv`.

Never commit `media/`. Never delete a video unless the user asks.

### How to fix a transcript

- The transcript is plain text without timestamps.
- Run `python -I scripts/transcript_fix.py scan <transcript>`. It lists the lines with a known error from `whisper-fixes.md` and the runs of repeated lines. It changes nothing. Check each hit by meaning: the table gives candidates, not sure errors.
- Write the planned replacements to a file in your scratchpad, one per line: `old phrase => new phrase`. Use whole phrases.
- Run `python -I scripts/transcript_fix.py apply <transcript> <fixes>`. It shows the diff and changes nothing. Read the diff.
- Then add `--write --backup <scratchpad>/<name>.raw.txt`. The script copies the raw file first. It replaces whole words only and stops if a phrase is not found or the number of lines changes.
- Fix only clear errors in terms and names. Leave unclear words as they are and list them in the note.
- Add new cases to the table in `whisper-fixes.md`.

### Video hosts

- Videos are on Vimeo or Kinescope. The material page shows the host and the id. Example: `data-videolazy-type="kinescope"` and `data-videolazy-id`.
- Before you ask for the download, check that `yt-dlp` supports the host. If it does not, tell the user.
- Get the size before you ask: `yt-dlp -F` lists the formats with sizes and does not download. For Kinescope, use `scripts/kinescope.py` (below).
- In `sources/manifest.csv`, write the video id in `video_id` and the host in `video_host` (`vimeo` or `kinescope`). Leave both empty for documents.

### Kinescope

- `yt-dlp` has no Kinescope extractor. Its generic extractor finds the playlist but breaks the signed URL (`&amp;` instead of `&`) and gets error 403.
- Run `python -I scripts/kinescope.py <id>`. It prints the title, the length, and the formats with sizes. It downloads nothing.
- To download: `python -I scripts/kinescope.py <id> --download -f '<video format>+<audio format>' -o <scratchpad>/<name>.mp4`. It merges the best video and the audio without re-encoding.
- What the script does, if you need to do it by hand:
  1. Get the player page with the LMS referer: `curl -sS -H 'Referer: https://lms.edu.ptsecurity.com/' https://kinescope.io/embed/<id>`.
  2. Find the `master.m3u8` URL in it. Replace `&amp;` and `\u0026` with `&`.
  3. List the formats: `yt-dlp -F --referer https://kinescope.io/embed/<id> '<m3u8 url>'`.
  4. Download the video and the audio: `-f '<video id>+<audio id>' --merge-output-format mp4`.
- The signed URL works only for a short time. Do not save it in the repository, in a note, or in the manifest. Do not print the `sign` parameter. The script hides it.

## Attachments

Some materials have a file for download: PCAP, archive, binary, dataset, VM image, document. The user wants to keep these files.

1. Ask the user before the download. Say the file name, the source, and the size.
2. Download the file from the link in the material into your scratchpad (see "Downloads"). Do not change the file.
3. Move it to `attachments/<week>/`. Use the naming rules above.
4. Run `python -I scripts/attachment_register.py <file> --material-id <id> --week <n> --original-name <name> --source-url <url>`. It detects the kind (`pcap`, `archive`, `binary`, `dataset`, `vm-image`, `document`, `other`) and adds the row to `sources/attachments.csv`: `id`, `material_id`, `week`, `kind`, `original_name`, `file`, `sha256`, `size`, `meta`, `source_url`, `downloaded`, `analyzed`. The `meta` column is JSON: format, packets, and duration for a PCAP; the file count, `encrypted`, and `unsafe_paths` for a zip or tar archive.
5. Update the attachment table in `README.md`.
6. In the note, write what the file is, where it comes from, and what the material says to do with it. `(network)` For a PCAP, write which frames matter and what they show. Use frame numbers from the PCAP.
7. Update `analyzed` only after you check the note against the file.

Safety rules for all attachments:

- A file can hold real malware or exploit data. Treat it as untrusted.
- Never run, open, unpack, mount, or import it, unless the user asks and the task is in the course lab. Then work only in the isolated environment that the course gives (for example the lab VM).
- For an archive, list the names only. If `unsafe_paths` is true, never extract it outside a lab VM.
- If an archive has a password, take it from the text of the material. Never guess or brute-force it.
- Do not upload a file to an online scanner or sandbox. This shares course material. Do it only if the user asks.
- Never commit `attachments/`. Never delete an attachment unless the user asks.
- Put the user's own results from the labs (captures, reports) in `labs/<week>/`, not in `attachments/`.

Extra rules for a PCAP `(network)`:

- Open a PCAP only in Wireshark, `tshark`, or other read-only analysis tools.
- Never replay PCAP traffic on a real network.
- Never run, open, or unpack a file that you extract from a PCAP, unless the user asks and the task is in the course lab.

## Lab trainer

Some courses run the labs on a separate platform (тренажёр), not in the LMS. `course.md` says if the course has one, when it opens, how many attempts a question has, and how many solved labs the certificate needs.

- Never submit an answer in the trainer. The attempts are limited. After the last wrong answer the lab counts as not solved. The user submits answers.
- You can help the user to analyse the data and to check an idea. Say how sure you are.
- Access can go through a VPN config (for example OpenVPN) and personal credentials that come by email. Never copy the config, keys, or credentials into the repository, a note, or a chat message. Never commit them.
- The trainer can have its own theory. The trainer can close after the course, and this theory is gone then. Before the end of the course, remind the user. Summarize the trainer theory only when the user asks for it.
- Put the user's own captures and lab reports in `labs/<week>/`.

## Detections `(network)`

- You can copy Suricata rules from the materials to `detections/`.
- Copy a rule only after you test it on the PCAP from the material. Use `suricata -r` or Dalton.
- Write the source next to the rule: the material id, the item number, and the `sid` if the material shows it.
- Never test rules on a real network.

## Tools and environment

`python -I scripts/doctor.py` finds the tools also outside `PATH`. Where they usually are:

| Tool | macOS | Windows |
|---|---|---|
| `tshark`, `capinfos`, `editcap` | `/Applications/Wireshark.app/Contents/MacOS/`. Not in `PATH`: use the full path. | `C:\Program Files\Wireshark\`. Often not in `PATH`. |
| `yt-dlp`, `ffmpeg`, `ffprobe` | `/opt/homebrew/bin/` (Homebrew) | in `PATH` after `winget` (open a new shell) |
| `whisper-cli` | `/opt/homebrew/bin/` | not used |
| Whisper model | `~/.cache/whisper-cpp/ggml-large-v3.bin`. About 6 minutes for 1 hour of audio on Apple M4 Pro. | `faster-whisper` downloads it on the first run |

Helper scripts in `scripts/`:

| Script | What it does |
|---|---|
| `doctor.py [--net]` | Checks the tools, the hardware, and the project. `--net` checks once that the course hosts answer. |
| `transcribe.py <video>` | Makes a transcript of a video. Picks the engine by the hardware. |
| `transcript_fix.py scan\|apply` | Finds known speech-to-text errors and repeats. Replaces whole phrases with a diff and a raw copy. |
| `kinescope.py <id>` | Lists or downloads the formats of a Kinescope video. Hides the signed URL. |
| `attachment_register.py <file>` | Registers an attachment in `sources/attachments.csv`. `--dry-run` only shows the kind, the size, and the meta. |
| `glossary_insert.py <blocks> <glossary> <out>` | Inserts new glossary entries. Stops if an old line would change. |
| `check_glossary.py` | Checks the order, duplicates, and headings of the glossary, and the `[[glossary#...]]` links. |
| `check_links.py` | Checks that every other `[[link]]` points to an existing note. |

Shell pitfalls:

- Run Python with `-I`. For checks over many files, Python is safer than shell loops.
- macOS has no `timeout` command. Use the timeout of the tool call.
- In zsh, `echo =====` fails (`=` expansion). Put such text in quotes.
- In zsh, a glob without a match stops the command (`no matches found`). Quote the pattern, or do the check in Python.
- In Windows PowerShell 5.1, `curl` is another command (`Invoke-WebRequest`). Write `curl.exe`.
- On Windows, use `py` if `python` is missing.

## Do and do not

- Do ask the user before a download, an install, or a change of a setting.
- Do tell the user when a result is uncertain.
- Do not guess facts about an attack or a protocol. Say "not sure" and mark the gap.
- Do not test any attack on a real network. Practical tasks run only in the course lab.
- Do not publish or share course materials.
- Do not edit the user's own notes without being asked. Add new text in a separate section.

## Progress

Update `README.md` after each material: status, date, and open questions.
