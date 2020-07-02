import datetime


def is_same_date(datetime1, datetime2):
    dt1 = datetime1 - datetime.timedelta(microseconds=datetime1.microsecond)
    dt2 = datetime2 - datetime.timedelta(microseconds=datetime2.microsecond)
    return dt1 == dt2


def remove_microseconds(date_t):
    dt = date_t - datetime.timedelta(microseconds=date_t.microsecond)
    return dt


def remove_seconds(datetime1):
    dt1 = datetime1 - datetime.timedelta(seconds=datetime1.second)
    return dt1
