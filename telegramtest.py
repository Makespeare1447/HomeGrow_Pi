from telepot.loop import MessageLoop
def handle(msg):
    pprint(msg)

MessageLoop(bot, handle).run_as_thread()