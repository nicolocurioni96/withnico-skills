# ASC Upload Guide

## Install asc CLI
```bash
brew install asc
```

## Authenticate
```bash
asc auth login \
  --name "MyApp" \
  --key-id "YOUR_KEY_ID" \
  --issuer-id "YOUR_ISSUER_ID" \
  --private-key /path/to/AuthKey_XXXXXX.p8
```

## Get App ID
```bash
asc apps list
```

## Upload
```bash
asc screenshots upload \
  --app YOUR_APP_ID \
  --dir ./screenshots-output
```

## Device Identifiers
| Folder | asc flag |
|--------|---------|
| iphone-6.9 | IPHONE_69 |
| iphone-6.7 | IPHONE_67 |
| ipad-13 | IPAD_PRO_3GEN_129 |
| ipad-12.9 | IPAD_PRO_129 |

## Validate Before Upload
```bash
python3 scripts/validate_output.py --dir ./screenshots-output
```
