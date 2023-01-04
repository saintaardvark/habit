import pytest
from server.habit import get_streak_for_single_habit

from server.habit import get_streak_for_single_habit


def test_get_streak_for_single_habit_zero_length():
    """
    Degenerate case:  we haven't logged *any* habits, so the count should be zero.
    """
    test_data = []
    today = 1
    assert get_streak_for_single_habit(test_data, today=today) == 0


def test_get_streak_for_single_habit_single_day_including_today():
    """
    We just started doing a habit today.  The count should be one.
    """
    test_data = [1]
    today = 1
    assert get_streak_for_single_habit(test_data, today=today) == 1


def test_get_streak_for_single_habit_single_day_but_not_today():
    """
    We just started doing a habit yesterday.  We have not logged today.
    The count should be the length of the array.
    """
    test_data = [1]
    today = 2
    assert get_streak_for_single_habit(test_data, today=today) == 1


def test_get_streak_for_single_habit_single_day_sad_case():
    """
    We started doing a habit some time ago, but haven't kept up.
    """
    test_data = [1]
    today = 7
    assert get_streak_for_single_habit(test_data, today=today) == 0


def test_get_streak_for_multiple_days_including_today_happy_case():
    """
    We have been doing a habit for multiple days.  We just logged today.
    The count should be the length of the array.
    """
    test_data = [5, 4, 3, 2, 1]
    today = 5
    assert get_streak_for_single_habit(test_data, today=today) == 5


def test_get_streak_for_multiple_days_but_not_today_happy_case():
    """
    We have been doing a habit for multiple days.  We have not logged today.
    The count should be the length of the array.
    """
    test_data = [5, 4, 3, 2, 1]
    today = 6
    assert get_streak_for_single_habit(test_data, today=today) == 5


def test_get_streak_for_multiple_days_sad_case():
    """
    We started doing a habit some time ago.  We had a good streak going
    but lost it.
    """
    test_data = [3, 2, 1]
    today = 7
    assert get_streak_for_single_habit(test_data, today=today) == 0

def test_get_streak_for_multiple_days_including_today_some_gaps():
    """
    We have some gaps in our record.
    """
    test_data = [10, 9, 8, 3, 2, 1]
    today = 10
    assert get_streak_for_single_habit(test_data, today=today) == 3

def test_get_streak_for_multiple_days_but_nottoday_some_gaps():
    """
    We have some gaps in our record.
    """
    test_data = [10, 9, 8, 3, 2, 1]
    today = 11
    assert get_streak_for_single_habit(test_data, today=today) == 3
