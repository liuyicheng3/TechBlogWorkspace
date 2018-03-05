title: 全屏模式AdjustResize实现
date: 2017-9-15
categories:
- Android
   
   
tags:   
- Android
- 全屏模式
- AdjustResize

---

## 方案1 
使用stackoverflo 上的 AndroidBug5497Workaround


但是这个AndroidBug5497Workaround有个问题就是  
A如果是最开始输入框在下面，就会出现输入法先把界面顶上去 ，然后又调整下来的过程   
B如果在最上面就不会出现这个过程  



这个我们先考虑没有使用AndroidBug5497Workaround时候的情况  
A如果是最开始输入框在下面，就会出现输入法会把整个界面顶上去   
B如果在最上面，整个界面会看着基本不动，但是root view没有adjustResize的过程，因此导致原来alignparentBottom的元素看不到  



AndroidBug5497Workaround的原理是监听rootView 可视区域的变化，但是这个onGlobalLayout回调的速度明显慢于键盘弹出的速度，
所以在A情况下就会出现顶上去又弹回去的情况   
（如果在这里纠结使监听可视区域变化速度 和 键盘弹出速度  完全 一直的话 ，那是不可能的）
而在B情况下，由于没加AndroidBug5497Workaround这个时候本身就不会有顶去来的过程，所以主体界面本身就不会有抖动情况（注意 我们监听时候改变了主体界面的高度，但是这个根本不会影响到主体界面，因为即使改变高度， android 绘制的坐标系也是从左上角开始的，所以不存在任何问题）
而这时候我们改变root view的size  只是会导致底部的aliparentBottom的控件上移动，上移动的速度实际上比键盘弹出的速度慢，但是最终能调整到键盘的位置，所以这里根本不会导致主题界面抖动


    mChildOfContent.getViewTreeObserver().addOnGlobalLayoutListener(new ViewTreeObserver.OnGlobalLayoutListener() {
              public void onGlobalLayout() {
                  possiblyResizeChildOfContent();
              }
          });

    private void possiblyResizeChildOfContent() {
          int usableHeightNow = computeUsableHeight();
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
          }
      }

    private int computeUsableHeight() {
        Rect r = new Rect();
        mChildOfContent.getWindowVisibleDisplayFrame(r);
        return (r.bottom - r.top);
    }



#### 虚拟按键
注意android的虚拟按键有两种：  
一种是N5 N6一类的固定在底部的虚拟按键  

一种是华为 小米mix 一类的的  可以通过手势动态控制底部虚拟按键显示还隐藏   
这种就需要动态计算高度  

为了解决A问题，需要在顶部放置一个fake EditText ，点击目标EditText时候先让顶部的fakeEditText获得焦点，待键盘完全弹出来后再把焦点转移给目标EditText   
具体方案：目标EditText监控ontouch事件，在TouchUp时候消耗掉这个事件，这样就不会触发键盘直接弹出来了，这时候，顶部的 fake EditText先获取焦点，延迟一段时间 待键盘完全弹出后再让目标EditText获取焦点


## 方案2：
https://github.com/Jacksgong/JKeyboardPanelSwitch    
原理：  
在目标EditText下面加一个KPSwitchPanelLinearLayout  通过动态设置这个KPSwitchPanelLinearLayout的Visual状态和高度动态调整高度    
其包括两个步骤  
1、测量和调整高度  
2、editText获取焦点事件的拦截（也是通过ontouch实现的）  
      
      cn.dreamtobe.kpswitch.util.KeyboardUtil#attach(android.app.Activity, cn.dreamtobe.kpswitch.IPanelHeightTarget,    cn.dreamtobe.kpswitch.util.KeyboardUtil.OnKeyboardShowingListener)  
      
这里实际上是加了个  

    contentView.getViewTreeObserver().
                    addOnGlobalLayoutListener(
                            new KeyboardStatusListener(isFullScreen, isTranslucentStatus,
                                    isFitSystemWindows,
                                    contentView, target, listener));  
                                    
在onGlobalLayout里面计算出合适的高度设置给pannelView

    userRootView.getWindowVisibleDisplayFrame(r);
                displayHeight = (r.bottom - r.top);
    ......              
    calculateKeyboardHeight(displayHeight);
    calculateKeyboardShowing(displayHeight);

    中 calculateKeyboardHeight

    panelHeightTarget.refreshHeight




  
这里涉及到一个问题就是初始时候不止到键盘高度怎么办(或者手动调整过键盘高度怎么办)  
初始高度：会设置一个默认的最小高度给panel，然后待键盘完全弹出后在修复这个高度  

    panelLayoutHandler.resetToRecommendPanelHeight(panelHeight)
    >>
    ViewUtil.refreshHeight(panelLayout, recommendPanelHeight);
    ......
    final int validPanelHeight = KeyboardUtil.getValidPanelHeight(view.getContext());
    ViewGroup.LayoutParams layoutParams = view.getLayoutParams();
    if (layoutParams == null) {
        layoutParams = new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                validPanelHeight);
        view.setLayoutParams(layoutParams);
    } else {
        layoutParams.height = validPanelHeight;
        view.requestLayout();
    }






