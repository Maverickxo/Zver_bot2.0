import re


def extract_values_delivery(message_zakaz):
    pattern1 = [
        r"Обычная: (\d+)р.",
        r"Santa Claus delivery: (\d+)р.",
        r"Обычная \+ ✅страховка✅: (\d+)р.",
        r"Экспресс: (\d+)р.",
        r"Экспресс \+ ✅страховка✅: (\d+)р."
    ]
    pattern2 = r"Итоговая стоимость доставки: (\d+) руб."

    match2 = re.search(pattern2, message_zakaz)
    amount = None

    if match2:
        amount = int(match2.group(1))
    else:
        for pat in pattern1:
            match = re.search(pat, message_zakaz)
            if match:
                if pat == r"Santa Claus delivery: (\d+)р.":
                    amount = 800  # Установка стандартной стоимости для Santa Claus delivery
                else:
                    amount = int(match.group(1))
                break

    return amount

