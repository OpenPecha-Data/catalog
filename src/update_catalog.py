import csv
from pathlib import Path
import pandas


def get_poti_layers(path):
    layers = {}
    for op in path.iterdir(): 
        op_name = op.name
        layers[op.name] = '_'.join([layer.stem for layer in (op/f'{op_name}.opf'/'layers').iterdir()])
    
    return [layers[key] for key in sorted(layers.keys())]

def update(ops_path, catalog_path):
    layers = get_poti_layers(ops_path)

    df = pandas.read_csv(catalog_path)
    print(len(df), len(layers))
    df['Layers'] = layers
    df.to_csv(catalog_path, index=False)
    


if __name__ == "__main__":
    ops_path = Path('../../openpecha-toolkit/usage/layer_output/')
    catalog_path = '../data/catalog.csv'

    update(ops_path, catalog_path)