import telebot as tb
import psycopg2
from keyboard_f import keyboard_f
from rating import get_ratings_ofone, get_ratings_ofall
from config import TOKEN
from output import output

bot = tb.TeleBot(TOKEN())
conn = psycopg2.connect(database="postgres",
                        user="postgres",
                        password="postgres",)
cursor = conn.cursor()
users = set()
num = 0
t_name = ""

@bot.message_handler(commands=["start"])   ### Готов
def welcome(message) -> None:
    global users, stage
    stage = "START"   
    print(20*"#", stage, 20*"#") #
    users.add((message.chat.first_name, message.chat.last_name, message.chat.username,
                message.chat.id))
    with open("data_users.txt", mode="r+") as f:
        f.write(f"{users}\n")
    bot.send_message(message.chat.id,
                           "Добро пожаловать в бота с рейтингом преподавателей. "
                           "Для вывода всех команд используйте команду '/help'.", 
                     reply_markup=keyboard_f(tb, stage="TEACHER_BUTTON"))

@bot.message_handler(commands=['list'])   ### Готов
def list_of_t(message) -> None:
    global stage
    stage = "LIST"   
    print(20*"#", stage, 20*"#") #
    mmsg_txt, s = message.text[6:], ""
    kafs = []
    if len(mmsg_txt) < 6:
        for i in range(1, 7): 
            cursor.execute(f"SELECT kaf_name FROM kafedra WHERE split_part(kaf_name, ' ', {i}) = '({mmsg_txt})'")
            kafs_i = [j[0] for j in list(cursor.fetchall())]
            if kafs_i: kafs = kafs_i
    else: 
        cursor.execute(f"SELECT kaf_name FROM kafedra WHERE kaf_name = '{mmsg_txt}'")
        kafs = [i[0] for i in list(cursor.fetchall())]
    if kafs:
        cursor.execute("SELECT t_name FROM teachers WHERE kaf_name=%s", (kafs[0],))
        teachs = [i[0] for i in list(cursor.fetchall())]
        for i in teachs:
            s += i + '\n'
        bot.send_message(message.chat.id, f"Преподаватели кафедры '{kafs[0]}':\n\n{s}",
                         reply_markup=keyboard_f(tb, stage="TEACHER_BUTTON"))
    else:
        bot.send_message(message.chat.id, f"Такой кафедры не существует",
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
                            "'/teacher Фамилия' для выбора преподавателя.\n"
                            "'/list Кафедра' для вывода всех преподавателей из этой кафедры.\n"
                            "'/chair' для вывода всех кафедр.\n"
                            "'/faculty' для вывода всех факультетов.\n"
                            "'/ratings' для вывода всех отзывов",
                    reply_markup=keyboard_f(tb, stage="TEACHER_BUTTON"))

@bot.message_handler(commands=['teacher'])   ### Почти Готов (?)
def choose(message) -> None:
    global stage
    stage = "TEACHER_CHOOSING"   
    print(20*"#", stage, 20*"#") #
    try:
        if len(message.text.split()) == 2:   ### Готов
            for i in range(1, 3+1):
                mssg = message.text.split()[1]
                cursor.execute(f"SELECT * FROM teachers WHERE split_part(t_name, ' ', {i}) = '{mssg.capitalize()}';")
                teacher = list(cursor.fetchall())
                if teacher: break
                if not teacher: bot.send_message(message.chat.id, text="Такого препода нет")
        elif len(message.text.split()) == 3:   ####### Тварь #######
            for i in range(1, 2+1):
                for j in range(i+1, 3+1):
                    mssg = message.text.split()[1:3]
                    print(i, j, ' ', mssg) ##################################
                    cursor.execute(f"SELECT * FROM teachers WHERE split_part(t_name, ' ', {i}) = '{mssg[0].capitalize()}' AND split_part(t_name, ' ', {j}) = '{mssg[1].capitalize()}';")
                    teacher = list(cursor.fetchall())
                    if teacher: break
                if teacher: break
            if not teacher: bot.send_message(message.chat.id, text="Такого препода нет")
        elif len(message.text.split()) == 4:   ### Готов
            cursor.execute(f"SELECT * FROM teachers WHERE t_name = '{message.text[9:]}';")
            teacher = list(cursor.fetchall())
            if not teacher: bot.send_message(message.chat.id, text="Такого препода нет")
        else:
            bot.send_message(message.chat.id, text="Имя препода необходимо ввести после '/teacher'")
    except  UnboundLocalError: bot.send_message(message.chat.id, text="Имя препода необходимо ввести после '/teacher'") #IndexError or ######################################################## 
    else:
        print(teacher, type(teacher), len(message.text.split()), message.text) ##################################
        if len(teacher) > 1:
            s = ""  
            for i in teacher:
                s += "  • " + i[1] + "\n    Кафедра: " + i[2] + '\n'
            bot.send_message(message.chat.id, text=f"С таким именем есть несколько преподов:\n{s}\n\nНеобходимо уточнить запрос - напишите '/teacher Фамилия Имя')")
        if len(teacher) == 1:
            global t_name
            t_name = teacher[0][1]
            bot.send_message(message.chat.id, text=output(t_name = teacher[0][1:-2][0], k_name = teacher[0][1:-2][1], stage=stage), reply_markup=keyboard_f(tb, stage))
            bot.register_next_step_handler(message, handle_butt)
        print("     ", message.text) ##################################

def handle_butt(message) -> None:   ### Готов
    global stage
    stage = "TEACHER_BUTTON"   
    print(20*"#", stage, 20*"#") #
    try:
        if message.text == 'Написать отзыв':   ### Готов
            bot.send_message(message.chat.id, text='Введите отзыв как на примере:\n4.9 Лучший препод')
            bot.register_next_step_handler(message, handle_rate)
        elif message.text == 'Посмотреть отзывы':   ### Готов
            global num, t_name
            num = 1
            ratings = get_ratings_ofone(tb, cursor, t_name)
            if ratings:
                bot.send_message(message.chat.id, 
                                text=output(num=num, t_name=t_name, ratings=ratings, stage=stage),
                                reply_markup=keyboard_f(tb, num=num, stage="TEACHER_LOOK"))
            else:
                bot.send_message(message.chat.id, 
                                text=f"У преподователя {t_name} еще нет отзывов\nВы можете стать первым!",
                                reply_markup=keyboard_f(tb, num=num, stage="TEACHER_CHOOSING"))
                bot.register_next_step_handler(message, handle_butt)
        elif message.text == 'Посмотреть статистику':   ### Готов
            cursor.execute(f"SELECT rate FROM ratings WHERE t_name = '{t_name}'")
            rates = list(cursor.fetchall())
            print(rates, *rates) ##################################
            teach_rate = [float(i[0]) for i in rates]
            if teach_rate:
                bot.send_message(message.chat.id, 
                                text=f"Статистика отзывов:\n\nПреподаватель: {t_name}\nКол-во отзывов: {len(teach_rate)}\nСредний показатель: {sum(teach_rate)/len(teach_rate)}", 
                                reply_markup=keyboard_f(tb, stage))
            else:
                bot.send_message(message.chat.id, 
                                text=f"У преподователя {t_name} еще нет отзывов\nВы можете стать первым!",
                                reply_markup=keyboard_f(tb, num=num, stage=stage))
                bot.register_next_step_handler(message, handle_butt)
        elif message.text == 'Убрать клавиатуру':   ### Готов
            bot.send_message(message.chat.id, 
                                text=f"Клавиатура убрана",
                                reply_markup=keyboard_f(tb, num=num, stage=stage))
            bot.register_next_step_handler(message, choose)
        else:
            bot.reply_to(message, 'Вы ввели фигню: ' + message.text)
    except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {message.chat.id}: {e}")
            bot.reply_to(message, text='oOOopS, tHE bUg hAppENeD', reply_markup=keyboard_f(tb, stage=stage))
        
def handle_rate(message) -> None:   ### Готов (?)
    global stage, t_name
    stage = "TEACHER_RATE"
    print(20*"#", stage, 20*"#") #
    rate = output(mssg=message.text, stage=stage)
    try:
        cursor.execute(f"INSERT INTO ratings(t_name, rate_txt, rate) VALUES('{t_name}', '{rate[1]}', {rate[0]});")
        conn.commit()
        bot.send_message(message.chat.id, text=f"Ваш отзыв:\n{rate[1]}\nВаша оценка:\n {rate[0]}")
        stage = "TEACHER_CHOOSING4LOOK"
        bot.register_next_step_handler(message, choose)
    except TypeError or psycopg2.errors.SyntaxError or psycopg2.errors.UndefinedColumn:
        bot.send_message(message.chat.id, text=f'Введите отзыв как на примере:\n4.9 Лучший препод')
        bot.register_next_step_handler(message, handle_rate)


@bot.callback_query_handler(func=lambda call: call.data == 'go_on')
def goon_btn(call):
    global num, t_name
    num += 1

    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id, 
                          text=output(num=num, t_name=t_name, ratings=get_ratings_ofone(tb, cursor, t_name), stage="TEACHER_BUTTON"),
                          reply_markup=keyboard_f(tb, num=num, max_num=len(get_ratings_ofone(tb, cursor, t_name)), stage="TEACHER_LOOK"))

@bot.callback_query_handler(func=lambda call: call.data == 'go_back')
def gobck_btn(call):
    global num, t_name
    num -= 1
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id, 
                          text=output(num=num, t_name=t_name, ratings=get_ratings_ofone(tb, cursor, t_name), stage="TEACHER_BUTTON"),
                          reply_markup=keyboard_f(tb, num=num, max_num=len(get_ratings_ofone(tb, cursor, t_name)), stage="TEACHER_LOOK"))
    
@bot.callback_query_handler(func=lambda call: call.data == 'blank')
def count_btn(call):
    pass
    

@bot.message_handler(content_types=['text'])
def echo(message):
    bot.send_message(message.chat.id, 
                     text=f"Простите, бот не умеет понимать ничего, кроме команд.\n"
                           "Чтобы просмотреть комнады введите '/help'")
    print("      ", message.text)

bot.polling(none_stop=True)




"""
CREATE TABLE fakultet (
		f_id SERIAL PRIMARY KEY,
		fak_name VARCHAR UNIQUE);
CREATE TABLE kafedra (
		k_id SERIAL PRIMARY KEY,
		kaf_name VARCHAR UNIQUE,
        fak_name VARCHAR REFERENCES fakultet(fak_name));
CREATE TABLE teachers (
		t_id SERIAL PRIMARY KEY, 
		t_name VARCHAR NOT NULL UNIQUE,
		kaf_name VARCHAR REFERENCES kafedra(kaf_name),
        fak_name VARCHAR REFERENCES fakultet(fak_name),
		rating FLOAT);
CREATE TABLE ratings (
		r_id SERIAL PRIMARY KEY,
		t_name VARCHAR REFERENCES teachers(t_name),
        rate_txt VARCHAR NOT NULL,
		rate FLOAT NOT NULL)

SELECT *
FROM teachers
WHERE split_part(t_name, ' ', 1) = 'Панков';
"""