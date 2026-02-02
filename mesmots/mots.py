from collections.abc import Iterable
from enum import Enum
import polars as pl

from training.SyllabTokenize import SyllabTokenize
from training.SyllabDecoder import SyllabDecoder


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

    lex: pl.DataFrame
    subset: Iterable[str]
    syllab_tokenize: SyllabTokenize
    syllab_decoder: SyllabDecoder

    def __init__(self, dataset_dir: str = "./dataset/", subset: Iterable[str] = ("ortho", "phon", "cgram"), **kwargs) -> None:
        self.lex = pl.read_csv(
            dataset_dir + "Lexique383.csv",
            has_header=True,
            **kwargs,
        ).select(*subset).drop_nulls()
        self.subset = subset
        self.syllab_tokenize = SyllabTokenize(dataset_dir + "ProbaEncoder.csv")
        self.syllab_decoder = SyllabDecoder(dataset_dir + "ProbaEncoder.csv")

    def endswith(self, phon: str) -> pl.Expr:
        return pl.col("phon").str.ends_with(phon)

    def startswith(self, phon: str) -> pl.Expr:
        return pl.col("phon").str.starts_with(phon)

    def contains(self, phon: str) -> pl.Expr:
        return pl.col("phon").str.contains(phon)

    def category(self, cat: Category) -> pl.Expr:
        return pl.col("cgram") == cat.value

    def or_(self, a: pl.Expr, b: pl.Expr) -> pl.Expr:
        return a | b

    def and_(self, a: pl.Expr, b: pl.Expr) -> pl.Expr:
        return a & b

    def xor_(self, a: pl.Expr, b: pl.Expr) -> pl.Expr:
        return a ^ b

    def apply(self, expr: pl.Expr) -> list[str]:
        return self.lex.filter(expr).select("ortho").to_series().unique().to_list()

    def split(self, word: str) -> list[str]:
        tmp = (
            self.lex
            .filter(pl.col("ortho") == word)
            .select("phon")
            .unique("phon")
        )
        if tmp.height:
            return tmp.transpose().to_series().to_list()
        print("not found in db, creating one...")
        tokens = self.syllab_tokenize.tokenize(word)
        if tokens is None:
            return []
        tokens = [""] + tokens + [""]
        sylls: list[str] = []
        for i in range(1, len(tokens) - 1):
            syll = self.syllab_decoder.get(tokens[i], tokens[i - 1], tokens[i + 1])
            if len(syll) == 0:
                return []
            sylls.append(syll[0][1])
        return ["".join(sylls)]

    def tail(self, s: str, n: int) -> str:
        return s[-n:]

    def head(self, s: str, n: int) -> str:
        return s[:n]

    def write_csv(self, file: str):
        self.lex.write_csv(file)


def main():
    m = Mots()
    print(m.split("bonjour"))
    print(m.split("macron"))
    #m = Mots()
    #print("Hello from mesmots!")
    #r1 = m.endswith(m.tail(m.split("saisissant")[0], 2))
    #print("r1", m.apply(r1), "r1")
    #r2 = m.startswith(m.head(m.split("bonjour")[0], 2))
    #print("r2", m.apply(r2), "r2")
    #r3 = m.and_(r1, r2)
    #print("r3", m.apply(r3), "r3")
    #r4 = m.category(Mots.Category.ADJ)
    #print("r4", m.apply(m.and_(m.or_(r1, r2), r4)), "r4")
    #m.write_csv("./Lexique383/Lexique383.csv")
    import os.path
    p = "./dataset/Lexique383.tsv"
    if os.path.isfile(p):
        print("Generating csv")
        df = pl.read_csv(
            p,
            has_header=True,
            separator="\t",
        ).select("ortho", "phon", "cgram", "syll", "orthosyll").drop_nulls()
        print(df)
        df.write_csv("./dataset/Lexique383.csv")
    else:
        print("TSV not found")

if __name__ == "__main__":
    main()
