![page主页](https://github.com/liuyicheng3/learning-summary/blob/master/images/githubPage.png)   

https://liuyicheng3.github.io/  


# 1. 发布TechBolg方法
## 1.1 一键发布

        python HexoUtil.py 
        
可能需要修改目录参数  

        utils = HexoUtil('/Users/lyc/github/learning-summary','/Users/lyc/TechBlogWorkspace')

#### 后台做的事儿
1. 删除source/_posts目录里面的文章
2. 从learning-summary 中挑选出可以发布的markdown，拷贝进source/_posts。(前三行是以下格式的，才可以发布）

            title: 点赞爱心动画
            date: 2017-10-10 
            categories:

3. 自动化Step1 和 Step 2
4. 同时把TechBlogWorkspace 同步更新到github中去

## 1.2 手动发布
### Step1  
1. 把要新加入的文章拷贝进source/_posts 目录  
2. 同时在顶部添加分类信息，去掉Title   
 

    title: iOS入门
    date: 2015-11-01 20:10:33
    categories:
    - iOS
    tags:
    - ios入门
    
    ---

这个地方切换到markdown的编辑模式查看具体格式

### Step2 
生成html，并部署

    hexo clean #清理以前的生成的资源

    hexo generate #由markdown生成静态html资源

    hexo deploy  #将生成的html资源目录部署到GitHub

如果不想直接部署到github，可以先  
        
        hexo server -p 4000

这时候就可以先在 http://localhost:4000/ 查看了个人主页



# 2.设置内容 
## 2.1 github部署地址
_config.yml

    # Extensions
    ## Plugins: https://hexo.io/plugins/
    ## Themes: https://hexo.io/themes/
    theme: hexo-theme-next
    
    # Deployment
    ## Docs: https://hexo.io/docs/deployment.html
    deploy:
      type: git
      repository: git@github.com:liuyicheng3/liuyicheng3.github.io.git 
      branch: master  

## 2.2头像信息  
themes/hexo-theme-next/_config.yml 

    # Sidebar Avatar
    # in theme directory(source/images): /images/avatar.jpg
    # in site  directory(source/uploads): /uploads/avatar.jpg
    avatar: https://github.com/liuyicheng3/learning-summary/blob/master/images/avatar.jpg?raw=true
            


# 3. 本地环境
### Step1  安装nodejs
### Step2  安装hexo 
    npm install -g hexo

### 可能需要的其它资源
1. Github 本地密钥配置
2. hexo-theme-next主题（由于工程资源已经完全上传到 https://github.com/liuyicheng3/TechBlogWorkspace 所以clone下来就有了）   

         https://github.com/iissnan/hexo-theme-next


# 4. 参考资料
https://www.jianshu.com/p/c5dbd724f5ec  
https://www.jianshu.com/p/465830080ea9
