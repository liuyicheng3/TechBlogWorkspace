title: AS工程导入
date: 2015-11-01 20:10:33
categories:
- Android
   
   
tags:   
- Android
---

# 1.工程导入
## 1.1 普通eclipse  工程导入
直接import，AS会提示转成eclipse工程
## 1.2 github上的工程导入  
用AS打开top level的settings.gradle选择进行配置导入   
ps：如果这一步直接导入的话就会报   Could not find method android() for arguments   

可能遇到的问题：  

1. 配置sdk位置（顶层build.gradle同级）
local.properties（建议从已有工程拷贝一个）  
sdk.dir=/Users/lyc/codeTools/android-sdk  

2. 配置模块的build.gradle的gradletoolVersion版本
buildToolsVersion '23.0.2'

建议从已有工程的里面找一个可用的版本填上去

查看自己已经有哪些版本的buildTools的方法，

![see](https://github.com/liuyicheng3/learning-summary/blob/master/images/AS%E5%AF%BC%E5%85%A5%E5%B7%A5%E7%A8%8B01.png?raw=true)  

3. modle配置模块的工程compileSdkVersionversion
为一个已有版本的

 


4. 配置
dependencies中的com.android.support的版本，要求是于compileSdkVersionversion的版本一直
，但是这个不好处理

compile 'com.android.support:design:25.1.1'
compile 'com.android.support:appcompat-v7:25.1.1'
compile 'com.android.support:cardview-v7:25.1.1'

英文有子序列号
建议按照以下方法写
compile 'com.android.support:cardview-v7:25.+'
这样就会取本版本号下面最大的一个

![see](https://github.com/liuyicheng3/learning-summary/blob/master/images/AS%E5%AF%BC%E5%85%A5%E5%B7%A5%E7%A8%8B02.png?raw=true)   

5.配置本地Gradel版本  
这个常见于直接从别人那里拷贝的工程（也就是带有gradle/wrapper/**）的工程

    distributionBase=GRADLE_USER_HOME
    distributionPath=wrapper/dists
    zipStoreBase=GRADLE_USER_HOME
    zipStorePath=wrapper/dists
    distributionUrl=https\://services.gradle.org/distributions/gradle-2.10-all.zip 
gradle会去找这个版本的gradle，如果找不到就会重新下载  
gradle的默认下载目录在用户目录的.gradle/wrapper/dists文件夹中（隐藏的）  里面会有所有已经下载的gradle 版本，可以把它改成一个已经有的版本就行

## 1.3 本地工程导入  
直接import




