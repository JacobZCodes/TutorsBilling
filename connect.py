import psycopg2
import credentials
if __name__ == "__main__":

    dbname = credentials.db_name
    user = credentials.db_user
    password = credentials.db_pass# MOTHERFUCKA HIDE THIS SHIT!
    host = credentials.db_host
    port = '5432'

    conn_string = f"dbname={dbname} user={user} password={password} host={host} port={port}"

    conn = psycopg2.connect(conn_string)

    curr = conn.cursor()

    # cur.execute does stuff
    curr.execute("""CREATE TABLE IF NOT EXISTS clients(firstName VARCHAR(40), lastName VARCHAR(40), phoneNumber BIGINT, email VARCHAR(255), owes INTEGER)             
    """)

    conn.commit()

    curr.close()
    conn.close()