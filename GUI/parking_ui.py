#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
from PyQt5.QtWidgets import  QTableWidget,QTableWidgetItem
from generated_ui import *
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton)
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QTableWidget,QVBoxLayout,
    QTableWidgetItem, QHBoxLayout,QSplitter,QGroupBox)
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QDir, Qt, QUrl, QTimer  
import boto3    
from datetime import datetime  
import time  


#to add background image
import sys
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtWidgets import *                     

#dynamic pricing function:
#Base prices: 6PM - 9AM: 1.99$
#Base prices: 9AM - 1PM: 3.99$
#Base prices: 1PM - 6PM: 2.99$
base_price = [1.99]*9 + [3.99]*4 + [2.99]*5 + [1.99]*6
#occupancy > 50%: add 1$ to base price
#occupancy > 80%: add 2$ to base price
#global price for 24hrs
price = base_price[:]

def pricing_info(spot_db):
    global price
    # get the present time
    time_obj = time.localtime()
    hour_time = time_obj.tm_hour
    
    # global price is reset at 00:00 to base_price
    if time_obj.tm_hour == 0 and time_obj.tm_min == 0:
        price = base_price[:]
        
    # get the occupancy status
    count = 0.0
    for i in range(len(spot_db)):
        if spot_db[i]['spot_no'] >= 1 and spot_db[i]['status']=='occupied':
            count += 1
    occupancy = (count*100.0)/6.0
    
    # add to base_price
    newval = base_price[hour_time]
    if occupancy > 80:
        newval = base_price[hour_time] + 2.0
    elif occupancy > 50:
        newval = base_price[hour_time] + 1.0
    
    # update price of the hour
    price[hour_time] = newval
    
    '''
    # static pricing
    if hour_time > 00 and hour_time <=9:
        price = 1.99
    elif hour_time > 9 and hour_time <=13:
        price = 3.99
    elif hour_time >13 and hour_time <=18:
        price = 2.99
    elif hour_time >18 and hour_time <= 24:
        price = 1.99  
    else:
        price = 1.99 
    '''      
          
    ui.price_label_15.setText(str(price[hour_time])+'$')


# create db with spot information
def get_spot_db():
    '''
    db = []
    a = {'spot_no':2,'status':'occupied','entry_time':(12,45)}
    b = {'spot_no':5,'status':'occupied','entry_time':(13,45)}
    c = {'spot_no':6,'status':'occupied','entry_time':(10,45)}
    d = {'spot_no':4,'status':'occupied','entry_time':(8,45)}
    e = {'spot_no':1,'status':'empty','entry_time':(8,45)}
    db.append(a)
    db.append(b)
    db.append(c)
    db.append(d)
    db.append(e)
    '''
    dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
    table = dynamodb.Table('SlotInformation')
    response = table.scan()
    items = response['Items']
    list_dict=[]
    
    for i in range(len(items)):
        dict_keys = {'spot_no':None,'status':None,'entry_time':None}
        list_dict.append(dict_keys)
    
    for j in range(len(items)):
        x= items[j]['Slot']
        list_dict[j]['spot_no']=int(x)
        x= items[j]['SlotStatus']
        list_dict[j]['status']=x
        x= items[j]['SlotTime']
        list_dict[j]['entry_time']=x
    
    return list_dict
    
# create db with license information
def get_license_db():
    '''
    db = []
    a = {'vehicle_no':'7AGX258','entry_time':(12,45),'exit_time':(12,45)}
    b = {'vehicle_no':'7NTN556','entry_time':(13,45),'exit_time':(12,45)}
    c = {'vehicle_no':'34GTY90','entry_time':(10,45),'exit_time':(12,45)}
    d = {'vehicle_no':'4457GT7','entry_time':(8,45),'exit_time':(12,45)}
    e = {'vehicle_no':'652FTR','entry_time':(8,45),'exit_time':(12,45)}
    db.append(a)
    db.append(b)
    db.append(c)
    db.append(d)
    db.append(e)
    '''
    dynamodb = boto3.resource('dynamodb',region_name='us-east-2')
    table = dynamodb.Table('LicensePlate')
    response = table.scan()
    items = response['Items']
    
    license_dict=[]
    
    for i in range(len(items)):
        dict_keys = {'vehicle_no':None,'entry_time':None,'exit_time':None}
        license_dict.append(dict_keys)
    
    for j in range(len(items)):
        #print(len(items))
        x= items[j]['Licenseplate']
        license_dict[j]['vehicle_no']=x
        x= extract_string2tuple(items[j]['EntryTime'])
        license_dict[j]['entry_time']=x
        if 'ExitTime' in items[j]:
            x=extract_string2tuple(items[j]['ExitTime'])
        else:
            x=None
        license_dict[j]['exit_time']=x
    
    #print(license_dict)
    return license_dict
    
#create tuple from string
def extract_string2tuple(s):
    datetime_object = datetime.strptime(s,'%m-%d-%Y %H:%M:%S')
    return (datetime_object.hour,datetime_object.minute)
    
#extract tuple values
#creates string from tuple
def extract_tuple2string(a):
    hr = a[0]
    mi = a[1]
    s = '%d:%d' % (hr,mi)
    return s
    #return '%s : %s' % (str(hr), str(mi))

#extract hour only
def extract_hr(a):
    hr = a[0]
    return hr

#extract minutes only
def extract_min(a):
    mi = a[1]
    return mi    
    
#to display number of spots available 
def number_of_spots_label(spot_db):
    count =0
    num = len(spot_db)
    for i in range(num):
    #for i in range(6):
        if spot_db[i]['spot_no'] >= 1 and spot_db[i]['status']=='occupied':
            count +=1
    count =  6 - count    
    ui.no_spots_label.setText(str(count))   

#to update the table 
def update_table(license_db):
    cols = 4
    if len(license_db) >= 1:
        for i in range(len(license_db)):
            #ui.tableWidget.setItem(i,0, QTableWidgetItem(str(db[i]['spot_no'])))
            ui.tableWidget.setItem(i,0, QTableWidgetItem(str(license_db[i]['vehicle_no'])))
            ui.tableWidget.setItem(i,1, QTableWidgetItem(extract_tuple2string(license_db[i]['entry_time'])))
            if license_db[i]['exit_time'] != None:
                ui.tableWidget.setItem(i,2, QTableWidgetItem(extract_tuple2string(license_db[i]['exit_time'])))
            #if license_db[i]['amount_due'] != None:   
                #ui.tableWidget.setItem(i,5, QTableWidgetItem(str(db[i]['amount_due'])))
            #ui.tableWidget.setItem(i,2, QTableWidgetItem("Full"))
  
 
#get spot_labels and put it in a list
def  make_listOf_spotLabels():
    label_list=[]
    label_list.append(ui.spot_no_1) 
    label_list.append(ui.spot_no_2) 
    label_list.append(ui.spot_no_3) 
    label_list.append(ui.spot_no_4) 
    label_list.append(ui.spot_no_5) 
    label_list.append(ui.spot_no_6) 
    return label_list
    

#to update filled spots with images
def update_filled_spots(spot_db,label_list):
    found = False
    size = len(label_list)
    for i in range(size):
         found = False
         for j in range(len(spot_db)):
             if spot_db[j]['spot_no']==i+1 and spot_db[j]['status'] == 'occupied':
                 found = True
                 break
         if found==True:
             grview = label_list[i]
             scene = QGraphicsScene()
             scene.addPixmap(QPixmap('car_occupied1.jpg'))
             grview.setScene(scene)
             grview.fitInView(scene.sceneRect()) 
        
         else:
             grview = label_list[i]
             scene = QGraphicsScene()
             scene.addPixmap(QPixmap('car_empty1.jpg'))
             grview.setScene(scene)
             grview.fitInView(scene.sceneRect())  
             
             
#to calculate amout due
def amount_due(license_db):
    global price
    due_time =0
    final_price =0.00
    for i in range(len(license_db)):
        if license_db[i]['exit_time'] != None:
            hr_en = extract_hr(license_db[i]['entry_time'])
            hr_ex = extract_hr(license_db[i]['exit_time'])
            mi_en = extract_min(license_db[i]['entry_time'])           
            mi_ex = extract_min(license_db[i]['exit_time'])
            
            # dynamic pricing
            if hr_ex >= hr_en:
                final_price = 0.0
                for p in range(int(hr_en),int(hr_ex)+1):
                    final_price += price[p]
            else:
                # wraps around - Max 24 hours
                final_price = 45.0  
            
            # if car exits in 15 min, then there is no cost
            #if hr_ex == hr_en and (mi_ex - mi_en) <= 15:
            #    final_price = 0.0
            
            final_price = round(final_price, 2)
            
            '''
            # static:
            price_t = 1.99
            hr_en = hr_en*60 + mi_en 
            hr_ex = hr_ex *60+ mi_ex
            due_time = hr_ex - hr_en
            final_price = due_time * (price_t/60)
            final_price = round(final_price, 2)
            '''
            
            ui.tableWidget.setItem(i,3, QTableWidgetItem(str(final_price)+'$'))

            
def update_gui():
    spot_db = get_spot_db()
    license_db = get_license_db()
    
    # update global price
    pricing_info(spot_db)
    
    # spots 
    number_of_spots_label(spot_db)
    
    # update the gui table
    update_table(license_db)
    
    label_list = make_listOf_spotLabels()
    update_filled_spots(spot_db,label_list)
    
    # update amount due for all cars
    amount_due(license_db)
                   
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    MainWindow.setStyleSheet("#MainWindow { border-image: url(/Users/uma/Documents/my_website/grey.jpg) 0 0 0 0 stretch stretch; }")   
    
    playlist_1 = QMediaPlaylist()
    playlist_1.addMedia(QMediaContent(QUrl.fromLocalFile("/Users/uma/Documents/my_website/output_version.mp4")))
    playlist_1.setPlaybackMode(QMediaPlaylist.Loop)
    
    playlist_2 = QMediaPlaylist()
    playlist_2.addMedia(QMediaContent(QUrl.fromLocalFile("/Users/uma/Documents/my_website/CarEntryH2.MOV")))
    playlist_2.setPlaybackMode(QMediaPlaylist.Loop)
    
    playlist_3 = QMediaPlaylist()
    playlist_3.addMedia(QMediaContent(QUrl.fromLocalFile("/Users/uma/Documents/my_website/CarExitH2.MOV")))
    playlist_3.setPlaybackMode(QMediaPlaylist.Loop)

    player_1 = QMediaPlayer(None, QMediaPlayer.VideoSurface)
    player_1.setVideoOutput(ui.vid_1)
    player_1.setPlaylist(playlist_1)
    player_1.setMuted(True)
    player_1.play()
    
    player_2 = QMediaPlayer(None, QMediaPlayer.VideoSurface)
    player_2.setVideoOutput(ui.vid_2)
    player_2.setPlaylist(playlist_2)
    player_2.setMuted(True)
    player_2.play()
    
    player_3 = QMediaPlayer(None, QMediaPlayer.VideoSurface)
    player_3.setVideoOutput(ui.vid_3)
    player_3.setPlaylist(playlist_3)
    player_3.setMuted(True)
    player_3.play()
    
    timer = QTimer()
    timer.timeout.connect(update_gui)
    timer.start(2000)
    MainWindow.show()
    
    update_gui()
    
    
    sys.exit(app.exec_())
    

            
