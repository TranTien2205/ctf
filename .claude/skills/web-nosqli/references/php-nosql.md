# PHP NoSQL — the `mongodb` extension's carriers

## `mongodb` — the extension

```php
$manager = new MongoDB\Driver\Manager("mongodb://localhost");
$query = new MongoDB\Driver\Query(["user" => $user, "pass" => $pass]);
$query = new MongoDB\Driver\Query(["user" => ["$ne" => null]]);
$query = new MongoDB\Driver\Query($filter);
$query = new MongoDB\Driver\Query($_GET);
$query = new MongoDB\Driver\Query($_POST);
$query = new MongoDB\Driver\Query(json_decode($body, true));
$query = new MongoDB\Driver\Query(json_decode($body));
$cursor = $manager->executeQuery("db.users", $query);
```

`MongoDB\Driver\Query` — the filter-array — `injection-points.md` —
`$user`/`$pass`/`$filter`/`$_GET`/`$_POST`/`json_decode` — the object-
carrier.

## `mongodb` — the `$`-key in the filter

```php
$query = new MongoDB\Driver\Query(["user" => ["$ne" => null]]);
$query = new MongoDB\Driver\Query(["user" => ["$gt" => ""]]);
$query = new MongoDB\Driver\Query(["user" => ["$regex" => "^a"]]);
$query = new MongoDB\Driver\Query(["$or" => [["user" => "a"], ["user" => "b"]]]);
$query = new MongoDB\Driver\Query(["$where" => "this.pass[0] == 'f'"]);
$query = new MongoDB\Driver\Query(["user" => ["$where" => "this.pass"]]);
$query = new MongoDB\Driver\Query(["$expr" => ["$eq" => [["$substrCP" => ["$pass", 0, 4]], "flag"]]]);
```

The `$`-key — `operators.md`.

## `mongodb` — the `$_GET`/`$_POST` carriers

```php
$query = new MongoDB\Driver\Query($_GET);
$query = new MongoDB\Driver\Query($_POST);
$query = new MongoDB\Driver\Query($_REQUEST);
$query = new MongoDB\Driver.Query($_COOKIE);
$query = new MongoDB\Driver.Query(array_merge($_GET, $_POST));
$query = new MongoDB\Driver.Query(array_merge($_GET, $_POST, $_COOKIE));
```

`$_GET`/`$_POST`/`$_REQUEST`/`$_COOKIE` — the superglobal —
`injection-points.md` — `user[$ne]=x` in `$_GET` — `{"user": {"$ne": "x"}}`
— the php-nest — the `[$ne]` is a bracket-key, `user[$ne]=x` →
`$_GET["user"]["$ne"] = "x"` — the php-nesting-carrier.

## `mongodb` — the `json_decode` — the object-carrier

```php
$filter = json_decode($body, true);     — assoc-array
$filter = json_decode($body);           — stdClass
$filter = json_decode($_GET["q"], true);
$filter = json_decode($_POST["q"], true);
$filter = json_decode($_COOKIE["q"], true);
$filter = json_decode(getallheaders()["x-filter"], true);
$filter = json_decode(file_get_contents("php://input"), true);
```

`json_decode` — the string-JSON — `carrier-json-deep.md` — `true` for
assoc-array, `false` for stdClass — `MongoDB\Driver\Query` takes either.

## `mongodb` — the `BulkWrite` — the write-side

```php
$bulk = new MongoDB\Driver\BulkWrite;
$bulk->insert(["user" => $user]);
$bulk->update(["user" => $user], ["$set" => ["role" => "admin"]]);
$bulk->update(["user" => $user], ["$set" => ["flag" => "x"]]);
$bulk->update(["user" => $user], ["$unset" => ["isLocked" => ""]]);
$bulk->update(["user" => $user], ["$inc" => ["balance" => 9999]]);
$bulk->update(["user" => $user], ["$rename" => ["flag" => "user"]]);
$bulk->update(["user" => $user], ["$push" => ["roles" => "admin"]]);
$bulk->update(["user" => $user], ["$addToSet" => ["perms" => "*"]]);
$bulk->update(["user" => $user], ["$pull" => ["bans" => "me"]]);
$bulk->update(["user" => $user], ["$mul" => ["score" => 2]]);
$bulk->update(["user" => $user], ["$min" => ["limit" => 0]]);
$bulk->update(["user" => $user], ["$max" => ["cap" => 999]]);
$bulk->update(["user" => $user], ["$currentDate" => ["ts" => true]]);
$bulk->update(["user" => $user], ["$bit" => ["flags" => ["and" => 15]]]);
$bulk->update(["user" => $user], ["$setOnInsert" => ["admin" => true]]);
$bulk->update(["user" => $user], ["$set" => ["role" => "admin"]], ["multi" => true]);
$bulk->update(["user" => $user], ["$set" => ["role" => "admin"]], ["upsert" => true]);
$bulk->update(["user" => $user], ["$set" => ["role" => "admin"]], ["arrayFilters" => []]);
$bulk->delete(["user" => $user]);
$bulk->delete(["user" => $user], ["limit" => 0]);
$bulk->delete(["user" => $user], ["limit" => 1]);
$manager->executeBulkWrite("db.users", $bulk);
```

`BulkWrite` — `update-injection.md`.

## `mongodb` — the `Command` — the admin-side

```php
$command = new MongoDB\Driver\Command(["usersInfo" => 1]);
$command = new MongoDB\Driver\Command(["listCollections" => 1]);
$command = new MongoDB\Driver\Command(["listDatabases" => 1]);
$command = new MongoDB\Driver\Command(["ping" => 1]);
$command = new MongoDB\Driver\Command(["buildInfo" => 1]);
$command = new MongoDB\Driver\Command(["collStats" => "users"]);
$command = new MongoDB\Driver\Command(["dbStats" => 1]);
$command = new MongoDB\Driver\Command(["serverStatus" => 1]);
$command = new MongoDB\Driver\Command(["connectionStatus" => 1]);
$command = new MongoDB\Driver\Command(["hostInfo" => 1]);
$command = new MongoDB\Driver\Command(["aggregate" => "users", "pipeline" => $pipeline]);
$command = new MongoDB\Driver\Command(["distinct" => "users", "key" => "role", "query" => $filter]);
$command = new MongoDB\Driver\Command(["count" => "users", "query" => $filter]);
$command = new MongoDB\Driver\Command(["find" => "users", "filter" => $filter]);
$command = new MongoDB\Driver\Command(["findAndModify" => "users", "query" => $filter, "update" => $update]);
$command = new MongoDB\Driver\Command(["mapReduce" => "users", "map" => $map, "reduce" => $reduce, "out" => "leak"]);
$command = new MongoDB\Driver\Command(["eval" => "function() { return 1; }"]);
$manager->executeCommand("db", $command);
```

`Command` — `mongodb-internals.md`.

## `mongodb` — the `aggregate` — the pipeline

```php
$command = new MongoDB\Driver\Command([
    "aggregate" => "users",
    "pipeline" => [
        ["$unionWith" => "flag"],
        ["$lookup" => ["from" => "flag", "localField" => "x", "foreignField" => "y", "as" => "f"]],
        ["$project" => ["flag" => 1]],
        ["$match" => ["flag" => ["$regex" => "^a"]]],
        ["$group" => ["_id" => null, "f" => ["$first" => "$flag"]]],
        ["$sort" => ["flag" => 1]],
        ["$limit" => 1],
        ["$skip" => 0],
        ["$count" => "n"],
        ["$facet" => ["a" => [["$match" => []]]]],
        ["$bucket" => ["groupBy" => "$p", "boundaries" => [0, 10]]],
        ["$bucketAuto" => ["groupBy" => "$p", "buckets" => 2]],
        ["$sortByCount" => "$u"],
        ["$set" => ["flag" => "$flag"]],
        ["$unset" => "secret"],
        ["$addFields" => ["f" => "$flag"]],
        ["$replaceRoot" => ["newRoot" => "$doc"]],
        ["$replaceWith" => "$doc"],
        ["$redact" => ["$cond" => ["if" => ["$eq" => ["$u", "admin"]], "then" => "$$KEEP", "else" => "$$PRUNE"]]],
        ["$out" => "leak"],
        ["$merge" => ["into" => "leak"]],
    ],
    "cursor" => new stdClass,
]);
```

`aggregate` — `aggregation.md`.

## `mongodb` — the `BSON` — the types

```php
new MongoDB\BSON\ObjectId("507f1f77bcf86cd799439011")
new MongoDB\BSON\Regex("^a", "i")
new MongoDB\BSON\UTCDateTime()
new MongoDB\BSON\Timestamp(0, 0)
new MongoDB\BSON\Decimal128("1.0")
new MongoDB\BSON\MinKey()
new MongoDB\BSON\MaxKey()
new MongoDB\BSON\Javascript("this.pass")
new MongoDB\BSON\Javascript("this.pass", ["x" => 1])
new MongoDB\BSON\Binary("...", 0)
new MongoDB\BSON\Symbol("x")
new MongoDB\BSON\DBPointer("x", new MongoDB\BSON\ObjectId())
new MongoDB\BSON\Int64(1)
new MongoDB\BSON\Undefined()
```

`BSON` — `mongodb-internals.md`.

## `mongodb` — the `readPreference`/`writeConcern` — the hints

```php
new MongoDB\Driver\ReadPreference(MongoDB\Driver\ReadPreference::PRIMARY)
new MongoDB\Driver\ReadPreference(MongoDB\Driver\ReadPreference::SECONDARY)
new MongoDB\Driver\WriteConcern(MongoDB\Driver\WriteConcern::MAJORITY)
new MongoDB\Driver\WriteConcern(1)
new MongoDB\Driver\WriteConcern(0)
```

`readPreference`/`writeConcern` — `mongodb-internals.md`.
