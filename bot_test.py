import telebot as tb
import psycopg2
from rating import rating
from keyboard_f import keyboard_f
from config import TOKEN
from output import output

bot = tb.TeleBot(TOKEN())
conn = psycopg2.connect(database="postgres",
                        user="postgres",
                        password="postgres",)
cursor = conn.cursor()
users = set()
t_name = ""

@bot.message_handler(commands=["start"])   ### Готов
def welcome(message) -> None:
    global users, stage
    stage = "START"   
    print(20*"#", stage, 20*"#") #
    users.add((message.chat.first_name, message.chat.last_name, message.chat.username, message.chat.id, message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username))
    with open("D:/Downloadse/UNI/BBNT/proj_sem_3/data_users.txt", mode="r+") as f:
        f.write(f"{users}\n")
    bot.send_message(message.chat.id,
                           "Добро пожаловать в бота с рейтингом преподавателей. "
                           "Для вывода всех команд используйте команду '/help'.")

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
        bot.send_message(message.chat.id, f"Преподаватели кафедры '{kafs[0]}':\n\n{s}")
    else:
        bot.send_message(message.chat.id, f"Такой кафедры не существует")

@bot.message_handler(commands=['name'])   ### Готов
def list_of_k(message) -> None:
    bot.send_message(message.chat.id, f"{message.chat.first_name} {message.chat.last_name} {message.chat.username} - {message.chat.id}")

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
    bot.send_message(message.chat.id, f"Кафедры МТУСИ:\n\n{s_f}")

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
    bot.send_message(message.chat.id, f"Факультеты МТУСИ:\n\n{s}")

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
                            "'/look Имя' для вывода отзывов о данном преподе")

@bot.message_handler(commands=['teacher'])   ### Готов (?)
def choose(message) -> None:
    global stage
    stage = "TEACHER_CHOOSING"   
    print(20*"#", stage, 20*"#") #
    try:
        for i in range(1, 4):
            mssg = message.text.split()[1].capitalize()
            cursor.execute(f"SELECT * FROM teachers WHERE split_part(t_name, ' ', {i}) = '{mssg}';")
            teacher = list(cursor.fetchall())
            if teacher: break
        else: 
            bot.send_message(message.chat.id, text="Такого препода нет")
    except IndexError or UnboundLocalError: bot.send_message(message.chat.id, text="Имя препода необходимо ввести после '/teacher'")
    else:
        print('\n', teacher, '\n', type(teacher), type(teacher[0]), len(teacher)) ##################################
        if len(teacher) > 1:
            s = ""  
            for i in teacher:
                s += i[1] + "\n  " + i[2] + '\n'
            bot.send_message(message.chat.id, text=f"С таким именем есть несколько преподов:\n{s}\n\nНеобходимо уточнить запрос (напишите фамилию)") ### метка что сейчас выбирается препод?
        if len(teacher) == 1:
            global t_name
            t_name = teacher[0][1]
            bot.send_message(message.chat.id, text=output(lst=teacher[0][1:-2]), reply_markup=keyboard_f(tb, stage))
            bot.register_next_step_handler(message, handle_butt)
        print("     ", message.text) ##################################

def handle_butt(message) -> None:  
    global stage
    stage = "TEACHER_BUTTON"   
    print(20*"#", stage, 20*"#") #
    try:
        if message.text == 'Написать отзыв':
            bot.send_message(message.chat.id, text='Введите отзыв как на примере:\n4.9 Лучший препод')
            bot.register_next_step_handler(message, handle_rate)
        elif message.text == 'Посмотреть отзывы':
            cursor.execute(f"SELECT * FROM ratings WHERE t_name = '{t_name}'")
            bot.send_message(message.chat.id, 
                             text=f"Отзывы по преподавателю {t_name}", 
                             reply_markup=keyboard_f(tb, stage="TEACHER_LOOK"))
        elif message.text == 'Посмотреть статистику':
            cursor.execute(f"SELECT rate FROM ratings WHERE t_name = '{t_name}'")
            rates = list(cursor.fetchall())
            print(rates, *rates) ##################################
            teach_rate = [float(i[j]) for i in rates for j in range(0, len(rates))]
            bot.send_message(message.chat.id, 
                             text=f"Статистика отзывов:\n\nПреподаватель: {t_name}\nКол-во отзывов: {len(teach_rate)}\nСредний показатель: {sum(teach_rate)/len(teach_rate)}", 
                             reply_markup=keyboard_f(tb, stage))
        elif message.text == 'Выбрать заново':
            bot.register_next_step_handler(message, choose)
        else:
            bot.reply_to(message, 'Вы ввели фигню: ' + message.text)
        bot.send_message(message.chat.id, text='Удаляю клавиатуру (потом убрать)', reply_markup=keyboard_f(tb, stage))
    except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {message.chat.id}: {e}")
            bot.send_message(message.chat.id, text=f'Произошла ошибка {e}', reply_markup=keyboard_f(tb, stage))
        
def handle_rate(message) -> None:
    global stage, t_name
    stage = "TEACHER_RATE"
    print(20*"#", stage, 20*"#") #
    rate = output(mssg=message.text)
    try:
        cursor.execute(f"INSERT INTO ratings(t_name, rate_txt, rate) VALUES('{t_name}', '{rate[1]}', {rate[0]});")
        conn.commit()
        bot.send_message(message.chat.id, text=f"Ваш отзыв:\n{rate[1]}\nВаша оценка:\n {rate[0]}\n\nДля просмотра всех отзывов на препода введите команду '/look Имя'")
        stage = "TEACHER_CHOOSING4LOOK"
        bot.register_next_step_handler(message, choose)
    except TypeError or psycopg2.errors.SyntaxError:
        bot.send_message(message.chat.id, text=f'Введите отзыв как на примере:\n4.9 Лучший препод')
        bot.register_next_step_handler(message, handle_rate)

"""
@bot.callback_query_handler(func=lambda call: call.data == 'go_on')
def save_btn(call):
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id  
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, 
                         text='Данные сохранены!')  


@bot.callback_query_handler(func=lambda call: call.data == 'go_back')
def save_btn(call):
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id  
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, 
                         text='Изменение данных!')
"""

@bot.message_handler(content_types=['text'])
def echo(message):
    bot.send_message(message.chat.id, text=f"Простите, бот не умеет понимать ничего, кроме команд.\nЧтобы просмотреть комнады введите '/help'")
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