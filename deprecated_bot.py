import os
import random
import telebot

class Player:
    def __init__(self, user_id, name) -> None:
        self.user_id = user_id
        self.name = name


BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

# number: List[(user_id, bet)]
place_bets = dict()
# user_id: bet
pass_line_bets = dict()
# user_id: amount
balances = dict()
# user_id: name
names = dict()
# point number
point = 0

# commands

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, "I only support pass line bets at the moment.\nUse /roll to roll the dice.\nUse /passline {amount} to place a bet. Use /balance to check balances.")

@bot.message_handler(commands=['roll'])
def roll_dice(message):
    dice_roll = (random.randint(1, 6), random.randint(1, 6))
    additional_message = parse_bets(dice_roll[0], dice_roll[1])
    bot.send_message(message.chat.id, f'{message.from_user.first_name} rolled {dice_roll[0] + dice_roll[1]} ({dice_roll[0]}, {dice_roll[1]})\n{additional_message}')

@bot.message_handler(commands=['balance', 'balances'])
def display_balances(message):
    bot.reply_to(message, get_balance_string())

@bot.message_handler(commands=['passline'])
def make_pass_line_bet(message):
    global point
    global balances
    global pass_line_bets
    global names
    if point != 0:
        bot.reply_to(message, f'Point has been established at {point}. Wait until it\'s been cleared.')
        return
    if not len(message.text.split()) > 1:
        bot.reply_to(message, 'Not a valid bet! Use /passline [number] to make a bet while the point is 0.')
        return
    if not message.text.split()[1].isdecimal():
        bot.reply_to(message, 'Not a valid bet! Use /passline [number] to make a bet while the point is 0.')
        return
    bet_amount = int(message.text.split()[1])

    sender_id = message.from_user.id
    user_balance = balances.get(sender_id, 50)
    if user_balance < bet_amount:
        bot.reply_to(message, f'Buddy, you can\'t afford that. Your balance is ${user_balance}')
        return
    
    balances[sender_id] = balances.get(sender_id, 50) - bet_amount
    pass_line_bets[sender_id] = bet_amount
    names[sender_id] = message.from_user.first_name

    bot.reply_to(message, f'${bet_amount} has been put on the table. Your balance is now ${balances[sender_id]}')

@bot.message_handler(commands=['placebet'])
def make_place_bet(message):
    global names
    global balances
    global place_bets
    # Validate
    if len(message.text.split()) < 3:
        bot.reply_to(message, 'Not a valid bet! Use /placebet [number] [amount] to make a place bet.')
        return
    if not message.text.split()[1].isdecimal() or not message.text.split()[2].isdecimal():
        bot.reply_to(message, 'Not a valid bet! Use /placebet [number] [amount] to make a place bet.')
        return
    
    bet_number = int(message.text.split()[1])
    bet_amount = int(message.text.split()[2])

    if bet_number not in { 4, 5, 6, 8, 9, 10 }:
        bot.reply_to(message, 'Not a valid place bet! Must bet on either 4, 5, 6, 8, 9, or 10. Read the rules dummy-san~~~')
        return

    sender_id = message.from_user.id
    if balances.get(sender_id, 50) < bet_amount:
        bot.reply_to(message, f'You better check your wallet before making this bet. You only have ${balances.get(sender_id, 50)}.')
        return
    
    # now actually make the bet
    place_bets.setdefault(bet_number, []).append((sender_id, bet_amount))
    balances[sender_id] = balances.get(sender_id, 50) - bet_amount
    names[sender_id] = message.from_user.first_name
    bot.reply_to(message, f'{message.from_user.first_name} put ${bet_amount} on {bet_number}.\nThey now have ${balances[sender_id]} remaining.')

@bot.message_handler(commands=['fund'])
def fund(message):
    global balances
    global names
    if balances[message.from_user.id] is not None and balances[message.from_user.id] < 5:
        balances[message.from_user.id] = 50
        bot.reply_to(message, f'Funded {names[message.from_user.id]} with $50 from the Soros slush fund.')
    else:
        bot.reply_to(message, "$4,800 a month mentality. 🤡")


def parse_bets(first_die_roll: int, second_die_roll: int) -> str:
    global point
    global balances
    global pass_line_bets
    global place_bets
    global names
    dice_sum = first_die_roll + second_die_roll
    additional_message = ""

    # Check for place bets
    if dice_sum in place_bets and point != 0:
        for user_id, bet_amount in place_bets[dice_sum]:
            odds_multiplier = 0
            if dice_sum in [4, 10]:
                odds_multiplier = 9 / 5
            elif dice_sum in [5, 9]:
                odds_multiplier = 7 / 5
            elif dice_sum in [6, 8]:
                odds_multiplier = 7 / 6

            winnings = round(bet_amount + (bet_amount * odds_multiplier), 2)
            balances[user_id] += winnings
            additional_message += f'{names[user_id]} made {winnings} on a place bet!\n'
        place_bets[dice_sum] = []
    
    # Check for pass line bets
    if point == 0:
        if dice_sum == 7 or dice_sum == 11:
            for user_id, bet in pass_line_bets.items():
                balances[user_id] = balances.get(user_id, 0) + (bet * 2)
            additional_message = "Craps! Big money baby!"
            pass_line_bets.clear()
            additional_message += f'\n\n{get_balance_string()}'
        elif dice_sum == 2 or dice_sum == 3 or dice_sum == 12:
            pass_line_bets.clear()
            additional_message = "1 Missed Call: The Money"
            additional_message += f'\n\n{get_balance_string()}'
        else:
            point = dice_sum
            additional_message = f'Point set to {point}!'
    elif point == dice_sum:
        for user_id, bet in pass_line_bets.items():
            balances[user_id] = balances.get(user_id, 0) + (bet * 2)
            additional_message = "Point! Winner!"
        point = 0
        pass_line_bets.clear()
        additional_message += f'\n\n{get_balance_string()}'
    elif dice_sum == 7:
        pass_line_bets.clear()
        place_bets.clear()
        additional_message = "Sando. 🥪"
        
        point = 0
    return additional_message 

def get_balance_string() -> str:
    global names
    global balances
    balance_str = ""
    for user_id, balance in balances.items():
        balance_str += f'{names.get(user_id, user_id)}: ${round(balance, 2)}\n'
    
    if not balance_str:
        return "No balances recorded so far."
    else:
        return balance_str

bot.infinity_polling()