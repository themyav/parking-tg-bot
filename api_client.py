import requests


class APIClient:
    @staticmethod
    async def get_user_by_phone_number(phone_number: str):
        # response = requests.get(f"http://api.example.com/users?phone={phone_number}")
        # return response.json()

        return {"id": "user123", "phone": phone_number, "user_type": "premium"}

    @staticmethod
    async def get_available_parkings_for_id(user_id, start_time, end_time):
        return [
            {"id": "A1", "cost_per_day": 500, "cost_per_hour": 50},
            {"id": "B2", "cost_per_day": 700, "cost_per_hour": 70},
            {"id": "C3", "cost_per_day": 300, "cost_per_hour": 30}
        ]

    @staticmethod
    async def book_place(user_id, place_id, start_time, end_time, car_number):
        return 200

    @staticmethod
    async def get_bookings_for_user_id(user_id):
        return [
            {"booking_id": "1", "start_time": "2023-12-01T10:00", "end_time": "2023-12-05T18:00",
             "car_number": "А123БВ777"},
            {"booking_id": "2", "start_time": "2023-12-10T09:00", "end_time": "2023-12-12T17:00",
             "car_number": "А123БВ777"}
        ]

    @staticmethod
    async def prolongate_booking(booking_id, new_finish_time):
        return 200
