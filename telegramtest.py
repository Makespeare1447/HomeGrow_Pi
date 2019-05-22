from telepot.loop import MessageLoop

import telepot
bot = telepot.Bot('387161336:AAGKJeu_VaMk0Cn1PyrT0N0cCh3f9ijYwBM')
#bot.getMe()

def handle(msg):
    pprint(msg)

MessageLoop(bot, handle).run_as_thread()