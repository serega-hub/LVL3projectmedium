import sqlite3
from config import DATABASE

class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            
            conn.execute('''CREATE TABLE IF NOT EXISTS requests (
                            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            username TEXT,
                            department TEXT,
                            issue TEXT,
                            status TEXT DEFAULT 'открыт')''')
            
            
            conn.execute('''CREATE TABLE IF NOT EXISTS faq (
                            faq_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT,
                            answer TEXT)''')
            conn.execute('''CREATE TABLE IF NOT EXISTS admins (
                            user_id INTEGER PRIMARY KEY)''')
            conn.commit()

    def __execute(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(sql, data)
            conn.commit()

    def insert_request(self, user_id, username, department, issue):
        sql = "INSERT INTO requests (user_id, username, department, issue) VALUES (?, ?, ?, ?)"
        self.__execute(sql, (user_id, username, department, issue))

    def insert_faq(self, data):
        
        sql = "INSERT INTO faq (question, answer) VALUES (?, ?)"
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def get_faq_questions(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT question FROM faq")
            return [row[0] for row in cur.fetchall()]

    def get_answer(self, question):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT answer FROM faq WHERE question = ?", (question,))
            result = cur.fetchone()
            return result[0] if result else "Извините, ответ не найден."
    def get_faq_list(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            
            cur.execute("SELECT faq_id, question FROM faq")
            return cur.fetchall()

    def get_answer_by_id(self, faq_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT question, answer FROM faq WHERE faq_id = ?", (faq_id,))
        return cur.fetchone()
    def add_admin(self, user_id):
        sql = "INSERT OR IGNORE INTO admins (user_id) VALUES (?)"
        self.__execute(sql, (user_id,))

    def get_admins(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM admins")
            return [row[0] for row in cur.fetchall()]

    def get_request_by_id(self, request_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM requests WHERE request_id = ?", (request_id,))
            return cur.fetchone()

    def update_request_status(self, request_id, new_status):
        sql = "UPDATE requests SET status = ? WHERE request_id = ?"
        self.__execute(sql, (new_status, request_id))

    
if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()
    
    
    faq_data = [
        ("Как оформить заказ?", "Для оформления заказа, пожалуйста, выберите интересующий вас товар и нажмите кнопку 'Добавить в корзину', затем перейдите в корзину и следуйте инструкциям для завершения покупки."),
        ("Как узнать статус моего заказа?", "Вы можете узнать статус вашего заказа, войдя в свой аккаунт на нашем сайте и перейдя в раздел 'Мои заказы'. Там будет указан текущий статус вашего заказа."),
        ("Как отменить заказ?", "Если вы хотите отменить заказ, пожалуйста, свяжитесь с нашей службой поддержки как можно скорее. Мы постараемся помочь вам с отменой заказа до его отправки."),
        ("Что делать, если товар пришел поврежденным?", "При получении поврежденного товара, пожалуйста, сразу свяжитесь с нашей службой поддержки и предоставьте фотографии повреждений. Мы поможем вам с обменом или возвратом товара."),
        ("Как связаться с вашей технической поддержкой?", "Вы можете связаться с нашей технической поддержкой через телефон на нашем сайте или написать нам в чат-бота."),
        ("Как узнать информацию о доставке?", "Информацию о доставке вы можете найти на странице оформления заказа на нашем сайте. Там указаны доступные способы доставки и сроки.")
    ]
    
    
    conn = sqlite3.connect(DATABASE)
    conn.execute("DELETE FROM faq")
    conn.commit()
    
    manager.insert_faq(faq_data)
    print("FAQ успешно загружены в базу данных.")