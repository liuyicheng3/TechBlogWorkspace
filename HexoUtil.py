# coding=utf-8
import os,shutil,sys
import logging
import time

# 通过下面的方式进行简单配置输出方式与日志级别
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("Hexo")

# 指定logger输出格式
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

# 控制台日志
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter  # 也可以直接给formatter赋值

class HexoUtil(object):
    def __init__(self,markdown_src_dir,hexo_workspace_dir):
        self.markdown_src_dir = markdown_src_dir
        self.hexo_workspace_dir = hexo_workspace_dir

    def check_if_ready(self, file_path):
        if not file_path.lower().endswith('.md'):
            return False
        match = False
        need_modify = False
        with open(file_path,'rb') as mark_down_file :
            lines_origin = mark_down_file.readlines()
            lines = map(lambda i:i.replace("\n", "").strip(),lines_origin)
            lines = filter(lambda i: len(i) > 0, lines)
            if len(lines) > 3 and lines[0].startswith('title: ') and lines[1].startswith('date: ') and lines[2].startswith('categories:') :
                for i in range(0,len(lines_origin)):
                    if lines_origin[i].replace("\n", "").strip().endswith('---'):
                        break
                    else:
                        if not lines_origin[i].endswith('  \n'):
                            lines_origin[i] = lines_origin[i].replace("\n", '    \n')
                            need_modify = True
                        if 'tags:'in lines_origin[i]:
                            lines_origin[i] = '   \ntags   \n'
                            need_modify = True
                match = True

        if need_modify:
            logger.info('%s的hexo 标签有问题，自动调整' % (os.path.basename(file_path)))
            with open(file_path,'wb') as mark_down_file :
                mark_down_file.writelines(lines_origin)

        return match


    def find_all_post(self,path):
        total_markdown = 0
        result = []
        if os.path.exists(path):
            files = os.listdir(path)
            for file_item in files:
                if os.path.isfile(os.path.join(path,file_item)):
                    if file_item.lower().endswith('.md'):
                        total_markdown += 1
                        if self.check_if_ready(os.path.join(path,file_item)):
                            result.append(os.path.join(path,file_item))
                else:
                    sub_total , sub_result = self.find_all_post(os.path.join(path,file_item))
                    total_markdown += sub_total
                    result.extend(sub_result)
        return total_markdown,result

    def analysis(self):
        return self.find_all_post(self.markdown_src_dir)

    def move2hexo(self,tobepublish_aar):
        if not os.path.exists(self.hexo_workspace_dir) :
            return False
        if os.path.exists(os.path.join(self.hexo_workspace_dir,'source/_posts')):
            shutil.rmtree(os.path.join(self.hexo_workspace_dir,'source/_posts'))
        os.mkdir(os.path.join(self.hexo_workspace_dir,'source/_posts'))
        for item in tobepublish_aar:
            new_path = os.path.join(self.hexo_workspace_dir,'source/_posts',os.path.basename(item))
            shutil.copy(item,new_path)
        logger.info('hexo 需要生成%d篇blog' % (len(tobepublish_aar)))
        return True


utils = HexoUtil('/Users/lyc/github/learning-summary','/Users/lyc/TechBlogWorkspace')
total,ready_aar = utils.analysis()
confirm_publish = raw_input('确认发布到 %s 的技术博客?(Y/N)\n'%utils.hexo_workspace_dir)
if cmp(confirm_publish.lower(),'y') != 0:
    logger.info('取消发布！！！')
    sys.exit(0)

logger.info('一共%d篇markdown，%d篇可以发布'%(total,len(ready_aar)))
for item in ready_aar:
    logger.info(item)
if utils.move2hexo(ready_aar):
    os.chdir(utils.hexo_workspace_dir)
    logger.info(os.getcwd())
    os.system('hexo clean')
    os.system('hexo generate')
    os.system('hexo deploy')
    os.system('git add -A')
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    os.system('git commit -m \'%s更新技术博客\''%dt)
    os.system('git push')
    os.system('hexo server -p 4000')
logger.info('Done')





