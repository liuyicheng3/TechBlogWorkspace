title: Android分包
date: 2015-11-01 20:10:33
categories:
- Android
   
tags   
- Android
- 打包
---

## 第一步：  gradle引入以及配置

        compile 'com.android.support:multidex:1.0.1'

        defaultConfig {
            minSdkVersion 14
            targetSdkVersion 22  // 请勿随意改动 //Android 6.0系统默认为targetSdkVersion小于23的应用默认授予了所申请的所有权限
            versionCode 5210
            versionName "5.2.1"
            //manifestPlaceholders = [ UMENG_CHANNEL_VALUE:"googleMarket" ]
            multiDexEnabled true
            multiDexKeepProguard file('multiDexKeep.pro')
            // resConfigs "en", "zh_CN", "zh_TW" 暂时限定语言, 当前情况下缩小大概 0.2M TODO googlePlay 版本取消限制
        }

## 第二步：修改Application  

        @Override
        protected void attachBaseContext(Context base) {
            super.attachBaseContext(base);
            MultiDex.install(base);
        }

## 第三步：保证关键类在主dex中 

 就是通过multiDexKeep.pro文件控制的  
 个推 sdk强制在主dex 中

        -dontwarn com.igexin.**
        -keep class com.igexin.**{*;}
