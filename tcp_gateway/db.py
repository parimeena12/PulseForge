import psycopg


def get_connection():
   return psycopg.connect(
         host = "localhost",
         port = 5432,
         dbname = "pulseforge",
         user = "pulseforge_user",
         password ="pulseforge_dev"
)


