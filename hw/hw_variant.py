"""Варианты домашних заданий курса «Python» (МИСИС, 2026/27).

Запуск из папки проекта:
    uv run hw_variant.py ваш-github-логин        — блоки для ДЗ1 и ДЗ2
    uv run hw_variant.py ваш-github-логин hw3    — папка hw3/logs/ и блок для ДЗ3
(без uv — python hw_variant.py …)

Для одного логина скрипт всегда выдаёт одно и то же. Только стандартная библиотека.
"""
import hashlib
import random
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


# ---------- h00_header ----------
BEGIN = "# === ВАРИАНТ ==="
END = "# === КОНЕЦ ВАРИАНТА ==="


def make_rng(tag: str, login: str) -> random.Random:
    """Детерминированный генератор для пары (задание, логин): одинаковый на любой ОС и версии Python."""
    key = f"{tag}:{login.strip().lower()}".encode("utf-8")
    return random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8], "big"))



# ---------- h12 ----------
# Часть генератора: ДЗ1 «Календарь чужой планеты» и ДЗ2 «Скинулись».
# Публичные функции: hw1_block(login) -> str, hw2_block(login) -> str.

# =====================================================================
# ДЗ1. Календарь чужой планеты
# =====================================================================

_H12_CONS = "бвгдзклмнпрстшж"
_H12_VOW = "аеиоу"
_H12_MONTH_SUF = ["рь", "нь", "ль", "ст", "н", "р", "й", "ра", "на", "тень", "дарь"]
_H12_LONG_PRE = ["Велико", "Средне", "Поздне", "Ранне", "Перво", "Мало", "Старо",
                 "Тёмно", "Долго", "Полу", "Ледо", "Зимо", "Ново"]
_H12_WDAY_SUF = ["ник", "дник", "ца", "нка", "ж", "д", "тень", "рник", "ла"]
_H12_BAD = ["бля", "пиз", "пезд", "манд", "елд", "пох", "еб", "жоп", "сук", "муд", "сра", "гов", "пид", "дер",
            "пук", "пер", "хер", "хуй", "трах", "залуп", "дроч", "шлю", "гнид", "туп", "дур",
            "лох", "кал", "зад", "пис", "сос", "сис", "жир", "гад", "бом", "шиз", "нег", "раб",
            "тра", "сер", "мер", "мор", "гроб", "бес", "мат", "лиж", "лиз", "сун",
            "гей", "урод", "кака", "попа", "жид", "гомо", "деб", "диб", "пип", "сек"]


_H12_STOP = ["вонь", "боль", "роль", "соль", "моль", "конь", "лень", "тень", "день", "пень",
             "дань", "рань", "зона", "нора", "гора", "кора", "пора", "мера", "вера", "рана",
             "мина", "вина", "лиса", "коза", "роза", "доза", "база", "ваза", "жара", "дума",
             "сума", "губа", "рудник", "садик", "сабля", "кабан", "банан", "лимон", "бутон",
             "дебил", "зомби", "гусар", "ливень", "камень", "ремень", "олень", "сирень", "мишень",
             "пелена", "минута", "монета", "ракета", "комета", "газета", "дорога", "погода",
             "работа", "забота", "суббота", "пятница", "среда", "середина", "начало", "ноль"]


def _h12_word(rng, n_syl, suffixes):
    """Выдуманное слово из слогов «согласная+гласная» и окончания; с заглавной буквы."""
    while True:
        w = "".join(rng.choice(_H12_CONS) + rng.choice(_H12_VOW) for _ in range(n_syl))
        w += rng.choice(suffixes)
        if not any(b in w for b in _H12_BAD) and w not in _H12_STOP:
            return w.capitalize()


def _h12_days_word(n):
    if n % 10 == 1 and n % 100 != 11:
        return "день"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return "дня"
    return "дней"


def _h12_hw1_data(login):
    """Константы варианта ДЗ1 (dict) — детерминированно по логину."""
    rng = make_rng("hw1", login)
    while True:
        a = rng.randint(3, 7)
        b = a * rng.randint(3, 25)
        c = b * rng.randint(2, 5)

        # --- дни недели: 5..10 названий, у двух совпадают первые две буквы
        n_wd = rng.randint(5, 10)
        wdays = []
        while len(wdays) < n_wd:
            w = _h12_word(rng, rng.choice([1, 2, 2]), _H12_WDAY_SUF)
            if 5 <= len(w) <= 9:
                wdays.append(w)
        # ловушка: одно название начинаем с того же слога, что и другое
        i, j = rng.sample(range(n_wd), 2)
        tail = _h12_word(rng, 1, _H12_WDAY_SUF).lower()
        wdays[j] = wdays[i][:2] + tail
        if any(x in wdays[j].lower() for x in _H12_BAD) or wdays[j].lower() in _H12_STOP:
            continue
        # все названия различимы по первым трём буквам, а пара-ловушка — ровно по третьей
        heads = [w[:3].lower() for w in wdays]
        if len(set(heads)) != n_wd or len(set(w.lower() for w in wdays)) != n_wd:
            continue

        # --- месяцы: 8..16, дней 20..38 (+1..2 в високосный у 1..3 месяцев)
        n_m = rng.randint(8, 16)
        names = []
        while len(names) < n_m:
            w = _h12_word(rng, rng.choice([1, 2, 2, 2, 3]), _H12_MONTH_SUF)
            if 5 <= len(w) <= 10 and w.lower() not in [x.lower() for x in names]:
                names.append(w)
        # один длинный месяц: «название год» почти во всю ширину таблицы (колонки по 2 символа)
        width = 3 * n_wd - 1
        target = max(9, min(16, width - 5 + rng.randint(-1, 2)))
        while True:
            pre = rng.choice(_H12_LONG_PRE)
            w = pre + _h12_word(rng, rng.randint(1, 3), _H12_MONTH_SUF).lower()
            if abs(len(w) - target) <= 1 and not any(b in w.lower() for b in _H12_BAD) \
                    and w.lower() not in [x.lower() for x in names]:
                break
        names[rng.randrange(n_m)] = w.capitalize()
        # «грязь» в написании: регистр и лишние пробелы
        dirty = rng.sample(range(n_m), 3)
        names[dirty[0]] = names[dirty[0]].upper()
        names[dirty[1]] = names[dirty[1]].lower()
        names[dirty[2]] = rng.choice(["  ", " "]) + names[dirty[2]] + rng.choice(["", " ", "  "])
        if names[dirty[2]] == names[dirty[2]].strip():
            continue

        days = [rng.randint(20, 38) for _ in range(n_m)]
        leap_days = days[:]
        for k in rng.sample(range(n_m), rng.randint(1, 3)):
            leap_days[k] += rng.randint(1, 2)
        months = [(names[k], days[k], leap_days[k]) for k in range(n_m)]
        first = rng.randrange(n_wd)
        return {"LEAP_A": a, "LEAP_B": b, "LEAP_C": c, "MONTHS": months,
                "WEEKDAYS": wdays, "FIRST_WEEKDAY": first}, rng


def _h12_hw1_checks(d, rng):
    """Примеры «Проверьте себя»: [(год, високосный?, дней)] ×2 и (год, месяц, день недели)."""
    a, b, c = d["LEAP_A"], d["LEAP_B"], d["LEAP_C"]
    norm = sum(m[1] for m in d["MONTHS"])
    extra = sum(m[2] for m in d["MONTHS"]) - norm

    def leap(y):
        return y % a == 0 and (y % b != 0 or y % c == 0)

    def mult(k, y):  # сколько кратных k среди 0..y-1
        return -((-y) // k)

    y1 = b * rng.randint(max(1, 1000 // b), max(2, 4000 // b))
    while y1 % c == 0:
        y1 += b
    y2 = c * rng.randint(1, max(1, 5000 // c))
    out = [(y1, leap(y1), norm + extra * leap(y1)), (y2, leap(y2), norm + extra * leap(y2))]
    rng.shuffle(out)
    y3 = rng.randint(1990, 2100)
    m3 = rng.randint(2, len(d["MONTHS"]))
    before = norm * y3 + extra * (mult(a, y3) - mult(b, y3) + mult(c, y3))
    before += sum(m[2] if leap(y3) else m[1] for m in d["MONTHS"][:m3 - 1])
    wd = d["WEEKDAYS"][(d["FIRST_WEEKDAY"] + before) % len(d["WEEKDAYS"])]
    return out, (y3, m3, wd)


def _h12_wrap_list(items, indent="    ", width=78):
    lines, cur = [], indent
    for it in items:
        piece = it + ", "
        if len(cur) + len(piece.rstrip()) > width and cur.strip():
            lines.append(cur.rstrip())
            cur = indent
        cur += piece
    if cur.strip():
        lines.append(cur.rstrip())
    return lines


def hw1_block(login):
    d, rng = _h12_hw1_data(login)
    leaps, (y3, m3, wd) = _h12_hw1_checks(d, rng)
    L = [BEGIN, f"# ДЗ1 · вариант для: {login}",
         "# Календарь вашей планеты. Годы считаются с нулевого.",
         "#",
         "# Високосность: год високосный, если делится на LEAP_A, кроме тех,",
         "# что делятся на LEAP_B, но делящиеся на LEAP_C — снова високосные.",
         f"LEAP_A = {d['LEAP_A']}",
         f"LEAP_B = {d['LEAP_B']}",
         f"LEAP_C = {d['LEAP_C']}",
         "",
         "# Месяцы по порядку: (название, дней в обычный год, дней в високосный год).",
         "# Пользователь вводит номер месяца, первый месяц — номер 1.",
         "MONTHS = ["]
    for name, n1, n2 in d["MONTHS"]:
        L.append(f'    ("{name}", {n1}, {n2}),')
    L += ["]",
          "",
          "# Дни недели по порядку. Сколько названий — столько дней в неделе.",
          "WEEKDAYS = ["]
    L += _h12_wrap_list([f'"{w}"' for w in d["WEEKDAYS"]])
    L += ["]",
          "",
          "# Каким днём недели было 1-е число первого месяца года 0:",
          "# индекс в списке WEEKDAYS (считая с нуля).",
          f"FIRST_WEEKDAY = {d['FIRST_WEEKDAY']}",
          "",
          "# Проверьте себя:"]
    for y, is_leap, n in leaps:
        L.append(f"#   год {y} — {'високосный' if is_leap else 'не високосный'}, "
                 f"в нём {n} {_h12_days_word(n)};")
    L.append(f"#   1-е число месяца №{m3} в {y3} году — {wd}.")
    L.append(END)
    return "\n".join(L) + "\n"


# =====================================================================
# ДЗ2. Скинулись
# =====================================================================

# (настоящее имя, пол, вин. и род. полного имени, уменьшительное: им., вин., род., латиница)
_H12_PEOPLE = [
    ("Василий", "м", "Василия", "Василия", "Вася", "Васю", "Васи", "vasya"),
    ("Пётр", "м", "Петра", "Петра", "Петя", "Петю", "Пети", "petya"),
    ("Мария", "ж", "Марию", "Марии", "Маша", "Машу", "Маши", "masha"),
    ("Александр", "м", "Александра", "Александра", "Саша", "Сашу", "Саши", "sasha"),
    ("Екатерина", "ж", "Екатерину", "Екатерины", "Катя", "Катю", "Кати", "katya"),
    ("Дмитрий", "м", "Дмитрия", "Дмитрия", "Дима", "Диму", "Димы", "dima"),
    ("Ольга", "ж", "Ольгу", "Ольги", "Оля", "Олю", "Оли", "olya"),
    ("Николай", "м", "Николая", "Николая", "Коля", "Колю", "Коли", "kolya"),
    ("Анна", "ж", "Анну", "Анны", "Аня", "Аню", "Ани", "anya"),
    ("Михаил", "м", "Михаила", "Михаила", "Миша", "Мишу", "Миши", "misha"),
    ("Татьяна", "ж", "Татьяну", "Татьяны", "Таня", "Таню", "Тани", "tanya"),
    ("Сергей", "м", "Сергея", "Сергея", "Серёжа", "Серёжу", "Серёжи", "seryozha"),
    ("Елена", "ж", "Елену", "Елены", "Лена", "Лену", "Лены", "lena"),
    ("Иван", "м", "Ивана", "Ивана", "Ваня", "Ваню", "Вани", "vanya"),
    ("Наталья", "ж", "Наталью", "Натальи", "Наташа", "Наташу", "Наташи", "natasha"),
    ("Алексей", "м", "Алексея", "Алексея", "Лёша", "Лёшу", "Лёши", "lyosha"),
    ("Ирина", "ж", "Ирину", "Ирины", "Ира", "Иру", "Иры", "ira"),
    ("Юлия", "ж", "Юлию", "Юлии", "Юля", "Юлю", "Юли", "yulya"),
    ("Григорий", "м", "Григория", "Григория", "Гриша", "Гришу", "Гриши", "grisha"),
    ("Полина", "ж", "Полину", "Полины", "Поля", "Полю", "Поли", "polya"),
]
# траты по шаблонам: «за <что>» (вин. падеж), «<что>» в начале, «<что>» в середине
_H12_ITEMS_T1 = ["такси", "бензин", "жильё", "ужин", "билеты на поезд", "аренду машины",
                 "парковку", "пиццу", "баню", "прокат лодки", "экскурсию", "трансфер"]
_H12_ITEMS_T2 = ["продукты", "шашлык", "завтрак", "дрова", "вода и снеки", "сувениры",
                 "аптека", "кофе", "фрукты", "продукты на рынке", "уголь и розжиг"]
_H12_ITEMS_T3 = ["кино", "музей", "боулинг", "квест", "канатная дорога", "кафе",
                 "мороженое", "аквапарк", "караоке", "бильярд", "лимонад"]


def _h12_forms(p):
    """Все формы человека: (им., вин., род., латиница) — списки; без «ё» тоже."""
    name, _, acc, gen, dim, dim_acc, dim_gen, lat = p
    def yo(xs):
        out = []
        for x in xs:
            out.append(x)
            if "ё" in x:
                out.append(x.replace("ё", "е"))
        return out
    return yo([name, dim]), yo([acc, dim_acc]), yo([gen, dim_gen]), [lat]


def _h12_aliases(people):
    al = {}
    for p in people:
        nom, acc, gen, lat = _h12_forms(p)
        for f in nom + acc + gen + lat:
            al.setdefault(f.lower(), p[0])
    return al


def _h12_case(rng, s, low=0.25):
    r = rng.random()
    if r < low:
        return s.lower()
    return s


def _h12_amount_text(rng, kop, spaced, suffix, show_zero=False):
    rub, k = divmod(kop, 100)
    r = str(rub)
    if spaced and rub >= 1000:
        r = f"{rub:,}".replace(",", " ")
    if k or show_zero:
        r += f".{k:02d}"
    return r + suffix


_H12_SUFFIXES = ["", "", " руб", "р", " р", " ₽", "₽"]


def _h12_join(rng, parts):
    if len(parts) == 1:
        return parts[0]
    if rng.random() < 0.5:
        return ", ".join(parts[:-1]) + " и " + parts[-1]
    return ", ".join(parts)


def _h12_render(rng, e, people_by_name, alt=None):
    """Строка журнала для траты e. alt — текст строки-оригинала (для дубля: написать иначе)."""
    for _ in range(100):
        p = people_by_name[e["payer"]]
        nom, acc, gen, lat = _h12_forms(p)
        payer = rng.choice(nom + nom + lat)
        payer = payer if payer in lat else _h12_case(rng, payer)
        if rng.random() < 0.1 and payer not in lat:
            payer = payer.upper() if rng.random() < 0.3 else payer.capitalize()
        spaced = rng.random() < 0.6
        amount = _h12_amount_text(rng, e["kop"], spaced, rng.choice(_H12_SUFFIXES),
                                  show_zero=rng.random() < 0.1)
        t = e["tpl"]
        if t == 1:
            verb = "заплатил" if p[1] == "м" else "заплатила"
            line = f"{payer} {verb} {amount} за {e['item']}, на всех"
        elif t == 2:
            names = e["parts"][:]
            rng.shuffle(names)
            lst = [_h12_case(rng, rng.choice(_h12_forms(people_by_name[n])[1]), 0.15) for n in names]
            line = f"{payer}: {e['item']} {amount}, на {_h12_join(rng, lst)}"
        else:
            names = e["excl"][:]
            rng.shuffle(names)
            lst = [_h12_case(rng, rng.choice(_h12_forms(people_by_name[n])[2]), 0.15) for n in names]
            line = f"{payer} — {amount}, {e['item']}, все кроме {_h12_join(rng, lst)}"
        if alt is None:
            return line
        # дубль: другое написание и плательщика, и суммы
        a_payer = alt.split(" ")[0].rstrip(":")
        if payer != a_payer and amount not in alt and line != alt:
            return line
    raise RuntimeError("не удалось переписать дубль")


def _h12_hw2_data(login):
    """(текст LOG без кавычек — список строк, ALIASES, траты по строкам, индексы пары-дубля)."""
    rng = make_rng("hw2", login)
    while True:
        n = rng.randint(4, 6)
        people = rng.sample(_H12_PEOPLE, n)
        names = sorted(p[0] for p in people)
        by_name = {p[0]: p for p in people}
        always = rng.choice(names)                      # участвует во всех тратах
        k_never = 1 if n < 5 else rng.choice([1, 1, 2])
        never = rng.sample(names, k_never)              # ни разу не платили
        payers = [x for x in names if x not in never]

        n_distinct = rng.randint(7, 13)
        tpls = [1, 1, 2, 2, 3, 3] + [rng.choice([1, 2, 2, 3, 3]) for _ in range(n_distinct - 6)]
        rng.shuffle(tpls)
        items = {1: rng.sample(_H12_ITEMS_T1, tpls.count(1)),
                 2: rng.sample(_H12_ITEMS_T2, tpls.count(2)),
                 3: rng.sample(_H12_ITEMS_T3, tpls.count(3))}
        exps = []
        t2_idx = [i for i, t in enumerate(tpls) if t == 2]
        outsider_i = rng.choice(t2_idx)                 # тут плательщик платит за других
        for i, t in enumerate(tpls):
            e = {"tpl": t, "item": items[t].pop()}
            e["payer"] = rng.choice(payers)
            if t == 1:
                e["parts"] = names[:]
                e["kop"] = rng.randint(60, 1500) * 1000 + rng.choice([0, 0, 0, 50])
            elif t == 2:
                if i == outsider_i:
                    cand = [x for x in payers if x != always]
                    e["payer"] = rng.choice(cand)
                    pool = [x for x in names if x != e["payer"] and x != always]
                    size = rng.randint(1, len(pool))
                    e["parts"] = [always] + rng.sample(pool, size)
                else:
                    pool = [x for x in names if x != always]
                    size = rng.randint(1, len(pool))
                    e["parts"] = [always] + rng.sample(pool, size)
                e["kop"] = rng.randint(150, 6000) * 100 + rng.choice([0, 0, rng.randint(1, 99)])
            else:
                pool = [x for x in names if x != always]
                size = rng.randint(1, n - 2)
                e["excl"] = rng.sample(pool, size)
                e["parts"] = [x for x in names if x not in e["excl"]]
                e["kop"] = rng.randint(100, 4000) * 100 + rng.choice([0, 0, 50, rng.randint(1, 99)])
            e["parts"] = sorted(e["parts"])
            exps.append(e)
        # пара-дубль: исходная трата с суммой от 1000, копия позже (через 3+ строки)
        cand = [i for i in range(len(exps) - 2)]
        di = rng.choice(cand)
        if exps[di]["kop"] < 100000:
            exps[di]["kop"] += rng.randint(10, 30) * 10000
        lines = [_h12_render(rng, e, by_name) for e in exps]
        pos = rng.randint(di + 3, len(exps)) if di + 3 <= len(exps) else None
        if pos is None:
            continue
        dup_line = _h12_render(rng, exps[di], by_name, alt=lines[di])
        lines.insert(pos, dup_line)
        exps.insert(pos, exps[di])
        dup = (di, pos)

        # --- гарантии
        keys = [(e["payer"], e["kop"], e["item"], tuple(e["parts"])) for e in exps]
        if len(set(keys)) != len(keys) - 1:
            continue
        kops = [e["kop"] for i, e in enumerate(exps) if i != pos]
        if len(set(kops)) != len(kops):
            continue
        if not any(e["kop"] % len(e["parts"]) for e in exps):
            continue
        if not any(e["payer"] not in e["parts"] for e in exps):
            continue
        if len(set(lines)) != len(lines):
            continue
        if not (8 <= len(lines) <= 14):
            continue
        paid = {e["payer"] for e in exps}
        if not [x for x in names if x not in paid]:
            continue
        inall = [x for x in names if all(x in e["parts"] for e in exps)]
        if not inall:
            continue
        return lines, _h12_aliases(people), exps, dup


def hw2_block(login):
    lines, aliases, _, _ = _h12_hw2_data(login)
    L = [BEGIN, f"# ДЗ2 · вариант для: {login}",
         "# Журнал трат из общего чата — как есть. Каждая трата делится поровну",
         "# между её участниками. Компания («все») — все люди из ALIASES.",
         'LOG = """']
    L += lines
    L += ['"""',
          "",
          "# Как человека могут написать в журнале (ключ — в нижнем регистре)",
          "# → кто это на самом деле.",
          "ALIASES = {"]
    groups = {}
    for k, v in aliases.items():
        groups.setdefault(v, []).append(f'"{k}": "{v}"')
    for v in sorted(groups):
        L += _h12_wrap_list(groups[v])
    L += ["}", END]
    return "\n".join(L) + "\n"



# ---------- h3 ----------
# ============================ ДЗ3 «Чёрный ящик» ============================
# Логи нескольких серверов вокруг ночи 25.10.2026 (Европа переводит часы назад).
# Внутри генератора момент времени — целое число секунд от 2026-10-25 01:00:00 UTC (момент перевода).
# zoneinfo не используем: у студента на Windows может не быть tzdata. Смещения на окно логов
# (24–25.10.2026) захардкожены и сверены с tzdata 2026e (hw_private/tests/test_hw3.py).

_H3_T0 = datetime(2026, 10, 25, 1, 0, 0)  # наивный, означает UTC
_H3_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
_H3_HOUR = 3600

# пояс -> (смещение в часах до 01:00 UTC 25.10.2026, после)
_H3_TZ_DST = {
    "Europe/Berlin": (2, 1), "Europe/Paris": (2, 1), "Europe/Warsaw": (2, 1), "Europe/Madrid": (2, 1),
    "Europe/Rome": (2, 1), "Europe/Prague": (2, 1), "Europe/London": (1, 0), "Europe/Lisbon": (1, 0),
    "Europe/Helsinki": (3, 2), "Europe/Athens": (3, 2),
}
_H3_TZ_FLAT = {
    "Europe/Moscow": 3, "Asia/Yekaterinburg": 5, "Asia/Novosibirsk": 7, "Asia/Vladivostok": 10,
    "Asia/Tokyo": 9, "America/New_York": -4, "UTC": 0,
}
_H3_NAMES = ["api", "auth", "db", "billing", "cache", "gateway", "queue", "search", "mail", "cdn",
             "metrics", "storage", "orders", "notify", "payments", "worker"]

# Шаблоны сообщений: {n} — число, {s} — 1..9, {p} — процент, {b} — байт IP, {d} — день (23/24), {c} — код HTTP.
_H3_ERR_EN = [
    "Timeout after {n} ms for user {n}",
    "Connection refused by 10.0.{b}.{b}:5432",
    "Payment {n}-{n} declined",
    "Write to disk sda{n} failed",
    "Upstream returned HTTP {c}",
    "Job {n} crashed with exit code {s}",
    "Retry {s} of 5 failed | queue=orders",
    "Backup from 2026-10-{d} failed",
]
_H3_ERR_RU = [
    "Нет связи с базой, попытка {s}",
    "Таймаут {n} мс при запросе к складу",
    "Платёж {n} отклонён банком",
    "Ошибка записи в файл report_{n}.csv",
    "Пользователь {n} не найден",
    "Очередь заказов переполнена: {n} задач | ждём",
    "Письмо {n} не доставлено",
]
_H3_MSG = {  # уровень -> (английские, русские)
    "DEBUG": (["Pool size {n}", "GC pause {n} ms", "Cache miss for key user:{n}", "Heartbeat {n}"],
              ["Соединений в пуле: {n}", "Кэш обновлён за {n} мс", "Сессий в памяти: {n}"]),
    "INFO": (["Health check ok", "Request {n} handled in {n} ms", "User {n} logged in",
              "Job {n} finished, previous ERROR cleared", "Config reloaded"],
             ["Запрос {n} обработан за {n} мс", "Пользователь {n} вошёл в систему", "Заказ {n} оформлен",
              "Проверка связи: ок"]),
    "WARNING": (["Slow query: {n} ms", "Retry {s} of 5 | queue=orders", "Certificate expires in {s} days"],
                ["Диск заполнен на {p}%", "Память: {n} МБ из 16384", "Медленный ответ склада: {n} мс"]),
    "CRITICAL": (["Service unavailable", "Out of memory: killed process {n}", "Disk sda{n} is read-only"],
                 ["Сервис недоступен", "Потеряно соединение с базой данных"]),
}
_H3_SPECIAL_DATE = [("INFO", "Резервная копия от 2026-10-24 23:00:00 проверена"),
                    ("INFO", "Backup 2026-10-24T23:00:00Z verified"),
                    ("INFO", "Отчёт за 2026-10-24 отправлен")]
_H3_SPECIAL_PIPE = [("WARNING", "Retry {s} of 5 | queue=orders"),
                    ("INFO", "Повтор записи: 2026-10-24T22:15:03Z | INFO | ok"),
                    ("INFO", "Платёж {n} | статус=ожидание")]
_H3_BAD_LEVELS = ["EROR", "error", "FATAL", "Warn", "WARN", "Error", "CRIT", "Info", "debug", "ERR",
                  "Critical", "NOTICE"]
_H3_BLANKS = ["", "", "   ", "\t", "  \t  "]
_H3_FORBIDDEN = "\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029\r"


def _h3_offset(zone, t):
    """Смещение пояса от UTC в часах в момент t."""
    if zone in _H3_TZ_DST:
        before, after = _H3_TZ_DST[zone]
        return before if t < 0 else after
    return _H3_TZ_FLAT[zone]


def _h3_key(tpl):
    """Шаблон top_errors для шаблона сообщения: каждая группа цифр -> <N>."""
    return re.sub(r"\d+", "<N>", re.sub(r"\{\w\}", "0", tpl))


def _h3_fill(rng, tpl):
    def repl(m):
        kind = m.group(1)
        if kind == "d":
            return rng.choice(["23", "24"])
        if kind == "c":
            return rng.choice(["500", "502", "503", "504"])
        if kind == "s":
            return str(rng.randint(1, 9))
        if kind == "p":
            return str(rng.randint(70, 99))
        if kind == "b":
            return str(rng.randint(0, 255))
        return str(rng.randint(2, 9999))
    return re.sub(r"\{(\w)\}", repl, tpl)


def _h3_pick(rng, pairs):
    """Взвешенный выбор: pairs = [(значение, вес), ...]."""
    x = rng.randint(1, sum(w for _, w in pairs))
    for value, w in pairs:
        x -= w
        if x <= 0:
            return value
    return pairs[-1][0]


def _h3_time(rng, srv, t, bad=None):
    """Время строки так, как его пишет сервер. bad — способ сделать время невозможным."""
    off = 0 if srv["style"] == "Z" else _h3_offset(srv["zone"], t)
    w = _H3_T0 + timedelta(seconds=t + off * _H3_HOUR)
    date, hh, mm, ss = f"{w.year:04d}-{w.month:02d}-{w.day:02d}", f"{w.hour:02d}", f"{w.minute:02d}", f"{w.second:02d}"
    if bad == "min":
        mm = str(rng.randint(60, 99))
    elif bad == "hour":
        hh = str(rng.randint(25, 29))
    elif bad == "feb":
        date = rng.choice(["2026-02-30", "2026-02-31"])
    elif bad == "day":
        date = f"{w.year:04d}-{w.month:02d}-32"
    sep = srv["sep"] if srv["sep"] != "mix" else rng.choice(["T", " "])
    if srv["style"] == "Z":
        suffix = "Z"
    elif srv["style"] == "offset":
        suffix = f"{'+' if off >= 0 else '-'}{abs(off):02d}:00"
    else:
        suffix = ""
    return f"{date}{sep}{hh}:{mm}:{ss}{suffix}", w


def _h3_parse(line):
    """Разбор строки по правилам ДЗ3 (как у студента). Битая — ValueError."""
    parts = line.strip().split(" | ", 2)
    if len(parts) != 3:
        raise ValueError("не 3 части")
    if parts[1] not in _H3_LEVELS:
        raise ValueError("уровень")
    return datetime.fromisoformat(parts[0]), parts[1], parts[2]


def _h3_gap(ts):
    """(начало, конец, длина, запас до второго по длине промежутка) по отсортированным моментам."""
    ts = sorted(ts)
    best, second = None, -1
    for a, b in zip(ts, ts[1:]):
        d = b - a
        if best is None or d > best[2]:
            if best is not None:
                second = max(second, best[2])
            best = (a, b, d)
        else:
            second = max(second, d)
    return best[0], best[1], best[2], best[2] - second


def _h3_attempt(rng):
    """Одна попытка собрать вариант. None — не прошла проверки (тогда следующая попытка того же rng)."""
    # ---- серверы ----
    n = rng.choice([3, 4, 4, 5, 5])
    names = sorted(rng.sample(_H3_NAMES, n))
    encs = ["cp1251", "utf-8-sig"] + ["utf-8"] * (n - 2)
    rng.shuffle(encs)
    dst_i = rng.randrange(n)
    styles = ["Z", "offset"] + [rng.choice(["Z", "offset", "naive"]) for _ in range(n - 3)]
    rng.shuffle(styles)
    dst_zone = rng.choice(list(_H3_TZ_DST))
    flat_pool = list(_H3_TZ_FLAT)
    rng.shuffle(flat_pool)
    any_pool = list(_H3_TZ_DST) + list(_H3_TZ_FLAT)
    rng.shuffle(any_pool)
    used = [dst_zone]
    servers = []
    for i, name in enumerate(names):
        if i == dst_i:
            style, zone = "naive", dst_zone
            sep = rng.choice(["T", " ", "mix", "mix"])
        else:
            style = styles.pop()
            pool = flat_pool if style == "naive" else any_pool
            zone = [z for z in pool if z not in used][0]
            sep = rng.choice(["T", "T", " ", "mix"])
        used.append(zone)
        servers.append({"name": name, "zone": zone, "style": style, "sep": sep, "enc": encs[i],
                        "eol": rng.choice(["\n", "\r\n"]), "ru": 50 if encs[i] != "utf-8" else 25})

    # ---- окно, инцидент ----
    S = -rng.randint(16 * _H3_HOUR, 19 * _H3_HOUR + 3599)
    E = rng.randint(9 * _H3_HOUR, 11 * _H3_HOUR + 3599)
    G0 = rng.randint(8 * 60, 25 * 60)                       # начало простоя: второй проход двойного часа
    G1 = G0 + rng.randint(18 * 60, min(40 * 60, 58 * 60 - G0))
    B0 = G0 - rng.randint(5 * 60, 14 * 60)                  # начало всплеска ошибок

    # ---- события: [t, сервер, уровень, сообщение, вид] ----
    events = []
    target = rng.randint(1400, 2600)
    weights = [rng.randint(2, 6) for _ in servers]
    for si in range(n):
        mean = (E - S) * sum(weights) // (target * weights[si])
        lo, hi = max(5, mean * 3 // 10), mean * 17 // 10
        t = S + rng.randint(0, lo)
        while t <= E:
            if t < B0 or t > G1:
                events.append([t, si, None, None, "bg"])
            t += rng.randint(lo, hi)
        t = B0 + rng.randint(0, 40)
        while t < G0:
            lvl = _h3_pick(rng, [("ERROR", 55), ("CRITICAL", 7), ("WARNING", 25), ("INFO", 13)])
            events.append([t, si, lvl, None, "burst"])
            t += rng.randint(30, 120)
    events.append([rng.randint(-600, -60), dst_i, "INFO", None, "wit"])   # конец первого прохода
    events.append([rng.randint(30, 300), dst_i, "INFO", None, "wit"])     # начало второго прохода
    events.append([G0, dst_i, "CRITICAL", rng.choice(["Аварийная остановка: нет памяти",
                                                      "Fatal: out of memory, shutting down"]), "g0"])
    events.append([G1, dst_i, "INFO", rng.choice(["Сервис перезапущен", "Service restarted"]), "g1"])
    events.sort(key=lambda e: (e[0], e[1]))

    # ---- план ERROR: ≥ 6 шаблонов, ничья на 5–6 месте (и иногда внутри топа) ----
    k = rng.randint(7, 9)
    k_ru = rng.randint(3, k - 3)
    tpls = rng.sample(_H3_ERR_RU, k_ru) + rng.sample(_H3_ERR_EN, k - k_ru)
    rng.shuffle(tpls)
    x = rng.randint(3, 6)
    c4 = x + rng.randint(1, 3)
    c3 = c4 if rng.randint(0, 1) else c4 + rng.randint(1, 3)
    c2 = c3 + rng.randint(1, 3)
    c1 = c2 + rng.randint(1, 5)
    counts = [c1, c2, c3, c4, x, x] + [rng.randint(1, x - 1) for _ in range(k - 6)]
    burst_err = [e for e in events if e[4] == "burst" and e[2] == "ERROR"]
    bg = [e for e in events if e[4] == "bg"]
    bg_err = sum(counts) - len(burst_err)
    if bg_err < 12:
        counts[0] += 12 - bg_err
        bg_err = 12
    picked = rng.sample(bg, bg_err + rng.randint(0, 2))
    for e in picked[:bg_err]:
        e[2] = "ERROR"
    for e in picked[bg_err:]:
        e[2] = "CRITICAL"
    rest = [tpls[i] for i in range(1, k) for _ in range(counts[i])]
    rng.shuffle(rest)
    pool = [tpls[0]] * counts[0] + rest                     # главная ошибка инцидента — в начале всплеска
    for e, tpl in zip(burst_err + picked[:bg_err], pool):
        e[3] = _h3_fill(rng, tpl)
    for e in events:
        if e[2] is None:
            e[2] = _h3_pick(rng, [("DEBUG", 28), ("INFO", 57), ("WARNING", 15)])
    plain = [e for e in events if e[4] == "bg" and e[2] in ("INFO", "WARNING") and e[3] is None]
    for e, special in zip(rng.sample(plain, 2), [rng.choice(_H3_SPECIAL_DATE), rng.choice(_H3_SPECIAL_PIPE)]):
        e[2], e[3] = special[0], _h3_fill(rng, special[1])
    for e in events:
        if e[3] is None:
            lang = 1 if rng.randint(1, 100) <= servers[e[1]]["ru"] else 0
            e[3] = _h3_fill(rng, rng.choice(_H3_MSG[e[2]][lang]))

    # ---- строки по файлам: (t, порядок, текст, вид) ----
    per = [[] for _ in servers]
    for e in events:
        line, _ = _h3_time(rng, servers[e[1]], e[0])
        per[e[1]].append((e[0], len(per[e[1]]), f"{line} | {e[2]} | {e[3]}", "ok", e))
    bad_kinds = (["level"] * rng.randint(2, 4) + ["time"] * rng.randint(2, 3)
                 + ["trunc"] * rng.randint(1, 3) + ["glue"] * rng.randint(1, 2))
    time_modes = ["min", "hour", "feb", "day"]
    rng.shuffle(time_modes)
    extra = [[] for _ in servers]
    for bi, kind in enumerate(bad_kinds):
        for _ in range(100):
            si = rng.randrange(n)
            j = rng.randint(1, len(per[si]) - 1)
            ta, tb = per[si][j - 1][0], per[si][j][0]
            tx = rng.randint(ta, tb)
            if -_H3_HOUR - 60 <= tx <= _H3_HOUR + 60 or ta <= G1 and tb >= G0:
                continue
            break
        else:
            return None
        srv = servers[si]
        lvl = _h3_pick(rng, [("INFO", 50), ("WARNING", 20), ("ERROR", 20), ("DEBUG", 10)])
        lang = 1 if rng.randint(1, 100) <= srv["ru"] else 0
        msg = _h3_fill(rng, rng.choice((_H3_ERR_EN, _H3_ERR_RU)[lang] if lvl == "ERROR" else _H3_MSG[lvl][lang]))
        if kind == "level":
            tm, _ = _h3_time(rng, srv, tx)
            text = f"{tm} | {rng.choice(_H3_BAD_LEVELS)} | {msg}"
        elif kind == "time":
            tm, _ = _h3_time(rng, srv, tx, bad=time_modes[bi % len(time_modes)])
            text = f"{tm} | {lvl} | {msg}"
        elif kind == "trunc":
            tm, _ = _h3_time(rng, srv, tx)
            full = f"{tm} | {lvl} | {msg}"
            text = full[:rng.randint(12, len(tm) + 3 + len(lvl) + 2)].rstrip()
        else:
            tm, _ = _h3_time(rng, srv, tx)
            tm2, _ = _h3_time(rng, srv, rng.randint(tx, tb))
            lvl2 = _h3_pick(rng, [("INFO", 60), ("WARNING", 25), ("DEBUG", 15)])
            msg2 = _h3_fill(rng, rng.choice(_H3_MSG[lvl2][lang]))
            text = f"{tm} | {lvl[:rng.randint(1, len(lvl))]}{tm2} | {lvl2} | {msg2}"
        extra[si].append((tx, 10 ** 6 + bi, text, kind, None))

    # пустые строки и строки из пробелов (не битые): минимум одна каждого вида на вариант
    blanks = [[] for _ in servers]
    for text in ["", rng.choice(_H3_BLANKS[2:])] + [rng.choice(_H3_BLANKS) for _ in range(rng.randint(0, 4))]:
        blanks[rng.randrange(n)].append(text)
    files, bad_meta, file_errs = {}, [], []
    for si, srv in enumerate(servers):
        rows = sorted(per[si] + extra[si], key=lambda r: (r[0], r[1]))
        rows = [(r[2], r[3], r[4]) for r in rows]
        for text in blanks[si]:
            rows.insert(rng.randint(1, len(rows)), (text, "blank", None))   # первая строка файла — всегда запись
        fname = srv["name"] + ".log"
        prev_wall, rollbacks = None, 0
        for no, (text, kind, e) in enumerate(rows, start=1):
            if any(ch in text for ch in _H3_FORBIDDEN) or (kind != "blank" and not text.isprintable()):
                return None
            if kind == "blank":
                continue
            if kind == "ok":
                if text != text.strip():
                    return None
                dt, lvl, msg = _h3_parse(text)          # нормальная строка обязана разбираться
                if dt.tzinfo is not None:
                    if dt.replace(tzinfo=None) - dt.utcoffset() != _H3_T0 + timedelta(seconds=e[0]):
                        return None
                elif srv["style"] == "naive":
                    if prev_wall is not None and dt < prev_wall:
                        rollbacks += 1
                    prev_wall = dt
                if not msg or re.search(r"\d", re.sub(r"[0-9]", "", msg)):    # цифры — только ASCII
                    return None
                if e[2] == "ERROR":
                    file_errs.append((fname, no, msg))
            else:
                try:
                    _h3_parse(text)
                except ValueError:
                    bad_meta.append({"file": fname, "line_no": no, "kind": kind})
                else:
                    return None
                if not text.strip():
                    return None
        if rollbacks != (1 if si == dst_i else 0):
            return None
        data = (srv["eol"].join(r[0] for r in rows) + srv["eol"]).encode(srv["enc"])
        files[fname] = data

    # ---- проверки кодировок ----
    for srv in servers:
        data = files[srv["name"] + ".log"]
        if srv["enc"] == "cp1251":
            if b"\x98" in data:
                return None
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                pass
            else:
                return None
        if (srv["enc"] == "utf-8-sig") != data.startswith(b"\xef\xbb\xbf"):
            return None
        if srv["enc"] != "utf-8":
            cyr_err = [m for f, _, m in file_errs if f == srv["name"] + ".log" and re.search("[а-яА-ЯёЁ]", m)]
            if not cyr_err:
                return None

    # ---- ответ (по истинным моментам) и проверки ловушек ----
    msk = lambda t: (_H3_T0 + timedelta(seconds=t + 3 * _H3_HOUR)).isoformat() + "+03:00"
    levels = {lvl: 0 for lvl in _H3_LEVELS}
    hours = {f"{h:02d}": 0 for h in range(24)}
    hour_days = {}
    for e in events:
        levels[e[2]] += 1
        if e[2] == "ERROR":
            h = (e[0] + 4 * _H3_HOUR) // _H3_HOUR % 24
            hours[f"{h:02d}"] += 1
            hour_days.setdefault(h, [])
            day = (e[0] + 4 * _H3_HOUR) // 86400
            if day not in hour_days[h]:
                hour_days[h].append(day)
    if max(len(v) for v in hour_days.values()) < 2:
        return None                                         # часы разных суток должны складываться
    tally = {}
    for _, _, m in sorted(file_errs):
        key = re.sub(r"\d+", "<N>", m)
        tally[key] = tally.get(key, 0) + 1
    top = sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    by_insertion = sorted(tally.items(), key=lambda kv: -kv[1])[:5]   # как Counter.most_common(5)
    if top == by_insertion or len(tally) != k or sorted(tally.values(), reverse=True) != sorted(counts, reverse=True):
        return None

    def moment(e, mode):
        srv, t = servers[e[1]], e[0]
        off = 0 if srv["style"] == "Z" else _h3_offset(srv["zone"], t)
        if mode == "fold0" and srv["style"] == "naive" and srv["zone"] in _H3_TZ_DST and 0 <= t < _H3_HOUR:
            return t - _H3_HOUR
        if mode == "strip":
            return t + off * _H3_HOUR
        if mode == "as_utc" and srv["style"] == "naive":
            return t + off * _H3_HOUR
        if mode == "as_msk" and srv["style"] == "naive":
            return t + (off - 3) * _H3_HOUR
        return t

    a, b, d, margin = _h3_gap([e[0] for e in events])
    if (a, b) != (G0, G1) or margin < 60:
        return None
    wrong = {}
    for mode in ("fold0", "strip", "as_utc", "as_msk"):
        wa, wb, wd, _ = _h3_gap([moment(e, mode) for e in events])
        if (wa, wb, wd) == (a, b, d):
            return None
        wrong[mode] = {"start": msk(wa), "end": msk(wb), "seconds": wd}
    report = {
        "levels": levels,
        "errors_by_hour_msk": hours,
        "top_errors": [[t, c] for t, c in top],
        "longest_gap": {"start": msk(a), "end": msk(b), "seconds": d},
        "bad_lines": [{"file": m["file"], "line_no": m["line_no"], "reason": m["kind"]}
                      for m in sorted(bad_meta, key=lambda m: (m["file"], m["line_no"]))],
    }
    return {"servers": servers, "files": files, "report": report, "wrong_gaps": wrong,
            "dst_server": servers[dst_i]["name"], "outage": (G0, G1), "window": (S, E)}


def _h3_build(login):
    rng = make_rng("hw3", login)
    for _ in range(300):
        model = _h3_attempt(rng)
        if model is not None:
            break
    else:
        raise RuntimeError("hw3: не удалось собрать вариант — напишите преподавателю")
    lines = [
        BEGIN,
        f"# ДЗ3 · вариант для: {login.strip()}",
        "# Логи — в папке hw3/logs/ (их создал hw_variant.py). Файл <сервер>.log пишет сервер <сервер>.",
        "# SERVER_TIMEZONES: сервер -> часовой пояс, где он стоит (имя для zoneinfo.ZoneInfo).",
        "# Время в строке без пояса (без Z и без +03:00) — местное время сервера в этом поясе.",
        "SERVER_TIMEZONES = {",
    ]
    lines += [f'    "{s["name"]}": "{s["zone"]}",' for s in model["servers"]]
    lines += ["}", END]
    model["block"] = "\n".join(lines)
    return model


def hw3_generate(login: str, logs_dir: Path) -> str:
    """Удаляет старые *.log в logs_dir, пишет логи варианта, возвращает блок варианта ДЗ3."""
    model = _h3_build(login)
    logs_dir = Path(logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    for old in sorted(logs_dir.glob("*.log")):
        if old.is_file():
            old.unlink()
    for name, data in model["files"].items():
        (logs_dir / name).write_bytes(data)
    return model["block"]



# ---------- h99_main ----------
USAGE = """Как запускать (из папки проекта):
    uv run hw_variant.py ваш-github-логин        — варианты ДЗ1 и ДЗ2
    uv run hw_variant.py ваш-github-логин hw3    — логи и вариант ДЗ3
Без uv: python hw_variant.py …"""

LOGIN_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}")


def rule(text: str) -> str:
    return f"──── {text} " + "─" * max(4, 60 - len(text))


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    if len(argv) not in (1, 2) or (len(argv) == 2 and argv[1].lower() != "hw3"):
        print(USAGE)
        return 2
    login = argv[0].strip()
    if not LOGIN_RE.fullmatch(login):
        print(f"«{login}» не похоже на логин GitHub: только латиница, цифры и дефис.")
        print("Подставьте свой логин вместо «ваш-github-логин».\n")
        print(USAGE)
        return 2

    if len(argv) == 1:
        print(rule("ДЗ1 → в самое начало hw1/main.py"))
        print(hw1_block(login))
        print()
        print(rule("ДЗ2 → в самое начало hw2/main.py"))
        print(hw2_block(login))
        return 0

    logs_dir = Path(__file__).resolve().parent / "hw3" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    block = hw3_generate(login, logs_dir)
    files = sorted(p.name for p in logs_dir.glob("*.log"))
    print(f"Логи записаны в {logs_dir}: {', '.join(files)}")
    print("Руками их не правьте. Испортили — запустите скрипт ещё раз, он создаст такие же.\n")
    print(rule("ДЗ3 → в самое начало hw3/main.py"))
    print(block)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
