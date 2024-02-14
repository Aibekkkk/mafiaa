import db
from telebot import TeleBot, types
import random
import requests
import json
from time import time
from time import sleep

game = False
indxs = 0
night = True

TOKEN = '6273646859:AAE-nLgy3uR0KzDAUMVJ7Whh3uYN-6mQdh0'
bot = TeleBot(TOKEN)

@bot.message_handler(func = lambda m: m.text.lower() == 'goplay' and m.chat.type == 'private')
def send_message(message):
    bot.send_message(message.chat_id, f'{message.from_user.first_name} играет')
    bot.send_message(message.from_user.id, 'вы добавлеены')
    db.insert_player(message.from_user.id, username = message.from_user.first_name)



@bot.message_handler(commands=["play"])
def game_strt(message):
    global game
    players = db.players_amount()
    if players >=5 and not game:
        db.set_roles(players)
        players_roles = db.players_amount()
        mafia_usernames = db.get_mafia_usernames()
        for player_id, role in players_roles:
            bot.send_message(player_id, text = role)
            if role == 'mafia':
                bot.send_message(player_id,
                                 text = f'Все члены мафии:\n{mafia_usernames}')
        game = True
        bot.send_message(message.chat.id, text='Игра стартанулась')
        return
    bot.send_message(message.chat.id, text='Где люди????')




@bot.message_handler(commands=["kick"])
def kick(message):
    username = " ".join(message.text.split( )[1:])
    usernames = db.get_all_alive()
    if not night:
        if not username in usernames:
            bot.send_message(message.chat_id, text='Нету такого имени')
            return
        voted = db.vote("citizen_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat_id, text='Ваш голос учтен')
            return
        bot.send_message(message.chat_id, text='У вас нету права к голосу')
        return
    bot.send_message(message.chat_id, text='Сейчас ночь нельзя никого кикнуть')


@bot.message_handler(commands=["kill"])
def kill(message):
    username = " ".join(message.text.split( )[1:])
    usernames = db.get_all_alive()
    mafia_username = db.get_mafia_usernames()
    if night and message.from_user.first_name in mafia_username:
        if not username in usernames:
            bot.send_message(message.chat.id, text='Нету такого имени')
            return
        voted = db.vote("mafia_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, text='Ваш голос учтен')
            return
        bot.send_message(message.chat.id, text='У вас нету права к голосу')
        return
    bot.send_message(message.chat.id, text='Сейчас ночь нельзя никого киллнуть')

def get_killed(night):
    if not night:
        username_killed = db.citizens_kill()
        return f'Горожане выгнали: {username_killed}'
    username_killed = db.mafia_kill()
    return f'Мафия убила: {username_killed}'



def game_loop(message):
    global night, game

    bot.send_message(message.chat.id,'Добра пожаловать, вам дается 120 секунд для знакомства.')
    sleep(120)
    while True:
        msg = get_killed(night)
        bot.send_message(message.chat.id, msg)
        if night:
            bot.send_message(message.chat.id,'Город заснул, просыпается мафия')
        else:
            bot.send_message(message.chat.id, 'Город просыпается, наступил день')
        winner = db.checkWinner()
        if winner == 'mafia' or winner == "citizen":
            game = False
            bot.send_message((message.chat.id, f"победили - {winner}"))
            return

        night = not night
        sleep(120)
        alive = db.get_all_alive()
        alive = '/n'.join(alive)
        bot.send_message(message.chat.id,f'в игре:/n{alive}')
        sleep(120)




if __name__ == '__main__':
    bot.polling(non_stop=True)