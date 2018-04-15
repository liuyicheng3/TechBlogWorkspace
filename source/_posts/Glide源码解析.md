title: Glide源码解析    
date: 2018-3-115     
categories:    
- Android    
       
       
       
tags:       
- Android    
- 图片       
    
    
---



![see](https://github.com/liuyicheng3/learning-summary/blob/master/images/glide_10.jpg?raw=true)    


# 1.请求流程 

        GlideApp.with(mActivity)
            .load(thumbnail)
            .placeholder(defaultResId)
            .into(this); 
            
1. GlideApp.with(mActivity) 获取RequestManager  
2. into(this)   

        Request previous = target.getRequest();
    
        if (previous != null) {
         requestManager.clear(target);
        }
    
        requestOptions.lock();
        Request request = buildRequest(target);
        target.setRequest(request);
        requestManager.track(target, request);  
        
3. com.bumptech.glide.request.SingleRequest#begin  开始量尺寸

        if (Util.isValidDimensions(overrideWidth, overrideHeight)) {
          onSizeReady(overrideWidth, overrideHeight);
        } else {
          target.getSize(this);
        }

onSizeReady后engine正式启动请求 

        loadStatus = engine.load(
        glideContext,
        model,
        requestOptions.getSignature(),
        this.width,
        this.height,
        requestOptions.getResourceClass(),
        transcodeClass,
        priority,
        requestOptions.getDiskCacheStrategy(),
        requestOptions.getTransformations(),
        requestOptions.isTransformationRequired(),
        requestOptions.isScaleOnlyOrNoTransform(),
        requestOptions.getOptions(),
        requestOptions.isMemoryCacheable(),
        requestOptions.getUseUnlimitedSourceGeneratorsPool(),
        requestOptions.getUseAnimationPool(),
        requestOptions.getOnlyRetrieveFromCache(),
        this);
        
4. 尝试重cache 和activeResource里面获取资源 

 EngineKey key = keyFactory.buildKey(model, signature, width, height, transformations,
        resourceClass, transcodeClass, options);

    EngineResource<?> active = loadFromActiveResources(key, isMemoryCacheable);
    if (active != null) {
      cb.onResourceReady(active, DataSource.MEMORY_CACHE);
      if (Log.isLoggable(TAG, Log.VERBOSE)) {
        logWithTimeAndKey("Loaded resource from active resources", startTime, key);
      }
      return null;
    }

    EngineResource<?> cached = loadFromCache(key, isMemoryCacheable);
    if (cached != null) {
      cb.onResourceReady(cached, DataSource.MEMORY_CACHE);
      if (Log.isLoggable(TAG, Log.VERBOSE)) {
        logWithTimeAndKey("Loaded resource from cache", startTime, key);
      }
      return null;
    }


5. 从sd卡和网络获取数据  


            EngineJob<?> current = jobs.get(key, onlyRetrieveFromCache);
            if (current != null) {
              current.addCallback(cb);
              if (Log.isLoggable(TAG, Log.VERBOSE)) {
                logWithTimeAndKey("Added to existing load", startTime, key);
              }
              return new LoadStatus(cb, current);
            }

            EngineJob<R> engineJob =
                engineJobFactory.build(
                    key,
                    isMemoryCacheable,
                    useUnlimitedSourceExecutorPool,
                    useAnimationPool,
                    onlyRetrieveFromCache);

            DecodeJob<R> decodeJob =
                decodeJobFactory.build(
                    glideContext,
                    model,
                    key,
                    signature,
                    width,
                    height,
                    resourceClass,
                    transcodeClass,
                    priority,
                    diskCacheStrategy,
                    transformations,
                    isTransformationRequired,
                    isScaleOnlyOrNoTransform,
                    onlyRetrieveFromCache,
                    options,
                    engineJob);

            jobs.put(key, engineJob);

            engineJob.addCallback(cb);
            engineJob.start(decodeJob);


最终会通过Glide里面定义的executor 获取数据  

      public void start(DecodeJob<R> decodeJob) {
        this.decodeJob = decodeJob;
        GlideExecutor executor = decodeJob.willDecodeFromCache()
            ? diskCacheExecutor
            : getActiveSourceExecutor();
        executor.execute(decodeJob);
      }
6. 获取数据的过程    

最开进来时候是在 GlideExecutor diskCacheExecutor   

com.bumptech.glide.load.engine.DecodeJob#runWrapped  


         private void runWrapped() {
             switch (runReason) {
              case INITIALIZE:
                stage = getNextStage(Stage.INITIALIZE);
                currentGenerator = getNextGenerator();
                runGenerators();
                break;
              case SWITCH_TO_SOURCE_SERVICE:
                runGenerators();
                break;
              case DECODE_DATA:
                decodeFromRetrievedData();
                break;
              default:
                throw new IllegalStateException("Unrecognized run reason: " + runReason);
            }
          }
  
                private void runGenerators() {
                    currentThread = Thread.currentThread();
                    startFetchTime = LogTime.getLogTime();
                    boolean isStarted = false;
                    while (!isCancelled && currentGenerator != null
                        && !(isStarted = currentGenerator.startNext())) {
                      stage = getNextStage(stage);
                      currentGenerator = getNextGenerator();

                      if (stage == Stage.SOURCE) {
                        reschedule();
                        return;
                      }
                    }
                    // We've run out of stages and generators, give up.
                    if ((stage == Stage.FINISHED || isCancelled) && !isStarted) {
                      notifyFailed();
                    }
                  }
          
这个地方实际上就是不断的生成NextGenerator ，在里面DataFetcherGenerator里面的startNext执行下一个操作，最后当NextStage为Stage.SOURCE时候切换回  GlideExecutor sourceExecutor;


                 private Stage getNextStage(Stage current) {
                    switch (current) {
                      case INITIALIZE:
                        return diskCacheStrategy.decodeCachedResource()
                            ? Stage.RESOURCE_CACHE : getNextStage(Stage.RESOURCE_CACHE);
                      case RESOURCE_CACHE:
                        return diskCacheStrategy.decodeCachedData()
                            ? Stage.DATA_CACHE : getNextStage(Stage.DATA_CACHE);
                      case DATA_CACHE:
                        // Skip loading from source if the user opted to only retrieve the resource from cache.
                        return onlyRetrieveFromCache ? Stage.FINISHED : Stage.SOURCE;
                      case SOURCE:
                      case FINISHED:
                        return Stage.FINISHED;
                      default:
                        throw new IllegalArgumentException("Unrecognized stage: " + current);
                    }
                  }
                  
          
PS：判断使用何种ModuleLoader就是在SourceGenerator里实现的 

       



7. 数据获取到后回调 

可能是直接从DecodeJob切回主线程 ，也可能是从SourceGenerator切回去的   

com.bumptech.glide.load.engine.DecodeJob#notifyComplete  
        
        callback.onResourceReady(resource, dataSource);
        
com.bumptech.glide.load.engine.SourceGenerator#onDataReady  

        DiskCacheStrategy diskCacheStrategy = helper.getDiskCacheStrategy();
            if (data != null && diskCacheStrategy.isDataCacheable(loadData.fetcher.getDataSource())) {
              dataToCache = data;
            
              cb.reschedule();
            } else {
              cb.onDataFetcherReady(loadData.sourceKey, data, loadData.fetcher,
                  loadData.fetcher.getDataSource(), originalKey);
            }

具体切换的实现逻辑：  


        @Override
        public void onResourceReady(Resource<R> resource, DataSource dataSource) {
            this.resource = resource;
            this.dataSource = dataSource;
            MAIN_THREAD_HANDLER.obtainMessage(MSG_COMPLETE, this).sendToTarget();
          }
        
         @Override
         public void onLoadFailed(GlideException e) {
            this.exception = e;
            MAIN_THREAD_HANDLER.obtainMessage(MSG_EXCEPTION, this).sendToTarget();
          }
          
          
子线程转回主线程的方法： 

        private static final Handler MAIN_THREAD_HANDLER =
              new Handler(Looper.getMainLooper(), new MainThreadCallback());   
      
     private static class MainThreadCallback implements Handler.Callback {
        
            @Synthetic
            @SuppressWarnings("WeakerAccess")
            MainThreadCallback() { }
        
            @Override
            public boolean handleMessage(Message message) {
              EngineJob<?> job = (EngineJob<?>) message.obj;
              switch (message.what) {
                case MSG_COMPLETE:
                  job.handleResultOnMainThread();
                  break;
                case MSG_EXCEPTION:
                  job.handleExceptionOnMainThread();
                  break;
                case MSG_CANCELLED:
                  job.handleCancelledOnMainThread();
                  break;
                default:
                  throw new IllegalStateException("Unrecognized message: " + message.what);
              }
              return true;
            }
          }
          
8. 显示数据及缓存 

        com.bumptech.glide.load.engine.EngineJob#handleResultOnMainThread  {
        
           ..... 
           engineResource.acquire();
            listener.onEngineJobComplete(this, key, engineResource);
        
            int size = cbs.size();
            for (int i = 0; i < size; i++) {
              ResourceCallback cb = cbs.get(i);
              if (!isInIgnoredCallbacks(cb)) {
                engineResource.acquire();
                cb.onResourceReady(engineResource, dataSource);
              }
            }
            // Our request is complete, so we can release the resource.
            engineResource.release();
        
            release(false /*isRemovedFromQueue*/);
        }
        
ps: 其实在cb.onResourceReady(engineResource, dataSource); 里面有release();



# 2.核心技术点 
## 2.1 AppGlideModule和ModuleLoader  

AppGlideModule#applyOptions 配置builder参数   

        @Override
        public void applyOptions(Context context, GlideBuilder builder) {
            final int diskCacheSizeBytes = 200 * 1024 * 1024; // 200 MB
            builder.setDiskCache(new DiskLruCacheFactory(MidData.ImageDir, diskCacheSizeBytes));
            judgeIfIsLowDevice(context,builder);
            super.applyOptions(context, builder);
        }

根据尺寸加载不同的url  

         @Override
            public void registerComponents(Context context, Glide glide, Registry registry) {
                registry.append(GlideUrl.class, InputStream.class, new SizeCompatLoader.SizeCompatFactory());
        
        //        registry.prepend(String.class, ByteBuffer.class, new Base64ModelLoaderFactory());
            }
            
moudleloader的定义demo

    public class SizeCompatLoader extends OkHttpUrlLoader {
    
        public SizeCompatLoader(Call.Factory client) {
            super(client);
        }
    
        @Override
        public boolean handles(GlideUrl url) {
            return super.handles(url);
        }
    
        @Override
        public LoadData<InputStream> buildLoadData(GlideUrl model, int width, int height, Options options) {
            ELog.e("url:"+model.toStringUrl());
            return super.buildLoadData(model, width, height, options);
        }
        ........
        
        public static class SizeCompatFactory extends  OkHttpUrlLoader.Factory{
        private static volatile Call.Factory internalClient;
        private Call.Factory client;

        private static Call.Factory getInternalClient() {
            if (internalClient == null) {
                synchronized (Factory.class) {
                    if (internalClient == null) {
                        internalClient = new OkHttpClient();
                    }
                }
            }
            return internalClient;
        }

        /**
         * Constructor for a new Factory that runs requests using a static singleton client.
         */
        public SizeCompatFactory() {
            this(getInternalClient());
        }

        /**
         * Constructor for a new Factory that runs requests using given client.
         *
         * @param client this is typically an instance of {@code OkHttpClient}.
         */
        public SizeCompatFactory(Call.Factory client) {
            this.client = client;
        }

        @Override
        public ModelLoader<GlideUrl, InputStream> build(MultiModelLoaderFactory multiFactory) {
            return new SizeCompatLoader(client);
        }

        @Override
        public void teardown() {
            // Do nothing, this instance doesn't own the client.
        }
        }
    }  
    
    

实际上可以注册多个moudleloader,使用过程中，通过handle(GlideUrl url) 决定是否可以使用这个加载器  
在请求流程里面是在SourceGenerator判断moudleloader使用哪一个的： 

          public boolean startNext() {
            if (dataToCache != null) {
              Object data = dataToCache;
              dataToCache = null;
              cacheData(data);
            }

            if (sourceCacheGenerator != null && sourceCacheGenerator.startNext()) {
              return true;
            }
            sourceCacheGenerator = null;

            loadData = null;
            boolean started = false;
            while (!started && hasNextModelLoader()) {
              loadData = helper.getLoadData().get(loadDataListIndex++);
              if (loadData != null
                  && (helper.getDiskCacheStrategy().isDataCacheable(loadData.fetcher.getDataSource())
                  || helper.hasLoadPath(loadData.fetcher.getDataClass()))) {
                started = true;
                loadData.fetcher.loadData(helper.getPriority(), this);
              }
            }
            return started;
          }

![see](https://github.com/liuyicheng3/learning-summary/blob/master/images/glide_8.png?raw=true)    




## 2.2 内存缓存 

* cache （LRUCache）  :不在使用的会放入到 cache里面 （因为每次从resource.acquire 会导致计数器加1，不再使用时候resource.release 会导致计数器减1，当计数器的值减为0时候就会放入cache中）

* activeresource（HashMap+WeakPreference） ： 正在使用的会放入到activeresource里面  



#### 内存缓存的读取
![see](https://github.com/liuyicheng3/learning-summary/blob/master/images/glide_0.png?raw=true)    
![see](https://github.com/liuyicheng3/learning-summary/blob/master/images/glide_1.png?raw=true)  

### activeresource的put
1. 在最后onEngenJobComplete时候 
![see](https://github.com/liuyicheng3/learning-summary/blob/master/images/glide_3.png?raw=true)    

### activeresource的移除 
1. 在从activeresource里面获取资源后  

        WeakReference<EngineResource<?>> activeRef = activeResources.get(key);
            if (activeRef != null) {
              active = activeRef.get();
              if (active != null) {
                active.acquire();
              } else {
                activeResources.remove(key);
              }
            }

2. 当资源被释放后

          public void onResourceReleased(Key cacheKey, EngineResource resource) {
            Util.assertMainThread();
            activeResources.remove(cacheKey);
            if (resource.isCacheable()) {
              cache.put(cacheKey, resource);
            } else {
              resourceRecycler.recycle(resource);
            }
          }
          
有两种原因导致资源被立即释放   

a. 最后 handleResultOnMainThread时候 每次enginResource计数器减1，当为0，时候会移入cache，同时从activeresource移除
![see](https://github.com/liuyicheng3/learning-summary/blob/master/images/glide_2.png?raw=true)      
  
  
b. 当into（Target）时候判断上一个还有绑定的资源时候的clear过程  
![see](https://github.com/liuyicheng3/learning-summary/blob/master/images/glide_5.png?raw=true)      

最终会导致realease过程
![see](https://github.com/liuyicheng3/learning-summary/blob/master/images/glide_6.png?raw=true)   


### cache的put操作  
1. 读取内存时候从activeresource获取到了元素：   

2. 当resource的计数器变成0的时候   

## 2.3 生命周期的绑定（通过一个隐形的fragment与activity的生命周期绑定）    
 
com.bumptech.glide.manager.RequestManagerRetriever#get(android.content.Context)


        public RequestManager get(Activity activity) {
            if (Util.isOnBackgroundThread()) {
              return get(activity.getApplicationContext());
            } else {
              assertNotDestroyed(activity);
              android.app.FragmentManager fm = activity.getFragmentManager();
              return fragmentGet(activity, fm, null /*parentHint*/);
            }
          }

        private RequestManager fragmentGet(Context context, android.app.FragmentManager fm,
        android.app.Fragment parentHint) {
                RequestManagerFragment current = getRequestManagerFragment(fm, parentHint);
                RequestManager requestManager = current.getRequestManager();
                if (requestManager == null) {
                // TODO(b/27524013): Factor out this Glide.get() call.
                Glide glide = Glide.get(context);
                requestManager =
                factory.build(glide, current.getGlideLifecycle(), current.getRequestManagerTreeNode());
                current.setRequestManager(requestManager);
        }
        return requestManager;
        }
        
        
其中RequestManagerFragment hook了所有的Fragment的生命周期  
        
关键属性ActivityFragmentLifecycle lifecycle：会在这里面pause request     

## 2.3 自定自定义transform  

      GlideApp.with(activity)
              .load(thumbnail)
              .transition(new DrawableTransitionOptions().crossFade()) //自定义 淡入淡出效果
              .transform(new MultiTransformation<Bitmap>(new CenterCrop(), new BlurTransformation())) //自定义图片后续处理比如 缩放、旋转、蒙灰 、或者高斯模糊
              .into(this);

高斯模糊BlurTransformation:  

    public class BlurTransformation extends BitmapTransformation {

    .....

    @Override
    protected Bitmap transform(@NonNull Context context, @NonNull BitmapPool pool,
                               @NonNull Bitmap toTransform, int outWidth, int outHeight) {

        int width = toTransform.getWidth();
        int height = toTransform.getHeight();
        int scaledWidth = width / sampling;
        int scaledHeight = height / sampling;

        Bitmap bitmap = pool.get(scaledWidth, scaledHeight, Bitmap.Config.ARGB_8888);

        Canvas canvas = new Canvas(bitmap);
        canvas.scale(1 / (float) sampling, 1 / (float) sampling);
        Paint paint = new Paint();
        paint.setFlags(Paint.FILTER_BITMAP_FLAG);
        canvas.drawBitmap(toTransform, 0, 0, paint);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR2) {
            try {
                bitmap = BlurRS.blur(context, bitmap, radius);
            } catch (RSRuntimeException e) {
                bitmap = BlurFast.blur(bitmap, radius, true);
            }
        } else {
            bitmap = BlurFast.blur(bitmap, radius, true);
        }

        return bitmap;
    }

    ......
}



## 3 参考资料  

Glide整体流程： http://www.cnblogs.com/android-blogs/p/5735655.html   

Glide缓存： http://www.cnblogs.com/android-blogs/p/5737611.html  

Glide绑定activity生命周期： http://www.jishux.com/plus/view-662982-1.html  















