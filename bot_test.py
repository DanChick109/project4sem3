import telebot as tb
import psycopg2
from keyboard_f import keyboard_f
from rating import get_ratings_ofone, get_ratings_ofall
from config import TOKEN
from output import output

bot = tb.TeleBot(TOKEN)
conn = psycopg2.connect(database="postgres",
                        user="postgres",
                        password="postgres",)
cursor = conn.cursor()
num = 0
t_name = ""
count = 0

bot.send_message(chat_id=1346307992, text=f"Бот перезапущен")

@bot.message_handler(commands=["start"])   ### Готов
def welcome(message) -> None:
    global stage
    stage = "START"   
    print(20*"#", stage, 20*"#") #
    users = set([message.chat.first_name, message.chat.last_name, message.chat.username, message.chat.id])
    with open("data_users.txt", mode="r+") as f:
        s = str([i for i in f.readlines()])
        if not(str(users) in s):
            f.write(f"{users}\n")
    bot.send_message(message.chat.id,
                           "Добро пожаловать в бота с рейтингом преподавателей. "
                           "Для вывода всех команд используйте команду '/help'.", 
                    reply_markup=keyboard_f(tb, stage="TEACHER_BUTTON"))

@bot.message_handler(commands=['ratings'])   ### Готов
def all_rating(message) -> None:
    global stage, num
    stage = "RATINGS"
    num = 1
    print(20*"#", stage, 20*"#") #
    cursor.execute(f"SELECT * FROM ratings")
    rates = list(cursor.fetchall())
    if rates: bot.send_message(message.chat.id, 
                            text=output(num=num, ratings=rates, stage=stage),
                            reply_markup=keyboard_f(tb, num=num, max_num=len(rates), stage=stage))


@bot.message_handler(commands=['list'])   ### Готов
def list_of_t(message) -> None:
    global stage
    stage = "LIST"   
    print(20*"#", stage, 20*"#") #
    mmsg_txt, s = message.text[6:], ""
    kafs = []
    if len(mmsg_txt) < 6:
        for i in range(1, 8+1):
            cursor.execute(f"SELECT kaf_name FROM kafedra WHERE split_part(kaf_name, ' ', {i}) = '({mmsg_txt})'")
            if kafs_i := [j[0] for j in list(cursor.fetchall())]: kafs = kafs_i
    if len(mmsg_txt) > 6:
        cursor.execute(f"SELECT kaf_name FROM kafedra WHERE kaf_name = '{mmsg_txt}'")
        kafs = [i[0] for i in list(cursor.fetchall())]
    if kafs:
        cursor.execute("SELECT t_name FROM teachers WHERE kaf_name=%s", (kafs[0],))
        teachs = [i[0] for i in list(cursor.fetchall())]
        for i in teachs:
            s += i + '\n'
        bot.send_message(message.chat.id, f"Преподаватели кафедры '{kafs[0]}':\n\n{s}",
                        reply_markup=keyboard_f(tb, stage="TEACHER_BUTTON"))
    else: bot.send_message(message.chat.id, f"Такой кафедры не существует",
                        reply_markup=keyboard_f(tb, stage="TEACHER_BUTTON"))

@bot.message_handler(commands=['name'])   ### Готов
def list_of_k(message) -> None:
    bot.send_message(message.chat.id, f"{message.chat.first_name} {message.chat.last_name} {message.chat.username} - {message.chat.id}",
                     reply_markup=keyboard_f(tb, stage="TEACHER_BUTTON"))

@bot.message_handler(commands=['chair'])   ### Готов
def list_of_k(message) -> None:
    global stage
    stage = "KAFEDRA"   
    print(20*"#", stage, 20*"#") #
    s_f, s_k = "", ""
    cursor.execute("SELECT fak_name FROM fakultet")
    faks = list(cursor.fetchall())
    for i in faks:
        s_f += i[0] + ":\n"
        cursor.execute(f"SELECT kaf_name FROM kafedra WHERE fak_name='{i[0]}'")
        kafs = list(cursor.fetchall())
        for j in kafs:
            s_f += "    • " + j[0] + "\n"
        s_f += "\n"
    bot.send_message(message.chat.id, f"Кафедры МТУСИ:\n\n{s_f}",
                     reply_markup=keyboard_f(tb, stage="TEACHER_BUTTON"))

@bot.message_handler(commands=['faculty'])   ### Готов
def list_of_f(message) -> None:
    global stage
    stage = "FAKULTET"   
    print(20*"#", stage, 20*"#") #
    s = ""
    cursor.execute("SELECT * FROM fakultet")
    faks = list(cursor.fetchall())
    for i in faks:
        s += i[1] + '\n'
    bot.send_message(message.chat.id, f"Факультеты МТУСИ:\n\n{s}", 
                    reply_markup=keyboard_f(tb, stage="TEACHER_BUTTON"))

@bot.message_handler(commands=['help'])
def help(message) -> None:
    global stage
    stage = "HELP"   
    print(20*"#", stage, 20*"#") #
    bot.send_message(message.chat.id,
                            "'/start' для вывода начального сообщения.\n"
                            "'/help' для вывода всех доступных команд.\n"
                            "'/teacher Имя' для выбора преподавателя (Можно ввести как ФИ, так и ИО, или полное ФИО).\n"
                            "'/list Кафедра' для вывода всех преподавателей из этой кафедры.\n"
                            "'/chair' для вывода всех кафедр.\n"
                            "'/faculty' для вывода всех факультетов.\n"
                            "'/ratings' для вывода всех отзывов",
                    reply_markup=keyboard_f(tb, stage="TEACHER_BUTTON"))

@bot.message_handler(commands=['teacher'])   ### Готов
def choose(message) -> None:
    global stage
    stage = "TEACHER_CHOOSING"   
    print(20*"#", stage, 20*"#") #
    teacher = []
    try:
        if len(message.text.split()) == 2:
            for i in range(1, 3+1):
                mssg = message.text.split()[1]
                cursor.execute(f"SELECT * FROM teachers WHERE split_part(t_name, ' ', {i}) = '{mssg.capitalize()}';")
                teacher = list(cursor.fetchall())
                if teacher: break
        elif len(message.text.split()) == 3:
            for i in range(1, 2+1):
                for j in range(i+1, 3+1):
                    mssg = message.text.split()[1:3]
                    print(i, j, ' ', mssg) ##################################
                    cursor.execute(f"SELECT * FROM teachers WHERE split_part(t_name, ' ', {i}) = '{mssg[0].capitalize()}' AND split_part(t_name, ' ', {j}) = '{mssg[1].capitalize()}';")
                    teacher = list(cursor.fetchall())
                    if teacher: break
                if teacher: break
        elif len(message.text.split()) == 4:
            cursor.execute(f"SELECT * FROM teachers WHERE t_name = '{message.text[9:]}';")
            teacher = list(cursor.fetchall())
        if len(message.text.split()) == 1: bot.send_message(message.chat.id, text="Имя преподавателя необходимо ввести после '/teacher'")
        if not teacher and len(message.text.split())>1: bot.send_message(message.chat.id, text="Такого преподавателя нет")

        if teacher:   
            print(teacher, type(teacher), len(message.text.split()), message.text) ##################################
            if len(teacher) > 1:
                s = ""  
                for i in teacher:
                    s += "  • " + i[1] + "\n    Кафедра: " + i[2] + '\n\n'
                bot.send_message(message.chat.id, text=f"С таким именем есть несколько преподов:\n{s}\n\nНеобходимо уточнить запрос - напишите '/teacher' с ФИ или ИО")
            if len(teacher) == 1:
                global t_name
                t_name = teacher[0][1]
                bot.send_message(message.chat.id, text=output(ratings=[teacher[0][1:-2][0], teacher[0][1:-2][1]], stage=stage), reply_markup=keyboard_f(tb, stage))
                bot.register_next_step_handler(message, handle_butt)
    except psycopg2.ProgrammingError or IndexError as e: 
        print(e)
        bot.send_message(message.chat.id, text="Имя преподавателя необходимо ввести после '/teacher'") #

def handle_butt(message) -> None:   ### Готов
    global stage
    stage = "TEACHER_BUTTON"   
    print(20*"#", stage, 20*"#") #
    try:
        if message.text == 'Написать отзыв':
            bot.send_message(message.chat.id, text='Введите отзыв как на примере (оценка не должна быть выше 5):\n4.9 Лучший препод')
            bot.register_next_step_handler(message, handle_rate)

        elif message.text == 'Посмотреть отзывы':
            global num, t_name
            num = 1
            ratings = get_ratings_ofone(tb, cursor, t_name)
            if ratings:
                print(ratings, len(ratings)) ##################################
                bot.send_message(message.chat.id, 
                                text=output(num=num, t_name=t_name, ratings=ratings, stage=stage),
                                reply_markup=keyboard_f(tb, num=num, stage="TEACHER_LOOK", max_num=len(ratings)))
            else: bot.send_message(message.chat.id, 
                                text=f"У преподователя {t_name} еще нет отзывов!",
                                reply_markup=keyboard_f(tb, num=num, stage="TEACHER_CHOOSING"))
            bot.register_next_step_handler(message, handle_butt)

        elif message.text == 'Посмотреть статистику':
            cursor.execute(f"SELECT rate FROM ratings WHERE t_name = '{t_name}'")
            rates = list(cursor.fetchall())
            teach_rate = [float(i[0]) for i in rates]
            if teach_rate: bot.send_message(message.chat.id, 
                            text=f"Статистика отзывов:\n\nПреподаватель: {t_name}\nКол-во отзывов: {len(teach_rate)}\nСредний показатель: {(sum(teach_rate)/len(teach_rate))//0.1/10}", 
                            reply_markup=keyboard_f(tb, stage="TEACHER_CHOOSING"))
            else: bot.send_message(message.chat.id, 
                                text=f"У преподователя {t_name} еще нет отзывов!",
                                reply_markup=keyboard_f(tb, num=num, stage="TEACHER_CHOOSING"))
            bot.register_next_step_handler(message, handle_butt)

        elif message.text == 'Отменить выбор': bot.send_message(message.chat.id, 
                                                                text=f"Клавиатура убрана",
                                                                reply_markup=keyboard_f(tb, num=num, stage=stage))
        else: bot.reply_to(message, text='Вы ввели фигню:'+message.text, reply_markup=keyboard_f(tb, num=num, stage="TEACHER_CHOOSING"))
    except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {message.chat.id}: {e}")
            bot.reply_to(message, text='oOOopS, tHE bUg hAppENeD', reply_markup=keyboard_f(tb, stage=stage))
        
def handle_rate(message) -> None:
    global stage, t_name
    stage = "TEACHER_RATE"
    print(20*"#", stage, 20*"#") #
    rate = output(mssg=message.text, stage=stage)
    print(rate[0], rate[0].isalpha(), float(rate[0]))
    if not(rate[0].isalpha()):
        if float(rate[0]) > 5.0: 
            bot.send_message(message.chat.id, text=f"Оценка не должна превышать 5")
            bot.register_next_step_handler(message, handle_rate)
        else: 
            try:
                cursor.execute(f"INSERT INTO ratings(t_name, rate_txt, rate) VALUES('{t_name}', '{rate[1]}', {rate[0]});")
                conn.commit()
                bot.send_message(message.chat.id, text=f"Ваш отзыв:\n  {rate[1]}\nВаша оценка:\n  {rate[0]}", reply_markup=keyboard_f(tb, stage="TEACHER_CHOOSING"))
                bot.send_message(message.chat.id, text=f"Выбранный преподаватель - {t_name}")
                bot.register_next_step_handler(message, handle_butt)
            except TypeError or psycopg2.errors.SyntaxError or psycopg2.errors.UndefinedColumn:
                bot.send_message(message.chat.id, text=f'Введите отзыв как на примере:\n4.9 Лучший препод')
                bot.register_next_step_handler(message, handle_rate)
    else: bot.send_message(message.chat.id, text=f'Введите отзыв как на примере:\n4.9 Лучший препод')

@bot.callback_query_handler(func=lambda call: call.data == 'go_on')
def goon_btn(call):
    global num, t_name, stage
    num += 1
    print(num, t_name, get_ratings_ofone(tb, cursor, t_name), "TEACHER_BUTTON")
    print(output(num=num, t_name=t_name, ratings=get_ratings_ofone(tb, cursor, t_name), stage="TEACHER_BUTTON"))
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id, 
                          text=output(num=num, t_name=t_name, ratings=get_ratings_ofone(tb, cursor, t_name), stage="TEACHER_BUTTON"),
                          reply_markup=keyboard_f(tb, num=num, max_num=len(get_ratings_ofone(tb, cursor, t_name)), stage="TEACHER_LOOK"))

@bot.callback_query_handler(func=lambda call: call.data == 'go_back')
def gobck_btn(call):
    global num, t_name, stage
    num -= 1
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id, 
                          text=output(num=num, t_name=t_name, ratings=get_ratings_ofone(tb, cursor, t_name), stage="TEACHER_BUTTON"),
                          reply_markup=keyboard_f(tb, num=num, max_num=len(get_ratings_ofone(tb, cursor, t_name)), stage="TEACHER_LOOK"))
    
@bot.callback_query_handler(func=lambda call: call.data == 'go_on_/rating')
def goon_btn(call):
    global num, stage
    num += 1
    rating = get_ratings_ofall(tb, cursor)
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id, 
                          text=output(num=num, t_name=t_name, ratings=rating, stage=stage),
                          reply_markup=keyboard_f(tb, num=num, max_num=rating, stage="RATINGS"))

@bot.callback_query_handler(func=lambda call: call.data == 'go_back_/rating')
def gobck_btn(call):
    global num, stage
    num -= 1
    rating = get_ratings_ofall(tb, cursor)
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id, 
                          text=output(num=num, t_name=t_name, ratings=rating, stage=stage),
                          reply_markup=keyboard_f(tb, num=num, max_num=rating, stage="RATINGS"))

@bot.callback_query_handler(func=lambda call: call.data == 'blank')
def count_btn(call):
    global count
    count += 1
    if count == 2:
        bot.send_message(call.message.chat.id, 
                         text=f"😁Кнопка с числом ничего не делает😁", 
                         reply_markup=keyboard_f(tb, num=num, stage="TEACHER_CHOOSING"))
        bot.register_next_step_handler(call.message, handle_butt)

@bot.message_handler(content_types=['text'])
def echo(message):
    bot.send_message(message.chat.id, 
                     text=f"Простите, бот не умеет понимать ничего, кроме команд.\n"
                           "Чтобы просмотреть комнады введите '/help'")
    print("      ", message.text)

bot.polling(none_stop=True)