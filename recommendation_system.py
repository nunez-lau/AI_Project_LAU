"""Recomendador de películas sencillo con filtrado colaborativo."""

from math import sqrt


# Cada fila representa a un usuario y cada columna, una película.
# None significa que el usuario no ha calificado esa película.
USERS = ["Ana", "Luis", "Marta", "Pedro", "Sofía"]
MOVIES = ["Matrix", "Titanic", "Interestelar", "Toy Story", "El Padrino"]
RATINGS: list[list[int | None]] = [
    [5, 3, 4, None, 2],
    [4, None, 5, 2, 3],
    [None, 4, 4, 5, None],
    [2, 5, None, 4, 4],
    [5, 2, 4, 1, None],
]

MIN_RATING = 1
MAX_RATING = 5


def _validate_user_index(user_index: int) -> None:
    """Comprueba que el índice corresponde a un usuario existente."""
    if not isinstance(user_index, int) or isinstance(user_index, bool):
        raise TypeError("El índice del usuario debe ser un número entero.")
    if not 0 <= user_index < len(USERS):
        raise IndexError(f"Índice de usuario fuera de rango: {user_index}")


def _average_rating(user_index: int) -> float:
    """Devuelve el promedio de las calificaciones conocidas de un usuario."""
    ratings = [
        rating for rating in RATINGS[user_index]
        if rating is not None
    ]
    if not ratings:
        return 0.0
    return sum(ratings) / len(ratings)


def cosine_similarity(user_a: int, user_b: int) -> float:
    """Calcula la similitud coseno entre dos usuarios.

    Compara solo las películas calificadas por ambos y centra cada nota
    respecto al promedio del usuario, para reducir diferencias al calificar.
    """
    _validate_user_index(user_a)
    _validate_user_index(user_b)

    average_a = _average_rating(user_a)
    average_b = _average_rating(user_b)
    common_ratings = [
        (rating_a - average_a, rating_b - average_b)
        for rating_a, rating_b in zip(RATINGS[user_a], RATINGS[user_b])
        if rating_a is not None and rating_b is not None
    ]
    if not common_ratings:
        return 0.0

    dot_product = sum(value_a * value_b for value_a, value_b in common_ratings)
    magnitude_a = sqrt(sum(value_a**2 for value_a, _ in common_ratings))
    magnitude_b = sqrt(sum(value_b**2 for _, value_b in common_ratings))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    # El límite protege el resultado de pequeños errores de redondeo.
    similarity = dot_product / (magnitude_a * magnitude_b)
    return max(-1.0, min(1.0, similarity))


def recommend_movies(target_user: str, limit: int = 3) -> list[tuple[str, float]]:
    """Recomienda películas no calificadas, ordenadas por nota estimada."""
    if target_user not in USERS:
        raise ValueError(f"Usuario desconocido: {target_user}")
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("El límite debe ser un número entero.")
    if limit < 0:
        raise ValueError("El límite de recomendaciones no puede ser negativo.")

    target_index = USERS.index(target_user)
    target_average = _average_rating(target_index)
    recommendations: list[tuple[str, float]] = []

    for movie_index, movie in enumerate(MOVIES):
        # Se excluyen las películas que el usuario ya calificó.
        if RATINGS[target_index][movie_index] is not None:
            continue

        weighted_deviation = 0.0
        similarity_total = 0.0
        for other_index, other_ratings in enumerate(RATINGS):
            other_rating = other_ratings[movie_index]
            if other_index == target_index or other_rating is None:
                continue

            similarity = cosine_similarity(target_index, other_index)
            # Usuarios con similitud negativa o nula no contribuyen al cálculo.
            if similarity > 0:
                neighbor_average = _average_rating(other_index)
                weighted_deviation += similarity * (other_rating - neighbor_average)
                similarity_total += similarity

        if similarity_total == 0:
            continue

        # Ajusta el promedio del usuario objetivo según las opiniones de sus vecinos.
        predicted_rating = target_average + weighted_deviation / similarity_total
        predicted_rating = max(MIN_RATING, min(MAX_RATING, predicted_rating))
        recommendations.append((movie, round(predicted_rating, 2)))

    # Orden alfabético como desempate para obtener resultados reproducibles.
    recommendations.sort(key=lambda recommendation: (-recommendation[1], recommendation[0]))
    return recommendations[:limit]


if __name__ == "__main__":
    target_user = "Ana"
    target_index = USERS.index(target_user)

    print(f"Similitud de {target_user} con los demás usuarios:")
    for other_index, other_user in enumerate(USERS):
        if other_index != target_index:
            similarity = cosine_similarity(target_index, other_index)
            print(f"  {other_user}: {similarity:.2f}")

    print(f"\nPelículas recomendadas para {target_user}:")
    recommendations = recommend_movies(target_user)
    if recommendations:
        for movie, predicted_rating in recommendations:
            print(f"  {movie}: nota estimada {predicted_rating:.2f}/5")
    else:
        print("  No hay suficientes calificaciones para generar recomendaciones.")