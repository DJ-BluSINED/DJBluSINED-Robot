import telebot
from telebot import types
import threading
import http.server
import socketserver
import time

#########
API_TOKEN = '7834618808:AAHumrmQBmXEtjnY1PLbEnExytS-u2VUX98'
bot = telebot.TeleBot(API_TOKEN)
admin = {6181692448}
admin2 = {7346891727}
user_ids = []
pending_user_id = None
sticker_to_send = None

###########

def delete_message(chat_id, message_id, delay):
    time.sleep(delay)
    bot.delete_message(chat_id, message_id)

##############

@bot.message_handler(commands=['start'])
def iniciar_bot(message):
    if message.chat.id in admin:
        return
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    user_id = message.from_user.id
    if user_id not in user_ids:
        user_ids.append(user_id)
    bot.reply_to(message, f"*Hola* _{first_name}_, *¿cómo va el día?🍷🗿*", parse_mode='Markdown')
    print(f"IDs: {user_ids}")

############

@bot.message_handler(func=lambda message: message.text.startswith('.'))
def send_message_to_user(message):
           
           ### comandos
           command = message.text[1:]
           if command.startswith('c'):
               if message.chat.id in admin:
                   cmds = "*🕹️Comandos:*\n\n• .m = Mandar mensajes _(.m <user_\__id> <mensaje>)_ \n• .s = Mandar stickers _(.s <user_\__id>_ _| después_ \*_inserta un sticker_\*_)_ \n• .l = Muestra la lista de los IDs registrados en el bot\n\n• .c = comandos _(este menú)_\n\n_🗿Nota: también puedes enviar los stickers sin el comando de .s_"
                   bot.send_message(message.chat.id, cmds, parse_mode='Markdown')
                   threading.Thread(target=delete_message, args=(message.chat.id, message.message_id, 10)).start()
           
           ### mensaje
           if command.startswith('m'):
               try:
                   parts = command.split(" ", 2)
                   user_id = int(parts[1])
                   if user_id not in user_ids:
                       bot.send_message(message.chat.id, "_🚫Este usuario no ha iniciado el bot🚫_", parse_mode='Markdown')
                       return
                   msgnot = "*No hay mensaje*"
                   msg_text = parts[2] if len(parts) > 2 else bot.reply_to(message, msgnot, parse_mode='Markdown') 
                   bot.send_message(user_id, msg_text)
                   print(f"Mensaje: <{msg_text}> al ID: {user_id}")
                   msg = bot.reply_to(message, f'*✅Mensaje enviado al usuario con ID:*`{user_id}`', parse_mode='Markdown')
                   threading.Thread(target=delete_message, args=(message.chat.id, msg.message_id, 5)).start()
               except (IndexError, ValueError):
                   msz = bot.reply_to(message, "_☝🏻🤓Uso correcto: .m <user_id> <mensaje>_", parse_mode='Markdown')
                   threading.Thread(target=delete_message, args=(message.chat.id, msz.message_id, 5)).start()
           
           ### sticker
           if command.startswith('s'):
               if message.chat.id not in admin:
                   return
               global pending_user_id
               parts = message.text.split()
               if len(parts) < 2:
                   mst = bot.reply_to(message, "_☝🏻🤓Uso correcto: .s <id del usuario>_", parse_mode='Markdown')
                   threading.Thread(target=delete_message, args=(message.chat.id, mst.message_id, 5)).start()
                   threading.Thread(target=delete_message, args=(message.chat.id, message.message_id, 10)).start()
                   return
               try:
                   
                   pending_user_id = int(parts[1])
                   mmm = bot.send_message(message.chat.id, f"*✈️Manda el sticker que le va a enviar al usuario con ID:* `{pending_user_id}`", parse_mode='Markdown')
                   
                   threading.Thread(target=delete_message, args=(message.chat.id, mmm.message_id, 15)).start()
               except ValueError:
                   ms = bot.reply_to(message, "_🤓Por favor, proporciona un ID de usuario válido_", parse_mode='Markdown')
                   threading.Thread(target=delete_message, args=(message.chat.id, ms.message_id, 5)).start()
           
           ### lista
           if command.startswith('l'):
               if message.chat.id not in admin:
                   return
               threading.Thread(target=delete_message, args=(message.chat.id, message.message_id, 5)).start()
               list_users(message)

def list_users(message):
    if user_ids:
        user_list = '\n'.join(str(user_id) for user_id in user_ids)
        bot.send_message(message.chat.id, f"*📋Lista de usuarios:*\n\n{user_list}", parse_mode='Markdown')
        threading.Thread(target=delete_message, args=(message.chat.id, message.message_id, 5)).start()
    else:
        mss = "_No hay usuarios registrados todavía🚫_"
        x = bot.send_message(message.chat.id, mss, parse_mode='Markdown')
        threading.Thread(target=delete_message, args=(message.chat.id, x.message_id, 5)).start()



#################


@bot.message_handler(content_types=['sticker'])
def handle_sticker_message(message):
    if message.chat.id in admin:
        
        global pending_user_id, sticker_to_send
        if pending_user_id is not None:
            bot.send_sticker(pending_user_id, message.sticker.file_id)
            mzz = bot.send_message(message.chat.id, "*Sticker enviado✅*", parse_mode='Markdown')
            threading.Thread(target=delete_message, args=(message.chat.id, mzz.message_id, 5)).start()
            pending_user_id = None
        else:
            sticker_to_send = message.sticker.file_id
            msti = bot.send_message(message.chat.id, "_¿A qué ID de usuario le va a enviar dicho sticker?❓_", parse_mode='Markdown')
            threading.Thread(target=delete_message, args=(message.chat.id, msti.message_id, 15)).start()
            bot.register_next_step_handler(message, handle_id_input)
    else:
        bot.forward_message(admin, message.chat.id, message.message_id)
            

def handle_id_input(message):
    global pending_user_id, sticker_to_send
    if sticker_to_send is not None:
        try:
            pending_user_id = int(message.text)
            bot.send_sticker(pending_user_id, sticker_to_send)
            threading.Thread(target=delete_message, args=(message.chat.id, message.message_id, 5)).start()
            ust = bot.send_message(message.chat.id, "*Sticker enviado correctamente al usuario✅*", parse_mode='Markdown')
            
            threading.Thread(target=delete_message, args=(message.chat.id, ust.message_id, 5)).start()
            
            sticker_to_send = None
            pending_user_id = None
        except ValueError:
            mva = bot.send_message(message.chat.id, "*_🤓Por favor, proporciona un ID de usuario válido._*", parse_mode='Markdown')
            threading.Thread(target=delete_message, args=(message.chat.id, mva.message_id, 5)).start()
    else:
        mpe = bot.send_message(message.chat.id, "*_⛔No hay un sticker pendiente para enviar_*", parse_mode='Markdown')
        threading.Thread(target=delete_message, args=(message.chat.id, mpe.message_id, 5)).start()


###################
### Recibir los mensajes

@bot.message_handler(func=lambda message: True)
def echo_all(message):
       if message.chat.id in admin:
           return
       if message.from_user.id not in user_ids:
        user_ids.append(message.from_user.id)
        print(user_ids, "\n")
        formatted_message = f"*💭Nuevo mensaje:*\n{message.text}\n\n👤*Usuario:*\n• _{message.from_user.first_name}_\n• _@{message.from_user.username}_\n• `{message.chat.id}`"
       bot.send_message(7346891727, formatted_message, parse_mode='Markdown')




### MAIN #######################
def run_server():
    PORT = 7000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

####################

def recibir_mensajes():
    bot.infinity_polling()

####################

if __name__ == '__main__':
    # Crea un hilo para ejecutar la función run_server
    server_thread = threading.Thread(target=run_server)
    server_thread.start()  # Inicia el hilo

    print('Iniciando el bot...')
    bot.set_my_commands([
    telebot.types.BotCommand("/start", "Iniciar el bot😀"),
    ])
    hilo_bot = threading.Thread(name="hilo_bot", target=recibir_mensajes)
    hilo_bot.start()
    print('Bot Iniciado✓')
    print("--------------------------------")
