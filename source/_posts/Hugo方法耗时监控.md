title: Hugo方法耗时监控
date: 2018-3-2 
categories:
- Android
   
   
   
tags:   
- Android
- 性能监控


---

# 使用方法
1. 在Android Project的build.gradle添加dependence： 

		buildscript {
		    repositories {
		        jcenter()
		    }
		    dependencies {
		        classpath 'com.android.tools.build:gradle:2.3.3'
		        classpath 'com.jakewharton.hugo:hugo-plugin:1.2.1'//关键所在
		    }
		}

2. 在Module的build.gradle文件中添加Hugo Plugin的应用

		apply plugin:'com.jakewharton.hugo'//关键所在  

3. 在相应的方法前，添加@DebugLog

	import hugo.weaving.DebugLog;

	......

 	@DebugLog //关键所在
    private int add(int a, int b){
        return a+b;
    }


ps：调用Hugo后，Hugo自动生效。由于仅在Debug中生效，因此，可以不用关闭

# 扩展思维
## "apply plugin"的作用   
作用申明 构建的项目类型    

## butterknife原理

1. 第一步 定义注解类型：InjectView


		@Target(ElementType.FIELD)
		@Retention(RetentionPolicy.RUNTIME)
		public @interface InjectView {
		    /**控件的id*/
		    int id() default -1;
		}

2. 根据解析当前类的注解  

		/**根据注解自动解析控件*/
	    private void analyseInjectView(){
	        try {
	            Class clazz = this.getClass();
	            Field[] fields = clazz.getDeclaredFields();
	            for (Field field : fields){
	                InjectView injectView = field.getAnnotation(InjectView.class);
	                if (injectView != null){
	                    int id = injectView.id();
	                    Log.e("lyc", "id->"+id);
	                    if (id > 0){
	                        field.setAccessible(true);
	                        field.set(this, findViewById(id));
	                    }
	                }
	            }
	        }catch (Exception e){}
	    }

3. 在onCreate方法里面调用解析注解的方法 

			analyseInjectView()


实际上apply plugin 就会在编译时候添加上解析注解的逻辑  


## 类型值注解

		   interface GenderStatus {
		        /**
		         * 性别
		         */
		        String F = "F";
		        String M = "M";
		        String N = "N";


		        //使用@IntDef的使用 代替enum
		        //用 @IntDef "包住" 常量；
		        // @Retention 定义策略
		        // 声明构造器
		        @StringDef({F, M, N})
		        @Retention(RetentionPolicy.SOURCE)
		        @interface GenderType {
		        }
		    }


StringDef定义：  

			@Retention(SOURCE)
			@Target({ANNOTATION_TYPE})
			public @interface StringDef {
			    /** Defines the allowed constants for this element */
			    String[] value() default {};
			}


# 参考文章  
使用方法:http://blog.csdn.net/daihuimaozideren/article/details/78231983  
原理分析:http://blog.csdn.net/xxxzhi/article/details/53048476    
Retention、Target注解:  http://blog.csdn.net/limj625/article/details/70242773
