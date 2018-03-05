title: Android 性能检测
date: 2015-11-01 20:10:33
categories:
- Android
   
   
   
tags:   
- Android
- 性能分析
---

# 手机端：

## 开发者选项
1. 绘图》 显示布局边界

2. 硬件加速渲染 》调试GPU过渡绘制  要打开


3. 监控》启用严格模式
	 
4. GPU呈现模式分析  可以对照颜色表找出耗时出在那一部分
 ![image](https://github.com/liuyicheng3/learning-summary/blob/master/images/GPU%E6%B8%B2%E6%9F%93%E6%A8%A1%E5%BC%8F.jpg?raw=true)
 
# 电脑端：
1. 查看MemoryMonitor  ，查看页面内存波动（对于listview ）

2. tools》android》android  device  monistor
（其实它就是把android sdk中tools下面的很多功能聚合起来；  如ddms，uiautomatorviewer，monitor等功能聚合起来，但是好像没有集成hierarchyviewer的功能）

3. 查看录制页面变化时候的cpu耗时   
  开始录制》选中进程，点击红色方框左边的按钮，然后点击红色方框里右侧的按钮录制正式开始，需要结束时，再点击右侧按钮结束，就会有结果自动生成  
 ![image](https://github.com/liuyicheng3/learning-summary/blob/master/images/%E5%88%86%E6%9E%90%E8%80%97%E6%97%B6.png?raw=true)
  
  分析结果》录制实际上是一个采样的过程，可以看图中红色方框里面最耗时的几个方法，基本上可以定位到程序的问题   
 ![image](https://github.com/liuyicheng3/learning-summary/blob/master/images/%E5%88%86%E6%9E%90%E8%80%97%E6%97%B6_2.png?raw=true)
4. 查看布局层次，以及每一层的绘制时间，目的是减小层次  
入口是在：tools 下面 hierarchyviewer  查看每个层次的绘制时间（这个好像必须在模拟器上看）


# 分析卡的原因


# 参考资料 
http://www.cnblogs.com/krislight1105/p/5352500.html  
http://blog.csdn.net/wangbaochu/article/details/50396512
