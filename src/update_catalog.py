import csv

Catalog_fn = 'data/catalog.csv'

def add_id_url(row):
    id = row[0]
    row[0] = f'[{id}](https://github.com/OpenPecha/{id})'
    return row


def update_catalog():
    updated_catalog = []
    with open(Catalog_fn) as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if row[0][0] == 'P':
                updated_catalog.append(add_id_url(row))

    with open(Catalog_fn, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(updated_catalog)


if __name__ == "__main__":
    update_catalog()
