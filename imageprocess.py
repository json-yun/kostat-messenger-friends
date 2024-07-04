from PIL import Image
from matplotlib import pyplot as plt
import numpy as np
import os

def tab_icon(im, filter=Image.BICUBIC):
    # generate background image
    background_main = np.zeros((42,40,4)).astype(np.uint8)
    background_main[:,:,3] = 255
    background_main[:,:,:3] = 239
    background_select = background_main.copy()
    background_select[:,:,:3] = 208
    background_select[0,:,:3] = 215
    background_select[41,:,:3] = 215
    background_select[:,0,:3] = 215
    background_select[:,39,:3] = 215

    background_select = Image.fromarray(background_select)
    background_main = Image.fromarray(background_main)

    # resize foreground image
    foreground = im.resize((40,40), filter)
    foreground = np.array(foreground)
    new_row = [[0, 0, 0, 0]]
    foreground = np.insert(foreground, 40, new_row, axis = 0)
    foreground = np.insert(foreground, 0, new_row, axis = 0)
    foreground_gray = foreground.copy()
    foreground_gray[:,:,0] = foreground_gray[:,:,0] * 0.299 + foreground_gray[:,:,1] * 0.587 + foreground_gray[:,:,2] * 0.114
    foreground_gray[:,:,1] = foreground_gray[:,:,0]
    foreground_gray[:,:,2] = foreground_gray[:,:,0]

    foreground = Image.fromarray(foreground)
    foreground_gray = Image.fromarray(foreground_gray)
    combined = Image.alpha_composite(background_select.convert('RGBA'), foreground.convert('RGBA'))
    combined_gray = Image.alpha_composite(background_main.convert('RGBA'), foreground_gray.convert('RGBA'))
    return combined, combined_gray

def resize100(im, size = (100, 100), filter=Image.BICUBIC):
    return im.resize(size, filter)

def replace_black(im):
    arr = np.array(im.convert('RGBA'))
    mask = np.all(arr == [0,0,0,255], axis = 2)
    arr[mask] = [1,1,1,255]
    return Image.fromarray(arr)

def imageprocess(sourcepath, TabControlName, TabName_ENG):
    path = 'C:/Kostat Messenger 2.0/Skins/Html/images/emoticon/'
    targetpath = path+TabControlName+'/'
    os.makedirs(targetpath, exist_ok = True)
    
    filelist = os.listdir(sourcepath)
    if 'nearest' in filelist:
        filter = Image.NEAREST
        size = (105, 105)
    else:
        filter = Image.BICUBIC
        size = (100, 100)
        
        
    imglist = []
    for file in filelist:
        if (file[-4:] == '.png') | (file[-4:] == '.bmp') | (file[-4:] == '.jpg'):
            imglist.append(file)
    
    if 'icon.png' in imglist:
        print('working: icon.png')
        im = Image.open(sourcepath + 'icon.png')
        select, main = tab_icon(im)
    
        select.save(path + 'Tab/tab_'+TabName_ENG+'_select.bmp')
        main.save(path + 'Tab/tab_'+TabName_ENG+'_main.bmp')
    
        imglist.remove('icon.png')
    else:
        print('working: icon.png')
        im = Image.open(sourcepath + imglist[0])
        select, main = tab_icon(im)
    
        select.save(path + 'Tab/tab_'+TabName_ENG+'_select.bmp')
        main.save(path + 'Tab/tab_'+TabName_ENG+'_main.bmp')
        
    for img in imglist:
        print('working: '+ img)
        im = Image.open(sourcepath + img)
        im_resized = resize100(im, size, filter)
        im_resized = replace_black(im_resized)
        im_resized.save(targetpath + img)
    print('image process: complete')

if __name__ == '__main__':
    folder = input('작업폴더 상대경로 입력:')
    TabControlName = input('저장폴더명 입력:')
    TabName_ENG = input('탭이름(영문) 입력:')
    imageprocess(folder, TabControlName, TabName_ENG)