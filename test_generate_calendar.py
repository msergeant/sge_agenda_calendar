import datetime

from generate_calendar import *


def test_monday_of_week_from_monday():
    date = datetime.date(2021, 8, 30)

    assert monday_of_week(date) == date

def test_monday_of_week_from_sunday():
    monday = datetime.date(2021, 8, 30)
    date = datetime.date(2021, 8, 29)

    assert monday_of_week(date) == monday

def test_monday_of_week_from_tuesday():
    monday = datetime.date(2021, 8, 30)
    date = datetime.date(2021, 8, 31)

    assert monday_of_week(date) == monday

CONCEPT_DATA = {
    'concepts': {
        datetime.date(2021, 8, 23): 'first concept',
        datetime.date(2021, 10, 1): 'second concept',
        datetime.date(2022, 1, 1): 'third concept'
    }
}

def test_concept_of_quarter_first_day():
    first_day = datetime.date(2021, 8, 23)

    assert concept_of_quarter(first_day, CONCEPT_DATA) == 'first concept'

def test_concept_of_quarter_last_day():
    last_day = datetime.date(2021, 12, 31)

    assert concept_of_quarter(last_day, CONCEPT_DATA) == 'second concept'

def test_concept_of_quarter_middle_day():
    last_day = datetime.date(2021, 11, 5)

    assert concept_of_quarter(last_day, CONCEPT_DATA) == 'second concept'

def test_concept_of_quarter_before_time():
    too_early = datetime.date(1988, 11, 5)

    assert concept_of_quarter(too_early, CONCEPT_DATA) == None
