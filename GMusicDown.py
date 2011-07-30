#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# auther: jeswang
# finished time: 2011.7.29

import os 
import stat
import urllib2
import urllib
import time,datetime 
import threading
from time import sleep
from BeautifulSoup import *

def getMusicName(url):
    url = url.replace('/',' ').replace('?', ' ')
    url = re.compile('[^ ]*.mp3').search(url).group()
    url = url.encode('ascii','ignore') 
    s = urllib.unquote(url)
    s = urllib.unquote(s)
    return s.decode("utf-8")

class getFile(threading.Thread): #The timer class is derived from the class threading.Thread 
    def __init__(self, url, path):
        threading.Thread.__init__(self) 
        self.url = url
        self.path = path
        self.thread_stop = False  
   
    def run(self): #Overwrite run() method, put what you want the thread do here  
        
        print "Str ", getMusicName(self.url), datetime.datetime.now() 
        data = urllib.urlretrieve(self.url, self.path)
        dlfile_stat = os.stat(self.path)
        size = dlfile_stat[stat.ST_SIZE]
        if size < 400:
            print "It's a html"
            f = open(self.path, "r")
            temp_soup = BeautifulSoup(f.read())
            print temp_soup.find('a')['href']
            f.close()
            os.remove(self.path)
            data = urllib.urlretrieve(temp_soup.find('a')['href'], self.path)
        print "End ", getMusicName(self.url), datetime.datetime.now() 
        self.stop()

    def stop(self):
        self.thread_stop = True 

if __name__ == "__main__":
    
    song_downlist = []
    threadPool = []
    print "请输入专辑的URL："
    album_url = raw_input()
    print "请输入保存的路径："
    savePlace = raw_input()
    
    if not savePlace:
        savePlace = "./album/"
    print "使用路径" + savePlace
    if not album_url :
        print "Get nothing!"
    else:
        c=urllib2.urlopen(album_url)
        soup=BeautifulSoup(c.read())
        song_list = soup.find('table', id='song_list')
        songs = song_list.findAll('tbody')
        #print song_list
        print "专辑共有"+len(songs).__str__()+"首歌曲。"
        
        songs_url = []
        for song in songs:
            songs_url.append("http://www.google.cn/music/top100/musicdownload?id="+song.contents[0]['id'][3:])
            #print songs_url
        threadAmount = len(songs)
        
        count = 0
        retryCount = 0
        newToken = 0
        response = ''
        for url in songs_url:
            print url
            song_html=urllib2.urlopen(url)
            song_soup=BeautifulSoup(song_html.read())
            song_html.close()
            result = song_soup.find('div', { "class" : "download"})
            while not result:
                #sleep(1.01)
                retryCount = retryCount + 1
                print "第"+str(retryCount)+"次尝试"
                if retryCount < 2 and not newToken:
                    token='ACEniO2oVYzMKymfcpq17C--HuvDeWhXk1LOL5OS3w-Z2tDGsbO51j3VoYbEMzdIAIHSMiw1V8ubTooFpf8OUSCUP5js-x_TgLGalfk94OeGxcyvVfAq_f-zF_qxzXSHZ059eGojA36x6GDIZrasmwIR567SuTB5zw'
                elif not newToken or retryCount > 5:
                    print "因为验证码的原因你需要一些额外的操作："
                    print "1. 在浏览器其打开网址" + url
                    print "2. 输入验证码"
                    print "3. 将验证成功页面的URL粘贴到下方："
                    token = raw_input()
                    response = re.compile(r'response=[^&]*').search(token).group()[9:]
                    #print response
                    token = re.compile(r'tok=[^&]*').search(token).group()[4:]
                    #print token
                    newToken = 1
                    retryCount = 0
                #print url+"&tok="+token+"&response=wvcfrvh&submitBtn=%E6%8F%90%E4%BA%A4"
                song_html=urllib2.urlopen(url+"&tok="+token+"&response="+response+"&submitBtn=%E6%8F%90%E4%BA%A4")
                song_soup=BeautifulSoup(song_html.read())
                song_html.close()
                result = song_soup.find('div', { "class" : "download"})
            
            retryCount = 0    
            #print result
            song_downlist.append("http://www.google.cn"+song_soup.find('div', { "class" : "download"}).find('a', href=re.compile('^/music*'))['href'])
            count = count + 1
            print 'Got ' + str(count) + '/' + len(songs).__str__()
            #print song_soup.find('div', { "class" : "download"}).find('a', href=re.compile('^/music*'))['href']
            #sleep(1.01)
            #print song_soup
            #http://file3.top100.cn/201107272306/6DC2902AFD8BAD372AB231C20FB4FBB6/Special_113641/Papercut%20(Album%20Version).mp3
        
        filename = ''
        for download_url in song_downlist:
            
            filename = getMusicName(download_url)
            print filename
            
            th = getFile(download_url ,savePlace+filename)
            threadPool.append(th) 
        
        for down_thread in threadPool:
            down_thread.start()

#End of file.
    
    
    
    
    
    
    