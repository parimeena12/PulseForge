import psycopg
def get_connection():
    connection = psycopg.connect(
        host="localhost",
        port=5433,
        dbname="pulseforge",
        user="pulseforge_user",
        password="pulseforge_dev"
    )

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                current_database(),
                current_user,
                inet_server_addr(),
                inet_server_port(),
                version()
        """)
        print("DATABASE CONNECTION:", cursor.fetchone())

    return connection

