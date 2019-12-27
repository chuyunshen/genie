import os

import pytest
import datetime
import tools


def test_fb_user():
    user = tools.set_up_fbuser()
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
    pytest.main(['src/test/test_fbuser.py'])
