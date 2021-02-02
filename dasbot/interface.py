import logging
from aiogram import types
from dynaconf import settings

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Interface(object):
    TIME_OPTIONS = ["09:00", "12:00", "15:00", "18:00", "21:00", "00:00", "03:00", "06:00"]
    SETTINGS_MENU = {
        0: {
            'main': {'row_len': 2, 'btns': [
                {'text': 'Quiz length', 'action': 'quiz-len'},
                {'text': 'Daily quiz time', 'action': 'quiz-time'}
            ]}
        },
        1: {
            'quiz-len': {'row_len': 4, 'btns': [
                {'text': n, 'action': n} for n in [5, 10, 20, 50]
            ]},
            'quiz-time': {'row_len': 4, 'btns': [
                {'text': t, 'action': t} for t in TIME_OPTIONS
            ] + [{'text': 'Unsubscribe', 'action': 'UNSUBSCRIBE'}]}
        }
    }

    def __init__(self, bot):
        self.bot = bot

    async def reply_with_help(self, message):
        await message.reply('Type /start to start the quiz, /settings to change the quiz time.')

    async def welcome(self, chat):
        text = ("Hi! I'm Dasbot. My mission is to help you memorize German articles.\n"
                "I know about 2000 most frequently used German words, and I'll be sending you a short quiz every day.\n"
                "To change the preferred quiz time (or turn it off), send /settings command.\n"
                "You can also practice any time by typing /start.")
        await self.bot.send_message(chat.id, text)

    async def daily_hello(self, chat):
        text = "Hi, it's Dasbot! Here's your daily German articles quiz:"
        await self.bot.send_message(chat.id, text)

    async def ask_question(self, chat):
        text = f"{chat.quiz.pos}/{chat.quiz.length}. "
        text += f"What's the article for {chat.quiz.question}?"
        result = await self.bot.send_message(chat.id, text, reply_markup=Interface.quiz_kb())
        log.debug("message sent, result: %s", result)

    async def give_feedback(self, chat, message, correct):
        text = "Correct, " if correct else "Incorrect, "
        text += f"{chat.quiz.answer} {chat.quiz.question}"
        await message.answer(text)

    async def announce_result(self, chat):
        text = f"{chat.quiz.correctly} out of {settings.QUIZ_LEN}"
        text += self.rate(chat.quiz.correctly) + "\n"
        text += "To start over, type /start, or /help for more info."
        await self.bot.send_message(chat.id, text, reply_markup=types.ReplyKeyboardRemove())

    def rate(self, correctly):
        ratio = round(correctly / settings.QUIZ_LEN * 10)
        if ratio in range(0, 4):
            msg = ", keep trying!"
        elif ratio in range(4, 7):
            msg = ", good job!"
        elif ratio in range(7, 10):
            msg = ", excellent!"
        elif ratio == 10:
            msg = ", perfeKt!"
        else:
            msg = "."
        return msg

    @staticmethod
    def quiz_kb():
        """ Returns object of ReplyKeyboardMarkup type """
        labels = ('der', 'die', 'das')
        keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        row_btns = (types.KeyboardButton(text) for text in labels)
        keyboard_markup.row(*row_btns)
        return keyboard_markup

    async def settings_main(self, message, callback_gen):
        await message.answer("Available settings:",
                             reply_markup=Interface.settings_kb(callback_gen, 0, 'main'))

    async def settings_quiztime_request(self, message):
        await message.answer("Please select quiz time (time zone Berlin/CET)",
                             reply_markup=Interface.quiz_time_settings_kb())

    async def settings_quiztime_set(self, query, pref):
        text = f'Daily quiz time is set to {pref} (Berlin time)'
        if pref == "UNSUBSCRIBE":
            text = 'Daily quiz is off'
        await self.bot.edit_message_text(chat_id=query.message.chat.id,
                                         message_id=query.message.message_id,
                                         text=text)

    @staticmethod
    def settings_kb(callback_gen, level, selected_id):
        menu = Interface.SETTINGS_MENU[level][selected_id]
        row_width = menu['row_len']
        buttons = menu['btns']
        markup = types.InlineKeyboardMarkup(row_width=row_width)

        for i, button in enumerate(buttons):
            callback_data = callback_gen(level=level + 1, selected_id=selected_id, action=button['action'])
            if i % row_width == 0:
                markup.row()
            markup.insert(types.InlineKeyboardButton(text=button['text'], callback_data=callback_data))

        return markup

    @staticmethod
    def quiz_time_settings_kb():
        """ Returns InlineKeyboardMarkup object with quiz options """
        row_width = 4
        inline_kb = types.InlineKeyboardMarkup(row_width=row_width)
        for i, option in enumerate(Interface.TIME_OPTIONS):
            if i % row_width == 0:
                inline_kb.row()
            inline_kb.insert(types.InlineKeyboardButton(option, callback_data=option))
        inline_kb.row()
        inline_kb.insert(types.InlineKeyboardButton("Daily quiz OFF", callback_data="UNSUBSCRIBE"))
        return inline_kb

    def recognized(self, msg_text):
        return msg_text in ['der', 'die', 'das']


if __name__ == "__main__":
    pass
