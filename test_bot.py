import unittest
from telebot import types
from bot import get_user_first_name, start_keyboard, language_keyboard  # Імпортуємо функції, які будемо тестувати

class TestBotLogic(unittest.TestCase):

    def test_get_user_first_name(self):
        # Симулюємо повідомлення від користувача
        class MockMessage:
            def __init__(self, first_name=None):
                self.from_user = type('MockUser', (), {"first_name": first_name})

        # Перевіряємо функцію для різних випадків
        self.assertEqual(get_user_first_name(MockMessage("John")), "John")
        self.assertEqual(get_user_first_name(MockMessage(None)), "друг")

    def test_start_keyboard(self):
        # Викликаємо функцію для створення клавіатури
        keyboard = start_keyboard()
        self.assertIsInstance(keyboard, types.ReplyKeyboardMarkup)
        
        # Збираємо всі кнопки та шукаємо кнопку '/help'
        buttons = [button['text'] for row in keyboard.keyboard for button in row if isinstance(button, dict)]
        
        # Перевіряємо, чи містить клавіатура кнопку '/help'
        self.assertIn("/help", buttons)

    def test_language_keyboard(self):
        # Перевірка наявності кнопок вибору мови
        keyboard = language_keyboard()
        self.assertIsInstance(keyboard, types.ReplyKeyboardMarkup)
        
        # Перевіряємо, чи є кнопки '/lang_en' та '/lang_uk'
        buttons = [button['text'] for row in keyboard.keyboard for button in row if isinstance(button, dict)]

        self.assertIn("/lang_en", buttons)
        self.assertIn("/lang_uk", buttons)

    def test_encoded_query(self):
        from urllib.parse import quote
        self.assertEqual(quote("Some Movie"), "Some%20Movie")
        self.assertEqual(quote("Тест"), "%D0%A2%D0%B5%D1%81%D1%82")

if __name__ == '__main__':
    unittest.main()
