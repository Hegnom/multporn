
import logging
from telegram.ext import Updater,  MessageHandler, Filters,CallbackQueryHandler,InlineQueryHandler, CommandHandler, CallbackContext
from uuid import uuid4
from telegram import InlineKeyboardButton, InlineKeyboardMarkup,InlineQueryResultArticle, InputTextMessageContent,Update
from multporn import Multporn , Utils
from urllib.parse import urlparse

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# THIS IS TOKEN FILL IT YOUR SELF
TOKEN  ="1840259290:AAEzXAwyU4SiTlh3e8jN-Qd-Xdu-ukgGHtA"


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    start =(
             fr"Hi {user.mention_markdown_v2()} \!"
             '\n\nTo use Multporn bot send any comics, video link from the site\.'
             "\n if you are too lazy you can also search via inline mode\."
             "\n also join https\://t\.me/vdoperbotarchive for further release \.") 

    key_board=[
         [InlineKeyboardButton('SEARCH', switch_inline_query_current_chat ='')],
       ] 
    try:
        update.message.reply_markdown_v2(start,reply_markup=InlineKeyboardMarkup(key_board))
    except:
        pass   


def search_engine(query):
    if query == "":
        query = "loli"
    page1=Utils.Search(str(query),page=1)
    page2=Utils.Search(str(query),page=2)
    page3=Utils.Search(str(query),page=3)
    page4=Utils.Search(str(query),page=4)
    searched= page1+page2+page3+page4
    searchlist=[]
    for i in searched:
        url =urlparse(i["link"]).path
        typeofcontent =url.split("/")[1]
        searchlist.append({"link":i["link"], "thumb":i["thumb"], "name":i["name"], "type":typeofcontent})       
    return searchlist
def content_maker(url):
    page = Multporn(url)
    pagecontenturl=[]
    for i in page.contentUrls:
        if urlparse(i).query  != "":
            pagecontenturl.append(i.removesuffix(urlparse(i).query))
        else:
            pagecontenturl.append(i)
    dic = {"type":page.contentType,"url":pagecontenturl}
    return dic


def inlinequery(update: Update, context: CallbackContext) -> None:
    query=update.inline_query.query
    inline_results = list()
    try :
       results = search_engine(query)
    except:
       results={"name":"Failed to search","thumb":"https://st4.depositphotos.com/2274151/30294/v/950/depositphotos_302946442-stock-illustration-failed-stamp-failed-square-grunge.jpg","link":"this is not working now ","type":"problem!"}
  
    for i in results :

        inline_results.append(InlineQueryResultArticle(id=uuid4(),
                                                       title= i["name"] ,
                                                       thumb_url = i["thumb"],
                                                       description=i["type"],
                                                       input_message_content=InputTextMessageContent(i["link"])  ))

    update.inline_query.answer(inline_results,cache_time=0,auto_pagination=True)

def sender(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("next", callback_data=1)],
        [InlineKeyboardButton("last page", callback_data=-1)],
    ]
    content = Multporn(update.message.text)
    if content.exists == True :
        typeandurl= content_maker(update.message.text)
        if typeandurl["type"] in ["video"]:
            try:
                context.bot.send_video(update.effective_user.id,typeandurl["url"][0])
            except:
                update.message.reply_text("file is too big!(bigger than 20 MB) try some thing smaller or download it directly from:\n"+str(typeandurl["url"][0]))
        if typeandurl["type"] in ["comics","gif","pictures"]:
            context.user_data["typeandurl"]= typeandurl
            if typeandurl["type"] == "gif":
                context.bot.send_animation(update.effective_user.id , typeandurl["url"][0],reply_markup=InlineKeyboardMarkup(keyboard))
            if typeandurl["type"] in ["comics","pictures"]:
                context.bot.send_photo(update.effective_user.id , typeandurl["url"][0],reply_markup=InlineKeyboardMarkup(keyboard))

def key_board_maker(wantedpage,listofurl):
    len_list =len(listofurl)
    last_page =int(len_list)-1
    if int(wantedpage) == 0:
        keyboard = [
            [InlineKeyboardButton("Next", callback_data=1)],
            [InlineKeyboardButton("Last page", callback_data=last_page)],
                    ]
        return keyboard
    if int(wantedpage) == int(len_list)-1:
        keyboard = [
            [InlineKeyboardButton("Previous", callback_data=last_page-2)],
            [InlineKeyboardButton("Firstpage", callback_data=0)],
                    ]
        return keyboard
    if int(wantedpage) == -1 :
        keyboard = [
            [InlineKeyboardButton("Previous", callback_data=last_page-2)],
            [InlineKeyboardButton("Firstpage", callback_data=0)],
                    ]
        return keyboard
    else:
        keyboard = [
            [InlineKeyboardButton("Previous", callback_data=int(wantedpage)-1),InlineKeyboardButton("Next", callback_data=int(wantedpage)+1)],
            [InlineKeyboardButton("Firstpage", callback_data=0),InlineKeyboardButton("Last page", callback_data=last_page)],
                    ]
        return keyboard


def button(update: Update, context: CallbackContext) :
    query = update.callback_query
    query.answer() 
     
    try :
        keyboard = key_board_maker(wantedpage=query.data,listofurl=context.user_data["typeandurl"]["url"]) 
        typeandurl = context.user_data["typeandurl"]
        query.delete_message()
        if typeandurl["type"] == "gif":
            context.bot.send_animation(update.effective_user.id , typeandurl["url"][int(query.data)],reply_markup=InlineKeyboardMarkup(keyboard))
        if typeandurl["type"] in ["comics","pictures"]:        
            context.bot.send_photo(update.effective_user.id , typeandurl["url"][int(query.data)],reply_markup=InlineKeyboardMarkup(keyboard))
        
    except:
        pass

def main() -> None:

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.chat_type.private, sender))
    dispatcher.add_handler(InlineQueryHandler(inlinequery))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()