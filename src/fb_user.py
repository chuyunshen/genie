from datetime import datetime, timedelta
from arrow import Arrow
from fbchat import Client
from fbchat.models import *
from typing import Dict, List
from fb2cal.src import fb2cal
from ics import Calendar, Event
from settings import *
from dateutil.relativedelta import relativedelta
from ics.grammar.parse import ContentLine
import random
import tools


class FBUser:
    """
    Facebook user to login and congratulate her/his friends,
    having a birthday on the login date.
    """
    _username: str
    _password: str
    birthday_calendar: Calendar
    client: Client

    def __init__(self, username: str, password: str, cal: Calendar) -> None:
        """ Initialize a new Facebook user with the username and
        password stored in the account_details file.

        birthday_calendar: has attributes events (a set of ics.Event). Important
        attributes of an Event include name, uid (facebook user id),
        begin (birthday, arrow format), and description (contains birthday
        message, str).
        """
        self._username = username
        self._password = password
        self.birthday_calendar = cal
        self.client = _login(self)
        print("{} is logged in".format(self.client.uid))

    def get_client(self) -> Client:
        return self.client

    def get_uid_by_name(self, name) -> str:
        """ Finds a Facebook friend's uid by name. If the name does not exist
        in the friend list, NameError is raised.
        """
        friends = self.get_friend_dict()
        for uid in friends:
            if name == friends[uid][0]:
                return uid
        raise NameError

    def get_friend_dict(self) -> Dict:
        """ Gets a dictionary of friends mapping from their uid to their name.
        """
        friend_dict = {}
        user_list = [user for user in self.client.fetchAllUsers() if
                     user.is_friend]

        for user in user_list:
            friend_dict[user.uid] = [user.name, user.url, user.photo]
        return friend_dict

    def send_message(self, uid, message) -> None:
        """ Send a message"""
        self.client.send(Message(text=message),
                         thread_id=uid,
                         thread_type=ThreadType.USER)

    def send_scheduled_message(self, uid, message, today,
                               scheduled_date) -> None:
        """
        uid: str of Facebook user id
        message: str
        today: datetime.date object
        scheduled_date: arrow object
        """
        if today == scheduled_date.date():
            self.send_message(uid, message)
            print("Message to {} has been sent.".format(uid))

    def send_all_scheduled_birthday_messages(self, today) -> None:
        """Checks and sends all scheduled birthday messages."""
        for event in self.birthday_calendar.events:
            if event.description:
                self.send_scheduled_message(event.uid, event.description,
                                            today, event.begin)

    def update_birthday_calendar(self) -> None:
        """ Updates the birthday calendar by checking for duplicated events and
        the adding the new events to the existing calendar. This method also
        deletes events for people who are not in the Facebook/Messenger
        friends list anymore.
        Regular updates of the birthday calendars ensures newly added friends'
        birthday information is added and if a friend's birthday this year
        (e.g., 2019-08-29) has passed, then that birthday event's begin
        attribute is updated to a new year's date (e.g., 2020-08-29), with the
        previously saved birthday message under attribute description removed
        (set to None).
        """
        self.download_birthday_calendar()
        new_cal = tools.parse_ics()
        all_old_uids = [event.uid for event in self.birthday_calendar.events]
        all_new_uids = [event.uid for event in new_cal.events]

        # events in the new calendar but not in the original calendar:
        for event in new_cal.events:
            if event.uid in all_old_uids:
                # if they have changed their birthdays or this year's birthday
                # has already passed--update to next year's
                updated_birthday = get_birthday_by_uid(event.uid, new_cal)
                if event.begin != updated_birthday:
                    event.begin = updated_birthday
            else:
                self.birthday_calendar.events.add(event)

        # events in the original calendar but not in the new calendar
        for event in self.birthday_calendar.events:
            if event.uid not in all_new_uids:
                # check if there is deleted friends and if they are still in
                # the friends list
                if event.uid not in self.get_friend_dict():
                    self.birthday_calendar.events.remove(event)

    def set_birthday_by_uid(self, uid, birthday) -> None:
        """Set the birthday for a friend by uid.
        Args:
            uid: str
            birthday: datetime
        """
        # Initialize birthday_event to a new event
        birthday_event = Event()
        # If the uid exists in the current birthday_calendar, we will delete
        # the old event.
        uid_exists = False
        for event in self.birthday_calendar.events:
            if event.uid == uid:
                birthday_event = event
                uid_exists = True
        if uid_exists:
            self.birthday_calendar.events.remove(birthday_event)
        birthday_event.uid = uid
        birthday_event.name = "{}'s Birthday".format(
            self.get_friend_dict()[uid][0])

        today = datetime.today()
        # Calculate the year as this year or next year based on if its past
        # current month or not
        # Also pad day, month with leading zeros to 2dp
        year = today.year if birthday.month >= today.month else (
                today + relativedelta(years=1)).year
        month = '{:02d}'.format(birthday.month)
        day = '{:02d}'.format(birthday.day)
        birthday_event.begin = f'{year}-{month}-{day} 00:00:00'
        birthday_event.make_all_day()
        birthday_event.duration = timedelta(days=1)
        birthday_event.extra.append(
            ContentLine(name='RRULE', value='FREQ=YEARLY'))
        self.birthday_calendar.events.add(birthday_event)

    def save_calendar(self) -> None:
        """ Save the updated birthday calendar to calendar_dir.
        """
        with open(config.calendar_dir, 'w') as f:
            f.writelines(self.birthday_calendar)

    def schedule_birthday_message_for_uid(self, uid, message) -> None:
        """Schedules a birthday message for Facebook friend with the given uid.
        """
        for event in self.birthday_calendar.events:
            if event.uid == uid:
                event.description = message
                return
        raise NameError

    def download_birthday_calendar(self) -> None:
        """ Gets/updates birthday calendar from Facebook and saves the calendar at
        "fb2cal/src/calendar.ics".
        """
        fb2cal.main2()
        # dont do this too often or else the account will be banned

    def select_random_wish(self, wish_type) -> str:
        """Returns a random birthday wish."""
        wishes = read_wishes(wish_type)
        return random.choice(wishes)

    def logout(self) -> None:
        """ Helper method to logout from a Facebook account"""
        self.client.logout()
        print("User is logged out")


def _login(self) -> Client:
    """ Helper method to login to a Facebook account using a username and
    password from account_details"""
    return Client(self._username, self._password)


def get_birthday_by_uid(uid, birthday_calendar) -> Arrow:
    """ Returns the birthday of a specific uid, as an arrow object
    """
    for event in birthday_calendar.events:
        if event.uid == uid:
            return event.begin


def read_wishes(wish_type) -> List[str]:
    """"Reads in birthday wishes. If wish_type is 'funny', funny birthday
    wishes are read in, otherwise, serious birthday wishes are read in."""
    if wish_type == 'funny':
        f = open(config.funny_birthday_wish_path, "r")
    else:
        f = open(config.serious_birthday_wish_path, "r")
    wishes = f.read().splitlines()
    f.close()
    return wishes
