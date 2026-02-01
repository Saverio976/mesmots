from collections.abc import Iterable
import polars as pl
try:
    from .utils import get_likeness_word
except ImportError:
    from utils import get_likeness_word

def apply_likeness(row: dict) -> int:
    before = row["before"]
    ortho_before = row["ortho_before"]
    ortho_after = row["ortho_after"]
    orthosyll = row["orthosyll"]
    word = row["word"]
    max_value = row["max_value"]
    assert isinstance(before, str)
    assert isinstance(ortho_before, str)
    assert isinstance(orthosyll, str)
    assert isinstance(word, str)
    assert isinstance(max_value, int)
    word_now = word[:len(orthosyll)]
    word_after = word[len(orthosyll):]
    score = 0
    params = {
        "max_value": max_value,
        "len_penaly": False,
    }
    score += get_likeness_word(s=ortho_before, x=before, reverse=True, **params)
    score += get_likeness_word(s=orthosyll, x=word_now, reverse=False, **params)
    score += get_likeness_word(s=ortho_after, x=word_after, reverse=False, **params)
    return score

class SyllabTokenize:
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

    def __init__(self, encoder: str) -> None:
        self.df = pl.concat((
            self.df,
            pl.read_csv(encoder, has_header=True, schema=self.schema)
        ))
        self.syllab_len_max = max(
            self.df
            .select("ortho_before", "ortho_after")
            .with_columns(pl.col("*").str.len_chars())
            .max().transpose().to_series().to_list()
        )
        self.df = self.df.with_columns(pl.lit(self.syllab_len_max).alias("max_value"))

    def __tokenize(self, word: str, before: list[str]) -> list[str] | None:
        if word == "":
            return before
        res = (
            self.df
            .with_columns(
                pl.lit(word).alias("word"),
                pl.lit(before[-1]).alias("before")
            )
            .filter(pl.col("word").str.starts_with(pl.col("orthosyll")))
            .with_columns(
                pl.struct(pl.all())
                .map_elements(apply_likeness, return_dtype=pl.Int32)
                .alias("score")
            )
            .sort("score", descending=True)
        )
        possibilities = res .select("orthosyll")
        for row in possibilities.iter_rows():
            assert isinstance(row[0], str)
            word_test = word[len(row[0]):]
            before_test = before + [row[0]]
            recursive = self.__tokenize(word_test, before_test)
            if recursive is None:
                continue
            return recursive
        return None


    def tokenize(self, word: str) -> list[str] | None:
        res = self.__tokenize(word, [""])
        if res is None:
            return res
        if len(res) == 0:
            return res
        if res[0] == "":
            return res[1:]
        return res

if __name__ == "__main__":
    proba = SyllabTokenize("./dataset/ProbaEncoder.csv")
    print(
        proba.tokenize("macron")
    )
