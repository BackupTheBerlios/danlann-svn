$!
create album index page
!$

<h1 class = 'title'>$album.title$</h1>
$if(album.description)$
<p class = 'description'>$album.description$</p>
$endif$

$if(album.subalbums)$
<div class = 'albums'>
$album.subalbums:basic/sindex()$
</div>
$endif$

$if(album.photos)$
<div class = 'photos'>
$album.photos:basic/pindex()$
</div>
$endif$

$! vim:syntax=html
!$
