# coding=utf-8
import os,sys
import logging
import time


# 通过下面的方式进行简单配置输出方式与日志级别
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("Github")

# 指定logger输出格式
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

# 控制台日志
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter  # 也可以直接给formatter赋值
local_dir = os.path.basename(os.getcwd())
logger.info(local_dir)
os.system('git status')
confirm_publish = raw_input('确认把%s发布到Github?(Y/N)\n'%local_dir)
if cmp(confirm_publish.lower(),'y') != 0:
    logger.info('取消发布！！！')
    sys.exit(0)
dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
os.system('git add -A')
os.system('git commit -m \'%s更新技术博客\''%dt)
os.system('git push')
logger.info('Done')









