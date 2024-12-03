import telebot  # Бібліотека для роботи з Telegram Bot API
import requests  # Бібліотека для виконання HTTP-запитів
from telebot import types  # Модуль для роботи з типами клавіатур і кнопок у Telegram
from urllib.parse import quote  # Функція для кодування URL-запитів

# Токен API для Telegram бота
API_TOKEN = '7538748283:AAF04wzxWHcUa_5hdRI2kcX452v8iTARS3U'
# Ключ API для OMDb
OMDB_API_KEY = '5f4fe9dc'

# Створюємо об'єкт бота
bot = telebot.TeleBot(API_TOKEN)

# Мова бота для кожного користувача
user_languages = {}

# Функція для отримання імені користувача
def get_user_first_name(message):
    return message.from_user.first_name if message.from_user.first_name else "друг"

# Функція для створення клавіатури з кнопкою /help
def start_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    help_button = types.KeyboardButton('/help')
    keyboard.add(help_button)
    return keyboard

# Функція для створення клавіатури для вибору мови
def language_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    english_button = types.KeyboardButton('/lang_en')
    ukrainian_button = types.KeyboardButton('/lang_uk')
    keyboard.add(english_button, ukrainian_button)
    return keyboard

# Обробник команди /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = get_user_first_name(message)
    user_languages.setdefault(message.from_user.id, 'uk')  # За замовчуванням українська
    keyboard = start_keyboard()
    bot.reply_to(message, f"Привіт, {user_name}! \n"
                          "Використовуйте кнопку нижче для отримання допомоги.", reply_markup=keyboard)

# Обробник команди /help
@bot.message_handler(commands=['help'])
def send_help(message):
    user_name = get_user_first_name(message)
    language = user_languages.get(message.from_user.id, 'uk')
    if language == 'uk':
        help_text = ("Доступні команди:\n"
                     "/start - Привітання і основні інструкції\n"
                     "/find <назва фільму> - Знайти фільм за назвою\n"
                     "/search <ключове слово> - Знайти фільми за ключовими словами\n"
                     "/genre <жанр> - Знайти фільми за жанром\n"
                     "/lang_en - Вибрати англійську мову")
    else:
        help_text = ("Available commands:\n"
                     "/start - Greeting and basic instructions\n"
                     "/find <movie title> - Find a movie by title\n"
                     "/search <keyword> - Find movies by keyword\n"
                     "/genre <genre> - Find movies by genre\n"
                     "/lang_uk - Switch to Ukrainian language")
    bot.reply_to(message, help_text)

# Обробник команди /find
@bot.message_handler(commands=['find'])
def find_movie(message):
    user_name = get_user_first_name(message)
    language = user_languages.get(message.from_user.id, 'uk')
    try:
        search_query = message.text.split(' ', 1)[1]
    except IndexError:
        if language == 'uk':
            bot.reply_to(message, f"Будь ласка, {user_name}, надайте назву фільму після команди /find.")
        else:
            bot.reply_to(message, f"Please provide the movie title after the /find command, {user_name}.")
        return

    # Кодуємо запит для уникнення проблем з символами
    encoded_query = quote(search_query)
    url = f'http://www.omdbapi.com/?t={encoded_query}&apikey={OMDB_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if data.get('Response') == 'True':
        title = data.get('Title')
        year = data.get('Year')
        rating = data.get('imdbRating')
        director = data.get('Director')
        actors = data.get('Actors')
        genre = data.get('Genre')  # Додаємо жанр фільму
        overview = data.get('Plot')
        poster = data.get('Poster')
        trailer_url = f"https://www.youtube.com/results?search_query={title}+trailer"

        response_message = (f"🎬 Назва: {title}\n"
                            f"📅 Рік: {year}\n"
                            f"⭐ Рейтинг IMDb: {rating}\n"
                            f"🎥 Режисер: {director}\n"
                            f"🎭 Актори: {actors}\n"
                            f"📚 Жанр: {genre}\n"  # Додаємо жанр у відповідь
                            f"📝 Опис: {overview}\n"
                            f"▶️ Трейлер на YouTube: {trailer_url}")
        if poster != 'N/A':
            bot.send_photo(message.chat.id, poster, caption=response_message)
        else:
            bot.reply_to(message, response_message)
    else:
        if language == 'uk':
            bot.reply_to(message, f"Фільм не знайдено, {user_name}.")
        else:
            bot.reply_to(message, f"Movie not found, {user_name}.")

# Обробник команди /search
@bot.message_handler(commands=['search'])
def search_movies(message):
    user_name = get_user_first_name(message)
    language = user_languages.get(message.from_user.id, 'uk')
    try:
        search_query = message.text.split(' ', 1)[1]
    except IndexError:
        if language == 'uk':
            bot.reply_to(message, f"Будь ласка, {user_name}, надайте ключове слово після команди /search.")
        else:
            bot.reply_to(message, f"Please provide the keyword after the /search command, {user_name}.")
        return

    # Кодуємо запит для уникнення проблем з символами
    encoded_query = quote(search_query)
    url = f'http://www.omdbapi.com/?s={encoded_query}&apikey={OMDB_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if data.get('Response') == 'True':
        movies = data.get('Search')
        if movies:
            for movie in movies:
                movie_title = movie.get('Title')
                movie_year = movie.get('Year')
                movie_poster = movie.get('Poster')

                # Додатковий запит для отримання деталей фільму, включаючи жанр
                movie_encoded_title = quote(movie_title)
                movie_url = f'http://www.omdbapi.com/?t={movie_encoded_title}&apikey={OMDB_API_KEY}'
                movie_response = requests.get(movie_url)
                movie_data = movie_response.json()

                if movie_data.get('Response') == 'True':
                    genre = movie_data.get('Genre', 'Невідомо')  # Отримання жанру
                    response_message = (f"🎬 Назва: {movie_title}\n"
                                        f"📅 Рік: {movie_year}\n"
                                        f"📚 Жанр: {genre}\n")
                    if movie_poster != 'N/A':
                        bot.send_photo(message.chat.id, movie_poster, caption=response_message)
                    else:
                        bot.reply_to(message, response_message)
                else:
                    if language == 'uk':
                        bot.reply_to(message, f"Не вдалося отримати інформацію про фільм '{movie_title}', {user_name}.")
                    else:
                        bot.reply_to(message, f"Failed to retrieve information about '{movie_title}', {user_name}.")
        else:
            if language == 'uk':
                bot.reply_to(message, f"Не знайдено жодного фільму, що відповідає '{search_query}', {user_name}.")
            else:
                bot.reply_to(message, f"No movies found matching '{search_query}', {user_name}.")
    else:
        if language == 'uk':
            bot.reply_to(message, f"Щось пішло не так при пошуку фільмів, {user_name}.")
        else:
            bot.reply_to(message, f"Something went wrong while searching for movies, {user_name}.")

# Обробник команди /genre
@bot.message_handler(commands=['genre'])
def search_by_genre(message):
    user_name = get_user_first_name(message)
    language = user_languages.get(message.from_user.id, 'uk')
    try:
        genre_query = message.text.split(' ', 1)[1]
    except IndexError:
        if language == 'uk':
            bot.reply_to(message, f"Будь ласка, {user_name}, надайте жанр після команди /genre.")
        else:
            bot.reply_to(message, f"Please provide the genre after the /genre command, {user_name}.")
        return

    # Кодуємо запит для уникнення проблем з символами
    encoded_query = quote(genre_query)
    url = f'http://www.omdbapi.com/?s={encoded_query}&apikey={OMDB_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if data.get('Response') == 'True':
        movies = data.get('Search')
        if movies:
            for movie in movies:
                movie_title = movie.get('Title')
                movie_year = movie.get('Year')
                movie_poster = movie.get('Poster')

                # Додатковий запит для отримання деталей фільму, включаючи жанр
                movie_encoded_title = quote(movie_title)
                movie_url = f'http://www.omdbapi.com/?t={movie_encoded_title}&apikey={OMDB_API_KEY}'
                movie_response = requests.get(movie_url)
                movie_data = movie_response.json()

                if movie_data.get('Response') == 'True':
                    genre = movie_data.get('Genre', 'Невідомо')  # Отримання жанру
                    if genre_query.lower() in genre.lower():
                        response_message = (f"🎬 Назва: {movie_title}\n"
                                            f"📅 Рік: {movie_year}\n"
                                            f"📚 Жанр: {genre}\n")
                        if movie_poster != 'N/A':
                            bot.send_photo(message.chat.id, movie_poster, caption=response_message)
                        else:
                            bot.reply_to(message, response_message)
                else:
                    if language == 'uk':
                        bot.reply_to(message, f"Не вдалося отримати інформацію про фільм '{movie_title}', {user_name}.")
                    else:
                        bot.reply_to(message, f"Failed to retrieve information about '{movie_title}', {user_name}.")
        else:
            if language == 'uk':
                bot.reply_to(message, f"Не знайдено жодного фільму, що відповідає '{genre_query}', {user_name}.")
            else:
                bot.reply_to(message, f"No movies found matching '{genre_query}', {user_name}.")
    else:
        if language == 'uk':
            bot.reply_to(message, f"Щось пішло не так при пошуку фільмів, {user_name}.")
        else:
            bot.reply_to(message, f"Something went wrong while searching for movies, {user_name}.")

# Обробник команди /lang_en
@bot.message_handler(commands=['lang_en'])
def set_language_english(message):
    user_languages[message.from_user.id] = 'en'
    bot.reply_to(message, "Language set to English.")

# Обробник команди /lang_uk
@bot.message_handler(commands=['lang_uk'])
def set_language_ukrainian(message):
    user_languages[message.from_user.id] = 'uk'
    bot.reply_to(message, "Мову змінено на українську.")

# Запускаємо бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
