import telebot
from telebot import types
import random

player_data = {}
ba = 100
player_balance = []
cards = ['2♥', '3♥', '4♥', '5♥', '6♥', '7♥', '8♥', '9♥', '10♥', 'Валет♥', 'Дама♥', 'Король♥', 'Туз♥', '2♦', '3♦', '4♦',
         '5♦', '6♦', '7♦', '8♦', '9♦', '10♦', 'Валет♦', 'Дама♦', 'Король♦', 'Туз♦', '2♣', '3♣', '4♣', '5♣', '6♣', '7♣',
         '8♣', '9♣', '10♣', 'Валет♣', 'Дама♣', 'Король♣', 'Туз♣', '2♠', '3♠', '4♠', '5♠', '6♠', '7♠', '8♠', '9♠', '10♠',
         'Валет♠', 'Дама♠', 'Король♠', 'Туз♠']
players = []
bot = telebot.TeleBot('8303190584:AAFsB51zig-FjmErL2SaLyLKfenMTXHsv4g')


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not any(player['user_id'] == user_id for player in player_balance):
        player_balance.append({'user_id': user_id, 'ba': ba})
    bot.send_message(message.chat.id, 'халоу  майфрендо, чтобы начать игру пропиши /game')


@bot.message_handler(commands=['game'])
def game(message):
    bot.send_message(message.chat.id, 'добавлю тебя в список игроков! Ожидайте')
    player_name = message.from_user.first_name
    user_id = message.from_user.id
    if any(player['id'] == user_id for player in players):
        bot.send_message(message.chat.id, 'ты уже в списке!')
    else:
        players.append({'name': player_name, 'id': user_id})
    if len(players) >= 2:
        result = random_excluding(players, player_name)
        result_id = result['id']
        player_data[user_id] = {'stavka1': [], 'stavka2': [], 'stavka3': [], 'stavka4': [], 'target_cards': [],
                                'user_cards': [], 'target': result_id, 'cards': cards.copy(), 'id': user_id}
        if result:
            bot.send_message(message.chat.id, f'Случайный игрок (кроме тебя): {result["name"]}')
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton('играть', callback_data='action_name')
            markup.add(button)
            bot.send_message(player_data[user_id]['target'], 'игрок найден, нажми играть!', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Не удалось выбрать случайного игрока')


@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    target_id = call.from_user.id
    user_id = None
    for uid, data in player_data.items():
        if data['target'] == target_id:
            user_id = uid
            break
    if call.data == 'action_name':
        bot.send_message(call.message.chat.id, 'игра началась!')
        a = random.choice(player_data[user_id]['cards'])
        bot.send_message(target_id, a)
        player_data[user_id]['cards'].remove(a)
        b = random.choice(player_data[user_id]['cards'])
        bot.send_message(target_id, b)
        player_data[user_id]['cards'].remove(b)
        player_data[user_id]['target_cards'].append(a)
        player_data[user_id]['target_cards'].append(b)
        a1 = random.choice(player_data[user_id]['cards'])
        bot.send_message(user_id, a1)
        player_data[user_id]['cards'].remove(a1)
        b1 = random.choice(player_data[user_id]['cards'])
        bot.send_message(user_id, b1)
        player_data[user_id]['cards'].remove(b1)
        player_data[user_id]['user_cards'].append(a1)
        player_data[user_id]['user_cards'].append(b1)
        print()
        for player in player_balance:
            if player['user_id'] == user_id:
                player['ba'] -= 20
                balance1 = player['ba']
                break
        for player in player_balance:
            if player['user_id'] == target_id:
                player['ba'] -= 20
                balance = player['ba']
                break

        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(f'ставка, ваш баланс:{balance1}', callback_data=f'stavka_{user_id}')
        button1 = types.InlineKeyboardButton('чек', callback_data=f'check_{user_id}')
        button2 = types.InlineKeyboardButton('фолд', callback_data=f'fold_{user_id}')
        markup.add(button, button1, button2)
        bot.send_message(user_id, f'Ваши карты: {a1} {b1}', reply_markup=markup)

        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(f'ставка, ваш баланс:{balance}', callback_data=f'stavka_{target_id}')
        button1 = types.InlineKeyboardButton('чек', callback_data=f'check_{target_id}')
        button2 = types.InlineKeyboardButton('фолд', callback_data=f'fold_{target_id}')
        markup.add(button, button1, button2)
        bot.send_message(target_id, f'Ваши карты: {a} {b}', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith(('stavka_', 'check_', 'fold_')))
def handle_bet_buttons(call):
    action, player_id = call.data.split('_')
    player_id = int(player_id)
    user_balance = next((p['ba'] for p in player_balance if p['user_id'] == player_id), 0)

    if action == 'stavka':
        msg = bot.send_message(call.message.chat.id, 'Введите сумму ставки:')
        bot.register_next_step_handler(msg, lambda m: process_bet_amount(m, player_id, user_balance))


def process_bet_amount(message, player_id, balance):
    try:
        bet_amount = int(message.text)
        if balance >= bet_amount:
            for player in player_balance:
                if player['user_id'] == player_id:
                    player['ba'] -= bet_amount
                    break
            opponent_id = None
            for uid, data in player_data.items():
                if uid == player_id:
                    opponent_id = data['target']
                    break
                elif data['target'] == player_id:
                    opponent_id = uid
                    break
            if opponent_id:
                bot.send_message(opponent_id, f'Ваш соперник сделал ставку в размере {bet_amount}')
        else:
            bot.send_message(message.chat.id, "Недостаточно средств!")
    except ValueError:
        bot.send_message(message.chat.id, "Введите число!")


def random_excluding(lst, exclude_name):
    available = [x for x in lst if x['name'] != exclude_name]
    if available:
        return random.choice(available)
    return None


bot.polling(none_stop=True, interval=0)
