# App Store Connect Integration — Shotkit

Shotkit has native App Store Connect API integration. No third-party tools required.

## Setup

```bash
shotkit init
```

You need an App Store Connect API key:
1. Go to https://appstoreconnect.apple.com/access/integrations/api
2. Create a new key with "App Manager" or "Admin" role
3. Download the `.p8` private key file
4. Note the Key ID and Issuer ID

The `shotkit init` command will:
- Ask for your Key ID, Issuer ID, and path to .p8 file
- Verify the connection
- Let you pick your app
- Save config to `.shotkit.json`

## Commands

```bash
# List your apps
shotkit apps

# Download existing screenshots (backup)
shotkit download --output ./backup

# Upload new screenshots
shotkit upload --dir ./screenshots-output

# Replace existing screenshots
shotkit update --dir ./screenshots-output
```

## Security

- The `.p8` private key stays on disk — Shotkit only reads the path
- Add `.shotkit.json` to your `.gitignore`
- JWT tokens are generated locally and expire after 20 minutes

## Device Type Mapping

| Shotkit Key | ASC Display Type |
|-------------|-----------------|
| `iphone-6.9` | `APP_IPHONE_69` |
| `iphone-6.7` | `APP_IPHONE_67` |
| `iphone-6.5` | `APP_IPHONE_65` |
| `iphone-6.1` | `APP_IPHONE_61` |
| `ipad-13` | `APP_IPAD_PRO_3GEN_129` |
| `ipad-12.9` | `APP_IPAD_PRO_129` |
| `ipad-11` | `APP_IPAD_PRO_3GEN_11` |

## Validate Before Upload

Always validate before uploading:
```bash
shotkit validate --dir ./screenshots-output
shotkit upload --dir ./screenshots-output
```

The upload command runs validation automatically before uploading.
