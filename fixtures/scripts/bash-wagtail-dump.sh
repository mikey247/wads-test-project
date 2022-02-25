function wagtail_dumpdata() {
    if [ -z "$1" ]
    then
	filename="data"
    else
	filename="$1"
    fi

    if [ -z "$2" ]
    then
	format="json"
    else
	format="$2"
    fi

    ./manage.py dumpdata --format "${format}" --natural-foreign --indent 2 \
		-e contenttypes -e auth.permission \
		-e wagtailcore.groupcollectionpermission \
		-e wagtailcore.grouppagepermission -e wagtailimages.rendition \
		-e sessions > ${filename}.${format}

    # -e postgres_search.indexentry \
}