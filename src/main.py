from fb_user import set_up_fbuser
from datetime import datetime
from menu import *

"""
This file is the entry point for the program
"""


def main():
    fb_user = set_up_fbuser()
    today = datetime.today()
    # Upon login, automatically update birthday calendar and send scheduled
    # birthday messages
    fb_user.update_birthday_calendar()
    fb_user.send_all_scheduled_birthday_messages(today)
    menu = Menu(fb_user.get_friend_dict())
    while True:
        main_menu_choice = menu.get_main_menu_choice()
        friend_name = menu.get_friend_name()
        friend_uids = get_uid_by_name(friend_name, fb_user.get_friend_dict())

        if len(friend_uids) > 1:
            friend_uid = menu.get_friend_selection()
        else:
            friend_uid = friend_uids[0]

        if main_menu_choice == "edit":
            birthday = menu.get_friend_birthday()
            fb_user.add_friend_birthday(friend_uid, birthday)

        elif main_menu_choice == "schedule":

            birthday_message_type = menu.get_birthday_message_type()
            if birthday_message_type == 'random':
                random_birthday_message_type = \
                    menu.get_random_birthday_message_type()
                message = tools.select_random_wish(random_birthday_message_type)

            else:
                message = menu.get_drafted_birthday_message()

            fb_user.schedule_birthday_message_for_uid(friend_uid, message)
            print("Message scheduled!")

        elif main_menu_choice == 'exit':
            fb_user.save_calendar()
            fb_user.logout()


if __name__ == "__main__":
    main()
