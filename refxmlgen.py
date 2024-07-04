import os
from emoticon_module import IndexableDict
import lxml.etree as ET
import re
from imageprocess import *


path = 'C:/Kostat Messenger 2.0/Skins/Html/images/emoticon/'
try:
    xml_reference = ET.parse(path + 'reference.xml')
except:
    print("reference.xml이 없습니다. 재설치 후 다시 시도하세요.")
    raise
data = xml_reference.getroot()

os.chdir(input('위치 설정: '))
print('설정된 디렉토리: '+os.getcwd())
d = input('이용할 디렉토리 입력. 미입력시 하위 디렉토리 전체를 대상으로 작업합니다.\n').replace('\\', '/')
if d == '':
    folders = [folder.replace('\\', '/') for folder in os.listdir() if os.path.isdir(folder)]
    try:
        folders.remove('__pycache__')
    except ValueError:
        pass
else:
    folders = [d.replace('\\', '/')]
auto = input('자동모드 설정(y/N):')
if (auto=='y') | (auto=='Y'):
    auto = True
else:
    auto = False


# source는 상대경로 또는 절대경로
for source in folders:
    filelist = sorted(os.listdir(source), key=lambda x: (len(x), x))
    print(source)
    if auto:
        TabControlName = TabName_ENG = [i.split(' ')[0] for i in filelist[:3]][2]
        TabName = source.split('/')[-2:]
        if '' in TabName:
            TabName.remove('')
        TabName = TabName[0]
    else:
        TabControlName = input('폴더명(컨트롤명) 입력:')
        TabName = input('탭이름(한글) 입력:')
        TabName_ENG = input('탭이름(영문, 띄어쓰기 없이) 입력:').replace(' ', '')
    imageprocess(source+'/', TabControlName, TabName_ENG)
    Img_Def = 'tab_'+TabName_ENG+'_main.bmp'
    Img_Down = 'tab_'+TabName_ENG+'_select.bmp'

    newtab =  "\t<EmoticonTabitem TabControlNM=\""+TabControlName+"\">\n"
    newtab_tag = "\t\t<tag>1</tag>\n"
    newtab_tabname = "\t\t<TabName>"+TabName+"</TabName>\n"
    newtab_tabname_eng = "\t\t<TabName_ENG>"+TabName_ENG+"</TabName_ENG>\n"
    newtab_imgdef = "\t\t<Img_Def>"+Img_Def+"</Img_Def>\n"
    newtab_imgdown = "\t\t<Img_Down>"+Img_Down+"</Img_Down>\n\t</EmoticonTabitem>\n\n"
    data.append(ET.fromstring(newtab+newtab_tag+newtab_tabname+newtab_tabname_eng+newtab_imgdef+newtab_imgdown))

    imglist = [i for i in filelist if i[-4:]=='.png'] #img리스트
    try:
        imglist.remove('icon.png')
    except ValueError:
        pass

    for i in range(len(imglist)):
        newitem = '\t<EmoticonItem EmoticonType=\"sticker\">\n'
        newitem_tabname = '\t\t<TabName>'+TabControlName+'</TabName>\n'
        newitem_name= "\t\t<Name>"+imglist[i]+"</Name>\n"
        newitem_listname= "\t\t<ListName>"+imglist[i]+"</ListName>\n"
        newitem_kor= "\t\t<Kor><![CDATA[("+TabName+" "+str(i+1)+")]]></Kor>\n"
        newitem_eng= "\t\t<Eng><![CDATA[("+TabName_ENG+" "+str(i+1)+")]]></Eng>\n"
        newitem_hint= "\t\t<Hint><![CDATA["+TabName+" "+str(i+1)+"]]></Hint>\n\t</EmoticonItem>\n\n"
        data.append(ET.fromstring(newitem+newitem_tabname+newitem_name+newitem_listname+newitem_kor+newitem_eng+newitem_hint))

    try:
        with open(path+'reference_new.xml', 'wb+') as file:
            ET.ElementTree(data).write(file, pretty_print=True,encoding='utf-8', xml_declaration=True)
        # tree = ET.ElementTree(data)
        # tree.write('C:/Kostat Messenger 2.0/Skins/Html/images/emoticon/test.xml', encoding='utf-8', xml_declaration=True, cdata=True)
        print('reference 추가완료')
    except:
        print('오류')
        raise