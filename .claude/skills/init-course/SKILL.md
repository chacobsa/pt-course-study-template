---
name: init-course
description: Set up this study repository for one Positive Education course. Fills course.md, creates README.md and the week folders. Use once, when course.md still has TODO values, or when the user types /init-course.
---

# init-course

Prepare this repository for the user's course. Follow [AGENTS.md](../../../AGENTS.md). Talk to the user in Russian.

## Steps

1. Run `python scripts/doctor.py` (`python3` on macOS). Show the result. If a required tool is missing, point the user to `SETUP.md` and ask before you install anything.
2. Ask the user for: the course name, the LMS link (`.../course_sessions/<id>`), the study period, the number of weeks, and the course profile (`network`, `general` or `attachments`; explain each in one line, see the Course profile section of AGENTS.md). Do not guess.
3. Ask the user: "Вы установили сертификаты Минцифры (https://www.gosuslugi.ru/landing/crt, см. SETUP.md, шаг 0)?" If no, stop. The user installs them by hand. Never install certificates yourself.
   Then open the course page in the built-in browser. If it shows a certificate error, stop and send the user back to step 0. The user is already logged in. If the LMS asks for a login, stop and ask the user to log in.
   - Read only the list of items and the course description (completion rules, schedule).
   - Do not click any material. A click can mark it as completed.
4. Write the facts to `course.md`. Replace all `TODO` values.
5. Create `README.md` from `README.template.md`. Fill the placeholders. Add the table rows of the open weeks in the LMS order, with numbers `<week>-<position>` as in AGENTS.md (count all items, including section headers). A row without a known ID has `—` in the ID column.
6. Create the folders for the open weeks by profile. Add `.gitkeep` only in folders that Git must keep (`notes`, `transcripts`, `labs`).
   - All profiles: `notes/<week>/`, `transcripts/<week>/`, `media/<week>/`, `labs/<week>/`.
   - `network`: also `attachments/<week>/`, `detections/`, `cheatsheets/`.
   - `attachments`: also `attachments/<week>/`.
   - `general`: no `attachments/` yet. Create it when a material has a file.
   - For a profile other than `network`, delete the "Атака" section from `templates/note.md` and remove the `(network)` parts of AGENTS.md only if the user asks.
7. Delete `README.template.md` and keep a short pointer to the template at the end of `README.md`. Ask the user first.
8. Tell the user what you filled, what is still unknown, and the next step: pick the first material and run the note workflow.

## Do not

- Do not open materials, take tests or surveys, or send answers.
- Do not enter passwords.
- Do not commit or push. Offer it to the user.
