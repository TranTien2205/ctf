from Crypto.Util.number import getPrime, bytes_to_long

p, q = getPrime(512), getPrime(512)
n, e = p * q, 3
c = pow(bytes_to_long(FLAG), e, n)
print(n, e, c)
