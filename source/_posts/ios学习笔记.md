title: iOS入门
date: 2015-11-01 20:10:33
categories:
- iOS
   
   
   
tags:   
- ios入门

---

# 第一课：熟悉OC语法

# 第二课：storyboard和 手写View

storyboard;

直接往上面拖放控件，然后按住ctr  把控件拖动到   @implementation，就相当于自动findview了，可以直接使用是这个控件了  

   @property (weak, nonatomic) IBOutlet UILabel *detailDescriptionLabel;


还有一种就是直接关联上点击事件
把控件直接拖动到这个申明方法上就可以了


    - (IBAction)showAlert:(id)sender;

这个的原理可以看看storyboard的文件内容就可以明白了，大致和android的类似



图片资源文件两种放法
1. 在Supporting  Files 同级添加一个Resources的包，里面直接放图片进去（可以只放三倍图）   

         UIImageView *imageView = [[UIImageView alloc] init];
            imageView.image = [UIImage imageNamed:@"home_banner.png"];	// 正常显示的图片
            
2. 在Assets.xcaseset里面右键新建New image set，然后手动把图片拖动到右边的一倍两倍三倍的框框中去 




storyboard  改成手写UI类型  

1. 第一步： 
- 删除storyboard文件  
- 编辑Supporting Files目录下的 .plist文件,
删除Main storyboard  file name这一项
2. 第二步：
    编辑AppDelegate

    
    - (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
        self.window = [[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
        [self.window makeKeyAndVisible];
        
        ViewController *__rootController = [[ViewController alloc] init];
        UINavigationController *__navCtrler = [[UINavigationController alloc] initWithRootViewController:__rootController];
        __navCtrler.navigationBarHidden = YES;
        self.window.rootViewController = __navCtrler;
      // Override point for customization after application launch.
        return YES;
    }


这个相当于Application的oncreate,在这里加载Entry activity


在ViewController里面手动往根View里面添加控件

    - (void)viewDidLoad {
        [super viewDidLoad];
        
        UILabel *firstLable=[[UILabel alloc]init];
        firstLable.frame=CGRectMake(0, 0, 100, 100);
        firstLable.backgroundColor = [UIColor whiteColor]; //设置lable背景颜色为黑色
    
        firstLable.text=@"第一级";
        firstLable.userInteractionEnabled = YES;
    
        [firstLable setTextColor:[UIColor greenColor]]; //设置文本字体颜色为白色
    
        [self.view addSubview:firstLable];
        UITapGestureRecognizer *singleTap = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapLable:)];
        [firstLable addGestureRecognizer:singleTap];
        
        // Do any additional setup after loading the view, typically from a nib.
    }


viewDidLoad 相当于Activity的oncreate，这里我们就是手写View，然后加到根View里面去 self.view
    [self.view addSubview:firstLable];



# 第三课：Viewcontroller  之间的跳转

在ViewController从一个Viewcontroller跳到另外一个SecondViewController

    -(void) tapLable:(UILabel *)sender{
        NSLog(@"进入第二级Controller");
        
        SecondViewController *controller = [[SecondViewController alloc] init];
        [self.navigationController pushViewController:controller animated:YES];
    }


在SecondViewController也是一样的写法

 返回第一个VIewCOntroller的方法

    [self.navigationController popViewControllerAnimated:YES];
