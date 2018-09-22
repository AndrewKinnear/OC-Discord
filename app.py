import discord
import sqlite3 as sql
from contextlib import contextmanager
import random

TOKEN = "Thanos did nothing wrong
client = discord.Client()

@contextmanager
def connection_to_database():
    try:
        connection = sql.connect('quiz.db')
        yield connection
        connection.close()
    except sql.Error as e:
        print("connection_to_database(): connection error: " + e)


def dbLookup(query, *args):
    with connection_to_database() as connection:
        connection.row_factory = sql.Row
        c = connection.cursor()
        c.execute(query, (args))
        connection.commit()
        rows = c.fetchall()
        return rows


def dbAlter(query, *args):
    with connection_to_database() as connection:
        c = connection.cursor()
        c.execute(query, (args))
        connection.commit()


@client.event
async def on_message(message):
    if message.content.startswith('!add'):
        answers = []

        await client.send_message(message.channel, "Multiple Choice, or True or False? (!M or !TF)")
        res = await client.wait_for_message(timeout=20, author=message.author)

        await client.send_message(message.channel, "---- Add a question to the database: ----")
        question = await client.wait_for_message(timeout=20, author=message.author)
        question = question.content

        if res.content.startswith('!M'):
            await client.send_message(message.channel, "Please add an answer:")

            for i in range(4):
                msg = await client.wait_for_message(timeout=20, author=message.author)
                answers.append(msg.content)
                fmt = '{} left to go...'
                await client.send_message(message.channel, fmt.format(3 - i))

            await client.send_message(message.channel, "What is the correct answer?")
            ans = await client.wait_for_message(timeout=20, author=message.author)
            ans = ans.content
            dbAlter("INSERT INTO quiz VALUES (?, ?, ?, ?, ?, ?, ?)", None, question, answers[0], answers[1], answers[2], answers[3], ans)
        else:
            await client.send_message(message.channel, "Was the question True, or False?")
            ans = await client.wait_for_message(timeout=20, author=message.author)
            ans = ans.content
            dbAlter("INSERT INTO quiz VALUES (?, ?, ?, ?, ?, ?, ?)", None, question, None, None, None, None, ans)
        await client.send_message(message.channel, 'Question Added')
    
    if message.content.startswith('!quizme'):
        question = dbLookup("SELECT * FROM quiz ORDER BY RANDOM() LIMIT 1")

        if(question[0][6] == "True" or question[0][6] == "False"):
            question_string = f"**Question**: \n\n {question[0][1]} \n \n True or False?"
        else:
            question_string = f"**Question**: \n \n {question[0][1]} \n {question[0][2]} \n {question[0][3]} \n {question[0][4]} \n {question[0][5]}?"
        await client.send_message(message.channel, question_string)
        ans = await client.wait_for_message(author=message.author)

        if(ans.content.lower() == question[0][6].lower()):
            await client.send_message(message.channel, f"Correct! **{message.author.name}** has been awarded 100 experience!")
            print(message.author)
            dbAlter("UPDATE user SET experience = experience + 100 WHERE name = ?", str(message.author))

            # Random request to rank question. Ask 20% of the time to help verify question reliability.
            x = random.randint(0, 100)

            if(x > 80):
                msg = await client.send_message(message.channel, 'Was that last question a good one? Use the thumbs up/thumbs down emoji on this message to rank it!')
                res = await client.wait_for_reaction(['👍', '👎'], message=msg, timeout=10)
                await client.send_message(message.channel, '{0.user} gave that last question a {0.reaction.emoji}! Thanks for voting.'.format(res))
        else:
            await client.send_message(message.channel, "Incorrect. Type !quiz to try again.")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)