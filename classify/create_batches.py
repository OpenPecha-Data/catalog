import csv
import re
from pathlib import Path


def write_batch(pecha_ids, batch):
    batch_path = Path(f"./classify/csv_files/batch{batch}.txt")
    batch_path.write_text(pecha_ids, encoding='utf-8')



if __name__ == "__main__":
    num = 0
    batch = 0
    pecha_ids = ""
    with open(f"./classify/csv_files/catalog.csv", newline="") as file:
        pechas = list(csv.reader(file, delimiter=","))
        for pecha in pechas[1:]:
            pecha_id = re.search("\[.+\]", pecha[0])[0][1:-1]
            num += 1
            pecha_ids += pecha_id+"\n"
            if num == 2000:
                batch += 1
                write_batch(pecha_ids, batch)
                pecha_ids = ""
                num = 0
                
                