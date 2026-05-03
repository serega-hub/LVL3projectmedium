import telebot
from telebot import types
from config import TOKEN, DATABASE
from bdtehpodderjka import *

bot = telebot.TeleBot(TOKEN)
manager = DB_Manager(DATABASE)

def notify_admins(request_id, username, dept, issue):
    admins = manager.get_admins()
    print(f"Список админов из БД: {admins}")
    text = (f"🚨 <b>Новая заявка №{request_id}</b>\n"
            f"👤 От: @{username}\n"
            f"🏢 Отдел: {dept}\n"
            f"📝 Проблема: {issue}")
    
    
    markup = types.InlineKeyboardMarkup()
    btn_done = types.InlineKeyboardButton("✅ Решено", callback_data=f"status_done_{request_id}")
    btn_process = types.InlineKeyboardButton("⏳ В работе", callback_data=f"status_work_{request_id}")
    markup.add(btn_process, btn_done)

    for admin_id in admins:
        try:
            bot.send_message(admin_id, text, parse_mode="HTML", reply_markup=markup)
        except Exception as e:
            print(f"Не удалось отправить сообщение админу {admin_id}: {e}")


def save_request(message, dept):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Unknown"
        issue = message.text
        
        # 1. Сохраняем
        manager.insert_request(user_id, username, dept, issue)
        
        # 2. Уведомляем пользователя сразу
        bot.send_message(message.chat.id, "✅ Ваша заявка принята!")

        # 3. Уведомляем админов
        # Передаем просто строчку вместо ID, если не получается вытащить ID из БД
        notify_admins("НОВАЯ", username, dept, issue)
        
    except Exception as e:
        print(f"Ошибка в save_request: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❓ FAQ (Частые вопросы)", "🛠 Написать в поддержку")
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "❓ FAQ (Частые вопросы)")
def show_faq_list(message):
    faq_items = manager.get_faq_list() 
    markup = types.InlineKeyboardMarkup()
    
    for faq_id, question in faq_items:
        
        markup.add(types.InlineKeyboardButton(text=question, callback_data=f"faq_{faq_id}"))
    
    bot.send_message(message.chat.id, "Выберите интересующий вас вопрос:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('faq_'))
def answer_faq(call):
    
    faq_id = int(call.data.split('_')[1])
    
    
    result = manager.get_answer_by_id(faq_id)
    
    if result:
        question, answer = result
        bot.send_message(call.message.chat.id, f"<b>{question}</b>\n\n{answer}", parse_mode="HTML")
    
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda m: m.text == "🛠 Написать в поддержку")
def select_dept(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Программисты", callback_data="dept_dev"))
    markup.add(types.InlineKeyboardButton("Отдел продаж", callback_data="dept_sales"))
    bot.send_message(message.chat.id, "Выберите отдел:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('dept_'))
def ask_issue(call):
    dept = "Программисты" if call.data == "dept_dev" else "Отдел продаж"
    msg = bot.send_message(call.message.chat.id, f"Опишите проблему для отдела {dept}:")
    bot.register_next_step_handler(msg, save_request, dept)

def save_requestt(message, dept):
    manager.insert_request(message.from_user.id, message.from_user.username, dept, message.text)
    bot.send_message(message.chat.id, "✅ Ваша заявка сохранена в БД!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('status_'))
def change_status(call):
    
    data = call.data.split('_')
    new_status_code = data[1]
    req_id = int(data[2])
    
    new_status = "в работе" if new_status_code == "work" else "решено"
    
    
    manager.update_request_status(req_id, new_status)
    
    
    req_data = manager.get_request_by_id(req_id)
    user_id = req_data[1] 
    
    bot.answer_callback_query(call.id, f"Статус изменен на: {new_status}")
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id, 
                          text=call.message.text + f"\n\n🟢 Статус: {new_status}")
    
    
    bot.send_message(user_id, f"📢 Статус вашей заявки №{req_id} изменен на: <b>{new_status}</b>", parse_mode="HTML")


@bot.message_handler(commands=['admin_setup'])
def setup_admin(message):
    
    MY_ID = 7176869463 
    if message.from_user.id == MY_ID:
        manager.add_admin(message.from_user.id)
        bot.send_message(message.chat.id, "Вы успешно добавлены в список админов!")
bot.infinity_polling()