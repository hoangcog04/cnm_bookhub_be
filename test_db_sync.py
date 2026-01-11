import pymysql

def test():
    params = [
        {'host': 'localhost', 'user': 'root', 'password': 'root', 'db': 'cn_bookhub'},
        {'host': '127.0.0.1', 'user': 'root', 'password': 'root', 'db': 'cn_bookhub'},
        {'host': 'localhost', 'user': 'root', 'password': '', 'db': 'cn_bookhub'},
        {'host': '127.0.0.1', 'user': 'root', 'password': '', 'db': 'cn_bookhub'},
        {'host': 'localhost', 'user': 'root', 'password': 'root', 'db': 'cnm_bookhub_be'},
        {'host': '127.0.0.1', 'user': 'root', 'password': 'root', 'db': 'cnm_bookhub_be'},
    ]
    
    for p in params:
        print(f"Testing {p}...")
        try:
            conn = pymysql.connect(**p)
            print("SUCCESS!")
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                print(f"Tables: {[r[0] for r in cursor.fetchall()]}")
            conn.close()
            return
        except Exception as e:
            print(f"  FAILED: {e}")

if __name__ == "__main__":
    test()
