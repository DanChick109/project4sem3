def get_ratings_ofone(tb, cursor, t_name: str) -> list:
    cursor.execute(f"SELECT * FROM ratings WHERE t_name = '{t_name}'")
    ratings = list(cursor.fetchall())
    return ratings

def get_ratings_all(tb, cursor) -> list:
    cursor.execute(f"SELECT * FROM ratings")
    ratings = list(cursor.fetchall())
    return ratings