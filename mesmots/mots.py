from enum import Enum
import polars


class Mots:
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

    LEX: polars.DataFrame

    def __init__(self, lexique_path: str = "./Lexique383/Lexique383.tsv") -> None:
        self.LEX = polars.read_csv(
            lexique_path,
            has_header=True,
            separator="\t"
        ).select("ortho", "phon", "cgram")

    def endswith(self, phon: str) -> polars.Expr:
        return polars.col("phon").str.ends_with(phon)

    def startswith(self, phon: str) -> polars.Expr:
        return polars.col("phon").str.starts_with(phon)

    def contains(self, phon: str) -> polars.Expr:
        return polars.col("phon").str.contains(phon)

    def category(self, cat: Category) -> polars.Expr:
        return polars.col("cgram") == cat.value

    def or_(self, a: polars.Expr, b: polars.Expr) -> polars.Expr:
        return a | b

    def and_(self, a: polars.Expr, b: polars.Expr) -> polars.Expr:
        return a & b

    def xor_(self, a: polars.Expr, b: polars.Expr) -> polars.Expr:
        return a ^ b

    def apply(self, expr: polars.Expr) -> list[str]:
        return self.LEX.filter(expr).select("ortho").to_series().unique().to_list()

    def split(self, word: str) -> list[str]:
        tmp = self.LEX.filter(polars.col("ortho") == word).select("phon")
        res: set[str] = set()
        for row in tmp.iter_rows():
            res.add(row[0])
        return list(res)

    def tail(self, s: str, n: int) -> str:
        return s[-n:]

    def head(self, s: str, n: int) -> str:
        return s[:n]


def main():
    m = Mots()
    print("Hello from mesmots!")
    r1 = m.endswith(m.tail(m.split("saisissant")[0], 2))
    print("r1", m.apply(r1), "r1")
    r2 = m.startswith(m.head(m.split("bonjour")[0], 2))
    print("r2", m.apply(r2), "r2")
    r3 = m.and_(r1, r2)
    print("r3", m.apply(r3), "r3")
    r4 = m.category(Mots.Category.ADJ)
    print("r4", m.apply(m.and_(m.or_(r1, r2), r4)), "r4")


if __name__ == "__main__":
    main()
