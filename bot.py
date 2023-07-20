from telegram import *
from telegram.ext import *
import requests
import json
from types import SimpleNamespace
import math
import random
import time
from datetime import datetime
import pytz

kyc = "👨‍💻 Xác minh KYC"
uytin = "💎 DS Uy tín"

domain = "https://chousd.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    buttons = [[KeyboardButton(uytin)]]

    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Chào mừng bạn đến với <b>Chợ MMO</b>. Click nút bên dưới để kiểm tra danh sách uy tín.", reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)


async def messageHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    chat_id = update.effective_chat.id

    if update.message.chat.type != "private":

        if "/uytin" in update.message.text:
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text='|<', callback_data='first'),
                  InlineKeyboardButton(text='<', callback_data='prev'),
                  InlineKeyboardButton(text='>', callback_data='next'),
                  InlineKeyboardButton(text='>|', callback_data='last')]],
            )

            await context.bot.send_message(chat_id, text=content(1), reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)

        if "uy tín" in update.message.text:

            requests.post(f"{domain}/api/add-user",{'username': f"@{username}"})

            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text='VOTE UY TÍN', callback_data='vote')]],
            )

            start_time = time.time()
            seconds = abs(time.time() - start_time - 300)
            time_remaining = time.strftime("%M:%S", time.gmtime(seconds))

            text = f"<b>Biểu quyết uy tín @{username}</b>\n<i>Thời gian còn: {time_remaining}</i> ⏱"

            msg = await context.bot.send_message(chat_id, text=text, reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)

            #delete last message
            try:
                res = requests.get(f"{domain}/api/votings/@{username}")
                last_msg_id = res.json()["msg_id"]
                await context.bot.delete_message(message_id=last_msg_id, chat_id='-654706459')

                requests.post(f"{domain}/api/voting", {'username': f'@{username}','start_time': start_time, 'msg_id':  msg.message_id})
            except:
                requests.post(f"{domain}/api/voting", {'username': f'@{username}','start_time': start_time, 'msg_id':  msg.message_id})

        return

    # if username is None:
    #     await context.bot.send_message(chat_id, text="Vui lòng cập nhật Username của bạn!")
    #     return

    # if kyc in update.message.text:
    #     link = f"https://kyc.chootc.com/#/{username}-{chat_id}"

    #     reply_markup = InlineKeyboardMarkup(
    #         [[InlineKeyboardButton(text='Tiến hành KYC', url=link)]],
    #     )

    #     text = "<b>🔥 Xác minh danh tính của bạn!</b> \n \n<i>Hãy thực hiện theo các bước dưới đây</i> \n1. Chuẩn bị thiết bị của bạn: cho phép trình duyệt truy cập định vị và camera. \n2. Nhấn vào nút <b>Tiến hành KYC</b>. \n3. Làm theo hướng dẫn trên trình duyệt."

    #     await context.bot.send_message(chat_id, text=text, reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)

    if "/uytin" in update.message.text or uytin in update.message.text:

        if "@" in update.message.text:

            username = update.message.text[8:]
            res = requests.get(
                f"{domain}/api/check-user/{username}")

            if res.text == "":
                text = f"@{username} không tồn tại trong hệ thống!"
                await context.bot.send_message(chat_id, text=text)
                return

            if res.json()['transaction'] is None:
                text = f"@{username} chưa có giao dịch nào thành công"
            else:
                text = f"@{username} đã giao dịch thành công {res.json()['transaction']} lần"

                if res.json()['reputation'] == 'yes':
                    text += " - Uy tín 💎"

            await context.bot.send_message(chat_id, text=text)
            return

        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text='|<', callback_data='first'),
             InlineKeyboardButton(text='<', callback_data='prev'),
             InlineKeyboardButton(text='>', callback_data='next'),
             InlineKeyboardButton(text='>|', callback_data='last')]],
        )

        await context.bot.send_message(chat_id, text=content(1), reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)

    # if "/kyc" in update.message.text:

    #     if "@" not in update.message.text:
    #         await context.bot.send_message(chat_id, text="Sai cú pháp, phải có @ trước Username!")
    #         return

    #     username = update.message.text[6:]
    #     res = requests.get(
    #         f"{domain}/api/check-user/{username}")

    #     if res.text == "":
    #         text = f"@{username} chưa gửi thông tin KYC!"
    #         await context.bot.send_message(chat_id, text=text)
    #         return

    #     if res.json()['kyc'] == 'pending':
    #         text = f"@{username} KYC đang chờ xét duyệt!"
    #     if res.json()['kyc'] == 'success':
    #         text = f"@{username} đã KYC thành công!"
    #     if res.json()['kyc'] == 'failed':
    #         text = f"@{username} KYC thất bại! Liên hệ Admin để được hỗ trợ."

    #     await context.bot.send_message(chat_id, text=text)


def content(page):
    res = requests.get(f"{domain}/api/get-top?page={page}")

    text = "<b>🔥 Xếp hạng uy tín 🔥</b>\n\n<i>Xếp hạng dựa theo số lần xin uy tín thành công</i>\n"

    for index, item in enumerate(res.json()['data']):
        text += f"- {item['username']} ({item['transaction']} lần)"
        if item['reputation'] == 'yes':
            text += " - Uy tín 💎\n"
        else:
            text += "\n"

    text += f"\nTrang: {page}/{math.ceil(res.json()['total']/res.json()['per_page'])}"
    return text


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_id = update.effective_message.id
    chat_id = update.effective_chat.id
    username = update.effective_user.username

    query = update.callback_query
    await query.answer()

    if query.data in ["first", "prev", "next", "last"]:

        page = update.effective_message.text[-3:]
        current_page = int(page[:1])
        last_page = int(page[-1:])

        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text='|<', callback_data='first'),
              InlineKeyboardButton(text='<', callback_data='prev'),
              InlineKeyboardButton(text='>', callback_data='next'),
              InlineKeyboardButton(text='>|', callback_data='last')]],
        )

        if query.data == "first":
            if current_page == 1:
                return
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=content(1), reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)
        if query.data == "prev":
            if current_page > 1:
                p = current_page - 1
            else:
                return
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=content(p), reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)
        if query.data == "next":
            if current_page < last_page:
                p = current_page + 1
            else:
                return
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=content(p), reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)
        if query.data == "last":
            if current_page == last_page:
                return
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=content(page[-1:]), reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)

        return
    
    if query.data in ["vote"]:
        #get username is voted
        voting_user = update.effective_message.text.split("\n")[0].split()[-1]

        if username in voting_user:
            return
        
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text='VOTE UY TÍN', callback_data='vote')]],
        )

        res = requests.get(f"{domain}/api/votings/{voting_user}")
        start_time = res.json()["start_time"]
        voted_list = res.json()["voted_user"]

        if time.time() - float(start_time) > 300:
            text = update.effective_message.text.split("\n")
            del text[1]
            text[0] = f"<b>Kết quả biểu quyết uy tín {voting_user}</b>"
            text[1] = f"<b>{text[1]}</b>"
            text[-1] = f"<b>{text[-1]}</b>"

            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="\n".join(text), parse_mode=constants.ParseMode.HTML)
        else:
            # get current time
            seconds = abs(time.time() - float(start_time) - 300)
            time_remaining = time.strftime("%M:%S", time.gmtime(seconds))
            # current_time = time.strftime("%H:%M", time.localtime())
            current_time = datetime.now(tz=pytz.timezone('Asia/Ho_Chi_Minh'))
            current_hour = str(current_time)[11:16]

            #check user is admin
            response = requests.get(f"{domain}/api/isadmin/@{username}")
            if response.text:
                is_admin = "(Admin)"
            else:
                is_admin = ""

            #check user and set vote
            global voted_user

            if not voted_list:
                voted_user = f'@{username} {is_admin}'
                requests.put(f"{domain}/api/voting/{voting_user}",{'voted_user': voted_user})
            if voted_list and username not in voted_list:
                voted_user = f'{voted_list}\n@{username} {is_admin}'
                requests.put(f"{domain}/api/voting/{voting_user}",{'voted_user': voted_user})
            if voted_list and username in voted_list:
                return
            
            #export voted user list
            percent = 0
            has_admin = False
            voted_array = voted_user.split("\n")
            for index, item in enumerate(voted_array):
                if not index:
                    list_text = f"{index+1}. {item}"
                else:
                    list_text = f"{list_text}\n{index+1}. {item}"
                
                if "Admin" in item:
                    percent += 30
                    has_admin = True
                else:
                    percent += 15

            if percent < 100:
                result = f"Tỷ lệ: {percent}% | Chưa đủ uy tín để giao dịch 🔴"
            else:
                if has_admin:
                    result = f"Tỷ lệ: 100% | Đã đủ uy tín để giao dịch 🟢"
                    requests.post(f"{domain}/api/update-rep",{'username': voting_user})
                else:
                    percent_random = random.randrange(83, 96)
                    result = f"Tỷ lệ: {percent_random}% | Chưa đủ uy tín để giao dịch 🔴"   

            text = f"<b>Biểu quyết uy tín {voting_user}</b>\n<i>Thời gian còn: {time_remaining}</i> ⏱\n<b>Danh sách đã cho uy tín:</b>\n{list_text}\n\n<b>{result}</b>"
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup, parse_mode=constants.ParseMode.HTML)


app = ApplicationBuilder().token(
    "6221060241:AAHk9evaieypMU8SnO-H8YhnuMRVA0UVi8g").build()

app.add_handler(CommandHandler("start", start)) 
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.ALL, messageHandler))


# auto send message
async def callback_minute(context: ContextTypes.DEFAULT_TYPE):

    list = [
        "<b>Thành Viên Uy Tín Là Ai ?</b>\nLà những thành viên buôn bán thâm niên, chuyên nghiệp, có uy tín cao trong cộng đồng. Huy hiệu uy tín phải được đội ngũ bản quản lý chợ cấp.\n<b>Làm thế nào để trở thành TV uy tín ?</b>\n- Có trên 6 tháng hoạt động buôn bán tại Chợ OTC VN.\n- Giao dịch thành công tối thiểu 30 lần.\n- Được check thông tin cụ thể và phê duyệt từ 3 Admin.\n\n<i>Chat /uytin với bot @ChoOTCVN_bot để kiểm tra danh sách uy tín!</i>",

        ]
    
    # try:
    #     res = requests.get(f"{domain}/api/setup")
    #     last_msg_id = res.json()[0]["value"]
    #     await context.bot.delete_message(message_id=last_msg_id, chat_id='-1001871429218')
    #     msg = await context.bot.send_message(chat_id='-1001871429218', text=random.choice(list), parse_mode=constants.ParseMode.HTML)
    #     requests.put(f"{domain}/api/setup/3", {'value': msg.message_id})
    # except:
    #     msg = await context.bot.send_message(chat_id='-1001871429218', text=random.choice(list), parse_mode=constants.ParseMode.HTML)
    #     requests.put(f"{domain}/api/setup/3", {'value': msg.message_id})


# job_queue = app.job_queue

# job_minute = job_queue.run_repeating(callback_minute, interval=7200, first=10)

app.run_polling()
