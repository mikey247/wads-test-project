---
name: Release x.x.x
about: Project release checklist 
title: ''
labels: 'release'
assignees: ''

---

### Checklist for version vx.x.x

#### Ready for release

When `main-dev` is ready for a release:

- [] Merge with `main` as agreed main source branch.
- [] Merge `main` into `deploy` as current deployed branch **AND**
- [] Deploy `deploy` to VM
- [] Tag `main-dev` with `git tag -a v1.3_dev -m "23wXX brief summary"` and push tags `git push origin vx.x.x_dev`
- [] Tag `main` with `git tag -a v1.3 -m "23wXX brief summary"` and push tags `git push origin vx.x.x`
- [] Tag `deploy` with `git tag -a v1.3_deploy -m "23wXX brief summary"` and push tags `git push origin vx.x.x_deploy`

_where 23 is the current year and XX is current ISO week._

Current release is `vx.x.x` (main), `vx.x.x_dev` (main-dev),  and `vx.x.x_deploy` (deploy).

#### On the RVM after deployment

`./manage.py` steps and manual changes required after deployment:

- [] If the requirements changed, `pip install ...` 
- [] If new migrations were added, `./manage.py migrate` and `./manage.py showmigrations`
- [] If new/edited search or filter fields `./manage.py update_index`
- [] If new/edited static files `./manage.py collectstatic`
- [] Check status `./manage.py check` and `./manage.py check --deploy` (required)


#### Keeping track

##### New migration files 

For the next release vx.x.x we will be including migrations for:

- [] 

##### Data changes

As this replaces existing data for [], after deployment manual edits must be made to:

- [] 

##### Release notes

- Adds ..
- Fixes ...
- Removes ...
- Changes ...
