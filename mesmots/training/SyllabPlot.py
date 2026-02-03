from collections.abc import Iterable
import polars as pl
import asyncio

async def to_dict(lf: pl.LazyFrame):
    lf = lf.select("orthosyll")
    df = await lf.collect_async()
    res: list[str] = [
        row[0]
        for row in df.iter_rows()
    ]
    return res


class SyllabPlot:
    schema: dict[str, type[pl.String] | type[pl.UInt32]] = {
        "orthosyll": pl.String,
        "syll": pl.String,
        "ortho_before": pl.String,
        "ortho_after": pl.String,
        "nb_usage": pl.UInt32,
    }
    df: pl.DataFrame = pl.DataFrame(schema=schema)
    colums: Iterable[str] = ("orthosyll", "syll", "ortho_before", "ortho_after", "nb_usage")

    def __init__(self, encoder: str) -> None:
        self.df = pl.concat((
            self.df,
            pl.read_csv(encoder, has_header=True, schema=self.schema)
        ))

    async def get_usual_before_after(self, ortho: str) -> tuple[list[str], list[str]]:
        res = (
            self.df
            .lazy()
            .filter(
                (pl.col("ortho_before") == ortho)
                | (pl.col("ortho_after") == ortho)
            )
            .select("ortho_before", "ortho_after", "orthosyll", "nb_usage")
            .sort("nb_usage")
        )
        res_after_ = (
            res
            .filter(pl.col("ortho_before") == ortho)
            .select("ortho_before", "orthosyll")
            .unique("orthosyll", keep="first", maintain_order=True)
        )
        res_before_ = (
            res
            .filter(pl.col("ortho_after") == ortho)
            .select("ortho_after", "orthosyll")
            .unique("orthosyll", keep="first", maintain_order=True)
        )
        res_before_list, res_after_list = await asyncio.gather(to_dict(res_before_), to_dict(res_after_))
        return res_before_list, res_after_list


async def main():
    proba = SyllabPlot("./dataset/ProbaEncoder.csv")
    print(
        await proba.get_usual_before_after("jour")
    )

if __name__ == "__main__":
    asyncio.run(main())
