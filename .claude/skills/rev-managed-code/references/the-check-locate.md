# Locating the check — name or dataflow

- Names survive unobfuscated: CheckFlag/Verify/Compare in the
  TypeDef/MethodDef list.
- Obfuscated: follow the #US literals — an ldstr of an expected
  value, or the verdict string's xref.
