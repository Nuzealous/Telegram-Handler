# Telegram-Handler
A userbot-powered program made using Telethon, allowing users to manage across multiple Telegram groups in their Python terminal using simple command syntax.

## Command Syntax/Format

1. <copy{group_number}>{number_of_messages} -- Copies the last {number_of_messages} messages from the group labelled {group_number}
2. <send{group_number}>{Message to be sent} -- Sends {message_to_be_sent} to the group labelled {group_number}
3. <reply>{Message_to_be_sent} -- Replies to the last message sent across all selected groups with the {message_to_be_sent}
4. <paste{group_number}> -- Copies the last message sent in your Telegram's Saved Messages to the group labelled {group_number}
5. <edit>{Message_to_be_replaced} -- Edits the last message sent by the user across all selected groups to {message_to_be_replaced}
6. <delete> -- Deletes the last message sent by the user across all selected groups.

```Examples:
<copy1>10
<send3>Welcome!
<reply>See you soon!
<paste2>
<edit>That's *great.
<delete>```

## Installation
Running `main.py` is all that is needed to launch the program.
It is recommended to save `main.py` in a dedicated folder before running it.

Be sure to read the `README.md` and `LICENSE` files for detailed instructions and licensing information.

## Let's get in touch
Join my Telegram channel for updates, polls, and more coding fun: https://t.me/NutTub
Looking forward to seeing you there!
