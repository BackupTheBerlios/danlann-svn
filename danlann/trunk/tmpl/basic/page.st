<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>$gallery.title$</title>
$css: {c |
    <link rel = 'stylesheet' type = 'text/css' href = '$rootdir$/$c$' media = 'all'/>
}$
    </head>

    <body class = "$class$">
        <div id = "body" class = "body">
        $(tmpl)()$
        $basic/copyright()$
        </div>
        $basic/footer()$
    </body>
</html>
$!  vim:syntax=html
!$
