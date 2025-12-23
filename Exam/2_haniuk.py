#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import colorama
from colorama import Fore, Style
import asyncio
from googletrans import Translator, LANGUAGES
import sys

# Ініціалізація Colorama
colorama.init(autoreset=True)

# Мова інтерфейсу
lang = "tr"

# Базові тексти англійською (як оригінал для перекладу)
original_texts = {
    "title": "Interface language",
    "enter_numbers": "Enter three integers a, b, c: ",
    "numbers": "Numbers",
    "are_triple": "are a Pythagorean triple",
    "are_not_triple": "are not a Pythagorean triple",
    "because": "Because",
    "result_is": "The result is",
    "error_value": "Error: Please enter three integers separated by spaces.",
    "error_general": "An error occurred"
}

async def translate_text_async(text, dest_lang):
    """Асинхронно перекладає текст на вказану мову"""
    try:
        if dest_lang == "en":
            return text
        
        translator = Translator()
        result = await translator.translate(text, dest=dest_lang)
        return result.text
    except Exception as e:
        print(f"{Fore.YELLOW}Translation warning: {e}{Style.RESET_ALL}")
        return text

async def get_translated_texts_async(language):
    """Асинхронно повертає словник перекладених текстів"""
    translated = {}
    for key, text in original_texts.items():
        translated[key] = await translate_text_async(text, language)
    return translated

def is_pythagorean_triple(a, b, c):
    """Перевіряє, чи є три числа трійкою Піфагора"""
    numbers = sorted([a, b, c])
    x, y, z = numbers[0], numbers[1], numbers[2]
    return x*x + y*y == z*z

def format_equation(a, b, c):
    """Форматує рівняння для виводу"""
    numbers = sorted([a, b, c])
    x, y, z = numbers[0], numbers[1], numbers[2]
    
    if z == a:
        return f"{b}²+{c}²={a}²"
    elif z == b:
        return f"{a}²+{c}²={b}²"
    else:
        return f"{a}²+{b}²={c}²"

async def main_async():
    try:
        # Асинхронно отримуємо переклади
        texts = await get_translated_texts_async(lang)
        
        # Отримуємо назву мови
        language_name = LANGUAGES.get(lang, f"Unknown ({lang})").title()
        
        print(f"{Fore.CYAN}{texts['title']}: {language_name}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}")
        
        # Введення даних
        input_str = input(f"{texts['enter_numbers']}")
        a, b, c = map(int, input_str.split())
        
        # Перевірка на трійку Піфагора
        if is_pythagorean_triple(a, b, c):
            equation = format_equation(a, b, c)
            numbers_sorted = sorted([a, b, c])
            result = numbers_sorted[0]**2 + numbers_sorted[1]**2
            z_squared = numbers_sorted[2]**2
            
            print(f"\n{texts['numbers']} {Fore.RED}{a}, {b}, {c}{Style.RESET_ALL}, "
                  f"{Fore.CYAN}{texts['are_triple']}{Style.RESET_ALL}. "
                  f"{texts['because']} {equation} ({result}={z_squared}).")
        else:
            print(f"\n{texts['numbers']} {Fore.RED}{a}, {b}, {c}{Style.RESET_ALL}, "
                  f"{Fore.CYAN}{texts['are_not_triple']}{Style.RESET_ALL}.")
            
    except ValueError:
        print(f"{Fore.RED}{texts['error_value']}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}{texts['error_general']}: {e}{Style.RESET_ALL}")

def main():
    """Головна функція, яка запускає асинхронний код"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()