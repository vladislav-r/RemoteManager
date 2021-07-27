import telebot
from telebot import types
from datetime import datetime
import os
import config
import subprocess


TOKEN = config.TOKEN
bot = telebot.TeleBot(TOKEN, parse_mode=None)


markup = types.ReplyKeyboardMarkup( True, row_width=1)
itembtn1 = types.KeyboardButton('Выключить')
itembtn2 = types.KeyboardButton('Перезагрузить')
itembtn3 = types.KeyboardButton('Сон')
itembtn4 = types.KeyboardButton('Отмена')
itembtn5 = types.KeyboardButton('Запланировать')
itembtn6 = types.KeyboardButton('Отменить запланированную задачу')
markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)

sleepMarkup = types.InlineKeyboardMarkup()
sleepBtn = types.InlineKeyboardButton("Да", callback_data='sleepTrue')
sleepMarkup.add(sleepBtn)


scheduleMarkup = types.InlineKeyboardMarkup()
button1 = types.InlineKeyboardButton('Выключение', callback_data='shutdown')
scheduleMarkup.add(button1)


scheduleMarkupCancel = types.InlineKeyboardMarkup()
button_cancel= types.InlineKeyboardButton('Выключение', callback_data='shutdown-cancel')
scheduleMarkupCancel.add(button_cancel)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, message.chat.id, reply_markup=markup)

@bot.message_handler(content_types=['text'])
def choose_operation(message):
    if message.text == 'Выключить':
        os.system("shutdown /s /t 30")
        bot.send_message(message.chat.id, 'Выключение\nЕсть 30 секунд на отмену')
    elif message.text == 'Перезагрузить':
        os.system("shutdown /r /t 30 ")
        bot.send_message(message.chat.id, 'Перезагрузка\nЕсть 30 секунд на отмену')
    elif message.text == 'Сон':
        bot.send_message(message.chat.id, 'Переход в режим сна, ты уверен?', reply_markup = sleepMarkup)
    elif message.text == 'Отмена':
        os.system("shutdown /a")
        bot.send_message(message.chat.id, 'Отмена произведена успешно')
    elif message.text == 'Запланировать':
        bot.send_message(message.chat.id, 'Что запланировать?', reply_markup = scheduleMarkup)
    elif message.text == 'Отменить запланированную задачу':
        bot.send_message(message.chat.id, 'Задачи:', reply_markup = scheduleMarkupCancel)
    


@bot.callback_query_handler(func=lambda call: True)
def check_schedule(call):
    if call.data == 'shutdown':
        time = bot.send_message(call.message.chat.id, 'Напиши время в формате HH:MM')
        bot.register_next_step_handler(time , setTime) #setTime устанавливает задачу на время в time
    if call.data == 'sleepTrue':
        os.system("rundll32 powrprof.dll,SetSuspendState 0,1,0")
    if call.data == 'shutdown-cancel':
        try: #проверка на subprocess.CalledProcessError есть ли запланированные задачи
            res = subprocess.check_output("schtasks /query /fo list /tn shutdown", shell=True, encoding='utf-8', errors='ignore')
            # print(call.message.chat.id, res)
            os.system('schtasks /delete /tn "shutdown" /f')
            bot.send_message(call.message.chat.id, 'Успешно удалено')
        except subprocess.CalledProcessError:
            bot.send_message(call.message.chat.id, 'Запланированных задач нет')
        
        
        
def setTime(message): 
    try:
        time = str(message.text)
        os.system('''schtasks /create /sc ONCE /tn "shutdown" /tr " 'C:\Windows\System32\shutdown.exe' /s /t 30 /c 'Запланированное завершение работы' " /st '''+ time) 
        #задача будет выолнена единожды в указанное в time время с аргументами /s /t
    except Exception:
        bot.send_message(message.chat.id, 'Что-то пошло не так')
    bot.send_message(message.chat.id, 'Успешно сохранено')



    
bot.polling()
