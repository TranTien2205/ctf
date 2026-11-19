# The version feature map — what exists when — checklist

Companion to `version-feature-map.md`.

## Checklist

- [ ] glibc | tcache | key check | safe-linking | unlink checks | hooks
- [ ] <=2.25 | no | - | - | weak | yes
- [ ] 2.26-2.28 | yes | no | - | weak | yes
- [ ] 2.29 | yes | yes | - | weak | yes
- [ ] 2.30-2.31 | yes | yes | - | strong | yes
- [ ] 2.32-2.34 | yes | yes | yes | strong | yes
- [ ] >=2.35 | yes | yes | yes | strong | removed
