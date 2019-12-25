from fb_user import FBUser
from calendar_parser import BirthdayCalendar, HolidayCalendar
import datetime


def main():
    calendar_dir = 'fb2cal/src/birthdays.ics'
    birthday_cal = BirthdayCalendar(calendar_dir)
    name, birthday = birthday_cal.get_name_birthday_by_uid("100004947462023")
    calendar_url = "https://www.calendarlabs.com/ical-calendar/ics/39/Canada_Holidays.ics"
    holiday_cal = HolidayCalendar(calendar_url)

    user = FBUser(birthday_cal, holiday_cal)
    # user.send_message("100004947462023", "Hey this is a test")
    today = datetime.date(2020, 8, 29)
    # user.send_scheduled_message("100004947462023", "Happy birthday!", today, birthday)
    user.store_birthday_message_for_uid("100004947462023", "Be Happy")
    user.send_all_scheduled_birthday_messages(today)

if __name__== "__main__":
    main()
