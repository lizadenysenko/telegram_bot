import unittest
from unittest.mock import patch, MagicMock
from telebot import types
import bot  # Імпорт вашого бота

class TestBotIntegration(unittest.TestCase):

    @patch('bot.requests.get')  # Мокаємо HTTP-запит до OMDb API
    def test_find_movie(self, mock_get):
        # Налаштовуємо мок для відповіді від OMDb API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Response": "True",
            "Title": "Inception",
            "Year": "2010",
            "imdbRating": "8.8",
            "Director": "Christopher Nolan",
            "Actors": "Leonardo DiCaprio, Joseph Gordon-Levitt",
            "Genre": "Action, Sci-Fi",
            "Plot": "A thief who steals corporate secrets through the use of dream-sharing technology...",
            "Poster": "https://link_to_poster.jpg"
        }
        mock_get.return_value = mock_response

        # Симулюємо повідомлення користувача
        message = MagicMock()
        message.text = '/find Inception'
        message.from_user.id = 12345
        message.chat.id = 12345

        # Викликаємо команду /find
        bot.find_movie(message)

        # Перевірка, чи був надісланий правильний текст
        bot.reply_to.assert_called_with(
            message,
            "🎬 Назва: Inception\n📅 Рік: 2010\n⭐ Рейтинг IMDb: 8.8\n🎥 Режисер: Christopher Nolan\n🎭 Актори: Leonardo DiCaprio, Joseph Gordon-Levitt\n📚 Жанр: Action, Sci-Fi\n📝 Опис: A thief who steals corporate secrets through the use of dream-sharing technology...\n▶️ Трейлер на YouTube: https://www.youtube.com/results?search_query=Inception+trailer"
        )
        # Перевірка, чи була надіслана фотографія (постер фільму)
        bot.send_photo.assert_called_with(
            message.chat.id,
            "https://link_to_poster.jpg",
            caption="🎬 Назва: Inception\n📅 Рік: 2010\n⭐ Рейтинг IMDb: 8.8\n🎥 Режисер: Christopher Nolan\n🎭 Актори: Leonardo DiCaprio, Joseph Gordon-Levitt\n📚 Жанр: Action, Sci-Fi\n📝 Опис: A thief who steals corporate secrets through the use of dream-sharing technology...\n▶️ Трейлер на YouTube: https://www.youtube.com/results?search_query=Inception+trailer"
        )

    @patch('bot.requests.get')  # Мокаємо HTTP-запит для іншої команди
    def test_search_movies(self, mock_get):
        # Налаштовуємо мок для відповіді від OMDb API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Response": "True",
            "Search": [
                {"Title": "Inception", "Year": "2010", "Poster": "https://link_to_poster.jpg"},
                {"Title": "Interstellar", "Year": "2014", "Poster": "https://link_to_poster2.jpg"}
            ]
        }
        mock_get.return_value = mock_response

        # Симулюємо повідомлення користувача
        message = MagicMock()
        message.text = '/search sci-fi'
        message.from_user.id = 12345
        message.chat.id = 12345

        # Викликаємо команду /search
        bot.search_movies(message)

        # Перевірка, чи був надісланий правильний текст для кожного фільму
        bot.reply_to.assert_any_call(
            message,
            "🎬 Назва: Inception\n📅 Рік: 2010\n📚 Жанр: Sci-Fi\n"
        )
        bot.reply_to.assert_any_call(
            message,
            "🎬 Назва: Interstellar\n📅 Рік: 2014\n📚 Жанр: Sci-Fi\n"
        )

    def test_language_change(self):
        # Симулюємо зміну мови на англійську
        message = MagicMock()
        message.text = '/lang_en'
        message.from_user.id = 12345
        bot.set_language_english(message)
        
        # Перевіряємо, чи змінилася мова на англійську
        self.assertEqual(bot.user_languages[12345], 'en')
        
        # Перевірка відповіді
        bot.reply_to.assert_called_with(message, "Language set to English.")
        
        # Тепер змінюємо мову на українську
        bot.set_language_ukrainian(message)
        
        # Перевіряємо, чи змінилася мова на українську
        self.assertEqual(bot.user_languages[12345], 'uk')
        
        # Перевірка відповіді
        bot.reply_to.assert_called_with(message, "Мову змінено на українську.")

if __name__ == '__main__':
    unittest.main()
