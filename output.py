def output(stage:  str, ratings: list = [], num: int = 1, lst: list = [], mssg: str = "") -> str:
    if stage == "TEACHER_CHOOSING":
        t_name, k_name = lst[0], lst[1]
        return f"Вы выбрали:\n\nПреподаватель - {t_name}\nКафедра - {k_name}"
    if stage == "TEACHER_RATE":
        rating = mssg.split()[0]
        mssg = mssg.replace(rating+" ", "")
        rate_txt = mssg[:]
        return [rating, rate_txt]
    if stage == "TEACHER_BUTTON":
        return f"Отзыв №{num}\nПреподаватель {t_name.capitalize()}:\n\nОценка: {ratings[num-1][3]}\nОтзыв: {ratings[num-1][2]}"