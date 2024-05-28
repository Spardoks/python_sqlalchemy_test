import sqlalchemy as sq
import tabulate
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Publisher(Base):
    __tablename__ = "publisher"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=60), unique=True, nullable=False)

    def __repr__(self):
        return f"<Publisher: id {self.id} | name {self.name}>"


class Shop(Base):
    __tablename__ = "shop"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=60), unique=True, nullable=False)

    def __repr__(self):
        return f"<Shop: id {self.id} | name {self.name}>"


class Book(Base):
    __tablename__ = "book"

    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(length=60), nullable=False)
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey("publisher.id"), nullable=False)

    publisher = relationship(Publisher)

    def __repr__(self):
        return f"<Book: id {self.id} | title {self.title}> | id_publisher {self.id_publisher}"


class Stock(Base):
    __tablename__ = "stock"

    id = sq.Column(sq.Integer, primary_key=True)
    id_book = sq.Column(sq.Integer, sq.ForeignKey("book.id"), nullable=False)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey("shop.id"), nullable=False)
    count = sq.Column(sq.Integer, nullable=False)

    book = relationship(Book)
    shop = relationship(Shop)

    def __repr__(self):
        return f"<Stock: id {self.id} | id_book {self.id_book} | id_shop {self.id_shop} | count {self.count}>"


class Sale(Base):
    __tablename__ = "sale"

    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(sq.Float, nullable=False)
    date_sale = sq.Column(sq.DateTime, nullable=False)
    count = sq.Column(sq.Integer, nullable=False)
    id_stock = sq.Column(sq.Integer, sq.ForeignKey("stock.id"), nullable=False)

    stock = relationship(Stock)

    def __repr__(self):
        return f"<Sale: id {self.id} | price {self.price} | count {self.count}, date {self.date_sale}, id_stock {self.id_stock}>"


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


##################### QUERIES#####################


# specific query example
def print_sales_by_publisher_name_specific(session, publisher_name):
    data = []
    data.append(
        [
            "Название книги",
            "Название магазина, в котором была куплена эта книга",
            "Стоимость покупки",
            "Дата покупки",
        ]
    )
    sales_by_publisher = (
        session.query(Sale)
        .join(Stock)
        .join(Shop)
        .join(Book)
        .join(Publisher)
        .filter(Publisher.name == publisher_name)
    )
    for sale in sales_by_publisher.all():
        id_stock = sale.id_stock
        shop_by_stock_id = (
            session.query(Shop).join(Stock).filter(Stock.id == id_stock).first()
        )
        book_by_stock_id = (
            session.query(Book).join(Stock).filter(Stock.id == id_stock).first()
        )

        shop_name = shop_by_stock_id.name
        book_title = book_by_stock_id.title
        cost = sale.price * sale.count
        date = sale.date_sale
        data.append([book_title, shop_name, cost, date])
    results = tabulate.tabulate(data)
    print(results)
    print(f"Publisher: {publisher_name}")


# print all data example
def print_all_data(session):
    query = session.query(Publisher).all()
    for publisher in query:
        print(publisher)
    query = session.query(Shop).all()
    for shop in query:
        print(shop)
    query = session.query(Book).all()
    for book in query:
        print(book)
    query = session.query(Stock).all()
    for stock in query:
        print(stock)
    query = session.query(Sale).all()
    for sale in query:
        print(sale)


# complex find query example
def print_sales_by_publisher_id(session, publisher_id):
    # SELECT * FROM sale
    # JOIN stock ON sale.id_stock = stock.id
    # JOIN shop ON shop.id = stock.id_shop
    # JOIN book ON stock.id_book = book.id
    # JOIN publisher ON book.id_publisher = publisher.id
    # WHERE publisher.id = 'publisher_id';
    query = (
        session.query(Sale)
        .join(Stock)
        .join(Book)
        .join(Publisher)
        .filter(Publisher.id == publisher_id)
    )
    for sale in query:
        print(sale)


# subquery example
def print_saled_books(session):
    stock_books = session.query(Stock).join(Sale).subquery()
    sale_books = session.query(Book).join(stock_books, Book.id == stock_books.c.id_book)
    for c in sale_books:
        print(c)


# delete example
def delete_sale_by_id(session, sale_id):
    session.query(Sale).filter(Sale.id == sale_id).delete()
    session.commit()


# add example
def add_publisher(session, name, id=100):
    publisher = Publisher(id=id, name=name)
    session.add(publisher)
    session.commit()


# update example
def update_publisher_name(session, id, name):
    session.query(Publisher).filter(Publisher.id == id).update({Publisher.name: name})
    session.commit()
