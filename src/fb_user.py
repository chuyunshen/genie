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
import tools
from os import path
import exceptions


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
        print(f"{self.client.uid} is logged in")

    def get_client(self) -> Client:
        return self.client

    def get_uid_by_name(self, name) -> List[str]:
        """ Finds a Facebook friend's uid by name. If the name does not exist
        in the friend list, NameError is raised. Returns a list of uids.
        """
        uids = []
        friends = self.get_friend_dict()
        for uid in friends:
            if name == friends[uid][0]:
                uids.append(uid)
        if uids:
            return uids
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

    def send_scheduled_message(self, event) -> None:
        """ Send a scheduled birthday message and update the birthday's date
        to the next year's birthday."""
        self.send_message(event.uid, event.description)
        event.begin = event.begin.shift(years=1)
        print("Message to {} has been sent.".format(event.uid))
        print("Birthday date is updated to {}.".format(event.begin))

    def send_all_scheduled_birthday_messages(self, today) -> None:
        """Checks and sends all scheduled birthday messages."""
        for event in self.birthday_calendar.events:
            if event.description and today == event.begin.date():
                self.send_scheduled_message(event)

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
        tools.download_birthday_calendar()
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

    # TODO Remove this method
    # def set_birthday_by_uid(self, uid, birthday) -> None:
    #     """Set the birthday for a friend by uid.
    #     Args:
    #         uid: str
    #         birthday: datetime
    #     """
    #     # If the uid exists in the current birthday_calendar, we will delete
    #     # the old event.
    #     self.delete_birthday_by_uid(uid)
    #     # Initialize birthday_event to a new event
    #     birthday_event = Event()
    #     birthday_event.uid = uid
    #     birthday_event.name = "{}'s Birthday".format(
    #         self.get_friend_dict()[uid][0])
    #
    #     today = datetime.today()
    #     # Calculate the year as this year or next year based on if its past
    #     # current month or not
    #     year = today.year if birthday.month >= today.month else (
    #             today + relativedelta(years=1)).year
    #     # Pad day, month with leading zeros to 2dp
    #     month = '{:02d}'.format(birthday.month)
    #     day = '{:02d}'.format(birthday.day)
    #     birthday_event.begin = f'{year}-{month}-{day} 00:00:00'
    #     birthday_event.make_all_day()
    #     birthday_event.duration = timedelta(days=1)
    #     birthday_event.extra.append(
    #         ContentLine(name='RRULE', value='FREQ=YEARLY'))
    #     self.birthday_calendar.events.add(birthday_event)

    def add_friend_birthday(self, uid: int, birthday_date: datetime) -> None:
        """
        Add a new friend and her/his birthday to the birthday calendar.
        :param uid:             Friend's FB UID
        :param birthday_date:   Friend's birthday date
        :return:                None
        """
        # find the friend's name per UID
        # if the UID is not in the FB friends list, raise an exception
        name = self.get_friend_dict()[uid][0]
        if not name:
            raise exceptions.FriendNotFoundException
        # add a new event to the birthdays calendar
        self.birthday_calendar = add_event_to_calendar(self.birthday_calendar,
                                                       uid,
                                                       name,
                                                       birthday_date)

    def delete_birthday_by_uid(self, uid) -> None:
        """Delete a birthday event by uid."""
        uid_exists = False
        for event in self.birthday_calendar.events:
            if event.uid == uid:
                birthday_event = event
                uid_exists = True
        if uid_exists:
            self.birthday_calendar.events.remove(birthday_event)

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


def add_event_to_calendar(cal: Calendar, uid: int,
                          name: str, birthday_date: datetime) -> Calendar:
    """
    Method to add a new birthday event to the calendar.
    :param cal:             Calendar to be updated
    :param uid:             Friend's FB UID
    :param name:            Friend's FB name
    :param birthday_date:   Friend's birthday date
    :return:                Calendar
    """
    # Initialize birthday_event to a new event
    birthday_event = Event()
    birthday_event.uid = uid
    birthday_event.name = f"{name}'s Birthday"
    today = datetime.today()
    # Calculate the year as this year or next year based on if its past
    # current month or not
    year = today.year if birthday_date.month >= today.month else (
            today + relativedelta(years=1)).year
    # Pad day, month with leading zeros to 2dp
    month = '{:02d}'.format(birthday_date.month)
    day = '{:02d}'.format(birthday_date.day)
    birthday_event.begin = f'{year}-{month}-{day} 00:00:00'
    birthday_event.make_all_day()
    birthday_event.duration = timedelta(days=1)
    birthday_event.extra.append(
        ContentLine(name='RRULE', value='FREQ=YEARLY'))
    cal.events.add(birthday_event)
    return cal
