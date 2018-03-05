title: 生成分享图片    
date: 2018-1-3     
categories:    
- Python    
   
tags   
- Python    
- xml    
    
---

# 常用模块 
bs4  xml.dom.minidom  xml.etree   re

# 1. bs4用法    
详细使用文档 https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html    
http://www.cnblogs.com/twinsclover/archive/2012/04/26/2471704.html  

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(content, 'xml')  
    itemList= soup.select('html > body > div[class="area"] > ul.plist2.cf.ulList > li > a')  
    itemList2= soup.select('div[id="newsList"] > ul[id="v2"] > li[class="item"] > a ')   

判断书是否有属性的方法 tem.contents[0].attrs.has_key

    for item in itemList:
       if item.contents[0].attrs.has_key('src'):
           avatar = item.contents[0]['src']
       elif item.contents[0].attrs.has_key('lz_src'):
           avatar = item.contents[0]['lz_src']
       else:
           avatar='unset'
           print item
       star = StarItem(item.text,avatar)
       currentPageStars.append(star)  

判断是否有子元素的方法 newsItemDiv.p   
获取元素标签里面值的方法newsItemDiv.p.string

    for index,newsItemDiv in enumerate(itemList):
       tranItem = NewsItem(newsItemDiv.p.string if newsItemDiv.p else "",newsItemDiv.img['data-src'] if newsItemDiv.img else "",proto+"/"+domain+newsItemDiv['href'])
       newsItems.append(str(tranItem)+",\n")


ps:ul.plist2.cf.ulList 达标这个ul 使用了多种样式 plist2  cf  ulList     

# 2. minidom

## 使用minidom解析器打开 XML 文档

    DOMTree = xml.dom.minidom.parse(xmlPath)
    collection = DOMTree.documentElement

## 在集合中获取所有colors

    colors = collection.getElementsByTagName("color")

    namelist = []
    valuelist = []

# 打印每部电影的详细信息
    for color in colors:
        if color.hasAttribute("name"):
            colorname=color.getAttribute("name")
            colorvalue = color.childNodes[0].data
            if not (colorname in namelist):
                namelist.append(colorname)
                currentIndex = namelist.index(colorname) 



# 3. etree   

    import xml.etree.ElementTree
    tree = ElementTree.parse(lastYearPath )
    allItems = tree.findall('data/item')
    for pos,treeItem in enumerate(allItems):
        holidayYear = int(treeItem.attrib['year'])
        holidayMonth = int(treeItem.attrib['month'])
        holidayDate = int(treeItem.attrib['date'])


# 4. 正则  
 对于xml里面的注释很难读取出来建议使用

    import re  
    names = re.findall(r"<!\[CDATA\[(.*?)\]\]",data)










 

