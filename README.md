# p4-triggers-maid

Manually modify p4 triggers, **shake it off**. Completely implemented in Python!

## How it works

- Copy the script to the local p4 server through trigger, and then execute.
- Generate p4 triggers configuration through reflection, and automatically write it to **p4 triggers config** through
  trigger when 'change-commit'.

## Setup

- p4 server install python >= 3.9
- Install the modules in the requirements.txt
- Manually set two triggers

```
update_triggr update_trigger.py change-commit //repo/.triggers/... "python3 %//repo/.triggers/update_trigger.py% %change%"
update_p4_triggr_tables update_trigger.py change-commit //repo/.triggers/... "python3 /p4/triggers/main.py%"
```

## Feature

- Supports multiple rules (super whitelist, whitelist, path-level whitelist, regular include, regular exclude) for
  configuration filtering (no need to configure triggers for each path)

- Supports automatic update of p4 triggers (can be mixed with manually set triggers)

- Extension-friendly (extending a new trigger is very fast and simple)

- Local test-friendly (testing triggers is a very troublesome thing)

- etc...

## Example

Specific reference **main.py** and **trigger_test.py**

