from collections.abc import Iterable
from dataclasses import dataclass, asdict
from typing import final
import polars as pl

@final
@dataclass(slots=True, kw_only=True)
class SyllabRelationEncoder:
    orthosyll: str
    syll: str
    ortho_before: str
    ortho_after: str
    dict = asdict

class SyllabEncoder:
    schema: dict[str, type[pl.String] | type[pl.Int32]] = {
        "orthosyll": pl.String,
        "syll": pl.String,
        "ortho_before": pl.String,
        "ortho_after": pl.String,
        "nb_usage": pl.Int32,
    }
    df: pl.DataFrame = pl.DataFrame(schema=schema)
    colums: Iterable[str] = ("orthosyll", "syll", "ortho_before", "ortho_after", "nb_usage")
    tmp_relations: list[SyllabRelationEncoder] = []

    def __init__(self) -> None:
        pass

    def add(self, relation: SyllabRelationEncoder):
        self.tmp_relations.append(relation)

    def finalize(self):
        self.df = pl.concat((
            self.df,
            pl.DataFrame([
                {
                    **x.dict(),
                    "nb_usage": 0
                }
                for x in self.tmp_relations
            ], schema=self.schema)
        ))
        self.tmp_relations.clear()
        self.df = (
            self.df
            .with_columns(
                pl.len()
                .over(SyllabRelationEncoder.__slots__)
                .alias("nb_usage")
            )
            .unique(list(self.colums))
        )

    def write(self, file: str):
        self.df.write_csv(file)


def word_split(word: str) -> list[str]:
    return [""] + word.split("-") + [""]

def pair_valid(word_a: list[str], word_b: list[str]) -> bool:
    return len(word_a) == len(word_b)

def get_data(proba: SyllabEncoder, file: str):
    df = (
        pl
        .read_csv(file, has_header=True)
        .drop_nulls()
        .filter(pl.col("ortho").str.contains("-").not_())
        .select("orthosyll", "syll")
    )
    for row in df.iter_rows():
        assert isinstance(row[0], str)
        assert isinstance(row[1], str)
        orthosyll = word_split(row[0])
        syll = word_split(row[1])
        if not pair_valid(orthosyll, syll):
            continue
        for i in range(1, len(syll) - 1):
            proba.add(SyllabRelationEncoder(
                orthosyll=orthosyll[i],
                syll=syll[i],
                ortho_before=orthosyll[i - 1],
                ortho_after=orthosyll[i + 1]
            ))

if __name__ == "__main__":
    proba = SyllabEncoder()
    get_data(proba, "./dataset/Lexique383.csv")
    proba.finalize()
    print(proba.df)
    proba.write("./dataset/ProbaEncoder.csv")
