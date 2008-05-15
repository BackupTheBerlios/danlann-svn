$!
create photo exif page
!$
<h1 class = 'title'>$album.title$: $photo.title$</h1>
<table class = 'exif'>
$photo.exif: { e |
    <tr><th>$e.name$</th><td>$e.value$</td></tr>
}$
</table>

$! vim:syntax=html
!$
