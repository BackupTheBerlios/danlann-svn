$!
create gallery index page item

it is called recursively to show all albums and their subalbums on index
page
!$
<div class = 'album'>
<a title = 'album: $it.title$' href = '$it.dir$/index.xhtml'>$it.title$</a>
$it.subalbums:basic/gindex()$
</div>

$!  vim:syntax=html
!$
