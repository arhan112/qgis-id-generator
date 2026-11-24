# FjBa Basic ID Generator

**Fast. Simple. Reliable feature ID generation for QGIS.**

Basic ID Generator - FjBa makes it easy to create sequential IDs for vector features directly inside QGIS.

Generate simple numeric IDs:

```text
1
2
3
4
5
```

or structured IDs:

```text
ID-1
ID-2
ID-3
ID-4
```

## ✨ Features

- 🔢 Sequential ID generation
- 🏷️ Optional prefixes
- 🎯 Custom starting value
- ➕ Custom step/increment
- 🗂️ Multiple vector-layer support
- 🆕 Automatic ID field creation
- 🔄 Optional overwrite of existing values
- ↕️ Attribute-based sorting
- 🔽 Descending order
- 📊 Progress monitoring
- 🛑 Task cancellation
- 🌙 Dark and light themes
- ⌨️ Keyboard shortcuts

## 🚀 Quick Start

1. Select one or more vector layers.
2. Enter the ID field name.
3. Set the starting value and step.
4. Add an optional prefix.
5. Choose whether existing values should be overwritten.
6. Optionally select a sorting field.
7. Click **RUN**.

### Example

Settings:

```text
Field: asset_id
Prefix: ASSET-
Start: 100
Step: 1
```

Result:

```text
ASSET-100
ASSET-101
ASSET-102
ASSET-103
```

## ⌨️ Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + A` | Select all layers |
| `Ctrl + D` | Deselect all layers |
| `Ctrl + Enter` | Run |

## 🛡️ Data Safety

Always verify your selected layers and settings before running bulk updates.

When **Overwrite Existing Values** is enabled, existing attribute values may be replaced. Back up important data before performing bulk edits.

## ⚙️ Requirements

- QGIS 3.22 or newer
- Python 3.x
- PyQt5

## 📦 Installation

Install through:

**QGIS → Plugins → Manage and Install Plugins**

Search for:

**Basic ID Generator - FjBa**

You can also install the plugin from a ZIP package using **Install from ZIP**.

## 📝 Version

**1.0.0 — Initial Release**

## 👤 Author

**FjBa**

A simple QGIS utility for fast and consistent feature ID generation.

## 📄 License

See the included `LICENSE` file for license terms.

---

**Thank you for using Basic ID Generator - FjBa!**