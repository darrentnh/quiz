#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Quiz bot.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, Filters
import logging
import requests
import random
import sys

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

questions = {
1: ('''
Pt presents with right iliac fossa pain; diagnosed with pyogenic inflammation of the appendix. Mediator of Innate Immunity:
A) IFN Type 1
B) MBL
C) IgG
D) CTLs
E) Eosinophils
''', 'B'),

2: ('''
Immunoglobulin isotope switching from IgM to IgA involves
A) Activated RAG
B) Pairing with alternate light chain
C) Peptide presentation by HLA class II
D) CD4+ T cell help
E) Formation of alternate variable domain
''', 'D'),

3: ('''
Metastatic carcinoma cells are MOST likely to become lodged in which regions of the lymph node?
A) Subscapular sinus
B) Follicles
C) Paracortex
D) High endothelial venules
E) Medulla
''', 'A'),

4: ('''
Increased capillary permeability as a result of complement activation is MOST likely due to
A) depletion of C1
B) formation of anaphylatoxins
C) formation of C3b
D) formation of c5 convertase
E) formation of membrane attack complex
''', 'B')
}

user_qns = {}
multiple_choice_keyboard = ['A', 'B', 'C', 'D', 'E']

def start(bot, update):
    user = update.message.from_user
    update.message.reply_text(
    'Hi {}! Type /question to display a question'.format(user.first_name))


def help(bot, update):
    update.message.reply_text(
    'Type /question to display a question.')


def question(bot, update, user_data):
    user = update.message.from_user

    logger.info('User {} requsted for a question'.format(user.id))
    logger.info('Current user_qns: {}'.format(user_qns))

    # get unattempted questions
    if user.id in user_qns:
        # this means this is not the user's first question
        logger.info('Getting completed questions list of user id: '.format(user.id))
        completed_questions_list = user_qns[user.id]
        logger.info('completed_questions_list is: {}'.format(completed_questions_list))
        # inverse the question list
        new_questions_list = [x for x in range(1, len(questions) + 1) if x not in completed_questions_list]
        logger.info('new_questions_list is: {}'.format(new_questions_list))
        try:
            chosen_qn = random.sample(new_questions_list, 1)[0]
        # called when there are no more questions left in the bank
        except ValueError:
            update.message.reply_text('There are currently no more questions! Try again later. Type /reset to reset your progress.')
            return
        logger.info('Choosing a random question: Q{}'.format(chosen_qn))
    else:
        # initate complete questions list and give first random question
        logger.info('New user detected. Creating new question list.')
        user_qns[user.id] = []
        chosen_qn = random.randint(1, len(questions)) # choose a qn from the whole list

    # question has been chosen above
    qn_str = questions[chosen_qn][0]
    user_qns[user.id].append(chosen_qn)
    logger.info("Displayed Q{}".format(chosen_qn))
    update.message.reply_text(qn_str,
            reply_markup=ReplyKeyboardMarkup(multiple_choice_keyboard, one_time_keyboard=True))


def try_again(bot, update, user_data):
    user = update.message.from_user
    last_qn_no = user_qns[user.id][-1]
    chosen_qn = last_qn_no

    # question has been chosen above
    qn_str = questions[chosen_qn][0]
    user_qns[user.id].append(chosen_qn)
    logger.info("Displayed Q{}".format(chosen_qn))
    update.message.reply_text(qn_str,
            reply_markup=ReplyKeyboardMarkup(multiple_choice_keyboard, one_time_keyboard=True))


def check_answer(bot, update, user_data):
    # Obtain some basic user info
    user = update.message.from_user
    logger.info('Last question was: '.format(user_qns[user.id][-1])) # -1 is for the last question attempted on the list
    most_recent_qn = user_qns[user.id][-1]
    ans = questions[most_recent_qn][1]
    logger.info("Check_answer called. User {} (ID: {}) selected {}".format(
                user.first_name,
                user.id,
                update.message.text
                ))
    logger.info('Answer to last question should be: ' + ans)
    if update.message.text == ans:
        update.message.reply_text('Correct! Type /question for the next question.')
        logger.info('User is correct')
    else:
        # remove last question from the completed list because user got it wrong!
        # user_qns[user.id] = user_qns[user.id][:-1]
        update.message.reply_text('Wrong! Type /try to try again.')
        logger.info('User chose the wrong answer')

def reset(bot, update, user_data):
    user = update.message.from_user
    user_qns.pop('key', None)
    logger.info('The information associated with User ID: {} has been deleted.'.format(user.id))
    update.message.reply_text('You have successfully reset your progress.')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    try:
        TOKEN = sys.argv[1]
    except IndexError:
        logger.info('Enter your token as an argument after the script name')

    updater = Updater(TOKEN)
    logger.info('Polling...')
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("question", question, pass_user_data=True))
    dp.add_handler(CommandHandler("try", try_again, pass_user_data=True))
    dp.add_handler(CommandHandler("reset", reset, pass_user_data=True))


    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(RegexHandler('^[A-E]', check_answer, pass_user_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
