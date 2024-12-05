def output(lst: list = [], mssg: str ="") -> str:
    if len(lst) == 2:
        t_name, k_name = lst[0], lst[1]
        return f"Вы выбрали:\n\nПреподаватель - {t_name}\nКафедра - {k_name}"
    if len(list(mssg.split())) >= 2:
        rating = mssg.split()[0]
        mssg = mssg.replace(rating+" ", "")
        rate_txt = mssg[:]
        return [rating, rate_txt]