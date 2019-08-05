"""Help to upload statistical models to MongoDB."""

from config import Config
from models import MongoClient, StatsModel
from mlp_tools.helpers import ModelType
import sys


if __name__ == '__main__':

    if len(sys.argv) < 4:
        raise Exception("Please, specify\n1. path to the model dump file\n2. model id\n3. " +\
            "model type")

    model_file = sys.argv[1]
    model_id = sys.argv[2]
    model_type = sys.argv[3]

    if not ModelType.has_value(model_type):
        raise Exception("Model type not supported. Available types: [btts, scoreline, totals]")

    client = MongoClient(Config()['database'])
    stats_model = StatsModel()

    with open(model_file, mode='rb') as file:
        model_content = file.read()

    stats_model.update(model_id, model_type, model_content)
    client.conn.close()
