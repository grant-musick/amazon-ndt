from __future__ import division, absolute_import, print_function, unicode_literals

import datetime as dt
import calendar
import re

# AMAZON.DATE
# AMAZON.DURATION
# AMAZON.FOUR_DIGIT_NUMBER
# AMAZON.NUMBER
# AMAZON.TIME

DAY_PATTERN = 'DAY_PATTERN'
WEEK_PATTERN = 'WEEK_PATTERN'
WEEKEND_PATTERN = 'WEEKEND_PATTERN'
MONTH_PATTERN = 'MONTH_PATTERN'
YEAR_PATTERN = 'YEAR_PATTERN'
DECADE_PATTERN = 'DECADE_PATTERN'
SEASON_PATTERN = 'SEASON_PATTERN'
NOW_PATTERN = 'NOW_PATTERN'



# month/day to month/day non-inclusive
SEASON_MD_VALUES = {
    'SP': ((3,1),(6,1)),
    'SU': ((6,1),(9,1)),
    'FA': ((9,1),(12,1)),
    'WI': ((12,1), (3,1))
}

def _generate_day_pattern_values(amazon_date_str):
    start = dt.datetime.strptime(amazon_date_str, '%Y-%m-%d')
    duration = dt.timedelta(hours=24)
    return start, duration

def _generate_month_pattern_values(amazon_date_str):
    start = dt.datetime.strptime(amazon_date_str, '%Y-%m')
    first_day, num_days = calendar.monthrange(start.year, start.month)
    duration = dt.timedelta(days=num_days)
    return start, duration

def _generate_year_pattern_values(amazon_date_str):
    start = dt.datetime.strptime(amazon_date_str, '%Y')
    if calendar.isleap(start.year):
        num_days = 366
    else:
        num_days = 365
    duration = dt.timedelta(days=num_days)
    return start, duration

# NOTE: start days for weeks and weekends seem to be highly situational
# will take a while to coordinate AMAZON times with expected behavior
# For now weeks start on Monday i.e. -1
# and weekends start on Saturday i.e. -6
def _generate_week_pattern_values(amazon_date_str):
    start = dt.datetime.strptime(amazon_date_str + "-1", '%Y-W%U-%w')
    duration = dt.timedelta(days=7)
    return start, duration

def _generate_weekend_pattern_values(amazon_date_str):
    start = dt.datetime.strptime(amazon_date_str + "-6", '%Y-W%U-WE-%w')
    duration = dt.timedelta(days=2)
    return start, duration

def _generate_decade_pattern_values(amazon_date_str):
    new_date_str = amazon_date_str.replace("X","0")
    start = dt.datetime(year=int(new_date_str), month=1, day=1)
    duration = _calculate_decade_duration(start)
    return start, duration

def _generate_season_pattern_values(amazon_date_str):
    year, season = amazon_date_str.split("-")
    month, day = SEASON_MD_VALUES[season][0]
    start = dt.datetime(year=int(year), month=month, day=day)
    duration = _calculate_season_length(season, start)
    return start, duration

def _generate_now_pattern_values(amazon_date_str):
    now = dt.datetime.now()
    start = dt.datetime(year=now.year, month=now.month, day=now.day)
    duration = dt.timedelta(hours=24)
    return start, duration


PATTERNS = {
    DAY_PATTERN: (re.compile('^\d{4}-\d{2}-\d{2}$'), _generate_day_pattern_values),
    WEEK_PATTERN: (re.compile('^\d{4}-W\d{2}$'), _generate_week_pattern_values),
    WEEKEND_PATTERN: (re.compile('^\d{4}-W\d{2}-WE$'), _generate_weekend_pattern_values), 
    MONTH_PATTERN:  (re.compile('^\d{4}-\d{2}$'), _generate_month_pattern_values),
    YEAR_PATTERN: (re.compile('^\d{4}$'), _generate_year_pattern_values),
    DECADE_PATTERN: (re.compile('^\d{3}X$'), _generate_decade_pattern_values),
    SEASON_PATTERN: (re.compile('(^\d{4})-(WI|SP|SU|FA)$'), _generate_season_pattern_values),
    NOW_PATTERN: (re.compile('^PRESENT_REF$'), _generate_now_pattern_values)
}


def _calculate_decade_duration(decade_start):
    # assumes decade start is multiple of 10, e.g. 2010, 2020, etc
    start = decade_start
    leap_years = [x for x in range(start.year, start.year+10) if calendar.isleap(x)]
    num_leap_years = len(leap_years)
    num_reg_years = 10-num_leap_years
    duration = dt.timedelta(num_leap_years*366 + num_reg_years*365)
    return duration

def _calculate_season_length(season, start):
    if season == 'WI':
        year = start.year + 1
    else:
        year = start.year
    month, day = SEASON_MD_VALUES[season][1]
    end = dt.datetime(year=year, month=month, day=day)
    return end - start


def _get_start_duration_tuple(amazon_date_str):
    for key in PATTERNS:
        pattern, generate_func = PATTERNS[key]
        match_obj = pattern.match(amazon_date_str)
        if match_obj:
            return generate_func(amazon_date_str)

    raise ValueError("Unable to parse AMAZON.DATE {}".format(amazon_date_str))


class AmazonDate(object):
    def __init__(self, date_str):
        self._date_str = date_str
        start, duration = _get_start_duration_tuple(date_str)
        self._start = start
        self._duration = duration

    @property
    def start(self):
        return self._start

    @property
    def duration(self):
        return self._duration

    @property
    def amazon_date_str(self):
        return self._date_str




class AmazonDuration(object):

    PATTERN = re.compile("^P(\d+Y)?(\d+M)?(\d+W)?(\d+D)?T?(\d+H)?(\d+M)?(\d+S)?$")

    def __parse_helper(self, duration_str):
        try:
            match = AmazonDuration.PATTERN.match(duration_str)
            (   self.years, self.months, self.weeks, self.days, 
                self.hours, self.minutes, self.seconds) = [int(x[:-1]) for x in match.groups("0Z")]

        except:
            raise ValueError("Unable to parse: {}".format(duration_str))


    def __init__(self, duration_str):
        self._duration_str = duration_str
        self.__parse_helper(duration_str)


    def timedelta_from(self, start_time=None):
        if start_time is None:
            start_time = dt.datetime.now()

        base_timedelta = dt.timedelta(
            weeks=self.weeks, days=self.days, hours=self.hours,
            minutes=self.minutes, seconds=self.seconds
            )

        variable_delta = dt.timedelta()
        if self.is_variable:
            current_month = start_time.month
            current_year = start_time.year
            target_month = (current_month + self.months) % 12
            target_year = current_year + self.years
            variable_delta =    (dt.datetime(year=target_year, month=target_month, day=1) -
                                dt.datetime(year=current_year, month=current_month, day=1))

        return base_timedelta + variable_delta


    @property
    def is_variable(self):
        return self.years > 0 or self.months > 0

    @property
    def timedelta(self):
        return self.timedelta_from()

    @property
    def amazon_duration_str(self):
        return self._duration_str




# TODO: ACTUALLY IMPLEMENT THESE

class AmazonFourDigitNumber(object):
    def __init__(self, fdn_str):
        self._fdn_str = fdn_str
        self._fdn = None


class AmazonNumber(object):
    def __init__(self, number_str):
        self._number_str = number_str
        self._number = None


class AmazonTime(object):
    def __init__(self, time_str):
        self._time_str = time_str
        self._time = None
