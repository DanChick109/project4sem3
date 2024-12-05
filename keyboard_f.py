def keyboard_f(tb, stage: str):
    if stage == "TEACHER_CHOOSING":
        keyboard = tb.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        bttn1 = tb.types.KeyboardButton('Написать отзыв')
        bttn2 = tb.types.KeyboardButton('Посмотреть отзывы')
        bttn3 = tb.types.KeyboardButton('Посмотреть статистику')
        bttn4 = tb.types.KeyboardButton('Назад')
        keyboard.add(bttn1, bttn2, bttn3, bttn4)
        return keyboard
    if stage == "TEACHER_BUTTON":
        keyboard = tb.types.ReplyKeyboardRemove()
        return keyboard
    if stage == "TEACHER_LOOK":
        keyboard = tb.types.InlineKeyboardMarkup()
        button_save = tb.types.InlineKeyboardButton(text="Далее",
                                                    callback_data='go_on')
        button_change = tb.types.InlineKeyboardButton(text="Назад",
                                                    callback_data='go_back')
        keyboard.add(button_save, button_change)
        return keyboard