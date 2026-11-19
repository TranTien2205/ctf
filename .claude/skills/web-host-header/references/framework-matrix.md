# Framework matrix — the per-proxy host-header behavior, exhaustively

The per-proxy matrix — which headers each adds, which each strips, which each validates.

---

## 1. nginx — the most common reverse proxy

```nginx
# the nginx config — a proxy that validates the Host
server {
    listen 443 ssl;
    server_name target.com;
    proxy_pass http://backend;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Port $server_port;
    proxy_set_header X-Forwarded-Server $hostname;
    proxy_set_header X-Forwarded-User $remote_user;
    proxy_set_header X-Forwarded-Email $remote_email;
}
```

```text
nginx validates: the Host against the server_name — a 400 on a bad host
nginx adds: X-Forwarded-Host, X-Forwarded-Proto, X-Forwarded-Port,
           X-Forwarded-Server, X-Forwarded-User, X-Forwarded-Email
nginx passes: a client-supplied X-Forwarded-Host (unless the config strips it)
nginx rewrites: the path before forwarding — a traversal, an encoding, a
                case difference
```

## 2. Traefik — the modern reverse proxy

```text
Traefik validates: the Host against the router's rule — a 404 on a bad host
Traefik adds: X-Forwarded-Host, X-Forwarded-Proto, X-Forwarded-Port,
             X-Forwarded-Server
Traefik passes: a client-supplied X-Forwarded-Host (unless the config strips it)
Traefik rewrites: the path before forwarding — a traversal, an encoding, a
                  case difference
```

## 3. Apache — the mod_proxy pattern

```apache
# the Apache config — a proxy that validates the Host
<VirtualHost *:443>
    ServerName target.com
    ProxyPreserveHost On
    ProxyPass / http://backend/
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-For "%{REMOTE_ADDR}e"
    RequestHeader set X-Forwarded-Host "%{HTTP_HOST}e"
    RequestHeader set X-Forwarded-Server "%{HTTP_HOST}e"
    RequestHeader set X-Forwarded-User "%{REMOTE_USER}e"
</VirtualHost>
```

```text
Apache validates: the Host against the ServerName — a 400 on a bad host
Apache adds: X-Forwarded-Host, X-Forwarded-Proto, X-Forwarded-Server,
            X-Forwarded-User
Apache passes: a client-supplied X-Forwarded-Host (unless the config strips it)
Apache rewrites: the path before forwarding — a traversal, an encoding, a
                 case difference
```

## 4. HAProxy — the TCP-layer proxy

```haproxy
# the HAProxy config — a proxy that validates the Host
frontend https_in
    bind *:443 ssl crt /etc/ssl/target.com.pem
    acl is_target hdr(host) -i target.com
    use_backend target_backend if is_target
    default_backend reject_backend
```

```text
HAProxy validates: the Host against the ACL — a 403 on a bad host
HAProxy adds: X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto,
             X-Forwarded-User
HAProxy passes: a client-supplied X-Forwarded-Host (unless the config strips it)
HAProxy rewrites: the path before forwarding — a traversal, an encoding, a
                  case difference
```

## 5. Cloudflare — the edge proxy

```text
Cloudflare validates: the Host against the zone — a 403 on a bad host
Cloudflare adds: CF-Connecting-IP, CF-Ray, CF-Visitor, X-Forwarded-For,
                X-Forwarded-Proto, CF-Worker, CF-Scheme
Cloudflare strips: a client-supplied CF-* — the CDN's own headers
Cloudflare passes: a client-supplied X-Forwarded-Host (unless the config strips it)
Cloudflare rewrites: the path before forwarding — a traversal, an encoding,
                     a case difference
```

## 6. CloudFront — the AWS edge

```text
CloudFront validates: the Host against the distribution's aliases — a 403 on
                     a bad host
CloudFront adds: X-Amzn-Trace-Id, X-Forwarded-For, X-Forwarded-Host,
                X-Forwarded-Proto, CloudFront-Viewer-Country,
                CloudFront-Forwarded-Proto, CloudFront-Is-Mobile-Viewer,
                CloudFront-Is-Tablet-Viewer, CloudFront-Is-SmartTV-Viewer,
                CloudFront-Is-Desktop-Viewer
CloudFront strips: a client-supplied X-Amzn-* — the CDN's own headers
CloudFront passes: a client-supplied X-Forwarded-Host (unless the config strips it)
CloudFront rewrites: the path before forwarding — a traversal, an encoding,
                     a case difference
```

## 7. Akamai — the enterprise edge

```text
Akamai validates: the Host against the property's hostname — a 403 on a bad
                 host
Akamai adds: True-Client-IP, Akamai-Origin-Hop, X-Forwarded-For,
            X-Forwarded-Host, X-Forwarded-Proto, Akamai-Edgescape
Akamai strips: a client-supplied True-Client-IP — the CDN's own header
Akamai passes: a client-supplied X-Forwarded-Host (unless the config strips it)
Akamai rewrites: the path before forwarding — a traversal, an encoding, a
                 case difference
```

## 8. Varnish — the caching proxy

```text
Varnish validates: the Host against the vcl_recv logic — a 400 on a bad host
Varnish adds: X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto,
            X-Forwarded-Server, X-Forwarded-User
Varnish strips: a client-supplied Varnish-internal header — the VCL's own
Varnish passes: a client-supplied X-Forwarded-Host (unless the config strips it)
Varnish rewrites: the path before forwarding — a traversal, an encoding, a
                  case difference
```

## 9. Squid — the forward/reverse proxy

```text
Squid validates: the Host against the http_port accel configuration — a 400
                on a bad host
Squid adds: X-Forwarded-For
Squid strips: a client-supplied Squid-internal header — the Squid's own
Squid passes: a client-supplied X-Forwarded-Host (unless the config strips it)
Squid rewrites: the path before forwarding — a traversal, an encoding, a
                case difference
```

## 10. The per-proxy validate-map — which validates the Host

```text
a proxy validates the Host against a server list — a 400 on a bad host —
a negative result, not a retry signal.
```

## 11. The per-proxy strip-map — which strips the forwarded header

```text
a proxy strips the client-supplied forwarded header — the header doesn't
reach the app — the bypass fails — a different class.
```

## 12. The per-proxy verify-map — which verifies the forwarded header

```text
a proxy verifies the forwarded header it added — a client-supplied header
is rejected — the bypass fails — a different class.
```

## 13. The per-proxy rewrite-map — which rewrites the path

```text
a proxy rewrites the path before forwarding — a traversal, an encoding, a
case difference — the app's route reads the rewritten path — a route-
confusion.
```

## 14. The per-proxy boundary-map — which checks each gates

```text
a proxy's header gates a check — a canonical URL, a reset link, a
Location, a Set-Cookie, a cache key, a middleware rewrite — the app's
trust check reads the header's value — the differential's reach is the
downstream.
```

## 15. The per-proxy falsifier — when the proxy is dead

```text
a proxy that validates the Host against a server list → a 400 on a bad
host → a negative result, not a retry signal.
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
a trust check that reads a different input → a different class.
```
