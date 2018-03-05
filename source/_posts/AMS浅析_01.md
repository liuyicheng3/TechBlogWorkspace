title: AMS client端分析
date: 2017-8-1 
categories:
- Android
   
   
tags:   
- Android
- AMS

---

# Activity启动理解
PS：  
一定要下载官方对应版本SDK，然后应用的SDK版本也要对应  
建议配合GrepCode 查找类的位置，

# 1. Android的CS模式

Android启动是通过AtivityThread的main函数启动的，
四大组件的生命周期都是通过AMS远程控制的，比如我们启动一个Acitivity,Service等都不是直接启动的，都是binder告诉AMS我们要启动四大组件，然后AMS通过binder处理（比如Activity A要启动Activity B，但是中途涉及到A的onpause  onStop和B 的oncreate，都是AMS依据ActivityRecord进行处理的）

# 2. 三个核心部分
## client端：
ActivityThread  
ActivityMangerNative   和ActivityManagerProxy  
ApplicationThread和ApplicationThreadNative  

其实还涉及到：其它的比如 Instrumentation但是这个不是核心类

## Server端

ApplicationThreadProxy  
ActivityMangerService  
ProcessRecord  
ActivityStack  
ActivityRecord  

## 跨进程通讯Binder
Binder 和 Parcel

# 3. Activity A 启动Activity B的流程详解  

ps：  
ActivityMangerNative是往AMS发送消息的  
ApplicationThread是从AMS接受指令消息的



## 1、Client发送Intent
Activity#startActivity(Intent) >> Instrumentation#execStartActivity()  >>  
ActivityManagerNative#startActivity() >>

## 2、AMS 查询栈，告诉要Pause
ActivityMangerNative#onTransact() >>    

ActivityMangerNative#schedulePauseActivity()这里是抽象的具体实现在
ActivityThread$ApplicationThread#schedulePauseActivity() >>   

ActivityThread#sendMessage() 也就是通过H mH 发送Message>>  
ActivityThread$H#handleMessage()>>    
ActivityThread#handlePauseActivity这里先要取出当前Activity ActivityClientRecord r = mActivities.get(token) >>
ActivityThread#performPauseActivity()>>    

Instrumentation#callActivityOnPause >>

 ActivityManagerNative#activityPaused(token) 这个是在上一步Instrumentation pause完Activity后顺序执行的
 这里也就是通过binder发送消息>>  
 
 
 
 PS:Activity切换要不要调用onstop 要看Theme，如果是android:style/Theme.Translucent就不会调用Onstop。所以我是不讲stop这个流程（实际上鄙人是有点懒。。。）
 ## 3、AMS正式启动 Activity B    
 ActivityMangerNative#onTransact() >>    

ActivityMangerNative#scheduleLaunchActivity()这里是抽象的具体实现在
ActivityThread$ApplicationThread#scheduleLaunchActivity() >>  

经过H mH转到主线程里面
ActivityThread#handleLaunchActivity>> 

ActivityThread#performLaunchActivity
初始化Activity包括以下几步  
1. 生成Activity B ，这里仅仅是生成简单的java类 
 
       java.lang.ClassLoader cl = r.packageInfo.getClassLoader();
                activity = mInstrumentation.newActivity(
                        cl, component.getClassName(), r.intent);  

2. 附加给Activity 各种Android系统类型
 
        attach(Context context, ActivityThread aThread,
            Instrumentation instr, IBinder token, int ident,
            Application application, Intent intent, ActivityInfo info,
            CharSequence title, Activity parent, String id,
            NonConfigurationInstances lastNonConfigurationInstances,
            Configuration config, String referrer, IVoiceInteractor voiceInteractor) 

3. 回调oncreate  注意这个地方不会通知AMS
  
        mInstrumentation.callActivityOnCreate(activity, r.state);  

最终这个会调用到Activity的oncreate



ps：ActivityThread.H 的Message可以看看，就可以知道有哪些操作需要和AMS打交道 



>> 

ActivityThread#handleResumeActivity  
这里会依次调用

1. ActivityThread#performResumeActivity(token, clearHide)   
2. ActivityManagerNative#willActivityBeVisible（）  
告诉AMS Activity已经准备好了   
3. ActivityManagerNative#activityResumed（）  
告诉AMS Activity已经resumed


在2、3步骤里面就是做Activity B的界面绘制工作:
        
        r.window = r.activity.getWindow();
        View decor = r.window.getDecorView();
        decor.setVisibility(View.INVISIBLE);
        ViewManager wm = a.getWindowManager();
        a.mDecor = decor;
        l.type = WindowManager.LayoutParams.TYPE_BASE_APPLICATION;
        l.softInputMode |= forwardBit;
        if (a.mVisibleFromClient) {
            a.mWindowAdded = true;
            wm.addView(decor, l);
            }
            
            
具体流程参考ActivityThread#handleResumeActivity()流程

涉及到window，DecroView等
        




## AMS 通知显示Acitivity B已经Onresume，  
然后就是和onpause一样的流程并且回调Activity的onResume




 
 
 











# 4. 哪些是公用的，为hook做准备








