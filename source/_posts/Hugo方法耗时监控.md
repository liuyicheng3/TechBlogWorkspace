title: Hugo方法耗时监控
date: 2018-3-2 
categories:
- Android
tags:
- Android
- 性能监控


---

# 使用方法
1. 在Android Project的build.gradle添加dependence： 

		buildscript {
		    repositories {
		        jcenter()
		    }
		    dependencies {
		        classpath 'com.android.tools.build:gradle:2.3.3'
		        classpath 'com.jakewharton.hugo:hugo-plugin:1.2.1'//关键所在
		    }
		}

2. 在Module的build.gradle文件中添加Hugo Plugin的应用

		apply plugin:'com.jakewharton.hugo'//关键所在  

3. 在相应的方法前，添加@DebugLog

	import hugo.weaving.DebugLog;

	......

 	@DebugLog //关键所在
    private int add(int a, int b){
        return a+b;
    }


ps：调用Hugo后，Hugo自动生效。由于仅在Debug中生效，因此，可以不用关闭

# 参考文章  
使用方法:http://blog.csdn.net/daihuimaozideren/article/details/78231983  
原理分析:http://blog.csdn.net/xxxzhi/article/details/53048476  
