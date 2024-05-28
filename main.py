import json
import os

import sqlalchemy
from dotenv import dotenv_values, load_dotenv
from sqlalchemy.orm import sessionmaker

from models import (
    Book,
    Publisher,
    Sale,
    Shop,
    Stock,
    create_tables,
    print_sales_by_publisher_name_specific,
)

if __name__ == "__main__":
    # Prepare engine and session_maker
    config = dotenv_values(".env")
    load_dotenv()
    DB_USER = config["DB_USER"]
    DB_PASSWORD = config["DB_PASSWORD"]
    DB_IP = "localhost"
    DB_PORT = "5432"
    DB_NAME = "book_shop_db"
    DB_PROTOCOL = "postgresql+psycopg2"
    DSN = f"{DB_PROTOCOL}://{DB_USER}:{DB_PASSWORD}@{DB_IP}:{DB_PORT}/{DB_NAME}"
    engine = sqlalchemy.create_engine(DSN)
    Session = sessionmaker(bind=engine)

    # Prepare tables
    create_tables(engine)

    # Prepare test data
    creation_session = Session()
    with open("tests_data.json", "r", encoding="utf-8") as fd:
        data = json.load(fd)
    for record in data:
        model = {
            "publisher": Publisher,
            "shop": Shop,
            "book": Book,
            "stock": Stock,
            "sale": Sale,
        }[record.get("model")]
        creation_session.add(model(id=record.get("pk"), **record.get("fields")))
    creation_session.commit()
    creation_session.close()

    # Test query
    query_session = Session()
    publisher_name = "O\u2019Reilly"
    print_sales_by_publisher_name_specific(
        session=query_session, publisher_name=publisher_name
    )
    query_session.close()
