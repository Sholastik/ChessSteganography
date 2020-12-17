import argparse
import os
from random import shuffle, randint, choice

from PIL import Image

# Кодировка символов
chars_encoding = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6,
                  'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13,
                  'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19, 'U': 20,
                  'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25, '.': 26, ',': 27,
                  '!': 28, '?': 29, ' ': 30, '\n': 31, '0': 32, '1': 33, '2': 34,
                  '3': 35, '4': 36, '5': 37, '6': 38, '7': 39, '8': 40, '9': 41,
                  'А': 0, 'Б': 42, 'В': 1, 'Г': 43, 'Д': 44, 'Е': 4, 'Ё': 45,
                  'Ж': 46, 'З': 47, 'И': 48, 'Й': 49, 'К': 10, 'Л': 50, 'М': 12,
                  'Н': 7, 'О': 14, 'П': 51, 'Р': 15, 'С': 2, 'Т': 19, 'У': 52,
                  'Ф': 53, 'Х': 23, 'Ц': 54, 'Ч': 55, 'Ш': 56, 'Щ': 57, 'Ъ': 58,
                  'Ы': 59, 'Ь': 60, 'Э': 61, 'Ю': 62, 'Я': 63}
chars_decoding = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H',
                  8: 'I', 9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O',
                  15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V',
                  22: 'W', 23: 'X', 24: 'Y', 25: 'Z', 26: '.', 27: ',', 28: '!',
                  29: '?', 30: ' ', 31: '\n', 32: '0', 33: '1', 34: '2', 35: '3',
                  36: '4', 37: '5', 38: '6', 39: '7', 40: '8', 41: '9', 42: 'Б',
                  43: 'Г', 44: 'Д', 45: 'Ё', 46: 'Ж', 47: 'З', 48: 'И', 49: 'Й',
                  50: 'Л', 51: 'П', 52: 'У', 53: 'Ф', 54: 'Ц', 55: 'Ч', 56: 'Ш',
                  57: 'Щ', 58: 'Ъ', 59: 'Ы', 60: 'Ь', 61: 'Э', 62: 'Ю', 63: 'Я'}

# Значения (длины последовательностей из единиц), кодируемые шахматными фигурами
chess_encoding = sorted(
    {1: ["pawn", "king", "bishop"], 2: ["rook"], 3: ["knight"]}.items(),
    reverse=True
)
chess_decoding = {
    "pawn": 1, "king": 1, "bishop": 1, "rook": 2, "knight": 3
}

parser = argparse.ArgumentParser(description="Convert text to steganography images")
parser.add_argument("message", type=str)
parser.add_argument("path", type=str)
parser.add_argument("key", type=str)
parser.add_argument("--step", type=int, default=3)

args = parser.parse_args()

print("Checking arguments")
if len(args.key) != 6:
    raise argparse.ArgumentError("Length of key is not the same length as character")

if args.step & (args.step - 1) == 0:
    raise argparse.ArgumentError("Step is the power of two")
print("Arguments: Ok")
# Ключ, используемый для шифрования послания. Длина ключа должна быть равна длине одного символа
ORIGIN = int(args.key, base=2)
KEY = int(ORIGIN)

print("Loading base")
# Считывание изображения шахматной доски
base = Image.open("images/base.png")
print("Base: Ok")
# Координаты первой клетки и размеры клетки
left, top = 20, 20
width, height = 45, 45

# Считывание изображений шахматных фигур
print("Loading pieces")
pieces = {}
for item in ("bishop", "rook", "knight", "king", "queen", "pawn"):
    wh = Image.open(f"images/black-{item}.png")
    wh.thumbnail((width, height))
    white = Image.new("RGBA", (width, height), "black")
    white.paste(wh, (0, 0), wh)

    bl = Image.open(f"images/white-{item}.png")
    bl.thumbnail((width, height))
    black = Image.new("RGBA", (width, height), "white")
    black.paste(bl, (0, 0), bl)

    pieces[item] = (white, black)
print("Pieces: Ok")


# Функция добавления шахматной фигуры на доску
def add_piece(dest, piece, row, column):
    print("Adding piece")
    piece_image = pieces[piece][(row + column + 1) % 2]
    x = int(left + column * width)
    y = int(top + row * height)
    dest.paste(piece_image, (x, y), piece_image)
    print("Adding piece: Ok")


# Симметричное шифрование (Шифр Вернама)
def crypto(code):
    global KEY
    # Инкремент ключа шифрования
    KEY += args.step
    KEY %= 0b111111
    return code ^ KEY


# Перевод текста в строку из единиц и нулей
def encode_text(message):
    global KEY
    print("Encoding text")
    KEY = ORIGIN
    sequence = []
    # Перевод всех символов строки в заглавные символы
    for char in message.upper():
        # Количество единиц, идущих подряд
        value = 0
        # Перевод символа в строку из единиц и нулей
        for key in format(crypto(chars_encoding[char]), "06b"):
            if key == "1":
                value += 1
            else:
                if value != 0:
                    sequence.append(value)
                sequence.append(0)
                value = 0
        if value != 0:
            sequence.append(value)
    print("Encoding text: Ok")
    return sequence


# Преобразование текста в шахматное стего
def encode_images(message, sequence=None):
    print("Creating images")
    # Выбор координаты индикатора начала послания
    start = randint(0, args.step)
    index = start
    image = base.copy()

    # Добавление индикатора начала послания
    add_piece(image, "queen", index // 8, index % 8)
    index += 1

    # В случае, если функция вызвана повторно, следует кодировать с того места, на котором остановились
    sequence = sequence or encode_text(message)
    images = [image]

    # Оставшееся количество фигур
    amounts = {"pawn": 16, "king": 2, "rook": 4, "knight": 4, "bishop": 4}

    for i, seq in enumerate(sequence):
        # В случае, если поле заканчивается
        if index >= 63:
            # Добавление индикатоар окончания послания
            add_piece(image, "queen", index // 8, index % 8)

            # Повторный вызов преобразования для оставшейся последовательности
            print("End of field")
            images.extend(encode_images(None, [seq, *sequence[i + 1:]]))
            break

        # Пропуск клетки
        if seq == 0:
            index += 1

        # k - количество единиц, задаваемое каждой из фигур в v
        for (k, v) in chess_encoding:
            # В случае, если поле заканчивается
            if index >= 63:
                print("End of field")
                break

            # Пока количество подряд идущих единиц больше либо равно k
            while seq >= k:
                # Случайное перемешивание фигур, задавающих одно количество единиц
                shuffle(v)

                # Попытка добавить каждую из фигур
                for piece in v:
                    # Если осталась такая фигура
                    if amounts[piece] > 0:
                        amounts[piece] -= 1
                        seq -= k
                        add_piece(image, piece, index // 8, index % 8)
                        index += 1
                        break
                else:
                    # Если не осталось фигур из v
                    break

                # В случае, если поле заканичивается
                if index >= 63:
                    print("End of field")
                    break

        # Если не получилось закодировать символ
        if seq != 0:
            print("Insufficient amount of pieces")
            # Добавление индикатор окончания послания
            add_piece(image, "queen", index // 8, index % 8)
            # Повторный вызов преобразования для оставшейся последовательности
            images.extend(encode_images(None, [seq, *sequence[i + 1:]]))
            break
    else:
        # Если послание окончилось

        # Если на поле осталось место
        add_piece(image, "queen", index // 8, index % 8)

    # Добавление лишних фигур
    print("Adding excess pieces")
    cells = [*range(0, start), *range(index + 1, 64)]
    shuffle(cells)

    left = []
    for k, v in amounts.items():
        for _ in range((v + 1) // 3):
            left.append(k)

    shuffle(left)

    while len(cells) != 0 and len(left) != 0:
        item = choice(left)
        index = choice(cells)
        cells.remove(index)
        left.remove(item)
        add_piece(image, item, index // 8, index % 8)

    print("Creating images: Ok")
    return images


print("Creating images")
images = encode_images(args.message)
print("Creating images: Ok")

print("Saving images")
for x, image in enumerate(images):
    image.save(f"{args.path}/img{x}.png")
print("Saving images: ok")
print(len(images))
