import imaplib
import email
from email.header import decode_header

username = "k.badal19@gmail.com"
password = "mgwi rrnj oily lluc"

imap = imaplib.IMAP4_SSL("imap.gmail.com")

imap.login(username, password)

imap.select("INBOX")

specific_date = "16-Sep-2024"


status, messages = imap.search(None, f'ON "{specific_date}"')
messages = messages[0].split(b' ')

if not messages[0]:
    print(f"No emails found for {specific_date}.")
else:
    for mail in messages:
        try:
            res, msg_data = imap.fetch(mail, "(RFC822 FLAGS)")

            for response in msg_data:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])

                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    flags = response[0].decode()
                    if '\\Flagged' not in flags:
                        print(f"Deleting: {subject}")
                        imap.store(mail, "+FLAGS", "\\Deleted")
                    else:
                        print(f"Skipping (starred): {subject}")

        except Exception as e:
            print(f"Error processing email {mail}: {e}")
    imap.expunge()
imap.close()
imap.logout()
