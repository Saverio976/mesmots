from collections.abc import Iterable
from dataclasses import dataclass
from typing import final
import polars as pl
from utils import get_likeness_word

@dataclass(slots=True, kw_only=True)
class SyllabRelationDecoder:
    orthosyll: str
    ortho_before: str
    ortho_after: str

@final
@dataclass(slots=True, kw_only=True)
class SyllabRelationEncoder(SyllabRelationDecoder):
    syll: str
    nb_usage: int

@final
@dataclass(slots=True, kw_only=True)
class SyllabLikeness:
    input: SyllabRelationDecoder
    target: SyllabRelationEncoder
    score: float


def get_likeness(input: SyllabRelationDecoder, target: SyllabRelationEncoder, max_value: int = 50, coef_max: int = 50) -> SyllabLikeness:
    score = 0.0
    score += get_likeness_word(input.ortho_before, target.ortho_before, reverse=True, max_value=max_value, len_penaly=True)
    score += get_likeness_word(input.ortho_after, target.ortho_after, reverse=False, max_value=max_value, len_penaly=True)
    return SyllabLikeness(input=input, target=target, score=(score * target.nb_usage) / coef_max)


def apply_likeness(row: dict) -> float:
    orthosyll = row["orthosyll"]
    syll = row["syll"]
    ortho_before = row["ortho_before"]
    ortho_after = row["ortho_after"]
    nb_usage = row["nb_usage"]
    syllab_len_max = row["syllab_len_max"]
    nb_usage_max = row["nb_usage_max"]
    input_ortho_before = row["input_ortho_before"]
    input_orthosyll = row["input_orthosyll"]
    input_ortho_after = row["input_ortho_after"]
    assert isinstance(orthosyll, str)
    assert isinstance(syll, str)
    assert isinstance(ortho_before, str)
    assert isinstance(ortho_after, str)
    assert isinstance(nb_usage, int)
    assert isinstance(syllab_len_max, int)
    assert isinstance(nb_usage_max, int)
    assert isinstance(input_ortho_before, str)
    assert isinstance(input_orthosyll, str)
    assert isinstance(input_ortho_after, str)
    score = 0.0
    score += get_likeness_word(
        s=input_ortho_before,
        x=ortho_before,
        reverse=True,
        max_value=syllab_len_max,
        len_penaly=True
    )
    score += get_likeness_word(
        s=input_ortho_after,
        x=ortho_after,
        reverse=False,
        max_value=syllab_len_max,
        len_penaly=True
    )
    return (score * nb_usage) / nb_usage_max


class SyllabDecoder:
    schema: dict[str, type[pl.String] | type[pl.UInt32]] = {
        "orthosyll": pl.String,
        "syll": pl.String,
        "ortho_before": pl.String,
        "ortho_after": pl.String,
        "nb_usage": pl.UInt32,
    }
    df: pl.DataFrame = pl.DataFrame(schema=schema)
    colums: Iterable[str] = ("orthosyll", "syll", "ortho_before", "ortho_after", "nb_usage")
    syllab_len_max: int = 50
    nb_usage_max: int = 50

    def __init__(self, encoder: str) -> None:
        self.df = pl.concat((
            self.df,
            pl.read_csv(encoder, has_header=True, schema=self.schema)
        )).select(*self.colums)
        self.syllab_len_max = max(
            self.df
            .select("ortho_before", "ortho_after")
            .with_columns(pl.col("*").str.len_chars())
            .max().transpose().to_series().to_list()
        )
        self.nb_usage_max = max(
            self.df
            .select("nb_usage")
            .max().transpose().to_series().to_list()
        )
        self.df = self.df.with_columns(
            pl.lit(self.syllab_len_max).alias("syllab_len_max"),
            pl.lit(self.nb_usage_max).alias("nb_usage_max"),
        )

    def get(self, relation: SyllabRelationDecoder, nb_result: int = 5) -> list[tuple[float, str]]:
        res = (
            self.df
            .filter(pl.col("orthosyll") == relation.orthosyll)
            .with_columns(
                pl.lit(relation.ortho_before).alias("input_ortho_before"),
                pl.lit(relation.orthosyll).alias("input_orthosyll"),
                pl.lit(relation.ortho_after).alias("input_ortho_after"),
            )
            .with_columns(
                pl.struct(pl.all())
                .map_elements(apply_likeness)
                .cast(pl.Float32)
                .alias("score")
            )
            .sort("score", descending=True)
            .unique(["syll"], keep="first", maintain_order=True)
            .head(nb_result)
            .select("score", "syll")
        )
        ranked: list[tuple[float, str]] = []
        for row in res.iter_rows():
            assert isinstance(row[0], float)
            assert isinstance(row[1], str)
            ranked.append((row[0], row[1]))
        return ranked

if __name__ == "__main__":
    proba = SyllabDecoder("./dataset/ProbaEncoder.csv")
    print(
        proba.get(SyllabRelationDecoder(orthosyll="bon", ortho_before="", ortho_after="jour"))
    )
