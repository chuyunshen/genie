import os

from src.fb_user import FBUser
import pytest
import datetime


def test_fb_user():
    user = FBUser()
    name = "Chuyun Shen"
    uid = user.get_uid_by_name(name)
    birthday = user.get_birthday_by_uid(uid)
    today = datetime.date(2020, 8, 29)
    assert birthday.date() == today
    message = "happy bday"
    user.schedule_birthday_message_for_uid(uid, message)
    # user.save_calendar()
    user.send_all_scheduled_birthday_messages(today)


if __name__ == "__main__":
    print(f'Running tests from {os.getcwd()}')
    pytest.main(['src/tests/test_fbuser.py'])
