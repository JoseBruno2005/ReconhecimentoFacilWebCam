import psycopg2


def conexaodb():
    return psycopg2.connect(
        dbname="reconhecimentoFacial",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )