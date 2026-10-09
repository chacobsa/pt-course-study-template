---
name: init-course
description: Set up this study repository for one Positive Education course. Fills course.md, creates README.md, sources/manifest.csv rows and the week folders. Use once, when course.md still has TODO values, or when the user types /init-course.
---

# init-course

Prepare this repository for the user's course. Follow [AGENTS.md](../../../AGENTS.md). Talk to the user in Russian.

## Steps

1. Run `python -I scripts/doctor.py --net` (`python3` on macOS). Show the result. If a required tool is missing, point the user to `SETUP.md` and ask before you install anything. If a course host does not answer, tell the user (see AGENTS.md, "Downloads").
2. Ask the user for the LMS link (`.../course_sessions/<id>`) and the course profile (`network`, `general` or `attachments`; explain each in one line, see the Course profile section of AGENTS.md). Do not guess.
3. Ask the user: "Вы установили сертификаты Минцифры (https://www.gosuslugi.ru/landing/crt, см. SETUP.md, шаг 0)?" If no, stop. The user installs them by hand. Never install certificates yourself.
4. Open the course page in the built-in browser.
   - If it shows a certificate error, stop and send the user back to step 0 of `SETUP.md`.
   - The user logs in. If the LMS asks for a login, stop and ask the user to log in. Never enter a password.
   - If the built-in browser cannot open the LMS, tell the user and give the Yandex Browser advice. Ask before you switch to Claude in Chrome.
   - Read only the course page: the description, the completion rules, the schedule, the progress. Do not click any material, test, or survey. A click can mark it as completed.
5. Read the course structure with `fetch('/api/v2/course_sessions/<session>/take')` from the course page (see AGENTS.md, "Course structure"). It opens no material.
   - Match the sections to the weeks on the course page.
   - In each open section, sort all items (`materials`, `quizzes`, `polls`, `tasks`) by `section_position`. Check the result against the list on the course page. Count section headers too.
   - Note the hidden resources in `links`. They get no number.
   - Note `seconds_for_complete` and the `completed` flags.
6. Show the user what you found: the course name, the period, the number of weeks, the completion rules, the lab trainer facts, and the item list of the open weeks. Ask the user to confirm or fill the gaps. Do not guess.
7. Write the facts to `course.md`. Replace all `TODO` values. Write `—` for a fact that does not apply.
8. Create `README.md` from `README.template.md`. Fill the placeholders.
   - Add the table rows of the open weeks in the LMS order, with numbers `<week>-<position>` as in AGENTS.md. Material rows get the ID from the structure. Test and poll rows get `—`.
   - Write the hidden resources in the notes under the table.
   - For a profile other than `network`, delete the section "Темы атак".
   - Add the known attachments of the open weeks to the attachment table only when the user has asked for those materials. Do not open materials to look for files.
9. Add a row to `sources/manifest.csv` for each material of the open weeks: `id`, `week`, `seq`, `title_ru`, `lms_url` (`https://lms.edu.ptsecurity.com/viewer/sessions/<session>/materials/<id>`). Leave `kind`, `slug`, and the video columns empty until you work on the material. Write `no` in `downloaded`, `transcribed`, and `summarized`. Add the hidden resources with `kind` = `resource` and an empty `seq`.
10. Create the folders for the open weeks by profile. Add `.gitkeep` only in folders that Git must keep (`notes`, `transcripts`, `labs`).
    - All profiles: `notes/<week>/`, `transcripts/<week>/`, `media/<week>/`, `labs/<week>/`.
    - `network`: also `attachments/<week>/`, `detections/`, `cheatsheets/`.
    - `attachments`: also `attachments/<week>/`.
    - `general`: no `attachments/` yet. Create it when a material has a file.
    - Create `attachments/<week>/incoming/` only when the user downloads files by hand.
    - For a profile other than `network`, delete the "Атака" section from `templates/note.md` and remove the `(network)` parts of AGENTS.md only if the user asks.
11. Run `python -I scripts/check_links.py`. Repair the problems.
12. Ask the user if you can delete `README.template.md`. The new `README.md` already has a link to the template at the end.
13. Tell the user what you filled, what is still unknown, that reading the structure did not change the progress, and the next step: pick the first material and run the note workflow.

## Do not

- Do not open materials, take tests or surveys, or send answers.
- Do not enter passwords.
- Do not commit or push. Offer it to the user.
