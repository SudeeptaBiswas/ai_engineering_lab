# Lumen Notes support handbook

Lumen Notes is a made-up note-taking app, used in lesson 4.1. Every fact
below is invented, so a model can only know it by reading this text.

## Accounts and sign-up

You can sign up with an email address or with a Google account. A new
account starts on the Free plan. We send a confirmation email right after
sign-up; the confirmation link works for 48 hours. If it runs out, open the
app and choose "Resend confirmation" on the welcome screen.

One email address can have only one Lumen Notes account. To move notes from
one account to another, export them from the old account and import them in
the new one (see "Export and import"). Usernames can be changed once every
30 days from Settings > Profile.

Children under 13 may not create an account. School accounts are created by
a teacher through Lumen Classroom, which is a separate product with its own
handbook.

## Passwords and sign-in

Passwords must be at least 10 characters long and contain at least one
number. To reset a password, click "Forgot password" on the sign-in page and
enter your email address. The reset link we send expires after 15 minutes
and can be used only once. If you ask for several links, only the newest one
works.

After 5 wrong passwords in a row, the account is locked for 30 minutes. The
lock ends by itself; support cannot unlock it sooner. Signing in with Google
does not use a Lumen password at all, so the lock does not apply to it.

## Two-step sign-in

Two-step sign-in adds a 6-digit code from an authenticator app. Turn it on
in Settings > Security. When you turn it on, you get 8 backup codes. Each
backup code works once. Keep them somewhere safe, for example printed on
paper.

If you lose your phone and your backup codes, support can turn two-step
sign-in off, but only after an identity check: you answer questions about
your account and wait 72 hours. The wait is there so a stranger cannot take
over an account quickly.

## Plans and prices

There are three plans. Free: 3 notebooks, 2 GB of storage, sync on 2
devices. Plus: unlimited notebooks, 50 GB of storage, sync on any number of
devices, 6 euros per month or 60 euros per year. Team: everything in Plus,
plus shared notebooks and admin controls, 9 euros per person per month, with
a minimum of 3 people.

Prices include VAT for customers in the European Union. Students with a
school email address get 40 percent off Plus. The discount is checked again
every 12 months.

## Billing and invoices

We charge the card on the same day of the month that you first upgraded.
If you upgraded on the 31st, months with fewer days are charged on their
last day. Invoices are sent by email as PDF files within one hour of each
payment. Old invoices are also listed in Settings > Billing > History.

We accept Visa, Mastercard and PayPal. Bank transfer is possible only for
Team plans with 20 or more people. If a payment fails, we try again after 3
days and after 7 days. After the third failed try, the account moves back to
the Free plan, and notes over the Free limits become read-only. Nothing is
deleted.

## Refunds

You can ask for a full refund within 14 days of a payment. After 14 days we
do not refund, but you can cancel so the next payment does not happen.
Refunds go back to the card or PayPal account that paid, and take 5 to 10
working days to arrive. Yearly plans cancelled after the 14 days keep their
features until the end of the paid year.

Refunds are handled by the billing team, not by first-line support. Write to
billing@lumen.example with your invoice number.

## Storage and attachments

Each attachment can be at most 200 MB. Images inside notes are shrunk to a
width of 2000 pixels unless "Keep original images" is on. Audio recordings
are saved as M4A files. Deleted notes stay in the Trash for 30 days; after
that they are gone for good and support cannot bring them back.

When an account is over its storage limit, you can still read and edit
existing notes, but you cannot add new attachments.

## Sync

Sync runs every 60 seconds while the app is open, and right away when you
press the sync button. If the same note was changed on two devices while one
was offline, both versions are kept: the second one is saved as a copy with
"(conflict)" in its title. Nothing is merged automatically.

Sync needs app version 7.2 or newer. Older versions can still open notes on
the device but stop syncing.

## Export and import

You can export a single note or a whole notebook as Markdown, PDF or HTML.
A full account export is a ZIP file of Markdown files plus attachments; we
email a download link, and the link stays valid for 7 days. Exports bigger
than 10 GB are split into several ZIP files.

Import works from Markdown files, from plain text files and from ENEX files
made by other note apps. Tags in ENEX files are kept. Import does not bring
over comments or edit history.

## Sharing

Any note can be shared as a read-only web link. Links can have a password
and an end date. Free accounts can share up to 10 links at the same time;
Plus and Team have no limit. A shared notebook (Team only) can have at most
50 members. Members can be viewers, editors or owners; only owners can
delete the notebook.

## Account deletion

To delete an account, go to Settings > Account > Delete account. The account
is first deactivated for 14 days, so you can change your mind by signing in
again. After 14 days all notes, attachments and backups are deleted for good.
A paid plan must be cancelled first; the delete button stays grey until then.

## Support hours and contact

Chat support is open Monday to Friday, 8:00 to 18:00 Central European Time.
Email support at help@lumen.example answers within 2 working days; Team
plans get an answer within 4 working hours. There is no phone support.

## Developer API

The REST API is available on Plus and Team plans. Each API key may make 600
requests per minute; more requests get HTTP status 429 and should wait for
the number of seconds in the Retry-After header. API keys never expire, but
an owner can revoke them at any time in Settings > Developer. Webhooks retry
a failed delivery 5 times over 24 hours.
