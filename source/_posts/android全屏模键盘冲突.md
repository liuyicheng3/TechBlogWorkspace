title: 全屏模式底部键盘冲突    
date: 2017-9-10     
categories:    
- Android    
       
       
       
tags:       
- Android    
- 全屏模式    
- 键盘    
    
---

# 场景：全屏模式下activity的adjustResize 失效,弹键盘时候底部的输入框无法自动调整到键盘区域的上方 

## 1. 方案一：  
使用 AndroidBug5497Workaround （https://stackoverflow.com/questions/7417123/android-how-to-adjust-layout-in-full-screen-mode-when-softkeyboard-is-visible）  

<img src="https://github.com/liuyicheng3/learning-summary/blob/master/images/planA_normal.gif?raw=true" height="200px" width="100px" >  

原理：通过 getViewTreeObserver().addOnGlobalLayoutListener监听当前屏幕显示区域的大小，然后动态调整Activity rootView的height，实现“adjust resize”的效果   

       Rect r = new Rect();
       mChildOfContent.getWindowVisibleDisplayFrame(r);
      int usableHeightNow = r.bottom - r.top;
        if (usableHeightNow != usableHeightPrevious) {
            int usableHeightSansKeyboard = mChildOfContent.getRootView().getHeight();
            int heightDifference = usableHeightSansKeyboard - usableHeightNow;
            if (heightDifference > (usableHeightSansKeyboard/4)) {
                // keyboard probably just became visible
                frameLayoutParams.height = usableHeightSansKeyboard - heightDifference;
            } else {
                // keyboard probably just became hidden
                frameLayoutParams.height = usableHeightSansKeyboard;
            }
            mChildOfContent.requestLayout();
            usableHeightPrevious = usableHeightNow;

但是这个不能完全解决我们问题，会遇到下面的问题：  
在输入框在屏幕区域上方是没问题，在输入框在底部时候，会有一个特别不好的现象，键盘弹出后会迅速把整个Activity完全顶上去，然后调整回来。  

<img src="https://github.com/liuyicheng3/learning-summary/blob/master/images/planA.gif?raw=true" height="200px" width="100px" >


问题的原因是是OnGlobalLayoutListener不是实时和键盘弹时屏幕显示区域同步的。所以就会在键盘弹起的瞬间先把整个activity顶上去，然后顶上去后，屏幕内容又会掉下来  


补丁方案：  
输入框在底部时候不要直接弹出键盘，先让顶部的一个1px的输入框获得这个这个焦点，待键盘完全弹出来后再把焦点传递给底部的这个输入框，这样就不会有顶整个界面起来的现象

<img src="https://github.com/liuyicheng3/learning-summary/blob/master/images/planA_fix.gif?raw=true" height="200px" width="100px" >


补充问题    
为什么在顶部的时候不会出现顶上去又下来的情况？  
因为 输入框在最上面，键盘输入法只要弹出时不盖住输入框，就不会顶起这个Activity的内容，而内容区域调整也是延迟于键盘弹起速度的，但是由于键盘盖住了所以视觉感觉不出来    


#### 虚拟按键
注意android的虚拟按键有两种：  
一种是N5 N6一类的固定在底部的虚拟按键  

一种是华为 小米mix 一类的的  可以通过手势动态控制底部虚拟按键显示还隐藏   
这种就需要动态计算高度  

为了解决A问题，需要在顶部放置一个fake EditText ，点击目标EditText时候先让顶部的fakeEditText获得焦点，待键盘完全弹出来后再把焦点转移给目标EditText   
具体方案：目标EditText监控ontouch事件，在TouchUp时候消耗掉这个事件，这样就不会触发键盘直接弹出来了，这时候，顶部的 fake EditText先获取焦点，延迟一段时间 待键盘完全弹出后再让目标EditText获取焦点



## 2.方案二   
JkeyboardSwitch （https://github.com/Jacksgong/JKeyboardPanelSwitch）  

原理是在输入框下面加了一个和键盘高度相同的panel，在键盘弹出来的瞬间panel显示出来（invisualble状态），这样键盘的弹出和隐藏与panel的的invisualble和gone的状态同步起来，看起来的效果就是键盘出来时候把输入框顶上去，键盘收起来时候把输入框收回去  


这个方案的一个问题是“怎么在第一次弹出时候初始化panel高度和键盘高度一致?”    

<img src="https://github.com/liuyicheng3/learning-summary/blob/master/images/planB.gif?raw=true" height="200px" width="100px" >

补丁方案：  
第一次弹出瞬间把输入框的区域设置为Invisualbel ，初始panel的高度尽量大，待键盘完全弹出后把输入框区域显示出来，然后调整panel的高度，这样就能在用户无察觉的情况初始化这个panel高度。   

<img src="https://github.com/liuyicheng3/learning-summary/blob/master/images/planB_fix.gif?raw=true" height="200px" width="100px" >






