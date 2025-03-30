# main.py (updated)
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from handlers.contact import ContactHandler
from handlers.booking import BookingHandler
from handlers.view_bookings import ViewBookingsHandler
from handlers.prolongation import ProlongationHandler
from handlers.base import BaseHandler
from states import State
from config import TOKEN


def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', ContactHandler.start_command),
            MessageHandler(filters.CONTACT, ContactHandler.handle_contact)
        ],
        states={
            State.SELECT_ACTION.value: [
                MessageHandler(filters.Regex('^(Узнать свободные места)$'), BookingHandler.handle_main_menu),
                MessageHandler(filters.Regex('^(Мои бронирования)$'), ViewBookingsHandler.handle_view_bookings),
                MessageHandler(filters.Regex('^(Продлить бронирование)$'), ProlongationHandler.handle_prolong_menu)
            ],
            State.GET_START_DATE.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BookingHandler.handle_start_date_input)
            ],
            State.GET_END_DATE.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BookingHandler.handle_end_date_input)
            ],
            State.SELECT_PARKING.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BookingHandler.handle_parking_selection)
            ],
            State.CONFIRM_BOOKING.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BookingHandler.handle_booking_confirmation)
            ],
            State.INPUT_CAR_NUMBER.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, BookingHandler.handle_car_number_input)
            ],
            State.VIEW_BOOKINGS.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ViewBookingsHandler.handle_view_bookings)
            ],
            State.SELECT_BOOKING_TO_PROLONG.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ProlongationHandler.handle_booking_selection)
            ],
            State.PROLONG_BOOKING.value: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ProlongationHandler.handle_new_end_time)
            ]
        },
        fallbacks=[
            MessageHandler(filters.Regex('^Выйти$'), BaseHandler.error_handler),
            MessageHandler(filters.ALL, BaseHandler.error_handler)
        ],
        allow_reentry=True
    )

    app.add_handler(conv_handler)
    app.add_error_handler(BaseHandler.error_handler)

    print('Бот запущен...')
    app.run_polling()


if __name__ == '__main__':
    main()
