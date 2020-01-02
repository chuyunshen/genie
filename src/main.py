from fb_user import set_up_fbuser, save_cal_and_logout
from datetime import datetime
from menu import *
from switch import Switch

"""
This file is the entry point for the program
"""


def main() -> None:
    """Create an instance of FBUser,
    present menu to this user and interact with her/him.
    Send scheduled birthday messages and save the updated calendar on exit.
    :return: None
    """
    fb_user = set_up_fbuser()
    menu = Menu(fb_user.get_friend_dict())
    while True:
        main_menu_choice = menu.get_main_menu_choice()
        friend_uid = menu.get_friend_uid(fb_user)
        with Switch(main_menu_choice) as case:
            if case("edit"):
                birthday = menu.get_friend_birthday()
                fb_user.add_friend_birthday(friend_uid, datetime(birthday))
            if case("schedule"):
                message = menu.get_birthday_message()
                fb_user.schedule_birthday_message_for_uid(friend_uid, message)
            if case("exit"):
                save_cal_and_logout(fb_user)


if __name__ == "__main__":
    main()
