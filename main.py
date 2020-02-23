import SH1106
import Bilibili
import Keyboard
import time, os, sys
from PIL import Image, ImageDraw, ImageFont
os.chdir(sys.path[0])
print(sys.path[0])

FPS = 5
disp = SH1106.SH1106()
que = Keyboard.Init()
fontBig = ImageFont.truetype(os.path.abspath('Font.otf'), 13)
fontMedium = ImageFont.truetype(os.path.abspath('Font.otf'), 12)
fontSmall = ImageFont.truetype(os.path.abspath('Font.otf'), 11)

bdev = None
while bdev is None:
    try:
        bdev = Bilibili.BDev(debug=False, path=sys.path[0])
    except:
        print("Wait for network")
        time.sleep(1)

minute_tick, hour_tick = 0, 0
upstat, account = None, []

def update(flag = False):
    global minute_tick, hour_tick, upstat, account
    news = False

    if minute_tick == 0 or flag:
        ret = bdev.account()
        news = (len(account) > 0 and account[-1] != ret[0])
        if flag and len(account) > 0: account.pop(-1)
        while len(account) >= 360: account.pop(0)
        if ret[0] is not None: account.append(ret[0])
        if ret[0] is None: minute_tick -= 1
        # print("Update A")

    if hour_tick == 0:
        ret = bdev.upstat()
        if ret[0] is not None: upstat = ret[0]
        if ret[0] is None: hour_tick -= 1
        # print("Update B")

    minute_tick = (minute_tick + 1) % (10 * FPS)
    hour_tick = (hour_tick + 1) % (3600 * FPS)

    return news

def render(x, flag = False):
    f = ""
    if flag: f = "+"
    if x < 0: f, x = "-", -x
    if x > 1000000000: return "%s%.1fB" % (f, x / 1000000000)
    if x > 1000000: return "%s%.1fM" % (f, x / 1000000)
    if x > 1000: return "%s%.1fK" % (f, x / 1000)
    return f + str(x)

def logic(GUI):
    # Get Last Input
    key = -1
    while not que.empty():key = que.get()
    if key != -1: GUI = key

    # Update
    if key != -1: update(True)

    # Display
    global fontBig, fontMedium, fontSmall
    image = Image.new('1', (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image)

    if GUI == 0:
        if len(account) == 0: return GUI, image, key != -1
        followers, likes = account[-1]["followers"], account[-1]["likes"]
        followers_str, likes_str = ("关注 %s" % render(followers)), ("点赞 %s" % render(likes))
        delta_followers, delta_likes = account[-1]["followers"] - account[0]["followers"], account[-1]["likes"] - account[0]["likes"]
        if delta_followers != 0: followers_str += render(delta_followers, True)
        if delta_likes != 0: likes_str += render(delta_likes, True)
        draw.text((1, 0), "%s Lv.%d" % (account[-1]["name"], account[-1]["level"]), font=fontBig, fill=0)
        draw.text((1, 16), "播放 %s" % render(account[-1]["archives"] + account[-1]["articles"]), font=fontMedium, fill=0)
        draw.text((65, 16), "消息 %s" % render(account[-1]["unread"]), font=fontMedium, fill=0)
        draw.text((1, 32), followers_str, font=fontMedium, fill=0)
        draw.text((1, 48), likes_str, font=fontMedium, fill=0)

    if GUI == 1:
        if upstat is None: return GUI, image, key != -1
        draw.text((1, 0), "播放 %s%s" % (render(upstat["click"][0]), render(upstat["click"][1], True)), font=fontMedium, fill=0)
        draw.text((1, 16), "粉丝 %s%s" % (render(upstat["fans"][0]), render(upstat["fans"][1], True)), font=fontMedium, fill=0)
        draw.text((1, 32), "评论 %s%s" % (render(upstat["reply"][0]), render(upstat["reply"][1], True)), font=fontMedium, fill=0)
        draw.text((1, 48), "弹幕 %s%s" % (render(upstat["dm"][0]), render(upstat["dm"][1], True)), font=fontMedium, fill=0)

    if GUI == 2:
        if upstat is None: return GUI, image, key != -1
        draw.text((1, 0), "投币 %s%s" % (render(upstat["coin"][0]), render(upstat["coin"][1], True)), font=fontMedium, fill=0)
        draw.text((1, 16), "分享 %s%s" % (render(upstat["share"][0]), render(upstat["share"][1], True)), font=fontMedium, fill=0)
        draw.text((1, 32), "收藏 %s%s" % (render(upstat["fav"][0]), render(upstat["fav"][1], True)), font=fontMedium, fill=0)
        draw.text((1, 48), "充电 %s%s" % (render(upstat["elec"][0]), render(upstat["elec"][1], True)), font=fontMedium, fill=0)

    return GUI, image, key != -1

if __name__ == "__main__":
    try:
        # Initialize library.
        disp.Init()
        disp.clear()

        GUI, COLD = 0, 0
        # 0 Dashboard
        # -1 Sleep
        # 1,2 Up Stat
        while True:
            # Logic
            GUI, image, newsK = logic(GUI)
            newsU = update()

            # Sleep
            if newsK or newsU:
                COLD = 0
                if GUI == -1: GUI = 0
            if COLD >= 10 * FPS: COLD, GUI = 10 * FPS, -1
            COLD += 1

            # Draw
            disp.ShowImage(disp.getbuffer(image))
            time.sleep(1. / FPS)

    except IOError as e:
        print(e)
    except KeyboardInterrupt:
        exit()
    finally:
        disp.clear()
        Keyboard.clear()