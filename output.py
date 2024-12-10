def output(stage, t_name = "", ratings = [], num = 1, mssg = "") -> str:
    if stage == "TEACHER_CHOOSING":
        return f"Вы выбрали:\n\nПреподаватель - {ratings[0]}\nКафедра - {ratings[1]}"
    if stage == "TEACHER_RATE":
        rating = mssg.split()[0]
        mssg = mssg.replace(rating+" ", "")
        rate_txt = mssg[:]
        return [rating, rate_txt]
    if stage == "TEACHER_BUTTON":
        print(num, len(ratings), t_name, ' ', ratings)
        return f"Отзыв №{num}/{len(ratings)}\nПреподаватель {t_name}:\n\nОценка: {ratings[num-1][3]}\nОтзыв: {ratings[num-1][2]}"
    if stage == "RATINGS":
        return f"Отзыв №{num}/{len(ratings)}\nПреподаватель {ratings[num-1][1]}:\n\nОценка: {ratings[num-1][2]}\nОтзыв: {ratings[num-1][3]}"