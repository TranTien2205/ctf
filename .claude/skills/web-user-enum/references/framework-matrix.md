# Framework matrix — the per-stack oracle and fix, worked

## Django — the canonical timing case

`django.contrib.auth` — the default `ModelBackend.authenticate()`:
```python
user = UserModel.objects.get_by_natural_key(username)
if user.check_password(password): ...
# on a miss: UserModel.DoesNotExist -> no check_password -> ~0ms
# on a hit:  check_password -> PBKDF2 260k+ -> ~100ms
```
The fix (Django 1.10+): on `DoesNotExist`, run
`UserModel().set_password(password)` — a dummy hash to equalize the
work. Older versions and any custom backend without the dummy leak the
timing. The error text is uniform (`"Please enter a correct username
and password"`); the timing is the channel.

- `authenticate()` — `get_by_natural_key` then `check_password`
- the dummy-hash fix — only the newer default; custom backends skip it
- `USERNAME_FIELD = 'email'` — an email-login; probe the email slot
- the admin `/admin/login/` — the same `authenticate`, the same gap

## Flask/Werkzeug — the explicit short-circuit

```python
user = User.query.filter_by(username=u).first()
if user and check_password_hash(user.pw, p): ...
# on a miss: user is None -> `and` short-circuits -> no hash -> ~0ms
# on a hit:  check_password_hash -> PBKDF2/bcrypt -> ~80-300ms
```
The `and` short-circuit is the leak — `user and` means the hash only
runs on a real row. The equalization: hash a constant on the miss:
```python
if user is None: check_password_hash(DUMMY, p); return None
```
Most hand-rolled Flask auth skips it.

- `check_password_hash` — werkzeug's PBKDF2 (default ~600k iterations)
- `generate_password_hash` — the work is the gap
- a `LoginManager`/`flask_login` — same pattern, same gap
- the `flash("Invalid")` — uniform text, the timing is the channel

## Express/Node — the bcrypt gap

```js
const user = await User.findOne({ username });
if (user && await bcrypt.compare(pw, user.hash)) ...
// on a miss: user null -> no compare -> ~0ms
// on a hit:  bcrypt.compare -> ~80-120ms (cost 10-12)
```
The `bcrypt.compare` only runs on a real row. The equalization:
```js
if (!user) { await bcrypt.compare(pw, DUMMY_HASH); return null; }
```
- `bcrypt`/`bcryptjs`/`argon2`/`scrypt` — the gap scales with the cost
- `jsonwebtoken`/`express-session` — the session is separate
- a `passport` `LocalStrategy` — the `done(null,false)` on the miss

## Rails — `has_secure_password`

```ruby
user = User.find_by(email: e)
user&.authenticate(pw)   # authenticate runs bcrypt only if user
# on a miss: user nil -> &. skips -> ~0ms
# on a hit:  authenticate -> BCrypt::Password -> ~80-120ms
```
The `&.` safe-navigator skips `authenticate` on a nil — the gap.
- `has_secure_password` + `authenticate` — BCrypt
- Devise — `valid_password?` on the found user; the miss short-circuits
- Devise `paranoid` mode — a uniform message but the timing can remain

## Laravel — the `Hash::check` gap

```php
$user = User::where('email', $e)->first();
if ($user && Hash::check($pw, $user->password)) ...
// on a miss: $user null -> no Hash::check -> ~0ms
// on a hit:  Hash::check -> bcrypt/argon2 -> ~80-300ms
```
`Hash::check` only on a real row. The equalization: `Hash::check` a
constant on the miss — rarely applied.
- `Auth::attempt` — `retrieveByCredentials` then `validateCredentials`
- `Hash::check` — bcrypt (cost 10) / argon2id
- the `Password::sendResetLink` — the send-side reset oracle

## Spring — the `loadUserByUsername` gap

```java
UserDetails u = repo.loadUserByUsername(name);
if (u != null && encoder.matches(pw, u.getPassword())) ...
// on a miss: UsernameNotFoundException -> no matches -> ~0ms
// on a hit:  encoder.matches -> BCrypt -> ~80-120ms
```
`DaoAuthenticationProvider` calls `loadUserByUsername`; the
`UsernameNotFoundException` short-circuits before `matches`. Spring
equalizes only if `hideUserNotFoundExceptions` + a dummy is set.
- `DaoAuthenticationProvider` / `loadUserByUsername`
- `BCryptPasswordEncoder` / `Argon2` / `Pbkdf2`
- `UsernameNotFoundException` vs `BadCredentialsException` — a
  message-detail that may differ in the exception/error JSON

## ASP.NET — `UserManager.CheckPasswordAsync`

```csharp
var user = await _userManager.FindByNameAsync(name);
if (user != null && await _userManager.CheckPasswordAsync(user, pw)) ...
// on a miss: user null -> no CheckPassword -> ~0ms
// on a hit:  CheckPassword -> PBKDF2 -> ~100ms
```
- `SignInManager.PasswordSignInAsync` — `FindByName` then `CheckPassword`
- `UserManager` — Identity's `FailedLoginCount`/`AccessFailedCount` —
  the lockout counter (only a real row carries it → the lock oracle)
- `AccessFailedCount` — the per-account counter; `LockoutEnd`

## PHP (WordPress) — `wp_check_password`

```php
$user = get_user_by('login', $u);
if ($user && wp_check_password($p, $user->user_pass)) ...
// on a miss: get_user_by false -> no check -> ~0ms
// on a hit:  wp_check_password -> phpass/bcrypt -> ~80-300ms
```
- `wp_check_password` — phpass `PasswordHash` or bcrypt
- `wp_authenticate` — `get_user_by` then the check
- `?author=N` → `/author/<name>` — the redirect oracle
- `/wp-json/wp/v2/users` — the public user list
- `xmlrpc.php` `wp.getUsersBlogs` — a typed auth error
- `wp-login.php` `?action=lostpassword` — the reset oracle

## Drupal — the typed bind

Drupal's `user/<name>` path `200`/`404`s (a user-resource oracle), and
its login historically hashed only existing users — a timing oracle.
The `user/NAME` existence check is the more reliable channel.

## The matrix rule

The framework names the HASH (and so the expected gap) and the
short-circuit shape — `user and` / `user?.` / `if (u != null)` /
`get_user_by` — but the measurement is the same three arms on the same
channel. The stack is a hypothesis for the gap's SIZE; the oracle is
the measured delta, not the stack.
