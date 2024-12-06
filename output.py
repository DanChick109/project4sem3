def output(stage, t_name = "", k_name = "", ratings = [], num = 1, mssg = "") -> str:
    if stage == "TEACHER_CHOOSING":
        return f"Вы выбрали:\n\nПреподаватель - {t_name}\nКафедра - {k_name}"
    if stage == "TEACHER_RATE":
        rating = mssg.split()[0]
        mssg = mssg.replace(rating+" ", "")
        rate_txt = mssg[:]
        return [rating, rate_txt]
    if stage == "TEACHER_BUTTON":
        return f"Отзыв №{num}/{len(ratings)}\nПреподаватель {t_name[:-1]}:\n\nОценка: {ratings[num-1][3]}\nОтзыв: {ratings[num-1][2]}"