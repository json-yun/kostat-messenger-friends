from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import requests
import xml.etree.ElementTree as ET
import os
from PIL import Image             
import numpy as np

# pip install selenium==4.21.0 requests==2.32.3 numpy==2.0.0 pillow==10.3.0

def main() -> None:
    def tab_icon(im, filter=Image.BICUBIC) -> Image:
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
        mask = np.all(arr[:, :, 0:3] == [0,0,0], axis = 2)
        for i, j in zip(*np.where(mask)):
            arr[i, j] = [1, 1, 1, arr[i, j, 3]]
        return Image.fromarray(arr)
    
    def get_imgs_from_link(url: str) -> list[str]:
        # 웹 페이지 열기
        driver.get(url)
        # 페이지 로드 대기
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        actions = driver.find_element(By.CSS_SELECTOR, "body")
        actions.send_keys(Keys.PAGE_DOWN)
        actions.send_keys(Keys.PAGE_DOWN)
        actions.send_keys(Keys.PAGE_DOWN)
        actions.send_keys(Keys.END)
        # #list_emoticon 클래스를 가진 div 태그 찾기
        emoticon_urls = driver.find_elements(By.CSS_SELECTOR, "ul.list_emoticon > li > a.link_emoticon > img")
        kor_name = driver.title
        # kor_name = driver.find_element(By.CSS_SELECTOR, "div.info_product > h3.tit_product > span.tit_inner").text
        eng_name = url.split("e.kakao.com/t/")[1].split("/")[0].split("#")[0].split("&")[0].split("?")[0]

        result = []
        # 찾은 div 태그 내용 출력
        for i, emoticon in enumerate(emoticon_urls):
            img = emoticon.get_attribute("src")
            result.append(img)
        
        return [eng_name, kor_name], result

    path_reference = input("reference파일의 경로를 지정(기본값 reference.xml): ")
    if path_reference == "":
        path_reference = "reference.xml"
    try:
        data = ET.parse(path_reference).getroot()
    except:
        print("reference를 읽는 중 오류가 발생했습니다.")
        raise

    urls = []
    url = "_"
    print("\n작업할 url을 정확한 형식으로 입력하세요. 형식=https://e.kakao.com/t/xxxxxxxxx")
    while True:
        url = input(f"{len(urls)+1}: ")
        if url=="":
            break
        urls.append(url)
    
    length = len(urls)
    # 크롬 드라이버 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저 창을 보이지 않게 설정

    # 크롬 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options)

    list_img_urls = []
    # url 반복문
    for i, url in enumerate(urls, 1):
        print(f">> 이미지를 모으는 중.. {i}/{length}")
        names, img_urls = get_imgs_from_link(url)
        list_img_urls.append([names, img_urls])
    # 브라우저 종료
    driver.quit()
    
    list_imgs = []
    for i, [names, img_urls] in enumerate(list_img_urls, 1):
        print(f">> 이미지를 다운로드 중.. {i}/{length}")
        try:
            os.mkdir(names[0])
        except FileExistsError:
            yn = input(f"{names[0]}폴더가 이미 존재합니다. 계속하시겠습니까? (Y/n)..")
            if yn != "Y" and yn != "y":
                return
        imgs = []
        for j, img_url in enumerate(img_urls, 1):
            # 이미지 다운로드
            response = requests.get(img_url)
            # 이미지 데이터 저장
            img = f"{names[0]} ({j}).png"
            imgs.append(img)
            with open(f"{names[0]}/{img}", "wb") as file:
                file.write(response.content)
        list_imgs.append(imgs)

    try:
        os.mkdir("Tab")
    except FileExistsError:
        pass
    for i, [names, _] in enumerate(list_img_urls, 1):
        print(f">> 이미지를 처리 중.. {i}/{length}")
        sourcepath = names[0]+"/"
        filelist = os.listdir(sourcepath)
        if 'nearest' in filelist:
            filter = Image.NEAREST
            size = (105, 105)
        else:
            filter = Image.BICUBIC
            size = (100, 100)
        
        # tab_icon 작업
        tab_select, tab_main = tab_icon(Image.open(sourcepath+filelist[0]))
        
        tab_select.save('Tab/tab_'+names[0]+'_select.bmp')
        tab_main.save('Tab/tab_'+names[0]+'_main.bmp')

        for img in filelist:
            im = Image.open(sourcepath + img)
            im_resized = resize100(im, size, filter)
            im_resized = replace_black(im_resized)
            im_resized.save(sourcepath + img)
            
    for i, [names, _] in enumerate(list_img_urls, 1):
        print(f">> reference에 추가 중.. {i}/{length}")
        sourcepath = names[0]+"/"
        filelist = os.listdir(sourcepath)

        Img_Def = 'tab_'+names[0]+'_main.bmp'
        Img_Down = 'tab_'+names[0]+'_select.bmp'

        newtab =  "\t<EmoticonTabitem TabControlNM=\""+names[0]+"\">\n"
        newtab_tag = "\t\t<tag>1</tag>\n"
        newtab_tabname = "\t\t<TabName><![CDATA["+names[1]+"]]></TabName>\n"
        newtab_tabname_eng = "\t\t<TabName_ENG>"+names[0]+"</TabName_ENG>\n"
        newtab_imgdef = "\t\t<Img_Def>"+Img_Def+"</Img_Def>\n"
        newtab_imgdown = "\t\t<Img_Down>"+Img_Down+"</Img_Down>\n\t</EmoticonTabitem>\n\n"
        data.append(ET.fromstring(newtab+newtab_tag+newtab_tabname+newtab_tabname_eng+newtab_imgdef+newtab_imgdown))

        for i, img_name in enumerate(filelist, 1):
            newitem = '\t<EmoticonItem EmoticonType=\"sticker\">\n'
            newitem_tabname = '\t\t<TabName>'+names[0]+'</TabName>\n'
            newitem_name= "\t\t<Name>"+img_name+"</Name>\n"
            newitem_listname= "\t\t<ListName>"+img_name+"</ListName>\n"
            newitem_kor= "\t\t<Kor><![CDATA[("+names[1]+" "+str(i)+")]]></Kor>\n"
            newitem_eng= "\t\t<Eng><![CDATA[("+names[0]+" "+str(i)+")]]></Eng>\n"
            newitem_hint= "\t\t<Hint><![CDATA["+names[0]+" "+str(i)+"]]></Hint>\n\t</EmoticonItem>\n\n"
            data.append(ET.fromstring(newitem+newitem_tabname+newitem_name+newitem_listname+newitem_kor+newitem_eng+newitem_hint))

    try:
        with open(path_reference, 'wb+') as file:
            ET.indent(data, space="\t", level=0)
            ET.ElementTree(data).write(file, encoding='utf-8', xml_declaration=True)
        print('reference 추가완료')
    except:
        print('reference를 저장하지 못했습니다.')
        raise

if __name__ == "__main__":
    main()
