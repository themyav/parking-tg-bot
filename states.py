from enum import IntEnum

class State(IntEnum):
    SELECT_ACTION = 0
    GET_START_DATE = 1
    GET_END_DATE = 2
    SELECT_PARKING = 3
    CONFIRM_BOOKING = 4
    INPUT_CAR_NUMBER = 5
    VIEW_BOOKINGS = 6
    SELECT_BOOKING_TO_PROLONG = 7
    PROLONG_BOOKING = 8