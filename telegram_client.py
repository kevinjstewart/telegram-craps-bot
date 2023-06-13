import os
from posixpath import split
import random
from unicodedata import decimal
import telebot
from bets import *
from copy import deepcopy
from playerstore import *
from session import CrapsGame
import atexit
import pickle

BOT_TOKEN = os.environ.get('BOT_TOKEN')
SAVE_FILE_NAME = 'saved_game_1.pk'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['roll'])
def rolled(message):
    old_point = deepcopy(game.point)
    player_store.register_player_from_message(message)
    result = game.roll(message.from_user.id)
    response = f'🎲🎲 Rolled {result.roll.sum} ({result.roll.first_side}, {result.roll.second_side}).'

    if result.losing_bets or result.winning_bets:
        response += '\n'
        for bet in result.losing_bets:
            player_name = player_store.players[bet.player_id].name
            response += f'\n💥 {player_name} lost ${bet.amount:.2f} on a {bet.display_name()} bet.'
        for bet in result.winning_bets:
            player_name = player_store.players[bet.player_id].name
            response += f'\n🤑 {player_name} made ${bet.get_outcome(result.roll, point=old_point).payout:.2f} on a {bet.display_name()} bet.'
    
    response += '\n'

    if old_point == game.point:
        if old_point is None:
            response += 'Point was not set.'
        else:
            response += f'\nPoint is still {game.point}.'
    elif game.point is None:
        response += '\nPoint has been cleared.'
    else:
        response += f'\nPoint is now {game.point}.'

    bot.reply_to(message, response)

@bot.message_handler(commands=['point'])
def get_point(message):
    if game.point is None:
        bot.reply_to(message, '🚫 No point set.')
    else:
        bot.reply_to(message, f'🎯 Point set to {game.point}')

@bot.message_handler(commands=['balances'])
def get_balances(message):
    if not player_store.players:
        bot.reply_to(message, 'Zero balances to report.')
        return
    
    response = ''

    for player in player_store.players.values():
        response += f'\n👤 {player.name} has ${player.balance:.2f} in their hand.'

    bot.reply_to(message, response)

@bot.message_handler(commands=['bankroll', 'bankrolls'])
def get_bankrolls(message):
    if not player_store.players:
        bot.reply_to(message, 'Zero bankrolls to report.')
        return
    
    response = ''

    for player in player_store.players.values():
        response += f'\n👤 {player.name} has a ${player.bankroll:.2f} balance in their bankroll.'

    bot.reply_to(message, response)

@bot.message_handler(commands=['passline'])
def make_pass_line_bet(message):
    player_store.register_player_from_message(message)

    if game.point is not None:
        bot.reply_to(message, '🚫 Can\'t make a pass line bet with the point set.')
        return

    if len(message.text.split()) == 2 and message.text.split()[1].isdecimal():
        amount = Decimal(message.text.split()[1])
    else:
        bot.reply_to(message, 'Not a valid bet. Use /passline [number].')
        return
    player_id = message.from_user.id
    bet = PassLineBet(player_id=player_id, amount=amount)
    
    try:
        game.place_bet(bet)
        bot.reply_to(message, f'✔️ {player_store.players[player_id].name} just put ${bet.amount:.2f} on the pass line.')
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['placebet', 'place'])
def make_place_number_bet(message):
    player_store.register_player_from_message(message)

    split_message = message.text.split()

    if len(split_message) == 3 and split_message[1].isdecimal() and split_message[2].isdecimal() and int(split_message[2]) in POINT_NUMBERS:
        amount = Decimal(split_message[1])
        place_number = int(split_message[2])
    else:
        bot.reply_to(message, f'🚫 Not a valid bet. Use /placebet [amount] [number]. {split_message}')
        return
    player_id = message.from_user.id
    bet = PlaceBet(player_id=player_id, roll_number=place_number, amount=amount)
    
    try:
        game.place_bet(bet)
        bot.reply_to(message, f'✔️ {player_store.players[player_id].name} just made a ${bet.amount:.2f} place bet on {place_number}.')
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['come', 'comebet'])
def make_come_bet(message):
    player_store.register_player_from_message(message)

    if game.point is None:
        bot.reply_to(message, '🚫 Can\'t make a come bet when the point isn\'t set. Just make a pass line bet.')
        return

    if len(message.text.split()) == 2 and message.text.split()[1].isdecimal():
        amount = Decimal(message.text.split()[1])
    else:
        bot.reply_to(message, 'Not a valid bet. Use /comebet [number].')
        return
    player_id = message.from_user.id
    bet = ComeBet(player_id=player_id, amount=amount)

    try:
        game.place_bet(bet)
        bot.reply_to(message, f'✔️ {player_store.players[player_id].name} just made a ${bet.amount:.2f} come bet.')
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['field', 'fieldbet'])
def make_field_bet(message):
    player_store.register_player_from_message(message)

    if len(message.text.split()) == 2 and message.text.split()[1].isdecimal():
        amount = Decimal(message.text.split()[1])
    else:
        bot.reply_to(message, 'Not a valid bet. Use /field [number].')
        return
    player_id = message.from_user.id
    bet = FieldBet(player_id=player_id, amount=amount)

    try:
        game.place_bet(bet)
        bot.reply_to(message, f'✔️ {player_store.players[player_id].name} just made a ${bet.amount:.2f} field bet.')
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['horn', 'hornbet'])
def make_horn_bet(message):
    player_store.register_player_from_message(message)

    split_message = message.text.split()

    if len(split_message) == 2 and split_message[1].isdecimal():
        amount = Decimal(split_message[1])
    else:
        bot.reply_to(message, 'Not a valid bet. Use /horn [number].')
        return
    player_id = message.from_user.id
    bet = HornBet(player_id=player_id, amount=amount)

    try:
        game.place_bet(bet)
        bot.reply_to(message, f'✔️ {player_store.players[player_id].name} just made a ${bet.amount:.2f} horn bet 📯‼️.')
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['bets', 'list', 'listbets'])
def list_bets(message):
    player_store.register_player_from_message(message)

    if not game.bets and not game.staged_bets:
        bot.reply_to(message, '😴 Zero bets on the board. Unbelievable.')
        return
    
    response = ""

    for bet in game.staged_bets:
        player_name = player_store.players[bet.player_id].name
        response += f'\n✍🏻 | ${bet.amount:.2f} {bet.display_name()} bet by {player_name}'
    
    for bet in game.bets:
        player_name = player_store.players[bet.player_id].name
        response += f'\n{"🔐" if bet.is_contract_bet else "🔓"} | ${bet.amount:.2f} {bet.display_name()} bet by {player_name}'
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['deposit', 'save'])
def deposit_money(message):
    player_store.register_player_from_message(message)
    if len(message.text.split()) == 2 and message.text.split()[1].isdecimal():
        amount = Decimal(message.text.split()[1])
    else:
        bot.reply_to(message, '🚫 Invalid command. Use /deposit [amount] to deposit money into bankroll.')
        return
    try:
        player_store.deposit(message.from_user.id, amount)
        player = player_store.players[message.from_user.id]
        bot.reply_to(message, f'🏧 Deposited ${amount:.2f} into bankroll.\nYour balance is now ${player.balance:.2f}. Your bankroll is ${player.bankroll}.')
    except Exception as e:
        bot.reply_to(message, f'🚫 Error: {e.message}')

@bot.message_handler(commands=['withdraw', 'fund'])
def withdraw_money(message):
    player_store.register_player_from_message(message)
    if len(message.text.split()) == 2 and message.text.split()[1].isdecimal():
        amount = Decimal(message.text.split()[1])
    else:
        bot.reply_to(message, '🚫 Invalid command. Use /withdraw [amount] to withdraw money from bankroll.')
        return
    try:
        player_store.withdraw(message.from_user.id, amount)
        player = player_store.players[message.from_user.id]
        bot.reply_to(message, f'🏧 Withdrew ${amount:.2f} from bankroll.\nYour balance is now ${player.balance:.2f}. Your bankroll is ${player.bankroll:.2f}.')
    except Exception as e:
        bot.reply_to(message, f'🚫 Error: {e.message}')

def exit_handler():
    file = open(SAVE_FILE_NAME, 'wb')
    pickle.dump(obj=game, file=file)
    file.close()

if os.path.isfile(SAVE_FILE_NAME):
    game = pickle.load(open(SAVE_FILE_NAME, 'rb'))
    player_store = game.player_store
else:
    player_store = PlayerStore(id=uuid4())
    game = CrapsGame(player_store)

atexit.register(exit_handler)
bot.infinity_polling()