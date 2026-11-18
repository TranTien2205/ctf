# Historic CVEs — the deserialization canon worth knowing

## Why a CVE index matters

CTF challenges re-skin known CVEs. The CVE name is a search key for a
working gadget — a "custom" app that is really a vulnerable library version
will usually match a published chain.

## The Java canon

| CVE | Sink | The bug |
|---|---|---|
| CVE-2015-7501/4852 | commons-collections | InvokerTransformer — the CC1 family birth |
| CVE-2015-6420 | commons-collections | alternate CC path |
| CVE-2017-7504 | jboss | HTTPServerILServlet deserialization |
| CVE-2017-12149 | jboss | ReadOnlyAccessFilter deserialization |
| CVE-2016-3510 | weblogic | the WLS deserialization family |
| CVE-2018-2628/2893 | weblogic | T3/RMI deserialization |
| CVE-2015-8103 | jenkins | CLI deserialization |
| CVE-2017-1000353 | jenkins | remoting deserialization |
| CVE-2016-9299 | slf4j/others | various |
| CVE-2018-7489 | jackson | polymorphic type → JdbcRowSetImpl |
| CVE-2019-12384 | jackson | logback-jackson gadget |
| CVE-2020-8840 | jackson | xbean-reflect gadget |
| CVE-2013-7285 | xstream | dynamic-proxy → EventHandler → ProcessBuilder |
| CVE-2017-9805 | xstream | XML → convertToJava RCE |
| CVE-2020-26217/26258/26259 | xstream | denylist bypasses per release |
| CVE-2016-4438 | struts2 | REST plugin XStream deser |
| CVE-2017-5638 | struts2 | (OGNL, not deser — but same sink family) |
| CVE-2021-44228 | log4j2 | `${jndi:ldap://}` — the JNDI shape |

## The PHP canon

| CVE | Sink | The bug |
|---|---|---|
| CVE-2016-7124 | PHP core | `__wakeup` prop-count lie → skips __wakeup |
| CVE-2018-19296/19520 | PHPMailer | phar:// via `setLanguage`/`image` path |
| CVE-2019-11043 | PHP-FPM | (env-pathinfo, not deser) |
| CVE-2020-9478 | laravel | the env-file-read → APP_KEY leak chain |
| CVE-2021-3129 | laravel | Ignition RCE (facade/ignition) |
| CVE-2018-15133 | laravel | APP_KEY → unserialize cookie RCE |
| CVE-2017-16943 | wordpress | phar:// via WP_Image_Editor_Imagick |
| CVE-2019-8942/8943 | wordpress | crop-image path → phar |
| CVE-2018-20718 | wordpress | phar via Gd_Image |
| CVE-2017-1414 | phpmyadmin | session deser |
| CVE-2018-10561 | magento | unserialize on session |
| CVE-2016-4010 | magento | unserialize cookie → RCE |
| CVE-2020-15151 | drupal | phar via PEAR_ArchiveTar |
| CVE-2019-6339 | drupal | phar via Tar.php |
| CVE-2020-35749 | joomla | unserialize session |
| CVE-2020-28052 | phpmyadmin | deser via UserPreferences |

## The Python canon

| CVE | Sink | The bug |
|---|---|---|
| CVE-2019-6446 | numpy | `allow_pickle` default (changed in 1.16.3+) |
| CVE-2020-1747 | PyYAML | `full_load` `!!python/object/new` |
| CVE-2020-14343 | PyYAML | `full_load` `!!python/object/new` (the deeper one) |
| CVE-2017-16618 | gensim | `load` → pickle |
| CVE-2020-13092 | scikit-learn | `joblib.load` → pickle |
| CVE-2020-10744 | python-psutil | |
| CVE-2020-13976 | `furl`/others | |
| CVE-2021-28872 | celery | pickle task deser |
| various | `pyyaml.load` | `!!python/object/apply` — the classic |

## The .NET canon

| CVE | Sink | The bug |
|---|---|---|
| CVE-2019-18935 | Telerik UI for ASP.NET | `.rau` upload → `TypeNameHandling` deser → RCE |
| CVE-2017-9822 | DotNetNuke | cookie deser → `ObjectDataProvider` |
| CVE-2018-18931 | Sitecore | `Shell` deser |
| CVE-2020-0688 | Exchange | `validationKey` static → ViewState RCE |
| CVE-2020-17144 | Exchange | `machineKey` static → RCE |
| CVE-2021-27065 | Exchange | `ProxyLogon` → machineKey → RCE |
| CVE-2015-6099 | .NET WCF | `NetDataContractSerializer` |
| CVE-2019-16357 | Sitecore | deser |

## The Ruby canon

| CVE | Sink | The bug |
|---|---|---|
| CVE-2013-0156 | rails | `YAML.load` XML params → object deser |
| CVE-2013-0333 | rails | JSON params → YAML coerce |
| CVE-2016-2098 | rails | ActionView render → deser |
| CVE-2019-5420 | rails | `secret_key_base` derivations → Marshal |
| CVE-2020-8164 | rails | `signed`/`encrypted` cookie deser |
| CVE-2019-16370 | grape | Marshal.load on params |
| CVE-2020-8166/8167 | rails | |

## The Node canon

| CVE | Sink | The bug |
|---|---|---|
| CVE-2017-5941 | node-serialize | `$$ND_FUNC$$` IIFE → RCE |
| CVE-2017-16082 | `wet/`packages | post-install deser |
| CVE-2018-16472 | `express-cart` | cookie deser |
| CVE-2018-3774 | `node-serialize` family | |
| CVE-2020-7660/7662 | serialize-javascript | regex-fn revive |
| CVE-2021-23565 | `wicked` / `devalue` | |

## The cross-cutting "gadget publication" papers

These aren't CVEs — they're the research that MADE the gadgets:

- **Marshalling Pickles** (Frohoff/Lawrence, 2015) — the Java CC chain paper
- **PHP Object Injection** (Esser, 2009+) — POP chains + `__wakeup` suppression
- **ysoserial** (Frohoff, 2015+) — the Java catalog
- **ysoserial.net** (pwntester, 2017+) — the .NET catalog
- **phpgcc** (ambionics, 2016+) — the PHP catalog
- **Universal Rails RCE** (Espionage/many) — the ERB-proxy Marshal/YAML chain
- **ViewState attacks** (many) — the machineKey recipe
- **Log4Shell** (CVE-2021-44228) — the JNDI-in-a-string shape
- **Jackson polymorphic** — the `@type`/default-typing family
- **JNDI bypasses** (many) — the 8u191+ BeanFactory/serialized-data routes

## The re-skin reflex

A "custom" challenge app is often a named library version + thin glue. The
version fingerprint (composer.lock/pom.xml/package-lock/`serialVersionUID`
leak) → the CVE that covers it → the published gadget — faster than
building a fresh chain.

## Falsifier — when the CVE doesn't apply

- The lib version is patched (check the lockfile, not the CVE title)
- The vulnerable code path isn't reached by the endpoint
- A filter/Binder/`allowed_classes` blocks the gadget class
- The delivery channel (cookie vs body) doesn't reach the sink the CVE needs
