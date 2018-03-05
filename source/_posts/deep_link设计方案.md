title: Deeplink 设计
date: 2015-11-01 20:10:33
categories:
- Android
   
   
   
tags:   
- Android
---


## 概念  

deeplink指的是在第三方客户端/浏览器中，打开一个APP的H5页面时候，如果发现本地安装了这个APP，就会使用本地APP打开。
需要前端和客户端互相配合来实现本功能。

# 服务器端：

    <html>
    <head>
    <meta property="al:ios:url" content="applinks://docs" />
    <meta property="al:ios:app_store_id" content="12345" />
    <meta property="al:ios:app_name" content="App Links" />
    <meta property="al:android:url" content="applinks://docs" />
    <meta property="al:android:app_name" content="App Links" />
    <meta property="al:android:package" content="org.applinks" />
    <meta property="al:web:url"
    content="http://applinks.org/documentation" />
    </head>
    <body>
    Hello, world!
    </body>
    </html>

# 客户端  
客户端deeplink的实现需要依靠jump系统。ps:jump系统可以通过URI 实现在app中的定向跳转 ，比如我们的app叫“天上人间”（缩写tsrj）。 

1. 需要先在menifest中注册相应的scheme的filter。  
   ps:一般加载主页上面.


        <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <!-- Accepts URIs that begin with "tsrj://" -->
        <data android:scheme="tsrj"/>
        </intent-filter>
        <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <!-- Accepts URIs that begin with "http://m.tsrj.com/" -->
        <data
        android:host="m.tsrj.com"
        android:pathPrefix="/"
        android:scheme="http"/>
        <data
        android:host="m.tsrj.com"
        android:pathPrefix="/"
        android:scheme="https"/>
        </intent-filter>
    
2. 在MainActivity新增解析jump信息的方法


        private void jump(Intent intent) {
        /** 根据传过来的参数 进行jump跳转 **/
        String action_url = intent.getDataString();
        MLog.i("启动Main_action_url:" + action_url);
        if (!TextUtils.isEmpty(action_url)) {
        JumpManager.jump(this, action_url);
        } 
        }
        
        JumpManger就实现解析数据然后根据URI跳转的功能
        public static boolean jump(Context ctx, String action_url) {
        
        if (TextUtils.isEmpty(action_url)) {
        return false;
        }
        
        MLog.d("JumpManager  url:" + action_url);
        
        Uri uri = null;
        
        /**如果不是一个标准的uri格式说明传入的数据无效的 可以直接忽视*/
        
        try {
        uri = Uri.parse(action_url);
        } catch (Exception e) {
        return false;
        }
        
        if (uri == null) {
        return false;
        }
        
        /**检测到是一个合法的uri 先判断是否是满足跳转需求的头部 如果是 开始进行跳转检测 如果不是 直接往内置浏览器跳*/
        
        if (!action_url.startsWith(JumpUriFactory.JUM_URL_HEAD) && !action_url.startsWith(JumpUriFactory.JUMP_URL_HEAD_S) && !action_url.startsWith(JumpUriFactory.JUMP_URL_HEAD_CUSTOM)) {
        
        return false;
        }
        
        Intent jumpintent = null;
        
        List<String> paths = uri.getPathSegments();
        
        /**只有头没有页面参数就返回*/
        if (paths == null || paths.size() <= 0) {
        
        return false;
        }
        
        /**有path 但是path里面为空值 直接打开*/
        String action = paths.get(0);
        if (TextUtils.isEmpty(action)) {
        if (!isFromWebView) {
        jumpToInteriorPageActivity(ctx, uri);
        }
        return false;
        }
        
        /** 使用系统浏览器打开 */
        if (action.equals("web_system")) {
        jumpToSystemWebPage(ctx, uri);
        return true;
        }
        
        
        /*else if (action.equals(JumpPageSet.detail)) {
        goWaitress(ctx, action_url);
        return true;
        }*/
        
        /** city */
        else if (action.equals(JumpPageSet.city)) {
        goCity(ctx, action_url);
        return true;
        }
        
        /** usercenter */
        else if (action.equals(JumpPageSet.personal_info)) {
        goUserCenter(ctx, action_url);
        return true;
        }


3. 处理uri解析出里面的参数,放入intent，并跳往相应的主页


        /**
         * 将url的数据进行解析 得到一个存放所有参数的集合
         */
        public static Set<String> getMyQueryParameterNames(Uri uri) {
            String query = uri.getEncodedQuery();
            if (query == null) {
                return Collections.emptySet();
            }
            Set<String> names = new LinkedHashSet<String>();
            int start = 0;
            do {
                int next = query.indexOf('&', start);
                int end = (next == -1) ? query.length() : next;
                int separator = query.indexOf('=', start);
                if (separator > end || separator == -1) {
                    separator = end;
                }
                String name = query.substring(start, separator);
                names.add(Uri.decode(name));
                // Move start to end of name.
                start = end + 1;
            } while (start < query.length());
            return Collections.unmodifiableSet(names);
        }
        private static void goWaitress(final Context ctx, String actionUrl) {
            MLog.i("actionUrl"+actionUrl);
            Uri  uri;
            uri=Uri.parse(actionUrl);
            Set<String>  parameters=JumpManager.getMyQueryParameterNames(uri);
            Hashtable<String,String> params=new Hashtable<>();
            if(parameters!=null&&parameters.size()>0){
                for(String key:parameters){
                    String value=uri.getQueryParameter(key);
                    if(!TextUtils.isEmpty(value)){
                        params.put(key,value);
                    }
                }
            }
            Intent it= new Intent(act, WaitressPage.class);
            Set<String>  keySet=params.keySet();
            for (String k:keySet){
                it.putExtra(k,params.get(k));
            }
            startActivity(it);
            }



# DeepLink的坑： 

1. 由于有些页面有权限限制，所以要跳页面时候，要判断在当前账户当前版本是否可以打开
2. 如果从H5页面带过来的信息带有登录状态，而且当前app的账号信息和H5页面的不一致，可能需要一个账号切换工作


#微信里面的deeplink：
微信里面的主要就是二维码加上linkme，linkme和微信有合作可以直接把分享的内容通过里面的二维码倒回到app，不过这里要注意一个问题
微信里面的图片对size 是有要求的

图片size越大被压的越厉害，，这个即使通过以下方式绕过微信sdk也无法避免被压缩

        try {
            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setAction(Intent.ACTION_VIEW);
            intent.addCategory(Intent.CATEGORY_DEFAULT);
            ComponentName cmp = new ComponentName("com.tencent.mm", "com.tencent.mm.ui.tools.ShareScreenImgUI");
            intent.setComponent(cmp);
            String path = localImgPath;
            if (!TextUtils.isEmpty(path) && !path.startsWith("file://")) {
                path = "file://" + path;
            }
            intent.setDataAndType(Uri.parse(path), "image/jpeg");
            act.startActivity(intent);
        } catch (Exception e) {
            ELog.e("wechat share failed");
        }
        
 所以只有自己先压缩图片到一定的size，  再在这张压缩过的图片上绘制真正的二维码才行，（如果遇到好心的UI把二维码设计的很大就，可以跳过这个坑）
 



