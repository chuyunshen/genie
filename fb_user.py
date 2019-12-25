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

    def set_holiday_calendar(holiday_calendar):
        self.holiday_calendar = holiday_calendar

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





