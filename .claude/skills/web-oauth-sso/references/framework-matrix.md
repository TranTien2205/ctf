# Framework matrix — the OAuth implementations by stack

Every framework implements OAuth differently. This matrix names the
implementation details that change the attack surface.

## The framework map

| Framework | The IdP | The app | The trap |
|---|---|---|---|
| Node.js + passport-oauth2 | the app's own `oauth2` strategy | `passport.authenticate('oauth2')` | `state` bound to `req.session` — check `passport` `state` option |
| Node.js + openid-client | the IdP's `authorize` endpoint | `openid-client` `Client.authorizationUrl` | `state` bound to `req.session` — check `openid-client` `state` option |
| Python + authlib | the IdP's `authorize` endpoint | `authlib` `OAuth2Client` | `state` bound to `flask.session` — check `authlib` `state` option |
| Python + requests-oauthlib | the IdP's `authorize` endpoint | `requests_oauthlib` `OAuth2Session` | `state` bound to `flask.session` — check `requests_oauthlib` `state` option |
| PHP + league/oauth2-client | the IdP's `authorize` endpoint | `league/oauth2-client` `Provider` | `state` bound to `$_SESSION` — check `Provider` `state` option |
| Ruby + omniauth | the IdP's `authorize` endpoint | `omniauth` `auth` method | `state` bound to `session` — check `omniauth` `state` option |
| Java + Spring Security OAuth | the IdP's `authorize` endpoint | `spring-security-oauth2` `OAuth2AuthorizationRequest` | `state` bound to `HttpSession` — check `AuthorizationRequestRepository` |
| Go + golang.org/x/oauth2 | the IdP's `authorize` endpoint | `oauth2` `AuthCodeURL` | `state` bound to `http.Cookie` — check `AuthCodeURL` `state` option |
| Keycloak | Keycloak's `authorize` endpoint | `keycloak` `AuthorizationCode` | `state` bound to `keycloak.session` — check `keycloak` `state` option |
| Auth0 | Auth0's `authorize` endpoint | `auth0` `WebAuth` | `state` bound to `auth0` `state` — check `auth0` `state` option |
| Okta | Okta's `authorize` endpoint | `okta` `OAuth2` | `state` bound to `okta` `state` — check `okta` `state` option |
| Azure AD | Azure AD's `authorize` endpoint | `msal` `PublicClientApplication` | `state` bound to `msal` `state` — check `msal` `state` option |
| Google | Google's `authorize` endpoint | `google-auth` `OAuth2` | `state` bound to `google-auth` `state` — check `google-auth` `state` option |
| GitHub | GitHub's `authorize` endpoint | `github` `OAuth` | `state` bound to `github` `state` — check `github` `state` option |

## The implementation details

### Node.js + passport-oauth2

The `state` is bound to `req.session` — the `passport` `state` option controls
whether `state` is validated. The falsifier: `state` is bound to `req.session`
and validated — a `400` on `state` mismatch is the falsifier.

```javascript
passport.use(new OAuth2Strategy({
  authorizationURL: 'https://idp/authorize',
  tokenURL: 'https://idp/token',
  clientID: 'APP',
  clientSecret: 'SECRET',
  callbackURL: 'https://app/callback',
  state: true,  // bound to req.session
}));
```

### Node.js + openid-client

The `state` is bound to `req.session` — the `openid-client` `state` option
controls whether `state` is validated. The falsifier: `state` is bound to
`req.session` and validated — a `400` on `state` mismatch is the falsifier.

```javascript
const client = new openid.Client({
  client_id: 'APP',
  client_secret: 'SECRET',
  redirect_uris: ['https://app/callback'],
});
const authUrl = client.authorizationUrl({
  scope: 'openid',
  state: 'STATE',  // bound to req.session
});
```

### Python + authlib

The `state` is bound to `flask.session` — the `authlib` `state` option
controls whether `state` is validated. The falsifier: `state` is bound to
`flask.session` and validated — a `400` on `state` mismatch is the falsifier.

```python
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='APP',
    client_secret='SECRET',
    server_metadata_url='https://idp/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid'},
)
```

### PHP + league/oauth2-client

The `state` is bound to `$_SESSION` — the `Provider` `state` option controls
whether `state` is validated. The falsifier: `state` is bound to `$_SESSION`
and validated — a `400` on `state` mismatch is the falsifier.

```php
$provider = new League\OAuth2\Client\Provider\GenericProvider([
    'clientId' => 'APP',
    'clientSecret' => 'SECRET',
    'redirectUri' => 'https://app/callback',
    'urlAuthorize' => 'https://idp/authorize',
    'urlAccessToken' => 'https://idp/token',
]);
```

### Ruby + omniauth

The `state` is bound to `session` — the `omniauth` `state` option controls
whether `state` is validated. The falsifier: `state` is bound to `session`
and validated — a `400` on `state` mismatch is the falsifier.

```ruby
use OmniAuth::Builder do
  provider :oauth2, 'APP', 'SECRET',
    client_options: {
      site: 'https://idp',
      authorize_url: '/authorize',
      token_url: '/token',
    }
end
```

### Java + Spring Security OAuth

The `state` is bound to `HttpSession` — the `AuthorizationRequestRepository`
controls whether `state` is validated. The falsifier: `state` is bound to
`HttpSession` and validated — a `400` on `state` mismatch is the falsifier.

```java
@Bean
public OAuth2AuthorizationRequestRepository<OAuth2AuthorizationRequest>
    authorizationRequestRepository() {
  return new HttpSessionOAuth2AuthorizationRequestRepository();
}
```

### Go + golang.org/x/oauth2

The `state` is bound to `http.Cookie` — the `AuthCodeURL` `state` option
controls whether `state` is validated. The falsifier: `state` is bound to
`http.Cookie` and validated — a `400` on `state` mismatch is the falsifier.

```go
oauth2Config := &oauth2.Config{
  ClientID:     "APP",
  ClientSecret: "SECRET",
  RedirectURL:  "https://app/callback",
  Scopes:       []string{"openid"},
  Endpoint:     oauth2.Endpoint{AuthURL: "https://idp/authorize",
                                TokenURL: "https://idp/token"},
}
url := oauth2Config.AuthCodeURL("STATE")  // bound to http.Cookie
```
