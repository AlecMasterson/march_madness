
from concurrent.futures import as_completed, Future, ProcessPoolExecutor, wait
from tqdm import tqdm
from typing import List
import pandas

global df
df = pandas.DataFrame([{"A": 0}, {"A": 0}, {"A": 0}])

def main(X: List[int]) -> None:
    futures: List[Future] = []

    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(submit, x) for x in X]

        for _ in tqdm(as_completed(futures), total=len(futures)):
            pass

        wait(futures)

    results: List[tuple] = [future.result() for future in futures]

def submit(x: int) -> tuple:
    global df
    df.loc[x, "A"] = 1

    return (df.loc[x, "A"])


main([i for i in range(len(df))])
print(df)
