def btfl_num(num):
    dict_emo = {'1' : "1️⃣",
                '2' : "2️⃣",
                '3' : "3️⃣",
                '4' : "4️⃣",
                '5' : "5️⃣",
                '6' : "6️⃣",
                '7' : "7️⃣",
                '8' : "8️⃣",
                '9' : "9️⃣",
                '0' : "0️⃣"}
    s = ""
    for i in str(num):
        s += dict_emo[i]
    return s

def keyboard_f(tb, stage: str, num: int = 1, max_num: int = 2):
    if stage == "TEACHER_CHOOSING":
        print('\nk', stage)
        keyboard = tb.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        bttn1 = tb.types.KeyboardButton('Написать отзыв')
        bttn2 = tb.types.KeyboardButton('Посмотреть отзывы')
        bttn3 = tb.types.KeyboardButton('Посмотреть статистику')
        bttn4 = tb.types.KeyboardButton('Убрать клавиатуру')
        keyboard.add(bttn1, bttn2, bttn3, bttn4)
    elif stage == "TEACHER_BUTTON":
        keyboard = tb.types.ReplyKeyboardRemove()

    elif stage == "TEACHER_LOOK":
        print('\nk', stage, '\n', max_num, num)
        keyboard = tb.types.InlineKeyboardMarkup()
        count_button = tb.types.InlineKeyboardButton(text=f"{btfl_num(num)}", callback_data="blank")
        goon_button = tb.types.InlineKeyboardButton(text="Далее",
                                                    callback_data='go_on')
        gobck_button = tb.types.InlineKeyboardButton(text="Назад",
                                                    callback_data='go_back')
        if max_num != 1:
            if num != 1:
                if max_num == num: keyboard.add(gobck_button, count_button)
                else: keyboard.add(gobck_button, count_button, goon_button)
            else: keyboard.add(count_button, goon_button)
        else: keyboard.add(count_button)
        """if num == 1: keyboard.add(count_button, goon_button)
        if max_num == 1: keyboard.add(count_button)
        elif num == max_num: keyboard.add(gobck_button, count_button)
        else: keyboard.add(gobck_button, count_button, goon_button)"""

    elif stage == "RATINGS":
        keyboard = tb.types.InlineKeyboardMarkup()
        count_button = tb.types.InlineKeyboardButton(text=f"{btfl_num(num)}", callback_data="blank")
        goon_button = tb.types.InlineKeyboardButton(text="Далее",
                                                    callback_data='go_on_/rating')
        gobck_button = tb.types.InlineKeyboardButton(text="Назад",
                                                    callback_data='go_back_/rating')
        if num == 1: keyboard.add(count_button, goon_button)
        elif len(max_num) == 1: keyboard.add(count_button)
        elif num == len(max_num): keyboard.add(gobck_button, count_button)
        else: keyboard.add(gobck_button, count_button, goon_button)
    else: print("keyboard_f else =", bool(keyboard))
    return keyboard