import outputformat as ouf
from translate import translate
from pyfiglet import Figlet
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.text import Text
from rich import print as rprint
from functools import partial
from typing import List, Tuple, Callable
import time
import colorsys
from rich.style import Style
from rich.console import Group
from itertools import cycle

# Catppuccin colors
COLORS = {
    "rosewater": "#f5e0dc",
    "flamingo": "#f2cdcd",
    "pink": "#f5c2e7",
    "mauve": "#cba6f7",
    "red": "#f38ba8",
    "maroon": "#eba0ac",
    "peach": "#fab387",
    "yellow": "#f9e2af",
    "green": "#a6e3a1",
    "teal": "#94e2d5",
    "sky": "#89dceb",
    "sapphire": "#74c7ec",
    "blue": "#89b4fa",
    "lavender": "#b4befe",
    "text": "#cdd6f4",
    "subtext1": "#bac2de",
    "subtext0": "#a6adc8",
    "overlay2": "#9399b2",
    "overlay1": "#7f849c",
    "overlay0": "#6c7086",
    "surface2": "#585b70",
    "surface1": "#45475a",
    "surface0": "#313244",
    "base": "#1e1e2e",
    "mantle": "#181825",
    "crust": "#11111b",
}

console = Console()

LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Chinese": "zh",
    "Japanese": "ja",
    "Hebrew": "he",
    "Arabic": "ar",
    "Hindi": "hi",
    "Bengali": "bn",
    "Punjabi": "pa",
    "Malayalam": "ml",
    "Tamil": "ta",
    "Korean": "ko",
    "Dutch": "nl",
    "Turkish": "tr",
    "Polish": "pl",
    "Swedish": "sv",
    "Danish": "da",
    "Norwegian": "no",
    "Finnish": "fi",
    "Greek": "el",
    "Thai": "th",
    "Vietnamese": "vi",
    "Indonesian": "id",
    "Malay": "ms",
}


def create_ascii_title(text: str) -> Group:
    width = console.width
    figlet = Figlet(font="speed", width=width)
    ascii_art = figlet.renderText(text)
    gradient = list(COLORS.values())[: len(ascii_art.splitlines())]
    colored_lines = [
        Text(line.center(width), style=color)
        for line, color in zip(ascii_art.splitlines(), gradient)
    ]
    return Group(*colored_lines)


def sort_colors(colors: List[str]) -> List[str]:
    return sorted(
        colors,
        key=lambda c: colorsys.rgb_to_hsv(
            *[int(c.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)]
        ),
    )


def display_languages(languages: dict) -> None:
    language_list = [f"{name} ({code})" for name, code in languages.items()]

    console.print(
        Panel(
            "\n".join(language_list),
            title="Languages",
            border_style=COLORS["sapphire"],
            expand=False,
        )
    )


def get_input(prompt: str, validator: Callable[[str], bool]) -> str:
    while True:
        console.print(
            Panel(
                prompt,
                style=f"bold {COLORS['peach']}",
                expand=False,
            )
        )
        user_input = console.input(f"[{COLORS['green']}]--> ").strip()
        if validator(user_input):
            return user_input
        console.print(
            f"[{COLORS['red']}]Invalid input. Please try again.[/{COLORS['red']}]"
        )


def is_valid_language(lang: str) -> bool:
    return (
        lang.lower() in [l.lower() for l in LANGUAGES.keys()]
        or lang.lower() in LANGUAGES.values()
    )


def are_valid_languages(langs: str) -> bool:
    return all(is_valid_language(lang.strip()) for lang in langs.split(","))


def is_non_empty(text: str) -> bool:
    return bool(text.strip())


def parse_languages(langs: str) -> List[str]:
    return [lang.strip() for lang in langs.split(",") if lang.strip()]


def translate_text(text: str, src_lang: str, dest_lang: str) -> str:
    try:
        src_code = LANGUAGES.get(src_lang) or src_lang.lower()
        dest_code = LANGUAGES.get(dest_lang) or dest_lang.lower()

        if src_code not in LANGUAGES.values() or dest_code not in LANGUAGES.values():
            raise ValueError(
                f"Invalid language: {src_lang if src_code not in LANGUAGES.values() else dest_lang}"
            )

        return translate(text, src_code, dest_code)
    except ValueError as e:
        raise e
    except Exception as e:
        raise RuntimeError(f"Translation error: {str(e)}")


def create_gradient_bar():
    gradient_colors = [
        COLORS[color] for color in ["blue", "sapphire", "sky", "teal", "green"]
    ]
    return BarColumn(
        bar_width=None,
        style=Style(color=gradient_colors[0]),
        complete_style=Style(color=gradient_colors[-1]),
        finished_style=Style(color=gradient_colors[-1]),
        pulse_style=Style(color=gradient_colors[1]),
    )


def process_translations(
    text: str, src_lang: str, dest_langs: List[str]
) -> List[Tuple[str, str, float]]:
    results = []
    total_langs = len(dest_langs)

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        create_gradient_bar(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[progress.remaining]{task.remaining}s"),
    )

    with progress:
        overall_task = progress.add_task(
            "[bold cyan]Overall progress", total=total_langs
        )
        translation_task = progress.add_task(
            "[bold magenta]Translating", total=100, visible=False
        )

        for i, dest_lang in enumerate(dest_langs, 1):
            progress.update(translation_task, visible=True, completed=0)
            full_lang_name = next(
                (name for name, code in LANGUAGES.items() if code == dest_lang.lower()),
                dest_lang,
            )
            progress.update(
                overall_task, description=f"[green]Translating to {full_lang_name}"
            )

            try:
                start_time = time.time()
                translated = translate_text(text, src_lang, dest_lang)
                end_time = time.time()
                translation_time = end_time - start_time

                progress.update(translation_task, completed=100)

                results.append((full_lang_name, translated, translation_time))
            except (ValueError, RuntimeError) as e:
                results.append((full_lang_name, str(e), 0))
            finally:
                progress.update(overall_task, advance=1)
                progress.update(translation_task, visible=False)

    return results


def display_results(results: List[Tuple[str, str, float]]) -> None:
    color_cycle = cycle(["mauve", "pink", "rosewater", "flamingo", "peach", "yellow"])
    for lang, text, translation_time in results:
        color = next(color_cycle)
        console.print(
            Panel(
                Group(
                    Text(text, style=COLORS["text"]),
                    Text(
                        f"Translation time: {translation_time:.2f} seconds",
                        style=COLORS["subtext1"],
                    ),
                ),
                title=f"Translation to {lang}",
                border_style=COLORS[color],
                expand=False,
            )
        )


def main() -> None:
    title = create_ascii_title("Cute Translator")
    console.print(title)
    display_languages(LANGUAGES)

    get_language = partial(get_input, validator=is_valid_language)
    get_languages = partial(get_input, validator=are_valid_languages)
    src_lang = get_language("Enter Your Source Language Below")
    dest_langs = get_languages(
        "Enter Your Destination Language(s) Below (separate multiple languages with commas)"
    )
    text_to_translate = get_input(
        "Enter The Text You Wish To Translate", validator=is_non_empty
    )

    dest_lang_list = parse_languages(dest_langs)
    results = process_translations(text_to_translate, src_lang, dest_lang_list)
    display_results(results)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Translation cancelled by user.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {str(e)}[/bold red]")
