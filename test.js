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

  chk('启动页模块已定义',typeof showSplash==='function'&&typeof enterApp==='function'&&typeof spAngle==='function',true);
  showSplash();
  chk('showSplash无canvas环境安全退出',splashRun===false,true);
  enterApp();
  chk('enterApp可安全调用',true,true);
  chk('粒子流场角度函数有界',Math.abs(spAngle(100,100,1))<=4,true);
  chk('启动页粒子色板为浅色适配5色',SPLASH_COLORS.length,5);

  console.log(fails===0?'=== 全部测试通过 ===':'=== '+fails+' 项测试失败 ===');
  process.exit(fails===0?0:1);
}

var html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
var m=html.match(/<script>([\s\S]*?)<\/script>/);
if(!m){console.error('未找到内联 script');process.exit(1)}
eval(m[1]+'\n;('+runTests.toString()+')();');
