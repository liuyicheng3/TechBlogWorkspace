title: Gradle配置分析  
date: 2015-11-01 20:10:33
categories:
- android
   
   
tags:   
- 工具
- 打包

---


TopicLevel的gradle    

    buildscript {
        repositories {
            jcenter()
        }
        dependencies {
            classpath 'com.android.tools.build:gradle:2.2.2'
    
            // NOTE: Do not place your application dependencies here; they belong
            // in the individual module build.gradle files
        }
    }
    allprojects {
        repositories {
            jcenter()
        }
    }
    task clean(type: Delete) {
        delete rootProject.buildDir
    }




Mudule level的build.gradle  
    
    apply plugin: 'com.android.application'
    
    android {
        compileSdkVersion 20
        buildToolsVersion "24.0.0"
    
    
        compileOptions{
            sourceCompatibility JavaVersion.VERSION_1_8
            targetCompatibility JavaVersion.VERSION_1_8
        }
    
        defaultConfig {
            applicationId "com.lyc.study"
            minSdkVersion 15
            targetSdkVersion 20
            versionCode 1
            versionName "1.0"
            jackOptions{
                enabled true
            }
        }
        buildTypes {
            release {
                minifyEnabled false
                proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
            }
        }
    }
    
    dependencies {
        compile fileTree(include: ['*.jar'], dir: 'libs')
        compile 'com.android.support:support-v4:+'
        compile 'com.android.support:support-annotations:22.2.0'
        compile 'com.android.support:support-v13:20.1.1'
    }


以上是标准的打包方式,下面是常用的我们自定义的内容   
        
        dependencies {
            compile fileTree(include: '*.jar', dir: 'libs')
            compile project(':google_services')
    
            // compile 'com.android.support:multidex:1.0.1'
            compile 'top.zibin:Luban:1.0.9'
            debugCompile 'com.bugtags.library:bugtags-lib:latest.integration'
            
            testCompile 'junit:junit:4.12'
           
        }
        
        android {
            compileSdkVersion 21
            buildToolsVersion '23.0.2'
        
            sourceSets {
                main {
                    manifest.srcFile 'AndroidManifest.xml'
                    java.srcDirs = ['src']
                    resources.srcDirs = ['src']
                    aidl.srcDirs = ['src']
                    renderscript.srcDirs = ['src']
                    res.srcDirs = ['res']
                    assets.srcDirs = ['assets']
                    jniLibs.srcDirs = ['libs']
                }
        
                test.setRoot('test')
              
                debug.setRoot('build-types/debug')
                release.setRoot('build-types/release')
            }
        
            signingConfigs {
                debug {
                    // 请配置好pub.key及其密码，或者改为使用debug.keystore
                    storeFile file('pub.key') // storeFile file('debug.keystore')
                    storePassword STORE_PASSWORD
                    keyAlias KEY_ALIAS
                    keyPassword KEY_PASSWORD
                }
                release {
                    storeFile file('pub.key')
                    storePassword STORE_PASSWORD
                    keyAlias KEY_ALIAS
                    keyPassword KEY_PASSWORD
                }
            }
        
            buildTypes {
                debug {
                    buildConfigField "String", "RELEASE_TIME", "\"Not yet\""
                    buildConfigField "boolean", "DEVELOP_MODE", "true"
                    signingConfig signingConfigs.debug
        
                    ndk{
                        abiFilters 'armeabi', 'armeabi-v7a', 'x86' //,'arm64-v8a', 'x86_64', 'mips', 'mips64'
                    }
                }
                release {
                    buildConfigField "String", "RELEASE_TIME", "\"2017/1/1\"" //  发布时修改为当天日期
                    buildConfigField "boolean", "DEVELOP_MODE", "false" // 关闭开发者模式
                    proguardFiles 'proguard.cfg'
                    minifyEnabled true
                    shrinkResources true
                    debuggable false
                    jniDebuggable false
                    signingConfig signingConfigs.release
        
                    applicationVariants.all { variant ->
                        variant.outputs.each { output ->
                            def outputFile = output.outputFile
                            if (outputFile != null && outputFile.name.endsWith('.apk')) {
                                // APK命名格式 Going-release.apk TODO 发布时使用
                                def fileName = "Going-v${defaultConfig.versionName}-${defaultConfig.versionCode}-release.apk"
        //                         def fileName = "Going.apk"
                                output.outputFile = new File(outputFile.parent, fileName)
                            }
                        }
                    }
                }
            }
        
            defaultConfig {
                minSdkVersion 14
                targetSdkVersion 22  // 请勿随意改动 //Android 6.0系统默认为targetSdkVersion小于23的应用默认授予了所申请的所有权限
                versionCode 1000
                versionName "1.0.0"
                //manifestPlaceholders = [ UMENG_CHANNEL_VALUE:"googleMarket" ]
                multiDexEnabled false
                multiDexKeepProguard file('multiDexKeep.pro')
                resConfigs "en", "zh_CN", "zh_TW" //暂时限定语言, 当前情况下缩小大概 0.2M TODO googlePlay 版本取消限制
            }
        
            productFlavors {
                  own {}
                  googleMarket {}
  
                  tencent {}
                  baidu {}
        
       
            }
        
        //    productFlavors.all { flavor ->
        //        flavor.manifestPlaceholders = [ UMENG_CHANNEL_VALUE:name ]
        //    }
        
            packagingOptions {
                exclude 'META-INF/LICENSE.txt'
            }
        
            // 可以适当的打开Lint，检查是否存在隐藏问题
            lintOptions {
                checkReleaseBuilds false
                abortOnError false
            }
        
            android.dexOptions {
                jumboMode = true
                javaMaxHeapSize "2g"
                maxProcessCount 8
            }
        
        }
        
        // 替换编码方式，否则编译可能有中文乱码
        tasks.withType(org.gradle.api.tasks.compile.JavaCompile) {
            options.encoding = "UTF-8"
        }




相对于标准的我们在 android Task中新增了sourceSets这个Task制定了一些文件夹的目录，如果工程目录是标注的就不需要设置了


在build.gradle同级新建一个gradle.properties
里面可以用来存放build.gradle里面的一些参数
STORE_PASSWORD=nico
KEY_ALIAS=nick
KEY_PASSWORD=nico


这个地方对应的脚本是signingConfigs》debug里面的参数 


 buildTypes 》debug 中的buildConfigField参数则会在编译时候  
 
 ![gradle01](https://github.com/liuyicheng3/learning-summary/blob/master/images/gradle%E5%88%86%E6%9E%9001.png?raw=true)
 
                buildConfigField "String", "RELEASE_TIME", "\"Not yet\""
                buildConfigField "boolean", "DEVELOP_MODE", "true"

会在编译时候生成并存放在build/generated/source/buildConfig/...BuildConfig.java   



            public final class BuildConfig {
              public static final boolean DEBUG = Boolean.parseBoolean("true");
              public static final String APPLICATION_ID = "com.lyc.study";
              public static final String BUILD_TYPE = "debug";
              public static final String FLAVOR = "own";
              public static final int VERSION_CODE = 100;
              public static final String VERSION_NAME = "1.0.0";
              // Fields from build type: debug
              public static final boolean DEVELOP_MODE = true;
              public static final String RELEASE_TIME = "Not yet";
            }


可以参考友盟的多渠道打包（github）


一个介绍gradle比较好的网站   
http://stormzhang.com/posts/


https://segmentfault.com/a/1190000006915937

这两个网站都是一系列的教程，建议一个一个的看
