title: 热补丁
date: 2015-11-01 20:10:33
categories:
- Android
tags:
- Android
- 热补丁
---

# 基于java的热补丁逻辑

## 核心两个部分
### 1. hook部分  
hook部分主要是使用反射调用补丁里面的内容

hook部分的本质是提供对补丁方法调用的封装（主工程无法直接实例和调用补丁的方法），每次调用都是通过反射调用，传入activity，handler，callback进去。

### 2. 补丁部分
补丁实际上是java代码转的dex  
它的工作有两种：网络取数据，构造生成view


补丁部分构造view是通过hook部分传过来activity，然后用代码动态构造view，不涉及到任何布局文件，资源文件。  



## hook的初始化及调用过程
1. 初始化DexClassLoader  
classLoader = new DexClassLoader(dexApkFilePath
                    + dexName + ".apk", context.getDir("dex", Context.MODE_PRIVATE).getAbsolutePath(), null,
                    context.getClassLoader().getParent());
                    
2. load补丁相应的class  
controllerClass = classLoader.loadClass("com.nico.Controller");

3. 初始化构造函数
controllerConstrucor = controllerClass.getConstructor(new Class[]{Context.class, String.class, boolean.class});

4. 实例化补丁里面的类
controllerInstance = controllerConstrucor.newInstance(new Object[]{mContext});

5. 通过初始化的实例controllerInstance来调用里面的方法  
Method initController = controllerClass.getDeclaredMethod("initController", new Class[]{String.class, String.class, String.class});
        initController.setAccessible(true);
        initController.invoke(controllerInstance, new Object[]{paramsA, paramsB, paramsC});

## 补丁的升级

1. 校验是否有新的版本升级
2. 把新的补丁下载到本地sd卡中去
3. 解压补丁到data/data/app.pkg/app_dex目录  
ZipManager.extNativeZipFile(mContext,
                            mContext.getResources().getAssets().open(Utils.ZIP_NAME),
                            cachePath, dexApkFilePath, lastVersion)
4. 重新走一遍补丁的实例化过程（从DexLoader开始）

## 坑
1. 第一次安装，补丁放到asset目录下面
2. 由于里面传入了activity，要注意销毁补丁里面的强引用


## To Be Continue
1. load补丁里面的资源文件 ,通过反射调用AssetManger里面的资源文件，把ID设置上去 

 AssetManager assetManager = AssetManager.class.newInstance();  
            Method addAssetPath = assetManager.getClass().getMethod("addAssetPath", String.class);  
            addAssetPath.invoke(assetManager, libPath);  
            Resources superRes = super.getResources();  
            mRes = new Resources(assetManager, superRes.getDisplayMetrics(), superRes.getConfiguration());
            
2. 尝试使用mvp模式，把controllor从activity里面剥离开来，让所有contollor可以被热补丁，这要处理起来（可以把整个app轻量化）



## 参考资料

http://blog.csdn.net/wwj_748/article/details/46349781

http://blog.csdn.net/yuanzeyao/article/details/42390431

http://blog.csdn.net/u010386612/article/details/51077291


http://blog.csdn.net/cn_foolishman/article/details/46874811