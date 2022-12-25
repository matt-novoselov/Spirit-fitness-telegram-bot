import SpiritAPI
from aiogram import Bot, Dispatcher, executor, types
import asyncio
import aioschedule
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
admin_id = os.getenv("ADMIN_ID")


def init_db():
    return mysql.connector.connect(
        host=os.getenv("HOST"),
        user=os.getenv("DB_USERNAME"),
        passwd=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
    )


mydb = init_db()


def get_cursor():
    global mydb
    try:
        mydb.ping(reconnect=True, attempts=3, delay=5)
    except mysql.connector.Error as err:
        mydb = init_db()
    return mydb.cursor()


bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Started!")


async def main():
    VisitCount = SpiritAPI.GetMonthVisit()

    mycursor = get_cursor()
    mycursor.execute("SELECT TotalVisits, LastVisit FROM SpiritVisits")
    myresult = mycursor.fetchall()
    TotalVisits = myresult[0][0]
    LastVisit = myresult[0][1]

    if VisitCount < LastVisit and VisitCount != 0:
        sql = "UPDATE SpiritVisits SET TotalVisits='%s' WHERE id=1"
        val = (TotalVisits + VisitCount,)
        mycursor.execute(sql, val)
        mydb.commit()

        sql = "UPDATE SpiritVisits SET LastVisit='%s' WHERE id=1"
        val = (VisitCount,)
        mycursor.execute(sql, val)
        mydb.commit()

        await notifier()

    elif VisitCount > LastVisit:
        sql = "UPDATE SpiritVisits SET TotalVisits='%s' WHERE id=1"
        val = (TotalVisits + VisitCount - LastVisit,)
        mycursor.execute(sql, val)
        mydb.commit()

        sql = "UPDATE SpiritVisits SET LastVisit='%s' WHERE id=1"
        val = (VisitCount,)
        mycursor.execute(sql, val)
        mydb.commit()

        await notifier()

    mycursor.close()
    mydb.close()


async def notifier():
    mycursor = get_cursor()
    mycursor.execute("SELECT TotalVisits, LastVisit FROM SpiritVisits")
    myresult = mycursor.fetchall()
    TotalVisits = myresult[0][0]
    mycursor.close()
    mydb.close()

    await bot.send_message(admin_id, f"Посещено платных тренировок: {TotalVisits}\n\nПосещено в этом блоке: {TotalVisits%5}/5", parse_mode="Markdown")
    if TotalVisits % 5 == 0:
        await bot.send_message(admin_id, "Блок занятий закончился.", parse_mode="Markdown")




async def scheduler():
    aioschedule.every(6).hours.do(main)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())
    await main()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
