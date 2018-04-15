title: Android版本更新特性 	    
date: 2017-10-11         
categories:            
   
    
- Android           
  
tags:           
    
   
- 版本        
  
- Android        
    

           
---



## 1. Android 3.0 
* 硬件加速  

## 2. Android 4.1 
* 黄油计划

## 3. Android 4.4  
* 推出art 但是默认还是davilk
* 对齐唤醒：把AlarmManager的默认方法改用了对齐但不保证准确的模式

## 4. Android 5  
* Android Runtime (ART)默认运行平台设置  
* 引入Material Design设计
* 转场动画  

#### 保活注意点： 
在5.0以前使用LibMarsdeamon的保活方法   
在5.0以后使用JobScheduler进行保活   

JobScheduler使用系统定义要在以后的某个时间或在指定的条件下（例如，当设备在充电时）异步运行的作业来优化电池寿命    

		JobInfo.Builder builder = new JobInfo.Builder(job,
		                        new ComponentName(ApplicationManager.ctx, CustomJobSchedulerService.class));
		    builder.setPeriodic(3000);// 每隔三秒运行一次  设置太小会无效
		    builder.setPersisted(true);

		    JobScheduler jobScheduler = (JobScheduler) ApplicationManager.ctx.
		            getSystemService(Context.JOB_SCHEDULER_SERVICE);
		    if (jobScheduler!=null) {
		        jobScheduler.schedule(builder.build());
		    }


## Android 6.0
* 运行时请求权限
* Doze mode：应用不在白名单,系统灭屏经过大约一小时后,上层应用wake lock,alarm,还有网络链接都会失效       
参考链接： http://blog.csdn.net/xiaorenwu1206/article/details/49358433  

## Android7.0
* 分屏
* 加强版的Doze模式：N与6.0的区别就在于N在手机非静止时也可进入低电耗模式  
* Project Svelte：后台优化

## Android 8.0  
* 优化通知

### 参考资料  
1. https://www.jianshu.com/p/8a66806588bc
