title: 快速打包方案
date: 2015-11-01 20:10:33
categories:
- Android快速打包
   
tags   
- 打包
- Android
---


# 往apk文件里面动态添加信息的两种方法。 
（都需要保留安装时候的apk文件）

1. 方案一：往meta_info里面添加文件,写入参数信息
2. 方案二：在apk这个文件的comment信息里面添加需要传入的信息  



## 方案一：  
参考：http://tech.meituan.com/mt-apk-packaging.html   
主要代表：美团  
原理：meta_info（里面存的就是签名信息）里面的文件不参与签名，修改后，apk不需要签名 

## 方案二：  
参考：http://blog.csdn.net/kongpinde/article/details/51518466  
主要代表：天猫、豌豆荚   
原理：apk就是一个zip压缩包。而zip包有个comment区域，可以往里面写入信息，而不对apk的安装产生影响   
zip 文件的末尾有一个 Central Directory Record 区域，其末尾包含一个 File comment 区域，可以存放一些数据，所以 File comment 是 zip 文件一部分，如果可以正确的修改这个部分，就可以在不破坏压缩包、不用重新打包的的前提下快速的给 Apk 文件写入自己想要的数据。

comment 是在 Central Directory Record 末尾储存的，可以将数据直接写在这里，下表是 header 末尾的结构。
 ![image](https://raw.githubusercontent.com/liuyicheng3/learning-summary/master/images/zip_comment.png)
从表中可以看到定义 comment 长度的字段位于 comment 之前。

这里我们需要自定义 comment，在自定义 comment 内容的后面添加一个区域储存 comment 的长度，结构如下图。
![image](https://raw.githubusercontent.com/liuyicheng3/learning-summary/master/images/zip_comment_structure.png)

### Server动态生成apk 
这一部分可以在本地或服务端进行，需要定义一个长度为 2 的 byte[] 来储存 comment 的长度，直接使用 Java 的 api 就可以把 comment 和 comment 的长度写到 Apk 的末尾，代码如下：

    	public static void writeApk(File file, String comment) {
    		ZipFile zipFile = null;
    		ByteArrayOutputStream outputStream = null;
    		RandomAccessFile accessFile = null;
    		try {
    			zipFile = new ZipFile(file);
    			String zipComment = zipFile.getComment();
    			// 判断comment区域是否已经有数据了
    			if (zipComment != null)
    				return;
    			byte[] byteComment = comment.getBytes();
    			outputStream = new ByteArrayOutputStream();
    			// 将数据写入输出流
    			outputStream.write(byteComment);
    			// 紧接着写入数据大小
    			outputStream.write(short2Stream((short) byteComment.length));
        			byte[] data = outputStream.toByteArray();
    			accessFile = new RandomAccessFile(file, "rw");
    			// 跳到comment区域
    			accessFile.seek(file.length() - 2);
    			// 先写入数据大小
    			accessFile.write(short2Stream((short) data.length));
    			// 写入数据
    			accessFile.write(data);
    		} catch (Exception e) {
    			e.printStackTrace();
    		} finally {
    			try {
    				if (zipFile != null)
    					zipFile.close();
    				if (outputStream != null)
    					outputStream.close();
    				if (accessFile != null)
    					accessFile.close();
    			} catch (Exception e) {
    				e.printStackTrace();
    			}
    		}
    	}
    	private static byte[] short2Stream(short data) {
    		ByteBuffer buffer = ByteBuffer.allocate(2);
    		buffer.order(ByteOrder.LITTLE_ENDIAN);
    		buffer.putShort(data);
    		buffer.flip();
    		return buffer.array();
    	}



### 客户端解析apk数据：


        private static String readApk(Context context) {
    		// 获取文件路径
    		File file = new File(context.getPackageCodePath());
    		byte[] bytes = null;
    		RandomAccessFile accessFile = null;
    		try {
    			accessFile = new RandomAccessFile(file, "r");
    			long index = accessFile.length();
    			bytes = new byte[2];
    			// 获取comment文件的位置
    			index = index - bytes.length;
    			accessFile.seek(index);
    			// 获取comment中写入数据的大小byte类型
    			accessFile.readFully(bytes);
    			// 将byte转换成大小
    			int contentLength = stream2Short(bytes, 0);
    			// 创建byte[]数据大小来存储写入的数据
    			bytes = new byte[contentLength];
    			index = index - bytes.length;
    			accessFile.seek(index);
    			// 读取数据
    			accessFile.readFully(bytes);
    			return new String(bytes, "utf-8");
    		} catch (Exception e) {
    			e.printStackTrace();
    		} finally {
    			if (accessFile != null) {
    				try {
    					accessFile.close();
    				} catch (IOException e) {
    					e.printStackTrace();
    				}
    			}
    		}
    		return null;
    	}
    

    	private static short stream2Short(byte[] stream, int offset) {
    		ByteBuffer buffer = ByteBuffer.allocate(2);
    		buffer.order(ByteOrder.LITTLE_ENDIAN);
    		buffer.put(stream[offset]);
    		buffer.put(stream[offset + 1]);
    		return buffer.getShort(0);
    	}

# apk的安装过程
1. 复制APK安装包到data/app目录下（所以安装完成后，即使把sd卡中的apk删除也没关系）;
2. 解压并扫描安装包，把dex文件(Dalvik字节码)保存到dalvik-cache目录;
3. 并data/data目录下创建对应的应用数据目录。


## 应用安装涉及到如下几个目录：        

system/app ---------------系统自带的应用程序，获得adb root权限才能删除

data/app  ---------------用户程序安装的目录。安装时把                                                                                                      apk文件复制到此目录
data/data ---------------存放应用程序的数据
data/dalvik-cache--------将apk中的dex文件安装到dalvik-cache目录下(dex文件是dalvik虚拟机的可执行文件,其大小约为原始apk文件大小的四分之一)



## app卸载

删除安装过程中在上述三个目录下创建的文件及目录。



