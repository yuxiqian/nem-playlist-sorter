# -*- coding: UTF-8 -*-
from song import Song
from PIL import Image, ImageDraw2, ImageFont
from MusicBoxApi import api as NetEaseApi
from ncmbot.ncmbot import *

import os
import json
import getpass
import platform


def separator():
    try:
        print("-" * os.get_terminal_size().columns)
    except OSError:
        print("-" * 17)


buf_image = Image.new('RGB', (1024, 60), color='white')
buf_obj = ImageDraw2.Draw(buf_image)

netease = NetEaseApi.NetEase()
playlist = []
padding = 9
safe_ratio = 1.4

separator()
font_name = input(
    """请输入用于判定的字体名称：
    Windows 建议 msyh.ttc（默认）或 Arial。
    macOS 建议 PingFang（默认）或 Songti。
    Linux 建议思源体系列。
为了显示效果考虑，请尽量选择非等宽字体。
直接按 Enter 来选择默认值
>>> """)

if len(font_name) == 0:
    sysstr = platform.system()
    if sysstr == "Windows":
        font_name = "msyh.ttc"
    elif sysstr == "Darwin":
        font_name = "PingFang"
    else:
        font_name = "FreeSans"


try:
    font = ImageDraw2.Font('black', font_name, 60)
    font_small = ImageDraw2.Font('black', font_name, 30)
except:
    print('%s 不是可用的字体文件。' % font_name)
    exit(-1)


def get_pixel_width(string):
    if string == None:
        return 0
    # 画到 BUF_OBJ 上，获取其宽度像素值
    size_tuple = buf_obj.textsize(string, font)
    if len(size_tuple) == 2:
        return size_tuple[0]
    return 0


separator()


try:
    playlist_id = input("请输入歌单 ID 或 URL…\n>>> ").split('&userid=')[0]       \
        .replace("https://music.163.com/#/playlist?id=", "")                    \
        .replace("https://music.163.com/#/my/m/music/playlist?id=", "")         \
        .replace("https://music.163.com/playlist?id=", "")
    datalist = netease.playlist_detail(playlist_id)
except:
    print('%s 不是可用的歌单 ID。' % playlist_id)
    exit(-2)

separator()

try:
    sort_by = input("""想要依照哪个字段进行排序？
\tn - 依照歌曲名称（Name）进行排序（默认）
\ta - 依照专辑名称（Album）进行排序
\tr - 依照艺术家（aRtist）进行排序
>>> """).lower()[0]
except:
    print('解析输入失败。')
    exit(-3)


for song in datalist:
    new_song = Song()
    # print(song)
    # input()
    new_song.name = song["name"]
    new_song.album = song["album"]["name"]
    new_song.id = song["id"]
    artists = []
    for artist in song["artists"]:
        artists.append(artist["name"])
    new_song.artist = ' / '.join(artists)

    if sort_by == 'a':
        new_song.name_size = get_pixel_width(new_song.album)
    elif sort_by == 'r':
        new_song.name_size = get_pixel_width(new_song.artist)
    else:
        new_song.name_size = get_pixel_width(new_song.name)
    playlist.append(new_song)

playlist.sort(key=lambda x: x.name_size)

track_ids = []


# for item in playlist:
#     print("歌曲名称 = %s, 相对长度 = %d" % (item.name, item.name_size))
# results.append(item.name)
# results.append("%s - %s\n" % (item.artist, item.album))
# if item.name_size > max_width:
#     max_width = item.name_size

separator()
controller = input(
    "处理了 %d 首歌。\n按回车来登录「网易云音乐」账号并进行同步。或者，在此之前输入 i 来从长到短地排列歌曲。\n>>> " % len(playlist))

if controller != 'I' and controller != 'i':
    playlist.reverse()


for p in playlist:
    track_ids.append(str(p.id))

trackIdString = '[' + ', '.join(track_ids) + ']'

# result_image = Image.new(
#    'RGB', (1080, len(playlist) * (130)), color = "white")
# result_draw = ImageDraw2.Draw(result_image)

# frame_width = 1080

# for i in range(0, len(playlist)):
#    result_draw.text((padding * 5, padding + 130 * i),
#                     results[2 * i], font=font)
#    result_draw.text((padding * 5, padding + 130 * i + 80),
#                     results[2 * i + 1], font=font_small)

#    result_draw.line((padding * 5, padding + 130 * i + 120),
#                     (frame_width, padding + 130 * i + 120), 'gray')


# result_image.show()

# file_name = input("输入文件名来保存 PNG 文件 >>> ")
# result_image.save("%s.png" % file_name)

separator()

while True:
    try:
        option = int(
            input("想要如何登录到网易云音乐？\n\t1 - 用账号和密码\n\t2 - 用 HTTP Cookie\n>>> "))
    except:
        continue
    if option == 1:
        separator()
        login_name = input("输入手机号码…\n>>> ")
        # if len(login_name) != 11:
        #     print('%s 不是合法的手机号码。' % login_name)
        #     exit(-2)

        login_password = getpass.getpass("输入密码…\n>>> ")

        # if '@' in login_name:
        #     bot, resp = login(login_password, email=login_name)
        # else:
        bot, resp = login(login_password, phone=login_name)

        # print(json.dumps(dict(resp.headers)))
        # print(resp.content.decode())

        login_resp = json.loads(json.dumps(dict(resp.headers)))['Set-Cookie']
        break
    elif option == 2:
        separator()
        cookie_content = input("输入 Cookie 内容…\n>>> \n")
        login_resp = cookie_content
        break

MUSIC_U = login_resp.split('MUSIC_U=')[1].split(';')[0]


user_token = login_resp.split('__csrf=')[1].split(';')[0]

# user_token = 'fakefakefake'

# input("token = %s" % user_token)

# print(personal_fm().content.decode())
# input()

separator()
playlist_name = input("请输入要创建的新歌单名…\n>>> ")

# input(MUSIC_U)
bot = NCloudBot(MUSIC_U)
bot.method = 'CREATE_LIST'
bot.params = {"csrf_token": user_token}
bot.data = {"name": str(playlist_name), "csrf_token": user_token}
bot.send()

result = json.loads(bot.response.content.decode())

separator()
if result['code'] != 200:
    print("创建歌单失败。")
    exit(-4)

# separator()
# print(result)

# separator()

new_playlist_id = result['id']

final_result = add_song(str(new_playlist_id), trackIdString, MUSIC_U)

# print(final_result.content.decode())
# separator()

final_response = json.loads(final_result.content.decode())['code']

# print(resp)

if final_response == 200:
    print("成功！\n现在应该可以在\n https://music.163.com/#/playlist?id=%s \n访问新歌单了。" %
          new_playlist_id)
    exit(0)
else:
    print("往歌单中添加歌曲失败…")
    exit(-5)
