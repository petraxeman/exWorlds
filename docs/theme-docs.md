# Theme format

## Basics
The basic version of the theme should consist of one folder containing a file: theme.json.
Inside the theme folder, there can be any number of other files and folders.

The basic theme format is as follows:
```json
{
  "codename": "theme codename",
  "resources": {},
  "zones": {
    "default": {}
  }
}
```

### Codename
Codename is a technical field. It is used to differentiate themes from one another. The main rule is that the codename must be a unique string. Other than that, you can put anything in this field.

### Resources
Resources is a much more interesting field. Essentially, it is a list of all the resources and materials that will be used in your theme. More details on declaring resources can be found in the chapter on resources.

### Zones
Zones are essentially areas where certain resources are applied. There may be no zones at all, but in that case, no resources will be assembled or displayed in the program. More details on existing zones can be found in the chapter on zones.



## Resources

Resources generally correspond to resources from Godot.

Currently, there are five different types of resources:

- `load_image`
- `make_gradient`
- `make_plain_color`
- `make_stylebox`
- `make_font`

### load_image
Loads an image from the specified path. It is used in TextureRect, which is most commonly used as a background.

Example resource:
```json
{"action": "load_image", "path": "theme://images/image.jpg"}
```

### make_gradient
Creates a gradient based on the specified properties. This is a two-dimensional linear gradient, so you can define the starting and ending points of the gradient on a plane.

- **from** – An array of points (x, y) defining where the gradient starts.
- **to** – An array of points (x, y) defining where the gradient ends.
- **offsets** – An array of values that should have the same length as the color array. It specifies which color appears at which position along the gradient.
- **colors** – An array of colors in 01-color format. The first three values define the RGB color, and the fourth (optional) value defines the alpha (transparency) channel.

Example resource:
```json
{
  "action": "make_gradient",
  "from": [0, 0],
  "to": [1, 1],
  "offsets": [0, 0.5, 1],
  "colors": [[0.5, 0, 0], [0, 0.5, 0, 0.5], [0, 0, 0.5]]
}
```

### make_plain_color
A simple way to replace a gradient or an image. It has only one property:
- **color** – Defined in the same 01-color format with an optional alpha channel.

```json
{"action": "make_plain_color", "color": [0.5, 0, 0]}
```

### make_stylebox
Used for panels and buttons. This is a fairly complex resource with multiple properties:

- **corner** – Defines how many pixels the corners should be rounded.
- **color** – The main color of the stylebox.
- **cont-margin** – Defines how much the child elements of the object using this stylebox will be compressed.
- **bord-color** – The color of the border around the stylebox.
- **border-width** – The width of the border. If set to 0, the border will not be visible.
- **expand** – Defines how much the stylebox will "protrude" or extend.

```json
{
  "action": "make_stylebox",
  "corner": [0, 0, 0, 0],
  "color": [0, 1, 0],
  "cont-margin": [0, 0, 0, 0],
  "bord-color": [1, 0, 0],
  "border-width": 2,
  "expand": [0, 0, 0, 0]
}
```


### make_font
A configuration builder for text. It includes not only font settings but also the overall label configuration.

- **font-color** – The main text color in 01-color format.
- **shadow-color** – The color of the text shadow.
- **outline-color** – The color of the text outline.
- **shadow-offset** – The x, y position offset for the shadow relative to the text.
- **outline-size** – The size of the text outline.
- **shadow-outline-size** – The size of the shadow outline.

```json
{
  "action": "make_font",
  "font-color": [1, 1, 1],
  "shadow-color": [1, 1, 1],
  "outline-color": [1, 1, 1],
  "shadow-offset": [1, 1],
  "outline-size": 1,
  "shadow-outline-size": 1,
  "font": "theme://fonts/font.ttf"
}
```

### make_button_font

- **font** - Path to font file.
- **font-color** – The main text color in 01-color format.
- **font-hover-color** - The color of the font what shows when cursor over button
- **font-pressed-color** - The color of the font what shows when button pressed
- **font-disabled-color** - The color of the font what shows when button disabled
- **font-outline-color** - Color of text outline
- **outline-size** - Size of text outline

```json
{
  "font-color": [1, 1, 1],
  "font-hover-color": [1, 1, 1],
  "font-pressed-color": [1, 1, 1],
  "font-disabled-color": [1, 1, 1],
  "font-outline-color": [1, 1, 1],
  "outline-size": 1,
  "font": "theme://fonts/font.ttf"
}
```



## Zones

Every **button** has a subclass:
- button/normal
- button/hover
- button/pressed
- button/disabled
- texturerect/texture
- container/panel
- subwindow/border
- label/font
- lineedit/normal
- lineedit/focus
- option/normal
- option/hover
- option/pressed
- option/disabled
- option/font


server-selection
- main-view-background  : texture  : /texture
- exworlds-main-title   : font     : /font
- exworlds-main-version : font     : /font
- server-list-panel     : stylebox : /panel
- server-actions-list   : stylebox : /panel
- button-play           : stylebox : /normal, /hover, /disabled, /pressed
- button-delete-server  : stylebox : /normal, /hover, /disabled, /pressed
- button-add-server     : stylebox : /normal, /hover, /disabled, /pressed
- button-theme-editor   : stylebox : /normal, /hover, /disabled, /pressed
- button-open-settings  : stylebox : /normal, /hover, /disabled, /pressed
- button-exit           : stylebox : /normal, /hover, /disabled, /pressed

- server-item-server-name : font : /font
- server-item-server-orig : font : /font
- server-item-server-addr : font : /font

- server-settings-subwindow   : stylebox : /border
- server-settings-background  : texture  : /texture
- server-settings-title       : font     : /font
- server-settings-mark-lbl    : font     : /font
- server-settings-addr-lbl    : font     : /font
- server-settings-login-lbl   : font     : /font
- server-settings-passwd-lbl  : font     : /font

- server-settings-nark-edit     : stylebox : /normal, /focus
- server-settings-addr-edit     : stylebox : /normal, /focus
- server-settings-login-edit    : stylebox : /normal, /focus
- server-settings-passwd-edit   : stylebox : /normal, /focus
- server-settings-ok-button     : stylebox : /normal, /hover, /disabled, /pressed
- server-settings-cancel-button : stylebox : /normal, /hover, /disabled, /pressed

- server-delete-confirm-subwin  : stylebox : /border
- server-delete-conf-background : texture  : /texture
- server-delete-conf-text       : font     : /font
- server-delete-conf-accept     : stylebox : /normal, /hover, /disabled, /pressed
- server-delete-conf-cancel     : stylebox : /normal, /hover, /disabled, /pressed

---

- settings-view-background      : texture  : /texture

- localization-option-popup
- theme-option-popup

- file-picker/hover
- file-picker/normal