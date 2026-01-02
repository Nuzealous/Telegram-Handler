"""
Telegram Handler. The code is all in one.
For more details, e.g. command prompts, please refer to README.md
"""

# ----- standard libaries -----
import asyncio  # asynchronous programming
import datetime  # timestamps, formatting dates, logs, etc.
import re  # regular expressions > for parsing
import textwrap  # formats long text, e.g. wrapping
import json  # config.json
import os  # communicates with the operating system
from time import sleep  # output delays
import traceback  # error traceback
# ----- third party libraries -----
from telethon import TelegramClient  # Telethon core
from telethon.errors import SessionPasswordNeededError  # pinpoints login errors

# ===== Start & End =====

# for a neater interface


def program_start():
    print("\n" + "💨"*40 + "\n")


def program_end():
    print("\n" + "🍁"*40 + "\n")


def unexpected_error():
    """
    A message for contact details in case of bugs/errors.
    """
    print("\n❗" + "💬"*5)
    print("Message From Author:")
    sleep(1)
    print("Apologies for the error; it seems that there are bugs I have yet to handle.")
    sleep(0.5)
    print("Kindly report it at:")
    sleep(0.5)
    print(f"""
    - GitHub >> https://github.com/username/reponame/issues
    """)
    sleep(0.2)
    print("Do attach a complete copy of the traceback, thank you!")
    print("I've tried to sanitise the directories, but in case some leaks, please don't hesitate to redact it.")
    sleep(0.1)
    print("We will be in touch shortly; I appreciate your time and patience.")
    print("\n—Nuzealous")
    print("💬"*5 + " ❗\n")


# ===== Config(uration) =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
SESSION_NAME = os.path.join(BASE_DIR, "userbot_session")
# to save files in the same folder ^
DELAY = 1.5
last_sent_message = None  # global variable; tracks bot's last sent message


def start_load_config():
    """
    Load configuration from a JSON file.
    If the file does not exist, prompt user for details and saves them.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                print("Welcome back!")
                print("\n")
        except Exception:
            print(f"⚠️ Failed to read API details. Please re-insert them.\n")
            config = prompt_and_save_config()
    else:
        print("Welcome!\n")
        config = prompt_and_save_config()

    return config


def prompt_and_save_config():
    """
    Prompts the user for their API credentials and saves them to config.json.
    """
    print("Please enter your Telegram API details. You may get them at https://my.telegram.org\n")
    while True:
        try:
            api_id = int(input("1. Enter your API ID: ").strip())
            if not (-2147483648 <= api_id <= 2147483647):
                raise ValueError("API ID out of valid range")
            break
        except ValueError:
            print("❗ API ID must be a valid 32-bit number. Please try again.")
    api_hash = input("2. Enter your API Hash: ").strip()
    print("\n")
    config = {
        "_comment": "ALERT: This file stores your userbot's customisations. Do not edit manually!",
        "api_id": api_id,
        "api_hash": api_hash
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    return config


async def start_client(api_id, api_hash):
    """
    Tries to start the Telegram client with validation.
    """
    client = TelegramClient(SESSION_NAME, api_id, api_hash)
    while True:
        try:
            await client.start()
            return client
        except SessionPasswordNeededError:  # "never seen", yet keep for headless etc.
            print("Your account has two-factor authentication enabled.")
            password = input("Enter your Telegram password: ").strip()
            await client.sign_in(password=password)
            print("2FA verification successful.")
            return client
        except Exception:
            print("❌ Login failed. Please check your API ID, API Hash, and network.\n")
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)

        # Prompts user for API details if failed
        config = prompt_and_save_config()
        api_id = config["api_id"]
        api_hash = config["api_hash"]


def load_config():
    """
    Loads config from config.json
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)


def save_config(config):
    """
    Saves config to config.json
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


async def select_groups(client, config):
    """
    Prints a list of all groups, and prompts the user to select groups to monitor.
    Stores selection in config['selected_groups'] as list of IDs.
    """
    dialogs = await client.get_dialogs()
    groups = [d for d in dialogs if d.is_group or d.is_channel]
    if not groups:
        print("🔲  No groups/channels found for your account.")
        return []
    saved = config.get("selected_groups", [])
    # checks whether to keep previous group selections or re-choose
    if saved:
        saved_groups = [g for g in groups if g.id in saved]
        saved_names = [g.name for g in saved_groups]
        while True:
            names_str = ", ".join(saved_names)
            choice = input(
                f"Continue with previous channels/groups -- {names_str}? (Y/N): ").strip().lower()
            if choice in ("y", "yes"):
                print("\nCurrent active groups (use these as group labels):")
                for index, name in enumerate(saved_names):
                    print(f"""{index+1}. {name}""")
                return saved
            elif choice in ("n", "no"):
                break
            else:
                print("❗ Please answer 'Y' or 'N'.")
    # Displays all groups
    print("\nSelect channel/groups to monitor (comma-separated numbers):")
    for i, g in enumerate(groups):
        print(f"{i + 1}. {g.name}")
    while True:
        selected_input = input("Enter group numbers: ").strip()
        if not selected_input:
            print("❗ Please enter at least one number.")
            continue
        indexes = []
        invalid = False
        for x in selected_input.split(","):
            x = x.strip()
            if not x.isdigit():
                invalid = True
                break
            idx = int(x) - 1
            if idx < 0 or idx >= len(groups):
                invalid = True
                break
            indexes.append(idx)
        if invalid or not indexes:
            print(
                "❗ Invalid input. Enter valid comma-separated numbers corresponding to groups.")
            continue
        selected_ids = [groups[i].id for i in indexes]
        config["selected_groups"] = selected_ids
        save_config(config)
        selected_names = [groups[i].name for i in indexes]
        print("\nCurrent active groups (use these as group labels):")
        for index, name in enumerate(selected_names):
            print(f"{index+1}. {name}")
        return selected_ids

# ===== Telegram Login =====


async def start_client(api_id, api_hash):
    """
    Starts the Telegram client
    """
    client = TelegramClient(SESSION_NAME, api_id, api_hash)
    while True:
        try:
            await client.start()
            return client
        except SessionPasswordNeededError:
            password = input(
                "Your account has 2FA enabled. Enter password: ").strip()
            await client.sign_in(password=password)
            return client
        except Exception as e:
            print(f"❌ Failed to start client: {e}")
            config = load_config()
            api_id = int(input("Re-enter API ID: "))
            api_hash = input("Re-enter API Hash: ")
            config.update({"api_id": api_id, "api_hash": api_hash})
            save_config(config)

# ===== Main =====


async def main():
    global last_sent_message
    config = load_config()
    # Prompt for API if missing
    if not config.get("api_id") or not config.get("api_hash"):
        while True:
            try:
                api_id = int(input("Enter your API ID: ").strip())
                api_hash = input("Enter your API Hash: ").strip()
                config["api_id"] = api_id
                config["api_hash"] = api_hash
                save_config(config)
                break
            except ValueError:
                print("❗ API ID must be a number.")
    client = await start_client(config["api_id"], config["api_hash"])
    async with client:
        me = await client.get_me()
        username = f"@{me.username}" if me.username else "(no username set)"
        print(f"\nLogged in as -- Name: {me.first_name}, Username: {username}")
        print("\n✅ Userbot started successfully. Press Ctrl+C to terminate userbot.\n")
        # group selection process
        selected_ids = await select_groups(client, config)
        dialogs = await client.get_dialogs()
        selected_groups = [d for d in dialogs if d.id in selected_ids]

        # helper functions

        async def copy_messages(group, limit=10, wrap_width=60):
            history = await client.get_messages(group, limit=limit)
            # reverse to print oldest > newest
            history = list(reversed(history))
            print(f"\nLast {limit} messages from {group.name}:")
            for m in history:
                if m.sender_id:
                    try:
                        sender = await client.get_entity(m.sender_id)
                        # Get display name
                        name = getattr(sender, 'first_name', str(m.sender_id))
                        # Get username/fallback
                        username = getattr(sender, 'username', None)
                        sender_label = f"{name}, @{username}" if username else f"{name}, (username not set)"
                    except Exception:
                        sender_label = str(m.sender_id) + " (username not set)"
                else:
                    sender_label = "Unknown, (username not set)"
                # Timestamp
                local_time = m.date.astimezone().strftime("%Y-%m-%d %H:%M:%S")
                # Message text
                msg_text = m.message if m.message else "*non text*"
                wrapped_text = textwrap.fill(msg_text, width=wrap_width)
                # Reactions
                reaction_info = ""
                if getattr(m, "reactions", None) and m.reactions.results:
                    reactions = [
                        f"{getattr(r.reaction, 'emoticon', str(r.reaction))} x{r.count}"
                        for r in m.reactions.results
                    ]
                    reaction_info = " | Reactions: " + ", ".join(reactions)
                # Prints
                print(
                    f"[{local_time}] {sender_label}:{reaction_info}\n{wrapped_text}\n")

        async def get_last_message(groups):
            last_msg = None
            for g in groups:
                history = await client.get_messages(g, limit=1)
                if history:
                    msg = history[0]
                    if not last_msg or msg.date > last_msg.date:
                        last_msg = msg
            return last_msg

        async def execute_command(command: str):
            global last_sent_message
            command = command.strip()
            # <copy1>10  (copies last 10 messages from Group 1)
            copy_match = re.match(r"<copy(\d+)>(\d*)", command)
            if copy_match:
                grp_idx = int(copy_match.group(1)) - 1  # group index, 0-based
                num_msgs = int(copy_match.group(2)) if copy_match.group(
                    2) else 10  # default 10 messages
                if 0 <= grp_idx < len(selected_groups):
                    await copy_messages(selected_groups[grp_idx], num_msgs)
                    print(
                        f"✅ Copied last {num_msgs} messages from {selected_groups[grp_idx].name}")
                else:
                    print("❗ Invalid group number. Please try a different number.")
                return

            # <send1>Message
            send_match = re.match(r"<send(\d+)>(.+)", command)
            if send_match:
                grp_idx = int(send_match.group(1)) - 1
                msg = send_match.group(2).strip()
                if 0 <= grp_idx < len(selected_groups):
                    last_sent_message = await client.send_message(selected_groups[grp_idx], msg)
                    print(f"✅ Message sent to {selected_groups[grp_idx].name}")
                    await asyncio.sleep(DELAY)
                else:
                    print("❗ Invalid group number. Please try a different number.")
                return

            # <reply>Message
            reply_match = re.match(r"<reply>(.+)", command)
            if reply_match:
                msg = reply_match.group(1).strip()
                last_msg = await get_last_message(selected_groups)
                if last_msg:
                    last_sent_message = await client.send_message(last_msg.chat_id, msg, reply_to=last_msg.id)
                    print("✅ Reply sent")
                return

            # <paste1>  (copies and pastes the last message from Saved Messages to group 1)
            paste_match = re.match(r"<paste(\d+)>", command)
            if paste_match:
                grp_idx = int(paste_match.group(1)) - \
                    1  # convert to 0-based index
                if 0 <= grp_idx < len(selected_groups):
                    # Get last message sent in Saved Messages
                    saved = await client.get_entity("me")
                    history = await client.get_messages(saved, limit=1)
                    if history:
                        msg_to_send = history[0]
                        await client.forward_messages(selected_groups[grp_idx], msg_to_send)
                        print(
                            f"✅ Sent message to {selected_groups[grp_idx].name}")
                else:
                    print("❌ Invalid group number.")
                return

            # <edit>New text
            edit_match = re.match(r"<edit>(.+)", command)
            if edit_match and last_sent_message:
                new_text = edit_match.group(1).strip()
                await client.edit_message(last_sent_message, new_text)
                print("✅ Message edited")
                return

            # <delete>
            if command.startswith("<delete>") and last_sent_message:
                await client.delete_messages(last_sent_message.chat_id, last_sent_message)
                print("✅ Message deleted")
                last_sent_message = None
                return
            print("❌ Unknown command")

        # Command loop
        while True:
            cmd = input("\nEnter command: ")
            await execute_command(cmd)

# ===== Error Catching =====

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting safely; see you soon.")
        program_end()
    except Exception:
        print("\n🚨🚨 A fatal error has occurred. 🚨🚨\n")
        tb = traceback.format_exc()
        # Replace project directory paths
        tb = tb.replace(str(BASE_DIR), "<PROJECT_DIR>")
        # Replace absolute paths
        tb = re.sub(r"[A-Z]:\\[^:\n]*", "<ABS_PATH>", tb)  # Windows
        tb = re.sub(r"/[^:\n]*", "<ABS_PATH>", tb)  # Unix/Linux
        print(tb)  # sanitized traceback
        unexpected_error()

# ========== END OF CODE ==========
