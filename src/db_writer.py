import pandas as pd
from sqlalchemy import create_engine

class DatabaseWriter:
    def __init__(self, host, port, db, user, password):
        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
        self.engine = create_engine(connection_string)

    def write_logs(self, logs_df):
        logs_df.to_sql('logs', self.engine, if_exists='append', index=False)

    def export_to_csv(self, logs_df, output_path):
        logs_df.to_csv(output_path, index=False)