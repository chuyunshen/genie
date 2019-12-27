from fbchat import Client
from fbchat.models import *
from typing import List
from fb2cal.src import fb2cal
from ics import Calendar
from src.exceptions import *
import os
import configparser

TEST = True
if TEST:
    import tests.config_test as config
else:
    from src import config


class FBUser:
    """
    Facebook user to login and congratulate her/his friends,
    having a birthday on the login date.
    """
    _username: str
    _password: str
    birthday_calendar: Calendar
    client: Client

    def __init__(self) -> None:
        """ Initialize a new Facebook user with the username and
        password stored in the account_details file.

        birthday_calendar: has attributes events (a set of ics.Event). Important
        attributes of an Event include name, uid (facebook user id),
        begin (birthday, arrow format), and description (contains birthday
        message, str).
        """
        account_details = _read_account_details()
        if not account_details:
            raise AccountDetailsNotFoundException("No account detail is found.")
        self._username = account_details[0]
        self._password = account_details[1]
        self.client = _login(self)
        print("{} is logged in".format(self.client.uid))

        # update config file for fb2cal
        # config = configparser.ConfigParser()
        # config.read(config.config_dir)
        # config.set("AUTH", "fb_email", account_details[0])
        # config.set("AUTH", "fb_pass", account_details[1])
        # with open(config.config_dir, "w") as f:
        #     config.write(f)

        # if there exists a calendar, read in, otherwise, download from facebook
        if os.path.exists(config.calendar_dir):
            self.birthday_calendar = _parse_ics()
        else:
            self.download_birthday_calendar()

    def send_message(self, uid, message) -> None:
        """ Send a message"""
        self.client.send(Message(text=message),
                         thread_id=uid,
                         thread_type=ThreadType.USER)

    def send_scheduled_message(self, uid, message, today, scheduled_date):
        """
        uid: str of Facebook user id
        message: str
        today: datetime.date object
        scheduled_date: arrow object
        """
        if today == scheduled_date.date():
            self.send_message(uid, message)
            print("Message to {} has been sent.".format(uid))

    def update_birthday_calendar(self, birthday_calendar):
        """ Updates the birthday calendar by checking for duplicated events and
        the adding the new events to the existing calendar. This method also
        deletes events for people who are not in the friends list anymore.
        Regular updates of the birthday calendars ensures newly added friends'
        birthday information is added and if a friend's birthday this year
        (e.g., 2019-08-29), then a new year's date (e.g., 2020-08-29) is added.
        """
        raise NotImplementedError

    def save_calendar(self):
        """ Save the updated birthday calendar to calendar_dir.
        """
        with open(config.calendar_dir, 'w') as f:
            f.writelines(self.birthday_calendar)

    def get_uid_by_name(self, name):
        """ Finds a Facebook friend's uid by name. If the name does not exist,
        NameError is raised.
        """
        for event in self.birthday_calendar.events:
            if name == event.name.split("'")[0]:
                return event.uid
        raise NameError

    def schedule_birthday_message_for_uid(self, uid, message):
        """Schedules a birthday message for Facebook friend with the given uid.
        """
        for event in self.birthday_calendar.events:
            if event.uid == uid:
                event.description = message
                return
        raise NameError

    def send_all_scheduled_birthday_messages(self, today):
        """Checks and sends all scheduled birthday messages."""
        for event in self.birthday_calendar.events:
            if event.description:
                self.send_scheduled_message(event.uid, event.description,
                                            today, event.begin)

    def get_friend_dict(self):
        """ Gets a dictionary of friends mapping from their uid to their name.
        """
        raise NotImplementedError

    def download_birthday_calendar(self):
        """ Gets/updates birthday calendar from Facebook and saves the calendar at
        "fb2cal/src/calendar.ics".
        """
        fb2cal.main2()
        # dont do this too often or else the account will be banned

    def get_birthday_by_uid(self, uid):
        """ Returns the birthday of a specific uid, as an arrow object
        """
        for event in self.birthday_calendar.events:
            if event.uid == uid:
                return event.begin


def _read_account_details() -> List[str]:
    """ Helper method to read username and password from
    account_details.txt file and return them as a list."""
    f = open(config.account_details_path, "r")
    account_details = f.read().splitlines()
    f.close()
    return account_details


def _login(self) -> Client:
    """ Helper method to login to a Facebook account using a username and
    password from account_details"""
    return Client(self._username, self._password)


def _parse_ics():
    """ Parse a calendar from ics format"""
    g = open(config.calendar_dir, 'rb')
    cal = Calendar(g.read().decode())
    for event in cal.events:
        event.description = None
    g.close()
    return cal
