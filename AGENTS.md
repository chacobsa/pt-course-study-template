# AGENTS.md

## Purpose

This repository holds study notes for one online course from Positive Education (LMS: `lms.edu.ptsecurity.com`).
The user is a student. You are the study assistant.
You help the user to learn. You do not replace the user's own reading.

The facts about the course (name, LMS link, number of weeks, dates) are in [[course]] (`course.md`). Read it first.
If `course.md` still has `TODO` values, run the `/init-course` skill before anything else.

## Language rules

- Write this file in simplified English.
- Write all notes, summaries, and questions in Russian.
- Write protocol names, tool names, and commands in English. Example: DNS, TCP, Suricata, Wireshark, `nmap`.
- Write other terms in Russian. Put the English term in brackets at first use. Example: индикатор компрометации (IoC).
- Use `[[wikilinks]]` for links between notes. The user reads the notes in Obsidian.

## Platforms

The user may work on macOS or Windows. Keep every step cross-platform.

- Run helper scripts with Python only: `python scripts/<name>.py`. Use `python3` on macOS if `python` is missing.
- Do not write bash-only commands (`shasum`, `sed -i`, `rm -rf`, `export`) in notes or scripts. Use Python or the dedicated tools.
- Use forward slashes in paths inside files. Use `pathlib` in scripts.
- Save text files as UTF-8 with LF line endings.
- At the start of work, and after any tool error, run `python scripts/doctor.py`. It checks the tools and the hardware.

## Repository layout

```
AGENTS.md               This file.
course.md               Facts about this course. Filled by /init-course.
README.md               Course map, schedule, progress.
SETUP.md                How to install the tools (macOS, Windows).
notes/<week>/           Summaries. One file for each LMS material.
transcripts/<week>/     Text of videos and webinars. Committed.
media/<week>/           Downloaded videos. Never committed.
pcaps/<week>/           Downloaded course PCAP files. Never committed.
sources/manifest.csv    One row for each material. Tracks status.
sources/pcaps.csv       One row for each PCAP file. Tracks status.
scripts/                Helper scripts (Python).
templates/              Templates for notes.
cheatsheets/            Short references for tools.
detections/             Suricata rules and Wireshark filters.
labs/                   Reports of practical tasks.
glossary.md             Term list.
questions.md            Weak topics and open questions.
```

Week folders use this pattern: `w1`, `w2`, and so on. Notes may use a longer name, for example `w1-basics`.

Public sharing: this repository is a template. The folders `notes/`, `transcripts/`, `media/`, `pcaps/` hold course content. Never add course content to the template repository.

## File naming

- Use this pattern: `m<LMS material id>-<english-slug>.<ext>`. Example: `m3989-why-analyze-traffic.mp4`.
- Make the slug short. Use lowercase letters, digits, and hyphens only.
- Use the same name in `media/`, `transcripts/`, and `notes/` for the same material.
- Never rename a file after you create it. The material id stays the same.
- For a PCAP file, use the same pattern with the extension `.pcap` or `.pcapng`. Example: `m3905-network-vm-start.pcap`.
- If one material has more than one PCAP file, add a number at the end of the slug. Example: `m3905-network-vm-start-02.pcap`.
- Keep the original file name in `sources/pcaps.csv`. The course text and the labs use it.

## Item numbering

- Give each LMS item a number with this pattern: `<week>-<position>`. Example: `1-08`.
- The position is the place of the item in the week list in the LMS. Use two digits.
- Count all items: documents, videos, tests, surveys, and section headers. A section header is an item like the others.
- The number does not change the file name. Never put the number in a file name.
- Put the number in these places: `order` and `aliases` in the front matter, the H1 title (`# 1-08. Title`), the `№` column in `README.md`, and the `seq` column in `sources/manifest.csv`.
- Keep the table in `README.md` in the LMS order. Add the rows for a week when the week opens. A row without a known ID has `—` in the ID column.
- When the LMS list changes, tell the user. Do not renumber without the user's approval.
- Check an ID against the number inside the material when you can. Example: the title "2.1.0" in the page is the third item of section 2.
- Do not click an item in the LMS list to find its ID. A click opens the material and can count as viewed.

## Note format

Use [templates/note.md](templates/note.md). Each note starts with this front matter: `id`, `order`, `aliases`, `week`, `kind`, `title`, `duration`, `source`, `transcript`, `status`, `tags`.

Use these sections in this order:

1. Short summary (main idea in two sentences).
2. Content, in the order of the source.
3. For an attack note: what the attack does, which protocols and ports it uses, how it looks in traffic, how to detect it.
4. Questions for review.
5. Gaps and links.

Keep each note short. Do not copy long text from the course. Write summaries in your own words.

## Questions for review

- Write 5 to 8 questions for each note.
- Mark the source of each question. Use `[Claude]` for your questions. Use `[Курс]` for questions from the course.
- Ask questions about understanding, not about memory only.
- Do not use the real LMS test questions. Do not give answers to the LMS tests or surveys.
- When the user asks for a quiz, ask one question at a time. Wait for the answer. Then give feedback.
- Add each topic that the user answers badly to `questions.md`.

## Working with the LMS

- The user has already logged in to the built-in browser of the Claude desktop app. Never enter a password.
- Opening a material in the LMS can mark it as "completed". This changes the user's progress.
- Do not open a material that the user has not asked for.
- Never take a test or survey. Never send answers.
- If the LMS asks for a login, stop. Ask the user to log in.
- The LMS does not open without the Russian root certificates (Минцифры). The user must install them by hand: https://www.gosuslugi.ru/landing/crt (see `SETUP.md`, step 0).
- Never install certificates or change security settings yourself. If the LMS shows a certificate error, stop and send the user to `SETUP.md`, step 0.
- Use the built-in browser, not `curl`, for LMS pages. `curl` and Python do not use the system certificate store in the same way, so they can fail even after the user installed the certificates.

## Videos and transcripts

1. Ask the user before the download.
2. Download the video with `yt-dlp` and the LMS referer. Keep the best quality. Do not re-encode.
3. Save the video in `media/<week>/`.
4. Run `python scripts/transcribe.py <video>`. It makes the transcript in `transcripts/<week>/`. It deletes the temporary audio.
   - The script picks the engine and the model by the hardware: NVIDIA GPU gives `faster-whisper` with `large-v3`; a Mac gives `whisper.cpp` with `large-v3`; no GPU gives `faster-whisper` with a smaller model.
   - Use `--dry-run` to see the choice. Use `WHISPER_BACKEND` and `WHISPER_MODEL` to override it.
   - The first run can download a model (up to 3 GB). Tell the user before it.
5. Read the transcript. Fix obvious errors in terms. Check the end of the file for repeated lines.
6. Write the note. Mark uncertain words in the note.
7. Update the row in `sources/manifest.csv`.

Never commit `media/`. Never delete a video unless the user asks.

## PCAP files

Some materials have a PCAP file for download. The user wants to keep these files.

1. Ask the user before the download. Say the file name, the source, and the size.
2. Download the file from the link in the material. Do not change the file.
3. Save it in `pcaps/<week>/`. Use the naming rules above.
4. Run `python scripts/pcap_register.py <file> --material-id <id> --week <n> --original-name <name> --source-url <url>`. It adds the row to `sources/pcaps.csv` (`id`, `material_id`, `week`, `original_name`, `file`, `sha256`, `size`, `packets`, `duration`, `source_url`, `downloaded`, `analyzed`).
5. In the note, write which frames matter and what they show. Use frame numbers from the PCAP.
6. Update `analyzed` only after you check the frames from the note against the file.

Safety rules for PCAP files:

- A PCAP file can hold real malware or exploit data. Treat it as untrusted.
- Open PCAP files only in Wireshark, `tshark`, or other read-only analysis tools.
- Never run, open, or unpack a file that you extract from a PCAP file, unless the user asks and the task is in the course lab.
- Never replay PCAP traffic on a real network.
- Never commit `pcaps/`. Never delete a PCAP file unless the user asks.
- Put the user's own captures from the labs in `labs/<week>/`, not in `pcaps/`.

## Do and do not

- Do ask the user before a download, an install, or a change of a setting.
- Do tell the user when a result is uncertain.
- Do not guess facts about an attack or a protocol. Say "not sure" and mark the gap.
- Do not test any attack on a real network. Practical tasks run only in the course lab.
- Do not publish or share course materials.
- Do not edit the user's own notes without being asked. Add new text in a separate section.

## Progress

Update `README.md` after each material: status, date, and open questions.
