import os
import pytest
import datetime
import tools
from fb_user import get_birthday_by_uid
import arrow


@pytest.fixture(scope="module")
def setup():
    user = tools.set_up_fbuser()
    name = "Natalia Moran"
    message = "happy bday"
    return user, name, message


def test_send_messages(setup):
    # Arrange
    user, name, message = setup
    print(user.get_friend_dict())
    uid = user.get_uid_by_name(name)
    birthday = get_birthday_by_uid(uid, user.birthday_calendar)
    today = datetime.date(2020, 1, 21)

    # Act
    user.schedule_birthday_message_for_uid(uid, message)
    user.save_calendar()
    user.send_all_scheduled_birthday_messages(today)

    # Assert
    assert birthday.date() == today


def test_get_uid_by_name(setup):
    # Arrange
    user, name, message = setup

    # Assert
    assert '1104705831' == user.get_uid_by_name(name)
    with pytest.raises(Exception) as e_info:
        user.get_uid_by_name('test_name')


def test_set_birthday_by_uid(setup):
    # Arrange
    user, name, message = setup
    birthday = datetime.date(2020, 1, 1)

    # Act
    user.set_birthday_by_uid('1104705831', birthday)

    # Assert
    assert arrow.get(birthday) == get_birthday_by_uid('1104705831',
                                                      user.birthday_calendar)


def test_update_birthday_calendar(setup):
    # Arrange
    user, name, message = setup

    # Act
    user.update_birthday_calendar()


def test_logout(setup):
    # Arrange
    user, name, message = setup

    # Act
    user.logout()


if __name__ == "__main__":
    print(f'Running tests from {os.getcwd()}')
    pytest.main(args=['-s', 'src/test/test_fbuser.py'])
