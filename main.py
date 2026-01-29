from functools import reduce
from enum import Enum
import polars

LEX = polars.read_csv("./Lexique383/Lexique383.tsv", has_header=True, separator="\t").select("ortho", "phon", "cgram")

print(LEX.select("cgram").to_series().unique().to_list())


def ends_with(word: str, nb_match: int = 0) -> list[str]:
    res = LEX.filter(polars.col("ortho") == word).select("phon")
    expr = None
    for row in res.iter_rows():
        matched = row[0][-nb_match:]
        expr_ = polars.col("phon").str.ends_with(matched)
        if expr is None:
            expr = expr_
        else:
            expr = expr | expr_
    if expr is None:
        return []
    return LEX.filter(expr).select("ortho").to_series().to_list()


def starts_with(word: str, nb_match: int = 0) -> list[str]:
    res = LEX.filter(polars.col("ortho") == word).select("phon")
    expr = None
    for row in res.iter_rows():
        matched = row[0] if nb_match == 0 else row[0][:nb_match]
        expr_ = polars.col("phon").str.starts_with(matched)
        if expr is None:
            expr = expr_
        else:
            expr = expr | expr_
    if expr is None:
        return []
    return LEX.filter(expr).select("ortho").to_series().to_list()


def intersect(*vals: list[str]) -> list[str]:
    def intersect_(a: set[str], b: set[str]) -> set[str]:
        return a.intersection(b)
    return list(reduce(intersect_, map(lambda x: set(x), vals)))


class Category(Enum):
    PRO = "PRO"
    ADJ = "ADJ"
    LIA = "LIA"
    PRE = "PRE"
    ADV = "ADV"
    VER = "VER"
    AUX = "AUX"
    NOM = "NOM"
    ART = "ART"
    ONO = "ONO"
    CON = "CON"


def category(cat: Category, *vals: list[str]) -> list[str]:
    expr = None
    for val in vals:
        expr_ = polars.col("ortho").is_in(val)
        if expr is None:
            expr = expr_
        else:
            expr = expr | expr_
    if expr is None:
        return []
    res = LEX.filter(expr & (polars.col("cgram") == cat.value))
    return res.select("ortho").to_series().to_list()


def main():
    print("Hello from mesmots!")
    r1 = ends_with("manger", 2)
    print("r1", r1, "r1")
    r2= starts_with("bonjour", 2)
    print("r2", r2, "r2")
    r3 = intersect(r1, r2)
    print("r3", r3, "r3")
    r4 = category(Category.ADJ, r1, r2)
    print("r4", r4, "r4")


if __name__ == "__main__":
    main()
