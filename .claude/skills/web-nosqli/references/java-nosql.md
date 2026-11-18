# Java NoSQL — the `mongo-java-driver`/`spring-data-mongodb` carriers

## `mongo-java-driver` — the `Bson`/`Document`/`BasicDBObject`

```java
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import org.bson.Document;
import com.mongodb.BasicDBObject;
import com.mongodb.DBObject;
import com.mongodb.client.model.Filters;

MongoCollection<Document> users = db.getCollection("users");
users.find(new Document("user", new Document("$ne", null)))
users.find(new Document("user", new Document("$gt", "")))
users.find(new Document("user", new Document("$regex", "^a")))
users.find(new Document("user", new Document("$regex", ".*")))
users.find(new Document("user", new Document("$in", Arrays.asList("a", "b"))))
users.find(new Document("user", new Document("$nin", Arrays.asList("a", "b"))))
users.find(new Document("user", new Document("$exists", true)))
users.find(new Document("user", new Document("$type", "string")))
users.find(new Document("user", new Document("$size", 2)))
users.find(new Document("user", new Document("$all", Arrays.asList("a"))))
users.find(new Document("user", new Document("$mod", Arrays.asList(4, 0))))
users.find(new Document("user", new Document("$elemMatch", new Document("x", new Document("$gt", 0)))))
users.find(new Document("user", new Document("$where", "this.pass[0] == 'f'")))
users.find(new Document("user", new Document("$not", new Document("$eq", "x"))))
users.find(new Document("$or", Arrays.asList(new Document("user", "a"), new Document("user", "b"))))
users.find(new Document("$and", Arrays.asList(new Document("user", new Document("$ne", null)))))
users.find(new Document("$nor", Arrays.asList(new Document("user", "nobody"))))
users.find(new Document("$where", "this.pass[0] == 'f'"))
users.find(new Document("$expr", new Document("$eq", Arrays.asList(new Document("$substrCP", Arrays.asList("$pass", 0, 4)), "flag"))))
users.find(new Document("$comment", "x"))
users.find(new Document("$natural", 1))
users.find(new Document("$hint", new Document("user", 1)))
users.find(new Document("$maxScan", 100))
users.find(new Document("$snapshot", true))
users.find(new Document("$orderby", new Document("user", 1)))
users.find(new Document("$readPreference", new Document("mode", "primary")))
users.find(new Document("$explain", true))
users.find(new Document("$maxTimeMS", 100))
users.find(new Document("$query", new Document("user", "admin")))
```

`mongo-java-driver` — `injection-points.md`.

## `spring-data-mongodb` — the `MongoTemplate`/`Query`/`Criteria`

```java
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.mongodb.core.query.Criteria;

mongoTemplate.find(new Query(), User.class)
mongoTemplate.find(new Query(Criteria.where("user").ne(null)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").gt("")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").gte("")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").lt("z")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").lte("z")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").regex("^a")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").regex("^a", "i")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").regex(".*")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").in("a", "b")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").in(Arrays.asList("a", "b"))), User.class)
mongoTemplate.find(new Query(Criteria.where("user").nin("a", "b")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").nin(Arrays.asList())), User.class)
mongoTemplate.find(new Query(Criteria.where("user").exists(true)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").exists(false)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").type(2)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").type(2, 10)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").size(2)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").all("a", "b")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").all(Arrays.asList("a"))), User.class)
mongoTemplate.find(new Query(Criteria.where("user").mod(4, 0)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").elemMatch(Criteria.where("x").gt(0))), User.class)
mongoTemplate.find(new Query(Criteria.where("user").where("this.pass[0] == 'f'")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").not().is("x")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").not().ne(null)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").not().in("x")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").not().regex("^a")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").not().size(0)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").not().all("a")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").not().elemMatch(Criteria.where("x").gt(0))), User.class)
mongoTemplate.find(new Query(Criteria.where("user").not().exists(false)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").not().type(10)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").not().mod(4, 0)), User.class)
mongoTemplate.find(new Query(new Criteria().orOperator(Criteria.where("user").is("a"), Criteria.where("user").is("b"))), User.class)
mongoTemplate.find(new Query(new Criteria().andOperator(Criteria.where("user").ne(null), Criteria.where("pass").ne(null))), User.class)
mongoTemplate.find(new Query(new Criteria().norOperator(Criteria.where("user").is("nobody"))), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").ne(null)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").regex("^a")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").gt("")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").in("x", "y")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").exists(true)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").type(2)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").size(0)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").all("x")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").mod(4, 0)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").elemMatch(Criteria.where("x").gt(0))), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").where("this.pass")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").not().is("x")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").not().ne(null)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").not().in("x")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").not().regex("^a")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").not().size(0)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").not().all("x")), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").not().elemMatch(Criteria.where("x").gt(0))), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").not().exists(false)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").not().type(10)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").not().mod(4, 0)), User.class)
mongoTemplate.find(new Query(Criteria.where("user").is("admin").and("pass").not().where("this.pass")), User.class)
```

`spring-data-mongodb` — `injection-points.md`.

## `spring-data` — the `@Query`/`@Query`/`@Aggregation`/`@Update`

```java
@Query("{'user': ?0, 'pass': ?1}")
@Query("{user: ?0, pass: ?1}")
@Query("{user: {$ne: null}, pass: {$ne: null}}")
@Query("{user: {$regex: ?0}, pass: {$regex: ?1}}")
@Query("{user: {$in: ?0}, pass: {$in: ?1}}")
@Query("{user: {$exists: ?0}, pass: {$exists: ?1}}")
@Query("{user: {$type: ?0}, pass: {$type: ?1}}")
@Query("{user: {$size: ?0}, pass: {$size: ?1}}")
@Query("{user: {$all: ?0}, pass: {$all: ?1}}")
@Query("{user: {$mod: ?0}, pass: {$mod: ?1}}")
@Query("{user: {$elemMatch: ?0}, pass: {$elemMatch: ?1}}")
@Query("{user: {$where: ?0}, pass: {$where: ?1}}")
@Query("{user: {$not: ?0}, pass: {$not: ?1}}")
@Query("{$or: ?0}")
@Query("{$and: ?0}")
@Query("{$nor: ?0}")
@Query("{$where: ?0}")
@Query("{$expr: ?0}")
@Query("{$comment: ?0}")
@Query("{$natural: ?0}")
@Query("{$hint: ?0}")
@Query("{$maxScan: ?0}")
@Query("{$snapshot: ?0}")
@Query("{$orderby: ?0}")
@Query("{$readPreference: ?0}")
@Query("{$explain: ?0}")
@Query("{$maxTimeMS: ?0}")
@Query("{$query: ?0}")
```

`@Query` — `injection-points.md`.

## `spring-data` — the `Update`/`Aggregation`/`Projection`

```java
import org.springframework.data.mongodb.core.query.Update;
import org.springframework.data.mongodb.core.aggregation.Aggregation;

Update update = new Update();
update.set("role", "admin")
update.set("flag", "x")
update.unset("isLocked")
update.inc("balance", 9999)
update.push("roles", "admin")
update.addToSet("perms", "*")
update.pull("bans", "me")
update.rename("flag", "user")
update.multiply("score", 2)
update.min("limit", 0)
update.max("cap", 999)
update.currentDate("ts")
update.bitwise("flags", Update.BitwiseOperator.AND, 15)
update.setOnInsert("admin", true)
update.set("flag", "{$literal: \"x\"}")
update.set("flag", "{$ifNull: [\"$flag\", \"x\"]}")
update.set("flag", "{$concat: [\"$a\", \"$b\"]}")
update.set("flag", "{$toUpper: \"$a\"}")
update.set("flag", "{$toLower: \"$a\"}")
update.set("flag", "{$trim: {input: \"$a\"}}")
update.set("flag", "{$substrCP: [\"$a\", 0, 4]}")
update.set("flag", "{$split: [\"$a\", \"{\"]}")
update.set("flag", "{$arrayElemAt: [{$split: [\"$a\", \"{\"]}, 0]}")
update.set("flag", "{$convert: {input: \"$a\", to: \"string\"}}")
update.set("flag", "{$toString: \"$a\"}")
update.set("flag", "{$toInt: \"$a\"}")
update.set("flag", "{$toObjectId: \"$a\"}")
update.set("flag", "{$dateFromString: {dateString: \"$a\"}}")
update.set("flag", "{$dateToString: {date: \"$a\", format: \"%Y-%m-%d\"}}")
update.set("flag", "{$let: {vars: {p: \"$a\"}, in: \"$$p\"}}")
update.set("flag", "{$map: {input: \"$a\", as: \"i\", in: \"$$i\"}}")
update.set("flag", "{$filter: {input: \"$a\", as: \"i\", cond: {$gt: [\"$$i\", 0]}}}")
update.set("flag", "{$reduce: {input: \"$a\", initialValue: 0, in: {$add: [\"$$value\", \"$$this\"]}}}")
update.set("flag", "{$cond: [{$eq: [\"$a\", \"x\"]}, \"yes\", \"no\"]}")
update.set("flag", "{$ifNull: [\"$a\", \"x\"]}")
update.set("flag", "{$switch: {branches: [{case: {$eq: [\"$a\", \"x\"]}, then: \"y\"}], default: \"z\"}}")
update.set("flag", "{$literal: {$x: 1}}")
update.set("flag", "{$function: {body: \"function(a) { return a; }\", args: [\"$a\"], lang: \"js\"}}")
update.set("flag", "{$accumulator: {init: \"function() { return 0; }\", accumulate: \"function(s, a) { return s + a; }\", accumulateArgs: [\"$a\"], merge: \"function(a, b) { return a + b; }\", lang: \"js\"}}")
mongoTemplate.updateFirst(new Query(), update, User.class)
mongoTemplate.updateMulti(new Query(), update, User.class)
mongoTemplate.findAndModify(new Query(), update, User.class)
mongoTemplate.findAndReplace(new Query(), new User(), User.class)
mongoTemplate.findAndRemove(new Query(), User.class)
mongoTemplate.remove(new Query(), User.class)
mongoTemplate.upsert(new Query(), update, User.class)
```

`Update`/`Aggregation`/`Projection` — `update-injection.md`.
