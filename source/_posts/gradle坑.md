title: AS 踩坑日记
date: 2015-11-01 20:10:33
categories:
- 工具
tags:
- 工具

---



升级instant run时候的报错
Error:Access to the dex task is now impossible, starting with 1.4.0
1.4.0 introduces a new Transform API allowing manipulation of the .class files.
See more information: http://tools.android.com/tech-docs/new-build-system/transform-api

解决方案：

buildscript {
    repositories {
        jcenter()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:2.0.0'

    }
}

改成1.3.0


项目根目录的gradle的
grade.property

distributionUrl=https\://services.gradle.org/distributions/gradle-2.2-all.zip
