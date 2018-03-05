title: Okhttp核心流程
date: 2015-11-01 20:10:33
categories:
- android
   
tags   
- 网络层

---


## Interface：OkhttpClient（singleton）  Request  Response

## 主要由以下三部分 组成  

### 1. 任务调度： 核心类disruptor（singleton） 

a. 线程池   
b. 队列


      /** Ready async calls in the order they'll be run. */
      private final Deque<AsyncCall> readyAsyncCalls = new ArrayDeque<>();
      
      /** Running asynchronous calls. Includes canceled calls that haven't finished yet. */
      private final Deque<AsyncCall> runningAsyncCalls = new ArrayDeque<>();
      
      /** Running synchronous calls. Includes canceled calls that haven't finished yet. */
       private final Deque<RealCall> runningSyncCalls = new ArrayDeque<>();

(由于okhttp两种 运行模式   sync  和async）

### 2. 网络请求   
* 核心类RealCall HttpEngine StreamAllocation   Interceptor (及其中的内部类  Chain） 
* 每个请求会生成一个Request  
* 然后根据 request  和httpclieant  生成唯一的 RealCall(在real里面会构造出一个httpengine)  


okhttp一个请求的完整流程图  
 ![image](http://blog.piasy.com/img/201607/okhttp_full_process.png)

在realcall的execute方法中会调用     


    client.dispatcher().executed(this);//问题1  
    Response result = getResponseWithInterceptorChain(false);//问题2  
 
获得请求结果.    
现在看问题1  在这里面干了写什么   
其实就是 dispatcher记录任务而已 ，没有任何执行方法  
核心在问题2中  
她会  


    Interceptor.Chain chain = new ApplicationInterceptorChain(0, originalRequest, forWebSocket);
    return chain.proceed(originalRequest);
也就是生成拦截器 ，并用这个拦截器启动这个请求
继续进入proceed 可以看到
进入了ApplicationInterceptorChain的getresponse方法
开始构造HttpEngine    

    engine.sendRequest();//问题21
    engine.readResponse();//问题22
   
在问题21中其实就是  Rfc 标准的一种 实现  

    InternalCache responseCache = Internal.instance.internalCache(client);
    Response cacheCandidate = responseCache != null
        ? responseCache.get(request)
        : null;
        
就是看当前是否配置了cache   如果有cache   则在responseCache.get找 当前request的cache
这个过程 就是根据 Util.md5Hex(request.url().toString())的从map中取值cacheCandidate的过程 
当取到值后还要根据http cache的rfc标准  判断  是否合理能使用
new CacheStrategy.Factory(now, request, cacheCandidate).get();
在CacheStrategy中 这里会真正的判断和并处理当前的reponse cache和request（处理request是为了  当cache过期后还可以通过304  机制实现重用）；  

这里需要判断  当前的  cacheCOntrol    Expires等  （尤其要处理一种情况就是当cache过期了  要根据 etag和Last-Modified  等等  要在request 中添加参数）

      if (etag != null) {
        conditionalRequestBuilder.header("If-None-Match", etag);
      } else if (lastModified != null) {
        conditionalRequestBuilder.header("If-Modified-Since", lastModifiedString);
      } else if (servedDate != null) {
        conditionalRequestBuilder.header("If-Modified-Since", servedDateString);
      }

      Request conditionalRequest = conditionalRequestBuilder.build();

这是请求前的工作
现在开始发送请求

      httpStream = connect();
      httpStream.setHttpEngine(this);
这一部分的核心是StreamAllaction（辅助是ConnectionPool 和Route  RouteSelector）

    streamAllocation.newStream(client.connectTimeoutMillis(),
    client.readTimeoutMillis(), client.writeTimeoutMillis(),
    client.retryOnConnectionFailure(), doExtensiveHealthChecks);
解决的问题 是socket连接重用和  route
先是从连接池中找


     // Attempt to get a connection from the pool.
      RealConnection pooledConnection = Internal.instance.get(connectionPool, address, this);
      if (pooledConnection != null) {
        this.connection = pooledConnection;
        return pooledConnection;
      }
如果没有的话就看route可以重用嘛

     if (selectedRoute == null) {
      selectedRoute = routeSelector.next();
      synchronized (connectionPool) {
        route = selectedRoute;
      }
    }
    RealConnection newConnection = new RealConnection(selectedRoute);
    acquire(newConnection);
（这其实和一个dns解析 有关系也就是 一个域名对应多个ip  而且不一定所有的ip都是通的  建立连接的时候会尝试 所有的  直到通了为止

    RouteDatabase里的Set<Route> failedRoutes = new LinkedHashSet<>()）
弄完之后就是放如   

     Internal.instance.put(connectionPool, newConnection);
连接池中  方便下次继续使用
下一步 就是建立socket连接的过程

     newConnection.connect(connectTimeout, readTimeout, writeTimeout, address.connectionSpecs(),
        connectionRetryEnabled);
    routeDatabase().connected(newConnection.route());
跟进去 就是

       connectSocket(connectTimeout, readTimeout, writeTimeout, connectionSpecSelector);
继续

     try {
      Platform.get().connectSocket(rawSocket, route.socketAddress(), connectTimeout);
    } catch (ConnectException e) {
      throw new ConnectException("Failed to connect to " + route.socketAddress());
    }
    source = Okio.buffer(Okio.source(rawSocket));
    sink = Okio.buffer(Okio.sink(rawSocket));
连接socket（返回连接 是以Http1xStream Http2xStream）形式返回回来的
然后才是真正发送这个请求的过程

       httpStream.writeRequestHeaders(networkRequest);
       requestBodyOut = httpStream.createRequestBody(networkRequest, contentLength);
继续跟进

     httpEngine.writingRequestHeaders();
      String requestLine = RequestLine.get(
        request, httpEngine.getConnection().route().proxy().type());
    writeRequest(request.headers(), requestLine);

》》

    ** Returns bytes of a request header for sending on an HTTP transport. */
    public void writeRequest(Headers headers, String requestLine) throws IOException {
    if (state != STATE_IDLE) throw new IllegalStateException("state: " + state);
    sink.writeUtf8(requestLine).writeUtf8("\r\n");
    for (int i = 0, size = headers.size(); i < size; i++) {
      sink.writeUtf8(headers.name(i))
          .writeUtf8(": ")
          .writeUtf8(headers.value(i))
          .writeUtf8("\r\n");
    }
    sink.writeUtf8("\r\n");
    state = STATE_OPEN_REQUEST_BODY;
    }


读过程
就是通过这个stream构造出 newChunkedSink 或者newFixedLengthSink







到此 请求reponse的工作做完了
现在 如果是需要真正发送网络请求就也就是问题22

      networkResponse = new NetworkInterceptorChain(0, networkRequest).proceed(networkRequest);
》》

     engin.readResponse
》》

      // Write the request body to the socket.
      if (requestBodyOut != null) {
        if (bufferedRequestBody != null) {
          // This also closes the wrapped requestBodyOut.
          bufferedRequestBody.close();
        } else {
          requestBodyOut.close();
        }
        if (requestBodyOut instanceof RetryableSink) {
          httpStream.writeRequestBody((RetryableSink) requestBodyOut);
        }
      }

      networkResponse = readNetworkResponse();

》》

    Response readNetworkResponse() throws IOException {
    httpStream.finishRequest();

    Response networkResponse = httpStream.readResponseHeaders()
        .request(networkRequest)
        .handshake(streamAllocation.connection().handshake())
        .header(OkHeaders.SENT_MILLIS, Long.toString(sentRequestMillis))
        .header(OkHeaders.RECEIVED_MILLIS, Long.toString(System.currentTimeMillis()))
        .build();

    if (!forWebSocket) {
      networkResponse = networkResponse.newBuilder()
          .body(httpStream.openResponseBody(networkResponse))
          .build();
    }

    if ("close".equalsIgnoreCase(networkResponse.request().header("Connection"))
        || "close".equalsIgnoreCase(networkResponse.header("Connection"))) {
      streamAllocation.noNewStreams();
    }

    return networkResponse;
  }

解析和返回

      Response response = engine.getResponse();


     //tobe continue（已经 cache过程 请求重试过程）
      Request followUp = engine.followUpRequest();



### 3. cache管理




最后附上 相关的http请求cache的rfc内容
 ![image](https://raw.githubusercontent.com/liuyicheng3/learning-summary/master/images/http_cache.jpg)

### 每个状态的详细说明如下：

#### 1. Last-Modified  
在浏览器第一次请求某一个URL时，服务器端的返回状态会是200，内容是你请求的资源，同时有一个Last-Modified的属性标记(HttpReponse Header)此文件在服务期端最后被修改的时间，格式类似这样：  
Last-Modified:Tue, 24 Feb 2009 08:01:04 GMT  
客户端第二次请求此URL时，根据HTTP协议的规定，浏览器会向服务器传送If-Modified-Since报头(HttpRequest Header)，询问该时间之后文件是否有被修改过：  
If-Modified-Since:Tue, 24 Feb 2009 08:01:04 GMT  
如果服务器端的资源没有变化，则自动返回HTTP304（NotChanged.）状态码，内容为空，这样就节省了传输数据量。当服务器端代码发生改变或者重启服务器时，则重新发出资源，返回和第一次请求时类似。从而保证不向客户端重复发出资源，也保证当服务器有变化时，客户端能够得到最新的资源。  
注：如果If-Modified-Since的时间比服务器当前时间(当前的请求时间request_time)还晚，会认为是个非法请求  

#### 2. Etag工作原理  
HTTP协议规格说明定义ETag为“被请求变量的实体标记”（参见14.19）。简单点即服务器响应时给请求URL标记，并在HTTP响应头中将其传送到客户端，类似服务器端返回的格式：  
Etag:“5d8c72a5edda8d6a:3239″  
客户端的查询更新格式是这样的： 
If-None-Match:“5d8c72a5edda8d6a:3239″  
如果ETag没改变，则返回状态304。  
即:在客户端发出请求后，HttpReponse Header中包含Etag:“5d8c72a5edda8d6a:3239″  
标识，等于告诉Client端，你拿到的这个的资源有表示ID：5d8c72a5edda8d6a:3239。当下次需要发Request索要同一个URI的时候，浏览器同时发出一个If-None-Match报头(Http RequestHeader)此时包头中信息包含上次访问得到的Etag:“5d8c72a5edda8d6a:3239″标识。  
If-None-Match:“5d8c72a5edda8d6a:3239“  
,这样，Client端等于Cache了两份，服务器端就会比对2者的etag。如果If-None-Match为False，不返回200，返回304(Not Modified) Response。  

#### 3. Expires  
给出的日期/时间后，被响应认为是过时。如Expires:Thu, 02 Apr 2009 05:14:08 GMT  
需和Last-Modified结合使用。用于控制请求文件的有效时间，当请求数据在有效期内时客户端浏览器从缓存请求数据而不是服务器端.当缓存中数据失效或过期，才决定从服务器更新数据。  

#### 4. Last-Modified和Expires  
Last-Modified标识能够节省一点带宽，但是还是逃不掉发一个HTTP请求出去，而且要和Expires一起用。而Expires标识却使得浏览器干脆连HTTP请求都不用发，比如当用户F5或者点击Refresh按钮的时候就算对于有Expires的URI，一样也会发一个HTTP请求出去，所以，Last-Modified还是要用的，而且要和Expires一起用。  


#### 5. Etag和Expires  
如果服务器端同时设置了Etag和Expires时，Etag原理同样，即与Last-Modified/Etag对应的HttpRequestHeader:If-Modified-Since和If-None-Match。我们可以看到这两个Header的值和WebServer发出的Last-Modified,Etag值完全一样；在完全匹配If-Modified-Since和If-None-Match即检查完修改时间和Etag之后，服务器才能返回304.  


#### 6. Last-Modified和Etag  
分布式系统里多台机器间文件的last-modified必须保持一致，以免负载均衡到不同机器导致比对失败  
分布式系统尽量关闭掉Etag(每台机器生成的etag都会不一样)  
Last-Modified和ETags请求的http报头一起使用，服务器首先产生Last-Modified/Etag标记，服务器可在稍后使用它来判断页面是否已经被修改，来决定文件是否继续缓存  
过程如下:  
* 客户端请求一个页面（A）。  
* 服务器返回页面A，并在给A加上一个Last-Modified/ETag。  
* 客户端展现该页面，并将页面连同Last-Modified/ETag一起缓存。  
* 客户再次请求页面A，并将上次请求时服务器返回的Last-Modified/ETag一起传递给服务器。  
* 服务器检查该Last-Modified或ETag，并判断出该页面自上次客户端请求之后还未被修改，直接返回响应304和一个空的响应体。  


备注：   
* Last-Modified和Etag头都是由WebServer发出的HttpReponse Header，WebServer应该同时支持这两种头。  
* WebServer发送完Last-Modified/Etag头给客户端后，客户端会缓存这些头；  
* 客户端再次发起相同页面的请求时，将分别发送与Last-Modified/Etag对应的HttpRequestHeader:If-Modified-Since和If-None-Match。我们可以看到这两个Header的值和WebServer发出的Last-Modified,Etag值完全一样；  
* 通过上述值到服务器端检查，判断文件是否继续缓存；  


#### 7.关于 Cache-Control: max-age=秒 和 Expires  
Expires = 时间，HTTP 1.0 版本，缓存的载止时间，允许客户端在这个时间之前不去检查（发请求）  
max-age = 秒，HTTP 1.1版本，资源在本地缓存多少秒。  
如果max-age和Expires同时存在，则被Cache-Control的max-age覆盖。  
Expires 的一个缺点就是，返回的到期时间是服务器端的时间，这样存在一个问题，如果客户端的时间与服务器的时间相差很大，那么误差就很大，所以在HTTP 1.1版开始，使用Cache-Control: max-age=秒替代。  
Expires =max-age +   “每次下载时的当前的request时间”  
所以一旦重新下载的页面后，expires就重新计算一次，但last-modified不会变化   



