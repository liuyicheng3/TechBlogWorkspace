title: Android模块化方案    
date: 2015-11-01 20:10:33    
categories:    
- Android    
       
       
       
tags:       
- Android    
- 模块化    
---

## AAR模块化方案  
1、首先 按照应用分层（common  view），注意每个module最好配置一下resourcePrefix "mc_"  
2、上层再按照功能模块比如  信用卡和个人中心

这样每个都会打出一个aar，府工程引入所有的aar就可以引入这个模块

## 问题
但是这个距离一个可以发布出去的aar还有距离，有以下几个问题需要解决：  
1. 本地jar依赖（主工程很有可能也公用这个jar）；  
2. 混淆的问题；  
3. 多个aar合并；   
4. 兄弟模块互相调用，基模块调用父模块的方法；


### 问题1:  
Android dependency的几种方法：
eg：  

        testCompile 'junit:junit:4.12'
    //compile fileTree(dir: 'libs', include: ['*.jar'])  
    provided fileTree(dir: 'libs',include: ['*.jar'])  
    compile 'com.android.support:support-v4:23.0.1'  
    compile project(':Module_common')   
- testCompile ：  debug 会编译  正式打包不会编译
- compile ： 除去"compile jar"会编译进arr，其余的都不会编译进去
- provided：编译时候不会把jar编译进去

传递依赖的问题
（例如 modle A 依赖 Module B，Module B 又依赖Module  C ）   jar  都放在C里面，Module A不引入jar 也能引用到jar。

但是正式打包时候不需要这些jar，本地的jar必须以provided方式引入，这样aar里面就不会打进去这些jar了。

这会引入另外一个问题：C改成provide 这些jar后，A和B找不到这些依赖的jar 会编译失败

解决方案：
把jar单独成一个module D，写成provided
（也可在module A  和 B里面  把这些jar 都拷贝进去，然后统统写成provided）

### 问题2

首先要明白，我们要去混淆的是A和主工程的接口，而A和B以及C直接的调用都需要混淆，但是不能在B和C里面混淆，因为这样一混淆的话，A与B、C调用的接口也混淆了

所以混淆只能在A里面打开，A和B都不能打开混淆

### 问题3
默认会打出三个aar，但是我们只能发布一个aar出去，所以必须使用到 https://github.com/adwiv/android-fat-aar 写的合并aar的gradle

方法：  
1、拷贝 fat-aar.gradle到build.gradle 同级目录
2、module的build.gradle新增  
apply from: 'fat-aar.gradle'  ，

compile project(':Module_common')   
改成  
embedded project(':Module_common')

这样在打B的aar时候，会把基moduel的aar合并进来


如果这个模块工程就一个工程，就只需要解决问题1，同时配置一下混淆就行

## 问题4
通过hook调用
基模块：

    public class CommonModuleDataEngine {
    
        private static CommonModuleDataEngine INSTANCE;
    
        private AppInfo appInfo;//这个必须要父模块或者兄弟模块
        public static CommonModuleDataEngine getInstance() {
            if (INSTANCE == null) {
                INSTANCE = new CommonModuleDataEngine();
            }
            return INSTANCE;
        }
    
        private CommonModuleDataEngine() {
        }
    
        public String getAppInfo() {
            return appInfo.getAppInfo();
        }
    
        public static class Builder {
            private AppInfo appInfo;
    
            public Builder setAppInfo(AppInfo appInfo) {
                this.appInfo = appInfo;
                return this;
            }
            public void build() {
                CommonModuleDataEngine engin = CommonModuleDataEngine.getInstance();
                engin.appInfo = this.appInfo;
    
            }
    
        }
        public interface AppInfo {
    
            String getAppInfo();
    
        }
    
    }


主工程  

在Application初始化的时候初始几个基类CommonModuleDataEngine，


ps：内部类的去混淆  

        -keepclasseswithmembers  class CommonModuleDataEngine {*;}
    -keepclasseswithmembers  class CommonModuleDataEngine$* {*;}




### 其它注意事项  
1、主程序和Module里面的Manifest里面的一些配置同名。必须在manifest  中的相应的配置里面 添加  

        tools:replace="android:icon,theme,label"
例如基module和主程序都包含了高德定位，manifest必然也有相同的配置信息

    <meta-data
        tools:replace="android:value"
        android:name="com.amap.api.v2.apikey"
        android:value="*******" />

App组件化与业务拆分: http://www.jianshu.com/p/60c1b9ddd8ab  
安卓组件化相关开源方案最全总结：  
https://mp.weixin.qq.com/s/SbIWWj2kYC5kF7GEoRiWww   
https://juejin.im/post/5a7ab8846fb9a0634514a2f5


