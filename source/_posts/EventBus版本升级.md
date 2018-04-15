title: EventBus3.0    
date: 2018-2-10     
categories:    
- Android    
       
       
       
tags:       
- Android    
- eventbus3.0    
- 注解    
- APT    
    
    
---

# EventBus3.0 优点：

EventBus 3由于使用了注解，比起使用反射来遍历方法的2.4版本逊色不少。但开挂之后(启用了索引)远远超出之前的版本。

![性能对比](http://i.imgur.com/5evKXOx.png)

参考资料：https://www.cnblogs.com/bugly/p/5475034.html


## 开挂方法：  
1. 在当前moudle的gradle 添加    

			apply plugin: 'com.neenbedankt.android-apt'   

2. 在dependencies里面添加   

		dependencies 
		compile 'org.greenrobot:eventbus:3.0.0'
		apt 'org.greenrobot:eventbus-annotation-processor:3.0.1'   


3. 在使用时候   

		@Subscribe
		public void helloEventBus(UserReLoginEvent  event){
		    // TODO: 17/6/27  这是是为了测试而使用的
		    UtilsManager.toast(mContext,"这是eventbus 3.0 可以支持的");
		}



## 事件源定位：  
为了防止事件环路对EventBus加一个Wrapper，每次发送Event时候打印一下路径   

	 	private static void printWrapPath(String tagStr, Object... objects) {

	        StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
	        final StackTraceElement ste = stackTrace[5];

	        StringBuilder stringBuilder = new StringBuilder();
	        String className = ste.getFileName();
	        if (!TextUtils.isEmpty(className)) {
	            String methodName = ste.getMethodName();
	            int lineNumber = ste.getLineNumber();
	            stringBuilder.append("(").append(className).append(":").append(lineNumber).append(") #").append(methodName).append(" : ");
	        } else {
	            stringBuilder.append(" ");
	        }

	        String tag = (tagStr == null ? LOG_DEFAULT_TAG : tagStr);
	        String msg = (objects == null) ? "null" : getObjectsString(objects);
	        String headString = stringBuilder.toString();

	 		Log.println(type, tagStr, headString + msg);

	 	}


## 混淆问题  ：  

混淆作为版本发布必备的流程，经常会闹出很多奇奇怪怪的问题，且不方便定位，尤其是EventBus这种依赖反射技术的库。通常情况下都会把相关的类和回调方法都keep住，但这样其实会留下被人反编译后破解的后顾之忧，所以我们的目标是keep最少的代码。

首先，因为EventBus 3弃用了反射的方式去寻找回调方法，改用注解的方式。作者的意思是在混淆时就不用再keep住相应的类和方法。但是我们在运行时，却会报java.lang.NoSuchFieldError: No static field POSTING。网上给出的解决办法是keep住所有eventbus相关的代码：

		-keep class de.greenrobot.** {*;}  


其实我们仔细分析，可以看到是因为在SubscriberMethodFinder的findUsingReflection方法中，在调用Method.getAnnotation()时获取ThreadMode这个enum失败了，所以我们只需要keep住这个enum就可以了（如下）。

		-keep public enum org.greenrobot.eventbus.ThreadMode { public static *; }   


这样就能正常编译通过了，但如果使用了索引加速，是不会有上面这个问题的。因为在找方法时，调用的不是findUsingReflection，而是findUsingInfo。但是使用了索引加速后，编译后却会报新的错误：Could not find subscriber method in XXX Class. Maybe a missing ProGuard rule?

这就很好理解了，因为生成索引GeneratedSubscriberIndex是在代码混淆之前进行的，混淆之后类名和方法名都不一样了（上面这个错误是方法无法找到），得keep住所有被Subscribe注解标注的方法：

	-keepclassmembers class * {
	    @de.greenrobot.event.Subscribe <methods>;
	}


所以又倒退回了EventBus2.4时不能混淆onEvent开头的方法一样的处境了。所以这里就得权衡一下利弊：使用了注解不用索引加速，则只需要keep住EventBus相关的代码，现有的代码可以正常的进行混淆。而使用了索引加速的话，则需要keep住相关的方法和类。   

生成的索引的 gradle配置:  

			apt {
			    arguments {
			        eventBusIndex "com.example.myapp.MyEventBusIndex"
			    }
			}   

生成的索引demo：  

	 putIndex(new SimpleSubscriberInfo(com.lyc.MainActivity.class, true, new SubscriberMethodInfo[] {
	            new SubscriberMethodInfo("helloEventBus", com.lyc.eventbus.UserReLoginEvent.class),
	        }));


## Android APT
  参考资料：https://segmentfault.com/a/1190000005100468

