# UnEarthly Shop — HackTheBox (web)

Flag: recorded in `challenges/unearthly_shop/state.json` via `tools/hooks.py pre-flag`
(live response, `GET /admin/`).
Assistance: self-solved. phpggc was used to generate the Monolog gadget; no
writeup search.

## Layout

One container: nginx → php-fpm 7.4, plus mongod with `--noauth`. `config/nginx.conf`
serves `/www/frontend` at `/` and aliases `/admin` to `/www/backend/`. The flag is
`/root/flag`, readable only through the setuid binary `/readflag`, so the chain
has to end in command execution.

`entrypoint.sh` replaces `[REDACTED]` in `config/schema/users.json` with a random
16-character password and imports it — **in plaintext**. The same document's
`access` field is a PHP-serialized array:

```
a:4:{s:9:"Dashboard";b:1;s:7:"Product";b:1;s:5:"Order";b:1;s:4:"User";b:1;}
```

which is the first sign that something calls `unserialize` on stored data.

## 1. Aggregation pipeline injection — `frontend/Database.php:34`

```php
public function query($collection, $query)
{
    $collection = $this->db->$collection;
    $cursor = $collection->aggregate($query);
```

`ShopController::products` json_decodes the request body and passes it straight
in, so `POST /api/products` controls the **entire pipeline**, not just a filter.
`$unionWith` reads any other collection:

```json
[{"$limit":1},{"$unionWith":"users"},{"$match":{"username":{"$exists":true}}}]
```

returned the admin document with the plaintext password and the serialized
`access` string.

This is worth separating from ordinary NoSQL injection: a controlled *pipeline*
also has write stages. `$merge` and `$out` write to any collection, which later
turned out to be the only way back in after the admin panel locked itself.

## 2. Writing the unserialize input

`AuthController::login` does `$_SESSION['access'] = $login->access`, and
`UserModel.php:9` does `unserialize($_SESSION['access'] ?? '')` in its
constructor — which runs on every backend request, since `Controller::__construct`
builds a `UserModel` unconditionally.

`POST /admin/api/users/update` passes the decoded JSON straight to
`updateUser`, which does `$set: $data`. Only `_id`, `username` and `password`
are checked for presence, so any other field — including `access` — is written
verbatim. The new value reaches `unserialize` on the request after the next
login.

## 3. The autoloader supplies the gadget

The backend's vendor tree holds only `mongodb`, `symfony/polyfill-php80` and
`jean85` — no gadget. The frontend's holds `monolog 2.9.1`, `guzzle 6.5.8` and
`aws-sdk-php 3.33.4`. They are separate Composer installs in separate directories.

`backend/index.php:5`:

```php
spl_autoload_register(function ($name) {
    ...
    } elseif (preg_match('/_/', $name)) {
        $name = preg_replace('/_/', '/', $name);
    }
    $filename = "/${name}.php";
    if (file_exists($filename)) { require $filename; }
```

An underscore becomes a slash and the result is required as an **absolute
path**. PHP invokes the autoloader for every unknown class name it meets while
unserializing, so making the first element of the payload an object of class
`www_frontend_vendor_autoload` requires `/www/frontend/vendor/autoload.php`.
That registers the frontend's Composer autoloader, and the Monolog classes in
the second element then resolve normally. The primer class itself stays
undefined and becomes `__PHP_Incomplete_Class`, which is harmless.

## 4. Gadget

`phpggc Monolog/RCE1 system /readflag`, then wrapped:

```
a:2:{i:0;O:28:"www_frontend_vendor_autoload":0:{}i:1;<gadget>}
```

Wrapping breaks the gadget unless the reference indices are fixed. The array and
the primer object are two referenceable values inserted before the gadget, so
every `r:`/`R:` inside it shifts by exactly two — `r:2` became `r:4`. Measured
with `php -r` on an equivalent stub graph rather than assumed:

```
standalone: O:1:"A":1:{s:1:"s";O:1:"B":3:{s:1:"h";r:1; ...
wrapped   : a:2:{i:0;O:1:"P":0:{}i:1;O:1:"A":1:{s:1:"s";O:1:"B":3:{s:1:"h";r:3; ...
```

The gadget fires from `__destruct`, i.e. during shutdown, so `system()` output is
appended to the response body. `GET /admin/` returned the flag: `/admin/` is
`AuthController@index`, which is not privileged and so is not affected by the
broken access array.

## Traps

* The pipeline is fully controlled, not just a query document — check for
  `aggregate()` rather than `find()`, because the write stages change what is
  possible.
* Prepending anything to a phpggc payload invalidates its `r:` indices.
* Protected property names carry NUL bytes; they survive JSON (`\u0000`) and
  BSON, but a payload pasted through a terminal loses them silently.
* **Overwriting `access` locks the admin panel.** `Controller::__construct` does
  `if (!$this->access[$controller])`, and the poisoned array has no `User` key,
  so `POST /admin/api/users/update` — the route that wrote the payload — starts
  answering with a redirect to `Access Denied`. There is no way back through the
  panel; the restore has to go through `$merge` on the unauthenticated pipeline
  injection.

## Cleanup — not completed

The admin document was left holding the gadget. The first restore attempt failed
for the reason above (the update route was no longer reachable), and the second,
through `$merge` on `/api/products`, never got a connection: the instance stopped
answering on every path, including `/`, before it ran. What is left behind, in an
ephemeral container, is one user document whose `access` field executes
`/readflag` on each backend request.

The ordering mistake is worth recording: the payload should have carried the
original four access keys alongside the gadget — an array with `Dashboard`,
`Product`, `Order` and `User` set plus the gadget at another index would have
kept the panel usable and left a one-request restore available.
