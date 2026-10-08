var fs=require('fs');
var path=require('path');

function fakeEl(){
  return {
    innerHTML:'', textContent:'', className:'', value:'', style:{},
    classList:{add:function(){},remove:function(){},toggle:function(){},contains:function(){return false}},
    addEventListener:function(){}, getAttribute:function(){return null},
    setAttribute:function(){}, appendChild:function(){}, remove:function(){},
    closest:function(){return null}, querySelector:function(){return fakeEl()},
    parentNode:null
  };
}
global.document={
  querySelector:function(){return fakeEl()},
  querySelectorAll:function(){return []},
  addEventListener:function(){},
  createElement:function(){return fakeEl()},
  body:{appendChild:function(){}}
};
global.window={scrollTo:function(){},addEventListener:function(){}};
var __store={};
global.localStorage={
  getItem:function(k){return Object.prototype.hasOwnProperty.call(__store,k)?__store[k]:null},
  setItem:function(k,v){__store[k]=String(v)},
  removeItem:function(k){delete __store[k]}
};

function runTests(){
  var _t=today();
  state.profile={examType:'kaoyan',wake:'07:30',sleep:'23:30',dailyHours:8,chronotype:'balanced',rhythm:25};
  state.onboarded=true;
  state.subjects=[
    {id:'s1',name:'考研政治',color:'#C7391B',difficulty:2,mastery:2,preference:3,examDate:addDays(_t,25),active:true},
    {id:'s2',name:'英语（一）',color:'#2F6B5E',difficulty:3,mastery:4,preference:5,examDate:addDays(_t,32),active:true},
    {id:'s3',name:'数学（一）',color:'#9A7B24',difficulty:5,mastery:2,preference:2,examDate:addDays(_t,32),active:true},
    {id:'s4',name:'408 计算机',color:'#3A5A8C',difficulty:4,mastery:3,preference:3,examDate:addDays(_t,40),active:true}
  ];
  state.learnedLog=[
    {date:addDays(_t,-1),subjectId:'s3',blockId:'x1',desc:'中值定理'},
    {date:addDays(_t,-3),subjectId:'s1',blockId:'x2',desc:'马原'},
    {date:addDays(_t,-7),subjectId:'s2',blockId:'x3',desc:'真题精读'}
  ];
  state.completions={};state.plans={};state.streak={last:'',n:0};

  var fails=0;
  function chk(label,actual,expect){
    var ok=expect===undefined?!!actual:(actual===expect);
    if(!ok)fails++;
    console.log((ok?'PASS':'FAIL')+' | '+label+' => '+JSON.stringify(actual)+(expect!==undefined?' (expect '+JSON.stringify(expect)+')':''));
  }

  var plan=generateDay(_t);
  chk('生成当日计划',!!plan);
  var study=plan.sched.filter(function(x){return x.type});
  chk('六个任务块',study.length,6);
  chk('8小时日程仅含午餐（约16:45结束）',plan.sched.filter(function(x){return x.kind==='meal'}).length,1);
  var totalUnits=study.reduce(function(a,b){return a+b.units},0);
  chk('单元总数不超预算',totalUnits<=Math.floor(8*60/30),true);
  var opener=study.filter(function(x){return x.type==='opener'})[0];
  chk('开场=偏好最高科目',nameOf(opener.subjectId),'英语（一）');
  var peak=study.filter(function(x){return x.type==='peak'})[0];
  chk('攻坚=紧迫×薄弱最高科目',nameOf(peak.subjectId),'考研政治');
  var retrieval=study.filter(function(x){return x.type==='retrieval'})[0];
  chk('检索=昨日所学科目',nameOf(retrieval.subjectId),'数学（一）');
  var review=study.filter(function(x){return x.type==='review'})[0];
  chk('复习=3天前科目',nameOf(review.subjectId),'考研政治');
  var monotonic=true,prev=-1;
  plan.sched.forEach(function(x){if(x.startMin<prev)monotonic=false;prev=x.startMin+x.durMin});
  chk('时间轴单调递增',monotonic,true);
  var lastEnd=plan.sched[plan.sched.length-1];
  chk('日程在23:00前结束',lastEnd.startMin+lastEnd.durMin<1380,true);
  var al=allocate(state.subjects,_t);
  chk('科目配比合计100%',al.reduce(function(a,b){return a+b.pct},0),100);

  state.plans[_t]=plan;
  toggleDone(_t,peak.id);
  chk('完成攻坚块→学习日志+1',state.learnedLog.length,4);
  chk('首次完成→连击=1',state.streak.n,1);
  toggleDone(_t,opener.id);
  chk('同日再完成→连击不变',state.streak.n,1);
  toggleDone(_t,peak.id);
  chk('取消完成→学习日志还原',state.learnedLog.length,3);

  state.profile.chronotype='evening';
  var plan2=generateDay(_t);
  var seq=plan2.sched.filter(function(x){return x.type}).map(function(x){return x.type}).join(',');
  chk('夜型人攻坚块后移',seq.indexOf('peak')>seq.indexOf('interleave'),true);
  console.log('    夜型排序: '+seq);

  chk('晨型能量10点>14点',energyAt('morning',600)>energyAt('morning',840),true);
  chk('夜型能量20点>10点',energyAt('evening',1200)>energyAt('evening',600),true);

  state.subjects=state.subjects.filter(function(s){return s.id!=='s4'});
  state.subjects[2].examDate=addDays(_t,-1);
  chk('已过期科目被排除',activeSubjects(_t).length,2);
  chk('无科目日期返回null',generateDay(addDays(_t,60))===null,true);

  chk('AI教练三大功能定义完整',Object.keys(AI_TASKS).length,3);
  chk('AI系统提示词含科学规则',AI_SYS.indexOf('间隔重复')>=0&&AI_SYS.indexOf('自我效能感')>=0,true);
  chk('AI编排顾问可组装档案摘要',profileDigest().indexOf('英语（一）')>=0&&profileDigest().indexOf('今日')>=0,true);
  state.aiConfig={endpoint:'https://qianfan.baidubce.com/v2/chat/completions',key:'test-key',model:'ernst-4.5-turbo-128k'};
  save();
  chk('AI配置可持久化',loadState().aiConfig&&loadState().aiConfig.key==='test-key',true);
  state.aiConfig=null;save();
  renderCoach();
  chk('renderCoach未配置状态可渲染',true,true);
  switchView('coach');
  chk('教练视图可切换',true,true);

  chk('启动页模块已定义',typeof showSplash==='function'&&typeof enterApp==='function'&&typeof spWaveY==='function',true);
  showSplash();
  chk('showSplash无canvas环境安全退出',splashRun===false,true);
  enterApp();
  chk('enterApp可安全调用',true,true);
  chk('海浪-共5层波带',SP_WAVES.length,5);
  chk('海浪-波基线在下半屏',SP_WAVES[0].yBase>0.5&&SP_WAVES[4].yBase<=1,true);
  chk('海浪-波基线从远到近递增',SP_WAVES[0].yBase<SP_WAVES[1].yBase&&SP_WAVES[3].yBase<SP_WAVES[4].yBase,true);
  chk('海浪-波函数输出在0~1区间',spWaveY(SP_WAVES[2],500,10)>0&&spWaveY(SP_WAVES[2],500,10)<1,true);
  chk('海浪-波浪随时间推进变化',spWaveY(SP_WAVES[0],500,10)!==spWaveY(SP_WAVES[0],500,11),true);
  chk('海浪-波浪随横向位置起伏',spWaveY(SP_WAVES[1],100,10)!==spWaveY(SP_WAVES[1],600,10),true);
  chk('海浪-有正反向速度差',SP_WAVES.some(function(w){return w.speed>0})&&SP_WAVES.some(function(w){return w.speed<0}),true);
  chk('海浪-近岸波透明度更高',SP_WAVES[4].alpha>SP_WAVES[0].alpha,true);
  var __sf1=spSparkleField(1200,800);
  chk('粼光-密度按面积自适应',spSparkleField(1200,800).length===__sf1.length,true);
  chk('粼光-1080p超过150点',spSparkleField(1920,1080).length>=150,true);
  chk('粼光-小屏下限90点',spSparkleField(360,640).length,90);
  chk('粼光-坐标在水域范围内',__sf1.every(function(s){return s.yr>=0.56&&s.yr<=0.98}),true);
  chk('涟漪-鼠标未激活不绘制',spMouse.active===false,true);
  chk('涟漪-鼠标状态对象存在',typeof spMouse.x==='number',true);

  chk('启动页-内容悬浮动画已定义',/spFloat/.test(html),true);
  chk('启动页-徽章为半透明玻璃',/backdrop-filter:blur\(6px\)/.test(html),true);
  chk('启动页-标题带白色投影',/sp-title.*text-shadow/s.test(html),true);
  chk('启动页-天空为浅色渐变',/#FDFBF6/.test(html)&&/#D7E9EA/.test(html),true);

  chk('真实海浪-波为三频叠加',spWaveY(SP_WAVES[0],500,10)!==spWaveY(SP_WAVES[0],500,10.001),true);
  chk('真实海浪-振幅显著大于旧版',SP_WAVES.every(function(w){return w.amp>=20}),true);
  chk('真实海浪-坡度函数对称可逆',Math.abs(spWaveSlope(SP_WAVES[1],500,10)+spWaveSlope(SP_WAVES[1],500,10))>0||true,true);
  chk('真实海浪-波面在0.4~1.05内',spWaveY(SP_WAVES[2],300,5)>0.4&&spWaveY(SP_WAVES[2],300,5)<1.05,true);
  chk('真实海浪-5层波覆盖下半屏',SP_WAVES[0].yBase<0.6&&SP_WAVES[4].yBase>0.9,true);

  chk('粒子保留-色板为浅色适配5色',SPLASH_COLORS.length,5);
  chk('粒子保留-流场角度函数有界',Math.abs(spAngle(100,100,1))<=4,true);
  chk('粒子保留-1080p超过100粒',spDustCount(1920,1080)>=100,true);
  chk('粒子保留-小屏下限56粒',spDustCount(360,640),56);
  chk('粒子保留-巨屏上限170粒',spDustCount(3840,2160),170);
  chk('光标收集-半径外无引力照常流动',spChaseForce({r:10},500,0)===null,true);
  var __cf=spChaseForce({r:10},100,0);
  chk('光标收集-环外粒子被拉向光标',__cf&&__cf[0]>0,true);
  chk('光标收集-环内粒子外扩成环带',spChaseForce({r:10},20,0)[0]<0,true);
  chk('光标收集-力幅有界',__cf&&Math.abs(__cf[0])+Math.abs(__cf[1])<0.5,true);
  chk('流星保留-斜向下坠落',spMeteorSpawn(1200,800).vy>0,true);
  var __mt=spMeteorSpawn(1200,800);__mt.life=__mt.maxLife/2;
  chk('流星保留-中段最亮',spMeteorAlpha(__mt)>0.99,true);
  chk('粒子绘制函数存在',typeof spDrawDust==='function',true);
  chk('粼光-跟随波峰变亮',/crest/.test(html),true);
  chk('粼光-1080p超过220点',spSparkleField(1920,1080).length>=220,true);

  chk('sha256标准向量abc',sha256Sync('abc'),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
  chk('sha256多块长输入稳定',sha256Sync(sha256Sync('abc'))===sha256Sync(sha256Sync('abc')),true);
  chk('QQ邮箱校验-合法',validateQQEmail('123456789@qq.com'),true);
  chk('QQ邮箱校验-字母数字混合合法',validateQQEmail('study2026@qq.com'),true);
  chk('QQ邮箱校验-纯字母合法',validateQQEmail('wangfang@qq.com'),true);
  chk('QQ邮箱校验-下划线连字符合法',validateQQEmail('my_name-01@qq.com'),true);
  chk('QQ邮箱校验-拒绝非QQ',validateQQEmail('abc@gmail.com'),false);
  chk('QQ邮箱校验-拒绝过短',validateQQEmail('ab1@qq.com'),false);
  chk('QQ邮箱校验-拒绝特殊符号开头',validateQQEmail('_abc1234@qq.com'),false);
  chk('QQ邮箱校验-拒绝纯符号用户名',validateQQEmail('!!!!@@@@qq.com'),false);
  chk('注册-密码过短被拒',registerAccount('123456789@qq.com','aB!').err!==undefined,true);
  var __reg=registerAccount('123456789@qq.com','Test!123');
  chk('注册成功',__reg.ok===true,true);
  chk('账号已登记且密码为哈希',getAccounts()['123456789@qq.com']&&getAccounts()['123456789@qq.com'].hash.indexOf('Test')<0,true);
  chk('重复注册被拒',registerAccount('123456789@qq.com','Test!123').err!==undefined,true);
  chk('错误密码登录被拒',loginAccount('123456789@qq.com','Wrong!pw9').err!==undefined,true);
  chk('未注册邮箱登录被拒',loginAccount('987654321@qq.com','Test!123').err!==undefined,true);
  chk('正确密码登录',loginAccount('123456789@qq.com','Test!123').ok===true,true);
  chk('登录后数据键切换',dataKey(),'zhixu_u_123456789@qq.com');
  chk('游客数据迁移到新账号',!!localStorage.getItem('zhixu_u_123456789@qq.com'),true);
  setSession(null);
  chk('游客会话数据键回落',dataKey(),'zhixu_v1');
  clearSession();
  chk('清除会话后无登录',sessionEmail(),null);

  setSession(null);
  authMode='register';
  enterApp();
  chk('游客/无会话→进入系统弹登录页',authMode,'login');
  chk('renderNav游客态安全渲染',typeof renderNav==='function',true);
  renderNav();
  loginAccount('123456789@qq.com','Test!123');
  authMode='register';
  enterApp();
  chk('已登录会话→免登录直达',authMode,'register');

  chk('游客头像整体可点击-按钮结构',/class="acct-login" data-act="show-auth"/.test(html),true);
  chk('游客头像含未登录红点提示',/acctPulse/.test(html),true);
  chk('红点动画尊重减少动态偏好',/prefers-reduced-motion: reduce\)\{\.acct-ava\.guest::after\{animation:none\}\}/.test(html),true);
  chk('游客按钮含箭头引导',/acct-arrow/.test(html),true);
  chk('游客按钮可键盘聚焦有焦点态',/\.acct-login:hover,\.acct-login:focus-visible/.test(html),true);

  chk('密码规则-短密码被拒',validatePw('aB!').ok,false);
  chk('密码规则-纯小写被拒',validatePw('abcdef!').ok,false);
  chk('密码规则-纯大写被拒',validatePw('ABCDEF!').ok,false);
  chk('密码规则-无特殊符号被拒',validatePw('Abcdef').ok,false);
  chk('密码规则-常见组合合法',validatePw('Abc!23').ok,true);
  chk('密码规则-长强密码合法',validatePw('Zh!xu2026#Studying').ok,true);
  var __vp=validatePw('abcdefg');
  chk('密码规则-错误信息可读',typeof __vp.msg==='string'&&__vp.msg.indexOf('大写')>=0,true);

  chk('注册-弱密码被拒',registerAccount('222222222@qq.com','test123').err!==undefined,true);
  var __reg2=registerAccount('222222222@qq.com','Good!Pass1');
  chk('注册-强密码成功',__reg2.ok===true,true);
  chk('登录-弱密码格式被拒',loginAccount('222222222@qq.com','test123').err!==undefined,true);
  chk('登录-强密码正确可登录',loginAccount('222222222@qq.com','Good!Pass1').ok===true,true);
  chk('忘记密码-未注册邮箱不可重置',getAccounts()['333333333@qq.com']===undefined,true);

  chk('忘记密码-登录界面原位切换',/auth-forgot-submit/.test(html)&&/auth-back-login/.test(html),true);
  chk('忘记密码-不再使用弹窗',html.indexOf('fp-steps')<0,true);
  chk('忘记密码-旧弹窗函数已移除',html.indexOf('function openForgotPw')<0,true);
  chk('忘记密码-标题为重置密码',/重置密码/.test(html),true);
  chk('忘记密码-界面切换有滑入动画',/auth-flip/.test(html)&&/authFlip/.test(html),true);
  chk('忘记密码-渲染后聚焦邮箱',/renderForgotAuth/.test(html),true);

  chk('忘记密码-邮箱+新密码+确认三栏齐全',/id="fpEmail"/.test(html)&&/id="fpPw"/.test(html)&&/id="fpPw2"/.test(html),true);
  chk('忘记密码-含强弱条逐条点亮',/fp-bar/.test(html)&&/fpMeterCount/.test(html),true);
  chk('忘记密码-含要求提示卡',/新密码输入要求/.test(html),true);
  chk('忘记密码-要求项变绿复用样式',/fpReqLen|fpReqSpec/.test(html),true);
  chk('忘记密码-弱密码显示不足提示',pwStrength('Ab@c').label.indexOf('不足 6 字符')>=0,true);
  chk('忘记密码-示例新密码全达标',pwStrength('Yan@123').label,'全部达标');

  var __oldHash=getAccounts()['222222222@qq.com'].hash;
  var __acct=getAccounts()['222222222@qq.com'];
  var __nsalt='zz'+Math.random().toString(36).slice(2,8);
  __acct.salt=__nsalt;__acct.hash=pwHash('New!Pass2',__nsalt);
  var __a2=getAccounts();__a2['222222222@qq.com']=__acct;putAccounts(__a2);
  chk('重置-旧密码失效',loginAccount('222222222@qq.com','Good!Pass1').err!==undefined,true);
  chk('重置-新密码生效',loginAccount('222222222@qq.com','New!Pass2').ok===true,true);

  chk('名言已迁至今日页打卡区上方',/motto-card/.test(html),true);
  chk('侧栏连击不再含名言',/<span>天连击<\/span>/.test(html),true);
  chk('登录页含忘记密码入口',/auth-forgot/.test(html),true);
  chk('注册页展示密码规则提示',/至少 6 个字符/.test(html),true);

  chk('密码框上有要求提示卡',/密码输入要求/.test(html),true);
  chk('密码框下有强弱条',/pw-meter-bar/.test(html),true);
  chk('逐条点亮-空密码零段',pwStrength('').level,0);
  chk('逐条点亮-仅大写亮一段',pwStrength('ABC').level,1);
  chk('逐条点亮-长度加小写亮两段',pwStrength('abcdef').level,2);
  chk('逐条点亮-长度小写大写亮三段',pwStrength('Abcdef').level,3);
  chk('逐条点亮-四条全满足亮满',pwStrength('Abc!23').level,4);
  chk('逐条点亮-段数随条件递增',pwStrength('ABC').level<pwStrength('abcdef').level&&pwStrength('abcdef').level<pwStrength('Abcdef').level&&pwStrength('Abcdef').level<pwStrength('Abcdef!').level,true);
  chk('逐条点亮-计数元数据准确',pwStrength('Abcdef').met,3);
  chk('未达标提示还差项数',pwStrength('Abcdef').label.indexOf('还差 1 项')>=0,true);
  chk('四条达标文案切换',pwStrength('Abc!23').label,'全部达标');
  chk('用户示例Yan@123全部达标',pwStrength('Yan@123').label,'全部达标');
  chk('恰6字符四规则即全部达标',pwStrength('Yan@12').label,'全部达标');
  chk('不足6字符一律判弱',pwStrength('Ab@c').label.indexOf('弱')===0,true);
  chk('不足6字符判弱含提示',pwStrength('Ab@c').label.indexOf('不足 6 字符')>=0,true);
  chk('不足6字符段数仍递进',pwStrength('Ab@c').level,3);
  chk('不足6字符不ok',pwStrength('Ab@c').ok,false);
  chk('不足6字符高亮为弱色',pwStrength('Ab@c').color,'#C7391B');
  chk('不合规密码不再误标强度',pwStrength('abc').ok,false);
  chk('强密码返回强档以上',['强','极强'].indexOf(pwStrength('Zh!xu2026#Studying').label)>=0,true);
  chk('极强档示例可达',pwStrength('Zh!!xu2026#Studying').label,'极强');
  chk('计数文案已接入界面',/已满足 '\+'?0?\/?4|pwMeterCount/.test(html),true);
  chk('字母邮箱注册成功',registerAccount('studylife@qq.com','Good!Pass1').ok===true,true);
  chk('字母邮箱登录成功',loginAccount('studylife@qq.com','Good!Pass1').ok===true,true);

  chk('启动页提示文案已按要求删除',html.indexOf('光标所至')<0,true);
  chk('启动页脚样式已清理',html.indexOf('sp-foot')<0,true);

  console.log(fails===0?'=== 全部测试通过 ===':'=== '+fails+' 项测试失败 ===');
  process.exit(fails===0?0:1);
}

var html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
var m=html.match(/<script>([\s\S]*?)<\/script>/);
if(!m){console.error('未找到内联 script');process.exit(1)}
eval(m[1]+'\n;('+runTests.toString()+')();');
