$!
create photo page
!$

$if(photo.title)$
<h1 class = 'title'>$album.title$: $photo.title$</h1>
$else$
<h1 class = 'title'>$album.title$: no title</h1>
$endif$
$if(photo.description)$
<p class = 'description'>$photo.description$</p>
$endif$

<div class = 'photo preview'>
    <img alt = 'photo: $photo.title$' src = '$photo.name$.preview.jpg'/>
</div>

$! vim:syntax=html
!$
