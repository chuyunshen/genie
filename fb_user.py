from fbchat import Client
from fbchat.models import *
from typing import List, Tuple
from fb2cal.src import fb2cal


class FBUser:
    """
    Facebook user to login and congratulate her/his friends,
    having a birthday on the login date.
    """
    _username: str
    _password: str
    client: Client

    def __init__(self, birthday_calendar, holiday_calendar) -> None:
        """ Initialize a new Facebook user with the username and
        password stored in the account_details file"""
        account_details = _read_account_details()
        self._username = account_details[0]
        self._password = account_details[1]
        self.client = _login(self)
        print("{} is logged in".format(self.client.uid))
        self.birthday_calendar = birthday_calendar
        self.holiday_calendar = [holiday_calendar]

    def send_message(self, uid, message) -> None:
        """ Send a message"""
        self.client.send(Message(text=message),
                         thread_id=uid,
                         thread_type=ThreadType.USER)

    def send_scheduled_message(self, uid, message, today, scheduled_date):
        """
        uid: str of Facebook userid
        message: str
        today: datetime.date object
        scheduled_date: arrow object
        """
        if today == scheduled_date.date():
            self.send_message(uid, message)
            print("Message to {} has been sent.".format(uid))

    def set_birthday_calendar(birthday_calendar):
        self.birthday_calendar = birthday_calendar

    def add_holiday_calendar(holiday_calendar):
        self.holiday_calendar.append(holiday_calendar)

    def delete_holiday_calendar_by_index(index):
        self.holiday_calendar.pop(index)

    def find_uid_by_name(self, name):
        for event in self.birthday_calendar.events:
            if name == event.name.split("'")[0]:
                return uid
        raise NameError

    def store_birthday_message_for_uid(self, uid, message):
        for event in self.birthday_calendar.events:
            if event.uid == uid:
                event.description = message
                return
        raise NameError

    def store_holiday_message_for_uid(self, uid):
        # need to verify the uid is valid later
        uid_exists = True
        if not uid_exists:
            raise NameError
        for event in self.holiday_calendar.events:
            event[uid] = message

    def send_all_scheduled_birthday_messages(self, today):
        for event in self.birthday_calendar.events:
            if event.description:
                self.send_scheduled_message(event.uid, event.description,
                        today, event.begin)

    def send_all_scheduled_holiday_messages(self, today):
        for event in self.holiday_calendar.events:
            if event.description:
                for uid in event.description:
                    self.send_scheduled_message(uid, event.description[uid],
                        today, event.begin)

def _read_account_details() -> List[str]:
    """ Helper method to read username and password from
    account_details.txt file and return them as a list."""
    f = open("docs/account_details.txt", "r")
    account_details = f.readlines()
    f.close()
    return account_details


def _login(self) -> Client:
    """ Helper method to login to a Facebook account using a username and
    password from account_details"""
    return Client(self._username, self._password)





