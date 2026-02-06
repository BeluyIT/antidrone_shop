"""
Management command to load test data for the antidrone catalog.
"""

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, Product


# Transliteration table for Ukrainian
TRANSLIT_TABLE = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e',
    'є': 'ie', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i',
    'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
    'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'iu', 'я': 'ia',
    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E',
    'Є': 'Ie', 'Ж': 'Zh', 'З': 'Z', 'И': 'Y', 'І': 'I', 'Ї': 'I', 'Й': 'I',
    'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
    'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch',
    'Ш': 'Sh', 'Щ': 'Shch', 'Ь': '', 'Ю': 'Iu', 'Я': 'Ia',
}


def transliterate(text):
    """Transliterate Ukrainian text to Latin characters."""
    result = []
    for char in text:
        result.append(TRANSLIT_TABLE.get(char, char))
    return ''.join(result)


def make_slug(text):
    """Create a slug from Ukrainian text."""
    return slugify(transliterate(text))


# Categories structure
CATEGORIES = {
    'Антени': {
        'slug': 'anteny',
        'description': 'Антени для систем виявлення та протидії дронам',
        'children': [
            {'name': 'Directional', 'slug': 'directional', 'description': 'Спрямовані антени високої потужності'},
            {'name': 'Omni-Directional', 'slug': 'omni', 'description': 'Всеспрямовані антени для 360° покриття'},
            {'name': 'Patch', 'slug': 'patch', 'description': 'Патч-антени для компактних систем'},
            {'name': 'Panel', 'slug': 'panel', 'description': 'Панельні антени для стаціонарних систем'},
        ]
    },
    'Модулі': {
        'slug': 'moduli',
        'description': 'Електронні модулі для антидрон систем',
        'children': [
            {'name': 'RF Детектори', 'slug': 'rf-detektory', 'description': 'Модулі для виявлення радіочастотних сигналів'},
            {'name': 'Глушителі', 'slug': 'glushiteli', 'description': 'Модулі для подавлення сигналів керування'},
            {'name': 'SDR Модулі', 'slug': 'sdr-moduli', 'description': 'Software Defined Radio модулі'},
            {'name': 'Підсилювачі', 'slug': 'pidsylyuvachi', 'description': 'Підсилювачі потужності сигналу'},
            {'name': 'DC/DC', 'slug': 'dc-dc', 'description': 'DC/DC перетворювачі для живлення модулів'},
        ]
    },
    'Портативні детектори': {
        'slug': 'portatyvni-detektory',
        'description': 'Портативні детектори для швидкого виявлення БПЛА',
        'children': [],
    },
    'Антидронові рушниці': {
        'slug': 'antydronovi-rushnytsi',
        'description': 'Ручні комплекси подавлення та нейтралізації БПЛА',
        'children': [],
    },
}


# Products data
PRODUCTS = {
    'directional': [
        {
            'name': 'Yagi Antenna 2.4GHz 18dBi',
            'sku': 'ANT-2400-Y18',
            'description': 'Спрямована антена для виявлення дронів на частоті 2.4 GHz',
            'specs': {
                'Частота': '2400 MHz',
                'Коефіцієнт підсилення': '18 dBi',
                'Потужність': '50W',
                'Імпеданс': '50 Ohm',
                'Роз\'єм': 'N-type Female',
                'Розміри': '920×110×80 мм',
                'Вага': '1.2 кг',
                'Матеріал': 'Алюміній',
                'IP рейтинг': 'IP65',
            },
            'price_range': (2500, 3500),
        },
        {
            'name': 'Yagi Antenna 5.8GHz 24dBi',
            'sku': 'ANT-5800-Y24',
            'description': 'Високоспрямована антена для частоти 5.8 GHz з максимальним підсиленням',
            'specs': {
                'Частота': '5800 MHz',
                'Коефіцієнт підсилення': '24 dBi',
                'Потужність': '100W',
                'Імпеданс': '50 Ohm',
                'Роз\'єм': 'N-type Female',
                'Розміри': '680×90×70 мм',
                'Вага': '0.9 кг',
                'Матеріал': 'Алюміній анодований',
                'IP рейтинг': 'IP67',
            },
            'price_range': (3800, 4800),
        },
        {
            'name': 'Directional Log-Periodic 900MHz',
            'sku': 'ANT-0900-LP12',
            'description': 'Логоперіодична антена для низькочастотного діапазону 900 MHz',
            'specs': {
                'Частота': '850-960 MHz',
                'Коефіцієнт підсилення': '12 dBi',
                'Потужність': '200W',
                'Імпеданс': '50 Ohm',
                'Роз\'єм': 'N-type Female',
                'Розміри': '1200×400×120 мм',
                'Вага': '2.5 кг',
                'Матеріал': 'Нержавіюча сталь',
                'IP рейтинг': 'IP66',
            },
            'price_range': (5500, 7000),
            'is_popular': True,
        },
    ],
    'omni': [
        {
            'name': 'Omni Antenna 2.4GHz 8dBi',
            'sku': 'ANT-2400-O8',
            'description': 'Всеспрямована антена для кругового покриття на частоті 2.4 GHz',
            'specs': {
                'Частота': '2400-2500 MHz',
                'Коефіцієнт підсилення': '8 dBi',
                'Потужність': '50W',
                'Імпеданс': '50 Ohm',
                'Роз\'єм': 'N-type Male',
                'Розміри': '400×25 мм',
                'Вага': '0.3 кг',
                'Матеріал': 'Фібергласс',
                'IP рейтинг': 'IP65',
            },
            'price_range': (1200, 1800),
        },
        {
            'name': 'Omni Antenna 5.8GHz 12dBi',
            'sku': 'ANT-5800-O12',
            'description': 'Потужна всеспрямована антена для діапазону 5.8 GHz',
            'specs': {
                'Частота': '5725-5875 MHz',
                'Коефіцієнт підсилення': '12 dBi',
                'Потужність': '30W',
                'Імпеданс': '50 Ohm',
                'Роз\'єм': 'RP-SMA Female',
                'Розміри': '350×22 мм',
                'Вага': '0.25 кг',
                'Матеріал': 'Фібергласс',
                'IP рейтинг': 'IP54',
            },
            'price_range': (1500, 2200),
            'is_new': True,
        },
        {
            'name': 'Dual-Band Omni 2.4/5.8GHz',
            'sku': 'ANT-DUAL-O10',
            'description': 'Двохдіапазонна всеспрямована антена для комплексних систем',
            'specs': {
                'Частота': '2400-2500 / 5725-5875 MHz',
                'Коефіцієнт підсилення': '10/12 dBi',
                'Потужність': '50W',
                'Імпеданс': '50 Ohm',
                'Роз\'єм': 'N-type Female',
                'Розміри': '550×30 мм',
                'Вага': '0.45 кг',
                'Матеріал': 'Алюміній + Фібергласс',
                'IP рейтинг': 'IP67',
            },
            'price_range': (2800, 3600),
            'is_popular': True,
        },
    ],
    'patch': [
        {
            'name': 'Patch Antenna 2.4GHz 14dBi',
            'sku': 'ANT-2400-P14',
            'description': 'Компактна патч-антена для монтажу на стіну або щогла',
            'specs': {
                'Частота': '2400-2483 MHz',
                'Коефіцієнт підсилення': '14 dBi',
                'Потужність': '25W',
                'Імпеданс': '50 Ohm',
                'Роз\'єм': 'SMA Female',
                'Розміри': '200×200×40 мм',
                'Вага': '0.6 кг',
                'Матеріал': 'ABS пластик',
                'IP рейтинг': 'IP55',
            },
            'price_range': (1800, 2400),
        },
        {
            'name': 'Patch Antenna 433MHz 6dBi',
            'sku': 'ANT-0433-P6',
            'description': 'Патч-антена для діапазону 433 MHz (дистанційне керування)',
            'specs': {
                'Частота': '430-440 MHz',
                'Коефіцієнт підсилення': '6 dBi',
                'Потужність': '50W',
                'Імпеданс': '50 Ohm',
                'Роз\'єм': 'SMA Male',
                'Розміри': '350×350×60 мм',
                'Вага': '1.1 кг',
                'Матеріал': 'Алюміній',
                'IP рейтинг': 'IP65',
            },
            'price_range': (2200, 2900),
            'is_new': True,
        },
    ],
    'panel': [
        {
            'name': 'Panel Antenna 2.4GHz 19dBi',
            'sku': 'ANT-2400-PN19',
            'description': 'Панельна секторна антена для стаціонарних систем',
            'specs': {
                'Частота': '2400-2500 MHz',
                'Коефіцієнт підсилення': '19 dBi',
                'Потужність': '100W',
                'Імпеданс': '50 Ohm',
                'Роз\'єм': 'N-type Female',
                'Розміри': '350×350×45 мм',
                'Вага': '2.2 кг',
                'Матеріал': 'Алюміній',
                'IP рейтинг': 'IP66',
                'Кут випромінювання': '60°×15°',
            },
            'price_range': (4200, 5500),
            'is_popular': True,
        },
        {
            'name': 'Panel Antenna 5.8GHz 23dBi',
            'sku': 'ANT-5800-PN23',
            'description': 'Високопотужна панельна антена для діапазону 5.8 GHz',
            'specs': {
                'Частота': '5150-5850 MHz',
                'Коефіцієнт підсилення': '23 dBi',
                'Потужність': '50W',
                'Імпеданс': '50 Ohm',
                'Роз\'єм': 'N-type Female',
                'Розміри': '300×300×35 мм',
                'Вага': '1.8 кг',
                'Матеріал': 'Алюміній анодований',
                'IP рейтинг': 'IP67',
                'Кут випромінювання': '45°×12°',
            },
            'price_range': (4800, 6200),
        },
    ],
    'rf-detektory': [
        {
            'name': 'RF Detector Module 100MHz-6GHz',
            'sku': 'RFD-6000-PRO',
            'description': 'Широкосмуговий RF детектор для виявлення сигналів дронів',
            'specs': {
                'Діапазон частот': '100 MHz - 6 GHz',
                'Чутливість': '-90 dBm',
                'Динамічний діапазон': '80 dB',
                'Інтерфейс': 'USB 3.0 / Ethernet',
                'Живлення': '12V DC / PoE',
                'Споживання': '15W',
                'Розміри': '180×120×45 мм',
                'Вага': '0.8 кг',
                'Робоча температура': '-20°C до +60°C',
            },
            'price_range': (8500, 11000),
            'is_popular': True,
        },
        {
            'name': 'RF Detector Mini 2.4/5.8GHz',
            'sku': 'RFD-DUAL-MINI',
            'description': 'Компактний RF детектор для основних частот дронів',
            'specs': {
                'Діапазон частот': '2.4 GHz / 5.8 GHz',
                'Чутливість': '-85 dBm',
                'Динамічний діапазон': '60 dB',
                'Інтерфейс': 'UART / SPI',
                'Живлення': '5V DC',
                'Споживання': '2W',
                'Розміри': '60×40×15 мм',
                'Вага': '0.05 кг',
                'Робоча температура': '-10°C до +50°C',
            },
            'price_range': (2500, 3500),
            'is_new': True,
        },
    ],
    'glushiteli': [
        {
            'name': 'Jammer Module 2.4GHz 10W',
            'sku': 'MOD-JAM-2400-10',
            'description': 'Модуль глушіння для діапазону 2.4 GHz',
            'specs': {
                'Частота': '2400-2500 MHz',
                'Вихідна потужність': '10W',
                'Підсилення': '40 dB',
                'Інтерфейс керування': 'RS-485',
                'Живлення': '24V DC',
                'Споживання': '35W',
                'Розміри': '150×100×50 мм',
                'Вага': '0.7 кг',
                'Охолодження': 'Активне (вентилятор)',
            },
            'price_range': (7500, 9500),
        },
        {
            'name': 'Jammer Module 5.8GHz 5W',
            'sku': 'MOD-JAM-5800-5',
            'description': 'Компактний модуль глушіння для діапазону 5.8 GHz',
            'specs': {
                'Частота': '5725-5875 MHz',
                'Вихідна потужність': '5W',
                'Підсилення': '35 dB',
                'Інтерфейс керування': 'TTL',
                'Живлення': '12V DC',
                'Споживання': '20W',
                'Розміри': '120×80×40 мм',
                'Вага': '0.4 кг',
                'Охолодження': 'Пасивне (радіатор)',
            },
            'price_range': (5500, 7000),
        },
        {
            'name': 'Multi-Band Jammer Module',
            'sku': 'MOD-JAM-MULTI-20',
            'description': 'Багатодіапазонний модуль глушіння 433/900/2400/5800 MHz',
            'specs': {
                'Частоти': '433/900/2400/5800 MHz',
                'Вихідна потужність': '5W на канал',
                'Кількість каналів': '4',
                'Інтерфейс керування': 'Ethernet / RS-485',
                'Живлення': '48V DC / PoE+',
                'Споживання': '80W',
                'Розміри': '250×180×80 мм',
                'Вага': '2.5 кг',
                'Охолодження': 'Активне (2 вентилятори)',
            },
            'price_range': (14000, 18000),
            'is_popular': True,
        },
    ],
    'sdr-moduli': [
        {
            'name': 'SDR Transceiver 70MHz-6GHz',
            'sku': 'SDR-6000-TX',
            'description': 'Широкосмуговий SDR трансивер для аналізу та генерації сигналів',
            'specs': {
                'Діапазон частот': '70 MHz - 6 GHz',
                'Смуга пропускання': '56 MHz',
                'АЦП/ЦАП': '12 біт',
                'Інтерфейс': 'USB 3.0',
                'FPGA': 'Xilinx Artix-7',
                'Живлення': 'USB / 5V DC',
                'Споживання': '8W',
                'Розміри': '120×80×25 мм',
                'Вага': '0.3 кг',
            },
            'price_range': (9500, 12500),
            'is_popular': True,
        },
        {
            'name': 'SDR Receiver 24MHz-1.8GHz',
            'sku': 'SDR-1800-RX',
            'description': 'Бюджетний SDR приймач для моніторингу радіочастот',
            'specs': {
                'Діапазон частот': '24 MHz - 1.8 GHz',
                'Смуга пропускання': '3.2 MHz',
                'АЦП': '8 біт',
                'Інтерфейс': 'USB 2.0',
                'Чіпсет': 'RTL2832U + R820T2',
                'Живлення': 'USB',
                'Споживання': '1.5W',
                'Розміри': '85×25×10 мм',
                'Вага': '0.03 кг',
            },
            'price_range': (1200, 1800),
            'is_new': True,
        },
    ],
    'pidsylyuvachi': [
        {
            'name': 'Power Amplifier 2.4GHz 20W',
            'sku': 'AMP-2400-20',
            'description': 'Підсилювач потужності для діапазону 2.4 GHz',
            'specs': {
                'Частота': '2400-2500 MHz',
                'Вихідна потужність': '20W (43 dBm)',
                'Підсилення': '30 dB',
                'Ефективність': '35%',
                'Вхід/Вихід': 'SMA Female',
                'Живлення': '28V DC',
                'Споживання': '60W',
                'Розміри': '140×100×45 мм',
                'Вага': '0.9 кг',
                'Охолодження': 'Радіатор + вентилятор',
            },
            'price_range': (6500, 8500),
        },
        {
            'name': 'Power Amplifier 5.8GHz 10W',
            'sku': 'AMP-5800-10',
            'description': 'Підсилювач потужності для діапазону 5.8 GHz',
            'specs': {
                'Частота': '5725-5875 MHz',
                'Вихідна потужність': '10W (40 dBm)',
                'Підсилення': '25 dB',
                'Ефективність': '30%',
                'Вхід/Вихід': 'SMA Female',
                'Живлення': '24V DC',
                'Споживання': '35W',
                'Розміри': '120×80×40 мм',
                'Вага': '0.6 кг',
                'Охолодження': 'Радіатор',
            },
            'price_range': (5500, 7200),
            'is_new': True,
        },
        {
            'name': 'LNA 100MHz-6GHz 25dB',
            'sku': 'AMP-LNA-6000',
            'description': 'Малошумний підсилювач для приймальних систем',
            'specs': {
                'Частота': '100 MHz - 6 GHz',
                'Підсилення': '25 dB',
                'Коефіцієнт шуму': '1.5 dB',
                'IP3': '+22 dBm',
                'Вхід/Вихід': 'SMA Female',
                'Живлення': '5V DC / Bias-T',
                'Споживання': '0.5W',
                'Розміри': '50×30×15 мм',
                'Вага': '0.04 кг',
            },
            'price_range': (1800, 2500),
            'is_popular': True,
        },
    ],
}


GENERATED_TARGETS = {
    # Antennas (total 50)
    'directional': 48,
    'omni': 48,
    'patch': 48,
    'panel': 48,
    # Modules (total 264)
    'rf-detektory': 52,
    'glushiteli': 52,
    'sdr-moduli': 52,
    'pidsylyuvachi': 54,
    'dc-dc': 54,
    # New root categories
    'portatyvni-detektory': 8,
    'antydronovi-rushnytsi': 8,
}

GENERATED_META = {
    'directional': {
        'base_name': 'Directional Antenna',
        'sku_prefix': 'ANT-DIR',
        'price_range': (2500, 7500),
        'specs': lambda: {
            'Частота': f"{random.choice([433, 900, 2400, 5800])} MHz",
            'Підсилення': f"{random.randint(12, 26)} dBi",
            'Потужність': f"{random.randint(50, 250)} W",
            'Роз\'єм': random.choice(['N-type Female', 'N-type Male']),
            'IP рейтинг': random.choice(['IP65', 'IP66', 'IP67']),
        },
    },
    'omni': {
        'base_name': 'Omni Antenna',
        'sku_prefix': 'ANT-OMNI',
        'price_range': (1200, 3600),
        'specs': lambda: {
            'Частота': random.choice(['2400-2500 MHz', '5725-5875 MHz', '2400/5800 MHz']),
            'Підсилення': f"{random.randint(6, 12)} dBi",
            'Потужність': f"{random.randint(20, 80)} W",
            'Матеріал': random.choice(['Фібергласс', 'Алюміній']),
            'IP рейтинг': random.choice(['IP54', 'IP65', 'IP67']),
        },
    },
    'patch': {
        'base_name': 'Patch Antenna',
        'sku_prefix': 'ANT-PATCH',
        'price_range': (1600, 3200),
        'specs': lambda: {
            'Частота': random.choice(['433 MHz', '900 MHz', '2400 MHz']),
            'Підсилення': f"{random.randint(6, 16)} dBi",
            'Потужність': f"{random.randint(25, 100)} W",
            'Розміри': random.choice(['200×200×40 мм', '250×250×45 мм', '300×300×50 мм']),
            'IP рейтинг': random.choice(['IP55', 'IP65']),
        },
    },
    'panel': {
        'base_name': 'Panel Antenna',
        'sku_prefix': 'ANT-PANEL',
        'price_range': (3500, 6500),
        'specs': lambda: {
            'Частота': random.choice(['2400-2500 MHz', '5150-5850 MHz']),
            'Підсилення': f"{random.randint(18, 24)} dBi",
            'Кут випромінювання': random.choice(['60°×15°', '90°×10°']),
            'Потужність': f"{random.randint(50, 150)} W",
            'IP рейтинг': random.choice(['IP66', 'IP67']),
        },
    },
    'rf-detektory': {
        'base_name': 'RF Detector Module',
        'sku_prefix': 'MOD-RF',
        'price_range': (2800, 6800),
        'specs': lambda: {
            'Діапазон': random.choice(['400-6000 MHz', '700-5800 MHz']),
            'Чутливість': f"-{random.randint(65, 90)} dBm",
            'Інтерфейс': random.choice(['UART', 'SPI', 'I2C']),
            'Живлення': random.choice(['5V', '12V']),
        },
    },
    'glushiteli': {
        'base_name': 'Jammer Module',
        'sku_prefix': 'MOD-JAM',
        'price_range': (5000, 15000),
        'specs': lambda: {
            'Діапазон': random.choice(['900/2400/5800 MHz', '400-6000 MHz']),
            'Потужність': f"{random.randint(10, 50)} W",
            'Охолодження': random.choice(['Пасивне', 'Активне']),
            'Живлення': random.choice(['12V', '24V']),
        },
    },
    'sdr-moduli': {
        'base_name': 'SDR Module',
        'sku_prefix': 'MOD-SDR',
        'price_range': (3500, 12000),
        'specs': lambda: {
            'Частота': random.choice(['1-6000 MHz', '10-3500 MHz']),
            'Інтерфейс': random.choice(['USB 3.0', 'PCIe', 'Ethernet']),
            'Ширина смуги': random.choice(['10 MHz', '20 MHz', '40 MHz']),
            'Живлення': random.choice(['5V', '12V']),
        },
    },
    'pidsylyuvachi': {
        'base_name': 'Power Amplifier',
        'sku_prefix': 'MOD-AMP',
        'price_range': (4200, 11000),
        'specs': lambda: {
            'Частота': random.choice(['900 MHz', '2400 MHz', '5800 MHz']),
            'Підсилення': f"{random.randint(20, 40)} dB",
            'Потужність': f"{random.randint(10, 80)} W",
            'Живлення': random.choice(['12V', '24V']),
        },
    },
    'dc-dc': {
        'base_name': 'DC/DC Converter',
        'sku_prefix': 'MOD-DCDC',
        'price_range': (600, 2200),
        'specs': lambda: {
            'Вхідна напруга': random.choice(['9-36V', '12-48V', '18-72V']),
            'Вихідна напруга': random.choice(['5V', '9V', '12V', '24V']),
            'Потужність': f"{random.randint(30, 200)} W",
            'ККД': f"{random.randint(85, 95)}%",
        },
    },
    'portatyvni-detektory': {
        'base_name': 'Portable Detector',
        'sku_prefix': 'DET-PRT',
        'price_range': (15000, 45000),
        'specs': lambda: {
            'Діапазон': random.choice(['400-6000 MHz', '700-5800 MHz']),
            'Дальність': f"до {random.randint(1, 5)} км",
            'Час роботи': f"{random.randint(2, 8)} год",
            'Живлення': random.choice(['Li-Ion', 'LiFePO4']),
        },
    },
    'antydronovi-rushnytsi': {
        'base_name': 'Anti-Drone Rifle',
        'sku_prefix': 'GUN-AD',
        'price_range': (80000, 180000),
        'specs': lambda: {
            'Діапазони подавлення': random.choice(['900/2400/5800 MHz', '700/900/1800/2400/5800 MHz']),
            'Дальність': f"{random.randint(1, 3)} км",
            'Живлення': random.choice(['АКБ', 'АКБ + мережа']),
            'Маса': f"{random.uniform(3.5, 6.5):.1f} кг",
        },
    },
}


def create_generated_products(category, target_count):
    meta = GENERATED_META[category.slug]
    base_name = meta['base_name']
    sku_prefix = meta['sku_prefix']
    price_range = meta['price_range']
    specs_builder = meta['specs']

    for index in range(1, target_count + 1):
        name = f"{base_name} {index:02d}"
        price = Decimal(random.randint(*price_range))
        old_price = None
        if random.random() < 0.25:
            discount_percent = random.randint(15, 30)
            old_price = price * Decimal(100 + discount_percent) / Decimal(100)
            old_price = old_price.quantize(Decimal('1'))

        is_popular = random.random() < 0.3
        is_new = random.random() < 0.25

        Product.objects.create(
            category=category,
            name=name,
            slug=f"{make_slug(base_name)}-{index:02d}",
            sku=f"{sku_prefix}-{index:03d}",
            description=f"{base_name} для тестування каталогу",
            full_description=format_full_description(
                f"{base_name} для тестування каталогу",
                specs_builder()
            ),
            price=price,
            old_price=old_price,
            is_available=True,
            is_popular=is_popular,
            is_new=is_new,
        )

def format_full_description(description, specs):
    """Format full product description with specifications."""
    lines = [description, '', 'Технічні характеристики:', '']
    for key, value in specs.items():
        lines.append(f'- {key}: {value}')
    return '\n'.join(lines)


class Command(BaseCommand):
    help = 'Load test data for the antidrone catalog'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Only clear existing data without creating new',
        )

    def handle(self, *args, **options):
        clear_only = options.get('clear', False)

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Product.objects.all().delete()
        self.stdout.write(self.style.WARNING('Deleted all products'))
        Category.objects.all().delete()
        self.stdout.write(self.style.WARNING('Deleted all categories'))

        if clear_only:
            self.stdout.write(self.style.SUCCESS('Data cleared successfully!'))
            return

        # Create categories
        self.stdout.write('\nCreating categories...')
        category_map = {}

        for parent_name, parent_data in CATEGORIES.items():
            parent_cat = Category.objects.create(
                name=parent_name,
                slug=parent_data['slug'],
                description=parent_data['description'],
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS(f'Created category: {parent_name}'))
            category_map[parent_data['slug']] = parent_cat

            for child_data in parent_data['children']:
                child_cat = Category.objects.create(
                    name=child_data['name'],
                    slug=child_data['slug'],
                    description=child_data['description'],
                    parent=parent_cat,
                    is_active=True,
                )
                category_map[child_data['slug']] = child_cat
                self.stdout.write(self.style.SUCCESS(f'  Created subcategory: {child_data["name"]}'))

        # Rebuild MPTT tree
        Category.objects.rebuild()

        # Create products (static list)
        self.stdout.write('\nCreating products...')
        product_count = 0

        for category_slug, products in PRODUCTS.items():
            category = category_map.get(category_slug)
            if not category:
                self.stdout.write(self.style.ERROR(f'Category not found: {category_slug}'))
                continue

            for product_data in products:
                price = Decimal(random.randint(*product_data['price_range']))

                # Calculate old_price for some products (30% chance)
                old_price = None
                if random.random() < 0.3:
                    discount_percent = random.randint(20, 30)
                    old_price = price * Decimal(100 + discount_percent) / Decimal(100)
                    old_price = old_price.quantize(Decimal('1'))

                # Determine flags
                is_popular = product_data.get('is_popular', random.random() < 0.3)
                is_new = product_data.get('is_new', random.random() < 0.2)

                # Create product
                product = Product.objects.create(
                    category=category,
                    name=product_data['name'],
                    slug=make_slug(product_data['name']),
                    sku=product_data['sku'],
                    description=product_data['description'],
                    full_description=format_full_description(
                        product_data['description'],
                        product_data['specs']
                    ),
                    price=price,
                    old_price=old_price,
                    is_available=True,
                    is_popular=is_popular,
                    is_new=is_new,
                )
                product_count += 1

                flags = []
                if is_popular:
                    flags.append('popular')
                if is_new:
                    flags.append('new')
                if old_price:
                    flags.append('sale')
                flags_str = f' [{", ".join(flags)}]' if flags else ''

                self.stdout.write(
                    self.style.SUCCESS(f'Created product: {product.name} - {price} грн{flags_str}')
                )

        # Create generated products to hit target counts per category
        self.stdout.write('\nGenerating additional products...')
        for category_slug, target_total in GENERATED_TARGETS.items():
            category = category_map.get(category_slug)
            if not category:
                self.stdout.write(self.style.ERROR(f'Category not found for generation: {category_slug}'))
                continue
            existing_count = Product.objects.filter(category=category).count()
            to_create = max(target_total - existing_count, 0)
            if to_create:
                create_generated_products(category, to_create)
                product_count += to_create
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Generated {to_create} products for {category.name} (total {target_total})'
                    )
                )

        self.stdout.write('')
        total_categories = Category.objects.count()
        total_products = Product.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {total_categories} categories and {total_products} products!'
        ))
