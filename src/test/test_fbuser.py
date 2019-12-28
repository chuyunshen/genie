import os

import pytest
import datetime
import tools
from src.fb_user import get_birthday_by_uid


# Haven't figured out how to log in only once. With pytest.fixture, the program
# still logs in multiple times


@pytest.fixture(autouse=True)
def setup():
    user = tools.set_up_fbuser()
    name = "Chuyun Shen"
    message = "happy bday"
    return user, name, message


# def test_send_messages(setup):
#    user, name, message = setup
#    print(user.get_friend_dict())
#    uid = user.get_uid_by_name(name)
#    birthday = get_birthday_by_uid(uid, user.birthday_calendar)
#    today = datetime.date(2020, 8, 29)
#    assert birthday.date() == today
#    user.schedule_birthday_message_for_uid(uid, message)
#    # user.save_calendar()
#    user.send_all_scheduled_birthday_messages(today)
#
#
# def test_get_uid_by_name(setup):
#    user, name, message = setup
#    assert '100004947462023' == user.get_uid_by_name(name)
#    with pytest.raises(Exception) as e_info:
#        user.get_uid_by_name('kukunla')


def test_set_birthday_by_uid(setup):
    user, name, message = setup
    birthday = datetime.date(2020, 1, 1)
    user.set_birthday_by_uid('100004947462023', birthday)
    assert birthday == get_birthday_by_uid('100004947462023',
                                           user.birthday_calendar)


def test_update_birthday_calendar(setup):
    user, name, message = setup
    user.update_birthday_calendar()


if __name__ == "__main__":
    print(f'Running tests from {os.getcwd()}')
    pytest.main(args=['-s', 'src/test/test_fbuser.py'])
