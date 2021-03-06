title: Github 教程    
date: 2015-11-01 20:10:33    
categories:    
- 工具    
       
       
       
tags:       
- github    
- 工具    
    
---


## 本地工程上传github
1. 首先在github上创建一个resp
2. 在本地工程里面引入 .gitignore
  * 在androidstudio 安装一个ignore 插件，可以生成部分ignore
  * 对于gradle目录的工程，每一个存在build.gradle目录都需要放一个.gitignore
  * .gitignore 内容 （对于android的gradle目录结构最完整的ignore文件）[原文件](https://raw.githubusercontent.com/liuyicheng3/learning-summary/master/files/.gitignore) 
        
        
        .gradle
        /local.properties
        /gradle.properties
        /.idea/workspace.xml
        /.idea/libraries
        .DS_Store
        /build
        /captures
        bin
        gen
        .settings
        .idea
        target
        *.iml
        *.key



4. touch README.md  》》生成 reamdme文件
    
5. git init当前工程 》》生成 git信息

6. git add -A 》》把当前工程除了ingore的添加到git里面

7. git commit 》》生成第一次的commit信息

8. git remote add origin git@github.com:liuyicheng3/NewRepo.git   》》设置当前git工程的远程分支

9. git push -u origin master 》》push 到github上去

10. Attention:一般android studio的默认ssh是 androidstudio自己的，所以这时候用android studio会提交不上去
  需要在settiings>vertion control> git里面吧 SSH excutable 由built-in 改成 native


##维护git文档方法
 * 可以网页里面直接弄，就不要通本地修改再提交，太麻烦。
 * 涉及到外部链接的图片文件，git库里面建对应的文件夹统一维护。
 * 对于图片贴的地址一定要是raw的，不要那个github上显示的地址
```markdown
[原文件](https://raw.githubusercontent.com/liuyicheng3/learning-summary/master/files/.gitignore) 
```

## 一般的git工作流程

### 版本管理 
### 按featrue 开发
### codereview及合并

## Markdown 快捷键
   1. 空两行，让后代码区域两个TAB
   2. shift tab  收回一个tab


##  Git 常见场景  

###  1. 不小心提交错了分支，把修改直接提交到master里面了

  git log  查到提交前的versioncode
  git revert 123dadafa     revert到这个节点
	git push --force   强制用本地的版本覆盖git上的版本

git  reset  和 git revert区别 http://www.cnblogs.com/wanqieddy/archive/2013/05/14/3077689.html


### 2. git 舍弃本地的修改   

      git checkout . && git clean -xdf

### 3. git 合并分支的冲突   

解决冲突后需要   

      git rebase --continue   

### 4. git 生成patch  

当前还没提交，生成当前修改的patch 

      git diff  > 1.patch    

生成已经提交的几次记录的patch   

      git log    //查看需要生成到那个提交日志的patch
      git format-patch -3     // 从master往前3个提交的内容，可修改为你想要的数值
      git format-patch e795fefabc   //生成‘e795fefabc’这次提交的patch


### 5. git删除已有的记录    

修改git commit 除了 git commit --amend 还有 git commmit rebase, reset,   

https://blog.csdn.net/tangkegagalikaiwu/article/details/8542827/


### 6. 打 tag   

git tag   
git checkout v1.1.8   
 git push origin --tags   

### 6. review流程常用的命令  

git commit   
git commit --amend     
git push origin HEAD:refs/for/master    
git reset --soft ****    -> 这个地方的"****"要填写需要回滚的id（短的那个，不要长的）    
![prepare](https://github.com/liuyicheng3/learning-summary/blob/master/history/git_01.jpeg?raw=true) 

git cherry-pick ****************   -> 当前在master分支，要把master分支的一个修改也提到release分支 

1. 先在master上查看这次提交的Change-Id:*************  (这个是长的那个不是短的)  
2. 切换到release分支，git cherry-pick *************  

#### 参考资料   

http://blog.csdn.net/kevinx_xu/article/details/11660915







