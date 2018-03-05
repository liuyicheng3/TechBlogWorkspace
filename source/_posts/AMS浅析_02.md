title: AMS server端分析
date: 2017-8-3 
categories:
- Android
   
   
   
tags:   
- Android
- AMS

---



# Ams  server端

## 核心类：  
ActivityManagerNative是从Client接受binder 消息  
ApplicationThreadNative 是从AMS向Client发送指令  
ActivityStackSupervisor
ActivityStack就是存储ActivityRecord的容器，主要操作都是通过ActivityStackSupervisor来做的

ps:注意接IApplicationThread   

    A. ApplicationThreadNative实现了一部分，ActivityMangerService继承ApplicationThreadNative,然后实现了剩余的    
    B. ApplicationThreadNative.ApplicationThreadProxy完全实现了IApplicationThread
## Activity A启动Activity B流程  

## 1. Activity A启动Activity B流程  

ActivityManagerNative#onTransact（）>>   
ActivityManagerService#startActivity()>>    
ActivityManagerService#startActivityAsUser()>>   
ActivityStackSupervisor#startActivityMayWait()>>   
ActivityStack#resumeTopActivityLocked（）>>  
ActivityStack#startPausingLocked（）>>  
pause上一个Activity的调用方法

     prev.app.thread.schedulePauseActivity(prev.appToken, prev.finishing,  userLeaving, prev.configChangeFlags);

ActivityMangerNative.ApplicationThreadProxy.schedulePauseActivity  >>  
）

等client pause完了后
ActivityManagerNative#activityPaused（）  
这里实际调用的是ActivityManagerService的activityPaused（）>>  
ActivityStack#completePauseLocked() >>  
ActivityStack#resumeTopActivityLocked（）>>  
ActivityStackSupervisor#resumeTopActivitiesLocked(topStack, prev, null);  

这时候有两部分，如果当前应用还没有启动就通过Process  

        if (app != null && app.thread != null) {
            try {
                app.addPackage(r.info.packageName, mService.mProcessStats);
                realStartActivityLocked(r, app, andResume, checkConfig);
                return;
            } catch (RemoteException e) {
                Slog.w(TAG, "Exception when starting activity "
                        + r.intent.getComponent().flattenToShortString(), e);
            }

            // If a dead object exception was thrown -- fall through to
            // restart the application.
        }

        mService.startProcessLocked(r.processName, r.info.applicationInfo, true, 0,
                "activity", r.intent.getComponent(), false, false, true);
    }

### 1.1 在已有进程中启动

ActivityStackSupervisor#realStartActivityLocked（）>>  
   
        app.thread.scheduleLaunchActivity(new Intent(r.intent), r.appToken,
        System.identityHashCode(r), r.info,
        new Configuration(mService.mConfiguration), r.compat,
        app.repProcState, r.icicle, results, newIntents, !andResume,
        mService.isNextTransitionForward(), profileFile, profileFd,profileAutoStop;  
        
ActivityMangerNative.ApplicationThreadProxy.scheduleLaunchActivity  >>  



### 1.2 App进程不存在，需要新建  
ActivityManagerService#startProcessLocked()>>      

#### 1.2.1 fork一个新的进程的三个步骤：  
①AMS通过Socket通信，向Zygote发送一个创建进程请求，Zygote创建新进程。  
②创建好进程后，调用ActivityThread.main()。到此，我们到了新了一个进程中，也是程序的入口出。  
③调用ActivityThread.attach()开始新的应用程序，接着同过Binder通信通知AMS，新的进程已经创建好了，可以开始新的程序了。  

#### 1.2.2  ActivityManagerNative.attachApplication()  
ps：实际调用的是ActivityManagerService.attachApplication  
①根据Binder.getCallingPid(),或得客户进程pid，并调用attachApplicationLocked(IApplicationThreadthread,int pid)  
②在attachApplicationLocked中，根据pid找到对应的ProcessRecord对象，如果找不到说明改pid客户进程是一个没经过AMS允许的进程。  
③为ProcessRecordapp对象内部变量赋值  
④确保目标程序（APK）文件已经被转换为了odex文件。Android中安装程序是APK文件，实际上是一个zip文件。  
⑤调用ActivityStack.realStartActivityLocked通知客户进程运行指定Activity.  
⑥调用ApplicationThread.scheduleLaunchActivity，启动指定Activity。  

#### 1.2.3 客户进程启动指定Activity  
AMS通过IPC通行，通知客户进程启动指定Activity：  
①调用ApplicationThread.scheduleLaunchActivity  
②经过Handler消息传动，调用ActivityThread.handleLaunchActivity()  
③调用ActivityThread.performLaunchActivity()完成Activity的加载，并最终调用Activity生命周期的onCreate()方法  
④performLaunchActivity返回，继续调用ActivityThread.handleResumeActivity(),该方法内部又调用ActivityThread.performResumeActivity(),其内部仅仅调用了目标Activity的onResume()方法。到此Activity启动完成。  
⑤添加一个IdleHandler对象，因为在一般情况下，该步骤执行完毕后，Activity就会进入空闲状态，所以就可以进行内存回收。  

## 2. ActivityStack 、TaskRecord和ActivityRecord

从ActivityStack#destroyActivityLocked（）>>     

ActivityStack#removeActivityFromHistoryLocked（）>>  

    final TaskRecord task = r.task;
    if (task != null && task.removeActivity(r)) {
        if (DEBUG_STACK) Slog.i(TAG,
                 "removeActivityFromHistoryLocked: last activity removed from " + this);
         if (mStackSupervisor.isFrontStack(this) && task == topTask() && task.mOnTopOfHome) {
              mStackSupervisor.moveHomeToTop();
          }
           mStackSupervisor.removeTask(task);
      }
     r.takeFromHistory()

这里正式开始处理TaskRecord栈里面Activity记录

