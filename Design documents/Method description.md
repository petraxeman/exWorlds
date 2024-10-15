/pack/upload
  - codename: Codename of pack
  IF CREATE
    - name: Name of pack
    - image-name: Name of image
    - codename: Code name for pack
  IF UPDATE:
    - codename: Code name for pack
    -? name: Name of pack
    -? image-name: Name of image
    -? redactors: List of users who can change this pack