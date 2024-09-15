import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from rich.console import Group

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    display_languages,
    get_input,
    translate_text,
    process_translations,
    LANGUAGES,
    create_ascii_title,
    sort_colors,
    is_valid_language,
    is_non_empty,
    parse_languages,
    are_valid_languages,
)


class TestTranslator(unittest.TestCase):

    @patch("rich.console.Console.print")
    def test_display_languages(self, mock_print):
        display_languages(LANGUAGES)
        mock_print.assert_called()

    @patch("rich.console.Console.input", side_effect=["English", "Invalid", "Spanish"])
    @patch("rich.console.Console.print")
    def test_get_input(self, mock_print, mock_input):
        result = get_input("Test prompt", lambda x: x in LANGUAGES)
        self.assertEqual(result, "English")
        result = get_input("Test prompt", lambda x: x in LANGUAGES)
        self.assertEqual(result, "Spanish")

    @patch("main.translate")
    def test_translate_text(self, mock_translate):
        mock_translate.return_value = "Hola, mundo!"

        # Test with full language names
        result = translate_text("Hello, world!", "English", "Spanish")
        self.assertEqual(result, "Hola, mundo!")
        mock_translate.assert_called_with("Hello, world!", "en", "es")

        # Test with language codes
        result = translate_text("Hello, world!", "en", "es")
        self.assertEqual(result, "Hola, mundo!")
        mock_translate.assert_called_with("Hello, world!", "en", "es")

        # Test with mixed input (full name and code)
        result = translate_text("Hello, world!", "English", "es")
        self.assertEqual(result, "Hola, mundo!")
        mock_translate.assert_called_with("Hello, world!", "en", "es")

        # Test with invalid language
        with self.assertRaises(ValueError):
            translate_text("Hello, world!", "InvalidLanguage", "Spanish")

        # Test with invalid language code
        with self.assertRaises(ValueError):
            translate_text("Hello, world!", "en", "invalid")

    @patch("main.translate_text")
    @patch("rich.progress.Progress.add_task")
    @patch("rich.progress.Progress.update")
    def test_process_translations(
        self, mock_update, mock_add_task, mock_translate_text
    ):
        mock_translate_text.side_effect = ["Hola, mundo!", "Bonjour, le monde!"]
        results = process_translations(
            "Hello, world!", "English", ["Spanish", "French"]
        )
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], "Spanish")
        self.assertEqual(results[0][1], "Hola, mundo!")
        self.assertIsInstance(results[0][2], float)
        self.assertEqual(results[1][0], "French")
        self.assertEqual(results[1][1], "Bonjour, le monde!")
        self.assertIsInstance(results[1][2], float)

    def test_create_ascii_title(self):
        title = create_ascii_title("Cute Translator")
        self.assertIsInstance(title, Group)
        self.assertGreater(len(title.renderables), 0)

    def test_sort_colors(self):
        colors = ["#FF0000", "#00FF00", "#0000FF"]
        sorted_colors = sort_colors(colors)
        self.assertEqual(len(sorted_colors), len(colors))
        self.assertIsInstance(sorted_colors, list)

    def test_is_valid_language(self):
        self.assertTrue(is_valid_language("English"))
        self.assertTrue(is_valid_language("en"))
        self.assertFalse(is_valid_language("InvalidLanguage"))

    def test_are_valid_languages(self):
        self.assertTrue(are_valid_languages("English, Spanish, French"))
        self.assertTrue(are_valid_languages("en, es, fr"))
        self.assertFalse(are_valid_languages("English, InvalidLanguage, French"))

    def test_is_non_empty(self):
        self.assertTrue(is_non_empty("Hello"))
        self.assertFalse(is_non_empty(""))
        self.assertFalse(is_non_empty("  "))

    def test_parse_languages(self):
        result = parse_languages("English, French, German")
        self.assertEqual(result, ["English", "French", "German"])
        result = parse_languages("English,French,  German  ")
        self.assertEqual(result, ["English", "French", "German"])
        result = parse_languages("")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
