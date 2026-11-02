from datetime import date

import pytest

from app.services.passport import PassportValueError, parse_passport_value

T = date(2026, 11, 1)


def test_lists_dedup_split_cap():
    assert parse_passport_value("allergies", "Курица, курица; говядина\nрыба") == [
        "Курица",
        "говядина",
        "рыба",
    ]
    assert parse_passport_value("allergies", "нет") == []
    assert (
        len(parse_passport_value("chronic_conditions", ",".join(f"b{i}" for i in range(30)))) == 10
    )
    assert len(parse_passport_value("allergies", "x" * 200)[0]) == 40


@pytest.mark.parametrize("raw,val", [("28,5", 28.5), ("12 кг", 12.0), ("3", 3.0)])
def test_weight_ok(raw, val):
    assert parse_passport_value("weight_kg", raw) == val


@pytest.mark.parametrize("raw", ["abc", "0", "500", "-5", ""])
def test_weight_bad(raw):
    with pytest.raises(PassportValueError):
        parse_passport_value("weight_kg", raw)


def test_birth_date():
    assert parse_passport_value("birth_date", "10.01.2024", T) == date(2024, 1, 10)
    assert parse_passport_value("birth_date", "10/01/2024", T) == date(2024, 1, 10)
    for bad in ("32.01.2024", "01.01.2030", "01.01.1980", "вчера"):
        with pytest.raises(PassportValueError):
            parse_passport_value("birth_date", bad, T)
